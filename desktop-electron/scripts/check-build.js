const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const runtime = path.join(root, "build", "runtime-venv");

// python-build-standalone mette python.exe nella root (relocabile).
const pythonRoot = path.join(runtime, "python.exe");
const pythonScripts = path.join(runtime, "Scripts", "python.exe");

if (!fs.existsSync(pythonRoot) && !fs.existsSync(pythonScripts)) {
  console.error("\nERRORE: build incompleta.\n");
  console.error("Esegui prima: build_installer.bat\n");
  console.error("Mancante:", pythonRoot, "\n");
  process.exit(1);
}

// Un pyvenv.cfg significa che runtime-venv è un venv con path assoluti della
// macchina di build: non relocabile, si rompe sul PC dell'utente finale.
if (fs.existsSync(path.join(runtime, "pyvenv.cfg"))) {
  console.error("\nERRORE: build/runtime-venv è un venv non relocabile (pyvenv.cfg presente).\n");
  console.error("Il python.exe di un venv referenzia l'interprete base per path assoluto");
  console.error("e non funziona su altre macchine.\n");
  console.error("Elimina build/runtime-venv e rilancia: build_installer.bat  (build completa)\n");
  process.exit(1);
}

const required = [
  path.join(root, "build", "ffmpeg", "bin", "ffmpeg.exe"),
  path.join(root, "backend", "vendor", "qwibo", "ui", "server.py"),
];

for (const p of required) {
  if (!fs.existsSync(p)) {
    console.error("\nERRORE: build incompleta.\n");
    console.error("Esegui prima: build_installer.bat\n");
    console.error("Mancante:", p, "\n");
    process.exit(1);
  }
}

console.log("Build runtime OK — avvio electron-builder…");
