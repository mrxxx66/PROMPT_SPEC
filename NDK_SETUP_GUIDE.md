# NDK配置指南

本指南介绍如何安装和配置Android NDK以构建此项目。

## 安装Android NDK

### 方法1：使用Android Studio

1. 下载并安装Android Studio
2. 打开Android Studio
3. 转到 Settings > Appearance & Behavior > System Settings > Android SDK
4. 点击SDK Tools选项卡
5. 勾选"NDK (Side by side)"和"CMake"
6. 点击Apply并下载

### 方法2：独立下载

1. 访问 https://developer.android.com/ndk/downloads
2. 下载适合您系统的NDK版本
3. 解压到合适的目录，例如：`C:\android-ndk-r25c`

## 配置环境变量

### Windows系统：

1. 打开系统属性 > 高级 > 环境变量
2. 在"系统变量"中新建：
   - 变量名：`ANDROID_NDK_HOME` 
   - 变量值：NDK的安装路径，例如 `C:\android-ndk-r25c`
3. 或者，在"用户变量"中添加同样有效

### Linux/macOS系统：

在 `~/.bashrc` 或 `~/.zshrc` 中添加：
```bash
export ANDROID_NDK_HOME=/path/to/your/ndk
# 或者
export NDK_HOME=/path/to/your/ndk
```

## 验证配置

配置完成后，打开新的终端窗口，运行：
```bash
echo $ANDROID_NDK_HOME
# 应该输出NDK的安装路径
```

或者在Windows上运行：
```cmd
echo %ANDROID_NDK_HOME%
```

## 编译Dobby库

由于我们已经下载了Dobby库，需要对其进行编译：

1. 确保NDK已正确配置
2. 进入Dobby目录：
   ```bash
   cd jni/external/Dobby
   ```
3. 使用CMake编译：
   ```bash
   mkdir build && cd build
   cmake .. -DCMAKE_TOOLCHAIN_FILE=$ANDROID_NDK_HOME/build/cmake/android.toolchain.cmake -DANDROID_ABI="arm64-v8a" -DANDROID_PLATFORM=android-21
   make
   ```
4. 将编译好的库移动到适当位置：
   ```bash
   cp libdobby.a ../../../../libs/arm64-v8a/
   ```

## 运行构建

完成以上配置后，您可以运行构建脚本：
```bash
./build.sh
```

## 故障排除

如果仍然遇到问题，请检查：

1. NDK版本是否兼容（推荐r23b或更高版本）
2. 是否正确设置了环境变量
3. 是否有足够的磁盘空间进行编译
4. 是否安装了必要的构建工具（如make、cmake等）