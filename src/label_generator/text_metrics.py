"""Pomiar szerokosci tekstu na bazie pliku TTF/OTF.

Czyta `hmtx` z pliku fontu (deterministyczny pomiar - identyczny niezaleznie
od systemu na ktorym uruchamiany jest skrypt). Wszystkie wymiary w milimetrach
(skala druku, zgodna z viewBox SVG).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fontTools.ttLib import TTFont


@dataclass
class FontMetrics:
    """Metryka konkretnego pliku fontu w konkretnym rozmiarze (mm)."""

    font_path: Path
    size_mm: float
    units_per_em: int
    ascender_mm: float
    descender_mm: float
    line_gap_mm: float
    cap_height_mm: float
    x_height_mm: float
    _cmap: dict[int, str]
    _hmtx: dict[str, tuple[int, int]]
    _scale: float

    @classmethod
    def load(cls, font_path: Path, size_mm: float) -> "FontMetrics":
        font = TTFont(str(font_path))
        cmap = font.getBestCmap()
        hmtx_raw = font["hmtx"]
        hmtx = {name: hmtx_raw[name] for name in hmtx_raw.metrics}
        units_per_em = font["head"].unitsPerEm
        scale = size_mm / units_per_em
        os2 = font["OS/2"]
        # Bardziej spojne na cross-platform: sTypoAscender / sTypoDescender
        ascender_units = os2.sTypoAscender
        descender_units = abs(os2.sTypoDescender)
        line_gap_units = os2.sTypoLineGap
        cap_height_units = getattr(os2, "sCapHeight", os2.sTypoAscender)
        x_height_units = getattr(os2, "sxHeight", os2.sTypoAscender // 2)
        return cls(
            font_path=font_path,
            size_mm=size_mm,
            units_per_em=units_per_em,
            ascender_mm=ascender_units * scale,
            descender_mm=descender_units * scale,
            line_gap_mm=line_gap_units * scale,
            cap_height_mm=cap_height_units * scale,
            x_height_mm=x_height_units * scale,
            _cmap=cmap,
            _hmtx=hmtx,
            _scale=scale,
        )

    def char_width(self, char: str) -> float:
        codepoint = ord(char)
        glyph_name = self._cmap.get(codepoint)
        if glyph_name is None:
            raise MissingGlyphError(
                f"Brak glifu dla znaku {char!r} (U+{codepoint:04X}) w foncie "
                f"{self.font_path.name}. Sprawdz czy plik fontu obejmuje "
                f"wymagany skrypt (cyrylica, greka itp.)."
            )
        advance, _lsb = self._hmtx[glyph_name]
        return advance * self._scale

    def text_width(self, text: str) -> float:
        """Suma advance widthow znakow w tekscie. Bez kerningu (MVP)."""
        return sum(self.char_width(c) for c in text)

    def space_width(self) -> float:
        return self.char_width(" ")


class MissingGlyphError(ValueError):
    """Brak glifu dla znaku w wybranym foncie - zgloszenie jawne, nie silent fallback."""
