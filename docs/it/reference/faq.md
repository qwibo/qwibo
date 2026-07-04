# FAQ

## Generale

### Qwibo invia l'audio su internet?

**No** per la trascrizione. I **riassunti cloud** inviano solo testo al provider scelto.

### Lingue supportate?

Parakeet ottimizzato per **italiano**; altre lingue con qualità variabile.

### Serve Python o Docker?

**No** per l'app desktop. Docker è [qwibo-docker](https://github.com/qwibo/qwibo-docker).

### Mac o Linux desktop?

Non in alpha. Windows prima; Mac in roadmap.

---

## Modelli

### Spazio disco?

Parakeet ~2,5 GB + Qwen ~2 GB + dati job. Pianifica **8–12 GB** liberi.

### Riscaricare dopo aggiornamento?

Di solito **no** — modelli in `%APPDATA%\qwibo-desktop\models\`.

---

## Coda

### Perché un file alla volta?

Coda **FIFO** per limitare RAM.

### Stesso file due volte?

Se il primo job è **completed** → **nuova** cartella con nuovo timestamp.

### Chiudo la finestra?

Il worker continua finché non **Esci** dalla tray.

---

## Riassunto

| Modalità | Privacy | Requisiti |
|----------|---------|-----------|
| Cloud | Testo al provider | API key + rete |
| Qwen locale | Offline | ≥ 16 GB RAM |

---

## Documentazione

### Come pubblico le docs?

Dal repo **qwibo**:

```cmd
python scripts\publish_docs.py
```

Build MkDocs → copia in `../qwibo.github.io/docs/`, commit opzionale. **Nessuna GitHub Action.** Push su `qwibo.github.io`.

---

## Licenza

Uso personale gratuito. Uso commerciale: [licenza commerciale](commercial-license.md).
