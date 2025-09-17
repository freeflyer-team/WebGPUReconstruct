# Start at 100 to leave some room for hardcoded commands.
commandId = 100
captureCommandsString = ""
wrapCommandsString = ""
resetCommandsString = ""
runCommandsString = ""

from code_generation.struct_types import *

# An advanced command that requires custom code. Eg. when there are differences between web and native (eg. swapchain stuff).
def add_custom_command(classType, methodName, arguments, captureCode, replayCode):
    global commandId
    global captureCommandsString
    global wrapCommandsString
    global resetCommandsString
    global runCommandsString
    
    commandId += 1
    
    captureCommandsString += "function __WebGPUReconstruct_" + classType.webName + "_" + methodName + "(wgpur,result"
    for arg in arguments:
        captureCommandsString += ", " + arg
    captureCommandsString += ") {\n" + captureCode.replace("$COMMAND_ID", str(commandId)) + "}\n\n"
    
    wrapCommandsString += '        ' + classType.webName + ".prototype." + methodName + " = this.wrapMethodPost(" + classType.webName + ".prototype." + methodName + ", __WebGPUReconstruct_" + classType.webName + "_" + methodName + ', "' + classType.webName + "_" + methodName + '");\n'
    resetCommandsString += '        ' + classType.webName + ".prototype." + methodName + " = this." + classType.webName + "_" + methodName + '_original;\n'
    
    runCommandsString += "case " + str(commandId) + ":\n{\n" + replayCode + "break;\n}\n"

# A simple command that doesn't require any custom code. Captures a single command with arguments and replays it.
def add_simple_command(classType, methodName, nativeCommand, returnType, arguments, replayEpilogue = ""):
    # Logging
    capture = '__WebGPUReconstruct_DebugOutput("' + methodName + '");\n'
    replay = 'DebugOutput("' + methodName + '\\n");\n'
    
    # Write command id.
    capture += 'wgpur.file.writeUint32($COMMAND_ID);\n'
    
    # Class information
    if isinstance(classType, IdType):
        capture += 'wgpur.file.writeUint32(this.__id);\n'
        replay += 'const uint32_t subjectId = reader.ReadUint32();\n'
        replay += classType.nativeName + ' subject = map' + classType.webName + '[subjectId];\n'
    else:
        assert(isinstance(classType, NonCapturedType))
        replay += classType.nativeName + ' subject = ' + classType.nativeReplay + ';\n'
    
    # Result information.
    if isinstance(returnType, IdType):
        capture += '__WebGPUReconstruct_AddId(result);\n'
        capture += 'wgpur.file.writeUint32(result.__id);\n'
        
        replay += 'const uint32_t resultId = reader.ReadUint32();\n'
    else:
        assert(isinstance(returnType, NonCapturedType))
    
    # Arguments
    arguments2 = []
    for i in range(len(arguments)):
        argument = arguments[i]
        assert(not isinstance(argument, NonCapturedType))
        
        argumentName = "arg" + str(i)
        capture += argument.save(argumentName)
        replay += argument.declare_argument(argumentName)
        replay += argument.load(argumentName)
        
        if isinstance(argument, ArrayType):
            argumentName = argument.get_plural_name(argumentName)
        
        arguments2.append(argumentName)
    
    # Run command
    if isinstance(returnType, IdType):
        replay += 'map' + returnType.webName + '[resultId] = '
    replay += nativeCommand + '(subject'
    
    for i in range(len(arguments)):
        argument = arguments[i]
        replay += ', ' + argument.as_argument('arg' + str(i))
    
    replay += ');\n'
    
    # Clean up dynamic allocations.
    for i in range(len(arguments)):
        argument = arguments[i]
        replay += argument.cleanup('arg' + str(i))
    
    replay += replayEpilogue
    
    add_custom_command(classType, methodName, arguments2, capture, replay)

# Command that hasn't been implemented yet.
def add_unsupported_command(classType, methodName, argumentCount):
    # Logging
    capture = 'console.error("Unimplemented command: ' + methodName + '");\n'
    replay = 'ErrorOutput("Unimplemented command: ' + methodName + '\\n");\n'
    
    # Write command id.
    capture += 'wgpur.file.writeUint32($COMMAND_ID);\n'
    
    arguments = []
    for i in range(argumentCount):
        arguments.append('arg' + str(i))
    
    add_custom_command(classType, methodName, arguments, capture, replay)

# Custom command that is common across GPURenderPassEncoder, GPURenderBundleEncoder and GPUComputePassEncoder.
def add_set_bind_group_command(classType, methodName):
    add_custom_command(classType, "setBindGroup", ["index", "bindGroup", "offsets0", "offsets1", "offsets2"], """
__WebGPUReconstruct_DebugOutput("setBindGroup");
wgpur.file.writeUint32($COMMAND_ID);
wgpur.file.writeUint32(this.__id);
wgpur.file.writeUint32(index);
wgpur.file.writeUint32(bindGroup.__id);

if (offsets0 == undefined) {
    offsets0 = [];
}

// There are two overloads of this function, one taking a Uint32Array containing offsets, and one with a regular array.
if (offsets0 instanceof Uint32Array && offsets1 != undefined && offsets2 != undefined) {
    wgpur.file.writeUint64(offsets2);
    for (let i = 0; i < offsets2; i += 1) {
        wgpur.file.writeUint32(offsets0[offsets1 + i]);
    }
} else {
    wgpur.file.writeUint64(offsets0.length);
    for (let i = 0; i < offsets0.length; i += 1) {
    wgpur.file.writeUint32(offsets0[i]);
    }
}
""", """
DebugOutput("setBindGroup\\n");
""" + classType.nativeName + """ encoder = GetIdType(map""" + classType.webName + """, reader.ReadUint32());
const uint32_t index = reader.ReadUint32();
WGPUBindGroup bindGroup = GetIdType(mapGPUBindGroup, reader.ReadUint32());
const uint64_t offsetCount = reader.ReadUint64();
uint32_t* offsets = nullptr;
if (offsetCount > 0) {
    offsets = new uint32_t[offsetCount];
    for (uint64_t i = 0; i < offsetCount; ++i) {
        offsets[i] = reader.ReadUint32();
    }
}
""" + methodName + """(encoder, index, bindGroup, offsetCount, offsets);
if (offsets != nullptr) {
    delete[] offsets;
}
""")
    
