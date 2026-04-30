# Plan implementacji — etykiety-app

## Faza A — Setup + scaffold (0.5 dnia)

1. Struktura projektu (5+1 MD, src/, tests/, app.py)
2. Submodule `etykiety-svg` w `etykiety_svg/`
3. `requirements.txt`: streamlit, pyperclip, pyyaml, pydantic + transitive z etykiety-svg
4. venv + `pip install -r requirements.txt`
5. `app.py` Hello World: `st.title("etykiety-app")` + import etykiety-svg sanity check
6. `streamlit run app.py` → otwiera localhost:8501, wyswietla title + import OK
7. Repo na GitHubie Pietraseq/etykiety-app + push (z submodule)

**Zamknięcie fazy**: `streamlit run app.py` na świeżym kloniu (po `git clone --recursive`) działa, importuje etykiety-svg, pokazuje 1 stronę.

## Faza B — Prompt + parser (0.5 dnia)

1. `src/logic/prompt_template.py` — generator promptu dla AI z 15 językami
2. `src/logic/parser.py` — parser odpowiedzi AI: regex `^([A-Z]{2})\s*===\s*(.+)$`, walidacja (15 kodów, brak duplikatów)
3. `tests/test_parser.py` — pytest na różne formaty odpowiedzi (markdown bullets, plain, z dodatkowymi nagłówkami)
4. UI w `src/ui/translate.py`:
   - Textarea: tekst źródłowy (PL/EN)
   - Select: język źródłowy
   - Button: "Skopiuj prompt do AI" (pyperclip + komunikat)
   - Textarea: wklej odpowiedź AI
   - Po wklejeniu: lista 15 textarea z parsowanymi językami (do edycji)

**Zamknięcie fazy**: grafik wkleja przykładowy tekst, kopiuje prompt, wkleja do ChatGPT, kopiuje odpowiedź, wkleja do aplikacji - 15 textarea pojawia się z poprawnymi tłumaczeniami.

## Faza C — Settings + auto-tune (1 dzień)

1. `src/ui/settings.py`:
   - Radio: layout (8+7 / 5+5+5 / 3+3+3+3+3)
   - Radio: marker style (flag_circle / text_rect)
   - Color picker: kolor markera (gdy text_rect)
   - Number: preferred_lines (default 4)
   - Sliders advanced: font_size, column_width, page_size (zwijane "Zaawansowane")
2. `src/logic/tuner.py` — bisekcja:
   - Input: 15 tekstów + page_size + columns + preferred_lines
   - Algorytm: bisekcja na font_size w zakresie [1.0mm, 5.0mm], precyzja 0.05mm
   - Kryterium: max(linii_per_jezyk) <= preferred_lines, ale jak najwiekszy font
   - Output: optymalny font_size
3. `tests/test_tuner.py` — fixturem testów: różne długości tekstów → różne font_size
4. UI flow: po dostrojeniu auto-tune pokazuje "Optymalny font: 2.4mm. Wciska maks 4 wiersze (DE, RU mają 4)"

**Zamknięcie fazy**: grafik klika "Auto-dostrój", aplikacja w sekundę pokazuje optymalny font + listę języków z liczbą wierszy.

## Faza D — Preview + download (0.5 dnia)

1. `src/ui/preview.py`:
   - Generuj SVG przez `etykiety_svg.layout_page` + `write_svg`
   - Renderuj `st.components.v1.html(svg_string)` jako live preview
   - Button "Pobierz SVG" (st.download_button)
   - Button "Pobierz YAML" (config dla power-userów do `etykiety-svg`)
2. Live update: zmiana w textarea → re-render SVG (Streamlit auto re-runs)

**Zamknięcie fazy**: grafik widzi etykietę w przeglądarce + pobiera SVG na dysk.

## Faza E — Polish + dokumentacja (0.5 dnia)

1. UI po polsku, error handling (parser fail, brak języka, font za duży)
2. Walidacje: 15 języków obecnych, każdy non-empty, unique kody
3. README dla grafika z 4 screenshotami workflow
4. Hosting: instrukcja "Streamlit Cloud deploy" lub "lokalnie tylko dla zespołu"

**Zamknięcie fazy**: grafik czyta README + 1 raz przechodzi cały workflow → dochodzi do gotowego SVG bez pytania Pietrasa.

## Faza F — Sanity check + testy

- 5 różnych etykiet (różne długości tekstów) - aplikacja generuje sensowny output
- Test cross-browser (Chrome, Firefox)
- Test workflow z różnymi modelami AI (ChatGPT-5, Claude 4.7, Gemini) - czy wszystkie zwracają parsowalne formaty
- Cykl edycji: parser fail → grafik widzi co poszło nie tak

## Fazy odłożone (osobna iteracja, nie teraz)

- **Hosting Streamlit Cloud z autoryzacją** - jeśli grafików będzie >1 i Pietras chce kontrolować dostęp
- **Presety per produkt** - zapisywanie konfiguracji etykiety pod nazwą (np. "D609 default") do reuse
- **Eksport PDF** - WeasyPrint po SVG (dla drukarni która woli PDF)
- **DeepL API integration** - jeśli grafik nie chce pętli copy-paste z AI
- **Multi-product (batch)** - wkleja CSV z 10 produktami, dostaje 10 SVG zip
- **Migracja na React + FastAPI** - jeśli Streamlit hit limity (zwykle UX, nie wydajność)
