#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用security_detect库对数据集进行评测
计算拒答和非拒答的准确率
"""

# 导入必要的库
import json
import time
import logging
from typing import Dict, List, Tuple, Any
from collections import Counter
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from security_detector import SecurityDetector
    print("✅ 成功导入security_detector库")
except ImportError as e:
    print(f"❌ 导入security_detector库失败: {e}")
    sys.exit(1)

# 导入配置
try:
    from config import (
        REQUEST_DELAY, BATCH_SIZE, BATCH_DELAY, 
        MAX_RETRIES, RETRY_DELAY, MAX_SAMPLES,
        DATASET_PATH, PROGRESS_INTERVAL
    )
    print("✅ 成功加载配置文件")
except ImportError as e:
    print(f"❌ 加载配置文件失败: {e}")
    sys.exit(1)

# 设置输出路径
OUTPUT_PATH = "security_detection_evaluation_results.json"
OUTPUT_PATH_NO_API = "security_detection_evaluation_results_no_api.json"

def load_dataset(dataset_path):
    """加载数据集"""
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ 成功加载数据集，共 {len(data)} 条数据")
        return data
    except Exception as e:
        print(f"❌ 加载数据集失败: {e}")
        return None

def detect_with_retry(detector, question, max_retries=MAX_RETRIES):
    """带重试机制的检测函数"""
    for attempt in range(max_retries):
        try:
            result = detector.detect(question)
            return result
        except Exception as e:
            if "qps request limit reached" in str(e).lower():
                if attempt < max_retries - 1:
                    wait_time = RETRY_DELAY * (attempt + 1)
                    print(f"⚠️ API限流，等待 {wait_time} 秒后重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ API限流，已达到最大重试次数，跳过此条数据")
                    return None
            else:
                print(f"⚠️ 检测出错: {e}")
                return None
    return None

def evaluate_security_detection(dataset, enable_api_detection=None):
    """评测安全检测的准确率"""
    print("\n🔍 开始评测安全检测...")
    print(f"⚙️ 配置参数:")
    print(f"  请求延迟: {REQUEST_DELAY} 秒")
    print(f"  批次大小: {BATCH_SIZE}")
    print(f"  批次延迟: {BATCH_DELAY} 秒")
    print(f"  最大重试: {MAX_RETRIES}")
    print(f"  重试延迟: {RETRY_DELAY} 秒")
    
    # 初始化检测器
    if enable_api_detection is None:
        detector = SecurityDetector()
    else:
        detector = SecurityDetector(enable_api_detection=enable_api_detection)
    
    # 统计结果
    total_count = len(dataset)
    yes_count = 0  # 应该拒答的数量（标签为No）
    no_count = 0   # 不应该拒答的数量（标签为Yes）
    
    # 检测结果统计
    correct_detections = 0  # 正确检测的数量
    incorrect_detections = 0  # 错误检测的数量
    
    # 详细统计
    yes_correct = 0  # 应该拒答且被正确检测的数量
    yes_incorrect = 0  # 应该拒答但未被检测的数量
    no_correct = 0   # 不应该拒答且被正确检测的数量
    no_incorrect = 0  # 不应该拒答但被错误检测的数量
    
    # 跳过统计
    skipped_count = 0
    
    # 收集误判数据
    false_negatives = []  # 应该拒答但未被检测（漏检）
    false_positives = []  # 不应该拒答但被错误检测（误检）
    
    # 逐条检测
    for i, item in enumerate(dataset):
        question = item['question']
        true_label = item['label']
        
        # 使用带重试的检测函数
        result = detect_with_retry(detector, question)
        
        if result is None:
            skipped_count += 1
            continue
            
        detected_unsafe = not result.is_safe  # 检测为不安全 = 应该拒答
        
        # 统计标签数量
        if true_label == "Yes":
            no_count += 1  # 不应该拒答
            if detected_unsafe:
                no_incorrect += 1  # 错误地检测为不安全
                # 记录误检数据（False Positive）
                false_positives.append({
                    'question': question,
                    'true_label': true_label,
                    'detected_label': 'No',
                    'detection_result': result.to_dict() if hasattr(result, 'to_dict') else str(result),
                    'error_type': 'False Positive (误检)',
                    'description': '不应该拒答但被错误检测为不安全'
                })
            else:
                no_correct += 1    # 正确检测为安全
        else:  # true_label == "No"
            yes_count += 1  # 应该拒答
            if detected_unsafe:
                yes_correct += 1   # 正确检测为不安全
            else:
                yes_incorrect += 1 # 错误地检测为安全
                # 记录漏检数据（False Negative）
                false_negatives.append({
                    'question': question,
                    'true_label': true_label,
                    'detected_label': 'Yes',
                    'detection_result': result.to_dict() if hasattr(result, 'to_dict') else str(result),
                    'error_type': 'False Negative (漏检)',
                    'description': '应该拒答但未被检测为不安全'
                })
        
        # 计算准确率
        if (true_label == "No" and detected_unsafe) or (true_label == "Yes" and not detected_unsafe):
            correct_detections += 1
        else:
            incorrect_detections += 1
            
        # 显示进度
        if (i + 1) % PROGRESS_INTERVAL == 0:
            print(f"📊 已处理 {i + 1}/{total_count} 条数据...")
        
        # 每处理完一批数据后添加延迟
        if (i + 1) % BATCH_SIZE == 0:
            print(f"⏳ 批次 {i // BATCH_SIZE + 1} 完成，等待 {BATCH_DELAY} 秒...")
            time.sleep(BATCH_DELAY)
        else:
            # 每次请求之间添加延迟
            time.sleep(REQUEST_DELAY)
    
    print(f"📊 处理完成，跳过 {skipped_count} 条数据")
    
    return {
        'total_count': total_count,
        'yes_count': yes_count,
        'no_count': no_count,
        'correct_detections': correct_detections,
        'incorrect_detections': incorrect_detections,
        'yes_correct': yes_correct,
        'yes_incorrect': yes_incorrect,
        'no_correct': no_correct,
        'no_incorrect': no_incorrect,
        'skipped_count': skipped_count,
        'false_negatives': false_negatives,  # 漏检数据
        'false_positives': false_positives,  # 误检数据
        'total_errors': len(false_negatives) + len(false_positives)  # 总误判数量
    }

def calculate_metrics(stats):
    """计算各种指标"""
    print("\n📈 计算评测指标...")
    
    # 总体准确率
    overall_accuracy = stats['correct_detections'] / stats['total_count'] * 100
    
    # 拒答准确率（标签为No的检测准确率）
    yes_accuracy = stats['yes_correct'] / stats['yes_count'] * 100 if stats['yes_count'] > 0 else 0
    
    # 非拒答准确率（标签为Yes的检测准确率）
    no_accuracy = stats['no_correct'] / stats['no_count'] * 100 if stats['no_count'] > 0 else 0
    
    # 精确率（Precision）
    precision = stats['yes_correct'] / (stats['yes_correct'] + stats['no_incorrect']) * 100 if (stats['yes_correct'] + stats['no_incorrect']) > 0 else 0
    
    # 召回率（Recall）
    recall = stats['yes_correct'] / (stats['yes_correct'] + stats['yes_incorrect']) * 100 if (stats['yes_correct'] + stats['yes_incorrect']) > 0 else 0
    
    # F1分数
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        'overall_accuracy': overall_accuracy,
        'yes_accuracy': yes_accuracy,
        'no_accuracy': no_accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score
    }

def print_results(stats, metrics):
    """打印评测结果"""
    print("\n" + "="*60)
    print("🎯 SECURITY_DETECT 库评测结果")
    print("="*60)
    
    print(f"\n📊 数据集统计:")
    print(f"  总数据量: {stats['total_count']}")
    print(f"  应该拒答 (No标签): {stats['yes_count']}")
    print(f"  不应该拒答 (Yes标签): {stats['no_count']}")
    print(f"  跳过数据: {stats['skipped_count']}")
    
    print(f"\n🔍 检测结果统计:")
    print(f"  正确检测: {stats['correct_detections']}")
    print(f"  错误检测: {stats['incorrect_detections']}")
    
    print(f"\n📈 详细统计:")
    print(f"  应该拒答且被正确检测: {stats['yes_correct']}")
    print(f"  应该拒答但未被检测: {stats['yes_incorrect']}")
    print(f"  不应该拒答且被正确检测: {stats['no_correct']}")
    print(f"  不应该拒答但被错误检测: {stats['no_incorrect']}")
    
    print(f"\n🎯 准确率指标:")
    print(f"  总体准确率: {metrics['overall_accuracy']:.2f}%")
    print(f"  拒答准确率 (No标签): {metrics['yes_accuracy']:.2f}%")
    print(f"  非拒答准确率 (Yes标签): {metrics['no_accuracy']:.2f}%")
    
    print(f"\n📊 性能指标:")
    print(f"  精确率 (Precision): {metrics['precision']:.2f}%")
    print(f"  召回率 (Recall): {metrics['recall']:.2f}%")
    print(f"  F1分数: {metrics['f1_score']:.2f}%")
    
    print("\n" + "="*60)

def save_results(stats, metrics, output_path):
    """保存评测结果到文件"""
    results = {
        'statistics': stats,
        'metrics': metrics,
        'summary': {
            'overall_accuracy': f"{metrics['overall_accuracy']:.2f}%",
            'yes_accuracy': f"{metrics['yes_accuracy']:.2f}%",
            'no_accuracy': f"{metrics['no_accuracy']:.2f}%",
            'precision': f"{metrics['precision']:.2f}%",
            'recall': f"{metrics['recall']:.2f}%",
            'f1_score': f"{metrics['f1_score']:.2f}%"
        }
    }
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 评测结果已保存到: {output_path}")
    except Exception as e:
        print(f"⚠️ 保存结果失败: {e}")

def main():
    """主函数"""
    print("🚀 开始使用security_detect库评测数据集")
    
    # 数据集路径
    dataset_path = DATASET_PATH
    
    # 检查数据集是否存在
    if not os.path.exists(dataset_path):
        print(f"❌ 数据集文件不存在: {dataset_path}")
        return
    
    # 加载数据集
    dataset = load_dataset(dataset_path)
    if dataset is None:
        return
    
    dataset = dataset[:MAX_SAMPLES]
    print(f"🔍 只处理前 {MAX_SAMPLES} 条数据进行评测。")

    # 评测安全检测（默认配置，可能包含API/双重检测）
    # stats = evaluate_security_detection(dataset)
    # metrics = calculate_metrics(stats)
    # print_results(stats, metrics)
    # save_results(stats, metrics, OUTPUT_PATH)

    # 再次评测：禁用API，仅使用本地检测，并单独保存结果
    print("\n🔁 开始进行无API（仅本地）检测评测...")
    stats_no_api = evaluate_security_detection(dataset, enable_api_detection=False)
    metrics_no_api = calculate_metrics(stats_no_api)
    print_results(stats_no_api, metrics_no_api)
    save_results(stats_no_api, metrics_no_api, OUTPUT_PATH_NO_API)
    
    print("\n✅ 评测完成！")

if __name__ == "__main__":
    main() 