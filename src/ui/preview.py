"""Streamlit UI - kombinowana sekcja: zaawansowane ustawienia + auto-tune + live preview.

Layout: st.columns([2, 3]) - po lewej zaawansowane (page_size, text_area,
gutter, inter_block_gap, marker_override), po prawej duzy live preview SVG.
Auto-tune w tle - bisekcja na font_size po kazdej zmianie inputu.

Pietras moze klikac slidery / inputy po lewej i widziec efekt po prawej.
"""

from __future__ import annotations

import base64
import io
import re
import tempfile
from pathlib import Path

import streamlit as st
import yaml

from label_generator.layout import layout_page
from label_generator.svg_writer import write_svg

from src.logic.prompt_template import LANGUAGES
from src.logic.tuner import build_temp_config, find_optimal_font

PROJECT_ROOT = Path(__file__).resolve().parents[2] / "etykiety_svg"

# Powiekszenie SVG w preview - 220mm SVG przy 1mm=3.78px wynosi ~830px,
# scale 2.5 daje ~2080px -> sporo przestrzeni dla detali, scrolluje sie.
PREVIEW_SCALE = 2.5
PREVIEW_HEIGHT_PX = 1500


def render_combined_section(basic_params: dict | None) -> None:
    """Render zaawansowane settings + auto-tune + preview SVG w 2 kolumnach."""
    if not basic_params:
        return

    st.subheader("6. Modelowanie i podglad")
    st.caption(
        "Zmieniaj parametry po lewej - podglad po prawej aktualizuje sie automatycznie."
    )

    col_left, col_right = st.columns([2, 3])

    with col_left:
        advanced = _render_advanced_inputs()

    # Pelna konfiguracja
    config_kwargs = {
        "layout_name": basic_params["layout"],
        "page_size": (advanced["page_w"], advanced["page_h"]),
        "text_area_size": (advanced["text_area_w"], advanced["text_area_h"]),
        "gutter_mm": advanced["gutter"],
        "marker_size_mm": advanced["marker_override"] if advanced["marker_override"] > 0 else None,
        "marker_style": basic_params["marker_style"],
        "marker_color": basic_params["marker_color"],
        "inter_block_gap_mm": advanced["inter_gap"] if advanced["inter_gap"] > 0 else None,
    }

    # Auto-tune
    try:
        with col_left:
            with st.spinner("Bisekcja..."):
                optimal_font, lines_per_lang = find_optimal_font(
                    basic_params["translations"],
                    basic_params["preferred_lines"],
                    **config_kwargs,
                )
    except Exception as e:
        col_left.error(f"Bisekcja nie powiodla sie: {e}")
        return

    max_lines = max(lines_per_lang.values()) if lines_per_lang else 0
    min_lines = min(lines_per_lang.values()) if lines_per_lang else 0
    is_feasible = max_lines <= basic_params["preferred_lines"]

    # Status auto-tune w lewej kolumnie - 1 linia
    with col_left:
        if not is_feasible:
            st.error(
                f"### Etykieta niemozliwa\n\n"
                f"Najdluzszy jezyk ma **{max_lines}** wierszy zamiast preferowanych "
                f"**{basic_params['preferred_lines']}**, nawet przy foncie {optimal_font:.2f}mm.\n\n"
                f"Mozliwe rozwiazania:\n"
                f"- Skroc tekst zrodlowy (sekcja 1)\n"
                f"- Zwieksz wysokosc obszaru tekstu\n"
                f"- Zwieksz preferowana liczbe wierszy\n"
                f"- Wybierz wezszy layout (np. 5+5+5)"
            )
        else:
            st.success(f"Optymalny font: **{optimal_font:.2f} mm**")

        # Wiersze per jezyk - 1 linia summary (Pietras: "informacyjnie ze wszystkie razem")
        if min_lines == max_lines:
            st.markdown(f"**Wszystkie 15 jezykow: {min_lines} wierszy**")
        else:
            st.markdown(f"**Wszystkie 15 jezykow: {min_lines}-{max_lines} wierszy**")

        # Lista jezykow ktore wystaja (tylko gdy niefeasible)
        if not is_feasible:
            overflow_langs = [
                f"{code} ({n})" for code, n in lines_per_lang.items()
                if n > basic_params["preferred_lines"]
            ]
            if overflow_langs:
                st.markdown(f"**Wystaja:** {', '.join(overflow_langs)}")

    # Generacja SVG + preview po prawej
    full_params = {
        **basic_params,
        **config_kwargs,
        "optimal_font_mm": optimal_font,
        "lines_per_lang": lines_per_lang,
        "is_feasible": is_feasible,
    }

    with col_right:
        _render_preview_panel(full_params)


