/**
 * Carica desktop-electron/.env in process.env (solo dev; il file è gitignored).
 * Non sovrascrive variabili già presenti nell'ambiente. Nessuna dipendenza esterna.
 * Il token lead-gen (LEADS_APP_TOKEN) va QUI, mai committato.
 */

const fs = require("fs");
const path = require("path");

function candidateEnvPaths() {
  const list = [
    // dev: desktop-electron/.env ; packaged: dentro app.asar (build.files include ".env")
    path.join(__dirname, "..", ".env"),
  ];
  // packaged (fallback se .env viene messo tra le extraResources invece che in asar)
  if (process.resourcesPath) {
    list.push(path.join(process.resourcesPath, ".env"));
    list.push(path.join(process.resourcesPath, "app.asar", ".env"));
  }
  return list;
}

function loadEnv() {
  let text = null;
  for (const file of candidateEnvPaths()) {
    try {
      text = fs.readFileSync(file, "utf-8");
      break;
    } catch {
      /* prova il prossimo percorso */
    }
  }
  if (text === null) return; // nessun .env: feature lead-gen disattivata
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const eq = line.indexOf("=");
    if (eq === -1) continue;
    const key = line.slice(0, eq).trim();
    let val = line.slice(eq + 1).trim();
    if (
      (val.startsWith('"') && val.endsWith('"')) ||
      (val.startsWith("'") && val.endsWith("'"))
    ) {
      val = val.slice(1, -1);
    }
    if (key && !(key in process.env)) process.env[key] = val;
  }
}

module.exports = { loadEnv };
