"""Branding HappyLabel: logo w headerze + tlo nocne + footer 'by Pietras'."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).resolve().parents[2] / "assets"
LOGO_BANNER_DARK = ASSETS / "logo" / "happylabel-banner-dark.png"
BG_NIGHT = ASSETS / "backgrounds" / "background-night.webp"
BY_PIETRAS_DARK = ASSETS / "branding" / "by-pietras-dark.png"


def _b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def render_header() -> None:
    """Logo HappyLabel jako naglowek (banner). Tylko tryb nocny - jasny logo."""
    if LOGO_BANNER_DARK.exists():
        col_logo, _ = st.columns([2, 4])
        with col_logo:
            st.image(str(LOGO_BANNER_DARK), use_container_width=True)
    else:
        st.title("HappyLabel")


def apply_background() -> None:
    """Wstawia tlo nocne przez CSS injection."""
    if not BG_NIGHT.exists():
        return
    bg = _b64(BG_NIGHT)
    overlay = "rgba(14,17,23,0.78)"
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


def render_footer() -> None:
    """Widoczny 'by Pietras' w stopce. PNG jesli dostepny, fallback do tekstu."""
    if BY_PIETRAS_DARK.exists():
        b64 = _b64(BY_PIETRAS_DARK)
        st.markdown(
            f"""
            <div style="
                position: fixed;
                bottom: 14px;
                right: 22px;
                z-index: 999;
                opacity: 0.92;
                pointer-events: none;
                background: rgba(20, 24, 32, 0.55);
                padding: 6px 14px;
                border-radius: 8px;
                backdrop-filter: blur(4px);
            ">
                <img src="data:image/png;base64,{b64}" style="height: 36px; display: block;" />
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="
                position: fixed;
                bottom: 14px;
                right: 22px;
                z-index: 999;
                opacity: 0.92;
                font-size: 1.05rem;
                font-style: italic;
                color: #f0f0f0;
                pointer-events: none;
                background: rgba(20, 24, 32, 0.55);
                padding: 6px 14px;
                border-radius: 8px;
                backdrop-filter: blur(4px);
            ">
                by Pietras
            </div>
            """,
            unsafe_allow_html=True,
        )
