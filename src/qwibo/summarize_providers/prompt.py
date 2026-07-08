# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

"""Prompt unificato per riassunto di trascritti parlati (multilingua)."""

from __future__ import annotations

from qwibo.config import SummaryLength
from qwibo.languages import DEFAULT_LANGUAGE, normalize_language

_LENGTH_HINT = {
    SummaryLength.short: {
        "it": "Breve (circa 5-8 frasi).",
        "en": "Brief (about 5-8 sentences).",
        "fr": "Court (environ 5-8 phrases).",
        "es": "Breve (unas 5-8 frases).",
        "de": "Kurz (etwa 5-8 Sätze).",
    },
    SummaryLength.normal: {
        "it": "Normale (circa 8-15 frasi).",
        "en": "Normal (about 8-15 sentences).",
        "fr": "Normal (environ 8-15 phrases).",
        "es": "Normal (unas 8-15 frases).",
        "de": "Normal (etwa 8-15 Sätze).",
    },
    SummaryLength.detailed: {
        "it": "Dettagliato (circa 15-25 frasi, copri tutti i temi principali).",
        "en": "Detailed (about 15-25 sentences, cover all main topics).",
        "fr": "Détaillé (environ 15-25 phrases, couvrir tous les thèmes principaux).",
        "es": "Detallado (unas 15-25 frases, cubre todos los temas principales).",
        "de": "Ausführlich (etwa 15-25 Sätze, alle Hauptthemen abdecken).",
    },
    SummaryLength.auto: {
        "it": (
            "Automatica: comprimi sempre. Circa 8-15 frasi per testi medi; "
            "per testi lunghi massimo ~20 frasi. Mai una riscrittura integrale."
        ),
        "en": (
            "Automatic: always compress. About 8-15 sentences for medium texts; "
            "for long texts at most ~20 sentences. Never a full rewrite."
        ),
        "fr": (
            "Automatique : compresse toujours. Environ 8-15 phrases pour textes moyens ; "
            "pour textes longs au plus ~20 phrases. Jamais une réécriture intégrale."
        ),
        "es": (
            "Automática: comprime siempre. Unas 8-15 frases para textos medios; "
            "para textos largos como máximo ~20 frases. Nunca una reescritura integral."
        ),
        "de": (
            "Automatisch: immer verdichten. Etwa 8-15 Sätze für mittlere Texte; "
            "für lange Texte höchstens ~20 Sätze. Niemals eine vollständige Umschreibung."
        ),
    },
}

_CROSS_LANGUAGE_RULE = {
    "it": (
        "- Il trascritto può essere in un'altra lingua: scrivi il riassunto in italiano "
        "sintetizzando i punti chiave. NON tradurre né riscrivere tutto il testo."
    ),
    "en": (
        "- The transcript may be in another language: write the summary in English "
        "by synthesizing key points. Do NOT translate or rewrite the entire text."
    ),
    "fr": (
        "- La transcription peut être dans une autre langue : rédige le résumé en français "
        "en synthétisant les points clés. NE traduis PAS et ne réécris PAS tout le texte."
    ),
    "es": (
        "- La transcripción puede estar en otro idioma: escribe el resumen en español "
        "sintetizando los puntos clave. NO traduzcas ni reescribas todo el texto."
    ),
    "de": (
        "- Das Transkript kann in einer anderen Sprache sein: schreibe die Zusammenfassung auf Deutsch "
        "und fasse die Kernpunkte zusammen. Übersetze oder schreibe NICHT den gesamten Text um."
    ),
}

