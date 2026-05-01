"""Podzial slow na sylaby przez pyphen.

Mapuje kody jezyka uzywane w YAML (EN/PL/DE...) na kody locale uzywane przez
pyphen (en_US, pl_PL, de_DE...). Kontrolowane przez konfig - kazdy jezyk
mozna wylaczyc indywidualnie gdy slownik daje brzydkie podzialy.
"""

from __future__ import annotations

import pyphen


# YAML language code -> pyphen locale
LOCALE_MAP = {
    "EN": "en_US",
    "PL": "pl_PL",
    "UK": "uk_UA",
    "RO": "ro_RO",
    "DE": "de_DE",
    "HU": "hu_HU",
    "LT": "lt_LT",
    "SK": "sk_SK",
    "CZ": "cs_CZ",
    "IT": "it_IT",
    "ES": "es_ES",
    "GR": "el_GR",
    "FR": "fr_FR",
    "PT": "pt_PT",
    "RU": "ru_RU",
}


class Hyphenator:
    """Wrapper na pyphen.Pyphen z fallbackiem do braku podzialu."""

    def __init__(self, lang_code: str):
        locale = LOCALE_MAP.get(lang_code)
        if locale is None or locale not in pyphen.LANGUAGES:
            self._pyphen = None
        else:
            self._pyphen = pyphen.Pyphen(lang=locale)

    def split_pairs(self, word: str) -> list[tuple[str, str]]:
        """Zwraca liste par (left, right) - mozliwych podzialow slowa.

        Lewa strona zawiera lacznik na koncu, prawa zaczyna od reszty slowa.
        Pusta lista = brak slownika lub slowo zbyt krotkie do podzialu.
        """
        if self._pyphen is None:
            return []
        # iterate_pairs zwraca (lhs_no_hyphen, rhs) - ale my chcemy lhs Z lacznikiem
        return [(left + "-", right) for left, right in self._pyphen.iterate(word)]
