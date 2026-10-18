"""Regenerate the NA-03 fixtures: `fixtures/hashes.json` (SHA-256 per output file per fixture seed) and
`fixtures/expected/<seed>_{street,hq}_poses.json` (camera poses, framing and occlusion output; the parity inputs of NA-21,
12.6). Run from `tools/`:  `python -m netrun_art.tests.gen_fixtures`. The tests fail when these files drift."""
import os

from netrun_art import io
from netrun_art.checks import data_checks as DC
from netrun_art.tests import producer

SEEDS = [str(s) for s in range(101, 113)]       # 12 fixture seeds: each has a street run and an HQ run
HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures")
EXPECTED = os.path.join(FIX, "expected")


def compute(seed: str):
    """`(files, per-file hashes, data hash)` of one fixture seed."""
    files = producer.produce(seed)
    return files, DC.file_hashes(files), DC.data_hash(files)


def main() -> None:
    os.makedirs(EXPECTED, exist_ok=True)
    out = {"seeds": SEEDS, "hashes": {}}
    for s in SEEDS:
        files, hs, dh = compute(s)
        out["hashes"][s] = dict(hs, data=dh)
        io.dump(files["poses_street"], os.path.join(EXPECTED, f"{s}_street_poses.json"))
        io.dump(files["poses_hq"], os.path.join(EXPECTED, f"{s}_hq_poses.json"))
    io.dump(out, os.path.join(FIX, "hashes.json"))
    print("wrote", len(SEEDS), "seeds")


if __name__ == "__main__":
    main()
