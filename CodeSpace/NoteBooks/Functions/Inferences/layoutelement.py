from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np

from Functions.Inferences.elements import TextRegion, TextRegions


@dataclass
class LayoutElements(TextRegions):
    """
    Container class for layout elements detected by models.
    
    This simplified version only includes what's needed for PDF element detection.
    """
    element_probs: np.ndarray = field(default_factory=lambda: np.array([]))
    element_class_ids: np.ndarray = field(default_factory=lambda: np.array([]))
    element_class_id_map: dict[int, str] = field(default_factory=dict)
    text_as_html: np.ndarray = field(default_factory=lambda: np.array([]))
    table_as_cells: np.ndarray = field(default_factory=lambda: np.array([]))

    def __post_init__(self):
        """Initialize arrays after object creation"""
        element_size = self.element_coords.shape[0]
        # Initialize empty arrays for all attributes
        for attr in (
            "element_probs",
            "element_class_ids",
            "texts",
            "text_as_html",
            "table_as_cells",
        ):
            if getattr(self, attr).size == 0 and element_size:
                setattr(self, attr, np.array([None] * element_size))

        # Handle sources array
        if self.sources.size == 0 and self.element_coords.size > 0:
            self.sources = np.array([self.source] * self.element_coords.shape[0])
        elif self.source is None and self.sources.size:
            self.source = self.sources[0]

        self.element_probs = self.element_probs.astype(float)

    def iter_elements(self):
        """
        Iterate over elements as individual LayoutElement objects.
        
        This is the only method used by pdf_element_detector_cv2.py.
        """
        for (x1, y1, x2, y2), text, prob, class_id, source, text_as_html, table_as_cells in zip(
            self.element_coords,
            self.texts,
            self.element_probs,
            self.element_class_ids,
            self.sources,
            self.text_as_html,
            self.table_as_cells,
        ):
            yield LayoutElement.from_coords(
                x1,
                y1,
                x2,
                y2,
                text=text,
                type=(
                    self.element_class_id_map[class_id]
                    if class_id is not None and self.element_class_id_map
                    else None
                ),
                prob=None if np.isnan(prob) else prob,
                source=source,
                text_as_html=text_as_html,
                table_as_cells=table_as_cells,
            )


@dataclass
class LayoutElement(TextRegion):
    """
    Individual element detected in a document layout.
    
    Simplified version of the original class.
    """
    type: Optional[str] = None
    prob: Optional[float] = None
    text_as_html: Optional[str] = None
    table_as_cells: Optional[str] = None 