# Add an override for an already existing command.
def add_override_command(classType, methodName, argumentCount, overrides):
    global captureCommandsString
    global wrapCommandsString
    
    captureCommandsString += "function __WebGPUReconstruct_" + classType.webName + "_" + methodName + "_override(result"
    for i in range(argumentCount):
        captureCommandsString += ', arg' + str(i)

    captureCommandsString += ") {\n"

    for override in overrides:
        captureCommandsString += "if (" + override["condition"] + ") {\n"
        captureCommandsString += "__WebGPUReconstruct_" + classType.webName + "_" + methodName + ".call(this, result"
        arguments = override["arguments"]
        assert(len(arguments) == argumentCount)
        for i in range(argumentCount):
            captureCommandsString += ', ' + arguments[i]
        captureCommandsString += ");\n"

    captureCommandsString += "} else {\n"
    captureCommandsString += "__WebGPUReconstruct_" + classType.webName + "_" + methodName + ".call(this, result"
    for i in range(argumentCount):
        captureCommandsString += ', arg' + str(i)
    captureCommandsString += ");\n"
    captureCommandsString += "}\n"

    captureCommandsString += "}\n\n"

    wrapCommandsString += '        ' + classType.webName + ".prototype." + methodName + " = this." + classType.webName + "_" + methodName + '_original;\n'
    wrapCommandsString += '        ' + classType.webName + ".prototype." + methodName + " = this.wrapMethodPost(" + classType.webName + ".prototype." + methodName + ", __WebGPUReconstruct_" + classType.webName + "_" + methodName + '_override, "' + classType.webName + "_" + methodName + '");\n'

### COMMANDS
add_simple_command(GPUDevice, "createBuffer", "wgpuDeviceCreateBuffer", GPUBuffer, [GPUBufferDescriptor])
add_simple_command(GPUDevice, "createTexture", "wgpuDeviceCreateTexture", GPUTexture, [GPUTextureDescriptor])
add_simple_command(GPUDevice, "createSampler", "wgpuDeviceCreateSampler", GPUSampler, [GPUSamplerDescriptor])
add_simple_command(GPUDevice, "createBindGroupLayout", "wgpuDeviceCreateBindGroupLayout", GPUBindGroupLayout, [GPUBindGroupLayoutDescriptor])
add_simple_command(GPUDevice, "createPipelineLayout", "wgpuDeviceCreatePipelineLayout", GPUPipelineLayout, [GPUPipelineLayoutDescriptor])
add_simple_command(GPUDevice, "createBindGroup", "wgpuDeviceCreateBindGroup", GPUBindGroup, [GPUBindGroupDescriptor])
add_simple_command(GPUDevice, "createComputePipeline", "wgpuDeviceCreateComputePipeline", GPUComputePipeline, [GPUComputePipelineDescriptor])
add_simple_command(GPUDevice, "createRenderPipeline", "wgpuDeviceCreateRenderPipeline", GPURenderPipeline, [GPURenderPipelineDescriptor])
add_simple_command(GPUDevice, "createCommandEncoder", "wgpuDeviceCreateCommandEncoder", GPUCommandEncoder, [GPUCommandEncoderDescriptor])
add_simple_command(GPUDevice, "createRenderBundleEncoder", "wgpuDeviceCreateRenderBundleEncoder", GPURenderBundleEncoder, [GPURenderBundleEncoderDescriptor])
add_simple_command(GPUDevice, "createQuerySet", "wgpuDeviceCreateQuerySet", GPUQuerySet, [GPUQuerySetDescriptor])

add_simple_command(GPUTexture, "createView", "wgpuTextureCreateView", GPUTextureView, [GPUTextureViewDescriptor])

add_simple_command(GPUComputePipeline, "getBindGroupLayout", "wgpuComputePipelineGetBindGroupLayout", GPUBindGroupLayout, [Uint32])

add_simple_command(GPURenderPipeline, "getBindGroupLayout", "wgpuRenderPipelineGetBindGroupLayout", GPUBindGroupLayout, [Uint32])

