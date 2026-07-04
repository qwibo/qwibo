# Download e installazione

Qwibo si installa con un unico file `.exe`. Niente Python, ffmpeg o Docker.

## Download

1. Apri le [GitHub Releases](https://github.com/qwibo/qwibo/releases) del repo **qwibo**.
2. Scarica l'ultimo **`Qwibo-Setup-*.exe`** (alpha: tag `0.1.0-alpha.*`).
3. Dimensione ~**2–3 GB** — il runtime è nell'installer; i modelli si scaricano al primo avvio.

## Installazione

1. Doppio click sull'installer.
2. Accetta la licenza e conferma la cartella (default ok).
3. Fine wizard — Qwibo si apre da solo.

!!! warning "Windows SmartScreen"
    L'installer alpha **non è ancora firmato**. Windows può mostrare *"Windows ha protetto il PC"*.  
    **Ulteriori informazioni** → **Esegui comunque**. Vedi [SmartScreen](../troubleshooting/smartscreen.md).

## Dopo l'installazione

Al primo avvio parte il wizard **setup modelli** (~4–5 GB, una volta):

| Modello | Dimensione | Obbligatorio |
|---------|------------|--------------|
| Parakeet ASR | ~2,5 GB | Sì |
| Qwen locale | ~2 GB | Solo se RAM ≥ 16 GB |

Al termine si apre la finestra principale. Vedi [Primo avvio](first-run.md).

## Disinstallazione

**Impostazioni → App → Qwibo → Disinstalla**.

I dati in `%APPDATA%\qwibo-desktop\` **non** vengono rimossi automaticamente. Elimina quella cartella per reinstallazione pulita.

## Docker self-hosted

Per un'interfaccia browser su server di casa: [qwibo-docker](https://github.com/qwibo/qwibo-docker) — repo e documentazione separati.
