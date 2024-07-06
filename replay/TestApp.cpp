#include "TestApp.hpp"

#include "../build/replay/Capture.hpp"
#include <iostream>
#include <chrono>
#if __ANDROID__
#include <android/log.h>
#endif

using namespace std;

namespace WebGPUNativeReplay {

TestApp::TestApp(const Window& window, uint32_t width, uint32_t height, WGPUBackendType backendType, bool profile) :
    adapter(window, backendType),
    device(adapter),
    swapChain(adapter, device, window, width, height, profile),
    profile(profile)
{

}

TestApp::~TestApp() {

}

void TestApp::RunCapture(string_view filename) {
    Capture capture(filename, adapter, device, swapChain);

    const chrono::high_resolution_clock::time_point start = chrono::high_resolution_clock::now();

    while (capture.RunNextCommand());

    if (profile) {
        const chrono::high_resolution_clock::time_point end = chrono::high_resolution_clock::now();
        const chrono::duration<double> duration = chrono::duration_cast<chrono::duration<double>>(end - start);
        ProfilingOutput("Ran capture in " + to_string(duration.count()) + " seconds.\n");
    }
}

void TestApp::ProfilingOutput(string text) {
#if __ANDROID__
    __android_log_print(ANDROID_LOG_INFO, "WebGPUNativeReplay", "%s", text.c_str());
#else
    cout << text;
#endif
}

}