def _render_advanced_inputs() -> dict:
    """Render inputow zaawansowanych w lewej kolumnie. Compact layout."""
    st.markdown("**Rozmiar etykiety (mm)**")
    a, b = st.columns(2)
    page_w = a.number_input("Szer.", value=219.96, min_value=50.0, key="page_w", label_visibility="visible")
    page_h = b.number_input("Wys.", value=160.10, min_value=30.0, key="page_h", label_visibility="visible")

    st.markdown("**Obszar dla tekstu (mm)**")
    a, b = st.columns(2)
    text_area_w = a.number_input("Szer. ", value=100.0, min_value=20.0, key="ta_w")
    text_area_h = b.number_input("Wys. ", value=145.0, min_value=20.0, key="ta_h")

    st.markdown("**Odstepy (mm)**")
    gutter = st.number_input(
        "Miedzy kolumnami",
        value=3.0, min_value=0.0, step=0.5,
        key="gutter",
    )
    inter_gap = st.number_input(
        "Miedzy jezykami (0 = auto)",
        value=0.0, min_value=0.0, step=0.2,
        key="inter_gap",
        help="0 = auto z fontu. Wyzsza wartosc rozsuwa bloki jezykowe.",
    )
    marker_override = st.number_input(
        "Marker (0 = auto)",
        value=0.0, min_value=0.0, max_value=10.0, step=0.1,
        key="marker_override",
        help="0 = auto = line_height. >0 = override (clamped do line_height w silniku).",
    )

    return {
        "page_w": float(page_w),
        "page_h": float(page_h),
        "text_area_w": float(text_area_w),
        "text_area_h": float(text_area_h),
        "gutter": float(gutter),
        "inter_gap": float(inter_gap),
        "marker_override": float(marker_override),
    }


def _render_preview_panel(params: dict) -> None:
    """Render duzego SVG preview + download buttons w prawej kolumnie."""
    try:
        svg_bytes = generate_svg_bytes(params)
    except Exception as e:
        st.error(f"Generacja nie powiodla sie: {e}")
        return

    try:
        yaml_bytes = generate_yaml_bytes(params, st.session_state.get("product_code", "etykieta"))
    except Exception:
        yaml_bytes = b""

    # Toolbar: kod produktu + download buttons
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
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
    with c4:
        svg_b64 = base64.b64encode(svg_bytes).decode("ascii")
        data_url = f"data:image/svg+xml;base64,{svg_b64}"
        st.markdown(
            f'<a href="{data_url}" target="_blank" '
            f'style="display:inline-block;padding:8px 12px;background:#262730;'
            f'color:white;text-decoration:none;border-radius:4px;text-align:center;'
            f'width:100%;box-sizing:border-box;font-size:0.9em;">Pelen ekran</a>',
            unsafe_allow_html=True,
        )

    st.caption(f"Rozmiar: {len(svg_bytes) / 1024:.1f} kB | scale {PREVIEW_SCALE}x ({PREVIEW_HEIGHT_PX}px wys.)")

    # Powiekszony SVG - usuwam fixed width/height z root SVG, scale 2.5x
    svg_string = svg_bytes.decode("utf-8")
    # Remove width/height attrs z root svg (zostawiam viewBox)
    svg_for_preview = re.sub(r'\swidth="[^"]+mm"', "", svg_string, count=1)
    svg_for_preview = re.sub(r'\sheight="[^"]+mm"', "", svg_for_preview, count=1)

    html_wrapper = f"""
    <div style="background: white; padding: 10px; border-radius: 8px; overflow: auto; height: {PREVIEW_HEIGHT_PX}px;">
      <div style="transform: scale({PREVIEW_SCALE}); transform-origin: top left; width: {100/PREVIEW_SCALE}%;">
        {svg_for_preview}
      </div>
    </div>
    """
    st.components.v1.html(html_wrapper, height=PREVIEW_HEIGHT_PX + 20, scrolling=True)


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
    )
