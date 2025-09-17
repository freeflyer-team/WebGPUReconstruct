from code_generation.primitive_types import *
from code_generation.string_type import *
from code_generation.id_types import *

# Type not covered by the other types.
class CustomType:
    def __init__(self, saveCode, loadCode, declareArgumentCode = 'assert(false);\n', asArgumentCode = '$name', cleanupCode = ''):
        self.saveCode = saveCode
        self.loadCode = loadCode
        self.declareArgumentCode = declareArgumentCode
        self.asArgumentCode = asArgumentCode
        self.cleanupCode = cleanupCode
    
    def save(self, name):
        return self.saveCode.replace('$name', name)
    
    def load(self, name):
        return self.loadCode.replace('$name', name)
    
    def declare_argument(self, name):
        return self.declareArgumentCode.replace('$name', name)
    
    def as_argument(self, name):
        return self.asArgumentCode.replace('$name', name)
    
    def cleanup(self, name):
        return self.cleanupCode.replace('$name', name)

GPUColor = CustomType("""
if ($name.r != undefined) {
    wgpur.file.writeFloat64($name.r);
} else {
    wgpur.file.writeFloat64($name[0]);
}
if ($name.g != undefined) {
    wgpur.file.writeFloat64($name.g);
} else {
    wgpur.file.writeFloat64($name[1]);
}
if ($name.b != undefined) {
    wgpur.file.writeFloat64($name.b);
} else {
    wgpur.file.writeFloat64($name[2]);
}
if ($name.a != undefined) {
    wgpur.file.writeFloat64($name.a);
} else {
    wgpur.file.writeFloat64($name[3]);
}
""", """
$name.r = reader.ReadFloat64();
$name.g = reader.ReadFloat64();
$name.b = reader.ReadFloat64();
$name.a = reader.ReadFloat64();
""", "WGPUColor $name;", "&$name"
)

GPUExtent3D = CustomType("""
if ($name instanceof Array) {
    wgpur.file.writeUint32($name[0]);
    if ($name.length < 2) {
        $name.push(1);
    }
    wgpur.file.writeUint32($name[1]);
    if ($name.length < 3) {
        $name.push(1);
    }
    wgpur.file.writeUint32($name[2]);
} else {
    wgpur.file.writeUint32($name.width);
    if ($name.height == undefined) {
        $name.height = 1;
    }
    wgpur.file.writeUint32($name.height);
    if ($name.depthOrArrayLayers == undefined) {
        $name.depthOrArrayLayers = 1;
    }
    wgpur.file.writeUint32($name.depthOrArrayLayers);
}
""", """
$name.width = reader.ReadUint32();
$name.height = reader.ReadUint32();
$name.depthOrArrayLayers = reader.ReadUint32();
""", "WGPUExtent3D $name;", "&$name"
)

GPUOrigin3D = CustomType("""
if ($name instanceof Array) {
    wgpur.file.writeUint32($name[0]);
    wgpur.file.writeUint32($name[1]);
    wgpur.file.writeUint32($name[2]);
} else {
    wgpur.file.writeUint32($name.x);
    wgpur.file.writeUint32($name.y);
    wgpur.file.writeUint32($name.z);
}
""", """
$name.x = reader.ReadUint32();
$name.y = reader.ReadUint32();
$name.z = reader.ReadUint32();
""", "WGPUOrigin3D $name;"
)

Uint32DefaultMax = CustomType("""
if ($name == undefined) {
    wgpur.file.writeUint32(0xffffffff);
} else {
    wgpur.file.writeUint32($name);
}
""",
"""
$name = reader.ReadUint32();
""", "uint32_t $name;"
)

