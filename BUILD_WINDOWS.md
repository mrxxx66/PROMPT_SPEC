# Building on Windows

## Prerequisites

1. Install Android NDK r25c:
   - Download from: https://dl.google.com/android/repository/android-ndk-r25c-windows.zip
   - Extract to a directory (e.g., `C:\android-ndk-r25c`)

2. Add NDK to PATH:
   ```cmd
   set PATH=C:\android-ndk-r25c;%PATH%
   ```

## Build Steps

1. Open Command Prompt in the project directory

2. Navigate to the jni directory:
   ```cmd
   cd jni
   ```

3. Run the build command:
   ```cmd
   ndk-build APP_ABI="arm64-v8a" NDK_PROJECT_PATH=. NDK_APPLICATION_MK=./Android.mk
   ```

## Notes

- The Dobby library dependency is currently commented out in `Android.mk`
- To build with Dobby, you need to:
  1. Download Dobby library from GitHub
  2. Place `libdobby.a` in `jni/external/` directory
  3. Uncomment the Dobby sections in `Android.mk`, `main.cpp`, and `hook.cpp`

## Expected Output

If successful, you should see:
- Compiled library at `jni/libs/arm64-v8a/liblsfbypass.so`
- No error messages about missing Android.mk or APP_PLATFORM