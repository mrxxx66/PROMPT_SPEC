#!/usr/bin/env python3
"""
构建失败监控脚本
监控构建过程并在失败时自动启动修复流程
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path


def run_build_and_monitor():
    """运行构建并监控结果"""
    print("开始构建并监控...")
    
    try:
        # 运行构建脚本
        result = subprocess.run(
            ['bash', '../build.sh'],
            cwd=os.path.dirname(__file__),
            check=False,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("检测到构建失败，错误信息:")
            print(result.stderr)
            return result.stderr
        else:
            print("构建成功!")
            print(result.stdout)
            return None
            
    except FileNotFoundError:
        # 尝试PowerShell
        try:
            result = subprocess.run(
                ['powershell', '../build.sh'],
                cwd=os.path.dirname(__file__),
                check=False,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("检测到构建失败，错误信息:")
                print(result.stderr)
                return result.stderr
            else:
                print("构建成功!")
                print(result.stdout)
                return None
        except FileNotFoundError:
            print("找不到bash或PowerShell命令")
            return "系统命令不可用"


def handle_build_failure(error_msg):
    """处理构建失败"""
    print("构建失败，启动自动修复流程...")
    
    # 导入自动修复脚本并运行
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from scripts.auto_fix_on_build_failure import attempt_fix_build
    
    # 运行修复
    success = attempt_fix_build()
    
    if success:
        print("自动修复成功！")
        
        # 再次尝试构建
        print("再次尝试构建...")
        retry_result = run_build_and_monitor()
        
        if retry_result is None:
            print("重试构建成功！")
            return True
        else:
            print("重试构建仍然失败")
            return False
    else:
        print("自动修复失败")
        return False


def main():
    """主函数"""
    print("构建失败监控系统启动")
    
    # 运行构建并监控
    error_msg = run_build_and_monitor()
    
    if error_msg:
        # 构建失败，启动修复流程
        handle_build_failure(error_msg)
    else:
        print("构建成功，无需修复")


if __name__ == "__main__":
    main()