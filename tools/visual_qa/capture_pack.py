"""Review-pack capture (ART-0 D, ported from art-pass W10 / W9F; ART_BIBLE §13).

Captures every reachable screen of main's game (tools/visual_qa/review_pack.gd lists them)
at each combination of the chosen axes, laid out at 1280x720 and saved at --save-size
(800x450 by default, to keep packs small), and writes

    <out>/<scale>_<input>_re-<off|on>_<filter>[_<setting>]/<screen>.png   (+ <screen>.lint.json)
    <out>/manifest.json   (screen, axes, path, status, warnings, errors per picture)
    <out>/lint.json, <out>/lint_report.md   (runtime lint, via lint_report.py)
    <out>/sheets/*.jpg    (contact sheets, via contact_sheet.py, with --sheets)

    python tools/visual_qa/capture_pack.py --out %TEMP%/qa/pack --screens combat_start,grid \\
        --scales 1.0,1.6 --inputs mouse,pad --sheets
    python tools/visual_qa/capture_pack.py --out %TEMP%/qa/matrix --matrix -j 3 --sheets

Axes: --scales 1.0,1.6,2.0  --inputs mouse,pad  --reduce-effects off,on
      --filters none,grey,deutan  --settings off,hc,rm,cb-deutan  --scramble
      --screens a,b,c (default: all)
--matrix: scales 1.0,1.6,2.0 x mouse,pad x reduce effects off,on x filters none,grey, plus
      high contrast, reduce motion and the colour-blind mode (deutan) at 1.0 and 2.0 with the
      mouse and reduce effects off. A setting this build's Settings lacks (ART-0 C ports them) is
      skipped and named in the manifest's "skipped".

Filters: --filter-mode pillow (default) captures once per scale/input/RE/setting and derives
the grey and deutan pictures with tools/visual_qa/filters.py (the same maths as the shader,
pixel for pixel on the final frame, a third of the Godot runs). --filter-mode shader runs
Godot once per filter with tools/visual_qa/cvd_filter.gdshader on a CanvasLayer on top.

Every Godot run goes through tools/run_windowed.py (no focus, no sound, worktree only)
with its own user:// folder (APPDATA / XDG_DATA_HOME under <out>/_runs), so the player's
settings, saves and profile are never read or written. A screen that fails, hangs past
--screen-timeout or crashes the run is recorded in the manifest and the run carries on
with the next screen. The Godot log is kept per combo and its ERROR lines are recorded.
Keep packs out of git: write them under %TEMP% (review packs that land in the repo go to
docs/art_review/ART-n/, which gets a .gdignore). The run stops before it starts when the
disk holding --out has less than --min-free-gb. Run it as a file; never `python -`.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
import filters as cvd  # noqa: E402
import pack_axes  # noqa: E402

SCENE = "res://tools/visual_qa/review_pack.tscn"
RUN_OVERHEAD_S = 90.0
MAX_RELAUNCHES = 60
ERROR_LINES_KEPT = 40
## Game time advances a fixed step per frame, so motion lands at the same frame each run
## and two captures of one build diff near zero.
FIXED_FPS = 60
DEFAULT_SAVE_SIZE = "800x450"
## Least free space (GB) on the disk holding --out before a capture starts.
MIN_FREE_GB = 5.0
## The --matrix preset: the main axes, then the accessibility settings at these scales.
MATRIX = {"scales": "1.0,1.6,2.0", "inputs": "mouse,pad", "re": "off,on", "filters": "none,grey"}
MATRIX_SETTINGS = {"settings": "hc,rm,cb-deutan", "scales": "1.0,2.0", "inputs": "mouse", "re": "off"}


def _split(v: str) -> list[str]:
    return [x.strip() for x in v.split(",") if x.strip()]


def list_harness(godot: str, work: Path) -> dict:
    """The harness's screen list and the settings this build has (headless: no renderer)."""
    work.mkdir(parents=True, exist_ok=True)
    out = work / "screens.json"
    log = work / "list.log"
    out.unlink(missing_ok=True)
    with open(log, "w", encoding="utf-8", errors="replace") as f:
        subprocess.run([godot, "--headless", "--path", str(ROOT), SCENE, "--", "--list=%s" % out.as_posix()],
                       cwd=str(ROOT), stdout=f, stderr=subprocess.STDOUT, timeout=300)
    if not out.exists():
        sys.exit("capture_pack: the harness did not list its screens (see %s)" % log)
    return json.loads(out.read_text(encoding="utf-8"))


def _env_for(user_dir: Path) -> dict:
    env = dict(os.environ)
    user_dir.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        env["APPDATA"] = str(user_dir)
    else:
        env["XDG_DATA_HOME"] = str(user_dir)
    return env


