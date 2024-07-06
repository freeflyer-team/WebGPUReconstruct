saveFile = async () => {
    let evt = document.createEvent('Event');
    evt.initEvent('__WebGPUReconstruct_saveCapture', true, false);
    document.dispatchEvent(evt);
};

saveFile();
