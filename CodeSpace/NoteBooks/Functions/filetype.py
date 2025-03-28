from __future__ import annotations

import importlib
import os
import tempfile

from typing import IO, Optional

from Functions.model import FileType

try:
    importlib.import_module("magic")
    LIBMAGIC_AVAILABLE = True
except ImportError:
    LIBMAGIC_AVAILABLE = False

def detect_filetype(
    file_path: str | None = None,
    file: IO[bytes] | tempfile.SpooledTemporaryFile | None = None,
    encoding: str | None = None,
    content_type: str | None = None,
    metadata_file_path: Optional[str] = None,
) -> FileType:
    """Determine file-type of specified file."""
    # Simple PDF detection based on file extension
    if file_path and file_path.lower().endswith('.pdf'):
        return FileType.PDF
        
    # If file content is provided, check for PDF signature
    if file:
        if isinstance(file, tempfile.SpooledTemporaryFile):
            file_content = file.read()
            file.seek(0)
        else:
            current_pos = file.tell()
            file_content = file.read()
            file.seek(current_pos)
            
        # Check for PDF signature
        if file_content.startswith(b'%PDF-'):
            return FileType.PDF
    
    return FileType.UNK

class _FileTypeDetectionContext:
    def __init__(
        self,
        file_path: str | None = None,
        *,
        file: IO[bytes] | None = None,
        encoding: str | None = None,
        content_type: str | None = None,
        metadata_file_path: str | None = None,
    ):
        self._file_path_arg = file_path
        self._file_arg = file
        self._encoding_arg = encoding
        self._content_type = content_type
        self._metadata_file_path = metadata_file_path

    @classmethod
    def new(cls, **kwargs) -> _FileTypeDetectionContext:
        self = cls(**kwargs)
        self._validate()
        return self

    def _validate(self) -> None:
        if self.file_path and not os.path.isfile(self.file_path):
            raise FileNotFoundError(f"no such file {self._file_path_arg}")
        if not self.file_path and not self._file_arg:
            raise ValueError("either `file_path` or `file` argument must be provided")

class _FileTypeDetector:
    def __init__(self, ctx: _FileTypeDetectionContext):
        self._ctx = ctx

    @classmethod
    def file_type(cls, ctx: _FileTypeDetectionContext) -> FileType:
        return cls(ctx)._file_type

    @property
    def _file_type(self) -> FileType:
        if (
            (predicted_file_type := self._known_binary_file_type)
            or (predicted_file_type := self._file_type_from_content_type)
            or (predicted_file_type := self._file_type_from_guessed_mime_type)
            or (predicted_file_type := self._file_type_from_file_extension)
        ):
            result_file_type = predicted_file_type
        else:
            result_file_type = FileType.UNK

        return result_file_type