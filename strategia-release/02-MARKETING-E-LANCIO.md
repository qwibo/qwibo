# Piano di marketing e lancio — Qwibo (alpha)

Canali dove annunciare la release e **testi pronti all'uso** per favorire
l'adozione. Pensato per un'**alpha**: tono "early access / cerchiamo feedback",
non lancio in pompa magna (quello si tiene per la 1.0).

Aggiornato: 2026-07-04.

---

## 0. Strategia in una frase

> All'alpha **non** si fa il lancio grosso. Si fa un **soft-launch mirato** nelle
> community tecniche giuste (self-hosting, LLM locali, privacy), si raccoglie
> feedback, si sistemano i bug, e si **conserva Product Hunt / Show HN per la
> 1.0** (si lancia una volta sola bene: bruciare il lancio su un'alpha instabile
> è uno spreco).

---

## 1. Posizionamento (il messaggio)

**Cos'è:** app desktop Windows che **trascrive audio e ne fa il riassunto**,
**100% in locale**, senza mandare nulla nel cloud.

**Value proposition (una riga):**
> *Trascrivi e riassumi audio sul tuo PC, offline. Niente cloud, niente
> abbonamenti, i tuoi dati non escono di casa.*

**Perché la gente dovrebbe usarlo (i "gancetti"):**
- 🔒 **Privacy reale**: audio sensibili (interviste, riunioni, referti, atti)
  non vengono caricati su server di terzi.
- 💸 **Nessun costo a consumo**: niente API cloud a pagamento.
- 🌍 **Multilingua**: 25 lingue europee (IT, EN, FR, ES, DE in primo piano).
- 🧠 **Riassunto con LLM locale** (Qwen) oltre alla trascrizione.
- 🖥️ **Gira su hardware normale**: nessuna GPU richiesta, funziona su mini PC.

**Chi è il pubblico (target):**
- Giornalisti e redazioni (interviste da trascrivere).
- Studi legali / medici (dati riservati, no cloud per contratto/GDPR).
- Ricercatori, studenti (lezioni, focus group).
- Podcaster / creator (trascrizioni, sottotitoli).
- PMI e PA attente alla privacy / con connessione inaffidabile.
- Community self-hosting / privacy / LocalLLaMA.

---

## 2. Canali — priorità per un'ALPHA

### 🎯 Priorità ALTA (community tecniche, tolleranti verso l'alpha)
1. **Reddit r/LocalLLaMA** — pubblico perfetto (LLM in locale). Tono tecnico.
2. **Reddit r/selfhosted** — amano il "tutto in locale, niente cloud".
3. **Reddit r/privacy** e **r/degoogle** — angolo privacy.
4. **Hacker News — "Show HN"** *(valuta: ok anche in alpha se onesto sul
   "work in progress"; ma il vero colpo tienilo per la 1.0)*.
5. **Lobsters** (se hai un invito) — pubblico tecnico di qualità.

### 🎯 Priorità MEDIA
6. **Reddit di nicchia**: r/opensource, r/transcription, r/podcasting,
   r/journalism, r/datahoarder, subreddit per lingua (r/italy per il pubblico IT).
7. **Indie Hackers** — storia del build in pubblico.
8. **dev.to / Hashnode** — articolo tecnico "come ho impacchettato torch + NeMo
   + llama.cpp in un installer Windows che gira su qualsiasi CPU".
9. **X/Twitter** e **LinkedIn** — post + GIF demo; LinkedIn ottimo per il
   pubblico "aziende/privacy".

### 🎯 Da tenere per la 1.0 (lancio grosso)
10. **Product Hunt** — lancio una tantum, meglio con prodotto stabile e firmato.
11. **BetaList / directory** (AlternativeTo, SaaSHub, Slant) — schede permanenti.
12. Stampa tech italiana (il pubblico IT è a portata, autore italiano).

---

## 3. Testi pronti all'uso (copia-incolla)

> Adatta i link. Sii **onesto sull'alpha** e sui limiti (non firmato,
> Windows-only per ora): nelle community tecniche l'onestà premia.

### 3.1 Reddit — r/LocalLLaMA / r/selfhosted (EN)
**Titolo:**
`Qwibo (alpha): offline audio transcription + local LLM summary on Windows, no cloud, no GPU needed`

**Corpo:**
```
I built a Windows desktop app that transcribes audio and summarizes it 100%
locally — nothing is uploaded anywhere.

- ASR: NVIDIA Parakeet (25 EU languages, IT/EN/FR/ES/DE first)
- Summary: local LLM (Qwen 3B, GGUF via llama.cpp)
- CPU-only, no GPU required — tested on a mini PC
- Everything bundled in one installer (embedded Python runtime)

This is an early ALPHA: Windows-only for now, the installer isn't code-signed
yet (SmartScreen will warn), and I'm looking for feedback on real hardware.

The tricky part was making llama.cpp run on ANY x64 CPU: the prebuilt wheels
assumed AVX2 and crashed on some machines, so I recompiled it baseline (no AVX).

Download + notes: <LINK>
SHA256: <HASH>

Happy to answer technical questions about the packaging.
```

