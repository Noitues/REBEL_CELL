"""Lower the W10 static visual lint baseline (tools/visual_qa/lint_baseline.json).

Run it after migrating literal colours or font sizes out of a file under scripts/ui:

    python tools/visual_qa/update_lint_baseline.py            # lower counts to today's (never raises)
    python tools/visual_qa/update_lint_baseline.py --check    # print UP/DOWN only, write nothing
    python tools/visual_qa/update_lint_baseline.py --reset    # write today's counts as they are
    python tools/visual_qa/update_lint_baseline.py --report out.json   # every finding with lines

The counting lives in one place, tools/visual_qa/visual_lint_static.gd (the GUT test uses
the same file), run here through a headless Godot with a timeout and its output in a log
file (never a pipe). Written as a file on purpose: never run Python from stdin here.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--godot", default=os.environ.get("GODOT", "godot"))
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true", help="report only")
    g.add_argument("--reset", action="store_true", help="write today's counts, raising any that went up")
    ap.add_argument("--report", help="write every finding (file, rule, lines) to this JSON file")
    ap.add_argument("--timeout", type=float, default=300.0)
    args = ap.parse_args()
    user = []
    if not args.check:
        user.append("--write=%s" % ("reset" if args.reset else "lower"))
    if args.report:
        user.append("--report=%s" % Path(args.report).resolve().as_posix())
    fd, log_path = tempfile.mkstemp(prefix="lint_static_", suffix=".log")
    os.close(fd)
    cmd = [args.godot, "--headless", "--path", str(ROOT), "-s", "res://tools/visual_qa/lint_static_cli.gd", "--"] + user
    with open(log_path, "w", encoding="utf-8", errors="replace") as log:
        try:
            code = subprocess.run(cmd, cwd=str(ROOT), stdout=log, stderr=subprocess.STDOUT, timeout=args.timeout).returncode
        except subprocess.TimeoutExpired:
            code = 124
    text = Path(log_path).read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if line.startswith(("UP ", "DOWN ", "LINT ", "ERROR", "SCRIPT ERROR")):
            print(line)
    if "LINT STATIC DONE" not in text:
        print("update_lint_baseline: Godot did not finish (exit %d); log: %s" % (code, log_path))
        return code or 1
    os.remove(log_path)
    return code


if __name__ == "__main__":
    sys.exit(main())
