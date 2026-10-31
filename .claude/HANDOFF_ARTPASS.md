# Handoff: art-pass (REBEL_CELL), Solace vertical slice

| | |
|---|---|
| Written | 2026-10-31 08:12 local |
| Session id | a4b265ab-09bd-4ff8-861a-56cf9d74706b (`claude --resume`) |
| Worktree / commit | D:/rc_art/art-pass, branch art-pass @ c08c7ce7 (all work committed; only scratch files untracked) |
| Reason for pause | User request: clearing the session, restarting after the weekly reset |

## Goal
The designer's single visual interface for the Solace-only vertical slice: one continuous cel look from the city view down to a street-level netrun, with matching screens, transitions and end screens, all judged against the golden plates (`docs/concepts/golden_plates/street_overview.png`, `hq_rebel_cell_overview.png`). Art only: no game design. Rules and data go to build through the mailbox.

## Read first
1. `docs/concepts/DIRECTION_REVIEW.md`: the end of it. Every ruling is there. ART CALLs 46–49 (2026-10-30 designer answers, picks, the staged street, the 12 transitions), then "Overnight choices" O-1 to O-10 (decisions I made while the designer slept; the designer may overrule any).
2. `docs/concepts/SOLACE_SLICE_ROADMAP.md`.
3. `docs/concepts/HANDOFF_PACKAGE/BUILD_MERGE_GUIDE.md` and the mailbox `HANDOFF_PACKAGE/MAILBOX.md` (A-104 to A-114; "last read" is B-083).
4. Memory index: `C:\Users\noitu\.claude\projects\C--Users-noitu-Documents-Godot-rebel-cell\memory\MEMORY.md`, especially `token-economy-agents`, `targeted-tests-not-full-gate` and `solace-slice-direction`.

## Standing rules (also in memory)
- **Token economy:** the designer set the session to Sonnet until the weekly reset. Use `effort: low` Sonnet or Haiku agents, and the Batch API for text (`docs/concepts/HANDOFF_PACKAGE/batch/art_batch.py`; Haiku 5.5 needs thinking disabled and max_tokens 16000, Sonnet uses between_tools).
- **Never write "full suite" into an agent brief.** Targeted tests only. Build's merge runs the full gate.
- Never run `python -` in any form (it hangs; agents slip on it constantly). Run script files by path. Never pipe Godot output. Windowed Godot only through `tools/run_windowed.py` and the GPU lock.
- Never write in D:/Godot/rebel_cell (main, read-only). D: drive only. Kill only your own PIDs (never `taskkill /IM`). Never touch the designer's Blender or its MCP.
- Nothing replaces `final/`, the golden plates or main without designer review. Commit by explicit paths, with the trailer "Co-Authored-By: Claude <model> <noreply@anthropic.com>" matching the session model.
- The mailbox-check cron (session-only, hourly at :17) dies with the session. Recreate it if wanted. The prompt is "Mailbox check (art-pass): run `git -C D:/Godot/rebel_cell show main:docs/handoff/netrun_art/MAILBOX_TO_ART.md` and read any B entries after the last-read line in D:/rc_art/art-pass/docs/concepts/HANDOFF_PACKAGE/MAILBOX.md ..." Build's last entry is B-083 and nothing new has arrived for hours.
- The designer asked for choices to be made and logged, not asked about, while away. Checkpoint with them every few rounds, and anchor to their rulings, never to a metric.

## State of the work
**Everything is committed.** No agents are running.

| Area | Where | Status |
|---|---|---|
| City view r43 | clone `D:/rc_art/godot_look_tide`, branch art/tide-r43 (e2c9976c) | Accepted; full suite 4,080 tests, 0 failing. `final_proposed/` awaits designer sign-off before replacing `final/`. |
| Corp-colour traffic | `D:/rc_art/godot_look_traffic`, art/tide-traffic-corp 5df3d8ae (base r43) | Adopted by the designer; tuned (10x speed, random platoons, streak swap). Targeted tests only. |
| Jack-in prewarm | `D:/rc_art/godot_jackin`, art/jackin-prewarm 903853d4 (on game-v2) | READY, posted as A-114. About 22 s down to 10–11 s. Build merges. |
| Netrun zoom (street level) | godot_look_tide, art/netrun-zoom bf1e5737 | Round 4 done: dolly target bug fixed, staged street, plum facades, glossy road. Output in `docs/concepts/netrun_cel/zoom_rules/round4/`. |
| LOD sheets | art/zoom-lod-sheets 38f75b23 (worktree `D:/rc_art/godot_look_lod`) | 17 element sheets in `netrun_cel/zoom_rules/lod_sheets/`. The designer asked for these to review element by element; not yet reviewed. |
| Transitions | `docs/concepts/transitions/v2/` | 12-transition storyboard; 10 assumptions logged as O-1. |
| End screens | `docs/concepts/solace_endscreens/v2/` | Folder memo; the designer picked image slot B (survey map with grease pencil) for both. |
| Combat backdrop | `docs/concepts/combat_backdrop/v2/` | Cutaway picked; rooms per Site role. E10 is the approved combat target. |
| Supporting screens | `docs/concepts/cohesion/supporting_r42/` | 7 of 7 done on the new city, Solace names. |
| ART_BIBLE | `docs/concepts/ART_BIBLE_AMENDMENTS_DRAFT.md` | Draft only; ART_BIBLE.md untouched. |

