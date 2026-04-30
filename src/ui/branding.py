"""Branding HappyLabel: logo w headerze + tlo day/night zsynchronizowane z theme."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).resolve().parents[2] / "assets"
LOGO_BANNER_LIGHT = ASSETS / "logo" / "happylabel-banner-light.png"
LOGO_BANNER_DARK = ASSETS / "logo" / "happylabel-banner-dark.png"
BG_DAY = ASSETS / "backgrounds" / "background-day.webp"
BG_NIGHT = ASSETS / "backgrounds" / "background-night.webp"


def _detect_theme() -> str:
    """Zwraca 'dark' albo 'light'. Default 'light' gdy nie da sie wykryc."""
    try:
        ctx_theme = getattr(st.context, "theme", None)
        if ctx_theme is not None:
            value = getattr(ctx_theme, "type", None) or getattr(ctx_theme, "base", None)
            if isinstance(value, str) and value.lower() in {"dark", "light"}:
                return value.lower()
    except Exception:
        pass
    base = st.get_option("theme.base")
    if isinstance(base, str) and base.lower() == "dark":
        return "dark"
    return "light"


def _b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def render_header() -> None:
    """Logo HappyLabel jako naglowek (banner). Wybiera wariant pod theme."""
    theme = _detect_theme()
    logo_path = LOGO_BANNER_DARK if theme == "dark" else LOGO_BANNER_LIGHT
    if not logo_path.exists():
        st.title("HappyLabel")
        return
    col_logo, col_caption = st.columns([1, 2])
    with col_logo:
        st.image(str(logo_path), use_container_width=True)
    with col_caption:
        st.caption(
            "Generator wielojezycznych etykiet Happet - tekst -> AI -> SVG. "
            "Maskotka: matwa."
        )


def apply_background() -> None:
    """Wstawia tlo day/night przez CSS injection. Theme-aware."""
    theme = _detect_theme()
    bg_path = BG_NIGHT if theme == "dark" else BG_DAY
    if not bg_path.exists():
        return
    bg = _b64(bg_path)
    overlay = "rgba(14,17,23,0.78)" if theme == "dark" else "rgba(255,255,255,0.82)"
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
        </style>
        """,
        unsafe_allow_html=True,
    )
