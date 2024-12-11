#include "Configuration.hpp"

#include <cstring>
#include <cstdlib>
#include "Logging.hpp"
#include "../build/replay/Constants.hpp"

namespace WebGPUNativeReplay {

Configuration::Configuration(const std::vector<std::string>& arguments) {
    for (size_t i = 0; i < arguments.size(); ++i) {
        const std::string& argument = arguments[i];

        if (argument == "--width") {
            if (i + 1 < arguments.size()) {
                // Read width.
                width = atoi(arguments[i + 1].c_str());
                ++i;
            }
        } else if (argument == "--height") {
            if (i + 1 < arguments.size()) {
                // Read height.
                height = atoi(arguments[i + 1].c_str());
                ++i;
            }
        } else if (argument == "--help") {
            showHelp = true;
        } else if (argument == "--version") {
            showVersion = true;
        } else if (argument == "--fullscreen") {
            fullscreen = true;
        } else if (argument == "--vulkan") {
            backendType = WGPUBackendType_Vulkan;
        } else if (argument == "--d3d11") {
            backendType = WGPUBackendType_D3D11;
        } else if (argument == "--d3d12") {
            backendType = WGPUBackendType_D3D12;
        } else if (argument == "--metal") {
            backendType = WGPUBackendType_Metal;
        } else if (argument == "--mailbox") {
            mailbox = true;
        } else {
            filename = argument;
        }
    }
}

void Configuration::ShowVersion() {
    Logging::Info("WebGPUNativeReplay version: " + std::to_string(VERSION_MAJOR) + "." + std::to_string(VERSION_MINOR) + "\n");
    Logging::Info("Capture file format version: " + std::to_string(FILE_VERSION) + "\n");
}

void Configuration::ShowHelp() {
    Logging::Info("WebGPUNativeReplay [options] filename.wgpur\n");
    Logging::Info("  --help          Show this help screen.\n");
    Logging::Info("  --version       Show version information.\n");
    Logging::Info("  --width  WIDTH  Specify the width of the window.\n");
    Logging::Info("  --height HEIGHT Specify the height of the window.\n");
    Logging::Info("  --fullscreen    Run capture in fullscreen mode.\n");
    Logging::Info("  --vulkan        Request Vulkan backend.\n");
    Logging::Info("  --d3d11         Request Direct3D 11 backend.\n");
    Logging::Info("  --d3d12         Request Direct3D 12 backend.\n");
    Logging::Info("  --metal         Request Metal backend.\n");
    Logging::Info("  --mailbox       Use mailbox present mode (turn off VSync).\n");
}

}
