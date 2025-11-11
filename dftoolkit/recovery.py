"""Simulation utilities for recovering deleted files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List
import shutil
import time


DELETED_SUFFIX = ".deleted"


@dataclass
class DeletedFileRecord:
    """Represents a simulated deleted file in the training environment."""

    original_path: Path
    storage_path: Path
    size: int
    deleted_time: float

    def describe(self) -> str:
        """Return a human readable description of the record."""

        return (
            f"Deleted file: {self.original_path} (size: {self.size} bytes, "
            f"deleted: {time.ctime(self.deleted_time)})"
        )


class DeletedFileRecoverySimulator:
    """Locate and restore files from a simulated recycle bin structure."""

    def __init__(self, deleted_suffix: str = DELETED_SUFFIX) -> None:
        self.deleted_suffix = deleted_suffix

    def scan(self, image_directory: str | Path) -> List[DeletedFileRecord]:
        """Scan *image_directory* for simulated deleted files."""

        base_path = Path(image_directory)
        if not base_path.exists():
            raise FileNotFoundError(f"Image directory not found: {image_directory}")

        records: List[DeletedFileRecord] = []
        for candidate in base_path.rglob(f"*{self.deleted_suffix}"):
            stat_info = candidate.stat()
            original_name = candidate.stem
            original_path = candidate.with_name(original_name)
            deleted_time = stat_info.st_mtime
            records.append(
                DeletedFileRecord(
                    original_path=original_path,
                    storage_path=candidate,
                    size=stat_info.st_size,
                    deleted_time=deleted_time,
                )
            )
        return records

    def recover(self, records: Iterable[DeletedFileRecord], destination: str | Path) -> None:
        """Recover the provided *records* to *destination* directory."""

        dest_path = Path(destination)
        dest_path.mkdir(parents=True, exist_ok=True)

        for record in records:
            target_path = dest_path / record.original_path.name
            shutil.copy2(record.storage_path, target_path)

    def recover_single(self, record: DeletedFileRecord, destination: str | Path) -> Path:
        """Recover a single record to *destination* and return the path."""

        dest_path = Path(destination)
        dest_path.mkdir(parents=True, exist_ok=True)
        target_path = dest_path / record.original_path.name
        shutil.copy2(record.storage_path, target_path)
        return target_path