### 3.2 Hacker News — Show HN (EN)
**Titolo:**
`Show HN: Qwibo – offline transcription + local LLM summaries (Windows, no cloud)`

**Primo commento (contesto, come vuole HN):**
```
Author here. Qwibo is a Windows desktop app that transcribes audio and
summarizes it entirely offline — no cloud, no per-use API costs.

Stack: NVIDIA Parakeet for ASR (25 EU languages), a local Qwen 3B GGUF via
llama.cpp for summaries, all wrapped in Electron with an embedded, relocatable
Python runtime. CPU-only.

It's an early alpha. Known limits: Windows only, installer not yet signed,
first run is slow (loads ~GBs of weights). The interesting engineering problem
was CPU portability — I recompiled llama.cpp in a baseline (no-AVX) config so
it runs on any x64 CPU, verified by disassembling the DLLs to ensure zero AVX
instructions.

Looking for feedback, especially on odd CPUs/hardware.
```

### 3.3 Reddit / X — versione ITALIANA
**Titolo:**
`Qwibo (alpha): trascrizione audio + riassunto con IA, tutto in locale su Windows (no cloud)`

**Corpo:**
```
Ho creato un'app desktop per Windows che trascrive l'audio e ne fa il
riassunto, il tutto al 100% sul tuo PC: niente cloud, niente abbonamenti, i
dati non escono dal computer.

- Trascrizione: modello Parakeet (25 lingue, IT/EN/FR/ES/DE in primo piano)
- Riassunto: LLM locale (Qwen) via llama.cpp
- Solo CPU, nessuna GPU richiesta — provato su un mini PC
- Un unico installer, Python già incluso

È una ALPHA: per ora solo Windows, l'installer non è ancora firmato (SmartScreen
avvisa), e cerco feedback su hardware reale.

Download e note: <LINK>
```

### 3.4 X/Twitter (breve, con GIF)
```
🎙️ Qwibo (alpha)

Trascrivi + riassumi audio sul TUO PC. Offline. Niente cloud, niente
abbonamenti.

✅ 25 lingue
✅ LLM locale (Qwen)
✅ Solo CPU, gira su mini PC
✅ Windows

Cerco tester 👉 <LINK>
#privacy #selfhosted #AI
```

### 3.5 LinkedIn (tono professionale/privacy)
```
Molte aziende non possono caricare audio riservati nel cloud: interviste,
riunioni, dati sanitari o legali.

Ho sviluppato Qwibo: un'app desktop che trascrive e riassume l'audio
completamente in locale, senza mandare nulla su server esterni. Solo CPU,
nessuna GPU, multilingua.

È in fase alpha e cerco organizzazioni disposte a provarla e darmi feedback.
Dettagli e download: <LINK>
```

---

## 4. Asset da preparare prima di postare

- [ ] **GIF/video demo** (20-40s): carico file → scelgo lingua → trascrizione →
      riassunto. È l'asset che converte di più.
- [ ] **3-5 screenshot** puliti (coda, job in corso, riassunto finale).
- [ ] **Logo/icona** (già presente: `assets/icon.ico`).
- [ ] **Landing page** con bottone download, requisiti, changelog, checksum.
- [ ] **1 paragrafo "cos'è"** + **1 riga** value prop (già sopra).
- [ ] **FAQ breve**: "è gratis?", "i dati escono?", "serve GPU?", "quali lingue?",
      "perché SmartScreen avvisa?".

---

## 5. Tempistiche & buone pratiche

- **Reddit/HN**: posta in orario USA mattina (≈ 14:00–17:00 ora italiana),
  giorni feriali (mar–gio). Rispondi ai commenti nelle prime 2 ore (l'algoritmo
  premia l'engagement iniziale).
- **Un canale alla volta**, non tutto lo stesso giorno: così gestisci i feedback
  e non bruci le community.
- **Non spammare**: personalizza il testo per ogni subreddit, leggi le regole
  (alcuni vietano i "self-promotion" senza karma/flair).
- **Raccogli i contatti** dei tester (un form o una mail) per avvisarli degli
  update.
- **Metti sempre**: "alpha", "Windows", "non firmato", requisiti CPU. Aspettative
  oneste = meno recensioni negative.

---

## 6. Percorso consigliato

1. **Ora (alpha):** soft-launch su r/LocalLLaMA + r/selfhosted + r/privacy →
   raccogli feedback e bug su hardware vari.
2. **Beta:** allarga (più subreddit, dev.to, Indie Hackers), firma il codice.
3. **1.0:** lancio grosso coordinato — **Product Hunt** + **Show HN** + stampa +
   directory, con demo curata e installer firmato.
