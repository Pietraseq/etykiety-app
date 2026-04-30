# MEMORY.md — etykiety-app

Aktualny stan prac. Ostatnia aktualizacja: 2026-04-30

## Co działa (E2E)

- **Faza A**: scaffold + submodule etykiety-svg + Streamlit Hello World (commit init)
- **Faza B**: prompt template + parser AI + UI tłumaczenia (18/18 testów). Workflow: textarea → "Skopiuj prompt" → AI → wklej → 15 textarea edytowalnych
- **Faza C**: settings UI (layout 8+7/5+5+5/3+3+3+3+3, marker flag/text+color, preferred_lines 1-10) + auto-tune bisekcja font_size (11/11 testów)
- **Faza D**: live preview SVG + download (SVG/YAML) + "Pełen ekran" data URL
- **UI redesign**: side-by-side advanced+preview (kolumny 1:3), suwaki + number_inputs synced (helper `dual_input`), pomarańczowa ramka strefy roboczej w preview, suwak powiększenia 50-500% (default 200%), guzik "Ustawienia domyślne", banner "Etykieta niemożliwa"
- **Submodule etykiety-svg**: bumped 3x z poziomu app (le=4→le=10 dla columns, marker_size clamp do line_height, inter_block_gap_mm jako opcjonalny config)
- **29/29 testów PASS** (parser 18 + tuner 11)
- **Repo**: https://github.com/Pietraseq/etykiety-app (private), submodule etykiety-svg

## W toku (na koniec sesji 2026-04-30 wieczór)

- **Codex w tle (`bnmn0w53a`)**: generuje 6 assetów grafik dla `assets/backgrounds/` + `assets/logo/` (background-day/night.webp + 4× logo HappyLabel 1500). Foldery utworzone, Codex jeszcze nie zapisał plików gdy Pietras kończył sesję. Status nieznany - sprawdzić w nowej sesji przez `Read` na temp plik output albo `ls /c/Projekty/etykiety-app/assets/`.

## Do zrobienia (next session)

- [ ] Sprawdzić wynik Codex (czy 6 plików w `assets/`)
- [ ] Jeśli OK: review wizualny → integracja CSS w app.py (background day/night toggle, logo w headerze)
- [ ] Jeśli Codex nie wygenerował: alternatywna droga (ChatGPT/Claude.ai z DALL-E, ręcznie wklejony prompt)
- [ ] **Faza E**: README dla grafika ze screenshotami workflow, polish error handling, decyzja o hostingu (lokalnie vs Streamlit Cloud)
- [ ] Test grafików E2E na realnej etykiecie nowego produktu
- [ ] Cross-PC test: drugi PC `git clone --recursive` + venv + `streamlit run app.py`

## Aktualne problemy

- Brak na koniec sesji. Codex może być stuck - sprawdzić.

## Znane ograniczenia

- Tłumaczenia ręczne przez prompt do AI (bez API integration) - świadoma decyzja architektoniczna
- Streamlit nie obsługuje drag&drop reordering języków - manualnie w YAML jeśli potrzebne
- Logo Happet referencja tylko tekstowo w prompcie do Codex - jeśli efekt nieidealny, dorzucić `-i path/to/logo.png` w next iteration
- Codex skill `imagegen` w `~/.codex/skills/.system/` - pre-installed system skill, dostępny ale nie testowany do tej pory w naszym workflow

## Historia decyzji

- **2026-04-30 rano**: Start projektu po zamknięciu MVP `etykiety-svg`. Stack: Streamlit + Python 3.13 + git submodule etykiety-svg.
- **2026-04-30 rano**: Tłumaczenia bez API (DeepL/OpenAI) - generujemy prompt który grafik kopiuje do swojego AI, aplikacja parsuje odpowiedź. Format: `KOD === tekst` per linia.
- **2026-04-30 rano**: Layout 3 opcje: 8+7 (default, jak D609), 5+5+5, 3+3+3+3+3. Marker 2 opcje: flaga (default) lub skrót z kolorem.
- **2026-04-30 rano**: Auto-tune font_size przez bisekcję: input = preferred_lines, output = optymalny font.
- **2026-04-30 rano**: Repo osobne (Pietraseq/etykiety-app), etykiety-svg jako git submodule.
- **2026-04-30 popołudnie**: Po feedbacku UI: marker auto-skaluje się z fontem (zamiast fixed 2.6mm) — naprawa nachodzenia na 2. linię przy auto-tune małego fontu.
- **2026-04-30 popołudnie**: Refactor edytowalnych ramek tekstowych (jeden `<text>` per blok, word-spacing dla justify) — w submodule etykiety-svg. Grafik dostaje 15 obiektów tekstowych do edycji w Illustratorze, nie tysiąc per-word tspans.
- **2026-04-30 wieczór**: Side-by-side UI: advanced (sliders+inputs synced) po lewej (25%), preview SVG (75%) po prawej z pomarańczową ramką strefy roboczej (tylko display, nie download).
- **2026-04-30 wieczór**: Suwak zoom podglądu 100% = rzeczywista wielkość mm (transform: scale w wrapperze) + guzik "Ustawienia domyślne" resetujący 7 dual_inputów.
- **2026-04-30 wieczór**: Codex w tle generuje 6 grafik (backgrounds day/night + 4× logo HappyLabel 1500). Decyzje: WebP 2560×1440 dla bg, PNG transparent dla logo (2 wymiary × 2 warianty light/dark), styl Happet split aesthetic, "by Pietras" jako attribution. Workflow Pietrasa: Claude planuje + przygotowuje prompt + czeka na zgodę → Codex wykonuje. **Logo Happet TYLKO tekstowy opis w prompcie** (Pietras nie ma pliku gotowego do `-i` flag).

## Streamlit chodzi w tle

- Background ID: `b5957tnon` (z poziomu Claude session). 
- Port: localhost:8501.
- Po zamknięciu sesji Claude proces może zostać żywy - kill manualnie przez Task Manager albo `Get-Process python` w PowerShellu.