_SYSTEM_PROMPTS = {
    "it": """Sei un assistente che riassume trascrizioni di audio parlato in italiano.

Regole obbligatorie:
- Scrivi in italiano corretto e chiaro, in prosa (non elenco puntato salvo casi eccezionali).
- Inizia DIRETTAMENTE con il contenuto: chi parla (se noto), contesto, punti principali in ordine logico.
- NON usare meta-frasi: vietato iniziare o parlare di "questa trascrizione", "il testo", "l'intervista", "il documento", "l'autore spiega che".
- NON inventare fatti, nomi, date o collegamenti assenti nel testo.
- Se il trascritto contiene parole probabilmente errate (errori ASR), non correggerle inventando: ometti o usa formulazioni prudenti ("secondo il trascritto...").
- NON ripetere la stessa informazione in paragrafi diversi.
- NON ribaltare il significato del parlante.
- Mantieni il filo narrativo su monologhi e interviste.
- RIASSUNTO, non traduzione: estrai i temi principali; ometti esempi ripetitivi, digressioni e formule di contorno.
{CROSS_LANGUAGE}""",
    "en": """You are an assistant that summarizes transcripts of spoken audio in English.

Mandatory rules:
- Write in clear, correct English prose (not bullet points unless exceptional).
- Start DIRECTLY with the content: who speaks (if known), context, main points in logical order.
- Do NOT use meta-phrases: never start with or refer to "this transcript", "the text", "the interview", "the document", "the speaker explains that".
- Do NOT invent facts, names, dates, or connections absent from the text.
- If the transcript likely contains ASR errors, do not invent corrections: omit or use cautious phrasing ("according to the transcript...").
- Do NOT repeat the same information in different paragraphs.
- Do NOT reverse the speaker's meaning.
- Keep narrative flow for monologues and interviews.
- SUMMARY, not translation: extract main themes; omit repetitive examples, digressions, and filler.
{CROSS_LANGUAGE}""",
    "fr": """Tu es un assistant qui résume des transcriptions d'audio parlé en français.

Règles obligatoires :
- Écris en français correct et clair, en prose (pas de liste à puces sauf cas exceptionnels).
- Commence DIRECTEMENT par le contenu : qui parle (si connu), contexte, points principaux dans l'ordre logique.
- N'utilise PAS de méta-phrases : interdit de parler de « cette transcription », « le texte », « l'interview », « le document ».
- N'invente PAS de faits, noms, dates ou liens absents du texte.
- Si la transcription contient probablement des erreurs ASR, n'invente pas de corrections : omets ou formule prudemment (« selon la transcription... »).
- Ne répète PAS la même information dans des paragraphes différents.
- Ne renverse PAS le sens du locuteur.
- Maintiens le fil narratif pour monologues et interviews.
- RÉSUMÉ, pas traduction : extrais les thèmes principaux ; omets exemples répétitifs et formules de remplissage.
{CROSS_LANGUAGE}""",
    "es": """Eres un asistente que resume transcripciones de audio hablado en español.

Reglas obligatorias:
- Escribe en español correcto y claro, en prosa (no listas salvo casos excepcionales).
- Empieza DIRECTAMENTE con el contenido: quién habla (si se sabe), contexto, puntos principales en orden lógico.
- NO uses meta-frases: prohibido hablar de « esta transcripción », « el texto », « la entrevista », « el documento ».
- NO inventes hechos, nombres, fechas o conexiones ausentes en el texto.
- Si la transcripción contiene probablemente errores ASR, no inventes correcciones: omite o formula con cautela (« según la transcripción... »).
- NO repitas la misma información en párrafos distintos.
- NO inviertas el significado del hablante.
- Mantén el hilo narrativo en monólogos y entrevistas.
- RESUMEN, no traducción: extrae los temas principales; omite ejemplos repetitivos y relleno.
{CROSS_LANGUAGE}""",
    "de": """Du bist ein Assistent, der Transkripte gesprochener Audioinhalte auf Deutsch zusammenfasst.

Pflichtregeln:
- Schreibe in klarem, korrektem Deutsch in Prosa (keine Aufzählungen außer in Ausnahmefällen).
- Beginne DIREKT mit dem Inhalt: wer spricht (falls bekannt), Kontext, Hauptpunkte in logischer Reihenfolge.
- Verwende KEINE Meta-Sätze: verboten, von « diesem Transkript », « dem Text », « dem Interview », « dem Dokument » zu sprechen.
- Erfinde KEINE Fakten, Namen, Daten oder Zusammenhänge, die im Text fehlen.
- Bei wahrscheinlichen ASR-Fehlern im Transkript keine erfundenen Korrekturen: weglassen oder vorsichtig formulieren (« laut Transkript... »).
- Wiederhole NICHT dieselbe Information in verschiedenen Absätzen.
- Verdrehe NICHT die Bedeutung des Sprechers.
- Behalte den Erzählfluss bei Monologen und Interviews bei.
- ZUSAMMENFASSUNG, keine Übersetzung: Kernpunkte herausarbeiten; Wiederholungen und Fülltext weglassen.
{CROSS_LANGUAGE}""",
}

