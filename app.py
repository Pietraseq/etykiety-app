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
from src.ui.settings import render_settings_section


st.set_page_config(
    page_title="etykiety-app",
    page_icon=":label:",
    layout="wide",
)

st.title("etykiety-app")
st.caption("Generator wielojezycznych etykiet Happet - tekst -> AI -> SVG")

if not SVG_ENGINE_OK:
    st.error(f"Silnik etykiety-svg nie zaladowany: {SVG_ENGINE_ERROR}")
    st.code("git submodule update --init --recursive", language="bash")
    st.stop()

# Sekcja: tlumaczenie przez prompt do AI -> 15 textarea
translations = render_translate_section()

# Sekcja: ustawienia + auto-tune
st.markdown("---")
generation_params = render_settings_section(translations)

# Faza D - preview + download - placeholder
st.markdown("---")
st.subheader("7. Podglad i pobranie SVG (Faza D - WIP)")
if generation_params:
    st.info(
        "Tu bedzie: live preview SVG + przycisk download. "
        "Aktualnie gotowe parametry generacji (debug)."
    )
    with st.expander("Debug - parametry generacji"):
        # Pomijamy translations w widoku zeby nie zaspamowac
        params_view = {k: v for k, v in generation_params.items() if k != "translations"}
        st.json(params_view)
else:
    st.info("Uzupelnij sekcje 1-3 (15 jezykow) zeby aktywowac generacje.")
