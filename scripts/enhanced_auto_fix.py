#!/usr/bin/env python3
"""
增强版自动检测和修复构建问题的脚本
此脚本用于检测并修复常见的构建问题，如缺少Dobby库和NDK配置问题
"""

import os
import sys
import subprocess
import json
import urllib.request
from pathlib import Path
import platform


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
    
    # 检查Dobby是否已经下载
    dobby_dir = external_dir / "Dobby"
    if not dobby_dir.exists():
        try:
            # 克隆Dobby项目
            print("正在克隆Dobby项目...")
            subprocess.run([
                "git", "clone", "--depth=1", 
                "https://github.com/jmpews/Dobby.git", 
                str(dobby_dir)
            ], check=True)
            print("Dobby库已下载到", dobby_dir)
        except subprocess.CalledProcessError:
            print("无法通过Git下载Dobby库")
            return False
        except FileNotFoundError:
            print("系统中未找到Git命令")
            return False
    
    return True


def check_ndk_installed():
    """检查NDK是否已安装并配置"""
    # 检查环境变量
    ndk_env = os.environ.get('ANDROID_NDK_HOME') or os.environ.get('NDK_HOME')
    
    if ndk_env and Path(ndk_env).exists():
        print(f"NDK已配置: {ndk_env}")
        return True
    
    # 在某些常见位置查找NDK
    possible_paths = [
        Path.home() / "Android" / "Sdk" / "ndk",
        Path.home() / "Library" / "Android" / "sdk" / "ndk",
        Path("C:") / "Android" / "Sdk" / "ndk",
        Path("C:") / "android-ndk-*",  # Windows通配符
    ]
    
    for path in possible_paths:
        if path.exists():
            # 如果是通配符路径，展开它
            if '*' in str(path):
                expanded = list(Path(path.parent).glob(path.name))
                if expanded:
                    # 使用最新的NDK版本
                    latest_ndk = sorted(expanded, key=os.path.getmtime, reverse=True)[0]
                    os.environ['ANDROID_NDK_HOME'] = str(latest_ndk)
                    print(f"发现NDK: {latest_ndk}")
                    return True
            else:
                os.environ['ANDROID_NDK_HOME'] = str(path)
                print(f"发现NDK: {path}")
                return True
    
    print("警告: 未找到ANDROID_NDK_HOME或NDK_HOME环境变量")
    return False


def check_build_tools():
    """检查构建工具是否安装"""
    tools_needed = ['git', 'make', 'cmake']
    missing_tools = []
    
    for tool in tools_needed:
        try:
            subprocess.run([tool, '--version'], 
                         check=True, 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"警告: 缺少构建工具: {', '.join(missing_tools)}")
        return False
    
    print("构建工具齐全")
    return True


def compile_dobby_if_needed():
    """如果需要，编译Dobby库"""
    # 检查是否已经有预编译的库
    dobby_lib_path = Path("jni/external/libdobby.a")
    if dobby_lib_path.exists():
        print("Dobby库已存在，跳过编译")
        return True
    
    # 检查Dobby源码是否存在
    dobby_src_path = Path("jni/external/Dobby")
    if not dobby_src_path.exists():
        print("错误: Dobby源码不存在")
        return False
    
    print("开始编译Dobby库...")
    
    try:
        # 进入Dobby目录
        current_dir = os.getcwd()
        os.chdir(dobby_src_path)
        
        # 创建构建目录
        build_dir = Path("build")
        build_dir.mkdir(exist_ok=True)
        
        # 获取NDK路径
        ndk_path = os.environ.get('ANDROID_NDK_HOME') or os.environ.get('NDK_HOME')
        if not ndk_path:
            print("错误: 未设置NDK路径")
            return False
        
        # 运行CMake配置
        cmake_cmd = [
            'cmake', '.', '-B', 'build',
            f'-DCMAKE_TOOLCHAIN_FILE={ndk_path}/build/cmake/android.toolchain.cmake',
            '-DANDROID_ABI=arm64-v8a',
            '-DANDROID_PLATFORM=android-21'
        ]
        
        print("运行CMake配置...")
        result = subprocess.run(cmake_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"CMake配置失败: {result.stderr}")
            return False
        
        # 编译Dobby
        print("编译Dobby库...")
        make_cmd = ['cmake', '--build', 'build', '--parallel']
        result = subprocess.run(make_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Dobby编译失败: {result.stderr}")
            return False
        
        # 将编译好的库复制到正确的位置
        compiled_lib = build_dir / "lib" / "arm64-v8a" / "libdobby.a"
        if compiled_lib.exists():
            target_dir = Path("../../../../../libs/arm64-v8a/")
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / "libdobby.a"
            
            import shutil
            shutil.copy(compiled_lib, target_path)
            print(f"Dobby库已编译并复制到: {target_path}")
            
            # 同时复制到jni/external/libdobby.a
            ext_target = Path("../libdobby.a")
            shutil.copy(compiled_lib, ext_target)
            print(f"Dobby库已复制到: {ext_target}")
        else:
            print("错误: 编译后的库文件不存在")
            return False
        
        os.chdir(current_dir)
        return True
    except Exception as e:
        print(f"编译Dobby时发生错误: {str(e)}")
        return False


def attempt_fix_build():
    """尝试修复构建问题"""
    print("开始自动检测和修复构建问题...")
    
    # 检查构建工具
    if not check_build_tools():
        print("请安装所需的构建工具后再试")
        return False
    
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
        print("错误: NDK未配置，请安装NDK并设置ANDROID_NDK_HOME环境变量")
        print("参考文档: NDK_SETUP_GUIDE.md")
        return False
    
    # 编译Dobby库（如果需要）
    if not compile_dobby_if_needed():
        print("Dobby库编译失败")
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
        return False


def main():
    """主函数"""
    print("增强版自动检测和修复系统启动")
    
    # 尝试修复构建问题
    success = attempt_fix_build()
    
    if success:
        print("\n修复完成，项目构建成功!")
        return 0
    else:
        print("\n自动修复未能解决问题，请参考以下步骤手动处理:")
        print("- 查看 NDK_SETUP_GUIDE.md 了解如何配置NDK")
        print("- 查看 USER_GUIDE.md 了解完整的构建流程")
        return 1


if __name__ == "__main__":
    sys.exit(main())