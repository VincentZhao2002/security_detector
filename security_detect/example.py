#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
敏感词检测库使用示例
"""

from security_detector import SecurityDetector, DetectionResult


def basic_usage_example():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 初始化检测器
    detector = SecurityDetector()
    
    # 测试文本
    test_texts = [
        "这是一个正常的文本，没有任何问题。",
        "今天天气很好，我想去公园散步。",
        "这个文本包含一些敏感内容，需要被检测出来。",
        "我想了解一下关于政治的话题。",
        "这是一个完全安全的文本内容。"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n测试文本 {i}: {text}")
        result = detector.detect(text)
        
        print(f"  是否安全: {'是' if result.is_safe else '否'}")
        print(f"  风险等级: {result.risk_level}")
        print(f"  置信度: {result.confidence:.2f}")
        if result.sensitive_words:
            print(f"  发现的敏感词: {result.sensitive_words}")
        print(f"  详细信息: {result.details}")


def llm_safety_check_example():
    """LLM安全检查示例"""
    print("\n=== LLM安全检查示例 ===")
    
    detector = SecurityDetector()
    
    # 模拟用户输入
    user_inputs = [
        "请帮我写一篇关于人工智能的文章",
        "我想了解一些敏感的政治话题",
        "请解释一下量子计算的基本原理",
        "我想知道如何制作一些危险的东西",
        "请帮我分析一下股票市场的趋势"
    ]
    
    for i, user_input in enumerate(user_inputs, 1):
        print(f"\n用户输入 {i}: {user_input}")
        
        # 检查是否安全
        is_safe = detector.is_safe_for_llm(user_input)
        
        if is_safe:
            print("  ✅ 安全 - 可以作为LLM输入")
        else:
            print("  ❌ 不安全 - 不建议作为LLM输入")
            result = detector.detect(user_input)
            print(f"  原因: 发现敏感词 {result.sensitive_words}")


def batch_detection_example():
    """批量检测示例"""
    print("\n=== 批量检测示例 ===")
    
    detector = SecurityDetector()
    
    # 批量文本
    texts = [
        "正常文本1",
        "包含敏感内容的文本",
        "正常文本2",
        "另一个敏感文本",
        "正常文本3"
    ]
    
    # 批量检测
    results = detector.batch_detect(texts)
    
    print("批量检测结果:")
    for i, (text, result) in enumerate(zip(texts, results), 1):
        status = "✅ 安全" if result.is_safe else "❌ 不安全"
        print(f"  {i}. {text[:20]}... - {status}")


def sensitive_word_management_example():
    """敏感词管理示例"""
    print("\n=== 敏感词管理示例 ===")
    
    detector = SecurityDetector()
    
    # 获取当前敏感词数量
    original_count = len(detector.get_sensitive_words())
    print(f"当前敏感词数量: {original_count}")
    
    # 添加新的敏感词
    new_word = "测试敏感词"
    detector.add_sensitive_word(new_word)
    print(f"添加敏感词: {new_word}")
    
    # 测试新添加的敏感词
    test_text = f"这个文本包含{new_word}，应该被检测出来"
    result = detector.detect(test_text)
    print(f"检测结果: {'不安全' if not result.is_safe else '安全'}")
    print(f"发现的敏感词: {result.sensitive_words}")
    
    # 移除敏感词
    detector.remove_sensitive_word(new_word)
    print(f"移除敏感词: {new_word}")
    
    # 再次测试
    result = detector.detect(test_text)
    print(f"移除后检测结果: {'不安全' if not result.is_safe else '安全'}")


def performance_test_example():
    """性能测试示例"""
    print("\n=== 性能测试示例 ===")
    
    import time
    
    detector = SecurityDetector()
    
    # 生成大量测试文本
    test_texts = [
        f"这是第{i}个测试文本，用于性能测试。" for i in range(1000)
    ]
    
    # 测试批量检测性能
    start_time = time.time()
    results = detector.batch_detect(test_texts)
    end_time = time.time()
    
    # 统计结果
    safe_count = sum(1 for r in results if r.is_safe)
    unsafe_count = len(results) - safe_count
    
    print(f"检测了 {len(test_texts)} 个文本")
    print(f"耗时: {end_time - start_time:.2f} 秒")
    print(f"平均每个文本: {(end_time - start_time) / len(test_texts) * 1000:.2f} 毫秒")
    print(f"安全文本: {safe_count}")
    print(f"不安全文本: {unsafe_count}")


def main():
    """主函数"""
    print("敏感词检测库使用示例")
    print("=" * 50)
    
    try:
        # 运行各种示例
        basic_usage_example()
        llm_safety_check_example()
        batch_detection_example()
        sensitive_word_management_example()
        performance_test_example()
        
        print("\n" + "=" * 50)
        print("所有示例运行完成！")
        
    except Exception as e:
        print(f"运行示例时出错: {e}")


if __name__ == "__main__":
    main() 