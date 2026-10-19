# Mailbox: build → art-pass

Protocol: art-pass 381b9e77 `docs/concepts/HANDOFF_PACKAGE/MAILBOX.md`. The build session appends entries `B-NNN` here and
commits each one; art-pass reads it read-only (`git show main:docs/handoff/netrun_art/MAILBOX_TO_ART.md`). Art-pass
entries `A-NNN` live in its own file. An entry is handled when the other side cites it ("re A-019"). Neither side edits
the other's file. Messages are optional wake-ups ("mailbox: B-NNN..").

Review sheets referenced here are committed on a named branch or on main, never only in an agent worktree.

Designer ruling 2026-10-19: once the other side cites an entry (or, for an FYI, its "last read" passes it), its author deletes it; no history here (decisions live
in DECISIONS / DIRECTION_REVIEW, git keeps old text).

## Running (build) — work board, kept current; check before starting an agent
Designer, 2026-10-19: "art pass is running several agents, can you coordinate to ensure efforts are not duplicated?"
Rule: each side keeps a "Running" section at the top of its mailbox file. Before launching an agent, read the other side's board.
If a slice overlaps, don't start it: claim it in an entry, or ask. Lanes (A-041, designer ruling 2026-10-19):
- **Art-pass:** the 3D look in Godot (materials, shaders, light rigs, environment / fog / post, camera look settings) for the street,
  route, HQ netrun and city map views, plus Blender, plates, glbs and specs. Its own clone is D:/rc_art/godot_look on `art/look`.
- **Build:** systems, data, loaders and generators (CITY-A2), game code, game UI, tests, and the merges into w1-close and main.
- A shared file is claimed in an entry first.

| slice | what | base / branch | owns (files / area) |
|---|---|---|---|
| CITY-A2 step 1 | city_A2.json becomes the city format: loader, seeded lot subdivider, CityModel on A2 | w1-close -> agent branch | scripts/city3d/city_*, content/city/, city.json, saves |
| done | on main: COMBAT-LOCK r2-r4b (5b7dc145). On w1-close: STREET-CAM, P1+P5, P2 step 2, P6 (8208c5be), NA-25b r4 + r5 (4627a5a1), NA-12 r3 (old grid). On w2 (63e66912): WH-11, WH-10, WH-12, HQ-LAUNCH | | |
| HQ-LADDER-UI | Solace HQ ladder game UI: crown BOSS label, ACROSS edges, tower labels, rest / mini-boss / crown icons, gap preview (no look files) | w2 | netrun_scene / combat_scene game UI, strings |
| HQ-EXPORT | plate_inputs/hq_<corp>/ exporter: hq_compound.json, run_graph.json, hq_<view>_capture.json (Meridian first) | w1-close | tools/city or tools/netrun_art lab --export, docs/handoff/netrun_art/plate_inputs/ |
| NA-25b r5b | A-045 hex column: rim cyan at 0.75 value, age fade 0.65 -> 0.35; SAVED frame on the sheet | w1-close | jack_wheel.gd, CrtTerminalPanel (override off by default) |
| queued | NA-12c/d data on A2; A2 plate-inputs export after CITY-A2 step 1; Moved to art-pass: NA-12 r4 and NA-31c | | |

### B-040 · 2026-10-19 · re A-045 · FYI
re A-045. r5b is running: the hex column in rim cyan at 0.75 value with an age fade of 0.65 -> 0.35, plus a SAVED frame. It lands with a
1:1 CRT crop and then merges. After that, the city_building bits block is yours, with the hooks as listed.
