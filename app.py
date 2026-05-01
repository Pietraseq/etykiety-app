"""Streamlit entry point dla etykiety-app.

Faza A: scaffold + sanity check importu silnika etykiety-svg.
Faza B: prompt + parser + UI tłumaczenia (15 textarea).
Kolejne fazy: settings, auto-tune, podgląd, download.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Silnik renderowania SVG (label_generator) jest vendor-owany w src/.
# Dodajemy src/ do sys.path zeby `from label_generator.X` dzialalo top-level
# (kod silnika nie zna struktury aplikacji - traktuje siebie jako root pakiet).
ENGINE_SRC = Path(__file__).parent / "src"
if ENGINE_SRC.exists() and str(ENGINE_SRC) not in sys.path:
    sys.path.insert(0, str(ENGINE_SRC))

import streamlit as st

try:
    from label_generator.config import LabelConfig  # noqa: F401
    from label_generator.flags import DEFAULT_LANG_TO_FLAG
    SVG_ENGINE_OK = True
    SVG_ENGINE_ERROR = ""
except ImportError as e:
    SVG_ENGINE_OK = False
    SVG_ENGINE_ERROR = str(e)
    DEFAULT_LANG_TO_FLAG = {}

from src.ui.translate import render_translate_section
from src.ui.preview import render_combined_section
from src.ui.branding import apply_background, render_footer, render_header


st.set_page_config(
    page_title="HappyLabel",
    page_icon=str((Path(__file__).parent / "assets" / "logo" / "happylabel-square-light.png").resolve()),
    layout="wide",
)

apply_background()
render_header()

if not SVG_ENGINE_OK:
    st.error(
        f"Silnik renderowania SVG (`label_generator`) nie został załadowany.\n\n"
        f"**Szczegóły błędu:** `{SVG_ENGINE_ERROR}`"
    )
    st.markdown(
        "Sprawdź czy katalog `src/label_generator/` zawiera pełen kod silnika "
        "(layout.py, svg_writer.py, config.py i pozostałe). Jeśli brakuje plików — "
        "ponownie sklonuj repo."
    )
    st.stop()

try:
    translations = render_translate_section()

    st.markdown("---")
    render_combined_section(translations)
except Exception as e:
    st.error(
        "**Wystąpił nieoczekiwany błąd aplikacji.**\n\n"
        f"Szczegóły: `{type(e).__name__}: {e}`\n\n"
        "Spróbuj odświeżyć stronę. Jeśli błąd się powtarza — zgłoś go z treścią powyżej."
    )
    st.exception(e)
    st.stop()

render_footer()
