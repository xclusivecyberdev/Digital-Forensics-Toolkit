"""Utilities for extracting metadata from files."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional
import mimetypes
import os
import stat
import time


@dataclass
class FileMetadata:
    """Structured representation of common metadata fields."""

    path: Path
    size: int
    created: float
    modified: float
    accessed: float
    permissions: str
    mime_type: Optional[str]

    def as_readable_dict(self) -> Dict[str, str]:
        """Return the metadata as a human-readable mapping."""

        return {
            "path": str(self.path),
            "size": f"{self.size} bytes",
            "created": time.ctime(self.created),
            "modified": time.ctime(self.modified),
            "accessed": time.ctime(self.accessed),
            "permissions": self.permissions,
            "mime_type": self.mime_type or "unknown",
        }


class FileMetadataExtractor:
    """Extract metadata for files on disk."""

    def __init__(self, follow_symlinks: bool = False) -> None:
        self.follow_symlinks = follow_symlinks

    def extract(self, file_path: str | Path) -> FileMetadata:
        """Extract metadata for *file_path*.

        Args:
            file_path: Path to the file to analyze.

        Returns:
            :class:`FileMetadata` instance populated with filesystem data.
        """

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        stat_result = path.stat() if self.follow_symlinks else os.lstat(path)
        permissions = stat.filemode(stat_result.st_mode)
        mime_type, _ = mimetypes.guess_type(path.as_posix())

        return FileMetadata(
            path=path.resolve(),
            size=stat_result.st_size,
            created=stat_result.st_ctime,
            modified=stat_result.st_mtime,
            accessed=stat_result.st_atime,
            permissions=permissions,
            mime_type=mime_type,
        )

    def extract_as_dict(self, file_path: str | Path, readable: bool = False) -> Dict[str, str | int | float | None]:
        """Return metadata as a plain dictionary.

        Args:
            file_path: Path to the file.
            readable: When ``True`` return a human-friendly representation.
        """

        metadata = self.extract(file_path)
        return metadata.as_readable_dict() if readable else asdict(metadata)
