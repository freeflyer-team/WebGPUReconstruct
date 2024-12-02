#include "Logging.hpp"

#if __ANDROID__
#include <android/log.h>
#else
#include <iostream>
#endif

namespace WebGPUNativeReplay {
namespace Logging {

void Info(const std::string& text) {
#if __ANDROID__
    __android_log_print(ANDROID_LOG_INFO, "WebGPUNativeReplay", "%s", text.c_str());
#else
    std::cout << text;
#endif
}

void Warn(const std::string& text) {
#if __ANDROID__
    __android_log_print(ANDROID_LOG_WARN, "WebGPUNativeReplay", "%s", text.c_str());
#else
    std::cout << text;
#endif
}

void Error(const std::string& text) {
#if __ANDROID__
    __android_log_print(ANDROID_LOG_ERROR, "WebGPUNativeReplay", "%s", text.c_str());
#else
    std::cerr << text;
#endif
}

}
}
