# Problemi comuni

## Setup e avvio

### Download modelli fallito o bloccato

**Prova:** log dalla tray, ≥ 8 GB disco libero, riavvia Qwibo, controlla antivirus.

---

### "Avvio troppo lento"

Backend non risponde in ~3 minuti.

**Prova:** esci da tray, attendi, riapri; chiudi `python.exe` zombie; leggi log; reinstalla se necessario.

---

### Finestra bianca

Backend crashato dopo apertura. Log + riavvio.

---

## Trascrizione

### Job `running` a lungo

Attendi (primo job + model load). Controlla progresso. Riavvia se bloccato.

---

### Job `failed`

File corrotto, codec non supportato, modello ASR mancante. Prova clip corta `.wav`/`.mp3`.

---

### Qualità italiana scarsa

Rumore, sovrapposizioni, microfono lontano. Prova campione in ambiente quieto.

---

## Riassunto

### Trascrizione OK, riassunto no

Chiave API, rete, Qwen assente o RAM insufficiente. Trascrizione sempre in `trascrizione.txt`.

---

## Coda

### Stesso file non si accoda

Job attivo con stesso nome. Attendi o **Accoda comunque**.

---

## Performance

Mini PC lenti: ~2× tempo reale o peggio. Accoda file lunghi di notte.

---

## Ancora bloccato?

Tray → **Apri cartella log** → issue su [GitHub](https://github.com/qwibo/qwibo/issues) (senza chiavi API).

SmartScreen: [SmartScreen](smartscreen.md).
