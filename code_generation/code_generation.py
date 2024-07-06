import shutil

# Increment the file version whenever a change is introduced.
fileVersion = 4

from code_generation.commands import *

def replace_string_in_file(filename, oldString, newString):
    file = open(filename, "r")
    contents = file.read()
    file.close()
    
    contents = contents.replace(oldString, newString)
    
    file = open(filename, "w")
    file.write(contents)
    file.close()

def add_prefix_to_file(filename, prefix):
    file = open(filename, "r")
    contents = file.read()
    file.close()
    
    contents = prefix + contents
    
    file = open(filename, "w")
    file.write(contents)
    file.close()

def write_capture_files(configuration, browser):
    shutil.copytree("capture", "build/capture/" + browser, dirs_exist_ok=True)
    if browser == "firefox":
        replace_string_in_file("build/capture/" + browser + "/manifest.json", "$BROWSER_SPECIFIC", """
    "background": {
        "scripts": ["scripts/background.js"]
    },
    "browser_specific_settings": {
        "gecko": {
            "id": "webgpureconstruct@chainsawkitten.net"
        },
        "gecko_android": {
            "id": "webgpureconstruct@chainsawkitten.net"
        }
    }
""")
    else:
        replace_string_in_file("build/capture/" + browser + "/manifest.json", "$BROWSER_SPECIFIC", """
    "background": {
        "service_worker": "scripts/background.js"
    }
""")
    
    contentPath = "build/capture/" + browser + "/scripts/content.js"
    add_prefix_to_file(contentPath, "const __WebGPUReconstruct_DEBUG = " + ("true" if configuration["debug"] else "false") + ";\n")
    replace_string_in_file(contentPath, "$FILE_VERSION", str(fileVersion))
    replace_string_in_file(contentPath, "$CAPTURE_COMMANDS", captureCommandsString)
    replace_string_in_file(contentPath, "$WRAP_COMMANDS", wrapCommandsString)
    
    shutil.make_archive("build/capture/" + browser, 'zip', "build/capture/" + browser)

def write_replay_files():
    shutil.copyfile("replay/Capture.cpp", "build/replay/Capture.cpp")
    shutil.copyfile("replay/Capture.hpp", "build/replay/Capture.hpp")
    
    replace_string_in_file("build/replay/Capture.cpp", "$FILE_VERSION", str(fileVersion))
    replace_string_in_file("build/replay/Capture.cpp", "$RUN_COMMANDS", runCommandsString)
    replace_string_in_file("build/replay/Capture.cpp", "$ENUM_CONVERSIONS", enumConversionsString)
    replace_string_in_file("build/replay/Capture.hpp", "$MAPS", mapString)