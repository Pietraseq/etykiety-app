"""Streamlit UI - sekcja BASIC ustawien (layout, marker, preferred_lines).

Zaawansowane (rozmiar etykiety, obszar tekstu, odstepy, marker_size) sa w
preview.py side-by-side z podgladem SVG - zeby Pietras widzial efekt zmian
od razu.
"""

from __future__ import annotations

import streamlit as st

from src.logic.prompt_template import LANGUAGES

LAYOUT_CHOICES = ["8+7", "5+5+5", "3+3+3+3+3"]
MARKER_STYLES = ["flag_circle", "text_rect"]
MARKER_LABELS = {
    "flag_circle": "Flaga w kolku (jak HappSnack)",
    "text_rect": "Skrot kraju + kolorowy kwadracik",
}


def render_basic_settings(translations: dict[str, str]) -> dict | None:
    """Render basic settings (layout, marker, preferred_lines).

    Zwraca dict albo None gdy brak 15 jezykow.
    """
    if not translations or len(translations) < 15:
        st.info(
            f"Wymagane wszystkie 15 jezykow do dostrojenia layoutu "
            f"({len(translations)}/15 wypelnionych)."
        )
        return None

    st.subheader("5. Ustawienia layoutu")

    col1, col2, col3 = st.columns(3)
    with col1:
        layout = st.radio(
            "Layout",
            options=LAYOUT_CHOICES,
            index=0,
            help="8+7 - 2 kolumny jak D609; 5+5+5 - 3 kolumny wezsze; 3+3+3+3+3 - 5 najwezszych",
            key="layout_choice",
        )
    with col2:
        marker_style = st.radio(
            "Styl markera",
            options=MARKER_STYLES,
            format_func=lambda x: MARKER_LABELS[x],
            index=0,
            key="marker_style_choice",
        )
    with col3:
        preferred_lines = st.number_input(
            "Preferowana liczba wierszy",
            min_value=1,
            max_value=10,
            value=4,
            help="Najdluzszy jezyk nie przekroczy tej liczby. "
            "Wartosc 1 = sama nazwa produktu (krotki tekst).",
            key="preferred_lines",
        )
        if marker_style == "text_rect":
            marker_color = st.color_picker(
                "Kolor kwadracika",
                value="#E60000",
                key="marker_color_pick",
            )
        else:
            marker_color = "#E60000"

    return {
        "translations": translations,
        "layout": layout,
        "marker_style": marker_style,
        "marker_color": marker_color,
        "preferred_lines": int(preferred_lines),
    }
