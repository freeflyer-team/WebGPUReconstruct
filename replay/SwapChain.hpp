#pragma once

#include "WebGPU.hpp"

namespace WebGPUNativeReplay {

class Adapter;
class Device;
struct Window;

class SwapChain {
  public:
    SwapChain(Adapter& adapter, Device& device, const Window& window, uint32_t width, uint32_t height, bool profile);
    ~SwapChain();

    WGPUSurfaceTexture GetCurrentTexture();
    WGPUTextureFormat GetFormat() const;

  private:
    WGPUTextureFormat swapChainFormat = WGPUTextureFormat_Undefined;
    WGPUSurface surface;

    SwapChain() = delete;
    SwapChain(const SwapChain&) = delete;
    SwapChain& operator=(const SwapChain&) = delete;
};

}
