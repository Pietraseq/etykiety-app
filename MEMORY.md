# MEMORY.md — etykiety-app

Aktualny stan prac. Ostatnia aktualizacja: 2026-04-30

## Co działa

- Nic jeszcze - projekt w starcie

## W toku

- [ ] Faza A - setup projektu, submodule etykiety-svg, app.py Hello World

## Do zrobienia

- [ ] Faza B - prompt template + parser odpowiedzi AI + textarea inputs
- [ ] Faza C - settings UI + auto-tune bisekcja font_size
- [ ] Faza D - live preview SVG + download
- [ ] Faza E - polish + README dla grafika
- [ ] Hosting decision: lokalnie vs Streamlit Cloud

## Aktualne problemy

- Brak

## Znane ograniczenia

- Tłumaczenia ręczne przez prompt do AI (bez API integration) - workflow wymaga 2 copy-paste'ow grafika do dowolnego AI. Zasady decyzji w CONTEXT.md.
- Streamlit nie obsługuje natywnego drag&drop dla zmiany kolejności języków - jeśli grafik chce inny order, edytuje YAML z presetu.
- Live preview SVG w przeglądarce może wolno renderować dla skomplikowanych flag (ES z herbem ~80kb).

## Historia decyzji

- **2026-04-30:** Start projektu po zamknięciu MVP `etykiety-svg`. Stack: Streamlit + Python 3.13 + git submodule etykiety-svg.
- **2026-04-30:** Tłumaczenia bez API (DeepL/OpenAI) - generujemy prompt który grafik kopiuje do swojego AI (ChatGPT/Claude.ai/Gemini), aplikacja parsuje odpowiedź. Brak kosztów, brak zależności od konta API. Format odpowiedzi: `KOD === tekst` per linia.
- **2026-04-30:** Layout 3 opcje: 8+7 (default, jak D609), 5+5+5, 3+3+3+3+3. Marker 2 opcje: flaga (default) lub skrót z kolorem.
- **2026-04-30:** Auto-tune font_size przez bisekcję: input = preferred_lines, output = optymalny font. Cel: najdłuższy język ma <= preferred_lines, ale font jak największy (czytelność).
- **2026-04-30:** Repo osobne (Pietraseq/etykiety-app), etykiety-svg jako git submodule (czystość rozdzielenia engine vs UI).
