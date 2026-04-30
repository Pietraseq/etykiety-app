"""Parser odpowiedzi AI - tolerancyjny na rozne formaty markdown.

Idealnie AI zwraca:
    EN === Hello world
    PL === Witaj swiecie

Ale w praktyce ChatGPT/Claude.ai czasem dodaje:
- markdown bold: **EN** === Hello world
- bullety: - EN === Hello world
- backticki: `EN` === Hello world
- nadgodzajce naglowki: # Translations\n\nEN === ...
- duplikaty (np. obecny w naglowku i w body)

Regex tolerancyjny: lewa strona moze miec dowolny prefix non-alphanumeric.
"""

from __future__ import annotations

import re

from .prompt_template import LANGUAGES

# Regex: od poczatku linii, opcjonalny prefix (markdown, bullety, spacje),
# 2 wielkie litery (kod jezyka), ===, reszta linii jako tlumaczenie.
# Multiline mode - ^ pasuje do poczatku kazdej linii.
LANGUAGE_LINE = re.compile(
    r"^[\s\-*_>#`]*\**\s*([A-Z]{2})\s*\**\s*`?\s*===\s*(.+?)\s*$",
    re.MULTILINE,
)


def parse_translations(ai_response: str) -> dict[str, str]:
    """Wyciagnij {lang_code: text} z odpowiedzi AI.

    Tolerancyjny na markdown bold (**EN**), bullety (- EN, * EN), ranges,
    backticki, prefixy. Pierwsze wystapienie kodu jezyka wygrywa (duplikaty
    ignorowane - AI moze powtorzyc kod w naglowku i body).
    """
    if not ai_response or not ai_response.strip():
        return {}

    cleaned_text = _strip_markdown_artifacts(ai_response)

    result: dict[str, str] = {}
    for match in LANGUAGE_LINE.finditer(cleaned_text):
        code, text = match.group(1), match.group(2).strip()
        # Usun trailing markdown (`, **, ", )
        text = _clean_translation_text(text)
        if not text:
            continue
        if code not in result:
            result[code] = text
    return result


def validate_translations(
    parsed: dict[str, str],
    expected: list[str] = LANGUAGES,
) -> tuple[list[str], list[str]]:
    """Zwroc (missing, extra) - kody jezykow brakujacych i nadmiarowych."""
    expected_set = set(expected)
    parsed_set = set(parsed.keys())
    missing = sorted(expected_set - parsed_set)
    extra = sorted(parsed_set - expected_set)
    return missing, extra


def _strip_markdown_artifacts(text: str) -> str:
    """Usun typowe markdown wrappery ktore AI dodaje wokol bloku tlumaczen.

    Np. ```\nEN === ...\n``` -> EN === ...
    """
    text = re.sub(r"```\w*\n?", "", text)
    text = re.sub(r"\n```", "", text)
    return text


def _clean_translation_text(text: str) -> str:
    """Usun trailing artefakty markdown z tekstu tlumaczenia."""
    text = text.strip()
    # Usun trailing backticks, gwiazdki, podkreslenia (markdown)
    text = re.sub(r"[`*_]+$", "", text).strip()
    # Usun otaczajace cudzyslowy
    if len(text) >= 2:
        if (text[0] == text[-1]) and text[0] in ('"', "'", "“", "”", "«", "»"):
            text = text[1:-1].strip()
    return text
