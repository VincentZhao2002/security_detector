#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双重检测功能测试
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from security_detector import SecurityDetector


def test_dual_detection():
    """测试双重检测功能"""
    print("=== 双重检测功能测试 ===\n")
    
    # 初始化检测器（启用API检测）
    detector = SecurityDetector(enable_api_detection=True)
    
    print(f"检测方法: {detector.get_detection_method()}")
    print(f"API是否可用: {detector.is_api_available()}\n")
    
    # 测试文本列表
    test_texts = [
        "这是一句正常的测试文本",
        "我们要热爱祖国热爱党",
        "我要爆粗口啦：百度AI真他妈好用",
        "这是一句测试文本",
        "包含一些敏感词汇的文本",
        "正常的聊天内容，没有任何问题"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"测试 {i}: {text}")
        result = detector.detect(text)
        
        print(f"  是否安全: {result.is_safe}")
        print(f"  风险等级: {result.risk_level}")
        print(f"  置信度: {result.confidence:.2f}")
        print(f"  敏感词: {result.sensitive_words}")
        print(f"  检测方法: {result.details.get('detection_method', 'unknown')}")
        
        # 如果是双重检测，显示详细信息
        if result.details.get('detection_method') == 'dual_detection':
            local_result = result.details.get('local_result', {})
            api_result = result.details.get('api_result', {})
            print(f"  本地检测: 安全={local_result.get('is_safe')}, 风险={local_result.get('risk_level')}, 置信度={local_result.get('confidence', 0):.2f}")
            print(f"  API检测: 安全={api_result.get('is_safe')}, 风险={api_result.get('risk_level')}, 置信度={api_result.get('confidence', 0):.2f}")
        
        print()


def test_local_only_detection():
    """测试仅本地检测"""
    print("=== 仅本地检测测试 ===\n")
    
    # 初始化检测器（禁用API检测）
    detector = SecurityDetector(enable_api_detection=False)
    
    print(f"检测方法: {detector.get_detection_method()}\n")
    
    test_texts = [
        "这是一句正常的测试文本",
        "我们要热爱祖国热爱党",
        "包含一些敏感词汇的文本"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"测试 {i}: {text}")
        result = detector.detect(text)
        
        print(f"  是否安全: {result.is_safe}")
        print(f"  风险等级: {result.risk_level}")
        print(f"  置信度: {result.confidence:.2f}")
        print(f"  敏感词: {result.sensitive_words}")
        print()


def test_api_control():
    """测试API检测控制功能"""
    print("=== API检测控制测试 ===\n")
    
    detector = SecurityDetector()
    
    print(f"初始检测方法: {detector.get_detection_method()}")
    
    # 禁用API检测
    detector.set_api_detection(False)
    print(f"禁用API后: {detector.get_detection_method()}")
    
    # 启用API检测
    detector.set_api_detection(True)
    print(f"启用API后: {detector.get_detection_method()}")
    
    print(f"API是否可用: {detector.is_api_available()}\n")


if __name__ == "__main__":
    try:
        test_dual_detection()
        print("\n" + "="*50 + "\n")
        test_local_only_detection()
        print("\n" + "="*50 + "\n")
        test_api_control()
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc() 