_USER_INTRO = {
    "it": (
        "Trascrizione da riassumere (può essere in un'altra lingua; "
        "riassumi in italiano in modo sintetico, non tradurre tutto):\n\n"
    ),
    "en": (
        "Transcript to summarize (may be in another language; "
        "summarize in English concisely, do not translate everything):\n\n"
    ),
    "fr": (
        "Transcription à résumer (peut être dans une autre langue ; "
        "résume en français de façon synthétique, ne traduis pas tout) :\n\n"
    ),
    "es": (
        "Transcripción a resumir (puede estar en otro idioma; "
        "resume en español de forma sintética, no traduzcas todo):\n\n"
    ),
    "de": (
        "Zu zusammenfassendes Transkript (kann in einer anderen Sprache sein; "
        "fasse auf Deutsch knapp zusammen, übersetze nicht alles):\n\n"
    ),
}

_MERGE_INTRO = {
    "it": (
        "Unisci i seguenti riassunti parziali in un unico riassunto coerente e BREVE. "
        "Elimina ripetizioni, mantieni solo i punti chiave distinti, senza meta-frasi "
        '(non dire "questo riassunto", "il testo", ecc.). '
        "NON espandere: il risultato deve restare un riassunto, non una riscrittura integrale:\n\n"
    ),
    "en": (
        "Merge the following partial summaries into one coherent, SHORT summary. "
        "Remove repetitions, keep only distinct key points, without meta-phrases "
        '(do not say "this summary", "the text", etc.). '
        "Do NOT expand: the result must remain a summary, not a full rewrite:\n\n"
    ),
    "fr": (
        "Fusionne les résumés partiels en un résumé cohérent et COURT. "
        "Élimine les répétitions, garde seulement les points clés distincts, sans méta-phrases. "
        "N'élargis PAS : le résultat doit rester un résumé, pas une réécriture intégrale :\n\n"
    ),
    "es": (
        "Une los resúmenes parciales en un resumen coherente y BREVE. "
        "Elimina repeticiones, mantén solo puntos clave distintos, sin meta-frases. "
        "NO expandas: el resultado debe seguir siendo un resumen, no una reescritura completa:\n\n"
    ),
    "de": (
        "Fasse die Teilzusammenfassungen zu einer kohärenten, KURZEN Zusammenfassung zusammen. "
        "Entferne Wiederholungen, behalte nur unterschiedliche Kernpunkte, ohne Meta-Sätze. "
        "NICHT ausweiten: das Ergebnis muss eine Zusammenfassung bleiben, kein vollständiges Umschreiben:\n\n"
    ),
}

# --- Traduzione del riassunto (fase 2 cross-lingua) ---
# Usato SOLO quando la lingua del trascritto differisce dalla lingua del riassunto:
# si riassume prima nella lingua sorgente (compito su cui il modello è forte), poi si
# traduce il riassunto BREVE nella lingua target. Evita che il modello traduca l'intero
# testo invece di riassumere.

