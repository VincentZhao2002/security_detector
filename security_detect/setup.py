#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
敏感词检测库安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "敏感词检测库，专门为大语言模型输入安全检查而设计"

# 读取版本信息
def get_version():
    init_path = os.path.join(os.path.dirname(__file__), 'security_detector', '__init__.py')
    with open(init_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return '1.0.0'

setup(
    name="security-detector",
    version=get_version(),
    author="Security Detection Team",
    author_email="security@example.com",
    description="敏感词检测库，专门为大语言模型输入安全检查而设计",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/security-detector",
    packages=find_packages(include=['security_detector', 'security_detector.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Text Processing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "security-detector=cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["data/*.txt"],
    },
    keywords="security, sensitive words, content filtering, llm safety, text detection",
    project_urls={
        "Bug Reports": "https://github.com/your-username/security-detector/issues",
        "Source": "https://github.com/your-username/security-detector",
        "Documentation": "https://github.com/your-username/security-detector#readme",
    },
) 