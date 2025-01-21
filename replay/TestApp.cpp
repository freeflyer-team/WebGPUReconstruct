#include "TestApp.hpp"

#include "../build/replay/Capture.hpp"
#include <chrono>
#include <string>
#include <fstream>
#include <sstream>
#include "Configuration.hpp"
#include "Logging.hpp"

using namespace std;

namespace WebGPUNativeReplay {

TestApp::TestApp(const Window& window, const Configuration& configuration) :
    adapter(window, configuration.backendType),
    device(adapter),
    swapChain(adapter, device, window, configuration.width, configuration.height, configuration.mailbox),
    offscreen(configuration.offscreen),
    statsFile(configuration.statsFile)
{

}

TestApp::~TestApp() {

}

void TestApp::RunCapture(string_view filename, std::function<bool(void)> frameCallback) {
    Capture capture(filename, adapter, device, swapChain, offscreen);
    if (!capture.IsValid()) {
        return;
    }

    const chrono::high_resolution_clock::time_point start = chrono::high_resolution_clock::now();

    uint32_t frameCount = 0;
    bool started = false;
    bool finished = false;
    bool prematureQuit = false;
    while (!finished) {
        Capture::Status status = capture.RunNextCommand();
        switch (status) {
        case Capture::Status::END_OF_CAPTURE:
            finished = true;
            break;
        case Capture::Status::FRAME_START:
            started = true;
            break;
        case Capture::Status::FRAME_END:
            if (!frameCallback()) {
                finished = true;
                prematureQuit = true;
            }
            if (started) {
                frameCount++;
            }
            break;
        default:
            break;
        }
    }

    if (!prematureQuit) {
        const chrono::high_resolution_clock::time_point end = chrono::high_resolution_clock::now();
        const chrono::duration<double> duration = chrono::duration_cast<chrono::duration<double>>(end - start);

        stringstream stats;
        stats << "Ran " << frameCount << " frames in " << duration.count() << " seconds.\n";

        Logging::Info(stats.str());

        if (!statsFile.empty()) {
            ofstream file;
            file.open(statsFile);
            file << stats.str();
            file.close();
        }
    }
}

}