## Decisions and rationale (the non-obvious ones)
- **Netrun look = the city cel look zoomed in** (not AAA-2 realism). Rules may bend for the look, and pink is allowed where it serves. The slice is Solace-only and Meridian is hibernated (A-112 sent to build).
- **The netrun street is staged:** the real city has no street like the plate (mostly low buildings, no wide plaza). The road is widened about 3x in the view only, the real facing row keeps its real heights, and nodes sit only on visible floors. The HQ netrun is a hand-authored set piece with the real city behind it.
- **Zoom detail by px/BU bands** (City under 8, District 8–16, Near-street 16–28, Street 28–56, Close 56+), with per-element phases. The spec is `netrun_cel/zoom_rules/ZOOM_RULES.md`. It is gated behind `CityConfig.zoom_rules_on` (off by default; the City band is bit-exact against r43).
- **The Blender re-creation did not work for the zoom** (it did not look like the city); the real-engine zoom did. Do not go back to Blender for city-to-street continuity.
- The designer dropped colour-blind work; ignore `polish/colourblind/`.

## Constraints and gotchas
- The whole camera path must derive from ONE target street (`CityZoomTarget`, centre lot (34.5,-7.5), look N). An earlier dolly ended on the wrong street because of two targets.
- The street camera was 1.8x too zoomed in (a set_iso frustum bug), fixed in round 3.
- The GPU is shared and perf numbers swing (3.5 to 14 ms). Re-measure street-band p95 on a quiet GPU before claiming a result (limit 12.57 ms). Round 4's perf is unverified.
- Merge order for build is in BUILD_MERGE_GUIDE.md. Conflicts are expected between art's city3d chain and the jack-in branch in `city_view_3d.gd` and `city_water.gd`.
- 15 pre-existing tests fail on build's game-v2 (listed in A-114); those are build's.
- Untracked stray files in the art-pass worktree (`ART_DECO_PROMPT.md`, `GODOT_LOOK_TOOLBOX_PROMPT.md`, `bash.exe.stackdump`, `netrun_cel/v2/scripts/inspect_*.py` and `patch_city*.py`) are scratch or foreign. Do not commit them and do not delete foreign files.
- `.claude/HANDOFF.md` is the older animation-pass handoff and was left untouched. This file is the current one.

## Verification status
- r43: full suite 4,080 tests, 0 failing. Everything after that ran targeted tests only: netrun-zoom round 4 (121 tests after fixes, 0 failing), traffic (56, 0 failing), jack-in (its own tests pass).
- Nothing has been re-run since the last commits. No full gate has run on the netrun-zoom or traffic branches.

## Next steps (in order)
1. Read the designer's feedback on the sheets they have (LOD sheets, transitions v2, supporting screens, end screens, the round 4 street). Log changes as new ART CALLs.
2. Street polish pass (O-2): darker upper facades, more road streaks, the storefront band to 2.5x at 70–75 % down, and a quiet-GPU p95 re-measure. Brief the netrun-zoom agent at low effort with targeted tests.
3. E10 micro-detail polish on the combat plate against the cutaway backdrop (look-dev; Sonnet or better after the reset).
4. Redo the transitions v2 key frames with real renders where they now exist (T3, T6 bits, T11 HQ fly-in), and make T2 and T3 show the cutaway, not the old E10 backdrop.
5. Solace HQ netrun: the hand-authored set piece at golden-plate polish. Frame 4 in `netrun_cel/v2/` is only a concept.
6. Event and shop room interiors for the netrun street. The cutaway kit has bio-lab, server room and greenhouse; records and lobby are built but not rendered as rooms.
7. Fold ART_BIBLE_AMENDMENTS_DRAFT.md into ART_BIBLE.md once the designer reviews it.
8. When the designer approves r43: replace `final/` with `final_proposed/`, update the golden plates, and tell build to merge (BUILD_MERGE_GUIDE.md).
9. Netrun node anchors (street cabinet, rooftop relay, kiosk, storefront, data-hall entrance) are art-pass defaults. The node type colours are placeholders (O-7).

## Open questions for the user
- Is the round 4 street frame good enough, or do they want one more round? (O-2 chose "move on".)
- Should the traffic streak threshold change? (O-4 left it at 200 px/s.)
- Which LOD sheets to review first? Trees, parks, highway and water are still the r43 look in every band, and blade signs are not built.
