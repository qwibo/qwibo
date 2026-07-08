/**
 * Carica desktop-electron/.env in process.env (solo dev; il file è gitignored).
 * Non sovrascrive variabili già presenti nell'ambiente. Nessuna dipendenza esterna.
 * Il token lead-gen (LEADS_APP_TOKEN) va QUI, mai committato.
 */

const fs = require("fs");
const path = require("path");

function loadEnv() {
  const file = path.join(__dirname, "..", ".env");
  let text;
  try {
    text = fs.readFileSync(file, "utf-8");
  } catch {
    return; // nessun .env: normale in produzione
  }
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
