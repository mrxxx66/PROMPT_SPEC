#!/bin/bash
# 模拟构建失败的脚本，用于测试自动修复功能

echo "模拟构建过程..."

# 模拟Dobby库缺失错误
echo "Error: jni/external/libdobby.a: No such file or directory" >&2
echo "Build failed due to missing Dobby library" >&2

# 返回非零退出码表示失败
exit 1