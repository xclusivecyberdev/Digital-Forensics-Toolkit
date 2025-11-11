# Digital Forensics Toolkit

A Python-based learning toolkit that demonstrates common digital forensics
workflows, including metadata extraction, hash verification, timeline analysis,
and evidence handling concepts.

## Features

- **File metadata extraction** via `FileMetadataExtractor`.
- **Deleted file recovery simulation** using `DeletedFileRecoverySimulator` to
  locate files with a configurable `.deleted` suffix.
- **Hash calculation and verification** for MD5, SHA-1, and SHA-256 with
  `HashCalculator`.
- **Timeline analysis** through `TimelineAnalyzer`, which aggregates filesystem
  events into chronological reports.
- **Windows registry parsing** with `WindowsRegistryParser` for exported `.reg`
  files.
- **Memory dump analysis basics** using `MemoryDumpAnalyzer` to extract ASCII
  strings and search raw dumps.
- **Evidence collection with chain of custody logging** via `EvidenceCollector`.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # if you add additional dependencies
```

The toolkit has no external dependencies beyond the Python standard library.

## Usage

The CLI entry point is `dftoolkit.main`. Run it with Python to access the
subcommands below:

```bash
python -m dftoolkit.main <command> [options]
```

### Metadata Extraction

```bash
python -m dftoolkit.main metadata /path/to/file --readable
```

### Hash Calculation

```bash
python -m dftoolkit.main hash /path/to/file
```

### Hash Verification

```bash
python -m dftoolkit.main verify /path/to/file --md5 <expected> --sha1 <expected>
```

### Timeline Analysis

```bash
python -m dftoolkit.main timeline /path/to/directory --include-access
```

### Deleted File Recovery Simulation

```bash
python -m dftoolkit.main recover /path/to/image --destination ./recovered
```

Place simulated deleted files in the image directory with the suffix `.deleted`
(e.g., `document.txt.deleted`). The recovery command copies them to the
specified destination without the suffix.

### Registry Parsing

```bash
python -m dftoolkit.main registry exported.reg --filter "Run"
```

### Memory Dump String Extraction

```bash
python -m dftoolkit.main strings memory.dmp --limit 25
```

## Library Usage

Each feature is also available as a Python API:

```python
from dftoolkit import FileMetadataExtractor, HashCalculator

metadata = FileMetadataExtractor().extract("example.txt")
print(metadata.as_readable_dict())

hashes = HashCalculator().calculate("example.txt")
print(hashes.as_dict())
```

## Documentation

Detailed operational guidance, forensic procedures, and legal considerations
are documented in [`docs/forensic_procedures.md`](docs/forensic_procedures.md).

## License

This project is provided for educational purposes. Validate the toolkit in your
own environment before using it in real-world investigations.