def _error_lines(log: Path) -> list[str]:
    if not log.exists():
        return []
    out = []
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        if "ERROR" in line:
            out.append(line.strip())
    return out


def capture_combo(args, screens: list[str], combo: str, axes: dict, shader_filter: str, work: Path) -> dict:
    """Runs the harness for one combo until every screen has a status. Returns
    {screen: status dict} plus the combo's Godot ERROR lines under "_errors"."""
    out_dir = Path(args.out).resolve() / combo
    out_dir.mkdir(parents=True, exist_ok=True)
    run_dir = work / combo
    run_dir.mkdir(parents=True, exist_ok=True)
    for s in screens:
        for ext in (".status.json", ".png", ".lint.json"):
            (out_dir / (s + ext)).unlink(missing_ok=True)
    statuses: dict[str, dict] = {}
    errors: list[str] = []
    todo = list(screens)
    launches = 0
    while todo and launches < MAX_RELAUNCHES:
        launches += 1
        log = run_dir / ("godot_%02d.log" % launches)
        (out_dir / "_current.txt").unlink(missing_ok=True)
        user = [
            "--out=%s" % out_dir.as_posix(),
            "--screens=%s" % ",".join(todo),
            "--scale=%s" % axes["scale"],
            "--filter=%s" % shader_filter,
            "--screen-timeout=%s" % args.screen_timeout,
            "--save-size=%s" % args.save_size,
        ]
        if axes["input"] == "pad":
            user.append("--pad")
        if axes["re"] == "on":
            user.append("--reduce-effects")
        if args.scramble:
            user.append("--scramble")
        if args.native:
            user.append("--native=%s" % args.native)
        if args.settle > 0:
            user.append("--settle=%d" % args.settle)
        user += pack_axes.SETTINGS[axes.get("setting", "off")][1]
        timeout = RUN_OVERHEAD_S + args.screen_timeout * (len(todo) + 1)
        cmd = [sys.executable, str(ROOT / "tools" / "run_windowed.py"), "--log", str(log), "--timeout", str(timeout),
               "--godot", args.godot, "--", "--fixed-fps", str(FIXED_FPS), "--resolution", "%dx%d" % (pack_axes.WIDTH, pack_axes.HEIGHT), SCENE, "--"] + user
        started = time.time()
        with open(run_dir / ("driver_%02d.log" % launches), "w", encoding="utf-8", errors="replace") as dl:
            code = subprocess.run(cmd, cwd=str(ROOT), stdout=dl, stderr=subprocess.STDOUT,
                                  env=_env_for(work / "_user" / combo)).returncode
        errors += _error_lines(log)
        progressed = False
        for s in list(todo):
            st = out_dir / (s + ".status.json")
            if st.exists():
                statuses[s] = json.loads(st.read_text(encoding="utf-8"))
                todo.remove(s)
                progressed = True
        if not todo:
            break
        cur_file = out_dir / "_current.txt"
        cur = cur_file.read_text(encoding="utf-8").strip() if cur_file.exists() else ""
        victim = cur if cur in todo else todo[0]
        why = "Godot exited with %d after %.0f s while on this screen" % (code, time.time() - started)
        if code == 124:
            why = "the run timed out (%.0f s) on this screen" % timeout
        statuses[victim] = {"screen": victim, "status": "crashed", "error": why, "errors": [], "warnings": []}
        todo.remove(victim)
        if not progressed and victim != cur:
            # Nothing ran at all (the harness never started): don't loop on every screen.
            for s in todo:
                statuses[s] = {"screen": s, "status": "crashed", "error": "the harness did not start: " + why,
                               "errors": [], "warnings": []}
            todo = []
    (out_dir / "_current.txt").unlink(missing_ok=True)
    statuses["_errors"] = errors[-ERROR_LINES_KEPT:]
    print("capture_pack: %s: %d ok of %d" % (combo, sum(1 for s in screens if statuses.get(s, {}).get("status") == "ok"), len(screens)))
    return statuses


def derive_filter(out: Path, src_combo: str, dst_combo: str, screens: list[str], flt: str) -> None:
    src = out / src_combo
    dst = out / dst_combo
    dst.mkdir(parents=True, exist_ok=True)
    from PIL import Image
    for s in screens:
        p = src / (s + ".png")
        if p.exists():
            cvd.apply(Image.open(p), flt).save(dst / (s + ".png"), optimize=False)
        else:
            (dst / (s + ".png")).unlink(missing_ok=True)


