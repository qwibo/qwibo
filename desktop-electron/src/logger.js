const fs = require("fs");
const path = require("path");
const os = require("os");
const { shell } = require("electron");

function logDir() {
  const base = process.env.APPDATA || os.homedir();
  return path.join(base, "qwibo-desktop", "logs");
}

function logFilePath() {
  const dir = logDir();
  fs.mkdirSync(dir, { recursive: true });
  const date = new Date().toISOString().slice(0, 10);
  return path.join(dir, `qwibo-${date}.log`);
}

function write(level, message) {
  const line = `[${new Date().toISOString()}] [${level}] ${message}\n`;
  try {
    fs.appendFileSync(logFilePath(), line, "utf8");
  } catch {
    /* ignore */
  }
}

function formatArgs(args) {
  return args
    .map((a) => {
      if (a instanceof Error) return a.stack || a.message;
      if (typeof a === "object") {
        try {
          return JSON.stringify(a);
        } catch {
          return String(a);
        }
      }
      return String(a);
    })
    .join(" ");
}

function install() {
  for (const level of ["log", "warn", "error"]) {
    const original = console[level].bind(console);
    console[level] = (...args) => {
      write(level, formatArgs(args));
      original(...args);
    };
  }

  process.on("uncaughtException", (err) => {
    write("fatal", err.stack || err.message);
  });
  process.on("unhandledRejection", (reason) => {
    write("fatal", formatArgs([reason]));
  });
}

function openLogFolder() {
  const dir = logDir();
  fs.mkdirSync(dir, { recursive: true });
  return shell.openPath(dir);
}

module.exports = { install, write, logDir, logFilePath, openLogFolder };
