from __future__ import annotations

import os
from typing import Dict, Optional

from Functions.Inferences.yolox import UnstructuredYoloXModel, MODEL_TYPES

DEFAULT_MODEL = "yolox"
models: Dict[str, UnstructuredYoloXModel] = {}

def get_model(model_name: Optional[str] = None, model_path: Optional[str] = None) -> UnstructuredYoloXModel:
    """Gets the model object by model name."""
    global models

    if model_name is None:
        default_name_from_env = os.environ.get("DEFAULT_MODEL_NAME")
        model_name = default_name_from_env if default_name_from_env is not None else DEFAULT_MODEL

    if model_name in models:
        return models[model_name]

    if model_name in MODEL_TYPES:
        model = UnstructuredYoloXModel()
        
        # Get model parameters from MODEL_TYPES
        model_config = MODEL_TYPES[model_name]
        actual_model_path = model_path or model_config["model_path"]
        label_map = model_config["label_map"]
        
        # Initialize the model with the correct parameters
        model.initialize(model_path=actual_model_path, label_map=label_map)
        models[model_name] = model
        return model
    else:
        raise UnknownModelException(f"Unknown model type: {model_name}")

class UnknownModelException(Exception):
    """A model was requested with an unrecognized identifier."""
    pass