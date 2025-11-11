"""Minimal Windows registry parsing utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class RegistryValue:
    key_path: str
    name: str
    value: str


class WindowsRegistryParser:
    """Parse exported ``.reg`` files into structured data."""

    def __init__(self) -> None:
        self.values: List[RegistryValue] = []

    def parse_reg_file(self, file_path: str | Path) -> List[RegistryValue]:
        """Parse a Windows registry export file."""

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Registry file not found: {file_path}")

        current_key = ""
        parsed: List[RegistryValue] = []
        with path.open("r", encoding="utf-8", errors="ignore") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line or line.startswith(";"):
                    continue
                if line.startswith("[") and line.endswith("]"):
                    current_key = line.strip("[]")
                    continue
                if "=" in line and current_key:
                    name, value = line.split("=", 1)
                    name = name.strip().strip('"')
                    value = value.strip()
                    parsed.append(RegistryValue(key_path=current_key, name=name, value=value))
        self.values = parsed
        return parsed

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        """Return the parsed registry values as a nested dictionary."""

        registry_dict: Dict[str, Dict[str, str]] = {}
        for value in self.values:
            registry_dict.setdefault(value.key_path, {})[value.name] = value.value
        return registry_dict

    def find_values(self, key_substring: str) -> List[RegistryValue]:
        """Find values whose key path contains *key_substring*."""

        return [value for value in self.values if key_substring.lower() in value.key_path.lower()]
