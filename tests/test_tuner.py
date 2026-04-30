"""Pytest dla tunera - bisekcja font_size."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Dodaj submodule do path (jak w app.py)
SUBMODULE_SRC = Path(__file__).resolve().parents[1] / "etykiety_svg" / "src"
if str(SUBMODULE_SRC) not in sys.path:
    sys.path.insert(0, str(SUBMODULE_SRC))

from src.logic.tuner import (
    build_column_split,
    count_lines_per_block,
    find_optimal_font,
)
from src.logic.prompt_template import LANGUAGES


# Realny fixture - 15 jezykow D609 (skrocone)
D609_TEXTS = {
    "EN": "Single-use, oxygen-activated heat pack. For transporting animals and plants in cold days. Directions for use: Remove from foil, shake and place in the package.",
    "PL": "Jednorazowy, aktywowany tlenem ogrzewacz. Do transportu zwierząt i roślin w chłodne dni. Sposób użycia: Wyjąć z folii, potrząsnąć i umieścić w paczce.",
    "UK": "Одноразовий, активований киснем обігрівач. Для транспортування тварин і рослин у холодні дні. Спосіб використання: Вийняти з фольги, струсити та помістити в посилку.",
    "RO": "Încălzitor de unică folosință, activat cu oxigen. Pentru transportul animalelor și plantelor în zilele reci. Mod de utilizare: Scoateți din folie, agitați și introduceți în pachet.",
    "DE": "Einweg-, sauerstoffaktivierter Wärmer. Für den Transport von Tieren und Pflanzen an kalten Tagen. Anwendung: Aus der Folie nehmen, schütteln und in das Paket legen.",
    "HU": "Egyszer használatos, oxigénnel aktivált melegítő. Állatok és növények szállításához hideg napokon. Használat: Vegye ki a fóliából, rázza fel és helyezze a csomagba.",
    "LT": "Vienkartinis, deguonimi aktyvuojamas šildytuvas. Gyvūnų ir augalų transportavimui šaltomis dienomis. Naudojimas: Išimti iš folijos, pakratyti ir įdėti į siuntą.",
    "SK": "Jednorazový, kyslíkom aktivovaný ohrievač. Na prepravu zvierat a rastlín v chladných dňoch. Spôsob použitia: Vybrať z fólie, potriasť a vložiť do balíka.",
    "CZ": "Jednorázový, kyslíkem aktivovaný ohřívač. Pro přepravu zvířat a rostlin v chladných dnech. Způsob použití: Vyjmout z fólie, protřepat a vložit do balíku.",
    "IT": "Riscaldatore monouso attivato dall'ossigeno. Per il trasporto di animali e piante nelle giornate fredde. Modalità d'uso: Rimuovere dalla pellicola, agitare e inserire nel pacco.",
    "ES": "Calentador de un solo uso activado por oxígeno. Para el transporte de animales y plantas en días fríos. Modo de uso: Sacar de la bolsa, agitar y colocar en el paquete.",
    "GR": "Θερμαντικό μίας χρήσης, ενεργοποιούμενο με οξυγόνο. Για τη μεταφορά ζώων και φυτών σε κρύες ημέρες. Τρόπος χρήσης: Αφαιρέστε από το φύλλο, ανακινήστε και τοποθετήστε στο δέμα.",
    "FR": "Chauffe-main à usage unique activé par l'oxygène. Pour le transport des animaux et des plantes par temps froid. Mode d'emploi: Retirer du film, secouer et placer dans le colis.",
    "PT": "Aquecedor descartável ativado por oxigênio. Para o transporte de animais e plantas em dias frios. Modo de uso: Retirar da embalagem, agitar e colocar na encomenda.",
    "RU": "Одноразовый, активируемый кислородом обогреватель. Для транспортировки животных и растений в холодные дни. Способ применения: Достать из упаковки, встряхнуть и поместить в посылку.",
}


def test_column_split_8_7():
    cols = build_column_split("8+7")
    assert len(cols) == 2
    assert len(cols[0]) == 8
    assert len(cols[1]) == 7
    assert cols[0] == ["EN", "PL", "UK", "RO", "DE", "HU", "LT", "SK"]
    assert cols[1] == ["CZ", "IT", "ES", "GR", "FR", "PT", "RU"]


def test_column_split_5_5_5():
    cols = build_column_split("5+5+5")
    assert len(cols) == 3
    assert all(len(c) == 5 for c in cols)


def test_column_split_3_3_3_3_3():
    cols = build_column_split("3+3+3+3+3")
    assert len(cols) == 5
    assert all(len(c) == 3 for c in cols)


def test_column_split_invalid():
    with pytest.raises(ValueError):
        build_column_split("nonsense")


def test_count_lines_d609_default_font():
    """Sanity: D609 z domyslnymi parametrami (font 2.2mm) ma 4-5 wierszy per blok."""
    lines = count_lines_per_block(D609_TEXTS, font_size_mm=2.2)
    assert len(lines) == 15
    assert all(1 <= n <= 8 for n in lines.values())  # rozsadny zakres
    # UK i RU najdluzsze - powinny miec >= 4 linii przy font 2.2
    assert lines["UK"] >= 4
    assert lines["RU"] >= 4


def test_count_lines_smaller_font_fewer_lines():
    """Mniejszy font = mniej wierszy na blok."""
    lines_small = count_lines_per_block(D609_TEXTS, font_size_mm=1.5)
    lines_large = count_lines_per_block(D609_TEXTS, font_size_mm=3.0)
    avg_small = sum(lines_small.values()) / 15
    avg_large = sum(lines_large.values()) / 15
    assert avg_large > avg_small  # wiekszy font => wiecej wierszy


def test_find_optimal_font_basic():
    """Auto-tune: dla preferred=4 znajdzie sensowny font."""
    optimal, lines = find_optimal_font(D609_TEXTS, preferred_lines=4)
    assert 1.0 <= optimal <= 5.0
    assert max(lines.values()) <= 4
    # font powinien byc rozsadny - nie min, nie max ekstremum
    assert 1.5 <= optimal <= 4.0


def test_find_optimal_font_small_preferred():
    """Auto-tune dla preferred=3 - mniejszy font niz dla preferred=5."""
    font_3, _ = find_optimal_font(D609_TEXTS, preferred_lines=3)
    font_5, _ = find_optimal_font(D609_TEXTS, preferred_lines=5)
    assert font_5 > font_3  # wiecej wierszy = wiekszy font


def test_find_optimal_font_max_lines_respected():
    """Najdluzszy jezyk ma <= preferred_lines."""
    for preferred in [3, 4, 5, 6]:
        _, lines = find_optimal_font(D609_TEXTS, preferred_lines=preferred)
        assert max(lines.values()) <= preferred, (
            f"Dla preferred={preferred}: max lines = {max(lines.values())}"
        )


def test_find_optimal_font_short_text():
    """Dla bardzo krotkiego tekstu - max font (5.0mm)."""
    short = {code: "Hi" for code in LANGUAGES}
    optimal, lines = find_optimal_font(short, preferred_lines=4)
    assert optimal >= 4.5  # bliski max bo tekst krotki
    assert all(n == 1 for n in lines.values())  # 1 linia per jezyk


def test_find_optimal_font_layout_changes_result():
    """Inny layout = inne column_w = inny font dla tej samej preferred_lines."""
    font_8_7, _ = find_optimal_font(D609_TEXTS, preferred_lines=4, layout_name="8+7")
    font_5_5_5, _ = find_optimal_font(D609_TEXTS, preferred_lines=4, layout_name="5+5+5")
    # 5+5+5 = wezsze kolumny = mniejszy font dla tego samego preferred
    assert font_5_5_5 < font_8_7
