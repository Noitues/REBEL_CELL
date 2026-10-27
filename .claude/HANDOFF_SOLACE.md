# HANDOFF: Solace visual list (art-pass's Solace session), 2026-10-22

A fresh session resumes from this file alone. The designer paused on 2026-10-22, so start no new work until art-pass says so.

## Who you are and who you talk to
- This was the "Solace visual list (A-062/A-063 order)" session, started by **Resume Art-Pass** (local_9bc8d6cd-34c9-4590-8a8b-e5ddb503afee).
- **Art-pass is the designer's single interface.** Sheets, questions and design picks go to art-pass (SendMessage to that id), never
  to the user. Art-pass logs rulings in docs/concepts/DIRECTION_REVIEW.md.
- **Build** is "Resume per HANDOFF.md" (local_aa799908-e44d-4a41-b49f-2f1c55e227c9), in D:/Godot/rebel_cell (NEVER write there).
  Build merges art branches into main and replies in main:docs/handoff/netrun_art/MAILBOX_TO_ART.md (B-NNN). Read it with
  `git -C D:/Godot/rebel_cell show main:docs/handoff/netrun_art/MAILBOX_TO_ART.md`.
- **Mailbox rules (art-pass rulings 2026-10-22):**
  - Post a READY entry in art-pass docs/concepts/HANDOFF_PACKAGE/MAILBOX.md only after art-pass approves the sheet.
  - Art-pass ASSIGNS the A-number and does ALL pruning; never renumber or prune.
  - After posting, wake build once with one SendMessage naming the entry.
- **The look-toolbox** (local_59edc93f-f0e0-43fb-8a07-aa94f76898ce) owns rc_look modules and fenced shader lines. If you need its
  files, ask through art-pass.

## Worktrees, branches and heads (repo: the godot_look clone, origin D:/Godot/rebel_cell, fetch only)
| worktree | branch @ head | status |
|---|---|---|
| D:/rc_art/godot_look_nodes | art/look-nodes @ 3a13c63b | A-099, MERGED on main 505d4152 (B-079, gate20 green, strings re-exported). Done. |
| D:/rc_art/godot_look_bloom | art/look-bloom @ a91a2995 | A-096, MERGED on main c68fe831 (wired by build). Done. |
| D:/rc_art/godot_look_stills | art/look-stills @ 56430048 | A-092 + A-094, MERGED (main 85279eaa). Done. |
| D:/rc_art/godot_look_gatefix2 | art/look-gate @ 4458938c | Old. The gate fix 105e9808 (A-090) is merged; the stills commits on it were rebased into art/look-stills. Don't merge. |
| D:/rc_art/godot_look_hqport | art/look @ bd3c6499 | Superseded by art/look-gate 105e9808 (A-090, merged). Don't merge bd3c6499. |
| D:/rc_art/godot_look_run | detached dd89fefb | Old capture worktree; free to reuse or remove. |
Before new Godot work: `git -C D:/rc_art/godot_look_nodes fetch -q D:/Godot/rebel_cell main`, then branch a new worktree off
FETCH_HEAD. Untracked .uid files that main tracks block switches and rebases: delete only those (they regenerate).
Never merge main into an art branch: rebase onto it, or branch from it.

