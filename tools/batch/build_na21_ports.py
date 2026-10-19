"""NA-21 module ports through the Message Batches API (one request per module, Sonnet 5.5, cost cap $3).

    python tools/batch/build_na21_ports.py --out <dir> --submit      # build the requests, submit, save the batch id
    python tools/batch/build_na21_ports.py --out <dir> --ingest      # wait, fetch, write scripts/netrun_art/<file>.gd, print the cost

The system prompt is `tools/batch/prompts/na21_ports.md` plus the sources of the support classes; each user turn holds the Python
module(s) to port. Credentials: ANTHROPIC_API_KEY or the Windows user variable of that name (never printed). Written as a file on
purpose: never run Python from stdin on this machine.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_drafts import api_key  # noqa: E402

MODEL = "claude-sonnet-5-5"
PY = ROOT / "tools/netrun_art"
OUT_GD = ROOT / "scripts/netrun_art"
P_IN, P_OUT = 1.0, 5.0     # $/MTok at the batch price
CAP = 3.0

REVEAL_NOTES = """Port `lod.py` as `RevealTiers` (file reveal_tiers.gd). Public functions (same names as Python, config-backed):
`band_distance(z: float, d0: float = NAN, d1: float = NAN) -> float`, `zoom_dive(d, d0, d1)`, `zoom_detail(d, d_ov, d_dec)`, `dive_from_detail(zd, d_ov, d_dec, d0)`, `sstep(x, a, b)`,
`band_edges(ab: Array, d0: float = NAN, d1: float = NAN) -> Array`, `band(d: float, name: String, bands: Dictionary = {}) -> float`, `weights(d: float, bands: Dictionary = {}, floors: Dictionary = {}) -> Dictionary`
(an empty `floors` means the config floors), `lod_block() -> Dictionary` (NaN d0/d1 mean the config anchors; bands are read from config `lod.bands` as {name: [a, b]}; the ramps from `lod.ramps`).
ADD the per-asset reveal tiers (PIPELINE_SPEC 5.2b), not in Python: config `reveal` = {asset: [[tier: int, d_far: float, d_near: float], ...]}, distances camera-to-asset in BU.
`reveal_assets() -> Array` (sorted asset names), `tier_weight(asset: String, tier: int, d: float) -> float` (0 at and beyond `d_far`, 1 at and inside `d_near`, smoothstep in ln d exactly like `band`:
`t = clamp(ln(d_far / d) / ln(d_far / d_near))`, `smoothstep01(t)`; unknown asset or tier = 1.0, "always drawn"), `tier_weights(asset: String, d: float) -> Dictionary` ({tier int: weight}), `visible_tier(asset: String, d: float) -> int`
(the highest listed tier whose weight is above 0; 0 when none or the asset is unknown). Tiers of one asset overlap (cross-fade), so several weights can be above 0."""

POSES_NOTES = """Port `poses.py` as `NetrunPoseBuilder` (file netrun_pose_builder.gd). `const VERSION := 1`; the dive samples `[0.0, 0.25, 0.5, 0.75, 1.0]` and the walk names `["first", "mid", "last"]` are structural consts.
Public: `successors(run_graph: Dictionary, node: String) -> Array` ("" = None), `fixture_walks(run_graph: Dictionary) -> Dictionary`, `build_poses(derive: Dictionary, city: Dictionary, run_graph: Dictionary, net: Dictionary = {}) -> Dictionary`
(`{}` for no net). The Python class `_Ctx` becomes a private Dictionary context plus private static helper functions (one class per file; no inner class). In `_Ctx`, `self.d0 is not None` is "street with a net".
Map: `RG.*` -> `NetrunCameraRig`, `HO.*` -> `NetrunHqOrbit`, `HS.*` -> `NetrunHqSlots`, `LOD.*` -> `RevealTiers` (`zoom_dive`, `zoom_detail`, `weights`, `lod_block`), `SEC.*` -> `NetrunSection`, `OCC.*` -> `OcclusionHelper`,
`layer_nodes` -> `NetrunStreetDeriver.layer_nodes`. `dict(RG.RIG, look_bias_sign=...)` -> `NetrunCameraRig.street_rig_json()`, `dict(HO.HQ_RIG)` -> `NetrunHqOrbit.hq_rig()`, `RG.DIVE[...]` -> `NetrunCameraRig.dive_constants()[...]`.
Keep the int/float types of the output exactly (e.g. `u` in the dive samples is a float, `walked` is an Array of String ids). `rec["section"]` is only for kind "hq"."""

MODULES = [
    # (custom id, class, file, python files, notes)
    ("rig", "NetrunCameraRig", "netrun_camera_rig.gd", ["rig.py"],
     "The Python `Pose` class is already ported as `NetrunPose` (do NOT port it). Constants SENSOR, REF_W, REF_H, USE, UCX, UCY, UW, UH, SOLVER_*, RIG, LOOK_BIAS_SIGN, DIVE, HQ_PAGE come from config "
     "(`rig`, `look_bias_sign`, `dive`, `hq_page`); compute UCX etc. from `rig.use` with the same arithmetic. Port every other function including the ease functions and add `street_rig_json()` and `dive_constants()`. "
     "`bbox_px` returns `[]` where Python raises ValueError; `frame_points` treats that as `k = 9.0` inside the loop exactly as the Python `except ValueError`. The `centre` argument of `frame_points` is `[]` for None. "
     "`frame_points(pts, ...)`: `zip(*pts)` min/max per axis."),
    ("orbit", "NetrunHqOrbit", "netrun_hq_orbit.gd", ["hq/orbit.py"],
     "`FACES` is `NetrunHqSlots.FACES`. `HQ_RIG` is `hq_rig()`. `max(range(4), key=lambda i: (dot, -i))` picks the highest dot, ties to the LOWER index: write the loop with `>` comparing (dot, then -i)."),
    ("occ", "OcclusionHelper", "occlusion_helper.gd", ["occlusion.py"],
     "OCC dict = config `occlusion` (cone_margin, stub, ghost, edge, tsoft, vsoft); `FRONT_FADE`/`CLUTTER` from `front_fade_kit`/`clutter_kit` via `NetrunArtUnits.kit`; `EASE_S`, `MIN_SPAN` from config. "
     "`KEYS` becomes `keys()`. This helper runs on EVERY netrun view (street, HQ, exploit building) in OVERVIEW, DECISION, HOVER and every camera move; keep it pure and cheap. "
     "`occ_on` is a bool in the output dict."),
    ("lod", "RevealTiers", "reveal_tiers.gd", ["lod.py"], REVEAL_NOTES),
    ("section", "NetrunSection", "netrun_section.gd", ["section.py"],
     "`CONSTS` is `consts()`, built from the config `section` kit-unit pads and `NetrunArtUnits.kit`/`k_fit` with the Python arithmetic. `NO_CUT`, `ZCUT`, `LOOK_BLEND`, `POCHE`, `EDGE_COL` come from config `section`."),
    ("layout", "NetrunArtLayout", "netrun_art_layout.gd", ["layout.py"],
     "SKIP `apply_layout_rules` and `LAYOUT_RULES` (not needed by the twins; the city arrives already laid out). FRONT_BAND, EXTEND, BASE_TOL, AXIS_TOL come from config `layout`; FACE_TOL is only used by the skipped function. "
     "Keep OPEN_STATES, OWN_STATES, CORP_STATES, BFS_STEPS as consts. `_bfs` memoises `best(c, d)` in a Dictionary keyed by a String or an Array `[c, d]` (your choice); its tie rule is Python's `min(opts)` over `(turns, next_tile)` tuples, "
     "so compare turns first, then next tile `(i, j)` lexicographically. `_nearest_cell` keys are `(distance, cell)`: ties go to the lexicographically smaller cell. The `cells` list is sorted by `(i, j)`. Cells are `Vector2i` in GDScript. "
     "`_simplify` uses an exact cross-product test `!= 0` on floats made of x.5 values; keep it."),
    ("street", "NetrunStreetDeriver", "netrun_street_deriver.gd", ["derive/street.py"],
     "Imports: `LY.*` -> `NetrunArtLayout.*`, `RG.*` -> `NetrunCameraRig.*`, `game_partial`/`VERSION` -> `NetrunArtDeriver.game_partial(layout_seed: String, run: String, kind: String, corps: Array = []) -> Dictionary` and `NetrunArtDeriver.VERSION` (version 2). "
     "`RULES` -> `rules()`. `DeriveError` -> `{\"error\": msg}`. The `frontage` result rows are `dict(b, along=..., face=..., nrm=..., axis=..., dirn=...)`: copy `b` then add keys. "
     "In `choose_street` the score tuple `(layers assigned, floors, start_left 1/0)` is compared lexicographically and a later candidate wins only when STRICTLY greater; return it as `score` (an Array of 3 ints). "
     "`derive_street` output dict: keep EVERY key and type of the Python `base.update(...)`. `round(b[\"h\"], 1)` -> `roundf(x * 10.0) / 10.0` and `round(b[\"ts\"], 2)` -> `roundf(x * 100.0) / 100.0`. "
     "`a`, `c` in `street` are lists of two floats. `columns` rows are `[layer, bid]`. `partial` empty means build one with `NetrunArtDeriver.game_partial(str(city[\"layout_seed\"]), run_graph.get(\"run\", \"run\"), \"street\")`."),
    ("slots", "NetrunHqSlots", "netrun_hq_slots.gd", ["hq/slots.py"],
     "`SLOT_PARAMS` -> `slot_params()` (config `slot_params`; note `tier_floors` is an int in config, `int(p[\"tier_floors\"])` as in Python). `LANDMARK_ENTRIES` from config `landmark_entries`. `ENTRANCE_EPS` is a structural const (1e-9). "
     "`RULES[\"room_z_inset\"]` -> `NetrunStreetDeriver.rules()[\"room_z_inset\"]`. `layer_nodes` -> `NetrunStreetDeriver.layer_nodes`. `orbit.*` -> `NetrunHqOrbit.*`. `game_partial` -> `NetrunArtDeriver.game_partial(...)` (corps = [corp]), `VERSION` -> `NetrunArtDeriver.VERSION`. "
     "`overview.dir()` is `NetrunPose.dir()`. `FLOOR_BU` -> `NetrunArtUnits.floor_bu()`. `SlotError` -> `{\"error\": msg}`. In `derive_hq` the dict `rooms={i: rooms[i] for i in sorted(rooms)}` is just the rooms dict (key order does not matter, the writer sorts keys)."),
    ("poses", "NetrunPoseBuilder", "netrun_pose_builder.gd", ["poses.py"], POSES_NOTES),
]


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def system_blocks() -> list[dict]:
    support = "\n\n".join(f"### {p}\n```gdscript\n{read(ROOT / p)}\n```" for p in
                          ("scripts/netrun_art/netrun_art_units.gd", "scripts/netrun_art/netrun_pose.gd", "scripts/data/netrun_art_config_data.gd"))
    text = read(ROOT / "tools/batch/prompts/na21_ports.md") + "\n\n## Sources of the support classes\n" + support
    return [{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]


def build() -> list[dict]:
    out = []
    for cid, cls, fname, pyfiles, notes in MODULES:
        src = "\n\n".join(f"### tools/netrun_art/{f}\n```python\n{read(PY / f)}\n```" for f in pyfiles)
        user = (f"Port to `class_name {cls}` in `scripts/netrun_art/{fname}`.\n\nPython source (the oracle):\n{src}\n\nNotes for this module:\n{notes}\n")
        out.append({"custom_id": "na21__" + cid, "params": {
            "model": MODEL, "max_tokens": 24000, "system": system_blocks(), "thinking": {"type": "adaptive"},
            "output_config": {"effort": "medium"}, "messages": [{"role": "user", "content": user}]}})
    return out


def submit(d: Path) -> None:
    import anthropic
    reqs = build()
    d.mkdir(parents=True, exist_ok=True)
    (d / "na21_requests.jsonl").write_text("\n".join(json.dumps(r) for r in reqs) + "\n", encoding="utf-8")
    est = sum(len(json.dumps(r["params"]["messages"])) + len(json.dumps(r["params"]["system"])) for r in reqs) / 3.5 / 1e6 * P_IN
    print(f"{len(reqs)} requests, input estimate ${est:.3f} (cap ${CAP})")
    client = anthropic.Anthropic(api_key=api_key())
    b = client.messages.batches.create(requests=reqs)
    (d / "batch_ids.json").write_text(json.dumps({"na21": b.id}), encoding="utf-8")
    print("submitted", b.id)


def code_of(text: str) -> str | None:
    m = re.search(r"```gdscript\n(.*?)\n```", text, re.S)
    return m.group(1) + "\n" if m else None


def ingest(d: Path) -> None:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key())
    bid = json.loads((d / "batch_ids.json").read_text(encoding="utf-8"))["na21"]
    while True:
        b = client.messages.batches.retrieve(bid)
        if b.processing_status == "ended":
            break
        print(b.processing_status, b.request_counts.processing, "processing", flush=True)
        time.sleep(30)
    files = {f"na21__{c}": f for c, _, f, _, _ in MODULES}
    total = 0.0
    OUT_GD.mkdir(parents=True, exist_ok=True)
    for r in client.messages.batches.results(bid):
        if r.result.type != "succeeded":
            print(r.custom_id, r.result.type)
            continue
        m = r.result.message
        u = m.usage
        cost = ((u.input_tokens or 0) * P_IN + (getattr(u, "cache_creation_input_tokens", 0) or 0) * P_IN * 1.25
                + (getattr(u, "cache_read_input_tokens", 0) or 0) * P_IN * 0.1 + (u.output_tokens or 0) * P_OUT) / 1e6
        total += cost
        text = "".join(bl.text for bl in m.content if bl.type == "text")
        code = code_of(text)
        notes = text.split("```")[-1].strip()
        print(r.custom_id, "stop", m.stop_reason, "in", u.input_tokens, "out", u.output_tokens, f"${cost:.3f}", "code" if code else "NO CODE")
        if notes:
            print("   notes:", notes.replace("\n", " | ")[:700])
        if code:
            (OUT_GD / files[r.custom_id]).write_text(code, encoding="utf-8", newline="\n")
    print(f"BATCH COST ${total:.3f}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--ingest", action="store_true")
    a = ap.parse_args()
    d = Path(a.out)
    if a.submit:
        submit(d)
    if a.ingest:
        ingest(d)


if __name__ == "__main__":
    main()
