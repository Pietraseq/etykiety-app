"""Pytest dla parsera odpowiedzi AI - rozne formaty markdown."""

from __future__ import annotations

import pytest

from src.logic.parser import parse_translations, validate_translations
from src.logic.prompt_template import LANGUAGES


def test_basic_format_plain():
    response = """EN === Hello world
PL === Witaj swiecie
UK === Привіт світе"""
    result = parse_translations(response)
    assert result["EN"] == "Hello world"
    assert result["PL"] == "Witaj swiecie"
    assert result["UK"] == "Привіт світе"


def test_markdown_bold():
    response = """**EN** === Hello world
**PL** === Witaj swiecie
**UK** === Привіт"""
    result = parse_translations(response)
    assert result["EN"] == "Hello world"
    assert result["PL"] == "Witaj swiecie"
    assert result["UK"] == "Привіт"


def test_bullet_dash():
    response = """- EN === Hello world
- PL === Witaj swiecie"""
    result = parse_translations(response)
    assert result["EN"] == "Hello world"
    assert result["PL"] == "Witaj swiecie"


def test_bullet_asterisk():
    response = """* EN === Hello
* PL === Witaj"""
    result = parse_translations(response)
    assert result["EN"] == "Hello"
    assert result["PL"] == "Witaj"


def test_backticks_around_code():
    response = """`EN` === Hello
`PL` === Witaj"""
    result = parse_translations(response)
    assert result["EN"] == "Hello"
    assert result["PL"] == "Witaj"


def test_code_block_wrapper():
    response = """```
EN === Hello world
PL === Witaj
```"""
    result = parse_translations(response)
    assert result["EN"] == "Hello world"
    assert result["PL"] == "Witaj"


def test_extra_header_text():
    response = """Sure, here are the translations:

EN === Hello world
PL === Witaj swiecie

Let me know if you need anything else!"""
    result = parse_translations(response)
    assert result["EN"] == "Hello world"
    assert result["PL"] == "Witaj swiecie"
    # Heuristic: tylko 2 jezyki sparsowane, "Sure" / "Let" nie pasuja do regexu
    assert len(result) == 2


def test_quoted_translation():
    response = '''EN === "Hello world"
PL === "Witaj swiecie"'''
    result = parse_translations(response)
    assert result["EN"] == "Hello world"
    assert result["PL"] == "Witaj swiecie"


def test_diacritics_and_cyrillic():
    response = """PL === Jednorazowy, aktywowany tlenem ogrzewacz. Wyjąć z folii.
UK === Одноразовий, активований киснем обігрівач. Вийняти з фольги.
GR === Θερμαντικό μίας χρήσης ενεργοποιούμενο με οξυγόνο.
RU === Одноразовый, активируемый кислородом обогреватель."""
    result = parse_translations(response)
    assert "Jednorazowy" in result["PL"]
    assert "Одноразовий" in result["UK"]
    assert "Θερμαντικό" in result["GR"]
    assert "Одноразовый" in result["RU"]


def test_duplicate_codes_first_wins():
    response = """EN === First version
PL === Witaj
EN === Second version (should be ignored)"""
    result = parse_translations(response)
    assert result["EN"] == "First version"


def test_missing_languages_validation():
    parsed = {"EN": "Hello", "PL": "Witaj"}
    missing, extra = validate_translations(parsed, LANGUAGES)
    assert "EN" not in missing
    assert "PL" not in missing
    assert "UK" in missing
    assert "DE" in missing
    assert len(missing) == 13
    assert len(extra) == 0


def test_extra_languages_validation():
    full = {code: f"text_{code}" for code in LANGUAGES}
    full["ZZ"] = "unexpected"
    full["XX"] = "also unexpected"
    missing, extra = validate_translations(full, LANGUAGES)
    assert len(missing) == 0
    assert "XX" in extra
    assert "ZZ" in extra


def test_empty_response():
    assert parse_translations("") == {}
    assert parse_translations("   ") == {}


def test_no_separator_returns_empty():
    response = "Hello world\nWitaj\nПривіт"
    result = parse_translations(response)
    assert result == {}


def test_full_15_languages():
    """Pelny przyklad realnej odpowiedzi AI dla D609."""
    response = """EN === Single-use, oxygen-activated heat pack.
PL === Jednorazowy, aktywowany tlenem ogrzewacz.
UK === Одноразовий, активований киснем обігрівач.
RO === Încălzitor de unică folosință, activat cu oxigen.
DE === Einweg-, sauerstoffaktivierter Wärmer.
HU === Egyszer használatos, oxigénnel aktivált melegítő.
LT === Vienkartinis, deguonimi aktyvuojamas šildytuvas.
SK === Jednorazový, kyslíkom aktivovaný ohrievač.
CZ === Jednorázový, kyslíkem aktivovaný ohřívač.
IT === Riscaldatore monouso attivato dall'ossigeno.
ES === Calentador de un solo uso activado por oxígeno.
GR === Θερμαντικό μίας χρήσης, ενεργοποιούμενο με οξυγόνο.
FR === Chauffe-main à usage unique activé par l'oxygène.
PT === Aquecedor descartável ativado por oxigênio.
RU === Одноразовый, активируемый кислородом обогреватель."""
    result = parse_translations(response)
    missing, extra = validate_translations(result, LANGUAGES)
    assert missing == []
    assert extra == []
    assert len(result) == 15


@pytest.mark.parametrize("source_lang", ["EN", "PL"])
def test_prompt_includes_source_language(source_lang):
    from src.logic.prompt_template import build_prompt
    prompt = build_prompt("Test text", source_lang=source_lang)
    assert "Test text" in prompt
    if source_lang == "EN":
        assert "Source language: English" in prompt
    elif source_lang == "PL":
        assert "Source language: Polish" in prompt


def test_prompt_invalid_source_lang_raises():
    from src.logic.prompt_template import build_prompt
    with pytest.raises(ValueError):
        build_prompt("Test", source_lang="ZZ")
