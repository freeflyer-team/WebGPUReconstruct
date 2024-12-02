#include "Adapter.hpp"

#if WEBGPU_BACKEND_DAWN
#include <dawn/dawn_proc.h>
#include <dawn/native/DawnNative.h>
#endif
#include <atomic>
#include <thread>
#include <string_view>
#include "Logging.hpp"

#if __ANDROID__

#else
    #include <GLFW/glfw3.h>
    #if defined(_WIN32) || defined(WIN32)
        #define GLFW_EXPOSE_NATIVE_WIN32
    #elif __APPLE__
        #define GLFW_EXPOSE_NATIVE_COCOA
    #elif __linux__
        /// @todo Wayland?
        #define GLFW_EXPOSE_NATIVE_X11
    #endif
    #include <GLFW/glfw3native.h>
#endif

namespace WebGPUNativeReplay {

Adapter::Adapter(const Window& window, WGPUBackendType backendType) {
    InitializeBackend();
    CreateInstance();
    CreateSurface(window);
    RequestAdapter(backendType);
}

Adapter::~Adapter() {
    wgpuAdapterRelease(adapter);
#if !WEBGPU_BACKEND_DAWN
    // TODO Remove Dawn bug workaround.
    wgpuSurfaceRelease(surface);
#endif
    wgpuInstanceRelease(instance);
}

WGPUAdapter Adapter::GetAdapter() {
    return adapter;
}

WGPUSurface Adapter::GetSurface() {
    return surface;
}

void Adapter::InitializeBackend() {
#if WEBGPU_BACKEND_DAWN
    // Initialize Dawn
    DawnProcTable procs = dawn::native::GetProcs();
    dawnProcSetProcs(&procs);
    Logging::Info("Using Dawn backend.\n");
#else
    Logging::Info("Using wgpu backend.\n");
#endif
}

void Adapter::CreateInstance() {
    WGPUInstanceDescriptor instanceDescriptor = {};
    instanceDescriptor.nextInChain = nullptr;

    instance = wgpuCreateInstance(&instanceDescriptor);
}

void Adapter::CreateSurface(const Window& window) {
#if __ANDROID__
    WGPUSurfaceSourceAndroidNativeWindow platformSurfaceSource = {};
    platformSurfaceSource.chain.next = nullptr;
    platformSurfaceSource.chain.sType = WGPUSType_SurfaceSourceAndroidNativeWindow;
    platformSurfaceSource.window = window.window;
#elif defined(_WIN32) || defined(WIN32)
    WGPUSurfaceDescriptorFromWindowsHWND platformSurfaceSource = {};
    platformSurfaceSource.chain.next = nullptr;
    platformSurfaceSource.chain.sType = WGPUSType_SurfaceSourceWindowsHWND;
    platformSurfaceSource.hinstance = GetModuleHandle(NULL);
    platformSurfaceSource.hwnd = glfwGetWin32Window(window.window);
#elif __APPLE__
#error "WebGPU surface support has not been implemented on Mac."
    /// @todo Implement WGPUSurfaceSourceMetalLayer
#elif __linux__
    WGPUSurfaceDescriptorFromXlibWindow platformSurfaceSource = {};
    platformSurfaceSource.chain.next = nullptr;
    platformSurfaceSource.chain.sType = WGPUSType_SurfaceSourceXlibWindow;
    platformSurfaceSource.display = glfwGetX11Display();
    platformSurfaceSource.window = glfwGetX11Window(window.window);
#else
#error "Unsupported platform"
#endif

    WGPUSurfaceDescriptor surfaceDescriptor = {};
#if WEBGPU_BACKEND_WGPU
    // TODO Remove once wgpu switches to WGPUStringView.
    surfaceDescriptor.label = nullptr;
#endif
    surfaceDescriptor.nextInChain = reinterpret_cast<const WGPUChainedStruct*>(&platformSurfaceSource);

    surface = wgpuInstanceCreateSurface(instance, &surfaceDescriptor);
}

void Adapter::RequestAdapter(WGPUBackendType backendType) {
    WGPURequestAdapterOptions options = {};
    options.backendType = backendType;
    options.compatibleSurface = surface;
    options.forceFallbackAdapter = false;
    options.powerPreference = WGPUPowerPreference_HighPerformance;

    struct UserData {
        WGPUAdapter adapter = nullptr;
        std::atomic<bool> finished = false;
    };
    UserData userData;

#if WEBGPU_BACKEND_DAWN
    wgpuInstanceRequestAdapter(
        instance, &options, [](WGPURequestAdapterStatus status, WGPUAdapter adapter, WGPUStringView message, void* userdata) {
            UserData* userData = reinterpret_cast<UserData*>(userdata);
            userData->adapter = adapter;
            userData->finished = true;
        }, &userData);
#else
    wgpuInstanceRequestAdapter(
        instance, &options, [](WGPURequestAdapterStatus status, WGPUAdapter adapter, char const* message, void* userdata) {
            UserData* userData = reinterpret_cast<UserData*>(userdata);
            userData->adapter = adapter;
            userData->finished = true;
        }, & userData);
#endif

    // Wait for request to finish.
    while (!userData.finished) {
        std::this_thread::yield();
    };

    adapter = userData.adapter;

    // Get information about the adapter.
    WGPUAdapterInfo info = {};
    wgpuAdapterGetInfo(adapter, &info);

#if WEBGPU_BACKEND_DAWN
    const std::string_view deviceName(info.device.data, info.device.length);
#else
    const std::string_view deviceName = info.device;
#endif
    Logging::Info("Selected adapter " + std::string(deviceName) + "\n");

    Logging::Info("Backend type: ");
    switch (info.backendType) {
    case WGPUBackendType_Null:
        Logging::Info("Null.\n");
        break;
    case WGPUBackendType_WebGPU:
        Logging::Info("WebGPU.\n");
        break;
    case WGPUBackendType_D3D11:
        Logging::Info("D3D11.\n");
        break;
    case WGPUBackendType_D3D12:
        Logging::Info("D3D12.\n");
        break;
    case WGPUBackendType_Metal:
        Logging::Info("Metal.\n");
        break;
    case WGPUBackendType_Vulkan:
        Logging::Info("Vulkan.\n");
        break;
    case WGPUBackendType_OpenGL:
        Logging::Info("OpenGL.\n");
        break;
    case WGPUBackendType_OpenGLES:
        Logging::Info("OpenGL ES.\n");
        break;
    }
}

}
