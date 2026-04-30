"""Streamlit UI - sekcja tlumaczen przez prompt do AI.

Workflow grafika:
1. Wpisuje tekst zrodlowy (PL albo EN)
2. Klika "Skopiuj prompt do AI" - schowek
3. Wkleja w ChatGPT/Claude.ai/Gemini, czeka na odpowiedz
4. Kopiuje odpowiedz, wkleja do drugiego textarea
5. Aplikacja parsuje, pokazuje 15 textarea z przetlumaczonymi tekstami
6. Grafik moze recznie poprawic dowolny jezyk

Returns: dict {lang_code: text} albo {} jesli nie wklejona odpowiedz.
"""

from __future__ import annotations

import streamlit as st

try:
    import pyperclip
    PYPERCLIP_OK = True
except ImportError:
    PYPERCLIP_OK = False

from src.logic.parser import parse_translations, validate_translations
from src.logic.prompt_template import LANGUAGES, LANGUAGE_NAMES, build_prompt


def render_translate_section() -> dict[str, str]:
    """Render sekcji tlumaczenia. Zwraca {lang_code: text} po edycji."""

    # Sekcja 1: tekst zrodlowy + jezyk
    st.subheader("1. Tekst zrodlowy")
    col1, col2 = st.columns([4, 1])
    with col1:
        source_text = st.text_area(
            "Wpisz tekst do przetlumaczenia",
            placeholder="Np. 'Single-use, oxygen-activated heat pack. For transporting animals...'",
            height=100,
            key="source_text",
            label_visibility="collapsed",
        )
    with col2:
        source_lang = st.selectbox(
            "Jezyk zrodlowy",
            options=["EN", "PL"],
            index=0,
            key="source_lang",
        )

    # Sekcja 2: prompt do AI
    st.subheader("2. Skopiuj prompt do AI")
    if not source_text.strip():
        st.info("Wpisz tekst powyzej, zeby wygenerowac prompt.")
    else:
        prompt = build_prompt(source_text, source_lang)
        with st.expander("Podglad promptu (15 jezykow + zasady formatowania)", expanded=False):
            st.code(prompt, language="markdown")

        col_a, col_b = st.columns([1, 3])
        with col_a:
            if st.button("Skopiuj prompt", type="primary", use_container_width=True):
                if PYPERCLIP_OK:
                    try:
                        pyperclip.copy(prompt)
                        st.success("Skopiowano - wklej do ChatGPT/Claude.ai/Gemini.")
                    except Exception as e:
                        st.error(f"Blad clipboard: {e}. Skopiuj recznie z podgladu wyzej.")
                else:
                    st.warning("pyperclip nie zainstalowany - skopiuj recznie z podgladu.")
        with col_b:
            st.caption(
                "Wklej prompt do dowolnego AI (ChatGPT, Claude.ai, Gemini, "
                "Mistral...). AI odpowie 15 liniami w formacie `KOD === tekst`."
            )

    # Sekcja 3: wklej odpowiedz AI
    st.subheader("3. Wklej odpowiedz AI")
    ai_response = st.text_area(
        "Odpowiedz AI - 15 jezykow w formacie 'KOD === tekst'",
        placeholder="EN === ...\nPL === ...\nUK === ...\n(... 15 linii)",
        height=200,
        key="ai_response",
        label_visibility="collapsed",
    )

    if not ai_response.strip():
        return {}

    parsed = parse_translations(ai_response)
    missing, extra = validate_translations(parsed, LANGUAGES)

    # Status parsowania
    cols = st.columns(3)
    cols[0].metric("Sparsowano jezykow", f"{len(parsed)}/{len(LANGUAGES)}")
    cols[1].metric("Brakuje", len(missing))
    cols[2].metric("Nadmiarowe (zignorowane)", len(extra))

    if missing:
        st.warning(f"Brak {len(missing)} jezykow: **{', '.join(missing)}**. Mozesz je dopisac recznie nizej.")
    if extra:
        st.info(f"Nieoczekiwane kody (pominiete): {', '.join(extra)}")
    if not parsed:
        st.error(
            "Parser nie znalazl zadnego jezyka. Format powinien byc `KOD === tekst` "
            "(np. `EN === Hello world`). Sprawdz czy AI uzylo poprawnego separatora."
        )
        return {}

    # Sekcja 4: edytowalne textarea per jezyk
    st.subheader(f"4. Edytuj jezyki ({len(parsed)} sparsowane, mozesz poprawic dowolny)")

    edited: dict[str, str] = {}
    cols = st.columns(3)
    for i, code in enumerate(LANGUAGES):
        col = cols[i % 3]
        with col:
            initial = parsed.get(code, "")
            label = f"**{code}** ({LANGUAGE_NAMES[code]})"
            if not initial:
                label += " [BRAK]"
            edited[code] = st.text_area(
                label,
                value=initial,
                height=90,
                key=f"lang_text_{code}",
            )

    # Status koncowy - ile jezykow wypelnionych po edycji
    filled = sum(1 for t in edited.values() if t.strip())
    if filled == len(LANGUAGES):
        st.success(f"Wszystkie {filled} jezykow wypelnione - mozesz przejsc do generacji etykiety.")
    else:
        st.warning(f"Wypelnione {filled}/{len(LANGUAGES)} jezykow - uzupelnij brakujace przed generacja.")

    return {code: text.strip() for code, text in edited.items() if text.strip()}
