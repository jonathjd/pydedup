import argparse

from loguru import logger

from dedup import DedupPhotos
from validation import validate_hamming_distance, validate_output, validate_source


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
        help="The number of differences between the hashes for 2 photos to be considered duplicates (default 14)",
        required=False,
        default=13,
    )
    parser.add_argument("--dryrun", help="Performs a dry run of the operation.", action="store_true")

    args = parser.parse_args()

    # validate args
    try:
        source_dir = validate_source(args.source)
        unique_dir, dups_dir = validate_output(args.output, args.overwrite)
        ham_dist = validate_hamming_distance(args.hamming_distance)

        # pass into Dedup Obj
        dedup = DedupPhotos(source_dir, unique_dir, dups_dir, ham_dist, args.recursive)
        dedup.copy_images()
        exit_code = 0
    except Exception as e:
        exit_code = 1
        logger.error(e)

    exit(exit_code)


if __name__ == "__main__":
    main()
