# Qwibo — branding

Il marchio riprende l'etimologia del nome: **trascrivere** = trascrivere da una *bobina*.
La bobina (cerchio + perno) srotola il nastro che diventa **righe di testo**.

## Palette

| Ruolo | Hex | Uso |
|-------|-----|-----|
| Accent (dark bg) | `#38bdf8` | bobina + nastro su sfondo scuro (stesso accent della web UI) |
| Accent (light bg) | `#0284c7` | bobina + nastro su sfondo chiaro (contrasto AA) |
| Testo dark bg | `#f0f4ff` | righe di testo + wordmark su sfondo scuro |
| Testo light bg | `#0f172a` | righe di testo + wordmark su sfondo chiaro |

## File

| File | Uso |
|------|-----|
| `logo-mark.svg` | Solo simbolo, sfondo trasparente. Le righe di testo usano `currentColor`: eredita il colore del contesto (ideale inline nell'HTML). |
| `logo-horizontal-dark.svg` | Lockup orizzontale per sfondi scuri (hero landing, header UI). Testo in tracciati. |
| `logo-horizontal-light.svg` | Lockup orizzontale per sfondi chiari (docs, fatture, README). Testo in tracciati. |
| `favicon.svg` | Icona quadrata arrotondata su fondo `#0f172a` — favicon / app icon / social avatar. |

## Wordmark

Disegnato in **Inter Bold** (wght 700, opsz 14), minuscolo, letter-spacing −1, corpo 40.
Il testo nei lockup è **convertito in tracciati vettoriali**: nessun font da caricare sul sito,
rende identico ovunque (browser, e-mail, stampa, `<img>`).

## Regole d'uso

- Area di rispetto: almeno l'altezza di una riga di testo del simbolo su ogni lato.
- Non ruotare, non aggiungere ombre/gradienti, non cambiare le proporzioni.
- Dimensione minima simbolo: 16 px (favicon ok).
