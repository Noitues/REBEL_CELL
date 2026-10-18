"""Fresh-process worker for 12.3.1: prints the data hash for one producer and seed.

`python -m netrun_art.checks.hash_worker <producer spec> <layout seed>`. Imports only the hash path (no numpy).
"""
import sys

from .data_checks import data_hash, load_producer


def main(argv: list) -> int:
    """Print `data_hash(producer(seed))`."""
    print(data_hash(load_producer(argv[1])(argv[2])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
