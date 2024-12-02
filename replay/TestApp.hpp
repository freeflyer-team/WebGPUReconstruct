#pragma once

#include "Adapter.hpp"
#include "Device.hpp"
#include "SwapChain.hpp"
#include <string_view>

namespace WebGPUNativeReplay {

struct Window;

class TestApp {
  public:
    TestApp(const Window& window, uint32_t width, uint32_t height, WGPUBackendType backendType = WGPUBackendType_Undefined, bool profile = false);
    ~TestApp();

    void RunCapture(std::string_view filename);

  private:
    Adapter adapter;
    Device device;
    SwapChain swapChain;
    bool profile;

    TestApp(const TestApp&) = delete;
    TestApp& operator=(const TestApp&) = delete;
};

}
