#pragma once

#if WEBGPU_BACKEND_DAWN
#include <dawn/webgpu.h>
#endif

#if WEBGPU_BACKEND_WGPU
#include <wgpu.h>

inline void wgpuDeviceTick(WGPUDevice device) {
    wgpuDevicePoll(device, false, nullptr);
}

typedef WGPULimits WGPUSupportedLimits;
typedef WGPULimits WGPURequiredLimits;

typedef WGPURequestAdapterCallbackInfo WGPURequestAdapterCallbackInfo2;
typedef WGPURequestDeviceCallbackInfo WGPURequestDeviceCallbackInfo2;
typedef WGPUBufferMapCallbackInfo WGPUBufferMapCallbackInfo2;
typedef WGPUQueueWorkDoneCallbackInfo WGPUQueueWorkDoneCallbackInfo2;

#define wgpuInstanceRequestAdapter2 wgpuInstanceRequestAdapter
#define wgpuAdapterRequestDevice2 wgpuAdapterRequestDevice
#define wgpuBufferMapAsync2 wgpuBufferMapAsync
#define wgpuQueueOnSubmittedWorkDone2 wgpuQueueOnSubmittedWorkDone

typedef WGPUTexelCopyTextureInfo WGPUImageCopyTexture;
typedef WGPUTexelCopyBufferInfo WGPUImageCopyBuffer;
typedef WGPUTexelCopyBufferLayout WGPUTextureDataLayout;
#endif
