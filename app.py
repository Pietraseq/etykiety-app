"""Streamlit entry point dla etykiety-app.

Faza A: scaffold + sanity check importu silnika etykiety-svg.
Faza B: prompt + parser + UI tlumaczenia (15 textarea).
Kolejne fazy: settings, auto-tune, preview, download.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Submodule etykiety_svg dostarcza silnik renderowania SVG
SUBMODULE_SRC = Path(__file__).parent / "etykiety_svg" / "src"
if SUBMODULE_SRC.exists() and str(SUBMODULE_SRC) not in sys.path:
    sys.path.insert(0, str(SUBMODULE_SRC))

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
from src.ui.settings import render_basic_settings
from src.ui.preview import render_combined_section
from src.ui.branding import apply_background, render_header


st.set_page_config(
    page_title="HappyLabel",
    page_icon=str((Path(__file__).parent / "assets" / "logo" / "happylabel-square-light.png").resolve()),
    layout="wide",
)

apply_background()
render_header()

if not SVG_ENGINE_OK:
    st.error(f"Silnik etykiety-svg nie zaladowany: {SVG_ENGINE_ERROR}")
    st.code("git submodule update --init --recursive", language="bash")
    st.stop()

# Sekcje 1-3: tlumaczenie przez prompt do AI -> 15 textarea
translations = render_translate_section()

# Sekcja 5: BASIC settings (layout, marker, preferred_lines)
st.markdown("---")
basic_params = render_basic_settings(translations)

# Sekcja 6: zaawansowane + live preview side-by-side
st.markdown("---")
render_combined_section(basic_params)
