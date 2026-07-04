# Release per macOS senza possedere un Mac

Domanda: *"va fatta la release per Mac ma io non ho un Mac, come faremo?"*

Risposta breve: **si può fare senza comprare un Mac**, usando runner macOS in
cloud (GitHub Actions) o un Mac a noleggio. **Ma non è un semplice "flag"**:
richiede di ri-costruire tutto il runtime Python/ML per macOS. È un
mini-progetto a sé. Sotto trovi le opzioni, i costi e cosa serve davvero.

Aggiornato: 2026-07-04.

---

## 1. I due problemi separati

Fare la build Mac significa risolvere **due** cose distinte:

### A) Serve una macchina macOS per *compilare/firmare*
Apple **obbliga** a costruire e soprattutto a **notarizzare** l'app su macOS
(strumenti `xcodebuild`/`notarytool`). Non si può notarizzare da Windows.

### B) Serve ri-assemblare tutto il runtime per macOS
Oggi `desktop-electron/scripts/build_runtime.py` scarica e monta componenti
**specifici per Windows x64**:
- Python standalone (build Windows),
- wheel di **torch**,
- **NeMo/Parakeet** (ASR),
- **llama-cpp-python** compilato con MinGW per Windows.

Per il Mac servono le **versioni macOS** di tutti questi, e per due
architetture:
- **Apple Silicon (arm64)** — M1/M2/M3/M4, oggi la stragrande maggioranza,
- **Intel (x86_64)** — Mac vecchi.

Questo è il lavoro grosso: replicare `build_runtime.py` in versione macOS.
Buona notizia: su Apple Silicon torch e llama.cpp hanno wheel/build native
mature (Metal/Accelerate), quindi la portabilità CPU non è il problema che è
stato su Windows.

---

## 2. Come ottenere una macchina macOS (senza comprarla)

| Opzione | Costo | Adatto a | Note |
|---|---|---|---|
| **GitHub Actions — runner `macos-latest`** | Gratis fino ai minuti del piano, poi a consumo | Build + notarizzazione automatiche | **Consigliata.** Runner Apple Silicon disponibili. Firma/notarizza in CI. |
| **AWS EC2 Mac** | ~a ore, costoso (min. 24h) | Build occasionali "vere" | Potente ma caro. |
| **MacStadium / MacinCloud / Scaleway Mac** | Abbonamento/ore | Accesso desktop a un Mac | Utile per debug interattivo. |
| **Prestito/noleggio locale** | Basso | Primo test manuale | Un amico con un Mac per il primo giro. |

**Requisito trasversale:** per firmare e notarizzare serve l'**Apple Developer
Program a 99 $/anno**. Senza notarizzazione, su macOS recente Gatekeeper
**blocca** l'app in modo molto più aggressivo dello SmartScreen di Windows
(l'utente deve fare giri nascosti nelle impostazioni → adozione bassissima).

---

## 3. Percorso consigliato (concreto)

1. **Non farlo adesso.** Consolida prima l'alpha **Windows** (è già funzionante
   e testata). Il Mac è un secondo progetto: aprilo quando c'è domanda reale.
2. Quando decidi di partire:
   - Iscriviti all'**Apple Developer Program** (99 $/anno).
   - Crea un workflow **GitHub Actions** su runner `macos-latest` che:
     a. costruisce il runtime macOS (versione mac di `build_runtime.py`),
     b. impacchetta con electron-builder in **.dmg**,
     c. **firma** (Developer ID) e **notarizza** (`notarytool`),
     d. carica l'artefatto (stesso host di distribuzione della §01).
   - Target: **arm64** per primo (copre la maggioranza), poi valuta x86_64 o
     un binario **universal**.
3. Per il **debug interattivo** iniziale, affiancaci qualche ora di MacinCloud
   o un Mac in prestito: i runner CI sono "ciechi", serve almeno un primo giro
   manuale per far girare davvero torch/NeMo/llama.

---

## 4. Sforzo realistico (aspettative oneste)

- **Non** è "cambio un target e ho il .dmg". È **rifare la pipeline runtime**
  per macOS + firma + notarizzazione + test.
- Stima grezza: **giorni/settimane** di lavoro, non ore, soprattutto per far
  combaciare torch + NeMo (Parakeet) su macOS arm64 dentro il runtime embedded.
- Costo ricorrente minimo: **99 $/anno** (Apple) + eventuali minuti CI.

---

## 5. Riepilogo decisione

| Domanda | Risposta |
|---|---|
| Posso fare la build Mac senza un Mac? | Sì, via **GitHub Actions macOS** o Mac a noleggio. |
| Basta un flag? | No: va ri-costruito il runtime Python/ML per macOS (arm64/x86_64). |
| Serve pagare? | Sì: **99 $/anno** Apple Developer (per firma+notarizzazione). |
| Quando farlo? | **Dopo** aver stabilizzato l'alpha Windows. |
| Da dove partire? | Runner CI `macos-latest`, target **arm64**, output **.dmg** firmato+notarizzato. |
