# etykiety-app

Aplikacja Streamlit dla grafika Happet — generuje wielojęzyczne etykiety SVG z jednego tekstu PL/EN przez prompt do AI (ChatGPT/Claude.ai/Gemini).

## Workflow

1. Wpisujesz tekst po polsku albo angielsku
2. Klikasz "Skopiuj prompt do AI" → schowek
3. Wklejasz w ChatGPT / Claude.ai / Gemini → AI tłumaczy na 15 języków w sformatowanym układzie
4. Kopiujesz odpowiedź AI, wklejasz do aplikacji
5. Aplikacja parsuje 15 języków, pokazuje 15 textarea (możesz poprawić ręcznie)
6. Wybierasz layout (8+7 / 5+5+5 / 3+3+3+3+3), styl markera (flaga / skrót), preferowaną liczbę wierszy
7. Aplikacja auto-dostraja font_size i pokazuje preview SVG
8. Pobierasz SVG → otwierasz w Illustratorze / CorelDraw

## Quick start

```powershell
git clone --recursive https://github.com/Pietraseq/etykiety-app.git
cd etykiety-app
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -3.13 -m pip install -r requirements.txt

streamlit run app.py
# Otwiera sie http://localhost:8501
```

⚠️ Flaga `--recursive` jest WAŻNA — bez niej submodule `etykiety_svg/` będzie pusty.

Jak zapomniałeś `--recursive`:

```powershell
git submodule update --init --recursive
```

## Dokumentacja

- `CLAUDE.md` — instrukcje dla AI (stack, konwencje)
- `CONTEXT.md` — biznes (problem, cel, dla kogo)
- `MEMORY.md` — stan prac, decyzje
- `PLAN.md` — fazy implementacji A-E
- `REFERENCES.md` — Streamlit, format promptu, gotchas
- `etykiety_svg/` — submodule, silnik renderowania (osobne repo)

## Stack

- Python 3.13 + venv
- Streamlit (UI)
- pyperclip (clipboard)
- etykiety-svg (silnik SVG, jako submodule)

## Dane

- Source code commit, output `*.svg` gitignored
- Brak `.env` / sekretów - aplikacja nie ma żadnego API key
- Tłumaczenia robi grafik przez własne konto AI (ChatGPT/Claude.ai/Gemini)
