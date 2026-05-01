# MEMORY.md — etykiety-app

Aktualny stan prac. Ostatnia aktualizacja: 2026-05-01 (sesja domowy PC, rano)

## Co działa (E2E)

- **Faza A**: scaffold + submodule etykiety-svg + Streamlit Hello World
- **Faza B**: prompt template + parser AI + UI tłumaczenia. Workflow: textarea → "Skopiuj prompt" → AI → wklej → 15 textarea edytowalnych
- **Faza C**: settings UI (layout: 8+7, 5+5+5, 3+3+3+3+3, **15** jedna kolumna; marker flag/text+color; preferred_lines 1-10) + auto-tune bisekcja font_size
- **Faza D**: live preview SVG + download (SVG/YAML)
- **UI redesign**: side-by-side advanced+preview (kolumny 1:3), suwaki + number_inputs synced (helper `dual_input`), pomarańczowa ramka strefy roboczej w preview, suwak powiększenia 50-500% (default 200%), guzik "Ustawienia domyślne", banner "Etykieta niemożliwa"
- **Branding HappyLabel**: logo banner w headerze (4 warianty: banner/square × light/dark), background day/night zsynchronizowane z ręcznym toggle Dzień/Noc obok loga (auto-detect Streamlit theme zawiódł — `theme.base` jest config-time, `st.context.theme.type` w 1.57 nie odpowiada na user-toggle)
- **Tryb format gotowych tłumaczeń**: drugi tryb radio obok "Przetłumacz z PL/EN" — wkleja luźny tekst, AI tylko normalizuje format `KOD === tekst` (bez tłumaczenia)
- **Submodule etykiety-svg**: bumped 3x (le=4→le=10 dla columns, marker_size clamp do line_height, inter_block_gap_mm jako opcjonalny)
- **32/32 testów PASS** (parser 18 + tuner 11 + format prompt 3)
- **Repo**: https://github.com/Pietraseq/etykiety-app (private), submodule etykiety-svg

## Zmiany sesji 2026-05-01 rano (domowy PC)

- **Strefa robocza w preview**: pomarańczowa → niebieska (`#1976D2`). Czerwona (`#D32F2F`) zostaje przy overflow.
- **Krawędź etykiety w preview**: jasna szara → czarna (`#111111`), grubsza (`stroke = page_w * 0.0025`).
- **Pin szerokości obszaru tekstu do szerokości etykiety**: checkbox + margines (mm). Gdy włączony, slider „Szerokość obszaru tekstu" ukryty, wartość liczona automatycznie z `page_w - 2 × margin` i wyświetlana jako caption.
- **Justify toggle (UI + silnik)**: radio „Wyjustowany na całą szerokość" / „Wyrównany do lewej". W silniku `etykiety-svg`: nowe pole `LabelConfig.justify_full: bool = True`, parametr `wrap_and_justify(..., justify_full)`. Gdy False — wszystkie linie mają `word_spacing_mm = 0`.
- **Preferowana liczba wierszy**: wyciągnięta z `st.columns(3)` do osobnej sekcji `#### Preferowana liczba wierszy w bloku` z dużą kolumną slidera + boczną etykietą `N wiersz/wierszy` w dużej czcionce (1.6rem). Wcześniej była zwykłym `number_input` wciśniętym obok marker_color.
- **Hinty bez przykładów w nawiasach**: usunięto „(jak D609)", „(jak HappSnack)", „Np. 'Single-use, oxygen-activated heat pack...'" — placeholdery generyczne zamiast specyficznych przykładów.
- **„by Pietras" — REWIZJA decyzji**: Pietras chce żeby BYŁA atrybucja widoczna (zaprzeczył poprzedniemu odrzuceniu, „wcześniej go nie widziałem a chcę to"). Footer rozbudowany: PNG `branding/by-pietras-dark.png` w prawym dolnym rogu, opacity 0.92, height 36px (było 22px), tło z blur, padding, border-radius. Pliki branding/by-pietras-* ZOSTAJĄ.
- **Polskie znaki w UI**: cały user-facing layer (preview.py, settings.py, translate.py) zamieniony z ASCII-only („Wpisz tekst zrodlowy") na poprawną polszczyznę z diakrytykami („Wpisz tekst źródłowy"). Docstringi i prompt do AI bez zmian (dev-facing / EN).
- **Polish error handling w app.py**: wrap głównej sekcji w try/except z `st.exception(e)` i przyjazną wiadomością. Komunikat błędu submodule rozbudowany z instrukcją naprawy.
- **README.md**: pełen walkthrough grafika 12 kroków, sekcja „Funkcje zaawansowane" (pin/zoom/ramki/feasibility), tabela rozwiązywania problemów. Wcześniej był skrót.
- **Submodule etykiety-svg bumped do `6ad5ba7`**: dodano `justify_full` toggle, push na main.

