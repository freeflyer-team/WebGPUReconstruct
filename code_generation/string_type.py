# Unfortunately, can't just be done as an array of chars.
class StringType:
    def save(self, name):
        capture = 'if (' + name + ' == undefined) {\n'
        capture += '__WebGPUReconstruct_file.writeUint64(0);\n'
        capture += '} else {\n'
        capture += '__WebGPUReconstruct_file.writeUint64(' + name + '.length);\n'
        capture += 'for (let stringI = 0; stringI < ' + name + '.length; stringI += 1) {\n'
        capture += '__WebGPUReconstruct_file.writeUint8(' + name + '.charCodeAt(stringI));\n'
        capture += '}\n'
        capture += '}\n'
        return capture
    
    def load(self, name):
        replay = 'stringLength = reader.ReadUint64();\n'
        replay += 'if (stringLength > 0) {\n'
        replay += name + ' = new char[stringLength + 1];\n'
        replay += 'reader.ReadBuffer(reinterpret_cast<uint8_t*>(const_cast<char*>(' + name + ')), stringLength);\n'
        replay += 'const_cast<char*>(' + name + ')[stringLength] = \'\\0\';\n'
        replay += '} else {\n'
        replay += name + ' = nullptr;\n';
        replay += '}\n'
        return replay
    
    def declare_argument(self, name):
        return 'char* ' + name + ';\n';
    
    def as_argument(self, name):
        return name
    
    def cleanup(self, name):
        cleanup = 'if (' + name + ' != nullptr) {\n'
        cleanup += 'delete[] ' + name + ';\n'
        cleanup += '}\n'
        return cleanup
String = StringType()