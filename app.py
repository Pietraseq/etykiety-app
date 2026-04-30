"""Streamlit entry point dla etykiety-app.

Faza A: Hello World + sanity check importu silnika etykiety-svg (submodule).
Kolejne fazy doloza UI przez moduly z src/ui/.
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


st.set_page_config(
    page_title="etykiety-app",
    page_icon=":label:",
    layout="wide",
)

st.title("etykiety-app")
st.caption("Generator wielojezycznych etykiet Happet")

if SVG_ENGINE_OK:
    st.success(f"Silnik etykiety-svg zaladowany. Obsluguje {len(DEFAULT_LANG_TO_FLAG)} jezykow.")
    with st.expander("Lista obslugiwanych jezykow"):
        cols = st.columns(5)
        for i, (lang_code, flag_code) in enumerate(DEFAULT_LANG_TO_FLAG.items()):
            cols[i % 5].markdown(f"**{lang_code}** -> flaga `{flag_code}`")
else:
    st.error(f"Silnik etykiety-svg nie zostal zaladowany: {SVG_ENGINE_ERROR}")
    st.info(
        "Sprawdz czy submodule jest zainicjalizowany:\n\n"
        "```\ngit submodule update --init --recursive\n```"
    )
    st.stop()

st.markdown("---")
st.subheader("Status MVP")
st.markdown(
    "**Faza A** (scaffold + sanity check) - **GOTOWE**\n\n"
    "Kolejne fazy:\n"
    "- Faza B: prompt template + parser odpowiedzi AI\n"
    "- Faza C: settings UI + auto-tune bisekcja font_size\n"
    "- Faza D: live preview SVG + download\n"
    "- Faza E: polish + dokumentacja dla grafika"
)
