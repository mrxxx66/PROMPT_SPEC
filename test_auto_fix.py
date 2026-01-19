#!/usr/bin/env python3
"""
测试自动修复系统的脚本
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def simulate_build_failure():
    """模拟构建失败"""
    print("模拟构建失败场景...")
    
    # 运行模拟失败的脚本
    result = subprocess.run(
        ['bash', 'simulate_build_failure.sh'],
        check=False,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("成功模拟构建失败，错误信息:")
        print(result.stderr)
        return result.stderr
    else:
        print("模拟失败脚本异常退出")
        return None


def run_auto_fix_on_failure(error_msg):
    """在失败时运行自动修复"""
    print("启动自动修复流程...")
    
    # 导入自动修复脚本
    sys.path.append('./scripts')
    from auto_fix_on_build_failure import ai_analyze_error
    
    # 使用AI分析错误
    ai_response = ai_analyze_error(error_msg)
    
    if ai_response:
        print("AI分析完成")
        return True
    else:
        print("AI分析失败或未配置")
        return False


def main():
    """主函数"""
    print("开始测试自动修复系统")
    
    # 模拟构建失败
    error_msg = simulate_build_failure()
    
    if error_msg:
        # 运行自动修复
        success = run_auto_fix_on_failure(error_msg)
        
        if success:
            print("\n自动修复系统测试成功！")
            print("系统能够在检测到构建失败时:")
            print("1. 捕获错误信息")
            print("2. 调用AI分析错误")
            print("3. 提供建议的修复方案")
        else:
            print("\n自动修复系统测试失败")
    else:
        print("未能成功模拟构建失败")


if __name__ == "__main__":
    main()