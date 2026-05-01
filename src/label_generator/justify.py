"""Greedy line break + justyfikacja przez `word-spacing` (a nie per-slowo X).

Zwraca per linie:
- text: pelna tresc linii jako string
- word_spacing_mm: extra ponad naturalna szerokosc spacji (tyle dodajemy do
  kazdej spacji zeby linia wypelnila kolumne)
- x_mm: pozycja x poczatku linii (po flagi dla 1. linii, 0 dla outdent linii 2+)
- is_last: czy to ostatnia linia akapitu (ragged-right, brak word-spacing)

Output trafia do svg_writer ktory generuje JEDNO <text> per blok z N <tspan>
per linia. Cap stretch ratio: gdy spacje musialyby byc wieksze niz N x naturalna,
zostawiamy linie nie-justyfikowana (ragged) zamiast brzydko rozjechac.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .hyphenation import Hyphenator
from .text_metrics import FontMetrics


@dataclass
class Line:
    """Linia tekstu - tekst + word-spacing + x-offset."""

    text: str
    word_spacing_mm: float
    x_mm: float
    is_last: bool
    width_mm: float


def wrap_and_justify(
    text: str,
    line_widths_mm: list[float],
    font: FontMetrics,
    hyphenator: Optional[Hyphenator] = None,
    max_stretch_ratio: float = 1.5,
    justify_full: bool = True,
) -> list[Line]:
    """Lamie tekst na linie i liczy word-spacing dla kazdej.

    `justify_full=True` (default): justyfikacja przez word-spacing, ostatnia
    linia ragged-right. `justify_full=False`: wszystkie linie ragged-right
    (bez extra word-spacing, tekst wyrownany do lewej krawedzi kolumny).
    """
    words = text.split()
    if not words:
        return []

    word_widths = [font.text_width(w) for w in words]
    space_w = font.space_width()

    # Greedy wrap - wybor slow per linia
    lines_indices: list[list[int]] = []
    i = 0
    line_idx = 0
    while i < len(words):
        max_w = _line_width(line_widths_mm, line_idx)
        chosen: list[int] = []
        used = 0.0
        while i < len(words):
            w = word_widths[i]
            extra = w if not chosen else (space_w + w)
            if used + extra <= max_w:
                chosen.append(i)
                used += extra
                i += 1
            else:
                if not chosen and hyphenator is not None:
                    split = _find_hyphen_split(
                        words[i], word_widths[i], max_w - used, font, hyphenator
                    )
                    if split is not None:
                        left_part, right_part = split
                        words[i] = right_part
                        word_widths[i] = font.text_width(right_part)
                        words.insert(i, left_part)
                        word_widths.insert(i, font.text_width(left_part))
                        chosen.append(i)
                        used += word_widths[i]
                        i += 1
                        break
                if not chosen:
                    chosen.append(i)
                    used += w
                    i += 1
                break
        lines_indices.append(chosen)
        line_idx += 1

    result: list[Line] = []
    for li, indices in enumerate(lines_indices):
        is_last = li == len(lines_indices) - 1
        max_w = _line_width(line_widths_mm, li)
        line_words = [words[idx] for idx in indices]
        line_widths_chars = [word_widths[idx] for idx in indices]

        if not line_words:
            continue

        text_str = " ".join(line_words)
        n_words = len(line_words)
        sum_words = sum(line_widths_chars)
        x_mm = 0.0  # pozycja relatywna do bloku - svg_writer dorzuca offset 1. linii

        if is_last or n_words == 1 or not justify_full:
            word_spacing = 0.0
            natural_width = sum_words + max(0, n_words - 1) * space_w
            result.append(
                Line(
                    text=text_str,
                    word_spacing_mm=0.0,
                    x_mm=x_mm,
                    is_last=is_last,
                    width_mm=natural_width,
                )
            )
            continue

        n_spaces = n_words - 1
        natural_total = sum_words + n_spaces * space_w
        slack = max_w - natural_total
        if slack <= 0:
            word_spacing = 0.0
        else:
            extra_per_space = slack / n_spaces
            stretch_ratio = (space_w + extra_per_space) / space_w
            if stretch_ratio > max_stretch_ratio:
                word_spacing = 0.0
            else:
                word_spacing = extra_per_space

        result.append(
            Line(
                text=text_str,
                word_spacing_mm=round(word_spacing, 4),
                x_mm=x_mm,
                is_last=False,
                width_mm=max_w,
            )
        )

    return result


def _line_width(widths: list[float], line_idx: int) -> float:
    if line_idx < len(widths):
        return widths[line_idx]
    return widths[-1]


def _find_hyphen_split(
    word: str,
    word_width: float,
    available_mm: float,
    font: FontMetrics,
    hyphenator: Hyphenator,
) -> Optional[tuple[str, str]]:
    candidates = hyphenator.split_pairs(word)
    if not candidates:
        return None
    best = None
    for left, right in candidates:
        if font.text_width(left) <= available_mm:
            best = (left, right)
    return best
