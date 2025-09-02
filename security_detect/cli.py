#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
敏感词检测库命令行工具
"""

import argparse
import sys
import json
from pathlib import Path
from security_detector import SecurityDetector


def detect_text(text, detector, output_format='text'):
    """检测单个文本"""
    result = detector.detect(text)
    
    if output_format == 'json':
        return json.dumps({
            'text': text,
            'is_safe': result.is_safe,
            'risk_level': result.risk_level,
            'confidence': result.confidence,
            'sensitive_words': result.sensitive_words,
            'details': result.details
        }, ensure_ascii=False, indent=2)
    else:
        status = "✅ 安全" if result.is_safe else "❌ 不安全"
        output = f"文本: {text}\n"
        output += f"状态: {status}\n"
        output += f"风险等级: {result.risk_level}\n"
        output += f"置信度: {result.confidence:.2f}\n"
        if result.sensitive_words:
            output += f"发现的敏感词: {', '.join(result.sensitive_words)}\n"
        return output


def detect_file(file_path, detector, output_format='text'):
    """检测文件中的文本"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        return detect_text(text, detector, output_format)
    except FileNotFoundError:
        return f"错误: 文件 {file_path} 不存在"
    except Exception as e:
        return f"错误: 读取文件失败 - {e}"


def batch_detect_file(file_path, detector, output_format='text'):
    """批量检测文件中的多行文本"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            texts = [line.strip() for line in f if line.strip()]
        
        results = detector.batch_detect(texts)
        
        if output_format == 'json':
            output_data = []
            for text, result in zip(texts, results):
                output_data.append({
                    'text': text,
                    'is_safe': result.is_safe,
                    'risk_level': result.risk_level,
                    'confidence': result.confidence,
                    'sensitive_words': result.sensitive_words
                })
            return json.dumps(output_data, ensure_ascii=False, indent=2)
        else:
            output = f"批量检测结果 (共 {len(texts)} 个文本):\n"
            output += "=" * 50 + "\n"
            for i, (text, result) in enumerate(zip(texts, results), 1):
                status = "✅ 安全" if result.is_safe else "❌ 不安全"
                output += f"{i}. {text[:50]}{'...' if len(text) > 50 else ''}\n"
                output += f"   状态: {status} | 风险等级: {result.risk_level}\n"
                if result.sensitive_words:
                    output += f"   敏感词: {', '.join(result.sensitive_words)}\n"
                output += "\n"
            return output
            
    except FileNotFoundError:
        return f"错误: 文件 {file_path} 不存在"
    except Exception as e:
        return f"错误: 读取文件失败 - {e}"


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="敏感词检测命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s -t "这是一个测试文本"
  %(prog)s -f input.txt
  %(prog)s -b batch_input.txt
  %(prog)s -t "测试文本" --format json
  %(prog)s -w custom_words.txt -t "测试文本"
        """
    )
    
    # 输入参数
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '-t', '--text',
        help='要检测的文本'
    )
    input_group.add_argument(
        '-f', '--file',
        help='要检测的文件路径（单文件检测）'
    )
    input_group.add_argument(
        '-b', '--batch',
        help='要批量检测的文件路径（每行一个文本）'
    )
    
    # 可选参数
    parser.add_argument(
        '-w', '--words',
        help='自定义敏感词表文件路径'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='输出格式 (默认: text)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='敏感词检测库 v1.0.0'
    )
    
    args = parser.parse_args()
    
    try:
        # 初始化检测器
        detector = SecurityDetector(args.words)
        
        # 执行检测
        if args.text:
            result = detect_text(args.text, detector, args.format)
        elif args.file:
            result = detect_file(args.file, detector, args.format)
        elif args.batch:
            result = batch_detect_file(args.batch, detector, args.format)
        else:
            parser.print_help()
            return
        
        print(result)
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 