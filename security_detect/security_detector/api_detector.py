#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API检测模块
使用百度AI API进行文本内容审核
"""

import sys
import json
import base64
import logging
from typing import Dict, Optional, Tuple
from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import urlencode
import ssl

# 防止https证书校验不正确
ssl._create_default_https_context = ssl._create_unverified_context

logger = logging.getLogger(__name__)


class APIDetector:
    """API检测器，使用百度AI API进行文本审核"""
    
    def __init__(self, api_key: str = None, secret_key: str = None):
        """
        初始化API检测器
        
        Args:
            api_key: 百度AI API Key
            secret_key: 百度AI Secret Key
        """
        # 默认使用提供的API密钥，也可以从环境变量或配置文件读取
        self.api_key = api_key or 'esM4mXxoLIEkVOnGxR9JuFVe'
        self.secret_key = secret_key or 'DQg0XMh8KkUjUenlpIZAPnthGJQI8slJ'
        
        self.token_url = 'https://aip.baidubce.com/oauth/2.0/token'
        self.text_censor_url = "https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined"
        
        self.access_token = None
        self._fetch_token()
    
    def _fetch_token(self):
        """获取访问令牌"""
        try:
            params = {
                'grant_type': 'client_credentials',
                'client_id': self.api_key,
                'client_secret': self.secret_key
            }
            post_data = urlencode(params).encode('utf-8')
            req = Request(self.token_url, post_data)
            
            with urlopen(req, timeout=10) as f:
                result_str = f.read().decode()
            
            result = json.loads(result_str)
            
            if 'access_token' in result and 'scope' in result:
                if 'brain_all_scope' not in result['scope'].split(' '):
                    logger.warning('API权限不足，请确保已开通文本审核服务')
                self.access_token = result['access_token']
                logger.info("成功获取API访问令牌")
            else:
                logger.error('获取访问令牌失败，请检查API_KEY和SECRET_KEY')
                self.access_token = None
                
        except Exception as e:
            logger.error(f"获取访问令牌失败: {e}")
            self.access_token = None
    
    def _request(self, url: str, data: str) -> Optional[str]:
        """
        发送API请求
        
        Args:
            url: 请求URL
            data: 请求数据
            
        Returns:
            Optional[str]: 响应结果
        """
        try:
            req = Request(url, data.encode('utf-8'))
            with urlopen(req, timeout=10) as f:
                result_str = f.read().decode()
            return result_str
        except URLError as err:
            logger.error(f"API请求失败: {err}")
            return None
        except Exception as e:
            logger.error(f"API请求异常: {e}")
            return None
    
    def detect(self, text: str) -> Tuple[bool, str, float, Dict]:
        """
        使用API检测文本
        
        Args:
            text: 待检测的文本
            
        Returns:
            Tuple[bool, str, float, Dict]: (是否安全, 风险等级, 置信度, 详细信息)
        """
        if not self.access_token:
            logger.warning("API访问令牌无效，跳过API检测")
            return True, "unknown", 0.0, {"error": "API token invalid"}
        
        if not text or len(text.strip()) == 0:
            return True, "safe", 1.0, {"reason": "空文本"}
        
        try:
            # 拼接文本审核URL
            text_url = f"{self.text_censor_url}?access_token={self.access_token}"
            
            # 发送请求
            result_str = self._request(text_url, urlencode({'text': text}))
            
            if not result_str:
                logger.warning("API请求失败，跳过API检测")
                return True, "unknown", 0.0, {"error": "API request failed"}
            
            # 解析结果
            result = json.loads(result_str)
            
            # 分析API返回结果
            is_safe, risk_level, confidence, details = self._parse_api_result(result)
            
            return is_safe, risk_level, confidence, details
            
        except Exception as e:
            logger.error(f"API检测异常: {e}")
            return True, "unknown", 0.0, {"error": str(e)}
    
    def _parse_api_result(self, result: Dict) -> Tuple[bool, str, float, Dict]:
        """
        解析API返回结果
        
        Args:
            result: API返回的JSON结果
            
        Returns:
            Tuple[bool, str, float, Dict]: (是否安全, 风险等级, 置信度, 详细信息)
        """
        try:
            # 检查是否有错误
            if 'error_code' in result:
                logger.error(f"API错误: {result.get('error_msg', 'Unknown error')}")
                return True, "unknown", 0.0, {"error": result.get('error_msg', 'Unknown error')}
            
            # 获取结论
            conclusion = result.get('conclusion', '')
            conclusion_type = result.get('conclusionType', 1)
            
            # 获取详细信息
            data = result.get('data', [])
            
            # 判断是否安全
            # conclusionType: 1-合规, 2-不确定, 3-不合规, 4-审核失败
            if conclusion_type == 1:
                is_safe = True
                risk_level = "safe"
                confidence = 0.9
            elif conclusion_type == 2:
                is_safe = True  # 不确定时倾向于安全
                risk_level = "low"
                confidence = 0.6
            elif conclusion_type == 3:
                is_safe = False
                risk_level = "high"
                confidence = 0.95
            else:  # conclusion_type == 4
                is_safe = True
                risk_level = "unknown"
                confidence = 0.0
            
            # 构建详细信息
            details = {
                "conclusion": conclusion,
                "conclusion_type": conclusion_type,
                "api_data": data,
                "detection_method": "api"
            }
            
            # 如果有具体的违规信息，调整置信度
            if data and len(data) > 0:
                details["violations"] = data
                if conclusion_type == 3:
                    confidence = min(0.98, confidence + 0.03)
            
            return is_safe, risk_level, confidence, details
            
        except Exception as e:
            logger.error(f"解析API结果失败: {e}")
            return True, "unknown", 0.0, {"error": f"Parse error: {str(e)}"}
    
    def is_available(self) -> bool:
        """
        检查API是否可用
        
        Returns:
            bool: True表示可用，False表示不可用
        """
        return self.access_token is not None 