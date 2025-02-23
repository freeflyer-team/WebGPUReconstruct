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
        replay += name + '.data = new char[stringLength];\n'
        replay += 'reader.ReadBuffer(reinterpret_cast<uint8_t*>(const_cast<char*>(' + name + '.data)), stringLength);\n'
        replay += name + '.length = stringLength;\n'
        replay += '} else {\n'
        replay += name + '.data = nullptr;\n';
        replay += name + '.length = WGPU_STRLEN;\n'
        replay += '}\n'
        return replay
    
    def declare_argument(self, name):
        declare = 'WGPUStringView ' + name + ';\n'
        return declare
    
    def as_argument(self, name):
        return name
    
    def cleanup(self, name):
        cleanup = 'if (' + name + '.length > 0) {\n'
        cleanup += 'delete[] ' + name + '.data;\n'
        cleanup += '}\n'
        return cleanup
String = StringType()