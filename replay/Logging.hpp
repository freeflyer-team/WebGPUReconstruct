#pragma once

#include <string>

namespace WebGPUNativeReplay {
namespace Logging {

void Info(const std::string& text);
void Warn(const std::string& text);
void Error(const std::string& text);

}
}
