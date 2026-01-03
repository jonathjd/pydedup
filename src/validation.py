from pathlib import Path
from typing import Tuple


def validate_source(source: str) -> Path:
    p = Path(source)
    if not p.exists():
        raise SystemExit(f"Error: source directory does not exist: {p}")
    if not p.is_dir():
        raise SystemExit(f"Error: source path is not a directory: {p}")
    return p


def validate_output(output: str, overwrite: bool = False) -> Tuple[Path, Path]:
    p = Path(output)
    unique_dir = p / "unique"
    dups_dir = p / "duplicates"
    if p.exists() and not p.is_dir():
        raise SystemExit(f"Error: output path exists but is not a directory: {p}")
    if p.exists() and not overwrite:
        raise SystemExit(f"Output dir {p} exists. To overwrite add --overwrite flag.")
    else:
        try:
            unique_dir.mkdir(parents=True, exist_ok=True)
            dups_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise SystemExit(f"Error: failed to create output directory '{p}': {e}")
    return unique_dir, dups_dir


def validate_hamming_distance(hd_value) -> int:
    try:
        hd = int(hd_value)
    except (TypeError, ValueError):
        raise SystemExit(f"Error: hamming distance must be an integer, got: {hd_value!r}")
    if 0 > hd > 64:
        raise SystemExit(f"Error: hamming distance must be between 0 and 64 inclusive, got: {hd}")
    return hd
