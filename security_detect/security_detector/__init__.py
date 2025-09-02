#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
敏感词检测库
用于检测文本中是否包含敏感词，判断文本是否安全可以作为大语言模型的输入
"""

from .security_detector import SecurityDetector, DetectionResult

__version__ = "1.0.0"
__author__ = "Security Detection Team"
__description__ = "敏感词检测库，专门为大语言模型输入安全检查而设计"

__all__ = [
    "SecurityDetector",
    "DetectionResult",
    "__version__",
    "__author__",
    "__description__"
] 