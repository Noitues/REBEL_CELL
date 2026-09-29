"""Parallel GUT runner for REBEL_CELL (docs/TEST_SUITE.md).

Splits the test scripts into N shards balanced by the measured script times in
tests/test_manifest.json, runs one headless Godot per shard, merges the results and
exits non-zero on any failure, crash or timeout.

    python tools/run_tests.py                 # full suite, 4 shards
    python tools/run_tests.py -j 2            # full suite, 2 shards
    python tools/run_tests.py --tier fast     # the fast tier only (iteration)
    python tools/run_tests.py --select pass24 # scripts whose path contains "pass24"
    python tools/run_tests.py --update-times  # also write measured times to the manifest
    python tools/run_tests.py --no-isolate    # don't rerun failing scripts alone

A script that fails in its shard is run again alone (ANIM-R5): when it passes alone its
result depends on what ran before it in the shard (state leaking between scripts), and it
is reported as ORDER-DEPENDENT. The run still fails either way.

Each shard gets its own user:// directory (APPDATA / XDG_DATA_HOME point into the
shard's output folder), so save slots, profiles and GUT's temp files never collide
between shards or with a game or test run elsewhere on the machine. The single-process
command in CLAUDE.md stays valid; this runner only splits the same scripts.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tests" / "test_manifest.json"
TEST_DIRS = ["tests/unit", "tests/integration"]
# A script missing from the manifest (added on another branch) is still run; it is
# scheduled with this estimate and reported so it can be added.
DEFAULT_SECONDS = 10.0


def discover() -> list[str]:
    out: list[str] = []
    for d in TEST_DIRS:
        for p in sorted((ROOT / d).glob("test_*.gd")):
            out.append("res://" + p.relative_to(ROOT).as_posix())
    return out


def load_manifest() -> dict:
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)


def balance(scripts: list[str], seconds: dict[str, float], n: int) -> list[list[str]]:
    """Longest-processing-time-first: the slowest script goes to the emptiest shard."""
    shards: list[list[str]] = [[] for _ in range(n)]
    load = [0.0] * n
    # Ties broken by path so the split is deterministic.
    for s in sorted(scripts, key=lambda p: (-seconds.get(p, DEFAULT_SECONDS), p)):
        i = min(range(n), key=lambda k: (load[k], k))
        shards[i].append(s)
        load[i] += seconds.get(s, DEFAULT_SECONDS)
    return [sh for sh in shards if sh]


def shard_env(user_root: Path) -> dict[str, str]:
    env = dict(os.environ)
    user_root.mkdir(parents=True, exist_ok=True)
    # Godot's user:// lives under APPDATA on Windows and XDG_DATA_HOME on Linux.
    env["APPDATA"] = str(user_root)
    env["XDG_DATA_HOME"] = str(user_root)
    return env


def parse_junit(path: Path) -> dict:
    res = {"tests": 0, "failures": [], "pending": 0, "times": {}, "test_times": []}
    root = ET.parse(path).getroot()
    for suite in root.iter("testsuite"):
        name = "res://" + suite.get("name", "")
        total = 0.0
        for tc in suite.iter("testcase"):
            t = float(tc.get("time") or 0.0)
            total += t
            res["tests"] += 1
            res["test_times"].append((t, name, tc.get("name")))
            if tc.get("status") == "pending":
                res["pending"] += 1
            fail = tc.find("failure")
            if fail is not None:
                res["failures"].append((name, tc.get("name"), (fail.text or "").strip()))
        res["times"][name] = total
    return res


def godot_cmd(args, scripts: list[str], xml: Path) -> list[str]:
    # Headless already means no window and the Dummy audio driver; the flag says so.
    return [args.godot, "--headless", "--audio-driver", "Dummy", "--path", str(ROOT), "-s", "addons/gut/gut_cmdln.gd",
            "-gconfig=", "-gexit", "-glog=1", "-gtest=" + ",".join(scripts),
            "-gjunit_xml_file=" + str(xml)] + args.gut_arg


def isolate(scripts: list[str], out: Path, args) -> None:
    """Runs each failing script alone (at most --jobs at once) and says whether it passes
    alone: then its failure depends on the scripts before it in its shard."""
    print()
    print(f"run_tests: rerunning {len(scripts)} failing script(s) alone to spot order dependence")
    todo = list(enumerate(scripts))
    running: list[dict] = []
    while todo or running:
        while todo and len(running) < max(1, args.jobs):
            k, s = todo.pop(0)
            d = out / f"alone{k}"
            if d.exists():
                shutil.rmtree(d)
            d.mkdir(parents=True)
            log = open(d / "gut.log", "w", encoding="utf-8", errors="replace")
            p = subprocess.Popen(godot_cmd(args, [s], d / "results.xml"), cwd=str(ROOT), stdout=log,
                                 stderr=subprocess.STDOUT, env=shard_env(d / "userdata"))
            running.append({"s": s, "p": p, "log": log, "dir": d, "start": time.monotonic()})
        for r in list(running):
            rc = r["p"].poll()
            if rc is None and time.monotonic() - r["start"] > args.timeout:
                r["p"].kill()  # only this runner's own child process
                rc = r["p"].wait()
            if rc is None:
                continue
            r["log"].close()
            running.remove(r)
            xml = r["dir"] / "results.xml"
            alone_fails = parse_junit(xml)["failures"] if xml.exists() else None
            if alone_fails is None:
                print(f"  ALONE {r['s']}: wrote no results (log {r['dir'] / 'gut.log'})")
            elif alone_fails:
                print(f"  ALONE {r['s']}: fails alone too ({len(alone_fails)} failing)")
            else:
                print(f"  ORDER-DEPENDENT {r['s']}: passes alone; it fails after the scripts before it in its shard")
        time.sleep(0.5)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-j", "--jobs", type=int, default=4, help="number of shards (Godot processes)")
    ap.add_argument("--tier", choices=["all", "fast"], default="all")
    ap.add_argument("--select", default="", help="only scripts whose path contains this text")
    ap.add_argument("--godot", default=os.environ.get("GODOT", "godot"))
    ap.add_argument("--timeout", type=float, default=3600.0, help="seconds per shard")
    ap.add_argument("--out", default="", help="folder for shard logs and results (default: a new temp folder)")
    ap.add_argument("--update-times", action="store_true", help="write measured script times to the manifest")
    ap.add_argument("--list", action="store_true", help="print the shards and exit")
    ap.add_argument("--gut-arg", action="append", default=[], help="extra GUT argument for every shard (repeatable), e.g. --gut-arg=-gunit_test_name=foo")
    ap.add_argument("--no-isolate", action="store_true", help="don't rerun failing scripts alone to spot order-dependent ones")
    args = ap.parse_args()

    manifest = load_manifest()
    entries: dict = manifest["scripts"]
    found = discover()
    unlisted = [s for s in found if s not in entries]
    missing = [s for s in entries if s not in found]
    scripts = [s for s in found if args.tier == "all" or entries.get(s, {}).get("tier") == args.tier]
    if args.select:
        scripts = [s for s in scripts if args.select in s]
    if not scripts:
        print("run_tests: no scripts selected")
        return 2
    seconds = {s: float(entries.get(s, {}).get("seconds", DEFAULT_SECONDS)) for s in scripts}
    shards = balance(scripts, seconds, max(1, args.jobs))

    if args.list:
        for i, sh in enumerate(shards):
            print(f"shard {i}: ~{sum(seconds[s] for s in sh):.0f}s, {len(sh)} scripts")
            for s in sh:
                print(f"    {seconds[s]:7.1f}s  {s}")
        return 0

    out = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="rebel_cell_tests_"))
    out.mkdir(parents=True, exist_ok=True)
    print(f"run_tests: {len(scripts)} scripts in {len(shards)} shard(s); logs in {out}")
    for s in unlisted:
        print(f"run_tests: WARNING {s} is not in tests/test_manifest.json (scheduled at {DEFAULT_SECONDS:.0f}s)")
    for s in missing:
        print(f"run_tests: WARNING manifest lists {s}, which does not exist")

    procs = []
    t0 = time.monotonic()
    for i, sh in enumerate(shards):
        shard_dir = out / f"shard{i}"
        if shard_dir.exists():
            shutil.rmtree(shard_dir)
        shard_dir.mkdir(parents=True)
        xml = shard_dir / "results.xml"
        cmd = godot_cmd(args, sh, xml)
        log = open(shard_dir / "gut.log", "w", encoding="utf-8", errors="replace")
        p = subprocess.Popen(cmd, cwd=str(ROOT), stdout=log, stderr=subprocess.STDOUT,
                             env=shard_env(shard_dir / "userdata"))
        procs.append({"i": i, "p": p, "log": log, "xml": xml, "dir": shard_dir, "start": time.monotonic(), "end": None, "timed_out": False})

    pending = list(procs)
    while pending:
        for s in list(pending):
            rc = s["p"].poll()
            if rc is None and time.monotonic() - s["start"] > args.timeout:
                s["p"].kill()  # only this runner's own child process
                s["timed_out"] = True
                rc = s["p"].wait()
            if rc is not None:
                s["end"] = time.monotonic()
                s["rc"] = rc
                s["log"].close()
                pending.remove(s)
                print(f"run_tests: shard {s['i']} finished in {s['end'] - s['start']:.0f}s (exit {rc})")
        time.sleep(0.5)
    wall = time.monotonic() - t0

    total_tests = 0
    total_pending = 0
    failures: list = []
    problems: list[str] = []
    measured: dict[str, float] = {}
    for s in procs:
        sh = shards[s["i"]]
        if s["timed_out"]:
            problems.append(f"shard {s['i']} timed out after {args.timeout:.0f}s (log {s['dir'] / 'gut.log'})")
        if not s["xml"].exists():
            problems.append(f"shard {s['i']} wrote no results (crash or compile error; log {s['dir'] / 'gut.log'})")
            continue
        r = parse_junit(s["xml"])
        total_tests += r["tests"]
        total_pending += r["pending"]
        failures.extend(r["failures"])
        measured.update(r["times"])
        not_run = [x for x in sh if x not in r["times"]]
        for x in not_run:
            problems.append(f"shard {s['i']}: {x} did not run (log {s['dir'] / 'gut.log'})")
        if s["rc"] != 0 and not r["failures"]:
            problems.append(f"shard {s['i']} exited {s['rc']} without a failing test (log {s['dir'] / 'gut.log'})")

    print()
    print(f"run_tests: {total_tests} tests, {len(failures)} failing, {total_pending} pending, wall {wall:.0f}s")
    for name, test, msg in failures:
        print(f"  FAIL {name} :: {test}")
        for line in msg.splitlines()[:4]:
            print(f"       {line}")
    for p in problems:
        print(f"  ERROR {p}")

    if args.update_times and measured:
        for s, t in measured.items():
            if s in entries:
                entries[s]["seconds"] = round(t, 1)
        with open(MANIFEST, "w", encoding="utf-8", newline="\n") as f:
            json.dump(manifest, f, indent="\t", sort_keys=True)
            f.write("\n")
        print(f"run_tests: updated times for {len(measured)} scripts in {MANIFEST.relative_to(ROOT)}")

    if failures and not args.no_isolate:
        isolate(sorted({name for name, _t, _m in failures}), out, args)

    ok = not failures and not problems
    print("run_tests: PASSED" if ok else "run_tests: FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