add_simple_command(GPUCommandEncoder, "beginRenderPass", "wgpuCommandEncoderBeginRenderPass", GPURenderPassEncoder, [GPURenderPassDescriptor])
add_simple_command(GPUCommandEncoder, "beginComputePass", "wgpuCommandEncoderBeginComputePass", GPUComputePassEncoder, [GPUComputePassDescriptor])
add_simple_command(GPUCommandEncoder, "copyBufferToBuffer", "wgpuCommandEncoderCopyBufferToBuffer", undefined, [GPUBuffer, Uint64, GPUBuffer, Uint64, Optional(Uint64, "arg0.size - arg1")])
add_override_command(GPUCommandEncoder, "copyBufferToBuffer", 5, [{"condition": "arg3 == undefined", "arguments": ["arg0", "0", "arg1", "0", "arg2"]}])
add_simple_command(GPUCommandEncoder, "copyBufferToTexture", "wgpuCommandEncoderCopyBufferToTexture", undefined, [GPUTexelCopyBufferInfo, GPUTexelCopyTextureInfo, GPUExtent3D])
add_simple_command(GPUCommandEncoder, "copyTextureToBuffer", "wgpuCommandEncoderCopyTextureToBuffer", undefined, [GPUTexelCopyTextureInfo, GPUTexelCopyBufferInfo, GPUExtent3D])
add_simple_command(GPUCommandEncoder, "copyTextureToTexture", "wgpuCommandEncoderCopyTextureToTexture", undefined, [GPUTexelCopyTextureInfo, GPUTexelCopyTextureInfo, GPUExtent3D])
add_simple_command(GPUCommandEncoder, "clearBuffer", "wgpuCommandEncoderClearBuffer", undefined, [GPUBuffer, Optional(Uint64, 0), Optional(Uint64, "arg0.size - arg1")])
add_simple_command(GPUCommandEncoder, "resolveQuerySet", "wgpuCommandEncoderResolveQuerySet", undefined, [GPUQuerySet, Uint32, Uint32, GPUBuffer, Uint64])
add_simple_command(GPUCommandEncoder, "finish", "wgpuCommandEncoderFinish", GPUCommandBuffer, [GPUCommandBufferDescriptor], "wgpuCommandEncoderRelease(subject);\n")
add_simple_command(GPUCommandEncoder, "pushDebugGroup", "wgpuCommandEncoderPushDebugGroup", undefined, [String])
add_simple_command(GPUCommandEncoder, "popDebugGroup", "wgpuCommandEncoderPopDebugGroup", undefined, [])
add_simple_command(GPUCommandEncoder, "insertDebugMarker", "wgpuCommandEncoderInsertDebugMarker", undefined, [String])

add_simple_command(GPUComputePassEncoder, "setPipeline", "wgpuComputePassEncoderSetPipeline", undefined, [GPUComputePipeline])
add_simple_command(GPUComputePassEncoder, "dispatchWorkgroups", "wgpuComputePassEncoderDispatchWorkgroups", undefined, [Uint32, Optional(Uint32, 1), Optional(Uint32, 1)])
add_simple_command(GPUComputePassEncoder, "dispatchWorkgroupsIndirect", "wgpuComputePassEncoderDispatchWorkgroupsIndirect", undefined, [GPUBuffer, Uint64])
add_simple_command(GPUComputePassEncoder, "end", "wgpuComputePassEncoderEnd", undefined, [], "wgpuComputePassEncoderRelease(subject);\n")
add_simple_command(GPUComputePassEncoder, "pushDebugGroup", "wgpuComputePassEncoderPushDebugGroup", undefined, [String])
add_simple_command(GPUComputePassEncoder, "popDebugGroup", "wgpuComputePassEncoderPopDebugGroup", undefined, [])
add_simple_command(GPUComputePassEncoder, "insertDebugMarker", "wgpuComputePassEncoderInsertDebugMarker", undefined, [String])
add_set_bind_group_command(GPUComputePassEncoder, "wgpuComputePassEncoderSetBindGroup")

add_simple_command(GPURenderPassEncoder, "setViewport", "wgpuRenderPassEncoderSetViewport", undefined, [Float32, Float32, Float32, Float32, Float32, Float32])
add_simple_command(GPURenderPassEncoder, "setScissorRect", "wgpuRenderPassEncoderSetScissorRect", undefined, [Uint32, Uint32, Uint32, Uint32])
add_simple_command(GPURenderPassEncoder, "setBlendConstant", "wgpuRenderPassEncoderSetBlendConstant", undefined, [GPUColor])
add_simple_command(GPURenderPassEncoder, "setStencilReference", "wgpuRenderPassEncoderSetStencilReference", undefined, [Uint32])
add_simple_command(GPURenderPassEncoder, "beginOcclusionQuery", "wgpuRenderPassEncoderBeginOcclusionQuery", undefined, [Uint32])
add_simple_command(GPURenderPassEncoder, "endOcclusionQuery", "wgpuRenderPassEncoderEndOcclusionQuery", undefined, [])
add_simple_command(GPURenderPassEncoder, "executeBundles", "wgpuRenderPassEncoderExecuteBundles", undefined, [ArrayType(GPURenderBundle)])
add_simple_command(GPURenderPassEncoder, "end", "wgpuRenderPassEncoderEnd", undefined, [], "wgpuRenderPassEncoderRelease(subject);\n")
add_simple_command(GPURenderPassEncoder, "pushDebugGroup", "wgpuRenderPassEncoderPushDebugGroup", undefined, [String])
add_simple_command(GPURenderPassEncoder, "popDebugGroup", "wgpuRenderPassEncoderPopDebugGroup", undefined, [])
add_simple_command(GPURenderPassEncoder, "insertDebugMarker", "wgpuRenderPassEncoderInsertDebugMarker", undefined, [String])
add_set_bind_group_command(GPURenderPassEncoder, "wgpuRenderPassEncoderSetBindGroup")
add_simple_command(GPURenderPassEncoder, "setPipeline", "wgpuRenderPassEncoderSetPipeline", undefined, [GPURenderPipeline])
add_simple_command(GPURenderPassEncoder, "setIndexBuffer", "wgpuRenderPassEncoderSetIndexBuffer", undefined, [GPUBuffer, GPUIndexFormat, Optional(Uint64, 0), Optional(Uint64, "arg0.size - arg2")])
add_simple_command(GPURenderPassEncoder, "setVertexBuffer", "wgpuRenderPassEncoderSetVertexBuffer", undefined, [Uint32, GPUBuffer, Optional(Uint64, 0), Optional(Uint64, "arg1.size - arg2")])
add_simple_command(GPURenderPassEncoder, "draw", "wgpuRenderPassEncoderDraw", undefined, [Uint32, Optional(Uint32, 1), Uint32, Uint32])
add_simple_command(GPURenderPassEncoder, "drawIndexed", "wgpuRenderPassEncoderDrawIndexed", undefined, [Uint32, Optional(Uint32, 1), Uint32, Int32, Uint32])
add_simple_command(GPURenderPassEncoder, "drawIndirect", "wgpuRenderPassEncoderDrawIndirect", undefined, [GPUBuffer, Uint64])
add_simple_command(GPURenderPassEncoder, "drawIndexedIndirect", "wgpuRenderPassEncoderDrawIndexedIndirect", undefined, [GPUBuffer, Uint64])

