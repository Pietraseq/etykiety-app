"""Walidacja konfigu YAML przez pydantic.

Walidacja struktury, jednostek (wszystko w mm), obecnosci wszystkich
wymaganych jezykow. Nie sprawdza zawartosci tekstow - tylko schema.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class FontConfig(BaseModel):
    family: str
    path: Path
    bold_path: Optional[Path] = None
    size: float = Field(gt=0, description="Font size w mm")
    line_height: float = Field(default=1.2, gt=0)


class TextAreaConfig(BaseModel):
    x: float = 0
    y: float = 0
    width: float = Field(gt=0, description="Szerokosc obszaru tekstu w mm")
    height: float = Field(gt=0)


class PrefixMarkerConfig(BaseModel):
    size: float = Field(gt=0)
    # Style: text_rect = czerwony kwadracik z kodem kraju (oryginalny MVP),
    # flag_circle = okragla flaga, flag_rect = prostokatna flaga,
    # flag_rounded = prostokat z zaokraglonymi rogami
    style: str = Field(default="flag_circle")
    color: str = "#E60000"
    text_color: str = "#FFFFFF"
    bold: bool = True
    gap: float = Field(default=1.0, ge=0)
    rect_radius: float = Field(default=0.4, ge=0)  # mm, dla flag_rounded


class FlagsConfig(BaseModel):
    """Sciezka do folderu z plikami flag (relatywnie do roota projektu)."""

    path: Path = Field(default=Path("assets/flags"))
    # Override domyslnego mapowania jezyk -> kod flagi (lipis nazwy plikow)
    language_to_flag: dict[str, str] = Field(default_factory=dict)


class HyphenationConfig(BaseModel):
    enabled: bool = True
    per_language: dict[str, bool] = Field(default_factory=dict)


class LabelConfig(BaseModel):
    """Pelny konfig pojedynczej etykiety."""

    product_code: str
    description: Optional[str] = None
    page_size: tuple[float, float]
    text_area: TextAreaConfig
    columns: int = Field(default=2, ge=1, le=10)
    gutter: float = Field(default=4.0, ge=0)
    font: FontConfig
    prefix_marker: PrefixMarkerConfig
    flags: FlagsConfig = Field(default_factory=FlagsConfig)
    hyphenation: HyphenationConfig = Field(default_factory=HyphenationConfig)
    languages: dict[str, str]
    # Reczne przypisanie jezykow do kolumn. Lista kolumn, kazda kolumna - lista
    # kodow jezykow w kolejnosci wyswietlania. Gdy None - automat balansuje.
    column_split: Optional[list[list[str]]] = None
    # Odstep w mm miedzy blokami jezykowymi w tej samej kolumnie. Gdy None -
    # auto = line_height * 0.6 (gestszy uklad gdy font maly, luzniejszy gdy duzy).
    inter_block_gap_mm: Optional[float] = Field(default=None, ge=0)
    # Justyfikacja calego akapitu na cala szerokosc kolumny przez word-spacing.
    # True (default) = wyjustowany. False = ragged-right (wyrownany do lewej).
    justify_full: bool = True

    @field_validator("languages")
    @classmethod
    def _languages_not_empty(cls, v: dict[str, str]) -> dict[str, str]:
        if not v:
            raise ValueError("Brak jezykow w konfigu - wymagany przynajmniej jeden")
        for code, text in v.items():
            if not text or not text.strip():
                raise ValueError(f"Pusty tekst dla jezyka {code}")
        return v

    @field_validator("column_split")
    @classmethod
    def _column_split_valid(cls, v, info):
        if v is None:
            return v
        languages = info.data.get("languages", {})
        columns = info.data.get("columns", 2)
        if len(v) != columns:
            raise ValueError(
                f"column_split: oczekiwane {columns} kolumn, dostarczone {len(v)}"
            )
        flat = [code for col in v for code in col]
        if len(flat) != len(set(flat)):
            raise ValueError("column_split: duplikaty kodow jezykow")
        flat_set = set(flat)
        lang_set = set(languages.keys())
        if flat_set != lang_set:
            missing = lang_set - flat_set
            extra = flat_set - lang_set
            raise ValueError(
                f"column_split: braki={sorted(missing)}, nadmiar={sorted(extra)}"
            )
        return v

    @classmethod
    def load(cls, yaml_path: Path) -> "LabelConfig":
        with yaml_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)
