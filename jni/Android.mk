LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

LOCAL_MODULE := lsfbypass
LOCAL_SRC_FILES := main.cpp hook.cpp cache.cpp utils.cpp
LOCAL_LDLIBS := -llog -landroid
# LOCAL_STATIC_LIBRARIES := dobby  # Commented out for now
LOCAL_CFLAGS := -std=c++17 -Wall -Werror
LOCAL_CPPFLAGS := -std=c++17

include $(BUILD_SHARED_LIBRARY)

# Build Dobby static library
# include $(CLEAR_VARS)
# LOCAL_MODULE := dobby
# LOCAL_SRC_FILES := external/libdobby.a
# LOCAL_EXPORT_C_INCLUDES := $(LOCAL_PATH)/external
# include $(PREBUILT_STATIC_LIBRARY)