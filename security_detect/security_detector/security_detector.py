#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
敏感词检测库
用于检测文本中是否包含敏感词，判断文本是否安全可以作为大语言模型的输入
"""

import os
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging
from .config import DEFAULT_SENSITIVE_WORDS_FILE, ORIGINAL_SENSITIVE_WORDS_FILE, API_CONFIG, DUAL_DETECTION_CONFIG
from .api_detector import APIDetector

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    """检测结果数据类"""
    is_safe: bool
    sensitive_words: List[str]
    risk_level: str
    confidence: float
    details: Dict


class SecurityDetector:
    """敏感词检测器"""
    
    def __init__(self, sensitive_words_file: str = None, use_original_file: bool = False, 
                 enable_api_detection: bool = None, api_key: str = None, secret_key: str = None):
        """
        初始化检测器
        
        Args:
            sensitive_words_file: 敏感词表文件路径，如果为None则使用默认路径
            use_original_file: 是否使用原始文件（包含重复），默认False使用去重后的文件
            enable_api_detection: 是否启用API检测，默认使用配置文件设置
            api_key: 百度AI API Key，默认使用配置文件设置
            secret_key: 百度AI Secret Key，默认使用配置文件设置
        """
        if sensitive_words_file is None:
            if use_original_file:
                sensitive_words_file = ORIGINAL_SENSITIVE_WORDS_FILE
            else:
                sensitive_words_file = DEFAULT_SENSITIVE_WORDS_FILE
        
        self.sensitive_words_file = sensitive_words_file
        self.sensitive_words = set()
        self.word_patterns = []
        self._load_sensitive_words()
        
        # 初始化API检测器
        self.enable_api_detection = enable_api_detection if enable_api_detection is not None else DUAL_DETECTION_CONFIG.get("enable_dual_detection", True)
        self.api_detector = None
        
        if self.enable_api_detection:
            try:
                api_key = api_key or API_CONFIG.get("api_key")
                secret_key = secret_key or API_CONFIG.get("secret_key")
                self.api_detector = APIDetector(api_key=api_key, secret_key=secret_key)
                if not self.api_detector.is_available():
                    logger.warning("API检测器初始化失败，将仅使用本地检测")
                    self.api_detector = None
                else:
                    logger.info("API检测器初始化成功")
            except Exception as e:
                logger.error(f"初始化API检测器失败: {e}")
                self.api_detector = None
    
    def _load_sensitive_words(self):
        """加载敏感词表"""
        try:
            if not os.path.exists(self.sensitive_words_file):
                raise FileNotFoundError(f"敏感词表文件不存在: {self.sensitive_words_file}")
            
            with open(self.sensitive_words_file, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word and not word.startswith('#'):  # 忽略空行和注释
                        self.sensitive_words.add(word)
                        # 创建正则表达式模式，支持模糊匹配
                        pattern = re.escape(word)
                        self.word_patterns.append(re.compile(pattern, re.IGNORECASE))
            
            logger.info(f"成功加载 {len(self.sensitive_words)} 个敏感词")
            
        except Exception as e:
            logger.error(f"加载敏感词表失败: {e}")
            raise
    
    def detect(self, text: str) -> DetectionResult:
        """
        检测文本中的敏感词（支持双重检测）
        
        Args:
            text: 待检测的文本
            
        Returns:
            DetectionResult: 检测结果
        """
        if not text:
            return DetectionResult(
                is_safe=True,
                sensitive_words=[],
                risk_level="safe",
                confidence=1.0,
                details={"reason": "空文本"}
            )
        
        # 执行本地检测
        local_result = self._local_detect(text)
        
        # 如果启用了API检测且API可用，执行双重检测
        if self.enable_api_detection and self.api_detector and self.api_detector.is_available():
            try:
                api_result = self._api_detect(text)
                return self._combine_results(local_result, api_result)
            except Exception as e:
                logger.warning(f"API检测失败，使用本地检测结果: {e}")
                local_result.details["api_error"] = str(e)
                return local_result
        
        # 仅使用本地检测
        return local_result
    
    def _local_detect(self, text: str) -> DetectionResult:
        """
        本地敏感词检测
        
        Args:
            text: 待检测的文本
            
        Returns:
            DetectionResult: 检测结果
        """
        found_words = []
        
        # 检测敏感词
        for pattern in self.word_patterns:
            matches = pattern.findall(text)
            if matches:
                found_words.extend(matches)
        
        # 去重
        found_words = list(set(found_words))
        
        # 计算风险等级和置信度
        risk_level, confidence = self._calculate_risk_level(text, found_words)
        
        # 判断是否安全
        is_safe = len(found_words) == 0
        
        details = {
            "text_length": len(text),
            "sensitive_word_count": len(found_words),
            "detection_method": "pattern_matching"
        }
        
        return DetectionResult(
            is_safe=is_safe,
            sensitive_words=found_words,
            risk_level=risk_level,
            confidence=confidence,
            details=details
        )
    
    def _api_detect(self, text: str) -> DetectionResult:
        """
        API检测
        
        Args:
            text: 待检测的文本
            
        Returns:
            DetectionResult: 检测结果
        """
        is_safe, risk_level, confidence, details = self.api_detector.detect(text)
        
        return DetectionResult(
            is_safe=is_safe,
            sensitive_words=[],  # API检测不返回具体敏感词
            risk_level=risk_level,
            confidence=confidence,
            details=details
        )
    
    def _combine_results(self, local_result: DetectionResult, api_result: DetectionResult) -> DetectionResult:
        """
        合并本地检测和API检测结果
        
        Args:
            local_result: 本地检测结果
            api_result: API检测结果
            
        Returns:
            DetectionResult: 合并后的检测结果
        """
        # 获取权重配置
        local_weight = DUAL_DETECTION_CONFIG.get("local_weight", 0.3)
        api_weight = DUAL_DETECTION_CONFIG.get("api_weight", 0.7)
        min_confidence = DUAL_DETECTION_CONFIG.get("min_confidence", 0.6)
        
        # 计算加权置信度
        combined_confidence = (local_result.confidence * local_weight + 
                             api_result.confidence * api_weight)
        
        # 确定最终风险等级
        if not local_result.is_safe or not api_result.is_safe:
            # 任一检测认为不安全，则不安全
            final_is_safe = False
            final_risk_level = "high" if (local_result.risk_level == "high" or 
                                        api_result.risk_level == "high") else "medium"
        else:
            # 都认为安全，则安全
            final_is_safe = True
            final_risk_level = "safe"
        
        # 合并敏感词列表
        combined_sensitive_words = local_result.sensitive_words.copy()
        
        # 合并详细信息
        combined_details = {
            "local_result": {
                "is_safe": local_result.is_safe,
                "risk_level": local_result.risk_level,
                "confidence": local_result.confidence,
                "sensitive_words": local_result.sensitive_words
            },
            "api_result": {
                "is_safe": api_result.is_safe,
                "risk_level": api_result.risk_level,
                "confidence": api_result.confidence,
                "details": api_result.details
            },
            "detection_method": "dual_detection",
            "local_weight": local_weight,
            "api_weight": api_weight,
            "combined_confidence": combined_confidence
        }
        
        return DetectionResult(
            is_safe=final_is_safe,
            sensitive_words=combined_sensitive_words,
            risk_level=final_risk_level,
            confidence=combined_confidence,
            details=combined_details
        )
    
    def _calculate_risk_level(self, text: str, found_words: List[str]) -> Tuple[str, float]:
        """
        计算风险等级和置信度
        
        Args:
            text: 原始文本
            found_words: 发现的敏感词列表
            
        Returns:
            Tuple[str, float]: (风险等级, 置信度)
        """
        if not found_words:
            return "safe", 1.0
        
        # 计算敏感词密度
        total_chars = len(text)
        sensitive_chars = sum(len(word) for word in found_words)
        density = sensitive_chars / total_chars if total_chars > 0 else 0
        
        # 根据敏感词数量和密度确定风险等级
        if len(found_words) >= 5 or density > 0.1:
            risk_level = "high"
            confidence = min(0.95, 0.7 + density * 2)
        elif len(found_words) >= 2 or density > 0.05:
            risk_level = "medium"
            confidence = min(0.85, 0.6 + density * 3)
        else:
            risk_level = "low"
            confidence = min(0.75, 0.5 + density * 4)
        
        return risk_level, confidence
    
    def is_safe_for_llm(self, text: str) -> bool:
        """
        判断文本是否安全可以作为大语言模型的输入
        
        Args:
            text: 待检测的文本
            
        Returns:
            bool: True表示安全，False表示不安全
        """
        result = self.detect(text)
        return result.is_safe
    
    def get_sensitive_words(self) -> List[str]:
        """
        获取所有敏感词列表
        
        Returns:
            List[str]: 敏感词列表
        """
        return list(self.sensitive_words)
    
    def add_sensitive_word(self, word: str):
        """
        添加敏感词
        
        Args:
            word: 要添加的敏感词
        """
        if word and word not in self.sensitive_words:
            self.sensitive_words.add(word)
            pattern = re.escape(word)
            self.word_patterns.append(re.compile(pattern, re.IGNORECASE))
            logger.info(f"添加敏感词: {word}")
    
    def remove_sensitive_word(self, word: str):
        """
        移除敏感词
        
        Args:
            word: 要移除的敏感词
        """
        if word in self.sensitive_words:
            self.sensitive_words.remove(word)
            # 重新构建模式列表
            self.word_patterns = []
            for w in self.sensitive_words:
                pattern = re.escape(w)
                self.word_patterns.append(re.compile(pattern, re.IGNORECASE))
            logger.info(f"移除敏感词: {word}")
    
    def batch_detect(self, texts: List[str]) -> List[DetectionResult]:
        """
        批量检测文本
        
        Args:
            texts: 待检测的文本列表
            
        Returns:
            List[DetectionResult]: 检测结果列表
        """
        results = []
        for text in texts:
            results.append(self.detect(text))
        return results
    
    def set_api_detection(self, enable: bool = True):
        """
        启用或禁用API检测
        
        Args:
            enable: 是否启用API检测
        """
        self.enable_api_detection = enable
        if enable and not self.api_detector:
            try:
                api_key = API_CONFIG.get("api_key")
                secret_key = API_CONFIG.get("secret_key")
                self.api_detector = APIDetector(api_key=api_key, secret_key=secret_key)
                if self.api_detector.is_available():
                    logger.info("API检测已启用")
                else:
                    logger.warning("API检测器不可用")
            except Exception as e:
                logger.error(f"启用API检测失败: {e}")
        elif not enable:
            logger.info("API检测已禁用")
    
    def is_api_available(self) -> bool:
        """
        检查API检测是否可用
        
        Returns:
            bool: True表示可用，False表示不可用
        """
        return self.api_detector is not None and self.api_detector.is_available()
    
    def get_detection_method(self) -> str:
        """
        获取当前检测方法
        
        Returns:
            str: 检测方法描述
        """
        if self.enable_api_detection and self.is_api_available():
            return "双重检测（本地+API）"
        else:
            return "本地检测" 