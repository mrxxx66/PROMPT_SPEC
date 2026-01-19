#!/bin/bash
# 自动检测和修复构建问题的脚本

set -e

echo "自动检测和修复系统启动"

# 检查是否提供了API密钥（如果需要使用AI服务）
if [ -z "$SHENGSUAN_API_KEY" ]; then
    echo "警告: 未设置SHENGSUAN_API_KEY环境变量，跳过AI分析功能"
    echo "如需启用AI分析，请设置SHENGSUAN_API_KEY环境变量"
fi

# 检查Dobby库是否存在
if [ ! -f "jni/external/libdobby.a" ]; then
    echo "检测到问题: 缺少Dobby库文件"
    
    # 创建external目录
    mkdir -p jni/external
    
    echo "正在尝试下载Dobby库..."
    if command -v wget &> /dev/null; then
        # 尝试从GitHub下载预编译的Dobby库（注意：真实的预编译库链接需要根据实际情况调整）
        echo "系统中有wget命令，但没有可用的预编译Dobby库链接，跳过自动下载"
        echo "请访问 https://github.com/jmpews/Dobby 并手动下载适用于Android arm64的预编译库"
    elif command -v curl &> /dev/null; then
        echo "系统中有curl命令，但没有可用的预编译Dobby库链接，跳过自动下载"
        echo "请访问 https://github.com/jmpews/Dobby 并手动下载适用于Android arm64的预编译库"
    else
        echo "系统中没有wget或curl命令，请手动下载Dobby库"
    fi
else
    echo "Dobby库已存在"
fi

# 检查NDK是否已安装
if [ -z "$ANDROID_NDK_HOME" ] && [ -z "$NDK_HOME" ]; then
    echo "错误: 未设置ANDROID_NDK_HOME或NDK_HOME环境变量"
    echo "请安装NDK并设置环境变量"
    exit 1
else
    echo "NDK环境已配置"
fi

# 尝试构建项目
echo "开始构建项目..."
./build.sh

echo "构建完成!"