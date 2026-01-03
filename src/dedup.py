import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import chain
from pathlib import Path

import imagehash
from loguru import logger
from PIL import Image

from models import HashedPath


class DedupPhotos:
    GLOB_PATTERNS = ("*.jpg", "*.jpeg", "*.png", "*.tiff", "*.gif", "*.bmp")

    def __init__(
        self,
        source_dir: Path,
        unique_dir: Path,
        dups_dir: Path,
        hamming_distance: int,
        recursive: bool,
    ):
        self.source_dir = source_dir
        self.unique_dir = unique_dir
        self.dups_dir = dups_dir
        self.ham_dist = hamming_distance

        glob_func = source_dir.rglob if recursive else source_dir.glob
        self.image_paths = chain.from_iterable(glob_func(pattern) for pattern in self.GLOB_PATTERNS)

        self._hash_images()
        self._group_duplicates()

    def _hash_images(self):
        # Materialize paths for parallel processing
        paths = list(self.image_paths)
        self.hashed_images = []

        def compute_hash(p: Path):
            try:
                img = Image.open(p)
                return HashedPath(path=p, phash=imagehash.phash(img))
            except Image.UnidentifiedImageError:
                logger.warning(f"Skipping invalid photo {p}")
                return None

        # Threaded hashing to overlap I/O and speed up hashing
        max_workers = min(32, (len(paths) or 1))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(compute_hash, p): p for p in paths}
            for fut in as_completed(futures):
                res = fut.result()
                if res is not None:
                    self.hashed_images.append(res)

    def _group_duplicates(self):
        self.grouped_images = []
        assigned = set()  # indices of images already placed in a group

        n = len(self.hashed_images)
        for i in range(n):
            if i in assigned:
                continue
            img_1 = self.hashed_images[i]
            group = [img_1]
            for j in range(i + 1, n):
                if j in assigned:
                    continue
                img_2 = self.hashed_images[j]
                if int(img_1.phash - img_2.phash) <= self.ham_dist:
                    group.append(img_2)
                    assigned.add(j)
            # Record the group and mark base as assigned
            self.grouped_images.append(group)
            assigned.add(i)

    def copy_images(self, dryrun: bool = False):
        group_count = 0
        unique_count = 0
        for group in self.grouped_images:
            if len(group) == 1:
                # Unique photo - preserve relative path under unique_dir
                image_obj = group[0]
                rel_path = image_obj.path.relative_to(self.source_dir)
                dest_path = self.unique_dir / rel_path
                if not dryrun:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(image_obj.path, dest_path)
                unique_count += 1
            else:
                # Duplicate group
                group_count += 1
                group_dir = self.dups_dir / f"group_{group_count}"
                for i, image_obj in enumerate(group, start=1):
                    # need to append number to end of name in case a
                    # photo in 2 locs has the same name
                    if not dryrun:
                        group_dir.mkdir(exist_ok=True)
                        shutil.copy2(image_obj.path, group_dir / f"{i}_{image_obj.path.name}")
                print(f"Group {group_count}: {len(group)} images")
        print(f"{unique_count} unique images copied to '{self.unique_dir}'.")