## Solace list (A-062 / A-063 order)
1. **District + landmark:** DONE.
   - Kits, landmarks, park and HQ merged earlier.
   - Re-shoot S4 on main a28e199b, ACCEPTED: art-pass docs/concepts/solace_vertical/district/godot_s4/.
   - DEFERRED: the raid-zoom re-shoot, until the raid redesign lands (raid screens are paused).
   - OWED: one SOLACE GENERAL frame from the GAME path (the shifted Site point on main, not city_lab's hand-placed `--site=4,9`),
     to confirm the real spot matches the look. Add it to the next Godot capture (the garden implementation).
2. **HQ scene:** DONE.
   - Pass 4 merged.
   - The `_compound_aaa` leak fix is merged (A-090).
   - The backdrop stills were re-baked (A-092), and the Site close-up reads as SOLACE GENERAL with a green cross (A-094; a red cross
     is the protected emblem, so never use one).
3. **TIDE / Bloom / infection (B-056):** DONE for the street and HQ look (A-096, merged and wired by build).
   - Concept: art-pass docs/concepts/solace_vertical/bloom/ (sheet_A3d.jpg rev 3, NOTES.md). Godot parity:
     bloom/godot/parity_A.jpg.
   - DEFERRED: any raid-outcome wiring and the raid map look. The raid concept frames (darker plum, rev 3) are concept-only until
     the raid redesign.
   - Open, not ours: the toolbox is measuring why the Godot street is darker than the plate.
4. **REST / WORKSHOP / CACHE (B-058):** DONE, A-099 merged (main 505d4152).
   - Picks: C slap-tag icons, A's event-page layout, no RUN column, CACHE #D22C40 (tritan 9 vs the ELITE room glow, accepted), and
     the CACHE loot header.
   - Sheets: art-pass docs/concepts/solace_vertical/nodes/ (concept) and nodes/godot/impl_sheet.jpg.
5. **Culture garden (EX-11, B-061):** CONCEPT ROUND (see below). Then the designer's pick through art-pass, then the Godot
   implementation (the building, the O0-O3 plaza route, the I1-I5 room kit, the target Rack, the Bloom A look on the garden).
   - Not ours, on hold: the key_intel / key_breach key-lot buildings (B-061 placeholders).

## Culture garden status
- Brief: D:/rc_scratch/solace_v1/BRIEF_garden.md, with art-pass's 5 additions at the end. The spec draft is
  D:/rc_scratch/solace_v1/garden_spec.md (a copy of main's docs/handoff/plan2/drafts/exploit_buildings/solace.md).
- Output: art-pass docs/concepts/solace_vertical/garden/ (sheet.jpg, the A/B/C frames, NOTES.md, scripts/). See the "Final state"
  line at the end of this file for whether the round finished and was committed.
- Directions: A "Glass ward" (iron-ribbed palm house on a porcelain base), B "Culture stack" (incubator trays, cryo-drum vault), C
  "Hanging mountain" (a terraced mountain in a glass shell).
- Next: art-pass takes the pick to the designer. Implement on a new branch off the latest main.

## Commands
- **Tests:** targeted only (the designer ruled out the full gate for art-pass slices; build runs it at merge). Run each script alone:
  `godot --headless --path . -s addons/gut/gut_cmdln.gd -gconfig= -gtest=res://tests/unit/<name>.gd -gexit > <log> 2>&1`.
  `-gconfig=` is REQUIRED, or .gutconfig.json runs the whole suite. Import first (`godot --headless --path . --import`). Never pipe
  Godot output; log to files on D:. New test scripts go into tests/test_manifest.json with their tier. Run test_visual_lint_static
  when GDScript touches colours (Palette tokens only, no literal Color()).
- **Windowed captures:** only `python tools/run_windowed.py --log <file> -- --resolution 1920x1080 <scene> -- <args>`, from a
  DETACHED worktree of the commit (`git worktree add --detach D:/rc_art/<name> <sha>`; import there; remove it after). Freeze with
  `--reduce-effects=1` (hq_run_lab) or `--freeze=1 --reduce-effects=1` (tools/city/city_lab). Labs:
  - tools/art_pipeline/hq_run/hq_run_lab.tscn (states run_/full_/gate_/hq_/site_<corp>; `--bloom*` flags);
  - tools/city/city_lab;
  - tools/city/na23_lab.gd (street, `--bloom`);
  - tools/art_pipeline/backdrop/bake_backdrop_stills.tscn (refuses stills baked from stills; `--old-dir`);
  - tools/design_lab/nodes_capture.tscn.
- **Blender:** headless only, `--factory-startup`. Never touch the designer's Blender or its MCP. Copy scene scripts into your
  concept folder's scripts/ and patch the copies.
- **GPU lock:** D:/rc_scratch/GPU_LOCK, protocol D:/rc_scratch/GPU_QUEUE.md, helper
  D:/rc_art/art-pass/docs/concepts/solace_vertical/district/scripts/gpu_lock.py (pass a ME name). One GPU job at a time. NEVER
  remove the lock by hand; only the helper releases your own.
- **Hard rules:**
  - D: drive only; scratch under D:/rc_scratch/solace_v1/.
  - Never `python -`: an empty heredoc hangs, and agents slipped on this repeatedly, so remind each brief.
  - Kill only your own PIDs, never by image name.
  - Commit by explicit paths with the trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` (also for Sonnet agents;
    fix it on rebase if they write their own); never commit .uid, scratch or GPU_DONE files.

## Agent lanes
- **Sonnet:** high effort for concept rounds and ports; medium for slices; low for captures.
- **Haiku:** mechanical jobs.
- **Batch API:** drafts.
- **Opus:** rulings only.
- Every brief: research real refs first and cite them; a squint test (320 px plus a 4 px blur) on every sheet; a side-by-side against
  the golden plate (numbers alone never pass); art only, no game rules.
- Briefs that worked are in D:/rc_scratch/solace_v1/BRIEF_*.md; reuse their hard-rules block.

## Running agents at handoff
See "Final state" below.

## Final state (2026-10-22, at handoff)
- **Garden concept round:** DONE and committed in art-pass 5e6f9ae7 (docs/concepts/solace_vertical/garden/sheet.jpg, NOTES.md, the
  A/B/C frames, scripts/). Sent to art-pass, which takes the pick to the designer when they return.
  - Agent recommendation: A "Glass ward". It is the only one whose O-route and door read clearly over the building at the squint, it
    is cheapest to build, and it stacks best for taller graphs. B is the alternative; C out-shines the route.
  - Fix in the implementation, whatever is picked:
    - The inside and street Bloom reads as a hot pink fill, not the approved "dark plum body, hot edge" (match bloom/NOTES Rev 3
      and the Godot port's look_bloom.tres).
    - The AAA-2 frames clip too much (2.9-8 % over 0.85 vs the 2 % wish).
    - The garden is toned down in the cel map only to stay under the HQ's ratio; check it doesn't vanish in Godot.
  - Lot ask for build, via art-pass: 48 x 42 BU (8 x 7 lots) instead of 48 x 36, to fit the plaza apron. Clearance stays 8 BU.
  - The street route in the frames is a simplified 6-node proxy; the route chrome is a proxy of the game's.
- **Owed:** the SOLACE GENERAL game-path frame (see the Solace list, item 1). Do it in the garden implementation's Godot capture.
- **Running agents:** none. All finished; no background shells or worktrees of this session are left running.
- **Merged on main this session:** A-090 gate fix, A-092 stills, A-094 Site close-up, A-096 Bloom, A-099 nodes (main 505d4152).
- **Heads:**
  - art/look-nodes 3a13c63b, art/look-bloom a91a2995, art/look-stills 56430048 (all merged);
  - art/look-gate 4458938c and art/look bd3c6499 (superseded; don't merge);
  - art-pass: see `git log -1` after this file's commit.

## Update from art-pass, after this handoff (2026-10-22)
- **Garden pick (designer):** B "Culture stack", **without the thin spires / masts around it**. The lot is 48 x 42 BU, posted to
  build as A-100; wait for build's reply before you lock the footprint.
- **Next:** implement it in Godot on a new art branch from the latest main. Fix the hot-pink Bloom fill (it should be A Necrosis's
  plum body with a hot edge), the AAA-2 clipping, and include the owed SOLACE GENERAL game-path frame. Send the sheet to art-pass.

## Garden B implementation: PAUSED (2026-10-27)
The designer paused the Solace roadmap, including this work, until the tide raid concept passes wrap and the plan is reassessed. Resume
only when art-pass says so. No READY was posted and no A-number was taken.
- **Brief:** D:/rc_scratch/solace_v1/BRIEF_garden_impl.md (scope, must-fixes, off-limits list, slices). Re-read it, and any new art-pass
  ruling, before you resume.
- **Branch:** worktree D:/rc_art/godot_look_hqport, branch art/solace-garden @ 628ba8dd (one WIP commit on main 885975b6). Not for
  merge. Rebase onto the latest main before you resume, and delete the untracked .uid files that collide with main first.
- **What 628ba8dd holds (the agent was stopped mid slice 3; nothing is tested or captured):**
  - Slice 1, the asset, is drafted:
    - pipeline tools/art_pipeline/city/{culture_garden_spec,build_culture_garden,make_culture_garden,validate_culture_garden}.py;
    - outputs assets/city/key_buildings/culture_garden/{culture_garden.glb, manifest.json}.
    - Verify the spires are dropped, the fit to 48 x 42, and that the trays are modular.
  - Slices 2-3, the look, are drafted:
    - scripts/city3d/garden_{stage,materials,lights,look}.gd;
    - shaders/city/garden_{pbr,glass}.gdshader and garden_bloom.gdshaderinc (the garden's own include);
    - city_view_3d.gd: +93 lines, stage_garden / set_key_buildings / unstage_garden. These are additions only; the Bloom code is untouched.
      The intended build call is `view3d.set_key_buildings(KeyLots.for_seed(seed, corps, lot_bu))`.
    - Lab: tools/art_pipeline/garden/garden_lab.{gd,tscn}.
    - The agent stopped on "GardenLook overrides from the manifest's bloom block", so treat garden_look.gd as unfinished.
- **Still to do:**
  - Finish slice 3: the plaza O0-O3, rooms I1-I5, the WORKSHOP alcove at I3, the vault crown target at I5.
  - Check the must-fixes:
    - Bloom: a plum body with a hot edge, not a pink fill;
    - clipping: under 2 % over 0.85, median 0.12-0.15;
    - agar hue ~147.
  - Slice 4, captures and the compare sheet: plate | before | after, squint rows, band tables, plus the owed SOLACE GENERAL game-path
    frame.
  - Slice 5: the fast-tier test, the manifest entry, the touched tests, the DECISIONS entry "2026-10-27 - LOOK Solace culture garden (B)".
  - Then the sheet goes to art-pass, and READY only after an explicit APPROVED (take the A-number from MAILBOX.md then).
- **State at pause:**
  - No agents running.
  - No processes of this work left: no Godot or Blender command lines mention hqport or garden.
  - This work holds no GPU lock.
  - No capture worktrees were created.
