/**
 * Menu applicazione nativo, tradotto nelle 5 lingue core.
 * Le voci navigano il backend embedded (loadURL) o eseguono azioni desktop.
 */

const { Menu, shell, dialog, app } = require("electron");

const DOCS_URL = "https://qwibo.github.io/docs/";

const STRINGS = {
  it: {
    file: "File", newJob: "Nuova trascrizione", quit: "Esci",
    edit: "Modifica", prefs: "Preferenze",
    view: "Visualizza", reload: "Ricarica", theme: "Cambia tema (chiaro/scuro)",
    jobs: "Lavori", queue: "Coda e storico",
    help: "Aiuto", guide: "Guida utente", logs: "Apri cartella log", about: "Informazioni su Qwibo",
    aboutBody: "Trascrizione multilingua in locale.",
  },
  en: {
    file: "File", newJob: "New transcription", quit: "Quit",
    edit: "Edit", prefs: "Preferences",
    view: "View", reload: "Reload", theme: "Toggle theme (light/dark)",
    jobs: "Jobs", queue: "Queue & history",
    help: "Help", guide: "User guide", logs: "Open log folder", about: "About Qwibo",
    aboutBody: "Local multilingual transcription.",
  },
  fr: {
    file: "Fichier", newJob: "Nouvelle transcription", quit: "Quitter",
    edit: "Édition", prefs: "Préférences",
    view: "Affichage", reload: "Recharger", theme: "Changer de thème (clair/sombre)",
    jobs: "Tâches", queue: "File et historique",
    help: "Aide", guide: "Guide utilisateur", logs: "Ouvrir le dossier des logs", about: "À propos de Qwibo",
    aboutBody: "Transcription multilingue en local.",
  },
  es: {
    file: "Archivo", newJob: "Nueva transcripción", quit: "Salir",
    edit: "Edición", prefs: "Preferencias",
    view: "Ver", reload: "Recargar", theme: "Cambiar tema (claro/oscuro)",
    jobs: "Trabajos", queue: "Cola e historial",
    help: "Ayuda", guide: "Guía de usuario", logs: "Abrir carpeta de registros", about: "Acerca de Qwibo",
    aboutBody: "Transcripción multilingüe en local.",
  },
  de: {
    file: "Datei", newJob: "Neue Transkription", quit: "Beenden",
    edit: "Bearbeiten", prefs: "Einstellungen",
    view: "Ansicht", reload: "Neu laden", theme: "Design wechseln (hell/dunkel)",
    jobs: "Aufträge", queue: "Warteschlange & Verlauf",
    help: "Hilfe", guide: "Benutzerhandbuch", logs: "Log-Ordner öffnen", about: "Über Qwibo",
    aboutBody: "Mehrsprachige Transkription lokal.",
  },
};

const THEME_TOGGLE_JS =
  "(function(){var c=document.documentElement.getAttribute('data-theme')==='light'?'light':'dark';" +
  "var n=c==='light'?'dark':'light';document.documentElement.setAttribute('data-theme',n);" +
  "try{localStorage.setItem('qwibo-theme',n)}catch(e){}})()";

/**
 * @param {object} opts
 * @param {() => import('electron').BrowserWindow|null} opts.getWindow
 * @param {() => number|null} opts.getPort
 * @param {string} opts.locale        codice lingua (it/en/fr/es/de)
 * @param {() => void} opts.openLogFolder
 * @param {string} opts.appVersion
 */
function buildAppMenu(opts) {
  const t = STRINGS[opts.locale] || STRINGS.en;

  const go = (route) => {
    const win = opts.getWindow();
    const port = opts.getPort();
    if (win && port) win.loadURL(`http://127.0.0.1:${port}${route}`);
  };

  const template = [
    {
      label: t.file,
      submenu: [
        { label: t.newJob, accelerator: "CmdOrCtrl+N", click: () => go("/") },
        { type: "separator" },
        { label: t.quit, accelerator: "CmdOrCtrl+Q", click: () => app.quit() },
      ],
    },
    {
      label: t.edit,
      submenu: [
        { label: t.prefs, accelerator: "CmdOrCtrl+,", click: () => go("/settings") },
        { type: "separator" },
        { role: "cut" },
        { role: "copy" },
        { role: "paste" },
        { role: "selectAll" },
      ],
    },
    {
      label: t.view,
      submenu: [
        {
          label: t.theme,
          accelerator: "CmdOrCtrl+Shift+L",
          click: () => {
            const win = opts.getWindow();
            if (win) win.webContents.executeJavaScript(THEME_TOGGLE_JS).catch(() => {});
          },
        },
        { label: t.reload, accelerator: "CmdOrCtrl+R", click: () => { const w = opts.getWindow(); if (w) w.webContents.reload(); } },
        { type: "separator" },
        { role: "resetZoom" },
        { role: "zoomIn" },
        { role: "zoomOut" },
        { type: "separator" },
        { role: "togglefullscreen" },
      ],
    },
    {
      label: t.jobs,
      submenu: [
        { label: t.queue, click: () => go("/jobs") },
      ],
    },
    {
      label: t.help,
      submenu: [
        { label: t.guide, click: () => shell.openExternal(DOCS_URL) },
        { label: t.logs, click: () => opts.openLogFolder() },
        { type: "separator" },
        {
          label: t.about,
          click: () =>
            dialog.showMessageBox({
              type: "info",
              title: t.about,
              message: `Qwibo ${opts.appVersion}`,
              detail: t.aboutBody,
            }),
        },
      ],
    },
  ];

  return Menu.buildFromTemplate(template);
}

function applyAppMenu(opts) {
  Menu.setApplicationMenu(buildAppMenu(opts));
}

module.exports = { buildAppMenu, applyAppMenu, MENU_STRINGS: STRINGS };
