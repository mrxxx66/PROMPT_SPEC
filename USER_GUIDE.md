# 用户指南

## 项目概述

这是一个HyperOS SF Bypass模块项目，用于绕过HyperOS的安全特性。项目使用Zygisk框架，并依赖Dobby库进行底层Hook操作。

## 构建要求

- Android NDK
- Dobby库 (libdobby.a)
- 支持arm64-v8a架构

## 自动检测和修复功能

本项目包含自动检测和修复功能，旨在解决常见的构建问题。

### 使用Python自动修复脚本

运行以下命令启动自动修复：

```bash
python scripts/auto_fix_build.py
```

此脚本将：
1. 检测Dobby库是否存在
2. 如果缺失则尝试下载
3. 检查NDK环境配置
4. 尝试重新构建项目
5. 如构建失败，使用AI分析错误原因

### 使用增强版自动修复脚本

运行以下命令启动增强版自动修复：

```bash
python scripts/enhanced_auto_fix.py
```

增强版脚本具有更多功能：
- 更全面的NDK检测
- 自动编译Dobby库
- 更详细的错误报告

### 构建失败时的自动修复

当构建失败时，运行以下命令：

```bash
python scripts/auto_fix_on_build_failure.py
```

此脚本将：
1. 捕获构建错误信息
2. 使用AI分析错误原因（需要配置API密钥）
3. 提供针对性的修复建议
4. 尝试自动修复常见问题

### 构建监控系统

运行以下命令启动构建监控：

```bash
python scripts/build_monitor.py
```

监控系统将：
- 运行构建脚本
- 检测构建是否成功
- 如果失败，自动启动修复流程

## 配置AI分析功能

要启用AI分析功能，需要配置以下环境变量：

```bash
# 设置胜算云API密钥
export SHENGSUAN_API_KEY="your_api_key_here"
# API地址（可选，默认为 https://api.shengsuan.cloud/v1/chat/completions）
export SHENGSUAN_API_URL="https://api.shengsuan.cloud/v1/chat/completions"
# 模型名称（可选，默认为 deepseek/deepseek-v3.2）
export SHENGSUAN_MODEL="deepseek/deepseek-v3.2"
```

配置后，自动修复脚本将能够使用AI分析构建错误并提供修复建议。

## 手动构建步骤

如果自动修复不成功，可以尝试手动构建：

1. 确保已安装Android NDK
2. 设置NDK环境变量：
   ```bash
   export ANDROID_NDK_HOME=/path/to/ndk
   ```
   
3. 下载Dobby库：
   - 访问 https://github.com/jmpews/Dobby
   - 下载或构建适用于Android arm64的libdobby.a
   - 将其放置在 jni/external/libdobby.a

4. 运行构建脚本：
   ```bash
   ./build.sh
   ```

## CI/CD集成

项目遵循自动化修复与CI/CD工作流协同规范，通过创建带`v`前缀的版本标签来触发构建流程：

```bash
git tag v1.0.1-build.[BUILD_NUMBER]
git push origin v1.0.1-build.[BUILD_NUMBER]
```

云端构建将自动运行，构建产物可通过Artifacts下载。

## 环境变量配置

项目支持以下环境变量配置：

- `SHENGSUAN_API_KEY`: 胜算云API密钥，用于AI驱动的错误分析
- `SHENGSUAN_API_URL`: API地址（可选，默认为 https://api.shengsuan.cloud/v1/chat/completions）
- `SHENGSUAN_MODEL`: 模型名称（可选，默认为 deepseek/deepseek-v3.2）

## 故障排除

常见问题及解决方案：

1. **缺少Dobby库**：使用自动修复脚本或手动下载
2. **NDK未配置**：设置ANDROID_NDK_HOME或NDK_HOME环境变量
3. **构建失败**：检查NDK版本兼容性
4. **缺少构建工具**：安装make、cmake等必要工具

## 自动修复工作流

根据项目规范，自动化修复工作流包含以下完整闭环步骤：

1. 检测构建失败并分析错误
2. 生成并应用修复方案
3. 将修复后的代码变更提交回源分支（使用[skip ci]避免循环触发）
4. 创建带`v`前缀的版本标签并推送到仓库以触发新的构建流程
5. 可选地进行本地构建验证

缺少任何一环都可能导致修复无法持久化或无法验证，破坏自动化修复的可靠性。