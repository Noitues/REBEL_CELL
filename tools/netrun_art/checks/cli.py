"""Command line for the NA-04 checks.

    python -m netrun_art.checks --data --producer file.py:fn --seeds 1,2,3 [--zoned f --city f --derive f
                                 --beams f --dress f --hq-rail f --parity A B] [--out DIR]
    python -m netrun_art.checks --images DIR [--plates DIR] [--out DIR]
    python -m netrun_art.checks --reference --ref-config pvc_config.json --ref-rules rules_check.md --concepts DIR

Run from the `tools` folder (or with it on PYTHONPATH). Exit code 1 on any fail, else 0 (warn and n/a never fail).
`--images DIR` takes a capture folder (beauty.png, id.png, capture.json) or a folder of them; `--plates DIR` holds
golden captures with the same sub-folder names and adds renderer-tolerance records.
"""
import argparse
import os
import sys
from typing import Any, Dict, List, Optional

from .. import io
from . import data_checks as D
from . import image_checks as IC
from . import report as R


def build_parser() -> argparse.ArgumentParser:
    """Argument parser of the CLI."""
    ap = argparse.ArgumentParser(prog="netrun_art.checks")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--data", action="store_true", help="run the data checks (12.3, 12.4, 12.5, 12.6)")
    mode.add_argument("--images", metavar="DIR", help="run the image checks on a capture folder")
    mode.add_argument("--reference", action="store_true", help="compare with the art-pass rules_check.md")
    ap.add_argument("--plates", metavar="DIR", help="golden captures to compare against (renderer tolerances)")
    ap.add_argument("--config", help="composition.json override")
    ap.add_argument("--out", help="folder for checks.md and checks.json")
    ap.add_argument("--producer", help="path/to/file.py:func or module:func (layout seed -> {name: object})")
    ap.add_argument("--seeds", default="1,2,3", help="comma list of layout seeds (decimal strings)")
    for k in ("zoned", "city", "derive", "beams", "dress", "hq-rail"):
        ap.add_argument("--" + k, help=f"{k} JSON file")
    ap.add_argument("--parity", nargs=2, action="append", metavar=("A", "B"), help="two JSON files to compare byte for byte")
    ap.add_argument("--ref-config", help="art-pass pvc_config.json")
    ap.add_argument("--ref-rules", help="art-pass rules_check.md")
    ap.add_argument("--concepts", help="folder holding the golden images ({C}/ in the config)")
    return ap


def _load(path: Optional[str]) -> Optional[Dict[str, Any]]:
    return io.load(path) if path else None


def run_data(a: argparse.Namespace, cfg: Dict[str, Any]) -> List[R.Record]:
    """Data suite from the parsed arguments; the elapsed time is added as a note record."""
    inputs: Dict[str, Any] = {"producer": a.producer, "seeds": [s for s in a.seeds.split(",") if s],
                              "zoned": _load(a.zoned), "city": _load(a.city), "derive": _load(a.derive),
                              "beams": _load(a.beams), "dress": _load(a.dress), "hq_rail": _load(a.hq_rail),
                              "parity": [tuple(p) for p in (a.parity or [])]}
    recs, secs = D.run_data_suite(inputs, cfg)
    recs.append(R.record("12.3.time", R.PASS, round(secs, 3), "reported, 20 s budget", f"data suite {secs:.2f} s"))
    return recs


def run_images(a: argparse.Namespace, cfg: Dict[str, Any]) -> List[R.Record]:
    """Image checks on every capture under `--images`, plus renderer comparison against `--plates`."""
    recs: List[R.Record] = []
    plates = dict(IC.list_captures(a.plates)) if a.plates else {}
    for name, folder in IC.list_captures(a.images):
        rs, measured = IC.check_capture_folder(folder, cfg)
        recs += [dict(r, id=f"{name}/{r['id']}") for r in rs]
        if name in plates:
            _, golden = IC.check_capture_folder(plates[name], cfg)
            recs += IC.compare_renderers(golden, measured, cfg, prefix=f"{name}/RENDERER")
    return recs


def main(argv: Optional[List[str]] = None) -> int:
    """Run the selected checks, print the markdown report, write the files when `--out` is given."""
    a = build_parser().parse_args(argv)
    cfg = IC.load_config(a.config)
    if a.data:
        recs = run_data(a, cfg)
    elif a.images:
        recs = run_images(a, cfg)
    else:
        from . import reference as REF
        res = REF.run_reference(a.ref_config, a.ref_rules, a.concepts, cfg)
        sys.stdout.write(REF.summary_markdown(res))
        return 1 if any(s["mismatch"] for s in res["summary"].values()) else 0
    sys.stdout.write(R.to_markdown(recs))
    if a.out:
        R.write_reports(recs, a.out)
    return R.exit_code(recs)


if __name__ == "__main__":
    sys.exit(main())
