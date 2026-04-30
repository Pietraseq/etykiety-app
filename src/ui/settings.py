"""Streamlit UI - sekcja ustawien layoutu + auto-tune font_size.

Pietras chce:
- preferred_lines od 1 (sama nazwa produktu)
- 15 wierszy per jezyk w pionie z color-coded statusem (✓ / ⚠️)
- Banner "etykieta niemozliwa" gdy nawet min font nie pomieści tekstu
- Uproszczone Zaawansowane: rozmiar etykiety + obszar tekstu + odstep miedzy jezykami
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
            min_value=1,
            max_value=10,
            value=4,
            help="Najdluzszy jezyk nie przekroczy tej liczby. Aplikacja dobierze font_size. "
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

    with st.expander("Zaawansowane (rozmiar etykiety + obszar tekstu + odstepy)"):
        st.caption(
            "Etykieta to fizyczny rozmiar opakowania. Obszar tekstu to czesc "
            "etykiety zostawiona dla bloków językowych - reszta na ikony, logo, "
            "kod kreskowy, kod produktu (rysowane przez grafika)."
        )
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Rozmiar etykiety**")
            page_w = st.number_input("Szerokosc (mm)", value=219.96, min_value=50.0, key="page_w")
            page_h = st.number_input("Wysokosc (mm)", value=160.10, min_value=30.0, key="page_h")
        with col_b:
            st.markdown("**Obszar dla tekstu**")
            text_area_w = st.number_input("Szerokosc (mm)", value=100.0, min_value=20.0, key="ta_w")
            text_area_h = st.number_input("Wysokosc (mm)", value=145.0, min_value=20.0, key="ta_h")

        col_c, col_d, col_e = st.columns(3)
        with col_c:
            gutter = st.number_input(
                "Odstep miedzy kolumnami (mm)",
                value=3.0,
                min_value=0.0,
                step=0.5,
                key="gutter",
            )
        with col_d:
            inter_gap = st.number_input(
                "Odstep miedzy jezykami (mm)",
                value=0.0,
                min_value=0.0,
                step=0.2,
                help="0 = auto z fontu (ciaśniej dla małego, luźniej dla dużego). "
                "Wartosc > 0 nadpisuje (zageszcza/rozluznia uklad).",
                key="inter_gap",
            )
        with col_e:
            marker_override = st.number_input(
                "Rozmiar markera (mm)",
                value=0.0,
                min_value=0.0,
                max_value=10.0,
                step=0.1,
                help="0 = auto z fontu (= line_height). >0 = override.",
                key="marker_override",
            )

    st.subheader("6. Auto-dostrojenie font_size")

    config_kwargs = {
        "layout_name": layout,
        "page_size": (float(page_w), float(page_h)),
        "text_area_size": (float(text_area_w), float(text_area_h)),
        "gutter_mm": float(gutter),
        "marker_size_mm": float(marker_override) if marker_override > 0 else None,
        "marker_style": marker_style,
        "marker_color": marker_color,
        "inter_block_gap_mm": float(inter_gap) if inter_gap > 0 else None,
    }

    with st.spinner("Bisekcja na font_size..."):
        try:
            optimal_font, lines_per_lang = find_optimal_font(
                translations, int(preferred_lines), **config_kwargs
            )
        except Exception as e:
            st.error(f"Bisekcja nie powiodla sie: {e}")
            return None

    max_lines = max(lines_per_lang.values()) if lines_per_lang else 0

    # ETYKIETA NIEMOZLIWA - duzy banner
    if max_lines > preferred_lines:
        st.error(
            f"### ⚠️ Etykieta niemozliwa do zrobienia\n\n"
            f"Nawet przy najmniejszym foncie ({optimal_font:.2f} mm) najdluzszy "
            f"jezyk ma **{max_lines} wierszy** zamiast preferowanych {preferred_lines}. "
            f"Mozliwe rozwiazania:\n"
            f"- Skroc tekst zrodlowy (sekcja 1)\n"
            f"- Zwieksz wysokosc obszaru tekstu (Zaawansowane)\n"
            f"- Zwieksz preferowana liczbe wierszy\n"
            f"- Wybierz wezszy layout (np. 5+5+5 zamiast 8+7)"
        )
    else:
        st.success(
            f"Optymalny font: **{optimal_font:.2f} mm** "
            f"(najdluzszy jezyk ma {max_lines} z {preferred_lines} preferowanych wierszy)"
        )

    # Lista 15 jezykow w pionie z color-coded statusem
    st.markdown("**Wiersze per jezyk** (zielony = zgodny z preferowanym; pomaranczowy = wieksze):")
    for code in LANGUAGES:
        lines = lines_per_lang.get(code, 0)
        if lines == preferred_lines or (lines < preferred_lines and lines > 0):
            # OK - mniej lub rowno
            icon = "🟢" if lines == preferred_lines else "🟡"
            st.markdown(
                f"{icon} **{code}** — {lines} wierszy"
                + (f" (-{preferred_lines - lines})" if lines < preferred_lines else "")
            )
        elif lines > preferred_lines:
            st.markdown(f"🔴 **{code}** — {lines} wierszy (+{lines - preferred_lines} ponad limit)")
        else:
            st.markdown(f"⚫ **{code}** — brak danych")

    return {
        "translations": translations,
        "layout": layout,
        "marker_style": marker_style,
        "marker_color": marker_color,
        "preferred_lines": int(preferred_lines),
        "optimal_font_mm": optimal_font,
        "lines_per_lang": lines_per_lang,
        "is_feasible": max_lines <= preferred_lines,
        **config_kwargs,
    }
