"""Stale dla layoutu, markera i toggle justify - uzywane w preview.py.

Po refactorze nie ma juz osobnej sekcji 5 - layout, marker, preferred_lines
i justify trafily do panelu po lewej obok podgladu (sekcja 6 w preview.py),
zeby grafik nie musial scrollowac gora-dol miedzy ustawieniami a podgladem.
"""

from __future__ import annotations

LAYOUT_CHOICES = ["8+7", "5+5+5", "3+3+3+3+3", "15"]
LAYOUT_LABELS = {
    "8+7": "8 + 7 (dwie kolumny)",
    "5+5+5": "5 + 5 + 5 (trzy kolumny)",
    "3+3+3+3+3": "3 + 3 + 3 + 3 + 3 (pięć kolumn)",
    "15": "15 (jedna kolumna, wszystkie pod sobą)",
}
MARKER_STYLES = ["flag_circle", "text_rect"]
MARKER_LABELS = {
    "flag_circle": "Flaga w kółku",
    "text_rect": "Skrót kraju + kolorowy kwadracik",
}

JUSTIFY_FULL_LABEL = "Wyjustowany na całą szerokość kolumny"
JUSTIFY_RAGGED_LABEL = "Wyrównany do lewej (bez justyfikacji)"
