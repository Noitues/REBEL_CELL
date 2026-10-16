# Handoff — REBEL_CELL art-pass (art director session)

| | |
|---|---|
| Written | 2026-10-15 19:38 local |
| Session id | 2fda7edc-043a-4f51-a33f-a1ec952ac703 (transcript: `C:\Users\noitu\.claude\projects\C--Users-noitu-Documents-Godot-rebel-cell\2fda7edc-043a-4f51-a33f-a1ec952ac703.jsonl`) |
| Branch / commit | `art-pass` @ `39c4392f` (pushed). Worktree: `C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass` |
| Reason for pause | User request: the session is getting token-expensive |

## Goal
I am the **art director** for REBEL_CELL (a Godot 4.7 cyberpunk roguelite deckbuilder), working on the `art-pass` branch.

The designer (the user) is driving a concept-first art pass on several fronts:
- the **netrun route map** (the V3 side-view street in the AAA-2 realistic night look, built from ONE continuous procedural city);
- the **netrun entry storyboard**;
- **HQ netruns** for the 5 corps;
- **two new corps** (Aurelian Concord/Roman, Tethys Deep/Atlantis);
- **boss wheel v2/v3**.

All of it feeds a later **pipeline-tools spec** (Blender + Python tools to generate every netrun), which then goes as ONE hand-off package to the build orchestrator session ("Resume per HANDOFF.md", on `D:\Godot\rebel_cell`).

I also reviewed the build orchestrator's batches. Reviews are per group sheet, at text 1.0 only, and gameplay is final at 1.0 with mouse/keyboard.

## Working model
- **I coordinate background agents.** They render with headless Blender 5.2 (Cycles, HIP on the AMD RX 6700 XT) and write to `docs/concepts/...`. I review their output, relay the designer's notes, commit and push (explicit paths, trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`), and send results to the designer with SendUserFile.
- **GPU queue protocol:** `D:\rc_scratch\GPU_QUEUE.md`.
  - One Cycles job at a time; the lock is `D:\rc_scratch\GPU_LOCK`, and waiting agents write `GPU_WAITING_<name>`.
  - Parallel GPU pipelines don't help: there is one GPU, and two jobs at once just share it and risk running out of VRAM.
