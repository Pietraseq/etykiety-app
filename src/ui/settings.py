"""Streamlit UI - sekcja BASIC ustawien (layout, marker, preferred_lines, justify).

Zaawansowane (rozmiar etykiety, obszar tekstu, odstepy, marker_size) sa w
preview.py side-by-side z podgladem SVG - zeby Pietras widzial efekt zmian
od razu.
"""

from __future__ import annotations

import streamlit as st

from src.logic.prompt_template import LANGUAGES

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


def render_basic_settings(translations: dict[str, str]) -> dict | None:
    """Render basic settings (layout, marker, preferred_lines, justify).

    Zwraca dict albo None gdy brak 15 języków.
    """
    if not translations or len(translations) < 15:
        st.info(
            f"Wymagane wszystkie 15 języków do dostrojenia layoutu "
            f"({len(translations)}/15 wypełnionych)."
        )
        return None

    st.subheader("5. Ustawienia layoutu")

    col1, col2 = st.columns(2)
    with col1:
        layout = st.radio(
            "Layout",
            options=LAYOUT_CHOICES,
            format_func=lambda x: LAYOUT_LABELS[x],
            index=0,
            help="Im więcej kolumn, tym węższe bloki tekstu i więcej linii w bloku.",
            key="layout_choice",
        )
    with col2:
        marker_style = st.radio(
            "Styl markera (znacznika języka)",
            options=MARKER_STYLES,
            format_func=lambda x: MARKER_LABELS[x],
            index=0,
            key="marker_style_choice",
        )
        if marker_style == "text_rect":
            marker_color = st.color_picker(
                "Kolor kwadracika",
                value="#E60000",
                key="marker_color_pick",
            )
        else:
            marker_color = "#E60000"

    st.markdown("#### Preferowana liczba wierszy w bloku")
    pl_col1, pl_col2 = st.columns([3, 2])
    with pl_col1:
        preferred_lines = st.slider(
            "Liczba wierszy",
            min_value=1,
            max_value=10,
            value=int(st.session_state.get("preferred_lines", 4)),
            step=1,
            key="preferred_lines",
            label_visibility="collapsed",
            help=(
                "Najdłuższy język nie przekroczy tej liczby wierszy. "
                "Aplikacja dobierze największy font, który to gwarantuje."
            ),
        )
    with pl_col2:
        st.markdown(
            f"<div style='font-size: 1.6rem; font-weight: 600; line-height: 1.1; "
            f"padding-top: 4px;'>{preferred_lines} "
            f"{'wiersz' if preferred_lines == 1 else 'wiersze' if 2 <= preferred_lines <= 4 else 'wierszy'}"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("#### Formatowanie tekstu")
    justify_choice = st.radio(
        "Sposób wyrównania linii w bloku",
        options=[JUSTIFY_FULL_LABEL, JUSTIFY_RAGGED_LABEL],
        index=0,
        key="justify_choice",
        horizontal=True,
        help=(
            "Wyjustowany: linie wypełniają całą szerokość kolumny przez rozszerzenie spacji. "
            "Wyrównany do lewej: linie naturalnej długości, bez rozszerzania spacji."
        ),
    )
    justify_full = justify_choice == JUSTIFY_FULL_LABEL

    return {
        "translations": translations,
        "layout": layout,
        "marker_style": marker_style,
        "marker_color": marker_color,
        "preferred_lines": int(preferred_lines),
        "justify_full": justify_full,
    }