## Aktualne problemy

- **Codex sandbox bug na Windows**: `--sandbox workspace-write` powoduje `CreateProcessAsUserW failed: 1920` przy każdej próbie shell call. Workaround: `--sandbox danger-full-access`. To prawdopodobnie zabiło `bnmn0w53a` w poprzedniej sesji (foldery `assets/` były puste mimo wygenerowania obrazów do `~/.codex/generated_images/`). Powtórzone dziś (2026-05-01) — `codex exec` pada na `Get-Job`.
- **Streamlit auto theme detection nie działa**: w 1.57.0 `st.context.theme.type` nie odpowiada na user-toggle System/Light/Dark, `theme.base` jest config-time. Dlatego ręczny toggle Dzień/Noc w headerze (default Dzień).

## Do zrobienia (next session)

- [ ] Test grafików E2E na realnej etykiecie nowego produktu — to musi zrobić Pietras na produkcji
- [ ] Decyzja o hostingu: lokalnie vs Streamlit Cloud
- [ ] Drugi PC (praca): `git pull origin main` + `git submodule update --init --recursive` żeby zsynchronizować

## Aktualne problemy

- **Codex sandbox bug na Windows**: `--sandbox workspace-write` powoduje `CreateProcessAsUserW failed: 1920` przy każdej próbie shell call. Workaround: `--sandbox danger-full-access`. To prawdopodobnie zabiło `bnmn0w53a` w poprzedniej sesji (foldery `assets/` były puste mimo wygenerowania obrazów do `~/.codex/generated_images/`).
- **Streamlit auto theme detection nie działa**: w 1.57.0 `st.context.theme.type` nie odpowiada na user-toggle System/Light/Dark, `theme.base` jest config-time. Dlatego ręczny toggle Dzień/Noc w headerze (default Dzień).

## Znane ograniczenia

- Tłumaczenia ręczne przez prompt do AI (bez API integration) - świadoma decyzja architektoniczna
- Streamlit nie obsługuje drag&drop reordering języków - manualnie w YAML jeśli potrzebne
- Codex skill `imagegen` w `~/.codex/skills/.system/` - pre-installed system skill, używany w tej sesji do logo i tła
- Day mode: overlay alpha 0.92 + wymuszony ciemny tekst CSS (`!important`) — bo Streamlit theme.base=dark może dominować nad user-toggle Light. Tradeoff: tło day jest prawie niewidoczne pod overlayem, ale UI czytelne.

## Historia decyzji

