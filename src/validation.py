from pathlib import Path


def is_valid_source(source: str) -> bool:
    p = Path(source)
    return p.exists() and p.is_dir()


def is_valid_output(output: str, overwrite: bool) -> bool:
    p = Path(output)
    # Valid if the path does not exist (will be created) or
    # exists and is a directory and overwrite is true
    return (not p.exists()) or (p.is_dir() and overwrite)


def is_valid_hamming_distance(hd_value) -> bool:
    try:
        hd = int(hd_value)
    except (TypeError, ValueError):
        return False
    return 0 <= hd <= 64
