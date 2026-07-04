# Primo avvio

La prima volta che apri Qwibo dopo l'installazione, un **wizard** scarica i modelli vocali. Succede **una volta** — non durante la prima trascrizione.

## Wizard setup

1. Qwibo controlla `%APPDATA%\qwibo-desktop\models\`.
2. Se manca Parakeet, lo scarica (~2,5 GB).
3. Con **≥ 16 GB RAM**, scarica anche Qwen per riassunto locale (~2 GB).
4. Si apre la finestra principale.

!!! tip "Pazienza"
    Il tempo dipende dalla connessione. Se sembra fermo, controlla i log dalla tray (**Apri cartella log**).

## Finestra principale

Dopo il setup:

1. **Home** — upload, coda attiva, job recenti.
2. **Coda e storico** — elenco completo.
3. **Impostazioni riassunto** — API key e motori.
4. **Licenza** — termini e link documentazione.

## Prima trascrizione (test consigliato)

1. File da **10–20 minuti** che conosci bene.
2. Opzionale: **Genera riassunto** + motore.
3. **Accoda trascrizione**.
4. Pagina dettaglio job con progresso live.
5. A fine job: leggi trascrizione, scarica SRT, apri cartella output.

## Icona tray

Qwibo resta nella tray se chiudi la finestra (backend attivo finché non esci dalla tray).

| Azione | Effetto |
|--------|---------|
| Apri Qwibo | Ripristina finestra |
| Apri cartella log | Log diagnostici |
| Esci | Ferma backend ed esce |

## Dove finiscono i file

```text
%APPDATA%\qwibo-desktop\data\output\jobs\YYYYMMDD_HHMMSS_nomefile\
```

Vedi [Coda e output](../user-guide/jobs-and-output.md).

## Se il setup fallisce

| Sintomo | Cosa provare |
|---------|--------------|
| Download interrotto | Riavvia Qwibo |
| "Avvio troppo lento" | Antivirus; controlla log |
| Disco pieno | Libera almeno 8 GB |

Altro: [Problemi comuni](../troubleshooting/common-issues.md).
