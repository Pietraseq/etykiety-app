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

from src.logic.parser import parse_translations, validate_translations
from src.logic.prompt_template import (
    LANGUAGES,
    LANGUAGE_NAMES,
    build_format_prompt,
    build_prompt,
)
from src.ui.widgets import js_copy_button

MODE_TRANSLATE = "Przetłumacz z PL/EN"
MODE_FORMAT = "Mam już 15 tłumaczeń, sformatuj"


def render_translate_section() -> dict[str, str]:
    """Render sekcji tlumaczenia. Zwraca {lang_code: text} po edycji."""

    mode = st.radio(
        "Tryb pracy",
        options=[MODE_TRANSLATE, MODE_FORMAT],
        key="translate_mode",
        horizontal=True,
        help=(
            "Tryb 1: wpisujesz 1 tekst, AI tłumaczy na 15 języków. "
            "Tryb 2: masz już 15 tłumaczeń (od kontrahenta, z Excela...), "
            "AI tylko normalizuje format `KOD === tekst`."
        ),
    )

    prompt: str | None = None

    if mode == MODE_TRANSLATE:
        st.subheader("1. Tekst źródłowy")
        col1, col2 = st.columns([4, 1])
        with col1:
            source_text = st.text_area(
                "Wpisz tekst do przetłumaczenia",
                placeholder="Wpisz tutaj tekst, który ma się znaleźć na etykiecie",
                height=100,
                key="source_text",
                label_visibility="collapsed",
            )
            st.button("Zatwierdź tekst", key="submit_source", help="lub Ctrl+Enter w polu wyżej")
        with col2:
            source_lang = st.selectbox(
                "Język źródłowy",
                options=["EN", "PL"],
                index=0,
                key="source_lang",
            )
        if source_text.strip():
            prompt = build_prompt(source_text, source_lang)
    else:
        st.subheader("1. Wklej 15 tłumaczeń")
        st.caption(
            "Dowolny format — lista, CSV, Excel paste, plain text z nagłówkami "
            "(np. 'Polski: ...', 'English: ...'). AI dopasuje kody języków i sformatuje."
        )
        raw_translations = st.text_area(
            "Wklej tłumaczenia w jakimkolwiek formacie",
            placeholder="Polski: ...\nEnglish: ...\n...",
            height=200,
            key="raw_translations",
            label_visibility="collapsed",
        )
        st.button("Zatwierdź tłumaczenia", key="submit_raw", help="lub Ctrl+Enter w polu wyżej")
        if raw_translations.strip():
            prompt = build_format_prompt(raw_translations)

    st.subheader("2. Skopiuj prompt do AI")
    if prompt is None:
        st.info("Wpisz tekst powyżej, żeby wygenerować prompt.")
    else:
        with st.expander("Podgląd promptu (15 języków + zasady formatowania)", expanded=False):
            st.code(prompt, language="markdown")

        col_a, col_b = st.columns([1, 3])
        with col_a:
            js_copy_button(prompt, label="Skopiuj prompt")
        with col_b:
            st.caption(
                "Wklej prompt do dowolnego AI (ChatGPT, Claude.ai, Gemini, "
                "Mistral...). AI odpowie 15 liniami w formacie `KOD === tekst`. "
                "Backup: rozwiń podgląd promptu wyżej i użyj ikony copy w prawym górnym rogu."
            )

    st.subheader("3. Wklej odpowiedź AI")
    ai_response = st.text_area(
        "Odpowiedź AI — 15 języków w formacie 'KOD === tekst'",
        placeholder="EN === ...\nPL === ...\nUK === ...\n(... 15 linii)",
        height=200,
        key="ai_response",
        label_visibility="collapsed",
    )
    st.button("Zatwierdź odpowiedź AI", key="submit_response", help="lub Ctrl+Enter w polu wyżej")

    if not ai_response.strip():
        return {}

    parsed = parse_translations(ai_response)
    missing, extra = validate_translations(parsed, LANGUAGES)

    cols = st.columns(3)
    cols[0].metric("Sparsowano języków", f"{len(parsed)}/{len(LANGUAGES)}")
    cols[1].metric("Brakuje", len(missing))
    cols[2].metric("Nadmiarowe (zignorowane)", len(extra))

    if missing:
        st.warning(f"Brak {len(missing)} języków: **{', '.join(missing)}**. Możesz je dopisać ręcznie niżej.")
    if extra:
        st.info(f"Nieoczekiwane kody (pominięte): {', '.join(extra)}")
    if not parsed:
        st.error(
            "Parser nie znalazł żadnego języka. Format powinien być `KOD === tekst` "
            "(np. `EN === Hello world`). Sprawdź czy AI użyło poprawnego separatora."
        )
        return {}

    st.subheader(f"4. Edytuj języki ({len(parsed)} sparsowane, możesz poprawić dowolny)")

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

    filled = sum(1 for t in edited.values() if t.strip())
    if filled == len(LANGUAGES):
        st.success(f"Wszystkie {filled} języków wypełnione — możesz przejść do generacji etykiety.")
    else:
        st.warning(f"Wypełnione {filled}/{len(LANGUAGES)} języków — uzupełnij brakujące przed generacją.")

    return {code: text.strip() for code, text in edited.items() if text.strip()}
