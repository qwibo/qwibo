# Tracker — GitHub Issues

**GitHub Issues** su [qwibo/qwibo](https://github.com/qwibo/qwibo/issues) è la **fonte di verità** per bug, task di sprint ed evolutive in corso.

I file in `bug-fix/` e `microevolutive/` restano **riferimento e archivio** (piani dettagliati, post-mortem, storico). Non aprire nuovi file markdown per tracciare lavoro attivo.

---

## Token GitHub

Lo script legge il token **automaticamente** (l'agente Cursor non deve chiedere comandi manuali):

| Priorità | Sorgente |
|----------|----------|
| 1 | Variabile `GITHUB_TOKEN` nella sessione corrente |
| 2 | **Variabili utente Windows** (se l'hai messa in *Variabili d'ambiente* → funziona anche nel terminale Cursor) |
| 3 | File `.env` nella root: `GITHUB_TOKEN=github_pat_...` |
| 4 | File `data/.secrets/github_token` — una riga, gitignored |

**Setup consigliato (già fatto se `python -c "..."` stampa ok):** token in Variabili utente Windows.

**Alternativa file** (se il terminale agent non legge il registry):

```cmd
mkdir data\.secrets 2>nul
copy tracker\github_token.example data\.secrets\github_token
notepad data\.secrets\github_token
```

Incolla il token su una riga, salva. **Mai** committare quel file.

---

## Uso con Cursor chat

Quando segnali un bug o chiedi un task, l'agente può creare o aggiornare issue GitHub invece di file locali:

- *«Apri issue per il bug del menu Electron»*
- *«Crea task GitHub per PLAN_APP_I18N fase wizard»*
- *«Commenta issue #42 con il fix applicato»*

L'agente esegue `python scripts/github_issue.py ...` (vedi regola `.cursor/rules/github-issues.mdc`).

---

## Comandi

### Label (prima import o setup repo)

Anteprima label definite in `tracker/labels.yml`:

```cmd
python scripts/github_issue.py labels
```

Crea/aggiorna label su GitHub:

```cmd
python scripts/github_issue.py labels --apply
```

### Import issue da manifest

Anteprima (nessuna modifica su GitHub):

```cmd
python scripts/github_issue.py import --dry-run
```

Crea le issue (salta duplicati se trova lo stesso **Legacy ID** nel body):

```cmd
python scripts/github_issue.py import --apply
```

Manifest: `tracker/import-manifest.json` (bug aperti da `TRACCIAMENTO-BUG.md` + task sprint attivi).

### Creare issue manualmente

```cmd
python scripts/github_issue.py create "Titolo breve" --body "Descrizione markdown" --labels bug,priority-high,area-ui
```

### Elencare issue

```cmd
python scripts/github_issue.py list
python scripts/github_issue.py list --state closed --limit 50
```

### Commento e chiusura

```cmd
python scripts/github_issue.py comment 12 --body "Fix in PR #99"
python scripts/github_issue.py close 12
```

---

## Struttura cartella

| File | Ruolo |
|------|--------|
| `labels.yml` | Definizione label GitHub |
| `import-manifest.json` | Batch import iniziale (legacy ID nel body) |
| `README.md` | Questa guida |

---

## Commit e PR

Nei commit e nelle PR che risolvono lavoro tracciato, referenzia l'issue:

```
fix(summary): lower map-reduce threshold for local Qwen

Fixes #NN
```

---

## Cartelle correlate

| Path | Ruolo |
|------|--------|
| `bug-fix/` | Archivio bug risolti, post-mortem, `TRACCIAMENTO-BUG.md` storico |
| `microevolutive/` | Piani sprint (`active/`, `done/`) — dettaglio implementativo |
| `evolutive/` | Scenari utente e idee non in sprint |
