#pragma once

#include "../../replay/Uint8Reader.hpp"
#include "../../replay/WebGPU.hpp"
#include <string>
#include <string_view>
#include <unordered_map>
#include <map>

namespace WebGPUNativeReplay {

class Adapter;
class Device;
class SwapChain;

class Capture {
  public:
    Capture(std::string_view filename, Adapter& adapter, Device& device, SwapChain& swapChain);
    ~Capture();

    bool RunNextCommand();

  private:
    Adapter& adapter;
    Device& device;
    SwapChain& swapChain;

    Uint8Reader reader;
    
// Generated maps that map ID -> WebGPU object will be inserted here.
$MAPS

    struct CanvasTexture {
        WGPUTexture texture = nullptr;
        uint32_t usage = 0;
        WGPUTextureFormat format = WGPUTextureFormat_Undefined;
        uint32_t width = 0;
        uint32_t height = 0;
        uint64_t viewFormatCount = 0;
        WGPUTextureFormat* viewFormats = nullptr;
    };
    std::map<uint32_t, CanvasTexture> canvasTextures;

    bool hasBegun = false;
    WGPUShaderModule copyVertexShader;
    WGPUShaderModule copyFragmentShader;
    WGPURenderPipeline copyRenderPipeline;
    WGPUSampler sampler;
    
    void DebugOutput(std::string text);
    void ErrorOutput(std::string text);
    
    template <class T>
    T GetIdType(std::unordered_map<uint32_t, T>& m, uint32_t id) {
        if (id == 0) {
            return nullptr;
        }
        return m[id];
    }

    Capture() = delete;
    Capture(const Capture&) = delete;
    Capture& operator=(const Capture&) = delete;
};

}
