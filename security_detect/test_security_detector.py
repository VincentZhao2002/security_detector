#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
敏感词检测库测试文件
"""

import unittest
import tempfile
import os
from security_detector import SecurityDetector, DetectionResult


class TestSecurityDetector(unittest.TestCase):
    """敏感词检测器测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时敏感词文件
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        self.temp_file.write("测试敏感词1\n")
        self.temp_file.write("测试敏感词2\n")
        self.temp_file.write("危险词汇\n")
        self.temp_file.write("政治敏感\n")
        self.temp_file.write("暴力内容\n")
        self.temp_file.close()
        
        # 初始化检测器
        self.detector = SecurityDetector(self.temp_file.name)
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除临时文件
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.detector)
        self.assertEqual(len(self.detector.sensitive_words), 5)
        self.assertIn("测试敏感词1", self.detector.sensitive_words)
        self.assertIn("测试敏感词2", self.detector.sensitive_words)
    
    def test_detect_safe_text(self):
        """测试检测安全文本"""
        text = "这是一个完全安全的文本，没有任何敏感内容。"
        result = self.detector.detect(text)
        
        self.assertIsInstance(result, DetectionResult)
        self.assertTrue(result.is_safe)
        self.assertEqual(result.risk_level, "safe")
        self.assertEqual(result.confidence, 1.0)
        self.assertEqual(len(result.sensitive_words), 0)
    
    def test_detect_unsafe_text(self):
        """测试检测不安全文本"""
        text = "这个文本包含测试敏感词1，应该被检测出来。"
        result = self.detector.detect(text)
        
        self.assertIsInstance(result, DetectionResult)
        self.assertFalse(result.is_safe)
        self.assertIn("测试敏感词1", result.sensitive_words)
        self.assertGreater(result.confidence, 0)
    
    def test_detect_multiple_sensitive_words(self):
        """测试检测多个敏感词"""
        text = "这个文本包含测试敏感词1和测试敏感词2，应该被检测出来。"
        result = self.detector.detect(text)
        
        self.assertFalse(result.is_safe)
        self.assertIn("测试敏感词1", result.sensitive_words)
        self.assertIn("测试敏感词2", result.sensitive_words)
        self.assertEqual(len(result.sensitive_words), 2)
    
    def test_empty_text(self):
        """测试空文本"""
        result = self.detector.detect("")
        self.assertTrue(result.is_safe)
        self.assertEqual(result.risk_level, "safe")
        self.assertEqual(result.confidence, 1.0)
    
    def test_none_text(self):
        """测试None文本"""
        result = self.detector.detect(None)
        self.assertTrue(result.is_safe)
        self.assertEqual(result.risk_level, "safe")
        self.assertEqual(result.confidence, 1.0)
    
    def test_is_safe_for_llm(self):
        """测试LLM安全检查"""
        safe_text = "这是一个安全的文本。"
        unsafe_text = "这个文本包含测试敏感词1。"
        
        self.assertTrue(self.detector.is_safe_for_llm(safe_text))
        self.assertFalse(self.detector.is_safe_for_llm(unsafe_text))
    
    def test_add_sensitive_word(self):
        """测试添加敏感词"""
        new_word = "新敏感词"
        original_count = len(self.detector.sensitive_words)
        
        self.detector.add_sensitive_word(new_word)
        
        self.assertEqual(len(self.detector.sensitive_words), original_count + 1)
        self.assertIn(new_word, self.detector.sensitive_words)
        
        # 测试新添加的敏感词是否生效
        text = f"包含{new_word}的文本"
        result = self.detector.detect(text)
        self.assertFalse(result.is_safe)
        self.assertIn(new_word, result.sensitive_words)
    
    def test_remove_sensitive_word(self):
        """测试移除敏感词"""
        word_to_remove = "测试敏感词1"
        original_count = len(self.detector.sensitive_words)
        
        self.detector.remove_sensitive_word(word_to_remove)
        
        self.assertEqual(len(self.detector.sensitive_words), original_count - 1)
        self.assertNotIn(word_to_remove, self.detector.sensitive_words)
        
        # 测试移除的敏感词是否不再被检测
        text = f"包含{word_to_remove}的文本"
        result = self.detector.detect(text)
        self.assertTrue(result.is_safe)
    
    def test_batch_detect(self):
        """测试批量检测"""
        texts = [
            "安全文本1",
            "包含测试敏感词1的文本",
            "安全文本2",
            "包含测试敏感词2的文本"
        ]
        
        results = self.detector.batch_detect(texts)
        
        self.assertEqual(len(results), 4)
        self.assertTrue(results[0].is_safe)
        self.assertFalse(results[1].is_safe)
        self.assertTrue(results[2].is_safe)
        self.assertFalse(results[3].is_safe)
    
    def test_risk_level_calculation(self):
        """测试风险等级计算"""
        # 低风险
        text = "包含测试敏感词1的文本"
        result = self.detector.detect(text)
        self.assertIn(result.risk_level, ["low", "medium", "high"])
        
        # 高风险（多个敏感词）
        text = "包含测试敏感词1和测试敏感词2和危险词汇的文本"
        result = self.detector.detect(text)
        self.assertIn(result.risk_level, ["low", "medium", "high"])
    
    def test_confidence_calculation(self):
        """测试置信度计算"""
        text = "包含测试敏感词1的文本"
        result = self.detector.detect(text)
        
        self.assertGreaterEqual(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)
    
    def test_case_insensitive(self):
        """测试大小写不敏感"""
        text = "包含测试敏感词1的文本"
        text_upper = "包含测试敏感词1的文本".upper()
        
        result1 = self.detector.detect(text)
        result2 = self.detector.detect(text_upper)
        
        self.assertEqual(result1.is_safe, result2.is_safe)
        self.assertEqual(len(result1.sensitive_words), len(result2.sensitive_words))


class TestSecurityDetectorIntegration(unittest.TestCase):
    """集成测试类"""
    
    def test_large_sensitive_words_file(self):
        """测试大文件加载"""
        # 创建包含大量敏感词的临时文件
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        
        # 写入1000个测试敏感词
        for i in range(1000):
            temp_file.write(f"测试敏感词{i}\n")
        
        temp_file.close()
        
        try:
            detector = SecurityDetector(temp_file.name)
            self.assertEqual(len(detector.sensitive_words), 1000)
            
            # 测试检测性能
            text = "包含测试敏感词500的文本"
            result = detector.detect(text)
            self.assertFalse(result.is_safe)
            self.assertIn("测试敏感词500", result.sensitive_words)
            
        finally:
            os.unlink(temp_file.name)
    
    def test_special_characters(self):
        """测试特殊字符处理"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        temp_file.write("特殊字符@#$%\n")
        temp_file.write("数字敏感词123\n")
        temp_file.write("emoji敏感词😀\n")
        temp_file.close()
        
        try:
            detector = SecurityDetector(temp_file.name)
            
            # 测试特殊字符
            text = "包含特殊字符@#$%的文本"
            result = detector.detect(text)
            self.assertFalse(result.is_safe)
            
            # 测试数字
            text = "包含数字敏感词123的文本"
            result = detector.detect(text)
            self.assertFalse(result.is_safe)
            
        finally:
            os.unlink(temp_file.name)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_suite.addTest(unittest.makeSuite(TestSecurityDetector))
    test_suite.addTest(unittest.makeSuite(TestSecurityDetectorIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 