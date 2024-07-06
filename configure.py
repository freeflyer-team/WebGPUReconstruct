import argparse
import json
from pathlib import Path

# Parse arguments.
parser = argparse.ArgumentParser(description = "WebGPUReconstruct build configuration.")
parser.add_argument("--no-host", action = 'store_true', help = "Don't build the replayer for the host platform.")
parser.add_argument("--dawn", action = 'store_true', help = "Build the replayer with the Dawn backend.")
parser.add_argument("--wgpu", action = 'store_true', help = "Build the replayer with the wgpu backend.")
parser.add_argument("--android", action = 'store_true', help = "Build the replayer for Android.")
parser.add_argument("--ndk", help = "Path to where the NDK is stored. Required when building for Android.")
parser.add_argument("--target", default = "debug", help = "Target to build (debug/release). Default: debug.")
args=parser.parse_args()

# Validation.
build_replayer = not args.no_host or args.android
if build_replayer and not args.dawn and not args.wgpu:
    print("At least one backend needed to build replayer (--dawn or --wgpu).")
    quit()

if args.target != "debug" and args.target != "release":
    print("Unknown target: " + args.target)
    quit()

# Create build directory if it doesn't exist.
Path("build").mkdir(parents=True, exist_ok=True)

# Store configuration.
configuration = {
    "host" : not args.no_host,
    "dawn" : args.dawn,
    "wgpu" : args.wgpu,
    "android" : args.android,
    "ndk" : args.ndk,
    "debug" : (args.target == "debug"),
}

file = open("build/configuration.json", "w")
file.write(json.dumps(configuration))
file.close()

print("WebGPUReconstruct configured successfully.")