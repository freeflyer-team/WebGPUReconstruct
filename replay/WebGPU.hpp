#pragma once

#if WEBGPU_BACKEND_DAWN
#include <dawn/webgpu.h>

// TODO Remove once wgpu-native has updated to latest headers.
typedef WGPUBufferUsage WGPUBufferUsageFlags;
typedef WGPUTextureUsage WGPUTextureUsageFlags;
#endif

#if WEBGPU_BACKEND_WGPU
#include <wgpu.h>

inline void wgpuDeviceTick(WGPUDevice device) {
    wgpuDevicePoll(device, false, nullptr);
}

// TODO Remove once wgpu-native has updated to latest headers.
typedef WGPUSurfaceDescriptorFromAndroidNativeWindow WGPUSurfaceSourceAndroidNativeWindow;
typedef WGPUSurfaceDescriptorFromWindowsHWND WGPUSurfaceSourceWindowsHWND;
typedef WGPUSurfaceDescriptorFromXlibWindow WGPUSurfaceSourceXlibWindow;

const WGPUSType WGPUSType_SurfaceSourceAndroidNativeWindow = WGPUSType_SurfaceDescriptorFromAndroidNativeWindow;
const WGPUSType WGPUSType_SurfaceSourceWindowsHWND = WGPUSType_SurfaceDescriptorFromWindowsHWND;
const WGPUSType WGPUSType_SurfaceSourceXlibWindow = WGPUSType_SurfaceDescriptorFromXlibWindow;

typedef WGPUShaderModuleWGSLDescriptor WGPUShaderSourceWGSL;

const WGPUSType WGPUSType_ShaderSourceWGSL = WGPUSType_ShaderModuleWGSLDescriptor;
#endif
