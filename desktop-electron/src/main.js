const {
  app,
  BrowserWindow,
  dialog,
  Menu,
  Tray,
  shell,
} = require("electron");
const path = require("path");
const { findFreePort } = require("./find-port");
const { install: installLogger, logFilePath, openLogFolder } = require("./logger");
const {
  startBackend,
  stopBackend,
  waitForBackend,
} = require("./backend-spawn");
const { runModelSetupIfNeeded } = require("./model-setup");

installLogger();

const APP_VERSION = "0.1.0";
let mainWindow = null;
let tray = null;
let backendPort = null;
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