add_simple_command(GPURenderBundleEncoder, "finish", "wgpuRenderBundleEncoderFinish", GPURenderBundle, [GPURenderBundleDescriptor], "wgpuRenderBundleEncoderRelease(subject);\n")
add_simple_command(GPURenderBundleEncoder, "pushDebugGroup", "wgpuRenderBundleEncoderPushDebugGroup", undefined, [String])
add_simple_command(GPURenderBundleEncoder, "popDebugGroup", "wgpuRenderBundleEncoderPopDebugGroup", undefined, [])
add_simple_command(GPURenderBundleEncoder, "insertDebugMarker", "wgpuRenderBundleEncoderInsertDebugMarker", undefined, [String])
add_set_bind_group_command(GPURenderBundleEncoder, "wgpuRenderBundleEncoderSetBindGroup")
add_simple_command(GPURenderBundleEncoder, "setPipeline", "wgpuRenderBundleEncoderSetPipeline", undefined, [GPURenderPipeline])
add_simple_command(GPURenderBundleEncoder, "setIndexBuffer", "wgpuRenderBundleEncoderSetIndexBuffer", undefined, [GPUBuffer, GPUIndexFormat, Optional(Uint64, 0), Optional(Uint64, "arg0.size - arg2")])
add_simple_command(GPURenderBundleEncoder, "setVertexBuffer", "wgpuRenderBundleEncoderSetVertexBuffer", undefined, [Uint32, GPUBuffer, Optional(Uint64, 0), Optional(Uint64, "arg1.size - arg2")])
add_simple_command(GPURenderBundleEncoder, "draw", "wgpuRenderBundleEncoderDraw", undefined, [Uint32, Optional(Uint32, 1), Uint32, Uint32])
add_simple_command(GPURenderBundleEncoder, "drawIndexed", "wgpuRenderBundleEncoderDrawIndexed", undefined, [Uint32, Optional(Uint32, 1), Uint32, Int32, Uint32])
add_simple_command(GPURenderBundleEncoder, "drawIndirect", "wgpuRenderBundleEncoderDrawIndirect", undefined, [GPUBuffer, Uint64])
add_simple_command(GPURenderBundleEncoder, "drawIndexedIndirect", "wgpuRenderBundleEncoderDrawIndexedIndirect", undefined, [GPUBuffer, Uint64])

add_simple_command(GPUQueue, "submit", "wgpuQueueSubmit", undefined, [ArrayType(GPUCommandBuffer)])

add_custom_command(GPUCanvasContext, "configure", ["configuration"], """
__WebGPUReconstruct_DebugOutput("configure");
wgpur.file.writeUint32($COMMAND_ID);
if (this.__id == undefined) {
    __WebGPUReconstruct_AddId(this);
}
wgpur.file.writeUint32(this.__id);
if (configuration.usage == undefined) {
    configuration.usage = 0x10;
}
wgpur.file.writeUint32(configuration.usage);
wgpur.file.writeUint32(this.canvas.width);
wgpur.file.writeUint32(this.canvas.height);
""" + GPUTextureFormat.save("configuration.format") + ArrayType(GPUTextureFormat).save("configuration.viewFormat") + """
""", """
DebugOutput("configure\\n");
const uint32_t canvasID = reader.ReadUint32();
CanvasTexture& texture = canvasTextures[canvasID];
// Release previous "swapchain" texture if there was one.
if (texture.texture != nullptr) {
    wgpuTextureRelease(texture.texture);
    if (texture.viewFormatCount != 0) {
        delete[] texture.viewFormats;
    }
}
texture.usage = reader.ReadUint32() | WGPUTextureUsage_TextureBinding;
texture.width = reader.ReadUint32();
texture.height = reader.ReadUint32();
""" + GPUTextureFormat.load("texture.format") + ArrayType(GPUTextureFormat).load("texture.viewFormat") + """

WGPUTextureDescriptor descriptor = {};
descriptor.usage = texture.usage;
descriptor.dimension = WGPUTextureDimension_2D;
descriptor.size.width = texture.width;
descriptor.size.height = texture.height;
descriptor.size.depthOrArrayLayers = 1;
descriptor.format = texture.format;
descriptor.mipLevelCount = 1;
descriptor.sampleCount = 1;
descriptor.viewFormatCount = texture.viewFormatCount;
descriptor.viewFormats = texture.viewFormats;
canvasTextures[canvasID].texture = wgpuDeviceCreateTexture(device.GetDevice(), &descriptor);
""")

