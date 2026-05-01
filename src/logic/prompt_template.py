"""Generator promptu dla AI (ChatGPT/Claude.ai/Gemini).

Tworzy prompt ktory:
1. Wymaga okreslonego formatu odpowiedzi (parsowalnego regexem)
2. Pokrywa 15 jezykow uzywanych na etykietach Happet
3. Mowi AI co zachowac (nazwy brand) i czego unikac (markdown)

Format odpowiedzi: KAZDA linia jako `KOD === tekst`. Pusta linia oddziela
bloki dla czytelnosci. AI moze zwrocic w roznych stylach (markdown bold,
bullets) - parser tolerancyjny.
"""

from __future__ import annotations

# 15 jezykow uzywanych na etykietach Happet (kolejnosc = default order na etykiecie)
LANGUAGES: list[str] = [
    "EN", "PL", "UK", "RO", "DE", "HU", "LT", "SK",
    "CZ", "IT", "ES", "GR", "FR", "PT", "RU",
]

# Pelne angielskie nazwy dla AI (mniej niejednoznaczne niz "UK", ktore moze byc UK = Ukraine albo United Kingdom)
LANGUAGE_NAMES: dict[str, str] = {
    "EN": "English",
    "PL": "Polish",
    "UK": "Ukrainian",
    "RO": "Romanian",
    "DE": "German",
    "HU": "Hungarian",
    "LT": "Lithuanian",
    "SK": "Slovak",
    "CZ": "Czech",
    "IT": "Italian",
    "ES": "Spanish",
    "GR": "Greek",
    "FR": "French",
    "PT": "Portuguese",
    "RU": "Russian",
}


def build_format_prompt(raw_translations: str) -> str:
    """Zbuduj prompt do AI, ktory normalizuje gotowe tlumaczenia do formatu `KOD === tekst`.

    Tryb dla grafika ktory ma juz 15 tlumaczen (od kontrahenta, z poprzedniej etykiety,
    z Excela/Worda) i potrzebuje tylko sformatowania - nie tlumaczenia.
    """
    blocks = "\n".join(
        f"{code} === <{LANGUAGE_NAMES[code]} text>" for code in LANGUAGES
    )

    return f"""Format the following translations into the standard output format. The translations are already done - your job is ONLY to normalize formatting and assign correct language codes.

OUTPUT FORMAT - one line per language. Each line: language code, then " === " (space-equals-equals-equals-space) ONCE, then translation text. Example pattern:

{blocks}

RULES:
- Use the language code prefix exactly as shown (EN, PL, UK, RO, DE, HU, LT, SK, CZ, IT, ES, GR, FR, PT, RU)
- The " === " separator appears EXACTLY ONCE per line, between code and text. NEVER add a closing " === " at the end of the line.
- UK = Ukrainian (NOT British English)
- Plain text only - no markdown, no asterisks (**), no bullet points (-, *), no quotation marks around translations
- One translation per line; if input is multi-line, merge into single line
- DO NOT translate, paraphrase or "improve" the content - just normalize the format
- If a language is missing in the input, output `KOD === ???` to mark the gap
- If you cannot identify which language is which, make your best guess based on text content (e.g. cyrillic = UK or RU, greek alphabet = GR)

Input translations (already done, just normalize the format):
\"\"\"
{raw_translations.strip()}
\"\"\"
"""


def build_prompt(source_text: str, source_lang: str = "EN") -> str:
    """Zbuduj prompt do AI z tekstem zrodlowym i lista 15 jezykow docelowych.

    `source_lang` - kod jezyka zrodlowego (np. "EN" lub "PL"). AI tlumaczy
    z tego jezyka na pozostale 14 + zwraca tekst zrodlowy bez zmian.
    """
    if source_lang not in LANGUAGE_NAMES:
        raise ValueError(
            f"Nieznany jezyk zrodlowy: {source_lang!r}. "
            f"Obslugiwane: {list(LANGUAGE_NAMES.keys())}"
        )

    blocks = "\n".join(
        f"{code} === <{LANGUAGE_NAMES[code]} translation>" for code in LANGUAGES
    )

    return f"""Translate the following text to 15 languages used on Happet pet product labels.

OUTPUT FORMAT - one line per language. Each line: language code, then " === " (space-equals-equals-equals-space) ONCE, then the translation text. Example pattern:

{blocks}

RULES:
- Keep brand names unchanged ("Happet", product codes like "D609")
- Match the source tone (instructional / promotional / informational)
- Match the source length - don't add explanations or padding
- Plain text only - no markdown, no asterisks (**), no bullet points (-, *)
- Use the language code prefix exactly as shown (EN, PL, UK, RO, DE, HU, LT, SK, CZ, IT, ES, GR, FR, PT, RU)
- The " === " separator appears EXACTLY ONCE per line, between code and translation. NEVER add a closing " === " at the end of the line.
- UK = Ukrainian (NOT British English)
- One translation per line; if text is multi-sentence, keep it on one line

Source language: {LANGUAGE_NAMES[source_lang]}
Source text:
\"\"\"
{source_text.strip()}
\"\"\"
"""
