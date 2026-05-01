"""Emisja SVG przez lxml.

Strukturalnie:
- root <svg width="Wmm" height="Hmm" viewBox="0 0 W H">
- per-jezyk <g id="lang-XX" inkscape:label="XX">
  - <rect> czerwony kwadracik
  - <text> kod kraju (bold, white) na kwadraciku
  - per-linia <text> + per-slowo <tspan x y>

Atrybuty warstwowe podwojone: id (Corel) + inkscape:label (Adobe Illustrator).
Wspolrzedne zaokraglone do 3 miejsc po przecinku - deterministyczny output.
"""

from __future__ import annotations

from pathlib import Path

from lxml import etree

from .flags import build_flag_defs
from .layout import LanguageBlock, Page

INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"
SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"

NSMAP = {
    None: SVG_NS,
    "inkscape": INKSCAPE_NS,
    "xlink": XLINK_NS,
}


def write_svg(page: Page, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    svg = etree.Element(
        "svg",
        nsmap=NSMAP,
        attrib={
            "width": f"{_r(page.width_mm)}mm",
            "height": f"{_r(page.height_mm)}mm",
            "viewBox": f"0 0 {_r(page.width_mm)} {_r(page.height_mm)}",
        },
    )

    title = etree.SubElement(svg, "title")
    title.text = "etykiety-svg generated label"

    # <defs> z flagami + clipPath circle (potrzebne dla flag_circle / flag_rect)
    if page.prefix.style.startswith("flag") and page.prefix.flags_dir is not None:
        flag_codes = [b.flag_code for b in page.blocks]
        defs = build_flag_defs(page.prefix.flags_dir, flag_codes)
        svg.append(defs)

    for block in page.blocks:
        svg.append(_render_block(block, page))

    tree = etree.ElementTree(svg)
    tree.write(
        str(output_path),
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=True,
    )


def _render_block(block: LanguageBlock, page: Page) -> etree._Element:
    g = etree.Element(
        "g",
        attrib={
            "id": f"lang-{block.code.lower()}",
            f"{{{INKSCAPE_NS}}}label": block.code,
        },
    )

    # Marker wertykalnie wycentrowany na cap-height pierwszej linii.
    # Clamp do line_height zeby uniknac nachodzenia na 2. linie - jesli config
    # podaje wieksza wartosc, ograniczamy effective do line_height.
    requested_size = block.marker_size_mm
    effective_size = min(requested_size, block.line_height_mm)
    ascender = page.font_metrics.ascender_mm
    cap_height = page.font_metrics.cap_height_mm
    cap_top = block.y_mm + ascender - cap_height
    cap_center = cap_top + cap_height / 2
    marker_top = cap_center - effective_size / 2
    marker_x = block.x_mm
    marker_size = effective_size

    style = page.prefix.style
    if style == "text_rect":
        _append_text_rect(g, marker_x, marker_top, marker_size, block.code, page)
    elif style == "flag_circle":
        _append_flag_use(g, marker_x, marker_top, marker_size, block.flag_code, clip="circle")
    elif style == "flag_rect":
        _append_flag_use(g, marker_x, marker_top, marker_size, block.flag_code, clip=None)
    elif style == "flag_rounded":
        _append_flag_use(
            g, marker_x, marker_top, marker_size, block.flag_code,
            clip="rounded", rect_radius=page.prefix.rect_radius_mm,
        )
    else:
        raise ValueError(f"Nieznany prefix_marker.style: {style}")

    # Jeden <text> per blok = jedna edytowalna ramka tekstowa w Illustratorze.
    # N <tspan> per linia: 1. linia ma x=po fladze, kolejne x=0 (outdent).
    # Justyfikacja przez word-spacing (extra do kazdej spacji), nie per-slowo X.
    if not block.lines:
        return g

    text_el = etree.SubElement(
        g,
        "text",
        attrib={
            "font-family": "Arial, Helvetica, sans-serif",
            "font-size": f"{_r(page.font_metrics.size_mm)}",
            "fill": "#000000",
        },
    )

    for line_idx, line in enumerate(block.lines):
        if line_idx == 0:
            line_x_abs = block.x_mm + block.marker_size_mm + block.gap_mm + line.x_mm
        else:
            line_x_abs = block.x_mm + line.x_mm

        attrib: dict[str, str] = {"x": f"{_r(line_x_abs)}"}
        if line_idx == 0:
            attrib["y"] = f"{_r(block.y_mm + ascender)}"
        else:
            attrib["dy"] = f"{_r(block.line_height_mm)}"
        if line.word_spacing_mm > 0:
            attrib["word-spacing"] = f"{_r(line.word_spacing_mm)}"

        tspan = etree.SubElement(text_el, "tspan", attrib=attrib)
        tspan.text = line.text

    return g


def _append_text_rect(
    g: etree._Element,
    x: float,
    y: float,
    size: float,
    code: str,
    page: "Page",
) -> None:
    etree.SubElement(
        g,
        "rect",
        attrib={
            "x": f"{_r(x)}",
            "y": f"{_r(y)}",
            "width": f"{_r(size)}",
            "height": f"{_r(size)}",
            "fill": page.prefix.color,
        },
    )
    code_font_size = size * 0.7
    code_text = etree.SubElement(
        g,
        "text",
        attrib={
            "x": f"{_r(x + size / 2)}",
            "y": f"{_r(y + size * 0.78)}",
            "font-family": "Arial, Helvetica, sans-serif",
            "font-size": f"{_r(code_font_size)}",
            "font-weight": "bold" if page.prefix.bold else "normal",
            "fill": page.prefix.text_color,
            "text-anchor": "middle",
        },
    )
    code_text.text = code


def _append_flag_use(
    g: etree._Element,
    x: float,
    y: float,
    size: float,
    flag_code: str,
    clip: str | None = None,
    rect_radius: float = 0.0,
) -> None:
    """Dodaj <use href="#flag-XX"> z opcjonalnym clipPathem (circle / rounded)."""
    attrib = {
        "x": f"{_r(x)}",
        "y": f"{_r(y)}",
        "width": f"{_r(size)}",
        "height": f"{_r(size)}",
        f"{{{XLINK_NS}}}href": f"#flag-{flag_code}",
        "href": f"#flag-{flag_code}",
    }
    if clip == "circle":
        attrib["clip-path"] = "url(#flag-circle)"
    use = etree.SubElement(g, "use", attrib=attrib)
    if clip == "rounded":
        # Rounded rect via osobny clipPath inline (per-blok wymiary w mm)
        # Generujemy unikalny clipPath id per blok zeby nie kolidowac
        unique_id = f"flag-rounded-{flag_code}-{int(round(y * 1000))}"
        clip_el = etree.SubElement(
            g,
            "clipPath",
            attrib={"id": unique_id},
        )
        etree.SubElement(
            clip_el,
            "rect",
            attrib={
                "x": f"{_r(x)}",
                "y": f"{_r(y)}",
                "width": f"{_r(size)}",
                "height": f"{_r(size)}",
                "rx": f"{_r(rect_radius)}",
                "ry": f"{_r(rect_radius)}",
            },
        )
        use.set("clip-path", f"url(#{unique_id})")
        # clipPath musi byc PRZED <use>, lxml SubElement append'uje na koniec.
        # Reorder: usun use, dodaj clip, ponownie use.
        g.remove(use)
        g.append(use)


def _r(value: float) -> str:
    """Zaokraglenie do 3 miejsc po przecinku - deterministyczny output."""
    return f"{round(value, 3):g}"