add_custom_command(GPUCanvasContext, "getCurrentTexture", [], """
__WebGPUReconstruct_DebugOutput("getCurrentTexture");
wgpur.file.writeUint32($COMMAND_ID);
wgpur.file.writeUint32(this.__id);
__WebGPUReconstruct_AddId(result);
wgpur.file.writeUint32(result.__id);
wgpur.file.writeUint32(this.canvas.width);
wgpur.file.writeUint32(this.canvas.height);
""", """
DebugOutput("getCurrentTexture\\n");
const uint32_t canvasID = reader.ReadUint32();
const uint32_t id = reader.ReadUint32();
const uint32_t width = reader.ReadUint32();
const uint32_t height = reader.ReadUint32();

CanvasTexture& texture = canvasTextures[canvasID];
if (texture.width != width || texture.height != height) {
    DebugOutput("Canvas size has changed. Recreating texture.\\n");
    // Release the old texture.
    wgpuTextureRelease(texture.texture);
    
    WGPUTextureDescriptor descriptor = {};
    descriptor.usage = texture.usage;
    descriptor.dimension = WGPUTextureDimension_2D;
    descriptor.size.width = width;
    descriptor.size.height = height;
    descriptor.size.depthOrArrayLayers = 1;
    descriptor.format = texture.format;
    descriptor.mipLevelCount = 1;
    descriptor.sampleCount = 1;
    descriptor.viewFormatCount = texture.viewFormatCount;
    descriptor.viewFormats = texture.viewFormats;
    texture.texture = wgpuDeviceCreateTexture(device.GetDevice(), &descriptor);
    texture.width = width;
    texture.height = height;
}
mapGPUTexture[id] = texture.texture;
AddCanvasSize(texture.width, texture.height);
""")

add_custom_command(GPUDevice, "createShaderModule", ["descriptor"], """
__WebGPUReconstruct_DebugOutput("createShaderModule");
wgpur.file.writeUint32($COMMAND_ID);
__WebGPUReconstruct_AddId(result);
wgpur.file.writeUint32(result.__id);
__WebGPUReconstruct_DebugOutput(descriptor.code);
wgpur.file.writeUint64(descriptor.code.length);
for (let i = 0; i < descriptor.code.length; i += 1) {
    wgpur.file.writeUint8(descriptor.code.charCodeAt(i));
}
// TODO Hints
if (descriptor.compilationHints != undefined && descriptor.compilationHints.length > 0) {
    console.warn("WebGPUReconstruct currently doesn't support descriptor.compilationHints. This will be treated as undefined during replay.");
}
""", """
DebugOutput("createShaderModule\\n");
const uint32_t id = reader.ReadUint32();

const uint64_t codeLength = reader.ReadUint64();
char* code = new char[codeLength + 1];
reader.ReadBuffer(reinterpret_cast<uint8_t*>(code), codeLength);
code[codeLength] = '\\0';
DebugOutput(code);
DebugOutput("\\n");

WGPUShaderSourceWGSL wgsl = {};
wgsl.chain.sType = WGPUSType_ShaderSourceWGSL;
wgsl.code.data = code;
wgsl.code.length = codeLength;

WGPUShaderModuleDescriptor descriptor = {};
descriptor.nextInChain = reinterpret_cast<WGPUChainedStruct*>(&wgsl);
// TODO Hints

mapGPUShaderModule[id] = wgpuDeviceCreateShaderModule(device.GetDevice(), &descriptor);
delete[] code;
""")

add_custom_command(GPUQueue, "writeBuffer", ["buffer", "bufferOffset", "data", "dataOffset", "size"], """
__WebGPUReconstruct_DebugOutput("writeBuffer");
wgpur.file.writeUint32($COMMAND_ID);
wgpur.file.writeUint32(buffer.__id);
wgpur.file.writeUint64(bufferOffset);
if (dataOffset == undefined) {
    dataOffset = 0;
}
let dataUint8;
if (ArrayBuffer.isView(data)) {
    dataOffset *= data.BYTES_PER_ELEMENT;
    if (size == undefined) {
        size = data.byteLength - dataOffset;
    } else {
        size *= data.BYTES_PER_ELEMENT;
    }
    dataUint8 = (new Uint8Array(data.buffer)).subarray(data.byteOffset, data.byteOffset + data.byteLength);
} else {
    if (size == undefined) {
        size = data.byteLength - dataOffset;
    }
    dataUint8 = new Uint8Array(data);
}
wgpur.file.writeUint64(size);
wgpur.file.writeBuffer(dataUint8, dataOffset, size);
""", """
DebugOutput("writeBuffer\\n");
const uint32_t id = reader.ReadUint32();
const uint64_t bufferOffset = reader.ReadUint64();
const uint64_t size = reader.ReadUint64();
uint8_t* data = new uint8_t[size];
reader.ReadBuffer(data, size);
wgpuQueueWriteBuffer(device.GetQueue(), GetIdType(mapGPUBuffer, id), bufferOffset, data, size);
delete[] data;
""")

add_custom_command(GPUBuffer, "mapAsync", ["mode", "offset", "size"], """
__WebGPUReconstruct_DebugOutput("mapAsync");
wgpur.file.writeUint32($COMMAND_ID);
if (offset == undefined) {
    offset = 0;
}
if (size == undefined) {
    size = this.size - offset;
}
wgpur.file.writeUint32(this.__id);
wgpur.file.writeUint32(mode);
wgpur.file.writeUint64(offset);
wgpur.file.writeUint64(size);
if ((mode & GPUMapMode.WRITE) == 0) {
    this.__readOnly = true;
}
""", """
DebugOutput("mapAsync\\n");
uint32_t bufferID = reader.ReadUint32();
WGPUBuffer buffer = GetIdType(mapGPUBuffer, bufferID);
const uint32_t mode = reader.ReadUint32();
const uint64_t offset = reader.ReadUint64();
const uint64_t size = reader.ReadUint64();

bufferMapStateLock.lock();
bufferMapState[bufferID] = false;
bufferMapStateLock.unlock();

struct UserData {
    uint32_t bufferID;
    std::unordered_map<uint32_t, bool>* mapState;
    std::mutex* lock;
};

UserData* userdata = new UserData;
userdata->bufferID = bufferID;
userdata->mapState = &bufferMapState;
userdata->lock = &bufferMapStateLock;

WGPUBufferMapCallbackInfo callbackInfo = {};
callbackInfo.mode = WGPUCallbackMode_AllowProcessEvents;
callbackInfo.callback = [](WGPUMapAsyncStatus status, WGPUStringView message, void* userdata1, void* userdata2){
    if (status != WGPUMapAsyncStatus_Success) {
        Logging::Error("Failed to map buffer");
    }

    UserData* userdata = static_cast<UserData*>(userdata1);
    userdata->lock->lock();
    (*userdata->mapState)[userdata->bufferID] = true;
    userdata->lock->unlock();
    
    delete userdata;
};
callbackInfo.userdata1 = userdata;
wgpuBufferMapAsync(buffer, mode, offset, size, callbackInfo);
""")

