@echo off
setlocal enabledelayedexpansion

echo 🔧 敏感词检测库安装脚本
echo ================================

REM 检查Python版本
echo 📋 检查Python版本...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未找到，请先安装Python
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo 当前Python版本: %PYTHON_VERSION%

REM 检查pip
echo 📋 检查pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip未找到，请先安装pip
    pause
    exit /b 1
)

REM 确定wheel包路径
if "%~1"=="" (
    set WHEEL_PATH=security_detector-1.0.0-py3-none-any.whl
) else (
    set WHEEL_PATH=%~1
)

echo 📦 使用wheel包: %WHEEL_PATH%

REM 检查wheel包是否存在
if not exist "%WHEEL_PATH%" (
    echo ❌ Wheel包不存在: %WHEEL_PATH%
    echo 请确保wheel包在当前目录或指定正确的路径
    pause
    exit /b 1
)

REM 检查是否已安装
echo 🔍 检查是否已安装...
python -m pip list | findstr "security-detector" >nul
if not errorlevel 1 (
    echo ⚠️  检测到已安装的版本，将进行升级...
    set UPGRADE_FLAG=--upgrade
) else (
    set UPGRADE_FLAG=
)

REM 安装库
echo 📥 开始安装...
python -m pip install %UPGRADE_FLAG% "%WHEEL_PATH%"

REM 验证安装
echo ✅ 验证安装...
python -c "from security_detector import SecurityDetector; print('✅ 库导入成功'); detector = SecurityDetector(); result = detector.detect('测试文本'); print(f'✅ 功能测试成功: {result.is_safe}')"

if errorlevel 1 (
    echo ❌ 安装验证失败
    pause
    exit /b 1
)

echo.
echo 🎉 安装成功！
echo ================================
echo 使用示例:
echo   python -c "from security_detector import SecurityDetector; detector = SecurityDetector(); result = detector.detect('测试文本'); print(result.is_safe)"
echo.
echo 更多信息请查看:
echo   - README.md: 项目说明
echo   - QUICKSTART.md: 快速开始
echo   - INSTALLATION_GUIDE.md: 详细安装指南

pause 