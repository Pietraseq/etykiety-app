# etykiety-app — HappyLabel

Aplikacja Streamlit dla grafika Happet — generuje wielojęzyczne etykiety SVG z jednego tekstu PL/EN przez prompt do AI (ChatGPT / Claude.ai / Gemini).

## Workflow grafika (krok po kroku)

1. **Tryb pracy** — wybierasz na górze:
   - *Przetłumacz z PL/EN* — wpisujesz tekst w jednym języku, AI tłumaczy na 15
   - *Mam już 15 tłumaczeń, sformatuj* — masz gotowe tłumaczenia (np. od kontrahenta), AI tylko normalizuje format
2. **Tekst źródłowy** — wpisujesz tekst PL albo EN (lub wklejasz wszystkie 15 tłumaczeń w trybie 2)
3. **Skopiuj prompt do AI** — klikasz przycisk, prompt trafia do schowka
4. **Wklejasz w ChatGPT / Claude.ai / Gemini** — AI odpowiada 15 liniami w formacie `KOD === tekst`
5. **Kopiujesz odpowiedź AI, wklejasz do aplikacji**
6. **Edytujesz języki** — aplikacja parsuje 15 textarea, możesz poprawić każdy ręcznie
7. **Layout** — wybierasz jeden z 4 układów: `8+7`, `5+5+5`, `3+3+3+3+3` lub `15` (jedna kolumna)
8. **Marker** — flaga w kółku albo skrót kraju z kolorem
9. **Preferowana liczba wierszy** — suwak 1–10. Aplikacja dobierze największy font, który gwarantuje, że najdłuższy język nie przekroczy tej liczby.
10. **Formatowanie tekstu** — wyjustowany na całą szerokość kolumny vs wyrównany do lewej (ragged-right)
11. **Modelowanie** — po lewej zaawansowane parametry (rozmiar etykiety, obszar tekstu, odstępy), po prawej żywy podgląd SVG
12. **Pobierz SVG** — otwierasz w Illustratorze / CorelDraw, każdy język to osobny edytowalny obiekt tekstowy

## Quick start

```powershell
git clone --recursive https://github.com/Pietraseq/etykiety-app.git
cd etykiety-app
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -3.13 -m pip install -r requirements.txt

streamlit run app.py
# Otwiera się http://localhost:8501
```

⚠️ Flaga `--recursive` jest WAŻNA — bez niej submodule `etykiety_svg/` będzie pusty i aplikacja nie wystartuje.

Jeśli zapomniałeś `--recursive`:

```powershell
git submodule update --init --recursive
```

Po update silnika SVG (po `git pull` w `etykiety-app`):

```powershell
git submodule update --remote etykiety_svg
```

## Funkcje zaawansowane (sekcja 6 w UI)

- **Sprzężenie szerokości obszaru tekstu z szerokością etykiety** — gdy włączone, zmiana szerokości etykiety automatycznie aktualizuje szerokość obszaru tekstu (zachowując zadany margines lewy + prawy w mm)
- **Suwak powiększenia 50–500%** — 100% = rzeczywista wielkość mm, 200% domyślnie dla widoczności
- **Ramki podglądu** — czarna gruba = krawędź etykiety, niebieska przerywana = obszar tekstu (strefa robocza). Zmieniają się na czerwono gdy tekst wystaje poza obszar.
- **„Etykieta niemożliwa"** — komunikat gdy nawet najmniejszy font nie mieści najdłuższego języka w preferowanej liczbie wierszy. Aplikacja podpowiada możliwości naprawy.
- **„Ustawienia domyślne"** — przycisk resetuje wszystkie zaawansowane parametry do wartości startowych

## Rozwiązywanie problemów

| Problem | Rozwiązanie |
|---|---|
| Aplikacja nie startuje, błąd o `etykiety-svg` | `git submodule update --init --recursive` |
| Brakuje przycisku „Skopiuj prompt" | Wpisz tekst źródłowy i kliknij „Zatwierdź tekst" (lub Ctrl+Enter) |
| Parser nie znalazł żadnego języka | Sprawdź czy AI użyło separatora `===` (a nie `:` lub `-`). W razie potrzeby popraw odpowiedź ręcznie. |
| „Etykieta niemożliwa" | Skróć tekst, zwiększ obszar tekstu, zwiększ preferowaną liczbę wierszy lub wybierz węższy layout |
| Schowek nie działa | Skopiuj prompt ręcznie z podglądu (rozwiń ekspander) |

## Dokumentacja deweloperska

- `CLAUDE.md` — instrukcje dla AI (stack, konwencje)
- `CONTEXT.md` — biznes (problem, cel, dla kogo)
- `MEMORY.md` — stan prac, historia decyzji
- `PLAN.md` — fazy implementacji A–E
- `REFERENCES.md` — Streamlit, format promptu, gotchas
- `etykiety_svg/` — submodule, silnik renderowania SVG (osobne repo)

## Stack

- Python 3.13 + venv
- Streamlit (UI w przeglądarce)
- pyperclip (schowek)
- etykiety-svg (silnik SVG, jako git submodule)

## Dane

- Source code commit, output `*.svg` gitignored
- Brak `.env` / sekretów — aplikacja nie ma żadnego API key
- Tłumaczenia robi grafik przez własne konto AI (ChatGPT / Claude.ai / Gemini)