add_custom_command(GPUBuffer, "getMappedRange", ["offset", "size"], """
__WebGPUReconstruct_DebugOutput("getMappedRange");
wgpur.file.writeUint32($COMMAND_ID);
if (offset == undefined) {
    offset = 0;
}
if (size == undefined) {
    size = this.size - offset;
}
if (this.__mappedRanges == undefined) {
    this.__mappedRanges = [];
}
this.__mappedRanges.push([offset, size, result]);
""", """
DebugOutput("getMappedRange\\n");
""")

add_custom_command(GPUQueue, "writeTexture", ["destination", "data", "dataLayout", "size"], """
__WebGPUReconstruct_DebugOutput("writeTexture");
wgpur.file.writeUint32($COMMAND_ID);
""" + GPUTexelCopyTextureInfo.save("destination") + GPUExtent3D.save("size") + """
let dataUint8;
if (ArrayBuffer.isView(data)) {
    dataUint8 = (new Uint8Array(data.buffer)).subarray(data.byteOffset, data.byteOffset + data.byteLength);
} else {
    dataUint8 = new Uint8Array(data);
}

let size2 = size;
if (size2 instanceof Array) {
    size2 = {
        width: size[0],
        height: size[1],
        depthOrArrayLayers: size[2]
    };
}

// Data layout
let dataLayout2 = {
    offset: 0,
    bytesPerRow: dataLayout.bytesPerRow,
    rowsPerImage: dataLayout.rowsPerImage
};

const blockSize = __WebGPUReconstruct_get_block_size(destination.texture.format);
const imageSize = {
    x: destination.texture.width,
    y: destination.texture.height
};
const logicalMipSize = {
    x: Math.max(1, imageSize.x >> destination.mipLevel),
    y: Math.max(1, imageSize.y >> destination.mipLevel)
};
const physicalMipSize = {
    x: (Math.floor((logicalMipSize.x - 1) / blockSize.x) + 1) * blockSize.x,
    y: (Math.floor((logicalMipSize.y - 1) / blockSize.y) + 1) * blockSize.y
};

if (dataLayout2.bytesPerRow == undefined) {
    dataLayout2.bytesPerRow = Math.floor((physicalMipSize.x - 1) / blockSize.x + 1) * __WebGPUReconstruct_get_bytes_per_block(destination.texture.format);
}
if (dataLayout2.rowsPerImage == undefined) {
    dataLayout2.rowsPerImage = Math.floor((physicalMipSize.y - 1) / blockSize.y + 1);
}

""" + GPUTexelCopyBufferLayout.save("dataLayout2") + """

const offset = (dataLayout.offset == undefined) ? 0 : dataLayout.offset;
const remainingBufferLength = dataUint8.length - offset;
const dataLength = Math.min(remainingBufferLength, size2.depthOrArrayLayers * dataLayout2.rowsPerImage * dataLayout2.bytesPerRow);

wgpur.file.writeUint64(dataLength);
wgpur.file.writeBuffer(dataUint8, offset, dataLength);
""", """
DebugOutput("writeTexture\\n");
""" + GPUTexelCopyTextureInfo.declare_argument("destination") + GPUTexelCopyTextureInfo.load("destination") + GPUExtent3D.declare_argument("size") + GPUExtent3D.load("size") + GPUTexelCopyBufferLayout.declare_argument("dataLayout") + GPUTexelCopyBufferLayout.load("dataLayout") + """
const uint64_t dataLength = reader.ReadUint64();
uint8_t* data = new uint8_t[dataLength];
reader.ReadBuffer(data, dataLength);
wgpuQueueWriteTexture(device.GetQueue(), destination, data, dataLength, dataLayout, &size);
delete[] data;
""" + GPUTexelCopyTextureInfo.cleanup("destination") + GPUTexelCopyBufferLayout.cleanup("dataLayout"))

