# Kontekst biznesowy — etykiety-app

## Problem

`etykiety-svg` (silnik renderowania) wymaga ręcznego pisania YAML z 15 językami i znajomości stacku (Python venv, CLI). Grafik Happet nie zna Pythona i nie powinien być zmuszany do edycji YAML.

Realnie: każda nowa etykieta wymaga przepisania 15 wariantów językowych (z Wordu / od kontrahentów / przez Google Translate ręcznie), wybrania layoutu kolumn, dostrojenia rozmiaru fontu pod liczbę wierszy. Bez UI = grafik zostanie odcięty od narzędzia, Pietras musi wszystko robić sam.

## Cel

1. **Aplikacja webowa** (lokalnie / Streamlit Cloud) gdzie grafik wkleja tekst PL lub EN, wybiera layout i styl, dostaje gotowy SVG do pobrania w <2 min
2. **Tłumaczenia bezkosztowe** — nie integrujemy się z DeepL/OpenAI płatnym, zamiast tego generujemy gotowy prompt który grafik kopiuje do dowolnego AI (ChatGPT/Claude.ai/Gemini, ich własne darmowe konto)
3. **Auto-tune font_size** — grafik wpisuje "preferuję 4 wiersze", aplikacja sama bisekcyjnie znajduje rozmiar fontu, przy którym **najdłuższy** język ma ≤ 4 wierszy
4. **Działanie w przyszłości** — niezależne od konkretnej osoby, bez ukrytych konfiguracji, łatwe do uruchomienia na nowym PC (`git clone --recursive` + `streamlit run app.py`)

## Skala

- 1 grafik Happet (na razie), w przyszłości potencjalnie 2-3 osoby
- Częstotliwość: kilka etykiet w miesiącu (sporadycznie więcej przy nowych liniach produktów)
- 15 języków per etykieta (default), z możliwością rozszerzenia w przyszłości (ISO 639-1)
- 1 instancja, lokalnie lub na Streamlit Cloud (jednoosobowy hosting bezpłatny)

## Osoby

- Pietras — wszystko (PM, dev, ops). Decyzje produktowe, kod, hosting.
- Grafik Happet — odbiorca aplikacji. Edytuje teksty, dobiera layout, generuje SVG. Nie zna Pythona.
- AI (ChatGPT/Claude.ai) — tłumacz w pętli ręcznej. Grafik kopiuje prompt, wkleja, kopiuje wynik.

## Dlaczego to rozwiązanie a nie inne

**Wybrane: Streamlit + prompt do AI (manualny copy-paste) + git submodule etykiety-svg**

Odrzucone:
- **DeepL API** — 500K znaków/mies darmowe, ale wymaga konta, API key, billing setup. Pietras nie chce uzależniać workflow od cudzego API. Plus jakość tłumaczeń idiomatycznych ChatGPT/Claude bywa lepsza dla "marketingowego" tonu Happet.
- **Google Translate API** — płatne od 1. znaku, słabsze dla EU języków niż DeepL.
- **Hardcoded 15 textarea bez tłumaczeń** — grafik musiałby ręcznie przepisać 15x z innego źródła. Strata czasu.
- **React + FastAPI** — lepsze "na zawsze" ale ~tydzień pracy na sam UI. Streamlit MVP w 1-2 dni, jak grafik potwierdzi, że workflow ma sens, można migrować.
- **Desktop app (Tauri)** — wymaga build pipeline + dystrybucji `.exe`. Web app + lokalny `streamlit run` jest prostszy w dystrybucji (link do GitHubu wystarczy).
- **Monolit z `etykiety-svg` w jednym repo** — miesza UI logikę z silnikiem renderowania. Submodule daje czyste rozdzielenie i pozwala silnik rozwijać niezależnie (np. dla innych klientów / projektów Pietrasa).
