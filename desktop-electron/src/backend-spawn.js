/**
 * Avvio backend Python embedded — nessun Python di sistema per l'utente finale.
 */

const { app } = require("electron");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");
const http = require("http");
const { write: logWrite } = require("./logger");

function resourcesRoot() {
  return app.isPackaged ? process.resourcesPath : path.join(__dirname, "..", "build");
}

function backendDir() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, "backend");
  }
  return path.join(__dirname, "..", "backend");
}

function pythonExecutable() {
  const root = resourcesRoot();
  const candidates = [
    path.join(root, "runtime-venv", "python.exe"),
    path.join(root, "runtime-venv", "Scripts", "python.exe"),
  ];
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }
  if (!app.isPackaged) {
    const devVenv = path.join(backendDir(), ".venv", "Scripts", "python.exe");
    if (fs.existsSync(devVenv)) return devVenv;
  }
  return candidates[0];
}

function ffmpegBinDir() {
  const dir = path.join(resourcesRoot(), "ffmpeg", "bin");
  return fs.existsSync(path.join(dir, "ffmpeg.exe")) ? dir : null;
}

function entrypointPath() {
  return path.join(backendDir(), "entrypoint.py");
}

function userDataPaths() {
  const root = app.getPath("userData");
  return {
    data: path.join(root, "data"),
    models: path.join(root, "models"),
    logs: path.join(root, "logs"),
    // Cache scrivibile per numba/librosa e matplotlib: se puntassero alla loro
    // dir in "C:\Program Files\..." (sola lettura) tempfile andrebbe in loop e
    // il caricamento del modello si pianterebbe (bug os.access W_OK su Windows).
    cache: path.join(root, "cache"),
  };
}

function ensureUserDirs() {
  const paths = userDataPaths();
  for (const p of Object.values(paths)) {
    fs.mkdirSync(p, { recursive: true });
  }
  return paths;
}

function hasAsrModel() {
  const { models } = userDataPaths();
  try {
    for (const name of fs.readdirSync(models)) {
      if (!name.endsWith(".nemo")) continue;
      const stat = fs.statSync(path.join(models, name));
      if (stat.size > 2_200_000_000) return true;
    }
  } catch {
    /* prima esecuzione */
  }
  return false;
}

function hasQwenModel() {
  const { models } = userDataPaths();
  const gguf = path.join(
    models,
    "qwen2.5-3b-instruct",
    "qwen2.5-3b-instruct-q4_k_m.gguf"
  );
  try {
    return fs.existsSync(gguf) && fs.statSync(gguf).size > 1_500_000_000;
  } catch {
    return false;
  }
}

let backendProcess = null;

