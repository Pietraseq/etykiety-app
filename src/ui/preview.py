"""Streamlit UI - kombinowana sekcja: zaawansowane + auto-tune + live preview.

Layout: st.columns([1, 3]) - po lewej zaawansowane (slider+input), po prawej
duzy podglad SVG z obramowka strefy roboczej. SVG width=100% wypelnia kolumne.
"""

from __future__ import annotations

import io
import re
import tempfile
from pathlib import Path

import streamlit as st
import yaml

from label_generator.layout import layout_page
from label_generator.svg_writer import write_svg

from src.logic.tuner import build_temp_config, find_optimal_font

from src.ui.widgets import dual_input

PROJECT_ROOT = Path(__file__).resolve().parents[2] / "etykiety_svg"

PREVIEW_HEIGHT_PX = 1500
WORKSPACE_OUTLINE_COLOR_OK = "#1976D2"        # niebieski - obszar tekstu (OK)
WORKSPACE_OUTLINE_COLOR_OVERFLOW = "#D32F2F"  # czerwony - tekst wystaje poza obszar
PAGE_OUTLINE_COLOR = "#111111"                # czarny - granica calej etykiety, kontrastowa

TEXT_AREA_X = 5.0
TEXT_AREA_Y = 5.0


def render_combined_section(basic_params: dict | None) -> None:
    """Render zaawansowane settings + auto-tune + podglad SVG w 2 kolumnach."""
    if not basic_params:
        return

    st.subheader("6. Modelowanie i podgląd")
    st.caption(
        "Zmieniaj parametry po lewej (suwak lub liczba) — podgląd po prawej "
        "aktualizuje się automatycznie. Niebieska ramka = obszar tekstu (strefa robocza), "
        "czarna ramka = krawędź etykiety. Ramki są tylko podglądem, NIE są zapisane w pliku SVG."
    )

    col_left, col_right = st.columns([1, 3])

    with col_left:
        advanced = _render_advanced_inputs()

    config_kwargs = {
        "layout_name": basic_params["layout"],
        "page_size": (advanced["page_w"], advanced["page_h"]),
        "text_area_size": (advanced["text_area_w"], advanced["text_area_h"]),
        "gutter_mm": advanced["gutter"],
        "marker_size_mm": advanced["marker_override"] if advanced["marker_override"] > 0 else None,
        "marker_style": basic_params["marker_style"],
        "marker_color": basic_params["marker_color"],
        "inter_block_gap_mm": advanced["inter_gap"] if advanced["inter_gap"] > 0 else None,
        "justify_full": basic_params.get("justify_full", True),
    }

    try:
        with col_left:
            with st.spinner("Bisekcja..."):
                optimal_font, lines_per_lang = find_optimal_font(
                    basic_params["translations"],
                    basic_params["preferred_lines"],
                    **config_kwargs,
                )
    except Exception as e:
        col_left.error(f"Bisekcja nie powiodła się: {e}")
        return

    max_lines = max(lines_per_lang.values()) if lines_per_lang else 0
    min_lines = min(lines_per_lang.values()) if lines_per_lang else 0
    is_feasible = max_lines <= basic_params["preferred_lines"]

    with col_left:
        if not is_feasible:
            st.error(
                f"### Etykieta niemożliwa\n\n"
                f"Najdłuższy język: **{max_lines}** wierszy zamiast preferowanych "
                f"**{basic_params['preferred_lines']}** (font {optimal_font:.2f} mm).\n\n"
                f"Możliwości:\n"
                f"- Skróć tekst źródłowy\n"
                f"- Zwiększ wysokość obszaru tekstu\n"
                f"- Zwiększ preferowaną liczbę wierszy\n"
                f"- Wybierz węższy layout"
            )
        else:
            st.success(f"Optymalny font: **{optimal_font:.2f} mm**")

        if min_lines == max_lines:
            st.markdown(f"**Wszystkie 15 języków: {min_lines} wierszy**")
        else:
            st.markdown(f"**Wszystkie 15 języków: {min_lines}-{max_lines} wierszy**")

        if not is_feasible:
            overflow_langs = [
                f"{code} ({n})" for code, n in lines_per_lang.items()
                if n > basic_params["preferred_lines"]
            ]
            if overflow_langs:
                st.markdown(f"**Wystają:** {', '.join(overflow_langs)}")

    full_params = {
        **basic_params,
        **config_kwargs,
        "optimal_font_mm": optimal_font,
        "lines_per_lang": lines_per_lang,
        "is_feasible": is_feasible,
    }

    with col_right:
        _render_preview_panel(full_params)


DEFAULTS = {
    "page_w": 219.96,
    "page_h": 160.10,
    "ta_w": 100.0,
    "ta_h": 145.0,
    "gutter": 3.0,
    "inter_gap": 0.0,
    "marker_override": 0.0,
    "pin_margin_mm": 5.0,
}

