"""Embedowanie flag SVG (lipis/flag-icons) jako <symbol> w <defs> wynikowego SVG.

Czyta plik flagi (1x1, viewBox 0 0 512 512), wycina dzieci roota i opakowuje
w <symbol id="flag-XX">. Output renderuje flagi przez <use href="#flag-XX">
z clipPathem na okrag (lub rect z rx) wedlug stylu w config.
"""

from __future__ import annotations

from pathlib import Path

from lxml import etree

SVG_NS = "http://www.w3.org/2000/svg"

# Mapowanie kodu jezyka uzywanego w YAML -> kod kraju ISO (= nazwa pliku flagi)
# Uwaga: YAML uzywa "EN" dla angielskiego (flaga UK = gb), "UK" dla ukrainskiego (flaga ua)
DEFAULT_LANG_TO_FLAG = {
    "EN": "gb",
    "PL": "pl",
    "UK": "ua",
    "RO": "ro",
    "DE": "de",
    "HU": "hu",
    "LT": "lt",
    "SK": "sk",
    "CZ": "cz",
    "IT": "it",
    "ES": "es",
    "GR": "gr",
    "FR": "fr",
    "PT": "pt",
    "RU": "ru",
}


def load_flag_symbol(flag_code: str, flag_path: Path) -> etree._Element:
    """Wczytaj plik flagi i opakuj jego zawartosc jako <symbol id="flag-XX">.

    Zachowuje viewBox z oryginalu. Usuwa atrybut id z roota (zastepujemy
    naszym id-em). Wewnetrzne id-y pozostawia (lipis prefixuje je kodem
    kraju, kolizji nie ma).
    """
    if not flag_path.is_file():
        raise FileNotFoundError(f"Brak pliku flagi: {flag_path}")
    flag_tree = etree.parse(str(flag_path))
    flag_root = flag_tree.getroot()
    viewBox = flag_root.get("viewBox", "0 0 512 512")

    symbol = etree.Element(
        f"{{{SVG_NS}}}symbol",
        attrib={
            "id": f"flag-{flag_code}",
            "viewBox": viewBox,
            "preserveAspectRatio": "xMidYMid slice",
        },
    )
    for child in list(flag_root):
        symbol.append(child)
    return symbol


def build_flag_defs(
    flags_dir: Path,
    flag_codes: list[str],
) -> etree._Element:
    """Stworz <defs> z 15 <symbol> + 1 <clipPath> dla zaokraglenia."""
    defs = etree.Element(f"{{{SVG_NS}}}defs")

    # ClipPath: okrag wpisany w bounding box <use> (objectBoundingBox = 0..1)
    clip = etree.SubElement(
        defs,
        f"{{{SVG_NS}}}clipPath",
        attrib={
            "id": "flag-circle",
            "clipPathUnits": "objectBoundingBox",
        },
    )
    etree.SubElement(
        clip,
        f"{{{SVG_NS}}}circle",
        attrib={"cx": "0.5", "cy": "0.5", "r": "0.5"},
    )

    seen = set()
    for code in flag_codes:
        if code in seen:
            continue
        seen.add(code)
        flag_path = flags_dir / f"{code}.svg"
        defs.append(load_flag_symbol(code, flag_path))
    return defs


def resolve_flag_code(language_code: str, mapping: dict[str, str] | None = None) -> str:
    """Pobierz kod flagi (kraju) dla podanego kodu jezyka."""
    full = {**DEFAULT_LANG_TO_FLAG, **(mapping or {})}
    flag_code = full.get(language_code)
    if flag_code is None:
        raise ValueError(
            f"Brak mapowania jezyk -> flaga dla {language_code!r}. "
            f"Dodaj wpis w `flags.language_to_flag` w YAML lub w "
            f"DEFAULT_LANG_TO_FLAG."
        )
    return flag_code
