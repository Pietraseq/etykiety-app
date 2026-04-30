"""Streamlit UI - sekcja podgladu SVG + pobierania pliku.

Bierze parametry z render_settings_section, generuje SVG przez silnik
etykiety-svg (przez tempfile bo write_svg pisze do pliku), pokazuje live
preview w iframe i daje 2 download buttony:
- SVG (do Illustratora/Corelu)
- YAML (do reuse w etykiety-svg CLI)
"""

from __future__ import annotations

import io
import tempfile
from pathlib import Path

import streamlit as st
import yaml

from label_generator.layout import layout_page
from label_generator.svg_writer import write_svg

from src.logic.tuner import build_temp_config

PROJECT_ROOT = Path(__file__).resolve().parents[2] / "etykiety_svg"


def generate_svg_bytes(params: dict) -> bytes:
    """Generuj SVG bytes z parametrow z settings_section."""
    config = _build_config_from_params(params)
    page = layout_page(config, project_root=PROJECT_ROOT)

    # write_svg pisze do pliku - uzywamy tempfile zeby otrzymac bytes
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
        tmp_path = Path(f.name)
    try:
        write_svg(page, tmp_path)
        return tmp_path.read_bytes()
    finally:
        tmp_path.unlink(missing_ok=True)


def generate_yaml_bytes(params: dict, product_code: str) -> bytes:
    """Generuj YAML config dla reuse w etykiety-svg CLI.

    Wstawia rzeczywiste rozmiary i font po auto-tune zamiast placeholderow.
    """
    config = _build_config_from_params(params)
    data = config.model_dump(mode="python")
    data["product_code"] = product_code
    # Pydantic Path -> string dla czystego YAML
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
    """Wsadze build_temp_config (z tuner.py) z params + zaaplikuj optymalny font."""
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
    )


def render_preview_section(params: dict | None) -> None:
    """Render live preview + download buttons. Wymaga params z settings_section."""
    st.subheader("7. Podglad i pobranie SVG")

    if not params:
        st.info("Uzupelnij sekcje 1-6 (15 jezykow + ustawienia) zeby aktywowac generacje.")
        return

    col_a, col_b = st.columns([1, 2])
    with col_a:
        product_code = st.text_input(
            "Kod produktu (nazwa pliku)",
            value="etykieta",
            max_chars=30,
            key="product_code",
        )
    with col_b:
        st.caption(
            "Plik SVG: do Illustratora / CorelDraw. "
            "Plik YAML: do reuse w etykiety-svg CLI (power user)."
        )

    try:
        with st.spinner("Generuje SVG..."):
            svg_bytes = generate_svg_bytes(params)
    except Exception as e:
        st.error(f"Generacja nie powiodla sie: {e}")
        return

    try:
        yaml_bytes = generate_yaml_bytes(params, product_code or "etykieta")
    except Exception as e:
        st.warning(f"YAML nie wygenerowany: {e}")
        yaml_bytes = b""

    # Download buttony pierwsze - zeby grafik mogl pobrac od razu
    col1, col2, col3 = st.columns([1, 1, 1])
    col1.download_button(
        "Pobierz SVG",
        data=svg_bytes,
        file_name=f"{product_code or 'etykieta'}.svg",
        mime="image/svg+xml",
        type="primary",
        use_container_width=True,
    )
    if yaml_bytes:
        col2.download_button(
            "Pobierz YAML",
            data=yaml_bytes,
            file_name=f"{product_code or 'etykieta'}.yaml",
            mime="text/yaml",
            use_container_width=True,
        )
    col3.metric("Rozmiar SVG", f"{len(svg_bytes) / 1024:.1f} kB")

    # Live preview - SVG embedded inline
    st.markdown("**Podglad SVG (do otwarcia w Illustratorze / CorelDraw):**")
    svg_string = svg_bytes.decode("utf-8")
    # Wrapper z białym tlem - flagi sa kolorowe ale tekst czarny, na ciemnym tle
    # Streamlit moga byc nieczytelne
    html_wrapper = f"""
    <div style="background: white; padding: 20px; border-radius: 8px; max-width: 100%; overflow: auto;">
      {svg_string}
    </div>
    """
    st.components.v1.html(html_wrapper, height=750, scrolling=True)
