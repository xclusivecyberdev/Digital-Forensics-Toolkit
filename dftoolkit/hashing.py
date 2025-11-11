"""Hashing utilities for evidentiary verification."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import md5, sha1, sha256
from pathlib import Path
from typing import Dict, Iterable, Optional

BUFFER_SIZE = 1024 * 1024


@dataclass
class HashResult:
    """Container for the most common forensic hash algorithms."""

    md5: str
    sha1: str
    sha256: str

    def as_dict(self) -> Dict[str, str]:
        return {"md5": self.md5, "sha1": self.sha1, "sha256": self.sha256}


class HashCalculator:
    """Calculate and verify file hashes."""

    def __init__(self, buffer_size: int = BUFFER_SIZE) -> None:
        self.buffer_size = buffer_size

    def calculate(self, file_path: str | Path) -> HashResult:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        md5_hash = md5()
        sha1_hash = sha1()
        sha256_hash = sha256()

        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(self.buffer_size), b""):
                md5_hash.update(chunk)
                sha1_hash.update(chunk)
                sha256_hash.update(chunk)

        return HashResult(
            md5=md5_hash.hexdigest(),
            sha1=sha1_hash.hexdigest(),
            sha256=sha256_hash.hexdigest(),
        )

    def verify(self, file_path: str | Path, expected_hashes: Dict[str, str]) -> Dict[str, bool]:
        """Verify *file_path* against provided *expected_hashes*."""

        result = self.calculate(file_path)
        verification = {}
        for algorithm, digest in result.as_dict().items():
            expected = expected_hashes.get(algorithm)
            verification[algorithm] = expected is not None and expected.lower() == digest.lower()
        return verification

    @staticmethod
    def summarize_verification(verification: Dict[str, bool]) -> str:
        outcomes = [f"{algo.upper()}: {'match' if ok else 'mismatch'}" for algo, ok in verification.items()]
        return ", ".join(outcomes)
