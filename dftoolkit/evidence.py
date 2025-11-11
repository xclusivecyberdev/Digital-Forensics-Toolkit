"""Evidence handling and chain of custody logging."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json


@dataclass
class EvidenceItem:
    identifier: str
    description: str
    location: str
    hashes: Dict[str, str] | None = None


@dataclass
class ChainOfCustodyEntry:
    timestamp: datetime
    actor: str
    action: str
    notes: Optional[str] = None

    def serialize(self) -> Dict[str, str]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class EvidenceRecord:
    item: EvidenceItem
    custody_log: List[ChainOfCustodyEntry] = field(default_factory=list)

    def add_entry(self, actor: str, action: str, notes: str | None = None) -> ChainOfCustodyEntry:
        entry = ChainOfCustodyEntry(timestamp=datetime.utcnow(), actor=actor, action=action, notes=notes)
        self.custody_log.append(entry)
        return entry

    def serialize(self) -> Dict[str, object]:
        return {
            "item": asdict(self.item),
            "custody_log": [entry.serialize() for entry in self.custody_log],
        }


class EvidenceCollector:
    """Track evidentiary items and maintain a chain of custody."""

    def __init__(self) -> None:
        self.records: Dict[str, EvidenceRecord] = {}

    def register_item(self, identifier: str, description: str, location: str, hashes: Dict[str, str] | None = None) -> EvidenceRecord:
        if identifier in self.records:
            raise ValueError(f"Evidence item already registered: {identifier}")
        item = EvidenceItem(identifier=identifier, description=description, location=location, hashes=hashes)
        record = EvidenceRecord(item=item)
        record.add_entry(actor="System", action="Item registered", notes="Initial registration")
        self.records[identifier] = record
        return record

    def log_transfer(self, identifier: str, actor: str, action: str, notes: str | None = None) -> ChainOfCustodyEntry:
        record = self.records.get(identifier)
        if not record:
            raise KeyError(f"Evidence item not found: {identifier}")
        return record.add_entry(actor=actor, action=action, notes=notes)

    def export(self, output_path: str | Path) -> Path:
        """Persist the current chain of custody to a JSON file."""

        path = Path(output_path)
        data = {identifier: record.serialize() for identifier, record in self.records.items()}
        path.write_text(json.dumps(data, indent=2))
        return path

    def summary(self) -> List[str]:
        lines: List[str] = []
        for identifier, record in self.records.items():
            lines.append(f"Evidence {identifier}: {record.item.description} (stored at {record.item.location})")
            for entry in record.custody_log:
                lines.append(
                    f"  - {entry.timestamp.isoformat()} :: {entry.actor} :: {entry.action}"
                    + (f" :: {entry.notes}" if entry.notes else "")
                )
        return lines