function startBackend(port) {
  const python = pythonExecutable();
  const entry = entrypointPath();
  if (!fs.existsSync(python)) {
    throw new Error(
      "Runtime Python non trovato nell'installazione.\n" +
        "Reinstalla Qwibo o contatta il supporto."
    );
  }
  if (!fs.existsSync(entry)) {
    throw new Error(`Backend mancante: ${entry}`);
  }

  const paths = ensureUserDirs();
  const ffmpegDir = ffmpegBinDir();
  const pathEnv = ffmpegDir
    ? `${ffmpegDir}${path.delimiter}${process.env.PATH || ""}`
    : process.env.PATH || "";

  // launch_ui() avvia uvicorn/worker come NUOVI processi che non ereditano
  // il sys.path di entrypoint.py: senza PYTHONPATH importerebbero qwibo
  // solo da site-packages (che può essere un install editable non relocabile).
  // Puntando al vendor bundlato l'import funziona su qualsiasi macchina.
  const vendorDir = path.join(backendDir(), "vendor");
  const pythonPathParts = [];
  if (fs.existsSync(vendorDir)) pythonPathParts.push(vendorDir);
  if (process.env.PYTHONPATH) pythonPathParts.push(process.env.PYTHONPATH);

  // numba (via librosa/NeMo) e matplotlib scrivono cache accanto ai loro file;
  // in "C:\Program Files\..." è sola lettura → redirigiamo su cartelle
  // scrivibili, altrimenti tempfile va in loop e il caricamento modello si pianta.
  const numbaCache = path.join(paths.cache, "numba");
  const mplCache = path.join(paths.cache, "matplotlib");
  fs.mkdirSync(numbaCache, { recursive: true });
  fs.mkdirSync(mplCache, { recursive: true });

  const env = {
    ...process.env,
    PATH: pathEnv,
    PYTHONPATH: pythonPathParts.join(path.delimiter),
    QWIBO_PORT: String(port),
    QWIBO_UI_HOST: "127.0.0.1",
    QWIBO_DATA: paths.data,
    NEMO_CACHE_DIR: paths.models,
    NUMBA_CACHE_DIR: numbaCache,
    MPLCONFIGDIR: mplCache,
    QWIBO_DESKTOP: "1",
    PYTHONUNBUFFERED: "1",
    // Forza UTF-8 solo su stdin/stdout/stderr: senza, Windows usa cp1252 e
    // crasha stampando caratteri non-ASCII (es. "→"). NON usiamo PYTHONUTF8=1
    // perché quello cambierebbe anche la decodifica dell'output dei sottoprocessi
    // (tasklist, ffmpeg/ffprobe in codepage OEM) → UnicodeDecodeError che manda
    // in crash l'avvio del worker.
    PYTHONIOENCODING: "utf-8",
  };

  backendProcess = spawn(python, [entry], {
    cwd: backendDir(),
    env,
    stdio: ["ignore", "pipe", "pipe"],
    windowsHide: true,
  });

  backendProcess.stdout.on("data", (chunk) => {
    const text = chunk.toString();
    logWrite("backend", text.trimEnd());
    process.stdout.write(`[backend] ${chunk}`);
  });
  backendProcess.stderr.on("data", (chunk) => {
    const text = chunk.toString();
    logWrite("backend", text.trimEnd());
    process.stderr.write(`[backend] ${chunk}`);
  });

  backendProcess.on("exit", (code, signal) => {
    console.log(`Backend terminato (code=${code}, signal=${signal})`);
    backendProcess = null;
  });

  return backendProcess;
}

function stopBackend() {
  if (!backendProcess || backendProcess.killed) {
    backendProcess = null;
    return Promise.resolve();
  }

  const proc = backendProcess;
  const pid = proc.pid;

  return new Promise((resolve) => {
    const done = () => {
      backendProcess = null;
      resolve();
    };

    proc.once("exit", done);

    if (process.platform === "win32" && pid) {
      spawn("taskkill", ["/PID", String(pid), "/T", "/F"], { windowsHide: true }).on(
        "close",
        () => setTimeout(done, 300)
      );
    } else {
      proc.kill("SIGTERM");
      setTimeout(() => {
        if (!proc.killed) proc.kill("SIGKILL");
      }, 5000);
    }
  });
}

function waitForBackend(port, timeoutMs = 180000) {
  const url = `http://127.0.0.1:${port}/partials/queue`;
  const started = Date.now();

  return new Promise((resolve, reject) => {
    const tick = () => {
      if (Date.now() - started > timeoutMs) {
        reject(new Error("Avvio troppo lento. Riavvia Qwibo."));
        return;
      }

      const req = http.get(url, (res) => {
        res.resume();
        if (res.statusCode >= 200 && res.statusCode < 500) {
          resolve();
        } else {
          setTimeout(tick, 300);
        }
      });
      req.on("error", () => setTimeout(tick, 300));
      req.setTimeout(3000, () => {
        req.destroy();
        setTimeout(tick, 300);
      });
    };
    tick();
  });
}

module.exports = {
  startBackend,
  stopBackend,
  waitForBackend,
  userDataPaths,
  ensureUserDirs,
  hasAsrModel,
  hasQwenModel,
  pythonExecutable,
  backendDir,
};
