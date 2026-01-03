import argparse
from pathlib import Path

from loguru import logger

from dedup import DedupPhotos
from validation import is_valid_hamming_distance, is_valid_output, is_valid_source


def main():
    # accept args
    parser = argparse.ArgumentParser(description="A CLI program to help you identify duplicate photos.")
    parser.add_argument("source", help="The directory to scan for duplicate photos.")
    parser.add_argument(
        "--output",
        "-o",
        help="The directory to move/copy duplicate photos",
        required=True,
    )
    parser.add_argument("--overwrite", help="Overwrite output directory if exists", action="store_true")
    parser.add_argument("--verbose", "-v", help="Verbose logging", action="store_true")
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="Whether to recurisve scan the source directory",
    )
    parser.add_argument(
        "--hamming_distance",
        "-hd",
        help="The number of differences between the hashes for 2 photos to be considered duplicates (default 13)",
        required=False,
        default=13,
    )
    parser.add_argument("--dryrun", help="Performs a dry run of the operation.", action="store_true")

    args = parser.parse_args()

    # validate args
    if not is_valid_source(args.source):
        logger.error(f"Invalid source directory: {args.source}")
        exit(1)

    if not is_valid_output(args.output, args.overwrite):
        logger.error(f"Invalid output directory: {args.output}")
        exit(1)

    if not is_valid_hamming_distance(args.hamming_distance):
        logger.error(f"Invalid hamming distance: {args.hamming_distance}. Must be an integer between 0 and 64.")
        exit(1)

    # setup paths after validation
    source_dir, output_dir = Path(args.source), Path(args.output)
    unique_dir = output_dir / "unique"
    dups_dir = output_dir / "duplicates"
    if not args.dryrun:
        unique_dir.mkdir(parents=True, exist_ok=True)
        dups_dir.mkdir(parents=True, exist_ok=True)
    ham_dist = int(args.hamming_distance)

    # pass into Dedup Obj
    dedup = DedupPhotos(source_dir, unique_dir, dups_dir, ham_dist, args.recursive)
    dedup.copy_images(args.dryrun)
    exit(0)


if __name__ == "__main__":
    main()
