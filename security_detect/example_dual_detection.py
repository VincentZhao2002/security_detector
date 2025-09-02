#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双重检测功能示例
演示如何使用本地检测 + 百度AI API双重检测功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from security_detector import SecurityDetector


def main():
    """主函数"""
    print("=== 敏感词检测库 - 双重检测功能示例 ===\n")
    
    # 1. 初始化检测器（启用双重检测）
    print("1. 初始化检测器（启用双重检测）")
    detector = SecurityDetector(enable_api_detection=True)
    print(f"   检测方法: {detector.get_detection_method()}")
    print(f"   API是否可用: {detector.is_api_available()}\n")
    
    # 2. 测试文本列表
    test_texts = [
        "这是一句正常的测试文本，没有任何问题",
        "我们要热爱祖国热爱党，这是正确的价值观",
        "我要爆粗口啦：百度AI真他妈好用，这个功能太棒了",
        "正常的聊天内容，没有任何敏感词汇",
        "包含一些敏感词汇的文本，需要仔细检查"
    ]
    
    # 3. 执行检测
    print("2. 执行双重检测")
    for i, text in enumerate(test_texts, 1):
        print(f"\n测试文本 {i}: {text}")
        result = detector.detect(text)
        
        # 显示基本结果
        status = "✅ 安全" if result.is_safe else "❌ 不安全"
        print(f"   检测结果: {status}")
        print(f"   风险等级: {result.risk_level}")
        print(f"   置信度: {result.confidence:.2f}")
        
        if result.sensitive_words:
            print(f"   敏感词: {result.sensitive_words}")
        
        # 显示检测方法
        detection_method = result.details.get('detection_method', 'unknown')
        print(f"   检测方法: {detection_method}")
        
        # 如果是双重检测，显示详细信息
        if detection_method == 'dual_detection':
            local_result = result.details.get('local_result', {})
            api_result = result.details.get('api_result', {})
            
            print(f"   本地检测: 安全={local_result.get('is_safe')}, "
                  f"风险={local_result.get('risk_level')}, "
                  f"置信度={local_result.get('confidence', 0):.2f}")
            print(f"   API检测: 安全={api_result.get('is_safe')}, "
                  f"风险={api_result.get('risk_level')}, "
                  f"置信度={api_result.get('confidence', 0):.2f}")
    
    # 4. 演示API检测控制
    print("\n3. API检测控制演示")
    
    # 禁用API检测
    print("   禁用API检测...")
    detector.set_api_detection(False)
    print(f"   当前检测方法: {detector.get_detection_method()}")
    
    # 测试仅本地检测
    test_text = "这是一个测试文本"
    result = detector.detect(test_text)
    print(f"   检测结果: {'安全' if result.is_safe else '不安全'}")
    print(f"   检测方法: {result.details.get('detection_method', 'unknown')}")
    
    # 重新启用API检测
    print("\n   重新启用API检测...")
    detector.set_api_detection(True)
    print(f"   当前检测方法: {detector.get_detection_method()}")
    
    # 5. 批量检测示例
    print("\n4. 批量检测示例")
    batch_texts = [
        "安全文本1",
        "包含敏感内容的文本",
        "安全文本2"
    ]
    
    results = detector.batch_detect(batch_texts)
    for i, result in enumerate(results):
        status = "安全" if result.is_safe else "不安全"
        method = result.details.get('detection_method', 'unknown')
        print(f"   文本{i+1}: {status} (方法: {method})")
    
    print("\n=== 示例完成 ===")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"运行示例时出现错误: {e}")
        import traceback
        traceback.print_exc() 