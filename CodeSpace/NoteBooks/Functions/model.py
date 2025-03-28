"""Domain-model for file-types."""

from __future__ import annotations

import enum
from typing import Iterable, Type, cast

def _create_file_type_enum(
    cls: Type["FileType"],
    value: str,
    partitioner_shortname: str | None,
    importable_package_dependencies: Iterable[str],
    extra_name: str | None,
    extensions: Iterable[str],
    canonical_mime_type: str,
    alias_mime_types: Iterable[str],
    partitioner_full_module_path: str | None = None,
) -> "FileType":
    """Create a new FileType enum value."""
    val = object.__new__(cls)
    val._value_ = value
    val._extensions = tuple(extensions)
    val._canonical_mime_type = canonical_mime_type
    return val

class FileType(enum.Enum):
    """The collection of file-types recognized by `unstructured`."""

    def __new__(
        cls,
        value: str,
        partitioner_shortname: str | None,
        importable_package_dependencies: Iterable[str],
        extra_name: str | None,
        extensions: Iterable[str],
        canonical_mime_type: str,
        alias_mime_types: Iterable[str],
        partitioner_full_module_path: str | None = None,
    ):
        return _create_file_type_enum(
            cls,
            value,
            partitioner_shortname,
            importable_package_dependencies,
            extra_name,
            extensions,
            canonical_mime_type,
            alias_mime_types,
            partitioner_full_module_path,
        )

    PDF = (
        "pdf",
        "pdf",
        ["pdf2image", "pdfminer", "PIL"],
        "pdf",
        [".pdf"],
        "application/pdf",
        cast(list[str], []),
    )

    UNK = (
        "unk",
        None,
        cast(list[str], []),
        None,
        cast(list[str], []),
        "application/octet-stream",
        cast(list[str], []),
    )