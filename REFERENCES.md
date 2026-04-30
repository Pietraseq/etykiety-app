# REFERENCES.md — etykiety-app

Techniczna referencja: Streamlit, format promptu dla AI, gotchas.

## Dokumentacja

- **Streamlit** — https://docs.streamlit.io/ — UI komponenty, session state, cache
- **etykiety-svg** (submodule) — `etykiety_svg/CLAUDE.md` + `etykiety_svg/REFERENCES.md`
- **pyperclip** — https://pyperclip.readthedocs.io/ — clipboard read/write cross-platform
- **lipis/flag-icons** — https://github.com/lipis/flag-icons — flagi SVG (już w `etykiety-svg/assets/flags`)

⚠️ Dokumentację zawsze weryfikować na żywo — Streamlit ma częste zmiany API.

## Format promptu dla AI

Generowany przez `src/logic/prompt_template.py`:

```
Translate the following text to 15 languages used on Happet pet product labels.

Output format - one block per language, separator " === ":

EN === <english>
PL === <polish>
UK === <ukrainian>
RO === <romanian>
DE === <german>
HU === <hungarian>
LT === <lithuanian>
SK === <slovak>
CZ === <czech>
IT === <italian>
ES === <spanish>
GR === <greek>
FR === <french>
PT === <portuguese>
RU === <russian>

Rules:
- Keep brand names unchanged ("Happet", product codes like "D609")
- Match the source tone (instructional / promotional / informational)
- Match the source length (don't add explanations or padding)
- Plain text only - no markdown, no asterisks, no bullet points

Source language: {source_lang}
Source text:
"""
{user_text}
"""
```

Parser regex: `^([A-Z]{2})\s*===\s*(.+)$` (multiline)

## Wymagane atrybuty SVG dla AI/Corel (z etykiety-svg)

- `<g id="lang-XX" inkscape:label="XX">` — Corel czyta `id`, Illustrator `inkscape:label`
- `<text>` per blok = 1 obiekt edytowalny per język
- `<tspan x y dy word-spacing>` per linia
- Flagi: `<symbol>` w `<defs>` + `<use href="#flag-XX" clip-path="url(#flag-circle)">`

## Auto-tune algorytm (Faza C)

Bisekcja na `font_size` w zakresie [1.0mm, 5.0mm]:

```python
def find_optimal_font(texts: dict[str, str], page_size, columns, preferred_lines):
    lo, hi = 1.0, 5.0
    while hi - lo > 0.05:  # precyzja 0.05mm
        mid = (lo + hi) / 2
        max_lines = simulate_layout(texts, font_size=mid, ...).max_lines_per_block
        if max_lines > preferred_lines:
            hi = mid  # za duzy font - zmniejsz
        else:
            lo = mid  # mieści się - sprobuj większy
    return lo  # największy font przy którym najdłuższy <= preferred
```

`simulate_layout` używa funkcji z `etykiety_svg.layout` (bez generowania SVG, tylko obliczenia liczby linii per blok).

## Gotchas

- **Streamlit re-runs przy każdej zmianie inputu** — używaj `@st.cache_data` dla drogich obliczeń (auto-tune, parsowanie dużych odpowiedzi AI)
- **session_state dla persystencji między re-runs** — np. parsowane języki przechowuj w `st.session_state['languages']`, inaczej rerun zresetuje formularz
- **pyperclip na Linux** wymaga `xclip` lub `xsel` (Streamlit Cloud Linux) — sprawdzić przed deployem
- **etykiety-svg jako submodule**: po update silnika trzeba `git submodule update --remote etykiety_svg && git add etykiety_svg && git commit`
- **AI odpowiedzi w markdown**: ChatGPT lubi dodawać `**EN**` lub bullet listy. Parser musi tolerować typowe modele: gołe `EN === ...`, ale też `**EN** === ...` lub `- EN === ...`. Test różne modele zanim shipniemy.
- **Polskie znaki w pyperclip** na Windows — generalnie OK, ale unicode może spaść do `?` jeśli encoding źle ustawiony. Test cyrylica i greka też.
- **SVG embed w Streamlit**: `st.image(svg_bytes)` NIE działa dla SVG; użyj `st.components.v1.html(svg_string, height=...)` lub `streamlit-svg-renderer` (jeśli istnieje).

## Hosting opcje

| Opcja | Plus | Minus |
|---|---|---|
| Lokalnie u Pietrasa (`streamlit run`) | 0 kosztów, pełna kontrola | grafik musi mieć dostęp do PC Pietrasa albo własny setup |
| Streamlit Cloud (free tier) | publicznie dostępne, auto-deploy z GitHub | publiczny URL, limity zasobów (1GB RAM) |
| Self-hosted (VPS Hetzner / DO) | pełna kontrola, prywatny URL | ~5€/mies + setup admin |
| Docker compose | reproducible, łatwe wdrożenie | grafik musi instalować Docker |

Decyzja domyślna: **lokalnie w trakcie MVP**, decyzja o hostingu po Fazie E.

## Linki

- Repo: https://github.com/Pietraseq/etykiety-app
- Submodule: https://github.com/Pietraseq/etykiety-svg
- Streamlit Cloud (jeśli wdrożymy): TBD
