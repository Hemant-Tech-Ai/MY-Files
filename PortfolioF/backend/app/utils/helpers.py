import json
import os
from typing import Any, Dict, List, Optional

def load_json_data(file_path: str) -> Dict[str, Any]:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the JSON data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return {}

def get_data_file_path(filename: str) -> str:
    """
    Get the absolute path to a data file.
    
    Args:
        filename: Name of the file in the data directory
        
    Returns:
        Absolute path to the file
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "data", filename)

def filter_items(items: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Filter a list of items based on the provided filters.
    
    Args:
        items: List of items to filter
        filters: Dictionary of filter criteria
        
    Returns:
        Filtered list of items
    """
    if not filters:
        return items
    
    filtered_items = items
    
    for key, value in filters.items():
        if value is not None:
            if isinstance(value, list):
                filtered_items = [item for item in filtered_items if key in item and any(v in item[key] for v in value)]
            else:
                filtered_items = [item for item in filtered_items if key in item and item[key] == value]
    
    return filtered_items

def sort_items(items: List[Dict[str, Any]], sort_by: Optional[str] = None, sort_order: str = "asc") -> List[Dict[str, Any]]:
    """
    Sort a list of items based on the provided sort criteria.
    
    Args:
        items: List of items to sort
        sort_by: Field to sort by
        sort_order: Sort order ("asc" or "desc")
        
    Returns:
        Sorted list of items
    """
    if not sort_by or not all(sort_by in item for item in items):
        return items
    
    reverse = sort_order.lower() == "desc"
    return sorted(items, key=lambda x: x.get(sort_by, ""), reverse=reverse) 