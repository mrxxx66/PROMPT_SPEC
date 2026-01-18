#include <fstream>
#include <string>
#include <android/log.h>

#define LOG_TAG "SFBypass_ZNext"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
#define LOGW(...) __android_log_print(ANDROID_LOG_WARN, LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

std::string getPackageNameForUid(uid_t uid) {
    std::string package_name = "";

    // Read package name from /proc/[pid]/cmdline
    char cmdline_path[256];
    snprintf(cmdline_path, sizeof(cmdline_path), "/proc/%d/cmdline", uid);

    std::ifstream cmdline_file(cmdline_path);
    if (cmdline_file.is_open()) {
        std::getline(cmdline_file, package_name, '\0');
        cmdline_file.close();
    }

    return package_name;
}

bool isPackageWhitelisted(uid_t uid) {
    // This function would typically check against a cached whitelist
    // Implementation would be in cache.cpp
    return false;
}