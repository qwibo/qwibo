/**
 * Preload minimale — nessun bridge custom in v0.1 (UI = FastAPI embedded).
 */

const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("qwiboDesktop", {
  version: "0.1.0",
});
