"""Streamlit UI - sekcja ustawien layoutu + auto-tune font_size.

Po sparsowaniu tlumaczen grafik wybiera:
- Layout: 8+7 (default jak D609) / 5+5+5 / 3+3+3+3+3
- Marker: flaga (default) lub kwadracik z kodem (z color pickerem)
- Preferowana liczba wierszy (default 4)
- Zaawansowane: wymiary strony, obszaru tekstu, gutter, marker size

Aplikacja w tle uruchamia bisekcje na font_size i pokazuje:
- Optymalny font_size [mm]
- Tabele 'wiersze per jezyk' (ktorzy mieszcza sie a ktorzy wylewaja)
"""

from __future__ import annotations

import streamlit as st

from src.logic.prompt_template import LANGUAGES
from src.logic.tuner import find_optimal_font

LAYOUT_CHOICES = ["8+7", "5+5+5", "3+3+3+3+3"]
MARKER_STYLES = ["flag_circle", "text_rect"]
MARKER_LABELS = {
    "flag_circle": "Flaga w kolku (jak HappSnack)",
    "text_rect": "Skrot kraju + kolorowy kwadracik",
}


def render_settings_section(translations: dict[str, str]) -> dict | None:
    """Render sekcji ustawien + auto-tune. Zwraca dict z parametrami do Fazy D."""
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
            min_value=2,
            max_value=10,
            value=4,
            help="Najdluzszy jezyk nie przekroczy tej liczby. Aplikacja dobierze font_size.",
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

    with st.expander("Zaawansowane (wymiary strony, obszaru tekstu)"):
        col_a, col_b = st.columns(2)
        with col_a:
            page_w = st.number_input("Szerokosc strony (mm)", value=219.96, min_value=50.0)
            text_area_w = st.number_input("Szerokosc obszaru tekstu (mm)", value=100.0, min_value=20.0)
            gutter = st.number_input("Odstep miedzy kolumnami (mm)", value=3.0, min_value=0.0)
        with col_b:
            page_h = st.number_input("Wysokosc strony (mm)", value=160.10, min_value=30.0)
            text_area_h = st.number_input("Wysokosc obszaru tekstu (mm)", value=145.0, min_value=20.0)
            marker_size = st.number_input(
                "Rozmiar markera (mm)", value=2.6, min_value=1.0, max_value=10.0
            )

    # Auto-tune
    st.subheader("6. Auto-dostrojenie font_size")

    config_kwargs = {
        "layout_name": layout,
        "page_size": (float(page_w), float(page_h)),
        "text_area_size": (float(text_area_w), float(text_area_h)),
        "gutter_mm": float(gutter),
        "marker_size_mm": float(marker_size),
        "marker_style": marker_style,
        "marker_color": marker_color,
    }

    with st.spinner("Bisekcja na font_size (~1-2 sek)..."):
        try:
            optimal_font, lines_per_lang = find_optimal_font(
                translations, int(preferred_lines), **config_kwargs
            )
        except Exception as e:
            st.error(f"Bisekcja nie powiodla sie: {e}")
            return None

    max_lines = max(lines_per_lang.values()) if lines_per_lang else 0

    if max_lines > preferred_lines:
        st.error(
            f"Tekst zbyt dlugi - nawet przy foncie {optimal_font:.2f}mm "
            f"najdluzszy jezyk ma {max_lines} wierszy. "
            f"Skroc tekst albo zwieksz wysokosc obszaru tekstu."
        )
    else:
        st.success(
            f"Optymalny font: **{optimal_font:.2f} mm** "
            f"(najdluzszy jezyk ma {max_lines} wierszy z {preferred_lines} preferowanych)"
        )

    # Tabela wierszy per jezyk
    st.markdown("**Wiersze per jezyk:**")
    cols = st.columns(5)
    sorted_lines = sorted(lines_per_lang.items(), key=lambda x: -x[1])
    for i, (code, lines) in enumerate(sorted_lines):
        col = cols[i % 5]
        delta = lines - preferred_lines
        if delta > 0:
            col.metric(code, str(lines), delta=f"+{delta}", delta_color="inverse")
        else:
            col.metric(code, str(lines))

    return {
        "translations": translations,
        "layout": layout,
        "marker_style": marker_style,
        "marker_color": marker_color,
        "preferred_lines": int(preferred_lines),
        "optimal_font_mm": optimal_font,
        "lines_per_lang": lines_per_lang,
        **config_kwargs,
    }
