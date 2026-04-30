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

# Faza C/D - settings + preview - placeholder
st.markdown("---")
st.subheader("5. Ustawienia layoutu (Faza C - WIP)")
st.info(
    "Tu beda: layout (8+7 / 5+5+5 / 3+3+3+3+3), styl markera "
    "(flaga / skrot z kolorem), preferowana liczba wierszy, auto-tune font."
)

st.subheader("6. Podglad i pobranie SVG (Faza D - WIP)")
if translations:
    st.success(f"Stan: {len(translations)} jezykow gotowych do generacji.")
    with st.expander(f"Debug - sparsowane {len(translations)} jezykow"):
        st.json(translations)
else:
    st.info("Wklej odpowiedz AI w sekcji 3 zeby zobaczyc dane do generacji.")
