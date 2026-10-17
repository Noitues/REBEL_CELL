# Art session handoff (REBEL_CELL art-pass)

**Written** 2026-10-16 by the art-director session ("Resume Art-Pass"). Start the new art session with:

> Resume per docs/concepts/HANDOFF_PACKAGE/ART_SESSION_HANDOFF.md

## 1. Where things live

- **Live clone:** `C:/Users/noitu/Documents/Godot/rebel_cell`.
- **Art worktree:** `C:/Users/noitu/Documents/Godot/rebel_cell/.claude/worktrees/art-pass`.
- **Branch:** `art-pass`, pushed to origin.
- **Never merge `docs/concepts` into main.** It is about 4 GB of renders. Main has only the text import, at `docs/handoff/netrun_art/` (pinned to art-pass@7f021c21, with an INDEX).
- **Build session:** "Resume per HANDOFF.md", working in `D:\Godot\rebel_cell`. Never write in `D:\Godot\rebel_cell`. Address it by its session id from `list_sessions`. Short refs change; titles collide with this session's.
- **Heavy scratch:** `D:\rc_scratch\<task>\`. C: is tight.

| Doc | Path (under `docs/concepts/`) |
|---|---|
| Decision log | `DIRECTION_REVIEW.md` (newest at the end) |
| Spec | `route_map_graph/PIPELINE_SPEC.md` (§0 defines path abbreviations, e.g. `HK/` = `route_map_graph/hq_meridian/scripts/hq_kit/`) |
| Build hand-off | `HANDOFF_PACKAGE/README.md` (sent and accepted) |

## 2. Current vs superseded (designer-approved unless noted)

| Area | CURRENT | Superseded |
|---|---|---|
| Storyboard | `route_map_graph/storyboard/storyboard.mp4` (v3 round 3) | `storyboard_v3a.mp4`, v2 animatic |
| Halcyon HQ | `route_map_graph/hq_halcyon/H_*_v2.png` (predates the occlusion rule) | v1 |
| Orbital HQ | `route_map_graph/hq_orbital/H_*_v2.png` (predates the occlusion rule) | v1 |
| Rebel Cell HQ | `route_map_graph/hq_rebel_cell/H_*_v3.png` + `H_red_*_v3.png` | v2, v1 |
| Solace HQ | `route_map_graph/hq_solace/H_*_v4.png` (hybrid interiors, no people) | v3, v2 |
| Meridian HQ | `route_map_graph/hq_meridian_v3/` (Gatehouse Gantry), `H_*_v3.png` | the entire `route_map_graph/hq_meridian/` container fort (its `scripts/hq_kit/` is still the canonical HK/ kit) |
| Tethys HQ | `route_map_graph/hq_tethys/H_overview_v2.png`, `tethys_closeup_v2.png` | `city_all_corps/tethys_flooded_closeup.png`, `*_test*` |
| Aurelian HQ | none yet; the canonical silhouette is the full-city colosseum (columns, stepped tiers) | — |
| City key art | `city_all_corps/city_all_corps_{night,labeled,day}.png`: layout A2, 4K, render settings (b) | `*_r2b.png`, legacy layout (`CITY_LAYOUT=legacy`) |
| City layout | `city_planner/city_A2.json` + `plan_A2_horseshoe_bay.png` | planner designs A–E (reference only) |
| Netrun street | `route_map_graph/street_r2/` (rules-based, 14/14 tests pass) | storyboard street plates, hand-built `side_view/v3_aaa/r3` (target reference only) |
| Decisions | `route_map_graph/decisions/` (Q4 / Q6 / Q9 answered) | — |
| Metrics | `route_map_graph/proc_vs_custom/` (re-run: `python route_map_graph/proc_vs_custom/scripts/run_proc_vs_custom.py`) | — |
| Boss wheels | v2 / v3 identities approved; `boss_wheel_v2/POLISH_SESSION_PROMPT.md` (polish sessions, designer-scheduled) | — |

**Rule:** full-city landmark designs are canonical, and HQ netrun views must match them (spec §8.6b).

## 3. Half-done or known gaps

- **City:**
  - No road cuttings or tunnels; roads ride the terrain.
  - A straight sea edge at the far right (the Veyra River runs past the plan bounds).
  - JSON elements not mapped: undercity, drone corridors, ferry routes, checkpoints, civic glyphs.
- **Halcyon and Orbital:** the v2 finals predate the occlusion rule. Their kits carry it, but the images were not re-rendered.
- **Tethys:** no decision or hover finals. Its HQ peak ratio is 3.7× (mean 1.9×), above 2×; that is only a warning, unconfirmed by the designer.
- **Solace v4:** landmark at 2.56×, slightly over the 2–2.5× target; accepted silently.
- **Meridian decision shot:** median 0.175 (warning band).
- **Street r2:** the decision view fails R-REP-1 (regular near-facade grid), and there are no facade props.
- **Spec:** `TODO(refresh after sb v3 rev)` markers in §4 and §11 may still need the final storyboard round-3 look values from `storyboard/scripts/sb_ocjobs.py`.

## 4. Post-reset queue (in order)

1. **Tethys decision and hover finals** (`hq_tethys/`, 2560x1440, the same look as v2).
2. **Aurelian Concord HQ design pass.**
   - Use a fresh architect agent, like the Meridian v3 pass: DESIGN.md, 3 massing thumbnails, a recommendation, then a test, then finals.
   - It must match the full-city colosseum (columns, stepped tiers; `city_all_corps/scripts/landmarks.py`).
   - Identity: `new_corps/roman/identity.md`.
3. **Golden plates.**
   - Add a "golden plates" section to PIPELINE_SPEC: the plate list, the tolerances (median 0.14 ±0.03 pass / ±0.05 warn, 25–40 % under 0.10, ≤ 2.5 % over 0.85, landmark ≈2×, warn above), and the camera params.
   - Build the plate set: PNG + a values JSON + camera JSON per plate, for every HQ overview/decision, the street OVERVIEW/DECISION, and the city.
   - The build session runs the §12 checks on its Godot captures against them.
4. **Standalone `<corp>_landmark.py` modules** for all 7 (Halcyon, Solace, Orbital, Meridian, Aurelian, Tethys, plus the Rebel Cell centre).
   - Use the `build(ctx)` contract (`city_all_corps/NOTES.md`, "Landmark modules").
   - Meridian (`hq_meridian_v3/scripts/meridian_landmark.py`) and Tethys (`hq_tethys/scripts/tethys_landmark.py`) exist. The others are built-ins in `city_all_corps/scripts/landmarks.py`, with HQ-scale builders in `hq_<corp>/scripts/hq_build*.py`.
   - Then export `.glb` per corp.
5. Re-render the Halcyon and Orbital HQ finals with the occlusion rule (low priority).

## 5. Ownership split (D8, agreed with the build session)

- **Art-pass:** Blender, look-dev, the reference build, golden plates, landmark/module `.glb` exports, visual-quality ownership.
- **Build session:** `tools/netrun_art` pure modules, the checks, the GDScript twins, everything in Godot. It runs the §12 checks on Godot captures and reports drift to art-pass.
- **Hand-offs:** `.glb` + golden plates + check reports.

**Build replan rulings** (main repo, `docs/handoff/gates/REPLAN_2026-10-16.md` §D):
- **D1:** Aurelian and Tethys are fully playable.
- **D3:** the procedural planner city replaces the fixed layout.
- **D9:** the Heat chip and the "RAID AT n" tick go on the map.
- **D10:** HQ runs may exceed 7 layers, each unique.

## 6. Open art questions for the designer

- Central Server names conflict across corps and GDD sections. The list is in `HANDOFF_PACKAGE/README.md` §6 (Tethys = "THE BLACK SMOKER").
- Tethys HQ peak at 3.7×: accept or dim?
- Metro loop: dropped in city round 3c when the circle highway became the perimeter ring. Restore it?
- Q9 per-corp variance defaults are provisional (Halcyon, Orbital, Aurelian LOW; Solace, Meridian, Tethys MEDIUM; Rebel Cell centre and sprawl HIGH).
- The spec's provisional numbers: HQ lot coverage ≥ 90 %, ≥ 2 key-landmark building types per corp, the target-arrow hysteresis of 5 % and fade of 0.15 s.

## 7. How to work (hard-won rules)

- **Token economy:** Sonnet (or Haiku) at low/medium effort for mechanical work (finals, compose, metrics, docs). The default model only for new design. Review small previews or contact sheets, never full-res.
- **GPU:** one Cycles job at a time (`D:\rc_scratch\GPU_QUEUE.md`, `GPU_LOCK`, `GPU_WAITING_*`).
  - Agents' fair-wait logic has deadlocked twice. Tell agents: "if the lock is free, take it", with batches under 10 min.
  - If jobs stall, stop the agents and run their queued commands in one plain sequential shell script (`D:\rc_scratch\manual_queue.sh` is an example).
- **Rendering:** headless Blender 5.2, HIP (`compute_device_type='HIP'`, `scene.cycles.device='GPU'`), BVH2. Ignore the "CUEW" warning.
  - Never use the Blender MCP, and never touch the designer's interactive Blender.
  - ffmpeg isn't on PATH; encode with Blender's sequencer.
- **Shell:**
  - **Never `python -`** (agents slip on this constantly; it hangs or stalls).
  - **Never `taskkill /IM`.** One agent killed every python process, including the designer's Blender MCP. Kill own PIDs only.
- **Commits:**
  - Explicit paths, with the trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
  - Never commit `GPU_DONE` markers, `slicelib.py`, `tools/design_lab/w3_strips.gd.uid`, `__pycache__`, `*.stackdump`, or big scratch folders.
- **Image review:** some PNGs won't load directly. Convert them to JPEG previews with PIL first (thumbnail ≤1280).
- **No game design in art-pass.** Rules go to the build and design sessions.
