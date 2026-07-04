# Requisiti di sistema

I requisiti dipendono da **cosa usi**: solo trascrizione, riassunto API cloud o riassunto locale Qwen.

## Sistema operativo

| Requisito | Dettaglio |
|-----------|-----------|
| OS | **Windows 10 o 11** (64-bit) |
| Admin | Non richiesto per uso normale |
| Internet | Per **download modelli** e riassunti cloud opzionali |

## Confronto scenari

| Scenario | RAM | Disco libero | Rete in uso |
|----------|-----|--------------|-------------|
| **Solo trascrizione** | 8 GB min · 16 GB consigliati | ~8 GB | No (dopo setup) |
| **Trascrizione + API** | Come sopra | Come sopra | Sì per riassunto |
| **Trascrizione + Qwen locale** | **≥ 16 GB** · 32 GB ideali | ~10–12 GB | No (dopo setup) |

!!! note "RAM e Qwen"
    Prima del riassunto locale il modello ASR viene **scaricato dalla RAM**. Sotto **16 GB** Qwen non viene offerto.

---

## Solo trascrizione

| Risorsa | Dettaglio |
|---------|-----------|
| **RAM** | Minimo **8 GB**; **16 GB** per file lunghi (1 h+). |
| **Disco** | ~2,5 GB modello + dati job → **≥ 8 GB** liberi. |
| **CPU** | x64 moderna; ~**2× tempo reale** (1 min audio ≈ 2 min). |
| **GPU** | Non usata nell'alpha desktop (ASR su CPU). |

---

## Trascrizione + riassunto cloud

| Risorsa | Dettaglio |
|---------|-----------|
| **RAM** | Come solo trascrizione |
| **Rete** | Richiesta durante il riassunto |
| **API key** | In app → **Impostazioni riassunto** |

Adatto a PC con **8 GB RAM** se usi solo provider cloud.

---

## Trascrizione + Qwen locale

| Risorsa | Dettaglio |
|---------|-----------|
| **RAM** | **≥ 16 GB** (controllo al setup) |
| **Disco** | + ~2 GB GGUF |
| **CPU** | Riassunto CPU-bound; testi lunghi = diversi minuti |

Vedi [Modelli](models.md).

---

## Dipendenze incluse

L'installer contiene **Python embedded**, **ffmpeg** e backend Qwibo. L'utente finale non installa nulla a mano.

---

## Alternativa self-hosted

Mini PC Linux con più RAM/GPU: [qwibo-docker](https://github.com/qwibo/qwibo-docker).
