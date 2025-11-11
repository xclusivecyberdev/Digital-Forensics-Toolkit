"""Command line interface for the Digital Forensics Toolkit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from .hashing import HashCalculator
from .metadata import FileMetadataExtractor
from .memory import MemoryDumpAnalyzer
from .recovery import DeletedFileRecoverySimulator
from .timeline import TimelineAnalyzer
from .registry import WindowsRegistryParser


class ToolkitCLI:
    """A simple multi-tool style CLI exposing the toolkit capabilities."""

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(description="Digital Forensics Toolkit")
        subparsers = self.parser.add_subparsers(dest="command")

        metadata_parser = subparsers.add_parser("metadata", help="Extract file metadata")
        metadata_parser.add_argument("path")
        metadata_parser.add_argument("--readable", action="store_true")

        hash_parser = subparsers.add_parser("hash", help="Calculate file hashes")
        hash_parser.add_argument("path")

        verify_parser = subparsers.add_parser("verify", help="Verify file hashes")
        verify_parser.add_argument("path")
        verify_parser.add_argument("--md5")
        verify_parser.add_argument("--sha1")
        verify_parser.add_argument("--sha256")

        timeline_parser = subparsers.add_parser("timeline", help="Build timeline from directory")
        timeline_parser.add_argument("directory")
        timeline_parser.add_argument("--include-access", action="store_true")

        recovery_parser = subparsers.add_parser("recover", help="Simulate deleted file recovery")
        recovery_parser.add_argument("image_directory")
        recovery_parser.add_argument("--destination", default="recovered")

        registry_parser = subparsers.add_parser("registry", help="Parse a .reg export")
        registry_parser.add_argument("path")
        registry_parser.add_argument("--filter")

        memory_parser = subparsers.add_parser("strings", help="Extract ASCII strings from memory dump")
        memory_parser.add_argument("path")
        memory_parser.add_argument("--limit", type=int)

    def run(self, argv: List[str] | None = None) -> int:
        args = self.parser.parse_args(argv)
        if not args.command:
            self.parser.print_help()
            return 1

        if args.command == "metadata":
            extractor = FileMetadataExtractor()
            result = extractor.extract_as_dict(args.path, readable=args.readable)
            print(json.dumps(result, indent=2))
            return 0

        if args.command == "hash":
            calculator = HashCalculator()
            result = calculator.calculate(args.path)
            print(json.dumps(result.as_dict(), indent=2))
            return 0

        if args.command == "verify":
            calculator = HashCalculator()
            expected = {k: v for k, v in {"md5": args.md5, "sha1": args.sha1, "sha256": args.sha256}.items() if v}
            verification = calculator.verify(args.path, expected)
            print(HashCalculator.summarize_verification(verification))
            return 0

        if args.command == "timeline":
            analyzer = TimelineAnalyzer()
            analyzer.build_from_directory(args.directory, include_access_times=args.include_access)
            for line in analyzer.as_strings():
                print(line)
            return 0

        if args.command == "recover":
            simulator = DeletedFileRecoverySimulator()
            records = simulator.scan(args.image_directory)
            simulator.recover(records, args.destination)
            print(f"Recovered {len(records)} file(s) to {Path(args.destination).resolve()}")
            return 0

        if args.command == "registry":
            parser = WindowsRegistryParser()
            values = parser.parse_reg_file(args.path)
            if args.filter:
                values = parser.find_values(args.filter)
            for value in values:
                print(f"[{value.key_path}] {value.name} = {value.value}")
            return 0

        if args.command == "strings":
            analyzer = MemoryDumpAnalyzer()
            strings = analyzer.extract_ascii_strings(args.path, limit=args.limit)
            for string in strings:
                print(f"0x{string.offset:08x}: {string.value}")
            return 0

        self.parser.error(f"Unknown command: {args.command}")
        return 2


def main() -> int:
    return ToolkitCLI().run()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
