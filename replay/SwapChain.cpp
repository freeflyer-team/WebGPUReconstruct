#include "SwapChain.hpp"
#include "Adapter.hpp"
#include "Device.hpp"
#include <cassert>
#include <iostream>

namespace WebGPUNativeReplay {

SwapChain::SwapChain(Adapter& adapter, Device& device, const Window& window, uint32_t width, uint32_t height, bool profile) : surface(adapter.GetSurface()) {
    // Find suitable surface format.
    WGPUSurfaceCapabilities surfaceCapabilities = { 0 };
    wgpuSurfaceGetCapabilities(surface, adapter.GetAdapter(), &surfaceCapabilities);

    for (size_t i = 0; i < surfaceCapabilities.formatCount; ++i) {
        if (surfaceCapabilities.formats[i] == WGPUTextureFormat_RGBA8Unorm || surfaceCapabilities.formats[i] == WGPUTextureFormat_BGRA8Unorm) {
            swapChainFormat = surfaceCapabilities.formats[i];
            break;
        }
    }

    if (swapChainFormat == WGPUTextureFormat_Undefined) {
        std::cerr << "Could not find suitable surface format.\n";
        exit(EXIT_FAILURE);
    }

    const WGPUTextureUsageFlags requiredUsage = WGPUTextureUsage_RenderAttachment;
    if ((surfaceCapabilities.usages & requiredUsage) != requiredUsage) {
        std::cerr << "Surface doesn't support the required texture usage.\n";
        exit(EXIT_FAILURE);
    }

    WGPUSurfaceConfiguration configuration = {};
    configuration.device = device.GetDevice();
    configuration.width = width;
    configuration.height = height;
    configuration.format = swapChainFormat;
    configuration.usage = WGPUTextureUsage_RenderAttachment;
    configuration.presentMode = (profile ? WGPUPresentMode_Mailbox : WGPUPresentMode_Fifo);
    configuration.alphaMode = surfaceCapabilities.alphaModes[0];

    wgpuSurfaceConfigure(surface, &configuration);
}

SwapChain::~SwapChain() {
    wgpuSurfaceUnconfigure(surface);
#if WEBGPU_BACKEND_DAWN
    // TODO Remove Dawn bug workaround.
    wgpuSurfaceRelease(surface);
#endif
}

WGPUSurfaceTexture SwapChain::GetCurrentTexture() {
    WGPUSurfaceTexture surfaceTexture;
    wgpuSurfaceGetCurrentTexture(surface, &surfaceTexture);
    assert(surfaceTexture.status == WGPUSurfaceGetCurrentTextureStatus_Success);

    return surfaceTexture;
}

WGPUTextureFormat SwapChain::GetFormat() const {
    return swapChainFormat;
}

}