PIN_KEY = "pin_text_width_to_page"
PIN_MARGIN_KEY = "pin_margin_mm"


def _reset_defaults() -> None:
    """Resetuj wartości dual_inputów do defaultów przez wyczyszczenie session_state."""
    for key, val in DEFAULTS.items():
        st.session_state[key] = val
        if f"{key}__sl" in st.session_state:
            st.session_state[f"{key}__sl"] = val
        if f"{key}__ni" in st.session_state:
            st.session_state[f"{key}__ni"] = val
    st.session_state[PIN_KEY] = False


def _render_advanced_inputs() -> dict:
    """Render slider+number inputs w lewej kolumnie."""
    st.button(
        "Ustawienia domyślne",
        use_container_width=True,
        on_click=_reset_defaults,
        help="Przywróć wartości początkowe wszystkich parametrów.",
    )

    st.markdown("### Rozmiar etykiety")
    page_w = dual_input("Szerokość (mm)", 50.0, 300.0, DEFAULTS["page_w"], 0.1, "page_w", format="%.2f")
    page_h = dual_input("Wysokość (mm)", 30.0, 300.0, DEFAULTS["page_h"], 0.1, "page_h", format="%.2f")

    st.markdown("### Obszar dla tekstu")
    pin_to_page = st.checkbox(
        "Sprzęgnij szerokość obszaru tekstu z szerokością etykiety",
        key=PIN_KEY,
        help=(
            "Gdy włączone, szerokość obszaru tekstu = szerokość etykiety - 2 × margines. "
            "Zmiana szerokości etykiety automatycznie aktualizuje obszar tekstu."
        ),
    )

    if pin_to_page:
        margin = dual_input(
            "Margines (mm, lewy + prawy)",
            0.0, 50.0, DEFAULTS["pin_margin_mm"], 0.1, PIN_MARGIN_KEY, format="%.2f",
        )
        text_area_w = max(20.0, page_w - 2 * margin)
        st.caption(f"Szerokość obszaru tekstu (auto): **{text_area_w:.2f} mm**")
        # Synchronizuj pochodną wartość do session_state, żeby po wyłączeniu pinu
        # użytkownik miał ostatnio wyliczoną wartość w sliderze.
        st.session_state["ta_w"] = text_area_w
        for k in ("ta_w__sl", "ta_w__ni"):
            if k in st.session_state:
                st.session_state[k] = text_area_w
    else:
        text_area_w = dual_input("Szerokość (mm)", 20.0, 300.0, DEFAULTS["ta_w"], 0.1, "ta_w", format="%.2f")

    text_area_h = dual_input("Wysokość (mm)", 20.0, 300.0, DEFAULTS["ta_h"], 0.1, "ta_h", format="%.2f")

    st.markdown("### Odstępy")
    gutter = dual_input("Między kolumnami (mm)", 0.0, 20.0, DEFAULTS["gutter"], 0.1, "gutter", format="%.2f")
    inter_gap = dual_input(
        "Między językami (mm, 0 = auto)", 0.0, 10.0, DEFAULTS["inter_gap"], 0.1, "inter_gap", format="%.2f",
        help_text="0 = auto z fontu",
    )
    marker_override = dual_input(
        "Marker (mm, 0 = auto)", 0.0, 10.0, DEFAULTS["marker_override"], 0.1, "marker_override", format="%.2f",
        help_text="0 = auto = line_height",
    )

    return {
        "page_w": page_w,
        "page_h": page_h,
        "text_area_w": text_area_w,
        "text_area_h": text_area_h,
        "gutter": gutter,
        "inter_gap": inter_gap,
        "marker_override": marker_override,
    }


def _render_preview_panel(params: dict) -> None:
    """Render dużego SVG podglądu + download buttons w prawej kolumnie."""
    try:
        svg_bytes = generate_svg_bytes(params)
    except Exception as e:
        st.error(f"Generacja nie powiodła się: {e}")
        return

    try:
        yaml_bytes = generate_yaml_bytes(params, st.session_state.get("product_code", "etykieta"))
    except Exception:
        yaml_bytes = b""

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        product_code = st.text_input(
            "Kod produktu",
            value="etykieta",
            max_chars=30,
            key="product_code",
            label_visibility="collapsed",
            placeholder="Kod produktu (nazwa pliku)",
        )
    with c2:
        st.download_button(
            "SVG",
            data=svg_bytes,
            file_name=f"{product_code or 'etykieta'}.svg",
            mime="image/svg+xml",
            type="primary",
            use_container_width=True,
        )
    with c3:
        if yaml_bytes:
            st.download_button(
                "YAML",
                data=yaml_bytes,
                file_name=f"{product_code or 'etykieta'}.yaml",
                mime="text/yaml",
                use_container_width=True,
            )

    zoom_col, info_col = st.columns([3, 2])
    with zoom_col:
        zoom = st.slider(
            "Powiększenie podglądu (100% = rzeczywista wielkość)",
            min_value=50,
            max_value=500,
            value=200,
            step=25,
            format="%d%%",
            key="preview_zoom",
        )
    with info_col:
        st.caption(
            f"Rozmiar pliku: {len(svg_bytes) / 1024:.1f} kB | "
            f"Etykieta: {params['page_size'][0]:.1f} × {params['page_size'][1]:.1f} mm"
        )

    svg_string = svg_bytes.decode("utf-8")
    svg_for_preview = _prepare_svg_for_preview(svg_string, params)

    scale_factor = zoom / 100
    html_wrapper = f"""
    <div style="background: white; padding: 12px; border-radius: 8px; height: {PREVIEW_HEIGHT_PX}px; overflow: auto;">
      <div style="transform: scale({scale_factor}); transform-origin: top left; display: inline-block;">
        {svg_for_preview}
      </div>
    </div>
    """
    st.components.v1.html(html_wrapper, height=PREVIEW_HEIGHT_PX + 20, scrolling=True)