def plan(spec: dict, filter_mode: str) -> tuple[list, list]:
    """Jobs (combo, axes, shader filter) and Pillow-derived pictures (src, dst, axes, filter)
    for one axis spec {scales, inputs, re, filters, settings} (lists)."""
    jobs, derived = [], []
    for st in spec["settings"]:
        for sc in spec["scales"]:
            for inp in spec["inputs"]:
                for re in spec["re"]:
                    base = {"scale": sc, "input": inp, "re": re, "setting": st}
                    if filter_mode == "shader":
                        for f in spec["filters"]:
                            jobs.append((pack_axes.combo_name(sc, inp, re, f, st), dict(base, filter=f), f))
                    else:
                        src = pack_axes.combo_name(sc, inp, re, "none", st)
                        jobs.append((src, dict(base, filter="none"), "none"))
                        for f in spec["filters"]:
                            if f != "none":
                                derived.append((src, pack_axes.combo_name(sc, inp, re, f, st), dict(base, filter=f), f))
    return jobs, derived


def _spec(scales: str, inputs: str, re: str, filters: str, settings: str) -> dict:
    return {"scales": [pack_axes.scale_text(s) for s in _split(scales)], "inputs": _split(inputs),
            "re": _split(re), "filters": _split(filters), "settings": _split(settings)}


