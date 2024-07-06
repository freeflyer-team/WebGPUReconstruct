# Primitive types.
class PrimitiveType:
    def __init__(self, webName, nativeName):
        self.webName = webName
        self.nativeName = nativeName
    
    def save(self, name):
        capture = '__WebGPUReconstruct_file.write' + self.webName + '(' + name + ');\n'
        return capture
    
    def load(self, name):
        replay = name + ' = reader.Read' + self.webName + '();\n'
        return replay
    
    def declare_argument(self, name):
        return self.nativeName + ' ' + name + ';\n'
    
    def as_argument(self, name):
        return name
    
    def cleanup(self, name):
        return ''

# Optional wrapper for primitive types. Sets a default value other than 0 when a primitive type is not provided.
class Optional:
    def __init__(self, type, defaultValue):
        assert(isinstance(type, PrimitiveType))
        self.type = type
        self.defaultValue = defaultValue
    
    def save(self, name):
        capture = 'if (' + name + ' == undefined) {\n'
        capture += name + ' = ' + str(self.defaultValue) + ';\n'
        capture += '}\n'
        capture += self.type.save(name)
        return capture
    
    def load(self, name):
        return self.type.load(name)
    
    def declare_argument(self, name):
        return self.type.declare_argument(name)
    
    def as_argument(self, name):
        return name
    
    def cleanup(self, name):
        return ''

Uint8 = PrimitiveType("Uint8", "uint8_t")
Uint16 = PrimitiveType("Uint16", "uint16_t")
Uint32 = PrimitiveType("Uint32", "uint32_t")
Uint64 = PrimitiveType("Uint64", "uint64_t")
Int32 = PrimitiveType("Int32", "int32_t")
Bool = PrimitiveType("Uint8", "bool")
Float32 = PrimitiveType("Float32", "float")
Float64 = PrimitiveType("Float64", "double")