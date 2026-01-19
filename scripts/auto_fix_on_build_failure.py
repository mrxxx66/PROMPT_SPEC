#!/usr/bin/env python3
"""
Build失败时的自动检测和修复脚本
此脚本监控构建过程并在失败时自动分析和修复问题
"""

import os
import sys
import subprocess
import json
import urllib.request
import re
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
    tools_needed = ['git']
    missing_tools = []
    
    # 根据平台确定需要的工具
    if platform.system().lower() == "windows":
        tools_needed.extend(['make'])  # Windows上可能使用mingw或其他make工具
    else:
        tools_needed.extend(['make', 'cmake'])
    
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
            # 尝试不同的NDK路径配置
            alt_cmake_cmd = [
                'cmake', '-H.', '-Bbuild',
                f'-DCMAKE_TOOLCHAIN_FILE={ndk_path}/build/cmake/android.toolchain.cmake',
                '-DANDROID_ABI=arm64-v8a',
                '-DANDROID_PLATFORM=android-21',
                '-DCMAKE_BUILD_TYPE=Release'
            ]
            result = subprocess.run(alt_cmake_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"备用CMake配置也失败: {result.stderr}")
                return False
        
        # 编译Dobby
        print("编译Dobby库...")
        make_cmd = ['cmake', '--build', 'build', '--parallel']
        result = subprocess.run(make_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Dobby编译失败: {result.stderr}")
            return False
        
        # 将编译好的库复制到正确的位置
        compiled_lib_path = None
        # 查找编译好的库文件
        for root, dirs, files in os.walk('build'):
            for file in files:
                if file == 'libdobby.a':
                    compiled_lib_path = Path(root) / file
                    break
            if compiled_lib_path:
                break
        
        if compiled_lib_path:
            target_dir = Path("../../../../../libs/arm64-v8a/")
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / "libdobby.a"
            
            import shutil
            shutil.copy(compiled_lib_path, target_path)
            print(f"Dobby库已编译并复制到: {target_path}")
            
            # 同时复制到jni/external/libdobby.a
            ext_target = Path("../libdobby.a")
            shutil.copy(compiled_lib_path, ext_target)
            print(f"Dobby库已复制到: {ext_target}")
        else:
            print("错误: 编译后的库文件不存在")
            return False
        
        os.chdir(current_dir)
        return True
    except Exception as e:
        print(f"编译Dobby时发生错误: {str(e)}")
        return False


def ai_analyze_error(error_msg):
    """使用AI分析构建错误"""
    print(f"正在分析错误...")
    
    # 获取环境变量中的API配置
    api_key = os.environ.get('SHENGSUAN_API_KEY')
    api_url = os.environ.get('SHENGSUAN_API_URL', 'https://api.shengsuan.cloud/v1/chat/completions')
    model = os.environ.get('SHENGSUAN_MODEL', 'deepseek/deepseek-v3.2')
    
    if not api_key:
        print("警告: 未设置SHENGSUAN_API_KEY环境变量，跳过AI分析功能")
        print("要启用AI分析，请设置SHENGSUAN_API_KEY环境变量")
        return None
    
    # 准备发送给AI的提示
    prompt = f"""
    你是一个专业的Android NDK和C++构建专家。
    请分析以下构建错误并提供修复建议：
    
    错误信息:
    {error_msg}
    
    请提供具体的修复步骤。
    """
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    try:
        req = urllib.request.Request(api_url, 
                                   data=json.dumps(data).encode('utf-8'), 
                                   headers=headers)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        
        ai_response = result['choices'][0]['message']['content']
        print(f"AI分析结果:\n{ai_response}")
        
        return ai_response
    except Exception as e:
        print(f"AI分析失败: {str(e)}")
        return None


def attempt_build():
    """尝试构建项目"""
    print("开始构建项目...")
    try:
        # 使用subprocess运行构建脚本，捕获输出
        result = subprocess.run(
            ['bash', 'build.sh'], 
            check=False, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            print("构建成功!")
            print(result.stdout[-500:])  # 打印最后500个字符的输出
            return True
        else:
            print("构建失败:")
            print(result.stderr)
            
            # 分析错误
            error_analysis = ai_analyze_error(result.stderr)
            
            return False, result.stderr
    except FileNotFoundError:
        # 如果bash不可用，尝试powershell
        print("bash命令不可用，尝试PowerShell...")
        try:
            result = subprocess.run(
                ['powershell', './build.sh'], 
                check=False, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                print("构建成功!")
                print(result.stdout[-500:])
                return True
            else:
                print("构建失败:")
                print(result.stderr)
                
                # 分析错误
                error_analysis = ai_analyze_error(result.stderr)
                
                return False, result.stderr
        except FileNotFoundError:
            print("PowerShell命令也不可用")
            return False, "无法执行构建脚本"


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
        print("错误: NDK未配置，请安装NDK并设置ANDROID_NDK_HOME环境变量")
        print("参考文档: NDK_SETUP_GUIDE.md")
        return False
    
    # 编译Dobby库（如果需要）
    if not compile_dobby_if_needed():
        print("Dobby库编译失败")
        return False
    
    # 尝试构建
    build_result = attempt_build()
    
    if isinstance(build_result, tuple):
        # 构建失败，返回了错误信息
        success, error_msg = build_result
        print("\n检测到构建失败，正在尝试修复...")
        
        # 尝试针对性修复
        fixes_applied = 0
        max_fix_attempts = 3
        
        while not success and fixes_applied < max_fix_attempts:
            fixes_applied += 1
            print(f"\n正在进行第 {fixes_applied} 次修复尝试...")
            
            # 根据错误消息尝试修复
            if "arm64-v8a" in error_msg.lower():
                print("检测到ARM64架构相关错误，尝试修复...")
                # ARM64特定修复
                success, error_msg = attempt_build()
            elif "dobby" in error_msg.lower() or "libdobby" in error_msg.lower():
                print("检测到Dobby库相关错误，重新编译Dobby...")
                if compile_dobby_if_needed():
                    success, error_msg = attempt_build()
                else:
                    print("Dobby库重新编译失败")
                    break
            elif "ndk" in error_msg.lower():
                print("检测到NDK相关错误...")
                success, error_msg = attempt_build()
            else:
                print("未知错误类型，尝试AI分析...")
                ai_analysis = ai_analyze_error(error_msg)
                if ai_analysis:
                    print("AI分析已完成，但自动修复需要人工介入")
                success = False
                break
        
        return success
    else:
        # 构建成功
        return build_result


def main():
    """主函数"""
    print("Build失败自动检测和修复系统启动")
    print("此系统将在检测到构建失败时自动分析和修复问题")
    
    # 尝试修复构建问题
    success = attempt_fix_build()
    
    if success:
        print("\n修复完成，项目构建成功!")
        print("如果需要触发云端构建，请运行: python trigger_build_remotely.py")
        return 0
    else:
        print("\n自动修复未能解决问题")
        print("请参考以下步骤手动处理:")
        print("- 查看 NDK_SETUP_GUIDE.md 了解如何配置NDK")
        print("- 查看 USER_GUIDE.md 了解完整的构建流程")
        print("- 检查错误日志并手动修复")
        return 1


def trigger_remote_build():
    """创建远程构建触发器"""
    script_content = '''#!/usr/bin/env python3
import subprocess
import os
from datetime import datetime

def trigger_build():
    """触发远程构建"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    tag_name = f"v1.0.1-build.{timestamp}"
    
    print(f"创建版本标签: {tag_name}")
    
    # 创建标签
    result = subprocess.run(["git", "tag", tag_name], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"创建标签失败: {result.stderr}")
        return False
    
    # 推送标签
    result = subprocess.run(["git", "push", "origin", tag_name], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"推送标签失败: {result.stderr}")
        return False
    
    print(f"远程构建已触发，标签: {tag_name}")
    print("您可以前往 GitHub 仓库的 Actions 标签页查看构建进度")
    return True

if __name__ == "__main__":
    trigger_build()
'''
    
    with open('trigger_build_remotely.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("已创建远程构建触发脚本: trigger_build_remotely.py")


if __name__ == "__main__":
    # 创建远程构建触发器
    trigger_remote_build()
    
    # 运行主程序
    sys.exit(main())