#!/usr/bin/env python3
"""
自动检测和修复构建问题的脚本
此脚本用于检测并修复常见的构建问题，如缺少Dobby库
"""

import os
import sys
import subprocess
import json
import urllib.request
from pathlib import Path


def check_dobby_library():
    """检查Dobby库是否存在"""
    dobby_path = Path("jni/external/libdobby.a")
    return dobby_path.exists()


def download_dobby():
    """下载Dobby库的函数"""
    print("正在下载Dobby库...")
    
    # 创建external目录（如果不存在）
    external_dir = Path("jni/external")
    external_dir.mkdir(parents=True, exist_ok=True)
    
    # 尝试从GitHub获取Dobby库
    # 这里只是一个示例，实际使用时需要替换为有效的Dobby库下载链接
    try:
        # 检查是否安装了git
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        
        # 如果是首次下载，克隆整个Dobby项目并编译
        dobby_dir = external_dir / "Dobby"
        if not dobby_dir.exists():
            print("正在克隆Dobby项目...")
            subprocess.run([
                "git", "clone", "--depth=1", 
                "https://github.com/jmpews/Dobby.git", 
                str(dobby_dir)
            ], check=True)
        
        # 编译Dobby库（这里只是示意，实际编译过程可能更复杂）
        print("Dobby库已下载到", dobby_dir)
        print("请注意：Dobby库需要针对Android arm64平台进行交叉编译，这通常需要NDK")
        
        return True
    except subprocess.CalledProcessError:
        print("无法通过Git下载Dobby库")
        return False
    except FileNotFoundError:
        print("系统中未找到Git命令")
        return False


def check_ndk_installed():
    """检查NDK是否已安装并配置"""
    ndk_env = os.environ.get('ANDROID_NDK_HOME') or os.environ.get('NDK_HOME')
    if not ndk_env:
        print("警告: 未找到ANDROID_NDK_HOME或NDK_HOME环境变量")
        return False
    return True


def ai_analyze_error(error_msg):
    """使用AI分析构建错误"""
    print(f"正在分析错误: {error_msg}")
    
    # 根据错误消息类型提供修复建议
    if "libdobby.a" in error_msg.lower():
        print("AI分析结果: 构建失败原因是缺少Dobby库文件(libdobby.a)")
        print("修复建议: 下载适用于Android arm64架构的预编译Dobby库")
        return True
    
    # 这里可以扩展更多的错误分析逻辑
    print("AI分析结果: 未识别的错误类型")
    return False


def attempt_fix_build():
    """尝试修复构建问题"""
    print("开始自动检测和修复构建问题...")
    
    # 检查Dobby库
    if not check_dobby_library():
        print("检测到问题: 缺少Dobby库文件")
        
        # 尝试下载Dobby库
        if download_dobby():
            print("Dobby库下载成功!")
        else:
            print("无法自动下载Dobby库，请手动下载并放置到 jni/external/libdobby.a")
            print("下载链接: https://github.com/jmpews/Dobby")
            return False
    else:
        print("Dobby库已存在")
    
    # 检查NDK配置
    if not check_ndk_installed():
        print("警告: NDK未配置，请确保已安装NDK并设置了ANDROID_NDK_HOME环境变量")
        return False
    
    # 尝试重新构建
    print("尝试重新构建项目...")
    try:
        result = subprocess.run(['bash', 'build.sh'], check=True, capture_output=True, text=True)
        print("构建成功!")
        print(result.stdout[-500:])  # 打印最后500个字符的输出
        return True
    except subprocess.CalledProcessError as e:
        print("构建失败:")
        print(e.stderr)
        ai_analyze_error(e.stderr)
        return False


def main():
    """主函数"""
    print("自动检测和修复系统启动")
    
    # 尝试修复构建问题
    success = attempt_fix_build()
    
    if success:
        print("\n修复完成，项目构建成功!")
        return 0
    else:
        print("\n自动修复未能解决问题，请手动处理")
        return 1


if __name__ == "__main__":
    sys.exit(main())