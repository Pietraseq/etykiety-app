"""Auto-tune font_size przez bisekcje.

Cel: znalezc najwiekszy font_size przy ktorym najdluzszy jezyk ma <= preferred_lines.

Wykorzystuje silnik etykiety-svg (layout_page) do symulacji, bez emisji SVG.
Zakres bisekcji [1.0mm, 5.0mm], precyzja 0.05mm = ~7 iteracji.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

from .prompt_template import LANGUAGES

# Submodule etykiety_svg jest dodany do sys.path w app.py - importujemy z niego
from label_generator.config import (
    FlagsConfig,
    FontConfig,
    HyphenationConfig,
    LabelConfig,
    PrefixMarkerConfig,
    TextAreaConfig,
)
from label_generator.layout import layout_page


PROJECT_ROOT = Path(__file__).resolve().parents[2] / "etykiety_svg"


def build_column_split(
    layout_name: str,
    languages: Iterable[str] = LANGUAGES,
) -> list[list[str]]:
    """Mapuje 'layout_name' na listy jezykow per kolumna.

    Kolejnosc jezykow zachowana z `languages` (default: porzadek z LANGUAGES,
    czyli EN PL UK RO DE HU LT SK CZ IT ES GR FR PT RU).
    """
    splits = {
        "8+7": [8, 7],
        "5+5+5": [5, 5, 5],
        "3+3+3+3+3": [3, 3, 3, 3, 3],
    }
    if layout_name not in splits:
        raise ValueError(
            f"Nieznany layout: {layout_name!r}. Obslugiwane: {list(splits.keys())}"
        )
    sizes = splits[layout_name]
    langs = list(languages)
    if sum(sizes) != len(langs):
        raise ValueError(
            f"Layout {layout_name} wymaga {sum(sizes)} jezykow, dostarczono {len(langs)}"
        )
    out: list[list[str]] = []
    idx = 0
    for size in sizes:
        out.append(langs[idx:idx + size])
        idx += size
    return out


def build_temp_config(
    texts: dict[str, str],
    *,
    font_size_mm: float,
    layout_name: str = "8+7",
    page_size: tuple[float, float] = (219.96, 160.10),
    text_area_size: tuple[float, float] = (100.0, 145.0),
    text_area_origin: tuple[float, float] = (5.0, 5.0),
    gutter_mm: float = 3.0,
    marker_size_mm: float = 2.6,
    marker_style: str = "flag_circle",
    marker_color: str = "#E60000",
    line_height_multiplier: float = 1.2,
    enable_hyphenation: bool = True,
    hyphenation_per_lang: dict[str, bool] | None = None,
) -> LabelConfig:
    """Zbuduj LabelConfig dla testowej symulacji layoutu (bez zapisu SVG)."""
    column_split = build_column_split(layout_name, languages=texts.keys())
    columns = len(column_split)
    return LabelConfig(
        product_code="temp",
        page_size=page_size,
        text_area=TextAreaConfig(
            x=text_area_origin[0],
            y=text_area_origin[1],
            width=text_area_size[0],
            height=text_area_size[1],
        ),
        columns=columns,
        gutter=gutter_mm,
        font=FontConfig(
            family="Arial",
            path=Path("fonts/arial.ttf"),
            bold_path=Path("fonts/arialbd.ttf"),
            size=font_size_mm,
            line_height=line_height_multiplier,
        ),
        prefix_marker=PrefixMarkerConfig(
            size=marker_size_mm,
            style=marker_style,
            color=marker_color,
        ),
        flags=FlagsConfig(path=Path("assets/flags")),
        hyphenation=HyphenationConfig(
            enabled=enable_hyphenation,
            per_language=hyphenation_per_lang or {"UK": False, "GR": False},
        ),
        languages=texts,
        column_split=column_split,
    )


# Wartosc-sentinela: gdy font tak duzy, ze kolumna nie miesci sie w obszarze tekstu,
# silnik rzuca ValueError. W bisekcji traktujemy to jako "ekstremalnie za duzo wierszy".
OVERFLOW_LINES = 999


def count_lines_per_block(
    texts: dict[str, str],
    *,
    font_size_mm: float,
    project_root: Path = PROJECT_ROOT,
    **config_kwargs,
) -> dict[str, int]:
    """Symuluj layout dla danego font_size, zwroc {kod_jezyka: liczba_wierszy}.

    Gdy font za duzy (kolumna nie miesci sie w obszarze): zwroc wartosc-sentinele
    OVERFLOW_LINES dla wszystkich jezykow, zeby bisekcja wiedziala 'zmniejsz'.
    """
    config = build_temp_config(texts, font_size_mm=font_size_mm, **config_kwargs)
    try:
        page = layout_page(config, project_root=project_root)
    except ValueError as e:
        msg = str(e)
        if "przekracza dostepna wysokosc" in msg or "nie miesci sie" in msg:
            return {code: OVERFLOW_LINES for code in texts.keys()}
        raise
    return {block.code: len(block.lines) for block in page.blocks}


def find_optimal_font(
    texts: dict[str, str],
    preferred_lines: int,
    *,
    min_font: float = 1.0,
    max_font: float = 5.0,
    precision: float = 0.05,
    project_root: Path = PROJECT_ROOT,
    **config_kwargs,
) -> tuple[float, dict[str, int]]:
    """Bisekcja na font_size: znajdz najwiekszy font, ktory najdluzszy jezyk
    miesci w <= preferred_lines.

    Returns: (optymalny_font_mm, {kod_jezyka: liczba_wierszy_przy_tym_foncie}).
    """
    if not texts:
        return max_font, {}

    # Sprawdz ekstrema
    lines_at_min = count_lines_per_block(
        texts, font_size_mm=min_font, project_root=project_root, **config_kwargs
    )
    if max(lines_at_min.values()) > preferred_lines:
        # Nawet najmniejszy font nie wystarcza - zwroc min + ostrzezenie
        return min_font, lines_at_min

    lines_at_max = count_lines_per_block(
        texts, font_size_mm=max_font, project_root=project_root, **config_kwargs
    )
    if max(lines_at_max.values()) <= preferred_lines:
        # Nawet najwiekszy font sie miesci - zwroc max
        return max_font, lines_at_max

    # Bisekcja
    lo, hi = min_font, max_font
    best_font = min_font
    best_lines: dict[str, int] = lines_at_min

    while hi - lo > precision:
        mid = (lo + hi) / 2
        lines = count_lines_per_block(
            texts, font_size_mm=mid, project_root=project_root, **config_kwargs
        )
        max_lines = max(lines.values())
        if max_lines > preferred_lines:
            hi = mid  # font za duzy
        else:
            best_font = mid
            best_lines = lines
            lo = mid  # mieści się, sprobuj większy

    return round(best_font, 2), best_lines
