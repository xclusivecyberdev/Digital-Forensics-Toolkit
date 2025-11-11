"""Timeline reconstruction utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List
import time


@dataclass
class TimelineEvent:
    """Represents a single point in time for an artefact."""

    timestamp: float
    description: str
    source: Path | str

    def formatted(self) -> str:
        return f"{time.ctime(self.timestamp)} - {self.description} ({self.source})"


class TimelineAnalyzer:
    """Build chronological timelines from filesystem metadata and custom events."""

    def __init__(self) -> None:
        self.events: List[TimelineEvent] = []

    def add_event(self, event: TimelineEvent) -> None:
        self.events.append(event)

    def add_events(self, events: Iterable[TimelineEvent]) -> None:
        for event in events:
            self.add_event(event)

    def build_from_directory(self, directory: str | Path, include_access_times: bool = False) -> List[TimelineEvent]:
        """Create timeline events from file metadata in *directory*."""

        base_path = Path(directory)
        if not base_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        generated: List[TimelineEvent] = []
        for file_path in base_path.rglob("*"):
            if not file_path.is_file():
                continue
            stat_info = file_path.stat()
            generated.append(
                TimelineEvent(
                    timestamp=stat_info.st_ctime,
                    description=f"Created {file_path.name}",
                    source=file_path.resolve(),
                )
            )
            generated.append(
                TimelineEvent(
                    timestamp=stat_info.st_mtime,
                    description=f"Modified {file_path.name}",
                    source=file_path.resolve(),
                )
            )
            if include_access_times:
                generated.append(
                    TimelineEvent(
                        timestamp=stat_info.st_atime,
                        description=f"Accessed {file_path.name}",
                        source=file_path.resolve(),
                    )
                )
        self.add_events(generated)
        return generated

    def export(self, chronological: bool = True) -> List[TimelineEvent]:
        """Return the events, optionally sorted."""

        if chronological:
            return sorted(self.events, key=lambda event: event.timestamp)
        return list(self.events)

    def as_strings(self, chronological: bool = True) -> List[str]:
        return [event.formatted() for event in self.export(chronological=chronological)]
