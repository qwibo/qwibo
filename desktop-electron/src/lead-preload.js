/**
 * Preload del modal lead-gen: bridge sicuro renderer ↔ main.
 * La lingua arriva via additionalArguments (--locale=xx).
 */

const { contextBridge, ipcRenderer } = require("electron");

const localeArg = process.argv.find((a) => a.startsWith("--locale="));
const locale = localeArg ? localeArg.slice("--locale=".length) : "en";

contextBridge.exposeInMainWorld("qwiboLeads", {
  locale,
  submit: (email, consent) => ipcRenderer.invoke("leads:submit", { email, consent }),
  skip: () => ipcRenderer.send("leads:skip"),
});
