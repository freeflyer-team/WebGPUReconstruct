#pragma once

#include "WebGPU.hpp"

namespace WebGPUNativeReplay {

class Adapter;

class Device {
  public:
    explicit Device(Adapter& adapter);
    ~Device();

    WGPUDevice GetDevice();
    WGPUQueue GetQueue();

  private:
    WGPUDevice device;
    WGPUQueue queue;

    Device() = delete;
    Device(const Device&) = delete;
    Device& operator=(const Device&) = delete;
};

}
