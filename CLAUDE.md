# CLAUDE.md — etykiety-app

*Zasady uniwersalne → `C:\Projekty\CLAUDE.md`. Ten plik — tylko specyfika tego projektu.*

## Co to jest

UI dla grafika do generowania wielojęzycznych etykiet Happet. Wpisuje tekst PL/EN, kopiuje wygenerowany prompt do ChatGPT/Claude.ai, wkleja odpowiedź ze sformatowanymi 15 językami, dostraja layout (8+7 / 5+5+5 / 3+3+3+3+3 / 15) i marker (flaga / skrót), generuje SVG. Silnik renderowania (`label_generator`) jest **vendor-owany w `src/label_generator/`** — kod żyje w tym samym repo, nie ma submodułu.

## Tech stack

- Python 3.13 + venv lokalny w `.venv/`
- **Streamlit** (UI w przeglądarce, lokalnie albo Streamlit Cloud)
- `label_generator` — silnik SVG, vendor-owany (źródłowo z `etykiety-svg`, kopia w `src/label_generator/`)
- `pyperclip` (clipboard) - copy promptu do schowka (lokalnie; na chmurze fallback do ręcznego copy z ekspandera)
- `pyyaml`, `pydantic`, `fontTools`, `lxml`, `pyphen`, `pdfplumber`
- Brak płatnych API - tłumaczenia przez prompt do dowolnego AI (ChatGPT, Claude.ai, Gemini), grafik wkleja odpowiedź

## Konwencje tego projektu

- UI po polsku (grafik nie musi znać angielskiego)
- 1 plik `app.py` jako entry point Streamlit
- Logika UI w `src/ui/` (sekcje: translate, preview, branding, widgets)
- Logika niezależna od UI (parser, tuner, prompt) w `src/logic/`
- Silnik SVG w `src/label_generator/` - własność tego repo. Jeśli warto sync z osobnym `etykiety-svg`, kopiuj ręcznie (jest standalone CLI).
- Prompt do AI = jeden szablon w `src/logic/prompt_template.py`, format odpowiedzi = `KOD === tekst` per linia (parser regex)

## Komendy

```powershell
# Setup (pierwszy raz lub po klonowaniu)
git clone https://github.com/Pietraseq/etykiety-app.git
cd etykiety-app
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -3.13 -m pip install -r requirements.txt

# Uruchomienie
streamlit run app.py
# Otwiera sie http://localhost:8501

# Test parsera promptu i logiki (bez UI)
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
- `src/label_generator/` — silnik SVG (vendor-owany z `etykiety-svg`)
- `src/logic/` — niezależne od UI: prompt, parser, tuner
- `src/ui/` — Streamlit komponenty per sekcja
- `assets/flags/` — 15 flag SVG (lipis/flag-icons, MIT)
- `assets/logo/`, `assets/branding/`, `assets/backgrounds/` — branding HappyLabel
- `fonts/` — Arial TTF (Regular + Bold)
- `tests/` — pytest dla logiki (nie UI)

## Czego NIE robić specyficznie tu

- Nie hardkoduj API key DeepL/OpenAI - tłumaczenia robi GRAFIK przez wklejenie do swojego AI
- Nie commituj wygenerowanych SVG (`output/` w gitignore)
- Nie używaj zewnętrznych API tłumaczeń bez zgody Pietrasa (cost concerns)
- `etykiety_svg/` (folder po starym submodule) jest w `.gitignore` - nie commituj. Aktywny silnik to `src/label_generator/`.
