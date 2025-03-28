from __future__ import annotations

import asyncio
import importlib
import functools
import os
import logging
from functools import wraps
from typing import Any, Callable, List, Optional, TypeVar

from typing_extensions import ParamSpec

_T = TypeVar("_T")
_P = ParamSpec("_P")

logger = logging.getLogger(__name__)

class lazyproperty:
    """
    A decorator that converts a function into a lazy property.
    The function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access the value.
    """
    def __init__(self, func: Callable) -> None:
        self.func = func
        functools.update_wrapper(self, func)
        self.__doc__ = func.__doc__

    def __get__(self, obj: Any, cls: Any) -> Any:
        if obj is None:
            return self
        value = self.func(obj)
        setattr(obj, self.func.__name__, value)
        return value

def scarf_analytics() -> None:
    """
    Initialize Scarf analytics for tracking package usage.
    Can be disabled by setting SCARF_NO_ANALYTICS=true environment variable.
    """
    if os.environ.get("SCARF_NO_ANALYTICS", "").lower() == "true":
        logger.debug("Scarf analytics disabled via environment variable")
        return
    
    try:
        logger.debug("Scarf analytics initialized")
    except Exception as e:
        logger.debug(f"Failed to initialize Scarf analytics: {str(e)}")

def dependency_exists(dependency: str) -> bool:
    """Check if a Python dependency exists.
    
    Args:
        dependency: Name of the dependency package to check
        
    Returns:
        True if the dependency is installed, False otherwise
    """
    try:
        importlib.import_module(dependency)
    except ImportError as e:
        # Check to make sure this isn't some unrelated import error
        if dependency in repr(e):
            return False
    return True

def requires_dependencies(
    dependencies: str | list[str],
    extras: Optional[str] = None,
) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]:
    """Decorator to check if required dependencies are installed.
    
    This decorator checks if the specified dependencies are installed
    before executing the decorated function. If any dependency is missing,
    it raises an ImportError with instructions on how to install it.
    
    Args:
        dependencies: A string or list of strings representing required package names
        extras: Optional package extra to suggest in the error message
        
    Returns:
        A decorator function that checks for dependencies
    """
    if isinstance(dependencies, str):
        dependencies = [dependencies]

    def decorator(func: Callable[_P, _T]) -> Callable[_P, _T]:
        def run_check():
            missing_deps: List[str] = []
            for dep in dependencies:
                if not dependency_exists(dep):
                    missing_deps.append(dep)
            if len(missing_deps) > 0:
                raise ImportError(
                    f"Following dependencies are missing: {', '.join(missing_deps)}. "
                    + (
                        f"""Please install them using `pip install "unstructured[{extras}]"`."""
                        if extras
                        else f"Please install them using `pip install {' '.join(missing_deps)}`."
                    ),
                )

        @wraps(func)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs):
            run_check()
            return func(*args, **kwargs)

        @wraps(func)
        async def wrapper_async(*args: _P.args, **kwargs: _P.kwargs):
            run_check()
            return await func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return wrapper_async
        return wrapper

    return decorator