#!/bin/bash

# 敏感词检测库自动安装脚本
# 使用方法: ./install.sh [wheel_file_path]

set -e

echo "🔧 敏感词检测库安装脚本"
echo "================================"

# 检查Python版本
echo "📋 检查Python版本..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "当前Python版本: $python_version"

# 检查pip
echo "📋 检查pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 未找到，请先安装pip"
    exit 1
fi

# 确定wheel包路径
if [ $# -eq 1 ]; then
    WHEEL_PATH="$1"
else
    # 默认在当前目录查找
    WHEEL_PATH="security_detector-1.0.0-py3-none-any.whl"
fi

echo "📦 使用wheel包: $WHEEL_PATH"

# 检查wheel包是否存在
if [ ! -f "$WHEEL_PATH" ]; then
    echo "❌ Wheel包不存在: $WHEEL_PATH"
    echo "请确保wheel包在当前目录或指定正确的路径"
    exit 1
fi

# 检查是否已安装
echo "🔍 检查是否已安装..."
if pip3 list | grep -q "security-detector"; then
    echo "⚠️  检测到已安装的版本，将进行升级..."
    UPGRADE_FLAG="--upgrade"
else
    UPGRADE_FLAG=""
fi

# 安装库
echo "📥 开始安装..."
pip3 install $UPGRADE_FLAG "$WHEEL_PATH"

# 验证安装
echo "✅ 验证安装..."
python3 -c "
try:
    from security_detector import SecurityDetector
    print('✅ 库导入成功')
    
    detector = SecurityDetector()
    result = detector.detect('测试文本')
    print(f'✅ 功能测试成功: {result.is_safe}')
    
except Exception as e:
    print(f'❌ 安装验证失败: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 安装成功！"
    echo "================================"
    echo "使用示例:"
    echo "  python3 -c \"from security_detector import SecurityDetector; detector = SecurityDetector(); result = detector.detect('测试文本'); print(result.is_safe)\""
    echo ""
    echo "更多信息请查看:"
    echo "  - README.md: 项目说明"
    echo "  - QUICKSTART.md: 快速开始"
    echo "  - INSTALLATION_GUIDE.md: 详细安装指南"
else
    echo "❌ 安装验证失败"
    exit 1
fi 