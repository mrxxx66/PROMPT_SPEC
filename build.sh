#!/bin/bash
# Build script for HyperOS SF Bypass module

set -e

echo "Building HyperOS SF Bypass module..."

# Check if Dobby library exists
if [ ! -f "jni/external/libdobby.a" ]; then
    echo "Warning: Dobby library not found at jni/external/libdobby.a"
    echo "The build will fail without it."
    echo ""
    echo "To download Dobby:"
    echo "1. Visit https://github.com/jmpews/Dobby"
    echo "2. Download or build libdobby.a for Android arm64"
    echo "3. Place it in jni/external/libdobby.a"
    echo ""
    read -p "Do you want to continue without Dobby? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build the module
cd jni
ndk-build APP_ABI="arm64-v8a"
cd ..

echo "Build complete!"
echo "Output: jni/libs/arm64-v8a/liblsfbypass.so"