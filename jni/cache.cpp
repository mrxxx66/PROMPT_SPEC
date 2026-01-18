#include <unordered_map>
#include <shared_mutex>
#include <fstream>
#include <thread>
#include <sys/inotify.h>
#include <string>
#include <android/log.h>

#define LOG_TAG "SFBypass_ZNext"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
#define LOGW(...) __android_log_print(ANDROID_LOG_WARN, LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

// Global variables
std::unordered_map<uid_t, bool> identity_cache;
std::shared_mutex cache_mutex;
std::unordered_set<std::string> whitelist;
int inotify_fd = -1;
int watch_fd = -1;
std::thread* inotify_thread = nullptr;

bool isPackageWhitelisted(uid_t uid) {
    // Check cache first
    {
        std::shared_lock<std::shared_mutex> lock(cache_mutex);
        auto it = identity_cache.find(uid);
        if (it != identity_cache.end()) {
            return it->second;
        }
    }

    // If not in cache, resolve package name and check whitelist
    std::string package_name = "";

    // Read package name from /proc/[pid]/cmdline
    char cmdline_path[256];
    snprintf(cmdline_path, sizeof(cmdline_path), "/proc/%d/cmdline", uid);

    std::ifstream cmdline_file(cmdline_path);
    if (cmdline_file.is_open()) {
        std::getline(cmdline_file, package_name, '\0');
        cmdline_file.close();
    }

    if (package_name.empty()) {
        // If we can't read cmdline, try fallback method
        LOGW("Could not read package name for UID %d", uid);
        return false;
    }

    // Check if package is in whitelist
    bool is_whitelisted = whitelist.find(package_name) != whitelist.end();

    // Update cache
    {
        std::unique_lock<std::shared_mutex> lock(cache_mutex);
        identity_cache[uid] = is_whitelisted;
    }

    return is_whitelisted;
}

void initWhitelist() {
    std::string whitelist_path = "/data/adb/modules/hyperos_sf_bypass/whitelist.txt";
    std::ifstream file(whitelist_path);
    std::string line;

    whitelist.clear();

    if (file.is_open()) {
        while (std::getline(file, line)) {
            // Remove whitespace
            line.erase(0, line.find_first_not_of(" \t\r\n"));
            line.erase(line.find_last_not_of(" \t\r\n") + 1);

            if (!line.empty()) {
                whitelist.insert(line);
            }
        }
        file.close();
        LOGI("Loaded whitelist with %zu entries", whitelist.size());
    } else {
        LOGI("Whitelist file not found, using empty whitelist");
    }
}

void monitorWhitelistFile() {
    std::string whitelist_path = "/data/adb/modules/hyperos_sf_bypass/whitelist.txt";

    inotify_fd = inotify_init();
    if (inotify_fd < 0) {
        LOGE("Failed to initialize inotify");
        return;
    }

    watch_fd = inotify_add_watch(inotify_fd, whitelist_path.c_str(), IN_MODIFY | IN_CLOSE_WRITE);
    if (watch_fd < 0) {
        LOGE("Failed to add watch for whitelist file");
        close(inotify_fd);
        inotify_fd = -1;
        return;
    }

    inotify_thread = new std::thread([]() {
        char buffer[4096];
        while (true) {
            int length = read(inotify_fd, buffer, sizeof(buffer));
            if (length < 0) {
                LOGE("Error reading inotify events");
                break;
            }

            int i = 0;
            while (i < length) {
                struct inotify_event* event = (struct inotify_event*)&buffer[i];
                if (event->len) {
                    if (event->mask & IN_MODIFY || event->mask & IN_CLOSE_WRITE) {
                        LOGI("Whitelist file changed, reloading...");
                        initWhitelist();
                    }
                }
                i += sizeof(struct inotify_event) + event->len;
            }
        }
    });
    LOGI("Started inotify thread for whitelist monitoring");
}