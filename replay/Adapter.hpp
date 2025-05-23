#pragma once

#include "Window.hpp"
#include "WebGPU.hpp"

namespace WebGPUNativeReplay {

class Adapter {
  public:
    Adapter(const Window& window, WGPUBackendType backendType);
    ~Adapter();

    WGPUInstance GetInstance();
    WGPUAdapter GetAdapter();
    WGPUSurface GetSurface();

#if WEBGPU_BACKEND_DAWN
    uint32_t GetSubgroupMinSize() const;
    uint32_t GetSubgroupMaxSize() const;
#endif

  private:
    WGPUInstance instance;
    WGPUSurface surface;
    WGPUAdapter adapter;

#if WEBGPU_BACKEND_DAWN
    uint32_t subgroupMinSize;
    uint32_t subgroupMaxSize;
#endif

    void InitializeBackend();
    void CreateInstance();
    void CreateSurface(const Window& window);
    void RequestAdapter(WGPUBackendType backendType);

    Adapter() = delete;
    Adapter(const Adapter&) = delete;
    Adapter& operator=(const Adapter&) = delete;
};

}
