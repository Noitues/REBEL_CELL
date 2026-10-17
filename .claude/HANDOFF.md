# Handoff â€” REBEL_CELL art-pass (art director session)

| | |
|---|---|
| Written | 2026-10-16 ~01:30 local |
| Branch / commit | `art-pass` @ `41615f83` (pushed). Worktree: `C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass` |
| State | Round 1 is done and accepted by the art director. The designer reviews it in the morning (2026-10-16). No agents are running and the GPU is free. |

## Goal
I am the art director for REBEL_CELL on `art-pass`. Art only: no game design (memory `art-pass-no-game-design`).
- The concept work feeds a **pipeline-tools spec**: the Blender + Python tools that generate every netrun.
- The spec then goes as ONE hand-off package to the build session "Resume per HANDOFF.md" on `D:\Godot\rebel_cell`.
- That build session has the same name as this one, so address it by its ref [9d3b7c].

The designer's rule: the old art-direction session [061bfa] / `local_520d0498â€¦` is retired. Don't send it anything. All agents run from this session.

## Round 1: delivered and accepted by the AD (waiting for the designer's morning review)
**Storyboard v3, round 3** (`c83e3b00`), `route_map_graph/storyboard/`:
- Soft volumetric beam cones, coloured fog banks, a wet lit foreground, per-zoom exposure.
- `storyboard_v3a.mp4` is kept for comparison.
- Weak spots: the beam core reads as a line at dive height, and the nearest plinths in hover 2 stay dark.

**City all corps, revision 2b** (`a032bf6c`), `city_all_corps/`:
- The 7 districts read without labels, and there is one soft beam per landmark.
- The Tethys bay has clear water.
- The Meridian freight line runs from the north gate to the seawall at deck 17.5 BU. Its polyline is in `D:\rc_scratch\city_all_corps\meridian_rail.json`.

**HQ v2, all five** (`ae17ed12`, `46d161ce`, `41615f83`), `route_map_graph/hq_<corp>/*_v2.png`:
- The generalised kit, the dense city to the walls, and the occlusion rule (flatten, then ghost).
- Rebel Cell: a two-level Tokyo street with MAINFRAME as the hero.
- Meridian: the freight line on a 3 % grade, with the moat on W, S and E only.
- Solace: twin helix towers.
- Halcyon and Orbital finals predate the occlusion rule.

**Pipeline spec draft** (`418d1e13`), `route_map_graph/PIPELINE_SPEC.md`:
- 16 sections, with AD rulings on 24 source conflicts (Â§15).
- Â§13 holds the procedural-vs-hand-built gap rules; Â§12.7 holds the automatic composition checks.
- `TODO(refresh after sb v3 rev)` markers in Â§4/Â§11: refresh them from `sb_ocjobs.LOOK` now that the storyboard round 3 has landed.

**Procedural vs hand-built** (`87ca3762`), `route_map_graph/proc_vs_custom/`:
- 4 sheets plus metrics; the re-run command is in COMPARISON.md.
- Key finding: the procedural STREET is well behind the hand-built r3. It has a flat skyline, no signs, cut rooftops in the foreground, and thin fog. That is the main item for round 2.

## Decisions logged today (`docs/concepts/DIRECTION_REVIEW.md`)
- **Meridian freight line:** the line leads out of the fort, so the wallâ†”train shuttles are viable.
- **HQ occlusion rule:** sight-cone flatten to a 1â€“2 floor stub, then ghost to 15â€“20 %, with a 0.35 s ease.

## Waiting on the designer
- Reviews of all of round 1.
- Spec questions Q1â€“Q10 (`PIPELINE_SPEC.md` Â§14):
  - HQ scale against its lot;
  - mapping the graph onto slots;
  - distance LOD;
  - median tolerance;
  - landmark ratio above 2Ã— (MAINFRAME is about 12Ã—, Solace 2.8Ã—, Halcyon 2.9Ã—);
  - one power-cut level;
  - in-game entry durations;
  - the off-screen target marker;
  - art RNG streams;
  - zoom time (proposed 1.0 s).

