"""Basic memory dump analysis helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List
import re


ASCII_RE = re.compile(rb"[ -~]{4,}")


@dataclass
class MemoryString:
    offset: int
    value: str


class MemoryDumpAnalyzer:
    """Provide lightweight analysis features for raw memory dumps."""

    def __init__(self, min_length: int = 4) -> None:
        self.min_length = min_length

    def extract_ascii_strings(self, dump_path: str | Path, limit: int | None = None) -> List[MemoryString]:
        """Extract printable ASCII strings from the dump."""

        path = Path(dump_path)
        if not path.exists():
            raise FileNotFoundError(f"Memory dump not found: {dump_path}")

        results: List[MemoryString] = []
        data = path.read_bytes()
        for match in ASCII_RE.finditer(data):
            if len(match.group(0)) < self.min_length:
                continue
            results.append(MemoryString(offset=match.start(), value=match.group(0).decode("ascii", errors="ignore")))
            if limit and len(results) >= limit:
                break
        return results

    def search(self, dump_path: str | Path, pattern: bytes) -> List[int]:
        """Return offsets where *pattern* occurs in the dump."""

        path = Path(dump_path)
        if not path.exists():
            raise FileNotFoundError(f"Memory dump not found: {dump_path}")

        data = path.read_bytes()
        offsets: List[int] = []
        start = 0
        while True:
            idx = data.find(pattern, start)
            if idx == -1:
                break
            offsets.append(idx)
            start = idx + 1
        return offsets

    def summary(self, dump_path: str | Path) -> dict:
        """Provide a quick overview of the dump file."""

        path = Path(dump_path)
        if not path.exists():
            raise FileNotFoundError(f"Memory dump not found: {dump_path}")

        size = path.stat().st_size
        return {"path": str(path.resolve()), "size_bytes": size}
