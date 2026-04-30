# CLAUDE.md — etykiety-app

*Zasady uniwersalne → `C:\Projekty\CLAUDE.md`. Ten plik — tylko specyfika tego projektu.*

## Co to jest

UI dla grafika do generowania wielojęzycznych etykiet Happet. Wpisuje tekst PL/EN, kopiuje wygenerowany prompt do ChatGPT/Claude.ai, wkleja odpowiedź ze sformatowanymi 15 językami, dostraja layout (8+7 / 5+5+5 / 3+3+3+3+3) i marker (flaga / skrót), generuje SVG. Engine renderowania = `etykiety-svg` (submodule), tu tylko UI + tłumaczenia + auto-tune font_size pod preferowaną liczbę wierszy.

## Tech stack

- Python 3.13 + venv lokalny w `.venv/`
- **Streamlit** (UI w przeglądarce, lokalnie albo Streamlit Cloud)
- `etykiety-svg` jako git submodule — engine layoutu + emisji SVG
- `pyperclip` (clipboard) - copy promptu do schowka
- `pyyaml`, `pydantic` - jak w `etykiety-svg`
- Brak płatnych API - tłumaczenia przez prompt do dowolnego AI (ChatGPT, Claude.ai, Gemini), grafik wkleja odpowiedź

## Konwencje tego projektu

- UI po polsku (grafik nie musi znać angielskiego)
- 1 plik `app.py` jako entry point Streamlit
- Logika UI w `src/ui/` (sekcje: input, translate, settings, preview)
- Logika niezależna od UI (parser, tuner, prompt) w `src/logic/`
- `etykiety_svg/` to submodule - NIE modyfikuj wewnątrz, jeśli trzeba zmiany silnika - PR do `etykiety-svg`
- Prompt do AI = jeden szablon w `src/logic/prompt_template.py`, format odpowiedzi = `KOD === tekst` per linia (parser regex)

## Komendy

```powershell
# Setup (pierwszy raz lub po klonowaniu)
git clone --recursive https://github.com/Pietraseq/etykiety-app.git
cd etykiety-app
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -3.13 -m pip install -r requirements.txt

# Pull submodule po update etykiety-svg
git submodule update --remote etykiety_svg

# Uruchomienie
streamlit run app.py
# Otwiera sie http://localhost:8501

# Test parsera promptu (bez UI)
py -3.13 -m pytest tests/
```

## Pliki w repo

- `CLAUDE.md` — ten plik
- `CONTEXT.md` — biznes: dla kogo (grafik Happet), co robi
- `MEMORY.md` — stan prac, decyzje
- `PLAN.md` — fazy implementacji (A-E)
- `REFERENCES.md` — Streamlit docs, format promptu, gotchas
- `README.md` — quick start dla grafika
- `app.py` — entry point Streamlit
- `src/logic/` — niezależne od UI: prompt, parser, tuner
- `src/ui/` — Streamlit komponenty per sekcja
- `etykiety_svg/` — submodule (silnik renderowania SVG)
- `tests/` — pytest dla logiki (nie UI)

## Czego NIE robić specyficznie tu

- Nie hardkoduj API key DeepL/OpenAI - tłumaczenia robi GRAFIK przez wklejenie do swojego AI
- Nie modyfikuj `etykiety_svg/` (submodule) bezpośrednio - zmiany w silniku przez PR do `etykiety-svg`
- Nie commituj wygenerowanych SVG (`output/` w gitignore)
- Nie używaj zewnętrznych API tłumaczeń bez zgody Pietrasa (cost concerns)