- **Heavy scratch goes to `D:\rc_scratch\<task>\`**, because C: is tight (about 16–21 GB free). Clean C: by MOVING old `%TEMP%` work dirs to `D:\temp_archive_2026-10-15`, never by hard-deleting.

## Background agents RUNNING at handoff
These were spawned from this session. They may stop if this session is closed. If they did, re-launch them in the new session, using their folders' NOTES and scripts to resume.

| Agent | Output folder | State at 19:38 |
|---|---|---|
| Storyboard v3, one continuous city | `docs/concepts/route_map_graph/storyboard/` | Dive and street holds done. Moves plus the live-city layers are left, then compositing and encoding to replace `storyboard.mp4`. ETA ~20:15–20:30. |
| Full city render, all corps | `docs/concepts/city_all_corps/` | Waiting for the GPU after the storyboard. Delivers a 4K hero, a labelled version, a mainline-look version and a Tethys flooded close-up. |
| HQ revision pass (v2) | `docs/concepts/route_map_graph/hq_<corp>/` (outputs `*_v2.*`), status in `route_map_graph/hq_rev_STATUS.md` | Waiting after city_all_corps. Must send test overviews of Rebel Cell and Meridian to `D:\rc_scratch\hq_rev\tests\` before its full renders. |

## Pending reviews (what to check when each lands)
**Storyboard v3:**
- The beams must be soft volumetric cones, not laser rods; I flagged this on `test_frames/v3r2_rooms_open.png`.
- The cut-block outlines in the foreground must be gone.
- The fog strata must be about 1.3× denser.
- Values: 25–40 % of pixels under 0.10.

**HQ v2:**
- **Rebel Cell:** the mainline Tokyo-alley look plus the red MAINFRAME sign (`docs/concepts/round33_mainframe_sign/mainframe_red_v4.png`), keeping the three stacked lanes.
- **Meridian:** the route runs 360° round the fortress. Containers move wall-to-train every other turn and enable or disable links.
- **Orbital:** the platform centre is cleaned up; the rocket and silo read.
- **All five:** dense city right up to the walls, using the section cut instead of an empty belt.
- **Lighting:** the Solace, Rebel Cell and Meridian misses are fixed.

**City all corps:**
- All 7 districts read.
- Tethys is a flooded district with CLEAR water and a deeper distance fade.
- Rebel Cell is the Tokyo alley.

## State of the tree
- Committed and pushed through `39c4392f`. Everything finished so far is committed:
  - storyboard v2 animatic and v3 dive proof;
  - Halcyon and the other HQs (v1);
  - new corps;
  - boss wheel v2/v3 plus `boss_wheel_v2/POLISH_SESSION_PROMPT.md`;
  - route-map rounds;
  - `ROUTE_REQUIREMENTS.md`.
- **Uncommitted, in progress, owned by the running agents. Don't commit them mid-work:**
  - the storyboard scripts (`NOTES.md`, `look_preset.py`, `m44/onecity_*.py`, `sb_ocjobs.py`, `sb_onecity.py`, new `sb_ocfull.py`);
  - the test_frames v3/v3r2 PNGs;
  - `docs/concepts/city_all_corps/`.
- **Never commit:** the `GPU_DONE` marker files, `slicelib.py` and `tools/design_lab/w3_strips.gd.uid` at the worktree root (they aren't ours).

## Decisions and rationale
The decision log is `docs/concepts/DIRECTION_REVIEW.md`; the newest entries are at the end. The key ones:

**Route map:**
- V3 dynamic side view: parallax camera, a DECISION zoom by default, OVERVIEW on Z.
- AAA-2 realistic night look, kept at the r3 values (median luma about 0.14, 25–40 % of pixels under 0.10).
- Grease pencil for links, vinyl stickers for nodes, a hover power-cut.
- Traffic is light streaks only.
- The X cyberspace and wireframe directions were rejected; X2's scrolling-binary facades are parked.

**One continuous city:**
- The netrun street is derived from real map lots along the Site's border link. One camera, a look blend on shared geometry, and a section cut by zoom.
- Approved mainline layout rules: frontage ≥ 6 floors, border streets 8 BU, hero signage by rule.
- Rejected: cross-dissolving to a separate street set.

**Entry flow:**
- HQ (matches the mainline City Grid exactly; we never redesign finished mainline art) → select → jack-in (no wheel lens) → dive → walls dissolve into bits left to right with the links writing on → markers → zoom → choose.
- One press skips the whole sequence. The plan pencil is orange.
- The city is always alive; level of detail ramps with zoom.

**HQs:**
- Each has an orbit camera keeping the active room front and centre.
- Landmark lit to 1.5–2× its local background.
- Per corp:
  - Halcyon: spiral round the pyramid, exterior climbs, the eye as a lighthouse, SPOTTED; accepted as is.
  - Solace: two tube helix towers with oval portholes and a ladder route.
  - Orbital: sabotage circuits, then the early fire; the cutscenes are future work.
  - Rebel Cell: option A, three stacked lanes plus kill switches.

**Boss wheels v3:**
- Identities approved: Roman Pantheon (Ascendant + Omens); Atlantis Tank (fish are the slices, 2 to 8 arm pointers, kraken reveal).
- 4 rule exceptions approved.
- Polish happens in dedicated new sessions, one per wheel.

**New corps:**
- Identities, crests and icons accepted.
- The HQs for both need separate design passes. For Tethys, explore dams or water locks.

**Process:**
- NO game design in art-pass (memory `art-pass-no-game-design`).
- Don't render views no game screen uses.

## Constraints and gotchas
- **Never `python -`.** Agents keep slipping on heredocs; remind them.
- **Never launch Godot windowed**, and never write in `D:\Godot\rebel_cell`.
- **Blender MCP** connects to the designer's live Blender (protocol 9, behind the server's 13). Agents must NOT use it; render headless only.
- **Headless HIP** needs `compute_device_type='HIP'` plus `scene.cycles.device='GPU'` in each script.
  - HIP-RT costs about 86 s per render to build, so plain BVH2 is often faster.
  - Ignore the "CUEW init failed" warning (that's CUDA).
- **Video encoding:** ffmpeg isn't on PATH. Agents encode MP4s with Blender's built-in FFmpeg through the sequencer.
- **Git Bash fork errors** ("couldn't create signal pipe") sometimes kill an agent's queue script. Agents restart them; check the queue logs.
- **Task notifications:** "Agent … finished, background work still running" is usually interim; check the files and lock before reporting.

## Next steps
1. Confirm the three agents are still alive (`D:\rc_scratch\GPU_LOCK`, the `GPU_WAITING_*` files, `tasklist` for blender.exe, and the newest files in their folders). If any died, re-launch it from its folder's NOTES and scripts.
2. Review each result as it lands, against the "Pending reviews" list above, then commit (explicit paths), push and SendUserFile it to the designer.
3. After the storyboard v3 and HQ v2 are approved: write the **pipeline-tools spec** in `docs/concepts/route_map_graph/`. It covers:
   - the one-city derivation rules (storyboard NOTES, "One continuous city");
   - the look preset and LOD bands;
   - the `hq_kit` (`hq_halcyon/scripts/hq_kit/`) plus the generalised HQ kit;
   - the camera rig (`side_view/v3_dynamic/scripts/cam_rig.py`);
   - the dressing rules;
   - the Blender-to-Godot mapping;
   - the 5 gaps in `ROUTE_REQUIREMENTS.md`.
4. Build ONE hand-off package for the "Resume per HANDOFF.md" build session, then message it. The package contains:
   - the storyboard and spec;
   - the Godot mapping;
   - the mainline layout-rule changes;
   - the GDD naming notes (THE PANOPTICON was already suggested to it; the Central Server names conflict across GDD sections, flagged in the HQ NOTES).
   It must not cut slices before the designer approves.
5. **Later (designer-scheduled):**
   - boss wheel polish sessions (the prompt is ready);
   - Aurelian and Tethys HQ design passes;
   - the Orbital cutscenes.

## Open questions for the user
None blocking. Waiting on their reviews of the three running agents' results.
