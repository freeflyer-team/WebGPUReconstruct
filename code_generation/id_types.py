mapString = ""

# A type that is identified by an id.
class IdType:
    def __init__(self, webName, nativeName = ""):
        global mapString
        
        self.webName = webName
        self.nativeName = nativeName
        if nativeName == "":
            self.nativeName = 'W' + webName
        
        mapString += 'std::unordered_map<uint32_t, ' + self.nativeName + '> map' + self.webName + ';\n'
    
    def save(self, name):
        capture = 'if (' + name + ' == undefined) {\n'
        capture += '__WebGPUReconstruct_file.writeUint32(0);\n'
        capture += '} else {\n'
        capture += '__WebGPUReconstruct_file.writeUint32(' + name + '.__id);\n'
        capture += '}\n'
        return capture
    
    def load(self, name):
        replay = name + ' = GetIdType(map' + self.webName + ', reader.ReadUint32());\n'
        return replay
    
    def declare_argument(self, name):
        return self.nativeName + ' ' + name + ';\n'
    
    def as_argument(self, name):
        return name
    
    def cleanup(self, name):
        return ''

GPUBuffer = IdType("GPUBuffer")
GPUTexture = IdType("GPUTexture")
GPUTextureView = IdType("GPUTextureView")
GPUSampler = IdType("GPUSampler")
GPUBindGroupLayout = IdType("GPUBindGroupLayout")
GPUBindGroup = IdType("GPUBindGroup")
GPUPipelineLayout = IdType("GPUPipelineLayout")
GPUShaderModule = IdType("GPUShaderModule")
GPUComputePipeline = IdType("GPUComputePipeline")
GPURenderPipeline = IdType("GPURenderPipeline")
GPUCommandBuffer = IdType("GPUCommandBuffer")
GPUCommandEncoder = IdType("GPUCommandEncoder")
GPUComputePassEncoder = IdType("GPUComputePassEncoder")
GPURenderPassEncoder = IdType("GPURenderPassEncoder")
GPURenderBundle = IdType("GPURenderBundle")
GPURenderBundleEncoder = IdType("GPURenderBundleEncoder")
GPUQuerySet = IdType("GPUQuerySet")