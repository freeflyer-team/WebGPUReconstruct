# Unfortunately, can't just be done as an array of chars.
class StringType:
    def save(self, name):
        capture = 'if (' + name + ' == undefined) {\n'
        capture += '__WebGPUReconstruct_file.writeUint64(0);\n'
        capture += '} else {\n'
        capture += '__WebGPUReconstruct_file.writeString(String(' + name + '));\n'
        capture += '}\n'
        return capture
    
    def load(self, name):
        replay = 'stringLength = reader.ReadUint64();\n'
        replay += 'if (stringLength > 0) {\n'
        replay += '#if WEBGPU_BACKEND_DAWN\n'
        replay += name + '.data = new char[stringLength];\n'
        replay += 'reader.ReadBuffer(reinterpret_cast<uint8_t*>(const_cast<char*>(' + name + '.data)), stringLength);\n'
        replay += name + '.length = stringLength;\n'
        replay += '#else\n'
        replay += name + ' = new char[stringLength + 1];\n'
        replay += 'reader.ReadBuffer(reinterpret_cast<uint8_t*>(const_cast<char*>(' + name + ')), stringLength);\n'
        replay += 'const_cast<char*>(' + name + ')[stringLength] = \'\\0\';\n'
        replay += '#endif\n'
        replay += '} else {\n'
        replay += '#if WEBGPU_BACKEND_DAWN\n'
        replay += name + '.data = nullptr;\n';
        replay += name + '.length = WGPU_STRLEN;\n'
        replay += '#else\n'
        replay += name + ' = nullptr;\n';
        replay += '#endif\n'
        replay += '}\n'
        return replay
    
    def declare_argument(self, name):
        declare = '#if WEBGPU_BACKEND_DAWN\n'
        declare += 'WGPUStringView ' + name + ';\n'
        declare += '#else\n'
        declare += 'char* ' + name + ';\n';
        declare += '#endif\n'
        return declare
    
    def as_argument(self, name):
        return name
    
    def cleanup(self, name):
        cleanup = '#if WEBGPU_BACKEND_DAWN\n'
        cleanup += 'if (' + name + '.length > 0) {\n'
        cleanup += 'delete[] ' + name + '.data;\n'
        cleanup += '}\n'
        cleanup += '#else\n'
        cleanup += 'if (' + name + ' != nullptr) {\n'
        cleanup += 'delete[] ' + name + ';\n'
        cleanup += '}\n'
        cleanup += '#endif\n'
        return cleanup
String = StringType()