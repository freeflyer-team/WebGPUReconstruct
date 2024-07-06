# A type that is not currently supported and will warn the user if set.
class UnsupportedType:
    def save(self, name):
        capture = 'if (' + name + ' != undefined) {\n'
        capture += 'console.warn("WebGPUReconstruct currently doesn\'t support ' + name + '. This will be treated as undefined during replay.");\n'
        capture += '}\n'
        return capture
    
    def load(self, name):
        return ''
    
    def declare_argument(self, name):
        assert(False)
        return ''
    
    def as_argument(self, name):
        assert(False)
        return ''
    
    def cleanup(self, name):
        return ''
Unsupported = UnsupportedType()