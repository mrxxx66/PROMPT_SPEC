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

### 使用Shell自动修复脚本

运行以下命令启动自动修复：

```bash
chmod +x scripts/auto_fix_build.sh
./scripts/auto_fix_build.sh
```

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