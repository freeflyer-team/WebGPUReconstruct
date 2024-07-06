#pragma once

#if __ANDROID__
#include <game-activity/native_app_glue/android_native_app_glue.h>
#else
#include <GLFW/glfw3.h>
#endif

namespace WebGPUNativeReplay {
    
struct Window {
#if __ANDROID__
    ANativeWindow* window;
#else
    GLFWwindow* window;
#endif
};
    
}
