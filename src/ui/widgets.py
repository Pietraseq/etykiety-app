"""Streamlit helpery do reuzywania - dual_input (slider + number_input synced)
oraz js_copy_button (clipboard przez JS, dziala lokalnie i na Streamlit Cloud)."""

from __future__ import annotations

import json

import streamlit as st
import streamlit.components.v1 as components


def js_copy_button(text: str, label: str = "Skopiuj prompt", height: int = 50) -> None:
    """Przycisk copy oparty o JavaScript - dziala wszedzie (lokalnie + chmura).

    Uzywa klasycznego trick z document.execCommand('copy') na schowanym
    textarea - zawsze dostepne, nie wymaga pozwolen iframe ani HTTPS context.
    Zastapuje pyperclip ktore na Streamlit Cloud (Linux runtime bez X11) failuje.
    """
    safe = json.dumps(text)
    components.html(
        f"""
        <button id="copy-btn" onclick="
            const ta = document.createElement('textarea');
            ta.value = {safe};
            ta.style.position = 'fixed';
            ta.style.opacity = '0';
            ta.style.top = '0';
            ta.style.left = '0';
            document.body.appendChild(ta);
            ta.select();
            try {{
                document.execCommand('copy');
                this.innerText = 'Skopiowano ✓';
                this.style.background = '#16a34a';
            }} catch(e) {{
                this.innerText = 'Blad kopiowania';
                this.style.background = '#dc2626';
            }}
            document.body.removeChild(ta);
            setTimeout(() => {{
                this.innerText = '{label}';
                this.style.background = '#ff4b4b';
            }}, 2000);
        " style="
            background: #ff4b4b;
            color: white;
            border: none;
            padding: 0.55rem 1rem;
            border-radius: 0.5rem;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 500;
            width: 100%;
            font-family: 'Source Sans Pro', sans-serif;
        ">{label}</button>
        """,
        height=height,
    )


def dual_input(
    label: str,
    min_value: float,
    max_value: float,
    default: float,
    step: float,
    key: str,
    help_text: str | None = None,
    format: str | None = None,
) -> float:
    """Slider + number_input pod jednym labelem, synced przez session_state.

    Suwak do szybkiej zmiany, input do precyzyjnej wartosci. Obie metody
    zmieniaja te sama wartosc przechowywana w `st.session_state[key]`.

    Streamlit pattern z callbacks: `_sl` ma wlasny widget key, `_ni` osobny;
    on_change kazdego synchronizuje main `key`.
    """
    sl_key = f"{key}__sl"
    ni_key = f"{key}__ni"

    # Init state
    if key not in st.session_state:
        st.session_state[key] = default
    if sl_key not in st.session_state:
        st.session_state[sl_key] = st.session_state[key]
    if ni_key not in st.session_state:
        st.session_state[ni_key] = st.session_state[key]

    def _on_slider():
        st.session_state[key] = st.session_state[sl_key]
        st.session_state[ni_key] = st.session_state[sl_key]

    def _on_input():
        st.session_state[key] = st.session_state[ni_key]
        st.session_state[sl_key] = st.session_state[ni_key]

    label_with_help = label + (f" — _{help_text}_" if help_text else "")
    st.markdown(label_with_help, unsafe_allow_html=False)

    c1, c2 = st.columns([3, 1])
    c1.slider(
        label,
        min_value=min_value,
        max_value=max_value,
        step=step,
        key=sl_key,
        on_change=_on_slider,
        label_visibility="collapsed",
        format=format,
    )
    c2.number_input(
        label,
        min_value=min_value,
        max_value=max_value,
        step=step,
        key=ni_key,
        on_change=_on_input,
        label_visibility="collapsed",
        format=format,
    )

    return float(st.session_state[key])
