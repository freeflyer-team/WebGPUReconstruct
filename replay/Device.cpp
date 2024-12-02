#include "Device.hpp"
#include "Adapter.hpp"
#include "Logging.hpp"

#include <atomic>
#include <string_view>
#include <thread>
#include <vector>

namespace WebGPUNativeReplay {

Device::Device(Adapter& adapter) {
    // Query features.
    std::vector<WGPUFeatureName> features;

    std::vector<WGPUFeatureName> desiredFeatures = {
        WGPUFeatureName_DepthClipControl,
        WGPUFeatureName_Depth32FloatStencil8,
        WGPUFeatureName_TimestampQuery,
        WGPUFeatureName_TextureCompressionBC,
        WGPUFeatureName_TextureCompressionETC2,
        WGPUFeatureName_TextureCompressionASTC,
        WGPUFeatureName_IndirectFirstInstance,
        WGPUFeatureName_ShaderF16,
        WGPUFeatureName_RG11B10UfloatRenderable,
        WGPUFeatureName_BGRA8UnormStorage,
        WGPUFeatureName_Float32Filterable
    };
    for (WGPUFeatureName feature : desiredFeatures) {
        if (wgpuAdapterHasFeature(adapter.GetAdapter(), feature)) {
            features.push_back(feature);
        }
    }

    // Query limits.
    WGPUSupportedLimits supportedLimits = {};
    wgpuAdapterGetLimits(adapter.GetAdapter(), &supportedLimits);

    WGPURequiredLimits requiredLimits = {};
    requiredLimits.limits = supportedLimits.limits;

    WGPUDeviceDescriptor deviceDescriptor = {};
    deviceDescriptor.requiredFeatureCount = features.size();
    deviceDescriptor.requiredFeatures = features.data();
    deviceDescriptor.requiredLimits = &requiredLimits;

#if WEBGPU_BACKEND_DAWN
    deviceDescriptor.deviceLostCallbackInfo.mode = WGPUCallbackMode_WaitAnyOnly;
    deviceDescriptor.deviceLostCallbackInfo.callback = [](const WGPUDevice* device, WGPUDeviceLostReason reason, WGPUStringView message, void* userdata) {
        Logging::Error("Device lost " + std::to_string(reason) + ": " + std::string(std::string_view(message.data, message.length)) + "\n");
    };

    deviceDescriptor.uncapturedErrorCallbackInfo.callback = [](WGPUErrorType type, WGPUStringView message, void* userData) {
        Logging::Error("Uncaptured device error " + std::to_string(type) + ": " + std::string(std::string_view(message.data, message.length)) + "\n");
    };
#else
    deviceDescriptor.deviceLostCallback = [](WGPUDeviceLostReason reason, char const* message, void* userdata) {
        Logging::Error("Device lost " + std::to_string(reason) + ": " + std::string(message) + "\n");
    };

    deviceDescriptor.uncapturedErrorCallbackInfo.callback = [](WGPUErrorType type, char const* message, void* userData) {
        Logging::Error("Uncaptured device error " + std::to_string(type) + ": " + std::string(message) + "\n");
    };
#endif

#if WEBGPU_BACKEND_DAWN
    // Make sure debug labels are forwarded.
    std::vector<const char*> toggles;
    toggles.push_back("use_user_defined_labels_in_backend");
    toggles.push_back("use_dxc");

    WGPUDawnTogglesDescriptor dawnToggles = {};
    dawnToggles.chain.sType = WGPUSType_DawnTogglesDescriptor;
    dawnToggles.enabledToggles = toggles.data();
    dawnToggles.enabledToggleCount = toggles.size();

    deviceDescriptor.nextInChain = reinterpret_cast<const WGPUChainedStruct*>(&dawnToggles);
#endif

    struct UserData {
        WGPUDevice device;
        std::atomic<bool> finished = false;
    };
    UserData userData;

#if WEBGPU_BACKEND_DAWN
    wgpuAdapterRequestDevice(
        adapter.GetAdapter(), &deviceDescriptor, [](WGPURequestDeviceStatus status, WGPUDevice device, WGPUStringView message, void* userdata) {
            UserData* userData = reinterpret_cast<UserData*>(userdata);
            userData->device = device;
            userData->finished = true;
        }, &userData);
#else
    wgpuAdapterRequestDevice(
        adapter.GetAdapter(), &deviceDescriptor, [](WGPURequestDeviceStatus status, WGPUDevice device, char const* message, void* userdata) {
            UserData* userData = reinterpret_cast<UserData*>(userdata);
            userData->device = device;
            userData->finished = true;
        }, & userData);
#endif

    // Wait for request to finish.
    while (!userData.finished) {
        std::this_thread::yield();
    }

    device = userData.device;

    // Get queue.
    queue = wgpuDeviceGetQueue(device);
}

Device::~Device() {
    wgpuDeviceRelease(device);
}

WGPUDevice Device::GetDevice() {
    return device;
}

WGPUQueue Device::GetQueue() {
    return queue;
}

}
