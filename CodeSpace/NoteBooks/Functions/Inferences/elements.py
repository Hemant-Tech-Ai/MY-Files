from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Union

import numpy as np

from Functions.Inferences.constants import Source


@dataclass
class Rectangle:
    x1: Union[int, float]
    y1: Union[int, float]
    x2: Union[int, float]
    y2: Union[int, float]
    
    @property
    def coordinates(self):
        """Gets coordinates of the rectangle"""
        return ((self.x1, self.y1), (self.x1, self.y2), (self.x2, self.y2), (self.x2, self.y1))


@dataclass
class TextRegion:
    bbox: Rectangle
    text: Optional[str] = None
    source: Optional[Source] = None

    def __str__(self) -> str:
        return str(self.text)

    @classmethod
    def from_coords(
        cls,
        x1: Union[int, float],
        y1: Union[int, float],
        x2: Union[int, float],
        y2: Union[int, float],
        text: Optional[str] = None,
        source: Optional[Source] = None,
        **kwargs,
    ) -> TextRegion:
        """Constructs a region from coordinates."""
        bbox = Rectangle(x1, y1, x2, y2)
        return cls(text=text, source=source, bbox=bbox, **kwargs)


@dataclass
class TextRegions:
    element_coords: np.ndarray
    texts: np.ndarray = field(default_factory=lambda: np.array([]))
    sources: np.ndarray = field(default_factory=lambda: np.array([]))
    source: Source | None = None

    def __post_init__(self):
        if self.texts.size == 0 and self.element_coords.size > 0:
            self.texts = np.array([None] * self.element_coords.shape[0])

        if self.sources.size == 0 and self.element_coords.size > 0:
            self.sources = np.array([self.source] * self.element_coords.shape[0])
        elif self.source is None and self.sources.size:
            self.source = self.sources[0]

        self.element_coords = self.element_coords.astype(float)


def coords_intersections(coords: np.ndarray) -> np.ndarray:
    """Returns a square boolean matrix of intersections of given stack of coords"""
    x1s, y1s, x2s, y2s = coords[:, 0], coords[:, 1], coords[:, 2], coords[:, 3]

    intersections = ~(
        (x1s[None] > x2s[..., None])
        | (y1s[None] > y2s[..., None])
        | (x1s[None] > x2s[..., None]).T
        | (y1s[None] > y2s[..., None]).T
    )

    return intersections 