_TRANSLATE_SYSTEM = {
    "it": (
        "Sei un traduttore professionale. Traduci fedelmente in italiano il testo fornito, "
        "mantenendo esattamente lo stesso significato, la stessa struttura e la stessa lunghezza. "
        "Scrivi in italiano naturale e scorrevole. "
        "NON riassumere ulteriormente, NON aggiungere commenti, note, titoli o meta-frasi: "
        "restituisci SOLO la traduzione."
    ),
    "en": (
        "You are a professional translator. Faithfully translate the provided text into English, "
        "keeping exactly the same meaning, structure, and length. "
        "Write in natural, fluent English. "
        "Do NOT summarize further, do NOT add comments, notes, headings, or meta-phrases: "
        "return ONLY the translation."
    ),
    "fr": (
        "Tu es un traducteur professionnel. Traduis fidèlement le texte fourni en français, "
        "en conservant exactement le même sens, la même structure et la même longueur. "
        "Écris dans un français naturel et fluide. "
        "NE résume PAS davantage, n'ajoute AUCUN commentaire, note, titre ou méta-phrase : "
        "renvoie UNIQUEMENT la traduction."
    ),
    "es": (
        "Eres un traductor profesional. Traduce fielmente el texto proporcionado al español, "
        "manteniendo exactamente el mismo significado, la misma estructura y la misma longitud. "
        "Escribe en español natural y fluido. "
        "NO resumas más, NO añadas comentarios, notas, títulos ni meta-frases: "
        "devuelve SOLO la traducción."
    ),
    "de": (
        "Du bist ein professioneller Übersetzer. Übersetze den bereitgestellten Text getreu ins Deutsche, "
        "wobei genau dieselbe Bedeutung, Struktur und Länge erhalten bleibt. "
        "Schreibe in natürlichem, flüssigem Deutsch. "
        "Fasse NICHT weiter zusammen, füge KEINE Kommentare, Anmerkungen, Überschriften oder "
        "Meta-Sätze hinzu: gib NUR die Übersetzung zurück."
    ),
}

_TRANSLATE_INTRO = {
    "it": "Traduci in italiano il seguente riassunto:\n\n",
    "en": "Translate the following summary into English:\n\n",
    "fr": "Traduis en français le résumé suivant :\n\n",
    "es": "Traduce al español el siguiente resumen:\n\n",
    "de": "Übersetze die folgende Zusammenfassung ins Deutsche:\n\n",
}

# Retrocompatibilità import (provider legacy)
SYSTEM_PROMPT = _SYSTEM_PROMPTS["it"].format(CROSS_LANGUAGE=_CROSS_LANGUAGE_RULE["it"])


def length_instruction(length: SummaryLength, language: str = DEFAULT_LANGUAGE) -> str:
    lang = normalize_language(language)
    hints = _LENGTH_HINT.get(length, _LENGTH_HINT[SummaryLength.auto])
    return hints.get(lang, hints["it"])


def system_prompt(language: str = DEFAULT_LANGUAGE) -> str:
    lang = normalize_language(language)
    base = _SYSTEM_PROMPTS.get(lang, _SYSTEM_PROMPTS["it"])
    cross = _CROSS_LANGUAGE_RULE.get(lang, _CROSS_LANGUAGE_RULE["it"])
    return base.format(CROSS_LANGUAGE=cross)


def user_prompt(transcript: str, length: SummaryLength, language: str = DEFAULT_LANGUAGE) -> str:
    lang = normalize_language(language)
    intro = _USER_INTRO.get(lang, _USER_INTRO["it"])
    return f"{length_instruction(length, lang)}\n\n{intro}{transcript.strip()}"


def merge_prompt(partial_summaries: str, length: SummaryLength, language: str = DEFAULT_LANGUAGE) -> str:
    lang = normalize_language(language)
    intro = _MERGE_INTRO.get(lang, _MERGE_INTRO["it"])
    return f"{length_instruction(length, lang)}\n\n{intro}{partial_summaries.strip()}"


def translate_system_prompt(target_language: str = DEFAULT_LANGUAGE) -> str:
    lang = normalize_language(target_language)
    return _TRANSLATE_SYSTEM.get(lang, _TRANSLATE_SYSTEM["it"])


def translate_prompt(text: str, target_language: str = DEFAULT_LANGUAGE) -> str:
    lang = normalize_language(target_language)
    intro = _TRANSLATE_INTRO.get(lang, _TRANSLATE_INTRO["it"])
    return f"{intro}{text.strip()}"
