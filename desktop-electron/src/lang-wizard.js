/**
 * Wizard lingua al primo avvio: schermata "scegli lingua" pre-selezionata sulla
 * lingua del sistema operativo. Ritorna il codice scelto; main.js lo passa al
 * backend via QWIBO_UI_LOCALE. Il comportamento automatico (rilevamento SO) resta
 * anche se il wizard viene saltato/chiuso.
 */

const { BrowserWindow, ipcMain, app } = require("electron");
const path = require("path");

const CORE = ["it", "en", "fr", "es", "de"];

function osLocale() {
  const s = String(app.getLocale() || "").slice(0, 2).toLowerCase();
  return CORE.includes(s) ? s : "en";
}

function chooseLanguage() {
  return new Promise((resolve) => {
    const fallback = osLocale();
    const win = new BrowserWindow({
      width: 460,
      height: 460,
      resizable: false,
      minimizable: false,
      maximizable: false,
      fullscreenable: false,
      title: "Qwibo",
      autoHideMenuBar: true,
      icon: path.join(__dirname, "..", "assets", "icon.ico"),
      webPreferences: {
        preload: path.join(__dirname, "lang-preload.js"),
        contextIsolation: true,
        nodeIntegration: false,
        sandbox: true,
        additionalArguments: [`--oslocale=${fallback}`],
      },
    });

    let chosen = null;
    const onChoose = (_event, code) => {
      chosen = CORE.includes(code) ? code : fallback;
      if (!win.isDestroyed()) win.close();
    };
    ipcMain.once("lang:choose", onChoose);

    win.loadFile(path.join(__dirname, "..", "lang", "index.html"));
    win.on("closed", () => {
      ipcMain.removeListener("lang:choose", onChoose);
      resolve(chosen || fallback);
    });
  });
}

module.exports = { chooseLanguage, osLocale };
