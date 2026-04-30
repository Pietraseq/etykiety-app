"""Branding HappyLabel: logo w headerze + tlo day/night."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).resolve().parents[2] / "assets"
LOGO_BANNER_LIGHT = ASSETS / "logo" / "happylabel-banner-light.png"
LOGO_BANNER_DARK = ASSETS / "logo" / "happylabel-banner-dark.png"
BG_DAY = ASSETS / "backgrounds" / "background-day.webp"
BG_NIGHT = ASSETS / "backgrounds" / "background-night.webp"

THEME_KEY = "ui_theme"
THEME_DAY = "day"
THEME_NIGHT = "night"
THEME_LABELS = {THEME_DAY: "Dzien", THEME_NIGHT: "Noc"}


def _b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def get_theme() -> str:
    """Aktualny motyw z session_state. Default: dzien."""
    return st.session_state.get(THEME_KEY, THEME_DAY)


def render_header() -> None:
    """Logo HappyLabel jako naglowek (banner) + toggle Dzien/Noc po prawej."""
    if THEME_KEY not in st.session_state:
        st.session_state[THEME_KEY] = THEME_DAY

    col_logo, col_caption, col_toggle = st.columns([2, 3, 1])
    with col_logo:
        theme = st.session_state[THEME_KEY]
        # logo "light" = ciemne litery na jasnym tle, logo "dark" = jasne litery na ciemnym tle
        logo_path = LOGO_BANNER_DARK if theme == THEME_NIGHT else LOGO_BANNER_LIGHT
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        else:
            st.title("HappyLabel")
    with col_caption:
        st.caption(
            "Generator wielojezycznych etykiet Happet - tekst -> AI -> SVG. "
            "Maskotka: matwa."
        )
    with col_toggle:
        st.radio(
            "Motyw",
            options=[THEME_DAY, THEME_NIGHT],
            format_func=lambda x: THEME_LABELS[x],
            key=THEME_KEY,
            horizontal=True,
            label_visibility="collapsed",
        )


def apply_background() -> None:
    """Wstawia tlo day/night przez CSS injection - zaleznie od session_state[THEME_KEY]."""
    theme = get_theme()
    bg_path = BG_NIGHT if theme == THEME_NIGHT else BG_DAY
    if not bg_path.exists():
        return
    bg = _b64(bg_path)
    if theme == THEME_NIGHT:
        overlay = "rgba(14,17,23,0.78)"
        text_override = ""
    else:
        # Mocniejszy overlay dla day, plus wymuszamy ciemny tekst zeby napisy
        # Streamlita (ktore moga byc jasne gdy theme.base=dark) byly czytelne.
        overlay = "rgba(255,255,255,0.92)"
        text_override = """
        [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] * {
            color: #1f1f1f !important;
        }
        [data-testid="stAppViewContainer"] input,
        [data-testid="stAppViewContainer"] textarea,
        [data-testid="stAppViewContainer"] select {
            background-color: rgba(255,255,255,0.85) !important;
            color: #1f1f1f !important;
        }
        """
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background:
                linear-gradient({overlay}, {overlay}),
                url("data:image/webp;base64,{bg}") center/cover fixed no-repeat;
        }}
        [data-testid="stHeader"] {{
            background: transparent;
        }}
        {text_override}
        </style>
        """,
        unsafe_allow_html=True,
    )