GPUBindGroupEntry = CustomType("""
wgpur.file.writeUint32($name.binding);
if ($name.resource instanceof GPUSampler) {
    wgpur.file.writeUint8(0);
    wgpur.file.writeUint32($name.resource.__id);
} else if ($name.resource instanceof GPUTextureView) {
    wgpur.file.writeUint8(1);
    wgpur.file.writeUint32($name.resource.__id);
} else if (typeof GPUExternalTexture !== 'undefined' && $name.resource instanceof GPUExternalTexture) {
    wgpur.file.writeUint8(3);
    wgpur.file.writeUint32($name.resource.__id);
} else if ($name.resource instanceof GPUBuffer) {
    wgpur.file.writeUint8(2);
    wgpur.file.writeUint32($name.resource.__id);
    wgpur.file.writeUint64(0);
    wgpur.file.writeUint64($name.resource.size);
} else if ($name.resource instanceof GPUTexture) {
    wgpur.file.writeUint8(4);
    wgpur.file.writeUint32($name.resource.__id);
} else {
    wgpur.file.writeUint8(2);
    wgpur.file.writeUint32($name.resource.buffer.__id);
    let offset = $name.resource.offset;
    if (offset == undefined) {
        offset = 0;
    }
    wgpur.file.writeUint64(offset);
    let size = $name.resource.size;
    if (size == undefined) {
        size = $name.resource.buffer.size - offset;
    }
    wgpur.file.writeUint64(size);
}
""",
"""
$name = {};
$name.binding = reader.ReadUint32();
const uint8_t type = reader.ReadUint8();
switch (type) {
case 0:
    $name.sampler = GetIdType(mapGPUSampler, reader.ReadUint32());
    break;
case 1:
    $name.textureView = GetIdType(mapGPUTextureView, reader.ReadUint32());
    break;
case 2:
    $name.buffer = GetIdType(mapGPUBuffer, reader.ReadUint32());
    $name.offset = reader.ReadUint64();
    $name.size = reader.ReadUint64();
    break;
case 3:
    $name.textureView = externalTextures[reader.ReadUint32()].textureView;
    break;
case 4:
    $name.textureView = GetDefaultTextureView(reader.ReadUint32());
    break;
default:
    ErrorOutput("Unknown resource type when creating bind group.\\n");
    exit(0);
}
""", "WGPUBindGroupEntry $name;")
GPUBindGroupEntry.nativeName = "WGPUBindGroupEntry"

GPUConstants = CustomType("""
if ($names == undefined) {
    wgpur.file.writeUint64(0);
} else {
    let keys = Object.keys($names);
    wgpur.file.writeUint64(keys.length);
    for (let i = 0; i < keys.length; i += 1) {
        """ + String.save("keys[i]") + """
        wgpur.file.writeFloat64($names[keys[i]]);
    }
}
""", """
$nameCount = reader.ReadUint64();
WGPUConstantEntry* constants = new WGPUConstantEntry[$nameCount];
for (uint64_t keyI = 0; keyI < $nameCount; ++keyI) {
    """ + String.load("constants[keyI].key") + """
    constants[keyI].value = reader.ReadFloat64();
}
$names = constants;
""", 'assert(false);\n', '$name', """
for (uint64_t keyI = 0; keyI < $nameCount; ++keyI) {
    if ($names[keyI].key.length > 0) {
        delete[] $names[keyI].key.data;
    }
}
delete[] $names;
""")

GPUTexelCopyBufferInfo = CustomType(GPUBuffer.save("$name.buffer") + "\n"
    + Uint64.save("$name.offset") + "\n"
    + Uint32DefaultMax.save("$name.bytesPerRow") + "\n"
    + Uint32DefaultMax.save("$name.rowsPerImage"),
    GPUBuffer.load("$name.buffer") + "\n"
    + Uint64.load("$name.layout.offset") + "\n"
    + Uint32DefaultMax.load("$name.layout.bytesPerRow") + "\n"
    + Uint32DefaultMax.load("$name.layout.rowsPerImage"),
    "WGPUTexelCopyBufferInfo $name;",
    "&$name")

# TODO Remove and define a GPUOptionalBool type.
DepthWriteEnabled = CustomType("""
wgpur.file.writeUint8($name);
""",
"""
$name = reader.ReadUint8() ? WGPUOptionalBool_True : WGPUOptionalBool_False;
""")

TextureOrTextureView = CustomType("""
if ($name == undefined) {
    wgpur.file.writeUint8(0);
} else if ($name instanceof GPUTextureView) {
    wgpur.file.writeUint8(1);
    wgpur.file.writeUint32($name.__id);
} else if ($name instanceof GPUTexture) {
    wgpur.file.writeUint8(2);
    wgpur.file.writeUint32($name.__id);
}
""",
"""
switch (reader.ReadUint8()) {
case 0:
    $name = nullptr;
    break;
case 1:
    $name = GetIdType(mapGPUTextureView, reader.ReadUint32());
    break;
case 2:
    $name = GetDefaultTextureView(reader.ReadUint32());
    break;
}
""")