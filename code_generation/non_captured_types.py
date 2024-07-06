# A type that isn't captured.
class NonCapturedType:
    def __init__(self, webName, nativeName, nativeReplay):
        self.webName = webName
        self.nativeName = nativeName
        self.nativeReplay = nativeReplay
    
    def declare_argument(self, name):
        assert(False)
        return ''
    
    def as_argument(self, name):
        assert(False)
        return ''
    
    def cleanup(self, name):
        return ''

undefined = NonCapturedType("undefined", "void", "")
GPUDevice = NonCapturedType("GPUDevice", "WGPUDevice", "device.GetDevice()")
GPUQueue = NonCapturedType("GPUQueue", "WGPUQueue", "device.GetQueue()")
GPUCanvasContext = NonCapturedType("GPUCanvasContext", "", "")