- **2026-04-30 rano**: Start projektu po zamknięciu MVP `etykiety-svg`. Stack: Streamlit + Python 3.13 + git submodule etykiety-svg.
- **2026-04-30 rano**: Tłumaczenia bez API (DeepL/OpenAI) - generujemy prompt który grafik kopiuje do swojego AI, aplikacja parsuje odpowiedź. Format: `KOD === tekst` per linia.
- **2026-04-30 rano**: Layout 3 opcje (8+7, 5+5+5, 3+3+3+3+3). Marker 2 opcje: flaga (default) lub skrót z kolorem.
- **2026-04-30 rano**: Auto-tune font_size przez bisekcję: input = preferred_lines, output = optymalny font.
- **2026-04-30 rano**: Repo osobne (Pietraseq/etykiety-app), etykiety-svg jako git submodule.
- **2026-04-30 popołudnie**: Marker auto-skaluje się z fontem (zamiast fixed 2.6mm).
- **2026-04-30 popołudnie**: Refactor edytowalnych ramek tekstowych (jeden `<text>` per blok, word-spacing dla justify) — w submodule etykiety-svg.
- **2026-04-30 wieczór (praca)**: Side-by-side UI advanced+preview, suwak zoom podglądu, guzik "Ustawienia domyślne".
- **2026-04-30 wieczór (praca)**: Codex bg job nr 1 (`bnmn0w53a`) zaplanowany do generacji 6 grafik — sesja zakończyła się przed weryfikacją statusu.
- **2026-04-30 wieczór (dom)**: Klon obu repo na domowym PC. Cross-PC test: `git submodule update --init --recursive` + venv + `streamlit run app.py` — działa od razu, 29/29 testów PASS.
- **2026-04-30 wieczór (dom)**: Pietras dał logo Happet (3000×900 PNG, wklejone do chatu) jako visual reference dla Codexa. Zapisane lokalnie w `_brand-ref/happet-logo.png` (gitignored).
- **2026-04-30 wieczór (dom)**: Maskotka HappyLabel = **mątwa** (cuttlefish). Pietras: każdemu narzędziu w pracy chce przypisywać zwierzę.
- **2026-04-30 wieczór (dom)**: Backgrounds day/night = dwa osobne obrazy (toggle), nie split na jednym. Aplikacja zmienia tło zależnie od wybranego trybu UI.
- **2026-04-30 wieczór (dom)**: Codex bg job nr 2 (`bcal0ujvm`) z `--sandbox workspace-write` zacinał się na `CreateProcessAsUserW failed: 1920` — Windows sandbox bug. Restart z `--sandbox danger-full-access` (`b4n9hvz0o`) zadziałał: 6 plików dostarczonych, walidacja OK.
- **2026-04-30 wieczór (dom)**: "by Pietras" attribution **odrzucone** — Pietras nie chce podpisu na grafikach.
- **2026-05-01 rano (dom)**: REWIZJA — "by Pietras" w UI/footer **wraca**. Pietras: "wcześniej go nie widziałem a chcę to". Footer wyższy (36px, było 22px), opacity 0.92 (było 0.55), tło z blur. Pliki `branding/by-pietras-*` zostają. Atrybucja jest TYLKO w UI (overlay), NIE jest wstrzykiwana do generowanego SVG.
- **2026-04-30 wieczór (dom)**: Tryb format gotowych tłumaczeń (drugi obok translate). Pietras: czasem ma już 15 tłumaczeń sprawdzone, AI tylko formatuje.
- **2026-04-30 wieczór (dom)**: Layout "15" (jedna kolumna, wszystkie języki pod sobą) dodany do LAYOUT_CHOICES.
- **2026-04-30 wieczór (dom)**: Guzik "Pełen ekran" w preview usunięty (nie działał, niepotrzebny).
- **2026-04-30 wieczór (dom)**: Day mode czytelność: overlay 0.92 + wymuszony ciemny tekst (`color: #1f1f1f !important`). Auto-detect theme zastąpiony własnym radio Dzień/Noc.
- **2026-04-30 wieczór (dom)**: Codex bg job nr 3 (`bkel16rtz`) re-run dla 4 plików logo — fix paddingu "Label" w bloku negatywowym (litery wystawały).

## Cross-PC sync

- **Domowy PC**: `git pull` przy starcie, `streamlit run app.py` → http://localhost:8501
- **Praca PC**: `git pull origin main` + `git submodule update --remote etykiety_svg` żeby zsynchronizować
- Wszystkie zmiany pushowane na main automatycznie po każdej zamkniętej zmianie.

## Streamlit chodzi w tle

- W aktualnej sesji (Claude domowy PC): port 8501. Po zamknięciu sesji proces może zostać żywy — kill przez Task Manager albo `Get-Process python` w PowerShellu.
