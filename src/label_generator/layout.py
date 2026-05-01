"""Uklad bloku jezykowego + 2-kolumnowy flow.

`LanguageBlock` to jeden jezyk z czerwonym kwadracikiem-prefixem. Linia 1 ma
wezszy zakres (zostawia miejsce na kwadracik), linie 2+ wracaja do lewej
krawedzi kwadracika - klasyczny outdent.

Page robi greedy first-fit po kolumnach. Gdy zaden blok nie miesci sie
w obszarze - raise z jasnym komunikatem (zmien font/wymiary).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .config import LabelConfig
from .flags import resolve_flag_code
from .hyphenation import Hyphenator
from .justify import Line, wrap_and_justify
from .text_metrics import FontMetrics


@dataclass
class LanguageBlock:
    code: str
    flag_code: str
    lines: list[Line]
    line_height_mm: float
    marker_size_mm: float
    gap_mm: float
    x_mm: float = 0.0
    y_mm: float = 0.0

    @property
    def height_mm(self) -> float:
        return len(self.lines) * self.line_height_mm


@dataclass
class Page:
    width_mm: float
    height_mm: float
    blocks: list[LanguageBlock]
    text_area_x_mm: float
    text_area_y_mm: float
    column_width_mm: float
    columns: int
    gutter_mm: float
    font_metrics: FontMetrics
    prefix: "PrefixStyle"


@dataclass
class PrefixStyle:
    size_mm: float
    style: str
    color: str
    text_color: str
    bold: bool
    gap_mm: float
    rect_radius_mm: float
    flags_dir: "Path | None" = None
    bold_font_metrics: FontMetrics | None = None


def layout_page(config: LabelConfig, project_root) -> Page:
    """Pobierz konfig, zbuduj Page z gotowymi pozycjami blokow i slow."""
    from pathlib import Path

    project_root = Path(project_root)

    font_path = _resolve_path(config.font.path, project_root)
    font = FontMetrics.load(font_path, config.font.size)

    bold_metrics = None
    if config.prefix_marker.bold and config.font.bold_path is not None:
        bold_path = _resolve_path(config.font.bold_path, project_root)
        bold_metrics = FontMetrics.load(bold_path, config.font.size)

    line_height = config.font.size * config.font.line_height
    marker = config.prefix_marker.size
    gap = config.prefix_marker.gap
    n_cols = config.columns
    column_w = (config.text_area.width - (n_cols - 1) * config.gutter) / n_cols

    if column_w <= marker + gap + font.space_width():
        raise ValueError(
            f"Kolumna {column_w:.2f}mm zbyt waska dla markera {marker}mm + "
            f"gap {gap}mm + minimalnego slowa - zwieksz text_area.width"
        )

    first_line_w = column_w - marker - gap
    rest_line_w = column_w

    blocks: list[LanguageBlock] = []
    for code, text in config.languages.items():
        hyph_on = config.hyphenation.enabled
        if code in config.hyphenation.per_language:
            hyph_on = config.hyphenation.per_language[code]
        hyphenator = Hyphenator(code) if hyph_on else None

        flag_code = resolve_flag_code(code, config.flags.language_to_flag)

        lines = wrap_and_justify(
            text=text,
            line_widths_mm=[first_line_w, rest_line_w],
            font=font,
            hyphenator=hyphenator,
            justify_full=config.justify_full,
        )
        blocks.append(
            LanguageBlock(
                code=code,
                flag_code=flag_code,
                lines=lines,
                line_height_mm=line_height,
                marker_size_mm=marker,
                gap_mm=gap,
            )
        )

    inter_block_gap = (
        config.inter_block_gap_mm
        if config.inter_block_gap_mm is not None
        else line_height * 0.6
    )
    if config.column_split is not None:
        columns_layout = _split_by_assignment(blocks, config.column_split)
        for ci, col_blocks in enumerate(columns_layout):
            _validate_column_height(
                col_blocks, config.text_area.height, inter_block_gap, ci
            )
    else:
        columns_layout = _balance_columns(
            blocks,
            available_h=config.text_area.height,
            inter_block_gap=inter_block_gap,
            n_cols=n_cols,
        )

    for col_idx, col_blocks in enumerate(columns_layout):
        x = config.text_area.x + col_idx * (column_w + config.gutter)
        y = config.text_area.y
        for block in col_blocks:
            block.x_mm = x
            block.y_mm = y
            y += block.height_mm + inter_block_gap

    flat = [b for col in columns_layout for b in col]
    flags_dir = _resolve_path(config.flags.path, project_root)
    prefix_style = PrefixStyle(
        size_mm=config.prefix_marker.size,
        style=config.prefix_marker.style,
        color=config.prefix_marker.color,
        text_color=config.prefix_marker.text_color,
        bold=config.prefix_marker.bold,
        gap_mm=config.prefix_marker.gap,
        rect_radius_mm=config.prefix_marker.rect_radius,
        flags_dir=flags_dir,
        bold_font_metrics=bold_metrics,
    )

    return Page(
        width_mm=config.page_size[0],
        height_mm=config.page_size[1],
        blocks=flat,
        text_area_x_mm=config.text_area.x,
        text_area_y_mm=config.text_area.y,
        column_width_mm=column_w,
        columns=n_cols,
        gutter_mm=config.gutter,
        font_metrics=font,
        prefix=prefix_style,
    )


def _split_by_assignment(
    blocks: list[LanguageBlock],
    assignment: list[list[str]],
) -> list[list[LanguageBlock]]:
    """Rozlozenie blokow zgodnie z reczna lista per-kolumna z YAML."""
    by_code = {b.code: b for b in blocks}
    return [[by_code[code] for code in col] for col in assignment]


def _balance_columns(
    blocks: list[LanguageBlock],
    available_h: float,
    inter_block_gap: float,
    n_cols: int,
) -> list[list[LanguageBlock]]:
    """Balansowane dzielenie blokow miedzy kolumny - kazda kolumna podobnej wysokosci.

    Algorytm: policz target_h = total_h / n_cols. Wkladaj bloki po kolei do
    kolumny az suma jej wysokosci przekroczy target - wtedy next column.
    Daje wizualnie zbalansowane kolumny (kazda ~taka sama wysokosc).

    Zachowuje kolejnosc blokow z YAML (PL po EN, UK po PL itd.).
    """
    if n_cols == 1:
        cols = [list(blocks)]
        _validate_column_height(cols[0], available_h, inter_block_gap, 0)
        return cols

    block_heights = [b.height_mm for b in blocks]
    total_h = sum(block_heights) + max(0, len(blocks) - 1) * inter_block_gap
    target_h = total_h / n_cols

    cols: list[list[LanguageBlock]] = [[] for _ in range(n_cols)]
    current_col = 0
    used_h = 0.0
    for block in blocks:
        needed = block.height_mm + (inter_block_gap if cols[current_col] else 0)
        # Zostaw ostatnia kolumne na reszte (nie przeskakuj poza n_cols-1)
        if (
            used_h + needed > target_h
            and current_col < n_cols - 1
            and cols[current_col]  # nie przerzucaj jesli kolumna pusta
        ):
            current_col += 1
            used_h = 0.0
            needed = block.height_mm
        cols[current_col].append(block)
        used_h += needed

    for ci, col_blocks in enumerate(cols):
        _validate_column_height(col_blocks, available_h, inter_block_gap, ci)

    return cols


def _validate_column_height(
    col_blocks: list[LanguageBlock],
    available_h: float,
    inter_block_gap: float,
    col_idx: int,
) -> None:
    if not col_blocks:
        return
    h = sum(b.height_mm for b in col_blocks) + (len(col_blocks) - 1) * inter_block_gap
    if h > available_h:
        codes = ", ".join(b.code for b in col_blocks)
        raise ValueError(
            f"Kolumna {col_idx} przekracza dostepna wysokosc: {h:.2f}mm > "
            f"{available_h:.2f}mm (bloki: {codes}). Zmniejsz font, zwieksz "
            f"text_area.height albo dodaj kolumne."
        )


def _resolve_path(p, project_root):
    from pathlib import Path

    p = Path(p)
    if p.is_absolute():
        return p
    return project_root / p
