/**
 * Preload del wizard lingua: bridge sicuro renderer ↔ main.
 * La lingua del SO (pre-selezione) arriva via additionalArguments (--oslocale=xx).
 */

const { contextBridge, ipcRenderer } = require("electron");

const arg = process.argv.find((a) => a.startsWith("--oslocale="));
const osLocale = arg ? arg.slice("--oslocale=".length) : "en";

contextBridge.exposeInMainWorld("qwiboLang", {
  osLocale,
  choose: (code) => ipcRenderer.send("lang:choose", code),
});