def _prepare_svg_for_preview(svg_string: str, params: dict) -> str:
    """Zmodyfikuj SVG do podglądu w przeglądarce.

    1. Outer rect (krawędź etykiety) - czarny, grubszy, kontrastowy.
    2. Inner rect (obszar tekstu) - niebieski OK / czerwony przy overflow.
    3. overflow="visible" na root <svg> - tekst poza viewbox jest widoczny
       (NIE jest obcinany), żeby grafik widział co wystaje.
    """
    text_area_w, text_area_h = params["text_area_size"]
    page_w, page_h = params["page_size"]
    is_feasible = params.get("is_feasible", True)

    # Stroke width w mm; krawedz etykiety grubsza i bardziej widoczna od strefy roboczej
    page_stroke = max(0.30, page_w * 0.0025)
    workspace_stroke = max(0.18, page_w * 0.0012)

    inner_color = WORKSPACE_OUTLINE_COLOR_OK if is_feasible else WORKSPACE_OUTLINE_COLOR_OVERFLOW
    inner_dash = "1.4,0.8" if is_feasible else "2,1"

    page_rect = (
        f'<rect x="0" y="0" '
        f'width="{page_w}" height="{page_h}" '
        f'fill="none" stroke="{PAGE_OUTLINE_COLOR}" '
        f'stroke-width="{page_stroke}" '
        f'opacity="0.95"/>'
    )
    workspace_rect = (
        f'<rect x="{TEXT_AREA_X}" y="{TEXT_AREA_Y}" '
        f'width="{text_area_w}" height="{text_area_h}" '
        f'fill="none" stroke="{inner_color}" '
        f'stroke-width="{workspace_stroke}" stroke-dasharray="{inner_dash}" '
        f'opacity="0.85"/>'
    )

    inject = f"{page_rect}\n{workspace_rect}"

    if "</title>" in svg_string:
        svg_string = svg_string.replace("</title>", f"</title>\n{inject}", 1)
    else:
        svg_string = re.sub(r'(<svg[^>]*>)', r'\1\n' + inject, svg_string, count=1)

    svg_string = re.sub(
        r'<svg(?![^>]*\soverflow=)([^>]*)>',
        r'<svg\1 overflow="visible">',
        svg_string,
        count=1,
    )

    return svg_string


def generate_svg_bytes(params: dict) -> bytes:
    config = _build_config_from_params(params)
    page = layout_page(config, project_root=PROJECT_ROOT)
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
        tmp_path = Path(f.name)
    try:
        write_svg(page, tmp_path)
        return tmp_path.read_bytes()
    finally:
        tmp_path.unlink(missing_ok=True)


def generate_yaml_bytes(params: dict, product_code: str) -> bytes:
    config = _build_config_from_params(params)
    data = config.model_dump(mode="python")
    data["product_code"] = product_code
    if "font" in data and "path" in data["font"]:
        data["font"]["path"] = str(data["font"]["path"]).replace("\\", "/")
    if "font" in data and data["font"].get("bold_path"):
        data["font"]["bold_path"] = str(data["font"]["bold_path"]).replace("\\", "/")
    if "flags" in data and "path" in data["flags"]:
        data["flags"]["path"] = str(data["flags"]["path"]).replace("\\", "/")
    buf = io.StringIO()
    yaml.safe_dump(data, buf, allow_unicode=True, sort_keys=False, default_flow_style=False)
    return buf.getvalue().encode("utf-8")


def _build_config_from_params(params: dict):
    return build_temp_config(
        params["translations"],
        font_size_mm=params["optimal_font_mm"],
        layout_name=params["layout_name"],
        page_size=params["page_size"],
        text_area_size=params["text_area_size"],
        gutter_mm=params["gutter_mm"],
        marker_size_mm=params["marker_size_mm"],
        marker_style=params["marker_style"],
        marker_color=params["marker_color"],
        inter_block_gap_mm=params.get("inter_block_gap_mm"),
        justify_full=params.get("justify_full", True),
    )
