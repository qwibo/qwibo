const {
  app,
  BrowserWindow,
  dialog,
  ipcMain,
  Menu,
  Tray,
  shell,
} = require("electron");
const path = require("path");
const fs = require("fs");
require("./load-env").loadEnv();
const { findFreePort } = require("./find-port");
const { install: installLogger, logFilePath, openLogFolder } = require("./logger");
const {
  startBackend,
  stopBackend,
  waitForBackend,
} = require("./backend-spawn");
const { runModelSetupIfNeeded } = require("./model-setup");
const { applyAppMenu } = require("./menu");
const leads = require("./leads");

const CORE_LOCALES = ["it", "en", "fr", "es", "de"];

function readUiLocale() {
  try {
    const p = path.join(app.getPath("userData"), "data", "preferences.json");
    const prefs = JSON.parse(fs.readFileSync(p, "utf-8"));
    const code = String(prefs.ui_locale || "").slice(0, 2).toLowerCase();
    if (CORE_LOCALES.includes(code)) return code;
  } catch {
    /* primo avvio: preferences.json non ancora creato */
  }
  const sys = String(app.getLocale() || "").slice(0, 2).toLowerCase();
  return CORE_LOCALES.includes(sys) ? sys : "en";
}

function refreshAppMenu() {
  applyAppMenu({
    getWindow: () => mainWindow,
    getPort: () => backendPort,
    locale: readUiLocale(),
    openLogFolder,
    appVersion: APP_VERSION,
  });
}

function closeLeadWindow() {
  if (leadWindow && !leadWindow.isDestroyed()) leadWindow.close();
  leadWindow = null;
}

/** Modal opt-in email al primo avvio — solo se il token è configurato. */
function maybeShowLeadModal() {
  if (!leads.leadsEnabled() || leads.hasPrompted() || !mainWindow) return;
  leadWindow = new BrowserWindow({
    width: 460,
    height: 430,
    resizable: false,
    minimizable: false,
    maximizable: false,
    fullscreenable: false,
    parent: mainWindow,
    modal: true,
    title: "Qwibo",
    autoHideMenuBar: true,
    icon: path.join(__dirname, "..", "assets", "icon.ico"),
    webPreferences: {
      preload: path.join(__dirname, "lead-preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      additionalArguments: [`--locale=${readUiLocale()}`],
    },
  });
  leadWindow.loadFile(path.join(__dirname, "..", "lead", "index.html"));
  leadWindow.on("closed", () => {
    leadWindow = null;
  });
}

ipcMain.handle("leads:submit", async (_event, payload) => {
  const email = payload && payload.email;
  const consent = payload && payload.consent;
  const result = await leads.submitLead(email, consent, readUiLocale());
  closeLeadWindow();
  return result;
});

ipcMain.on("leads:skip", () => {
  leads.markPrompted();
  closeLeadWindow();
});

installLogger();

const APP_VERSION = "0.1.0";
let mainWindow = null;
let tray = null;
let backendPort = null;
let leadWindow = null;
let isShuttingDown = false;

const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
  app.on("second-instance", () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

function logHint() {
  return `Log: ${logFilePath()}`;
}

async function showError(title, message, detail) {
  await dialog.showMessageBox({
    type: "error",
    title,
    message,
    detail: `${detail}\n\n${logHint()}`,
  });
}

async function createWindow() {
  backendPort = await findFreePort(8765);

  try {
    startBackend(backendPort);
    await waitForBackend(backendPort);
  } catch (err) {
    console.error("Errore avvio backend:", err);
    await showError(
      "Qwibo — errore avvio",
      String(err.message || err),
      "Reinstalla l'applicazione. Se il problema persiste, invia il file di log al supporto."
    );
    app.quit();
    return;
  }

  mainWindow = new BrowserWindow({
    width: 1280,
    height: 860,
    minWidth: 960,
    minHeight: 640,
    title: `Qwibo ${APP_VERSION}`,
    icon: path.join(__dirname, "..", "assets", "icon.ico"),
    show: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  mainWindow.once("ready-to-show", () => mainWindow.show());
  mainWindow.loadURL(`http://127.0.0.1:${backendPort}/`);

  // Il menu segue la lingua UI: dopo che l'utente la cambia in Impostazioni
  // (redirect di salvataggio) ricostruiamo le label nella nuova lingua.
  mainWindow.webContents.on("did-navigate", () => refreshAppMenu());

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: "deny" };
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

function buildTrayMenu() {
  return Menu.buildFromTemplate([
    {
      label: "Apri Qwibo",
      click: () => {
        if (mainWindow) mainWindow.show();
        else createWindow();
      },
    },
    { type: "separator" },
    {
      label: "Apri cartella log",
      click: () => openLogFolder(),
    },
    { type: "separator" },
    {
      label: "Esci",
      click: () => app.quit(),
    },
  ]);
}

app.whenReady().then(async () => {
  tray = new Tray(path.join(__dirname, "..", "assets", "tray.png"));
  tray.setToolTip("Qwibo");
  tray.setContextMenu(buildTrayMenu());
  tray.on("double-click", () => {
    if (mainWindow) mainWindow.show();
  });

  const setupOk = await runModelSetupIfNeeded();
  if (!setupOk) {
    await showError(
      "Configurazione incompleta",
      "Download modelli non completato.",
      "Controlla la connessione internet e riavvia Qwibo."
    );
    app.quit();
    return;
  }

  await createWindow();
  refreshAppMenu();

  // Lead-gen (solo se token configurato): ritenta la coda offline e mostra
  // il modal opt-in al primo avvio. Mai bloccante per l'uso dell'app.
  leads.flushPending().catch(() => {});
  maybeShowLeadModal();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("before-quit", async (event) => {
  if (isShuttingDown) return;
  event.preventDefault();
  isShuttingDown = true;
  await stopBackend();
  backendPort = null;
  app.exit(0);
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
