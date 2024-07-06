#include "TestApp.hpp"

#include <game-activity/GameActivity.cpp>
#include <game-text-input/gametextinput.cpp>
#include <string>
#include <android/log.h>

extern "C" {

#include <game-activity/native_app_glue/android_native_app_glue.c>

void handle_cmd(android_app *app, int32_t cmd) {
    switch (cmd) {
        case APP_CMD_INIT_WINDOW:
        {
            WebGPUNativeReplay::Window window;
            window.window = app->window;
            
            int width = ANativeWindow_getWidth(window.window);
            int height = ANativeWindow_getWidth(window.window);
            std::string filename = std::string(app->activity->externalDataPath) + "/capture.wgpur";
            __android_log_print(ANDROID_LOG_INFO, "WebGPUNativeReplay", "Filename: %s", filename.c_str());
            
            WebGPUNativeReplay::TestApp testApp(window, width, height);
            testApp.RunCapture(filename);
            
            break;
        }
        case APP_CMD_TERM_WINDOW:
            
            break;
        default:
            break;
    }
}

void android_main(struct android_app *app) {
    // Register an event handler for Android events
    app->onAppCmd = handle_cmd;

    // This sets up a typical game/event loop. It will run until the app is destroyed.
    int events;
    android_poll_source *pSource;
    do {
        // Process all pending events before running game logic.
        if (ALooper_pollAll(0, nullptr, &events, (void **) &pSource) >= 0) {
            if (pSource) {
                pSource->process(app, pSource);
            }
        }
    } while (!app->destroyRequested);
}
}
