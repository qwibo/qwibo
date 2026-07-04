const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("setupApi", {
  onProgress: (callback) => {
    ipcRenderer.on("setup-progress", (_event, data) => callback(data));
  },
});
