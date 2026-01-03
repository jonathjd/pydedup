from dataclasses import dataclass
from pathlib import Path

from imagehash import ImageHash


@dataclass(frozen=True)
class HashedPath:
    path: Path
    phash: ImageHash
