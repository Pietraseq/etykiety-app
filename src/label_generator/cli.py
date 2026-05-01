"""CLI: `python -m label_generator <config.yaml> -o <output.svg>`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import LabelConfig
from .layout import layout_page
from .svg_writer import write_svg


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="label_generator",
        description="Generator wielojezycznych etykiet SVG (Happet).",
    )
    parser.add_argument(
        "config",
        type=Path,
        help="Sciezka do pliku YAML z definicja etykiety",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Sciezka do wynikowego pliku SVG",
    )
    parser.add_argument(
        "-s",
        "--marker-style",
        choices=["flag_circle", "flag_rect", "flag_rounded", "text_rect"],
        default=None,
        help="Override prefix_marker.style z YAML (np. text_rect dla wersji ze skrotem kraju)",
    )
    args = parser.parse_args(argv)

    config_path: Path = args.config.resolve()
    if not config_path.is_file():
        print(f"BLAD: brak pliku konfigu: {config_path}", file=sys.stderr)
        return 2

    config = LabelConfig.load(config_path)
    if args.marker_style is not None:
        config.prefix_marker.style = args.marker_style
    project_root = _find_project_root(config_path)

    page = layout_page(config, project_root=project_root)
    output_path: Path = args.output.resolve()
    write_svg(page, output_path)

    n_lines = sum(len(b.lines) for b in page.blocks)
    print(
        f"OK: {output_path}  | {len(page.blocks)} blokow jezykowych, "
        f"{n_lines} linii tekstu, page {page.width_mm}x{page.height_mm}mm"
    )
    return 0


def _find_project_root(config_path: Path) -> Path:
    """Znajdz root projektu - katalog zawierajacy folder `fonts/` lub `.git`."""
    current = config_path.parent.resolve()
    for parent in [current, *current.parents]:
        if (parent / "fonts").is_dir() or (parent / ".git").exists():
            return parent
    # Fallback: katalog konfigu
    return current


if __name__ == "__main__":
    raise SystemExit(main())