## Next steps (after the designer's reviews)
1. Apply the designer's notes on round 1.
2. Round 2: implement the Â§13 gap rules on the procedural street, then re-run proc_vs_custom until the street passes:
   - `frontage.silhouette`, `dressing.signs`, `streets.light`, `foreground.street`, `atmosphere.layers`, `palette.districts`;
   - and on the HQs and city, `density.falloff`.
3. Refresh the spec's look values, and close the TODO markers.
4. Build the ONE hand-off package for [9d3b7c] and send it to the designer first. The build session cuts no work before the designer approves.
5. Later, when the designer schedules them: the boss wheel polish sessions, the Aurelian and Tethys HQ passes, and the Orbital cutscenes.

## Working model and gotchas (unchanged)
**GPU:**
- The protocol is in `D:\rc_scratch\GPU_QUEUE.md`: one Cycles job at a time, `GPU_LOCK`, and `GPU_WAITING_<name>`.
- Watch for orphan runners after agents are stopped.

**Rendering:**
- Headless Blender 5.2 with HIP. Never use the Blender MCP, and never touch the designer's Blender (pid 11904).
- ffmpeg isn't on PATH; encode with Blender's sequencer.
- Heavy scratch goes in `D:\rc_scratch\<task>\`.

**Shell:** never `python -` (agents keep slipping on this), never launch Godot, never write in `D:\Godot\rebel_cell`.

**Commits:**
- Use explicit paths. Never commit the `GPU_DONE` markers, `slicelib.py`, `tools/design_lab/w3_strips.gd.uid` or `__pycache__`.
- Big scratch folders (storyboard/scratch is about 133 MB) are not committed; only the crops are.

**Reviewing images:**
- Some PNGs can't be read directly. Convert them with the scratchpad's `topreview.py`, and build contact sheets with `sheet.py`.
- Values come from `values.py` (sRGB luma).

## Update 2026-10-16 evening (round 2 delivered)
- **Committed and pushed through `199a450e`:**
  - HQ finals: Rebel Cell v3, Solace v4 (hybrid interiors, no people), Meridian v3 (Gatehouse Gantry), Tethys v2 (pier city, whales).
  - City 4K finals on layout A2 (Horseshoe Bay, `city_planner/city_A2.json`), with terrain, bay and translucent day sea.
  - Street round 2 (`route_map_graph/street_r2/`), decision sheets (`route_map_graph/decisions/`), city planner designs A–E plus A2.
  - The spec answers all designer questions (`PIPELINE_SPEC.md`).
- **Not yet in the spec:**
  - the A2 layout-from-JSON step (`zoning_a2.py`), terrain (`terrain_a2.py`), bay (`city_bay_a2.py`);
  - the landmark-module hook (`LANDMARK_MODULES`, Meridian and Tethys);
  - the Solace hybrid interior-mapping shader (`hq_solace/scripts/hq_imap.py`).
- **Known gaps for the build session:**
  - road cuttings and tunnels (roads ride the terrain);
  - a straight sea edge at the far right of the city;
  - unique building ids;
  - JSON elements not mapped: undercity, drone corridors, ferries as routes, checkpoints, civic glyphs.
- **Next:** spec update (Sonnet, low effort), then the ONE hand-off package to build session [9d3b7c], shown to the designer first.
- **Token economy:** Sonnet/Haiku for mechanical work (memory `token-economy-agents`). Never taskkill by image name (memory `never-taskkill-by-image`).

## Queued after the token reset (agreed with the build session, 2026-10-16)
1. Tethys decision and hover finals (hq_tethys).
2. Aurelian Concord HQ design pass (fresh architect agent; full-city circus with columns as canonical).
3. A golden-plates section in the spec plus a plate set (PNG + values JSON + camera params) for the build session's drift checks.
4. Landmark .glb exports per corp.
Ownership: art-pass = Blender and visual quality; build session = tools/netrun_art, GDScript, Godot. See the build replan at D:\Godot\rebel_cell\docs\handoff\gates\REPLAN_2026-10-16.md §D.
