"""Streamlit helpery do reuzywania - dual_input (slider + number_input synced)."""

from __future__ import annotations

import streamlit as st


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