def main() -> int:
    sys.stdout.reconfigure(line_buffering=True)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--screens", default="", help="comma list (default: every screen)")
    ap.add_argument("--scales", default="1.0")
    ap.add_argument("--inputs", default="mouse")
    ap.add_argument("--reduce-effects", default="off", help="off,on")
    ap.add_argument("--filters", default="none", help="none,grey,deutan")
    ap.add_argument("--filter-mode", choices=["pillow", "shader"], default="pillow")
    ap.add_argument("--settings", default="off", help="off,hc,rm,cb-deutan,cb-protan,cb-tritan (gated on Settings)")
    ap.add_argument("--matrix", action="store_true", help="the full preset (see above); overrides the axis options")
    ap.add_argument("--scramble", action="store_true")
    ap.add_argument("--save-size", default=DEFAULT_SAVE_SIZE, help="PNG size WxH (layout stays 1280x720)")
    ap.add_argument("--screen-timeout", type=float, default=90.0)
    ap.add_argument("--native", default="", help="WxH: the window at this size, saved 1:1 (review_pack --native, B1b)")
    ap.add_argument("--settle", type=int, default=0,
                    help="frames a screen settles before its picture (0: the harness's own; B5: more lets pencil finish writing on)")
    ap.add_argument("-j", "--jobs", type=int, default=1, help="Godot runs at once (default 1)")
    ap.add_argument("--godot", default=os.environ.get("GODOT", "godot"))
    ap.add_argument("--min-free-gb", type=float, default=MIN_FREE_GB)
    ap.add_argument("--no-lint", action="store_true", help="skip lint_report.py")
    ap.add_argument("--sheets", action="store_true", help="also build contact sheets (contact_sheet.py)")
    ap.add_argument("--list", action="store_true", help="print the screen list and the settings axes, and exit")
    args = ap.parse_args()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if ROOT in out.parents:
        # Inside the project: Godot must not import review PNGs, and git must not see them.
        (out / ".gdignore").touch()
        if "art_review" not in out.parts:
            print("capture_pack: warning: %s is inside the project; packs belong under %%TEMP%% "
                  "or docs/art_review/ART-n/" % out)
    free_gb = shutil.disk_usage(out).free / 1e9
    if free_gb < args.min_free_gb:
        sys.exit("capture_pack: %.1f GB free on the disk of %s (< %.1f GB): not capturing" % (free_gb, out, args.min_free_gb))
    work = out / "_runs"
    listing = list_harness(args.godot, work)
    known = listing["screens"]
    have = listing.get("settings_axes", {})
    order = {s["screen"]: i for i, s in enumerate(known)}
    what = {s["screen"]: s["what"] for s in known}
    if args.list:
        for s in known:
            print("%-22s %s" % (s["screen"], s["what"]))
        print("settings axes on this build: %s" % ", ".join("%s=%s" % kv for kv in sorted(have.items())))
        return 0
    screens = _split(args.screens) or [s["screen"] for s in known]
    unknown = [s for s in screens if s not in order]
    if unknown:
        sys.exit("capture_pack: unknown screens %s (see --list)" % ", ".join(unknown))
    if args.matrix:
        specs = [_spec(MATRIX["scales"], MATRIX["inputs"], MATRIX["re"], MATRIX["filters"], "off"),
                 _spec(MATRIX_SETTINGS["scales"], MATRIX_SETTINGS["inputs"], MATRIX_SETTINGS["re"], "none",
                       MATRIX_SETTINGS["settings"])]
    else:
        specs = [_spec(args.scales, args.inputs, args.reduce_effects, args.filters, args.settings)]
    skipped = []
    for spec in specs:
        for v, allowed, name in ((spec["inputs"], pack_axes.INPUTS, "inputs"), (spec["re"], pack_axes.RE, "reduce-effects"),
                                 (spec["filters"], pack_axes.FILTERS, "filters"), (spec["settings"], tuple(pack_axes.SETTINGS), "settings")):
            bad = [x for x in v if x not in allowed]
            if bad:
                sys.exit("capture_pack: bad --%s %s (allowed: %s)" % (name, bad, ",".join(allowed)))
        # Gate: a setting this build's Settings lacks is skipped (ART-0 C ports them).
        keep = []
        for st in spec["settings"]:
            prop = pack_axes.SETTINGS[st][0]
            if prop == "" or have.get(prop, False):
                keep.append(st)
            elif st not in [s["setting"] for s in skipped]:
                skipped.append({"setting": st, "why": "Settings has no %s on this build" % prop})
        spec["settings"] = keep
    for s in skipped:
        print("capture_pack: skipped setting %s: %s" % (s["setting"], s["why"]))
    jobs, derived = [], []
    for spec in specs:
        j, d = plan(spec, args.filter_mode)
        jobs += [x for x in j if x[0] not in {y[0] for y in jobs}]
        derived += [x for x in d if x[1] not in {y[1] for y in derived}]
    t0 = time.time()
    results: dict[str, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        futs = {ex.submit(capture_combo, args, screens, c, a, f, work): c for c, a, f in jobs}
        for fu in concurrent.futures.as_completed(futs):
            results[futs[fu]] = fu.result()
    for src, dst, _a, f in derived:
        derive_filter(out, src, dst, screens, f)
    # Manifest: this run's entries replace the same screen + combo, others are kept.
    manifest = pack_axes.load_manifest(out)
    ran = {c for c, _, _ in jobs} | {d for _, d, _, _ in derived}
    keep_entries = [e for e in manifest.get("entries", []) if not (e["screen"] in screens and e["combo"] in ran)]
    entries = list(keep_entries)
    combo_errors = dict(manifest.get("godot_errors", {}))

    def entry(screen: str, combo: str, axes: dict, st: dict, derived_from: str = "") -> dict:
        ok = st.get("status") == "ok"
        e = {"screen": screen, "what": what.get(screen, ""), "order": order[screen], "combo": combo, "axes": axes,
             "path": "%s/%s.png" % (combo, screen) if ok else "",
             "lint": "%s/%s.lint.json" % (derived_from or combo, screen) if ok else "",
             "status": st.get("status", "missing"), "error": st.get("error", ""),
             "errors": st.get("errors", []), "warnings": list(st.get("warnings", [])),
             "seconds": st.get("seconds", 0)}
        if derived_from:
            e["warnings"].append("%s derived with Pillow from %s" % (axes["filter"], derived_from))
        return e

    for c, a, _f in jobs:
        st = results.get(c, {})
        combo_errors[c] = st.get("_errors", [])
        for s in screens:
            entries.append(entry(s, c, a, st.get(s, {"status": "missing", "error": "no status written"})))
    for src, dst, a, _f in derived:
        st = results.get(src, {})
        for s in screens:
            entries.append(entry(s, dst, a, st.get(s, {"status": "missing"}), src))
    entries.sort(key=lambda e: (pack_axes.combo_sort_key(e["combo"]), e["order"]))
    manifest = {
        "about": "Review pack (tools/visual_qa/capture_pack.py, ART-0 D). One entry per screen and axis combo.",
        "size": [pack_axes.WIDTH, pack_axes.HEIGHT],
        "save_size": args.save_size,
        "filter_mode": args.filter_mode,
        "scramble": args.scramble,
        "settings_axes": have,
        "skipped": skipped,
        "text_scale_note": "text_scale is written directly (past Settings' clamp, %s on this build) as the storyboard does." % listing.get("text_scale_max", "?"),
        "godot_errors": combo_errors,
        "entries": entries,
    }
    (out / pack_axes.MANIFEST).write_text(json.dumps(manifest, indent=1), encoding="utf-8", newline="\n")
    bad = [e for e in entries if e["status"] != "ok" and e["screen"] in screens]
    print("capture_pack: %d pictures, %d not captured, %.0f s -> %s" % (len(entries) - len(bad), len(bad), time.time() - t0, out))
    for e in bad:
        if not e["warnings"] or "derived" not in e["warnings"][-1]:
            print("  %s %s: %s %s" % (e["combo"], e["screen"], e["status"], e["error"]))
    shutil.rmtree(work / "_user", ignore_errors=True)
    if not args.no_lint:
        subprocess.run([sys.executable, str(HERE / "lint_report.py"), str(out)], cwd=str(ROOT))
    if args.sheets:
        subprocess.run([sys.executable, str(HERE / "contact_sheet.py"), str(out)], cwd=str(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
