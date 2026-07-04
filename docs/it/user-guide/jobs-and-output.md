# Coda e output

## Due livelli dati

| Livello | Percorso | Ruolo |
|---------|----------|-------|
| **Registro** | `data\output\jobs\queue.db` | Elenco job, stati |
| **File** | `data\output\jobs\{id}\` | Audio, trascrizione, SRT |

Base: `%APPDATA%\qwibo-desktop\data\`

---

## Stati job

| Stato | Significato |
|-------|-------------|
| `queued` | In attesa |
| `running` | In elaborazione |
| `completed` | OK |
| `failed` | Errore |
| `cancelled` | Annullato in coda |

---

## ID e cartelle

Formato: `YYYYMMDD_HHMMSS_nome-file`

Collisione nello stesso secondo: suffisso `_2`, `_3`, …

### Contenuto cartella

```text
20260704_183045_intervista/
├── source.mp3
├── job.json
├── trascrizione.txt
├── sottotitoli.srt
└── riassunto.txt
```

---

## Coda FIFO

Un job alla volta. Nessun overwrite dei job passati.

---

## Duplicati

| Situazione | Comportamento |
|------------|---------------|
| Stesso nome in coda/running | Saltato (default) |
| Stesso nome già completato | **Nuovo** job, nuova cartella |
| "Accoda comunque" | Forza duplicato |

---

## Azioni UI

Annulla (solo `queued`), riprova, rielabora, + riassunto, elimina, sincronizza disco.

---

## Pulizia

Preferisci **Elimina** in UI. Per azzerare tutto: esci da tray e cancella `data\output\jobs\`. I modelli in `models\` restano.
