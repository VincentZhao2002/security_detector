#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
敏感词检测库配置文件
"""

import os

# 默认敏感词表文件路径
DEFAULT_SENSITIVE_WORDS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    "data", 
    "word_bank.txt"
)

# 原始敏感词表文件路径（包含重复）
ORIGINAL_SENSITIVE_WORDS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    "data", 
    "merged_row_by_row_cleaned.txt"
)

# 检测配置
DETECTION_CONFIG = {
    # 风险等级阈值
    "risk_thresholds": {
        "high": {
            "word_count": 5,
            "density": 0.1
        },
        "medium": {
            "word_count": 2,
            "density": 0.05
        },
        "low": {
            "word_count": 1,
            "density": 0.01
        }
    },
    
    # 置信度计算参数
    "confidence_params": {
        "base_confidence": 0.5,
        "density_multiplier": 3,
        "max_confidence": 0.95
    },
    
    # 检测方法配置
    "detection_methods": {
        "pattern_matching": True,
        "fuzzy_matching": False,
        "case_sensitive": False
    }
}

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": None  # 如果设置为文件路径，日志会写入文件
}

# 性能配置
PERFORMANCE_CONFIG = {
    "enable_cache": True,
    "cache_size": 1000,
    "batch_size": 100
}

# API检测配置
API_CONFIG = {
    "enable_api_detection": True,
    "api_key": "esM4mXxoLIEkVOnGxR9JuFVe",
    "secret_key": "DQg0XMh8KkUjUenlpIZAPnthGJQI8slJ",
    "timeout": 10,
    "retry_count": 3,
    "fallback_to_local": True  # API失败时是否回退到本地检测
}

# 双重检测配置
DUAL_DETECTION_CONFIG = {
    "enable_dual_detection": True,
    "local_first": True,  # 是否优先使用本地检测
    "api_weight": 0.7,    # API检测权重
    "local_weight": 0.3,  # 本地检测权重
    "min_confidence": 0.6  # 最小置信度阈值
} 