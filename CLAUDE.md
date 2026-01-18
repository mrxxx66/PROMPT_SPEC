# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains a ZygiskNext module for bypassing screenshot restrictions on Xiaomi HyperOS (Android 13/14) devices by hooking into the surfaceflinger process. The module injects into /system/bin/surfaceflinger to circumvent the private screenshot permission limitation that prevents whitelisted applications from capturing screenshots.

## Key Files and Structure

- `PROMPT_SPEC1.md` and `PROMPT_SPEC2.md` - Contain the complete specification for the ZygiskNext module
- `jni/` - Contains C++ source files for the module:
  - `main.cpp` - ZygiskNext entry point and process validation
  - `hook.cpp` - Dobby inline hook implementation for MiSurfaceFlingerStub::isCallingBySystemui
  - `cache.cpp` - Thread-safe cache and inotify monitoring for whitelist updates
  - `utils.cpp` - Utility functions for PID/UID to package name conversion
- `zygisk_next.xml` - ZygiskNext configuration
- `sepolicy.rule` - SELinux policy rules
- `.github/workflows/build.yml` - GitHub Actions CI/CD pipeline

## Development Commands

### Building
```bash
# Build the module for arm64-v8a architecture
ndk-build
# or
cmake .
```

### Testing
The module requires an Android device running Xiaomi HyperOS with Magisk/ZygiskNext installed. Testing involves:
1. Installing the module via Magisk
2. Adding packages to the whitelist file `/data/adb/modules/hyperos_sf_bypass/whitelist.txt`
3. Verifying that whitelisted apps can take screenshots

## Architecture Notes

1. **Performance Critical**: The hook function must be extremely fast as it's called on every frame draw
2. **Thread Safety**: Uses std::shared_mutex for cache operations to support concurrent reads
3. **Zero-IO Path**: All validation is done with cached data; no file I/O in the hook function
4. **Security**: Validate process name in `onModuleLoaded` to prevent injection into wrong processes
5. **Fallback Strategy**: Implements symbol resolution with hex pattern search fallback

## Key Implementation Details

- Hooks `android::MiSurfaceFlingerStub::isCallingBySystemui(int pid)` function
- Uses `android::IPCThreadState::self()->getCallingPid()` for accurate caller identification
- Implements async whitelist monitoring via inotify thread
- Caches validation results in `std::unordered_map<uid_t, bool>`
- Uses Dobby for robust inline hooking