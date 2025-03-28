from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from PIL.Image import Image


class UnstructuredModel(ABC):
    """Wrapper class for the various models used by unstructured."""

    def __init__(self):
        """Minimal model initialization"""
        self.model = None

    @abstractmethod
    def predict(self, x: Any) -> Any:
        """Do inference using the wrapped model."""
        if self.model is None:
            raise ModelNotInitializedError(
                "Model has not been initialized. Please call the initialize method with the "
                "appropriate arguments for loading the model.",
            )

    def __call__(self, x: Any) -> Any:
        """Inference using function call interface."""
        return self.predict(x)

    @abstractmethod
    def initialize(self, *args, **kwargs):
        """Load the model for inference."""
        pass


class UnstructuredObjectDetectionModel(UnstructuredModel):
    """Minimal wrapper class for object detection models."""

    @abstractmethod
    def predict(self, x: Image) -> Any:
        """Do inference using the wrapped model."""
        super().predict(x)
        return []


class ModelNotInitializedError(Exception):
    """Raised when model is not initialized properly."""
    pass 