add_custom_command(GPUQueue, "copyExternalImageToTexture", ["source", "destination", "copySize"], """
__WebGPUReconstruct_DebugOutput("copyExternalImageToTexture");

wgpur.file.writeUint32($COMMAND_ID);

// There is no native equivalent to copyExternalImageToTexture, and implementing it ourselves is quite an endeavor
// as it needs to handle color space conversion, format conversion, multiple sources for the external image, etc.
// To avoid this, we hack around it by allocating a second dummy texture that we copy the external image into,
// then copy the data from this image into a buffer, read back the buffer contents and use writeTexture to upload
// the data during replay.

// Default values.
""" + GPUTexelCopyTextureInfo.save("destination") + GPUExtent3D.save("copySize") + """
// Validation.
let blockSize = __WebGPUReconstruct_get_block_size(destination.texture.format);
if (blockSize.x != 1 || blockSize.y != 1) {
    console.error("copyExternalImageToTexture with block-compressed formats not supported by WebGPUReconstruct.");
}
if (destination.texture.sampleCount > 1) {
    console.error("copyExternalImageToTexture with sampleCount > 1 not supported by WebGPUReconstruct.");
}
let size = copySize;
if (copySize instanceof Array) {
    size = {
        width: copySize[0],
        height: copySize[1],
        depthOrArrayLayers: copySize[2]
    };
}

// Data layout
let dataLayout = {
    offset: 0,
    bytesPerRow: size.width * __WebGPUReconstruct_get_bytes_per_block(destination.texture.format),
    rowsPerImage: size.height
};

// bytesPerRow needs to be 256 byte aligned.
if (dataLayout.bytesPerRow > 0) {
    dataLayout.bytesPerRow = (Math.floor((dataLayout.bytesPerRow - 1) / 256) + 1) * 256;
}
""" + GPUTexelCopyBufferLayout.save("dataLayout") + """

// Reserve area for the data.
let dataLength = dataLayout.bytesPerRow * dataLayout.rowsPerImage * size.depthOrArrayLayers;
wgpur.file.writeUint64(dataLength);
let reserved = wgpur.file.reserve(dataLength);

// Quit if size to copy is 0.
if (dataLayout.bytesPerRow == 0) {
    return;
}

// Allocate dummy texture to copy into.
let dummyTexture = __webGPUReconstruct.GPUDevice_createTexture_original.call(this.__device, {
    size: size,
    dimension: destination.texture.dimension,
    format: destination.texture.format,
    usage: GPUTextureUsage.COPY_SRC | GPUTextureUsage.COPY_DST | GPUTextureUsage.RENDER_ATTACHMENT,
});

// Allocate dummy buffer to copy into.
let dummyBuffer = __webGPUReconstruct.GPUDevice_createBuffer_original.call(this.__device, {
    size: dataLength,
    usage: GPUBufferUsage.MAP_READ | GPUBufferUsage.COPY_DST,
});

// Copy external image into dummy texture.
__webGPUReconstruct.GPUQueue_copyExternalImageToTexture_original.call(this.__device.queue, source,
    {
        texture: dummyTexture,
        aspect: destination.aspect,
        colorSpace: destination.colorSpace,
        premultipliedAlpha: destination.premultipliedAlpha,
    },
    size);

// Copy texture data into buffer.
let commandEncoder = __webGPUReconstruct.GPUDevice_createCommandEncoder_original.call(this.__device);
__webGPUReconstruct.GPUCommandEncoder_copyTextureToBuffer_original.call(commandEncoder,
    {
        texture: dummyTexture,
        aspect: destination.aspect,
    },
    {
        buffer: dummyBuffer,
        bytesPerRow: dataLayout.bytesPerRow,
        rowsPerImage: dataLayout.rowsPerImage,
    }, size);
let commandBuffer = __webGPUReconstruct.GPUCommandEncoder_finish_original.call(commandEncoder);
__webGPUReconstruct.GPUQueue_submit_original.call(this, [commandBuffer]);

// Map buffer.
__webGPUReconstruct.GPUBuffer_mapAsync_original.call(dummyBuffer, GPUMapMode.READ).then(() => {
    // Read back data and write to reserved area.
    let bufferData = new Uint8Array(__webGPUReconstruct.GPUBuffer_getMappedRange_original.call(dummyBuffer));
    wgpur.file.writeReserved(reserved, bufferData);
    __webGPUReconstruct.GPUBuffer_unmap_original.call(dummyBuffer);
    dummyTexture.destroy();
    dummyBuffer.destroy();
});
""", """
DebugOutput("copyExternalImageToTexture\\n");

""" + GPUTexelCopyTextureInfo.declare_argument("destination") + GPUTexelCopyTextureInfo.load("destination") + GPUExtent3D.declare_argument("size") + GPUExtent3D.load("size") + GPUTexelCopyBufferLayout.declare_argument("dataLayout") + GPUTexelCopyBufferLayout.load("dataLayout") + """
const uint64_t dataLength = reader.ReadUint64();
uint8_t* data = new uint8_t[dataLength];
reader.ReadBuffer(data, dataLength);

wgpuQueueWriteTexture(device.GetQueue(), destination, data, dataLength, dataLayout, &size);

// Cleanup
delete[] data;
""" + GPUTexelCopyTextureInfo.cleanup("destination") + GPUTexelCopyBufferLayout.cleanup("dataLayout"))

