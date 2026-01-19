#!/bin/bash
# 触发云端构建的脚本

echo "准备触发云端构建..."

# 检查是否已有更改需要提交
if [[ $(git status --porcelain) ]]; then
    echo "检测到未提交的更改，正在提交..."
    git add .
    git commit -m "Auto: Prepare for build [skip ci]"
fi

# 获取当前时间戳作为版本号的一部分
TIMESTAMP=$(date +"%Y%m%d%H%M%S")

# 创建版本标签
TAG_NAME="v1.0.1-fix.${TIMESTAMP}"
echo "创建版本标签: ${TAG_NAME}"

git tag "${TAG_NAME}"

# 推送标签以触发构建
echo "推送标签以触发云端构建..."
git push origin "${TAG_NAME}"

echo "云端构建已触发，标签: ${TAG_NAME}"
echo "您可以前往 GitHub 仓库的 Actions 标签页查看构建进度"