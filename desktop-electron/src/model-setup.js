/**
 * Wizard modelli obbligatorio al primo avvio (subito dopo installazione).
 */

const { BrowserWindow } = require("electron");
const { spawn } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { write: logWrite } = require("./logger");
const {
  pythonExecutable,
  backendDir,
  userDataPaths,
  ensureUserDirs,
  hasAsrModel,
  hasQwenModel,
} = require("./backend-spawn");

const MIN_RAM_GB = 16;

function getRamGb() {
  return os.totalmem() / 1024 ** 3;
}

function needsModelSetup() {
  if (!hasAsrModel()) return true;
  if (getRamGb() >= MIN_RAM_GB && !hasQwenModel()) return true;
  return false;
}

function buildDownloadEnv() {
  const paths = ensureUserDirs();
  const vendorDir = path.join(backendDir(), "vendor");
  const pythonPathParts = [];
  if (fs.existsSync(vendorDir)) pythonPathParts.push(vendorDir);
  if (process.env.PYTHONPATH) pythonPathParts.push(process.env.PYTHONPATH);
  return {
    ...process.env,
    PYTHONPATH: pythonPathParts.join(path.delimiter),
    QWIBO_DATA: paths.data,
    NEMO_CACHE_DIR: paths.models,
    QWIBO_DESKTOP: "1",
    PYTHONUNBUFFERED: "1",
    // Solo stdout in UTF-8 (download_models.py stampa JSON con accenti). Non
    // PYTHONUTF8=1: cambierebbe la decodifica dei sottoprocessi e romperebbe.
    PYTHONIOENCODING: "utf-8",
  };
}

function runModelDownloads(sendProgress) {
  return new Promise((resolve, reject) => {
    const python = pythonExecutable();
    const script = path.join(backendDir(), "download_models.py");
    if (!fs.existsSync(python)) {
      reject(
        new Error(
          `Runtime Python non trovato: ${python}\nReinstalla Qwibo.`
        )
      );
      return;
    }
    if (!fs.existsSync(script)) {
      reject(new Error(`Script download mancante: ${script}`));
      return;
    }

    const proc = spawn(python, [script, "--setup-all"], {
      cwd: backendDir(),
      env: buildDownloadEnv(),
      stdio: ["ignore", "pipe", "pipe"],
      windowsHide: true,
    });

    let stderr = "";
    let settled = false;

    const finish = (ok, err) => {
      if (settled) return;
      settled = true;
      if (ok) resolve(true);
      else reject(err);
    };

    proc.stdout.on("data", (chunk) => {
      for (const line of chunk.toString().split("\n")) {
        const trimmed = line.trim();
        if (!trimmed.startsWith("{")) continue;
        try {
          const data = JSON.parse(trimmed);
          sendProgress(data);
          if (data.event === "complete") finish(true);
          if (data.event === "error") finish(false, new Error(data.message || "Download fallito"));
        } catch {
          /* ignore */
        }
      }
    });

    proc.stderr.on("data", (chunk) => {
      const text = chunk.toString();
      stderr += text;
      logWrite("setup", text.trimEnd());
    });

    proc.on("error", (err) => finish(false, err));
    proc.on("exit", (code) => {
      if (settled) return;
      if (code === 0) {
        finish(true);
        return;
      }
      finish(false, new Error(stderr.trim() || `Download terminato con codice ${code}`));
    });
  });
}

function openSetupWindow() {
  return new BrowserWindow({
    width: 560,
    height: 480,
    resizable: false,
    maximizable: false,
    minimizable: false,
    fullscreenable: false,
    title: "Configurazione Qwibo",
    icon: path.join(__dirname, "..", "assets", "icon.ico"),
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, "setup-preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });
}

async function runModelSetupIfNeeded() {
  if (!needsModelSetup()) {
    return true;
  }

  const win = openSetupWindow();
  await win.loadFile(path.join(__dirname, "..", "setup", "index.html"));

  const sendProgress = (data) => {
    if (!win.isDestroyed()) {
      win.webContents.send("setup-progress", data);
    }
  };

  try {
    await runModelDownloads(sendProgress);
    await new Promise((r) => setTimeout(r, 1200));
    if (!win.isDestroyed()) win.close();
    return true;
  } catch (err) {
    sendProgress({ event: "error", message: String(err.message || err) });
    return false;
  }
}

module.exports = {
  needsModelSetup,
  runModelSetupIfNeeded,
  getRamGb,
};