add_custom_command(GPUDevice, "importExternalTexture", ["descriptor"], """
__WebGPUReconstruct_DebugOutput("importExternalTexture");
wgpur.file.writeUint32($COMMAND_ID);

if (result.__id != undefined) {
    // Duplicate import, no need to re-import.
    wgpur.file.writeUint8(0);
    return;
}
wgpur.file.writeUint8(1);
__WebGPUReconstruct_AddId(result);
wgpur.file.writeUint32(result.__id);

// Determine image dimensions based on https://gpuweb.github.io/gpuweb/#external-source-dimensions
let width = 1;
let height = 1;
if (descriptor.source instanceof HTMLVideoElement) {
    width = descriptor.source.videoWidth;
    height = descriptor.source.videoHeight;
} else if (descriptor.source instanceof VideoFrame) {
    width = descriptor.source.displayWidth;
    height = descriptor.source.displayHeight;
} else {
    console.error("Unknown source in importExternalTexture");
}
wgpur.file.writeUint32(width);
wgpur.file.writeUint32(height);

// Allocate dummy texture to copy into.
let dummyTexture = __webGPUReconstruct.GPUDevice_createTexture_original.call(this, {
    size: {
        width: width,
        height: height
    },
    format: "rgba8unorm",
    usage: GPUTextureUsage.COPY_SRC | GPUTextureUsage.COPY_DST | GPUTextureUsage.RENDER_ATTACHMENT,
});

// Data layout
let dataLayout = {
    offset: 0,
    bytesPerRow: width * 4,
    rowsPerImage: height
};

// bytesPerRow needs to be 256 byte aligned.
dataLayout.bytesPerRow = (Math.floor((dataLayout.bytesPerRow - 1) / 256) + 1) * 256;

// Reserve area for the data.
let dataLength = dataLayout.bytesPerRow * dataLayout.rowsPerImage;
wgpur.file.writeUint64(dataLength);
let reserved = wgpur.file.reserve(dataLength);

// Allocate dummy buffer to copy into.
let dummyBuffer = __webGPUReconstruct.GPUDevice_createBuffer_original.call(this, {
    size: dataLength,
    usage: GPUBufferUsage.MAP_READ | GPUBufferUsage.COPY_DST,
});

let commandEncoder = __webGPUReconstruct.GPUDevice_createCommandEncoder_original.call(this);

// Copy external image into dummy texture.
let pipeline = __WebGPUReconstruct_getExternalTextureBlitPipeline(this);
let sampler = __WebGPUReconstruct_getExternalTextureBlitSampler(this);
let bindGroup = __webGPUReconstruct.GPUDevice_createBindGroup_original.call(this, {
    layout: __webGPUReconstruct.GPURenderPipeline_getBindGroupLayout_original.call(pipeline, 0),
    entries: [
        {
            binding: 0,
            resource: sampler
        },
        {
            binding: 1,
            resource: result
        }
    ]
});

let renderPass = __webGPUReconstruct.GPUCommandEncoder_beginRenderPass_original.call(commandEncoder, {
    colorAttachments: [
        {
            view: __webGPUReconstruct.GPUTexture_createView_original.call(dummyTexture),
            loadOp: "clear",
            storeOp: "store"
        }
    ]
});
__webGPUReconstruct.GPURenderPassEncoder_setPipeline_original.call(renderPass, pipeline);
__webGPUReconstruct.GPURenderPassEncoder_setBindGroup_original.call(renderPass, 0, bindGroup);
__webGPUReconstruct.GPURenderPassEncoder_draw_original.call(renderPass, 3);
__webGPUReconstruct.GPURenderPassEncoder_end_original.call(renderPass);

// Copy texture data into buffer.
__webGPUReconstruct.GPUCommandEncoder_copyTextureToBuffer_original.call(commandEncoder,
    {
        texture: dummyTexture,
    },
    {
        buffer: dummyBuffer,
        bytesPerRow: dataLayout.bytesPerRow,
        rowsPerImage: dataLayout.rowsPerImage,
    },
    {
        width: width,
        height: height
    });
let commandBuffer = __webGPUReconstruct.GPUCommandEncoder_finish_original.call(commandEncoder);
__webGPUReconstruct.GPUQueue_submit_original.call(this.queue, [commandBuffer]);

// Map buffer.
__webGPUReconstruct.GPUBuffer_mapAsync_original.call(dummyBuffer, GPUMapMode.READ).then(() => {
    // Read back data and write to reserved area.
    let bufferData = new Uint8Array(__webGPUReconstruct.GPUBuffer_getMappedRange_original.call(dummyBuffer));
    wgpur.file.writeReserved(reserved, bufferData);
    __webGPUReconstruct.GPUBuffer_unmap_original.call(dummyBuffer);
    dummyTexture.destroy();
    dummyBuffer.destroy();
});
""", """
DebugOutput("importExternalTexture\\n");
if (reader.ReadUint8()) {
    const uint32_t id = reader.ReadUint32();

    WGPUTextureDescriptor desc = {};
    desc.usage = WGPUTextureUsage_TextureBinding | WGPUTextureUsage_CopyDst;
    desc.dimension = WGPUTextureDimension_2D;
    desc.size.width = reader.ReadUint32();
    desc.size.height = reader.ReadUint32();
    desc.size.depthOrArrayLayers = 1;
    desc.format = WGPUTextureFormat_RGBA8Unorm;
    desc.mipLevelCount = 1;
    desc.sampleCount = 1;

    ExternalTexture& externalTexture = externalTextures[id];
    externalTexture.texture = wgpuDeviceCreateTexture(device.GetDevice(), &desc);
    externalTexture.textureView = wgpuTextureCreateView(externalTexture.texture, nullptr);

    WGPUTexelCopyTextureInfo destination = {};
    destination.texture = externalTexture.texture;
    destination.aspect = WGPUTextureAspect_All;

    WGPUTexelCopyBufferLayout dataLayout = {};
    dataLayout.bytesPerRow = desc.size.width * 4;
    // bytesPerRow needs to be 256 byte aligned.
    dataLayout.bytesPerRow = (((dataLayout.bytesPerRow - 1) / 256) + 1) * 256;
    dataLayout.rowsPerImage = desc.size.height;

    const uint64_t dataLength = reader.ReadUint64();
    uint8_t* data = new uint8_t[dataLength];
    reader.ReadBuffer(data, dataLength);

    wgpuQueueWriteTexture(device.GetQueue(), &destination, data, dataLength, &dataLayout, &desc.size);

    // Cleanup
    delete[] data;
}
""")

# Basic line indentation based on {}.
def format(code, baseIndentation = 0):
    formatted = ''
    indentation = baseIndentation
    
    split = code.splitlines(True)
    for line in split:
        indentation -= line.count('}') - line.count('{}')
        for i in range(indentation):
            formatted += '    '
        formatted += line.strip() + '\n'
        indentation += line.count('{') - line.count('{}')
    
    return formatted

captureCommandsString = format(captureCommandsString)
runCommandsString = format(runCommandsString, 1)
mapString = format(mapString, 1)
enumSaveFunctionsString = format(enumSaveFunctionsString)
enumConversionsString = format(enumConversionsString)
structSaveFunctionsString = format(structSaveFunctionsString)
structLoadFunctionsString = format(structLoadFunctionsString)
structFunctionDeclarationsString = format(structFunctionDeclarationsString, 1)