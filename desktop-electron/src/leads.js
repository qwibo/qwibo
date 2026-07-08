/**
 * Lead generation — raccolta email opt-in al primo avvio (GDPR, con consenso).
 *
 * Attiva SOLO se il token `LEADS_APP_TOKEN` è presente nell'ambiente (build/.env);
 * senza token la feature è disattivata e il modal non viene mostrato.
 * Il valore del token NON è mai committato: vedi desktop-electron/.env (gitignore).
 * Contratto server: PLAN_LEAD_GENERATION.md §4.
 */

const { app } = require("electron");
const fs = require("fs");
const os = require("os");
const path = require("path");
const https = require("https");
const http = require("http");
const crypto = require("crypto");
const { URL } = require("url");
const { write: logWrite } = require("./logger");

const DEFAULT_API_URL = "https://qwiboleads.antoniotrento.net/v1/leads";
const CONSENT_TEXT_VER = "2026-07";

function apiUrl() {
  return process.env.LEADS_API_URL || DEFAULT_API_URL;
}
function appToken() {
  return process.env.LEADS_APP_TOKEN || "";
}
function leadsEnabled() {
  return appToken().length > 0;
}

function statePath() {
  return path.join(app.getPath("userData"), "leads-state.json");
}
function pendingPath() {
  return path.join(app.getPath("userData"), "leads_pending.json");
}

function readJson(file, fallback) {
  try {
    return JSON.parse(fs.readFileSync(file, "utf-8"));
  } catch {
    return fallback;
  }
}
function writeJson(file, value) {
  try {
    fs.writeFileSync(file, JSON.stringify(value, null, 2), "utf-8");
  } catch (err) {
    logWrite("leads", `scrittura fallita ${file}: ${err.message}`);
  }
}

function readState() {
  const s = readJson(statePath(), {});
  return s && typeof s === "object" ? s : {};
}
function getInstallId() {
  const s = readState();
  if (s.install_id) return s.install_id;
  s.install_id = crypto.randomUUID();
  writeJson(statePath(), s);
  return s.install_id;
}
function hasPrompted() {
  return readState().leads_prompt_completed === true;
}
function markPrompted() {
  const s = readState();
  s.leads_prompt_completed = true;
  writeJson(statePath(), s);
}

function osString() {
  return `${process.platform}-${os.release()}`;
}

function buildPayload(email, consent, locale) {
  return {
    email: String(email || "").trim(),
    consent: consent === true,
    install_id: getInstallId(),
    app_version: app.getVersion(),
    os: osString(),
    locale: locale || app.getLocale() || "en",
    source: "first-run-modal",
    consent_text_ver: CONSENT_TEXT_VER,
  };
}

/** POST → { ok, retry, code }. retry=true per errori transitori (rete/429/5xx). */
function post(payload) {
  return new Promise((resolve) => {
    let u;
    try {
      u = new URL(apiUrl());
    } catch {
      resolve({ ok: false, retry: false });
      return;
    }
    const data = Buffer.from(JSON.stringify(payload), "utf-8");
    const lib = u.protocol === "http:" ? http : https;
    const req = lib.request(
      {
        method: "POST",
        hostname: u.hostname,
        port: u.port || (u.protocol === "http:" ? 80 : 443),
        path: u.pathname + u.search,
        headers: {
          "Content-Type": "application/json",
          "Content-Length": data.length,
          "X-App-Token": appToken(),
        },
        timeout: 10000,
      },
      (res) => {
        res.resume();
        const code = res.statusCode || 0;
        if (code === 200 || code === 201) resolve({ ok: true, code });
        else if (code === 429 || code >= 500) resolve({ ok: false, retry: true, code });
        else resolve({ ok: false, retry: false, code }); // 401/422: non ritentare all'infinito
      }
    );
    req.on("error", () => resolve({ ok: false, retry: true }));
    req.on("timeout", () => {
      req.destroy();
      resolve({ ok: false, retry: true });
    });
    req.write(data);
    req.end();
  });
}

function queuePending(payload) {
  const arr = readJson(pendingPath(), []);
  const list = Array.isArray(arr) ? arr : [];
  list.push(payload);
  writeJson(pendingPath(), list);
}

/** Invia un lead. Mai bloccante: in caso di errore transitorio, coda offline. */
async function submitLead(email, consent, locale) {
  markPrompted();
  if (!leadsEnabled()) return { ok: false, retry: false, disabled: true };
  const payload = buildPayload(email, consent, locale);
  const r = await post(payload);
  if (!r.ok && r.retry) {
    queuePending(payload);
    logWrite("leads", "lead in coda: invio fallito, ritento al prossimo avvio");
  }
  return r;
}

/** Ritenta i lead in coda (chiamare all'avvio). Mai bloccante. */
async function flushPending() {
  if (!leadsEnabled()) return;
  const arr = readJson(pendingPath(), []);
  if (!Array.isArray(arr) || arr.length === 0) return;
  const remaining = [];
  for (const payload of arr) {
    // eslint-disable-next-line no-await-in-loop
    const r = await post(payload);
    if (!r.ok && r.retry) remaining.push(payload);
  }
  try {
    if (remaining.length) writeJson(pendingPath(), remaining);
    else fs.unlinkSync(pendingPath());
  } catch {
    /* file già assente */
  }
}

module.exports = {
  leadsEnabled,
  hasPrompted,
  markPrompted,
  submitLead,
  flushPending,
  getInstallId,
  CONSENT_TEXT_VER,
};
