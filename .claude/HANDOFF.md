# Handoff: REBEL_CELL art-pass (single art interface)

| | |
|---|---|
| Written | 2026-10-22, late evening |
| Branch / commit | `art-pass` in the worktree `D:/rc_art/art-pass` (see `git log -1`). |
| Main | `D:/Godot/rebel_cell` main @ 505d4152, which includes A-099. It is read-only for art-pass. |
| State | Two sessions are working: the toolbox (module 19) and Solace (garden concepts). Nothing waits on the designer. |

## Role (keep these)
- Art-pass is the **only** session the designer talks to for visual work. It:
  - reviews every sheet from the look-toolbox and Solace against the golden plate, ART_BIBLE §1.2 and a squint test;
  - puts design picks to the designer with AskUserQuestion, recommendation first;
  - logs rulings in `docs/concepts/DIRECTION_REVIEW.md` and relays them back;
  - posts, numbers and prunes the A entries in `docs/concepts/HANDOFF_PACKAGE/MAILBOX.md`. Only art-pass numbers and prunes.
- Art calls (readability, bible rules, the order of work) art-pass rules on itself and logs.
- Hard rules:
  - Never write in `D:/Godot/rebel_cell`.
  - Never run `python -`.
  - Never `taskkill /IM`, and never touch the designer's Blender or its MCP.
  - Use the D: drive only.
  - No game design in art-pass.
  - Commit by explicit paths, with the Opus trailer. Never commit .uid, scratch or GPU_DONE files.
  - Redirect Godot output, never pipe it.
  - Build does all merges.
- Build's replies are in main `docs/handoff/netrun_art/MAILBOX_TO_ART.md`. Read it with `git -C D:/Godot/rebel_cell show
  main:docs/handoff/netrun_art/MAILBOX_TO_ART.md > D:/rc_scratch/review/mb_to_art.md`. Last read: **B-078**.
- Prune merged entries with `python D:/rc_scratch/review/prune.py <MAILBOX.md> A-NNN B-old B-new`.
- Raid reviews are **paused** for the raid redesign (A-088), and the mailbox cron is stopped. Restart both only when build says the
  redesign has landed. No raid-zoom renders until then.

## Mailbox state
- **Open READY entries:**
  - A-098: car-light slot fix, art/look-toolbox-7 @ 3ad4043a. Not merged yet; no pixel change.
  - A-099: nodes. **Merged as main 505d4152**, so prune it next time; build's B entry is to come.
- **Next free number: A-100.**
- Older ACK / FYI entries (A-044..A-068, A-080, A-083, A-085, A-088) remain. Prune them as build closes them.

## Sessions managed (all report to art-pass)
| Session | Id | Folder / branch | State | Next |
|---|---|---|---|---|
| Look-toolbox library | local_59edc93f-f0e0-43fb-8a07-aa94f76898ce | D:/rc_art/godot_look_toolbox_5 (+ D:/rc_art/godot_look) / art/look-toolbox-8 @ 177cf088 | Working on module 19 | See "Toolbox" below |
| Solace visual list | local_92774ce2-f55e-46ef-9a1e-b7bf80d81f52 | D:/rc_art/godot_look_hqport, art-pass for sheets | Garden concept round running | See "Solace" below |
| Toolbox module 13, vinyl (lab only) | local_fa015c16-d915-4677-8036-3b24f98c2145 | godot_look/.claude/worktrees/look-m13-vinyl-3bea20 | Idle; rulings applied ("\\" band on both families, card seam to kit) | Lab only on raid screens until the redesign lands |
| Toolbox module 14, CRT (lab only) | local_bb06fec7-aab4-425a-ac00-eb0946cab754 | .../look-m14-crt-8c2d79 | Idle; KEEP_STATIC ruled | Same |
| Toolbox module 16, binary bits (lab only) | local_59d9417f-9ef1-48aa-b05a-b7d5a22eee00 | .../look-m16-bits-6fad31 | Idle; bits rulings applied | Same |
| Toolbox grease-pencil polish | local_7ce28862-4a22-41fd-84e9-dcd4651418a2 | .../gifted-yonath-0c2f42 | Idle since 2026-10-22 morning | The toolbox owns it; ask the toolbox before reusing it |
| Toolbox decrypted holo (THREAT INTEL) | local_247ffb72-43e4-46f5-919e-ebda3871bebb | .../goofy-lalande-0a48b3 | Idle | Same |
| L2 Godot-reachable twin | local_c5bfd172-9efd-4fd2-bcb0-5726fb78fb7b | C: worktree loving-rhodes-0be732 | Done (2026-10-20) | Archive on the designer's yes |
| First HQ parity sheet (Meridian) | local_745f968c-1ab6-4ed9-b91c-499407a39d82 | C: worktree determined-goodall-5b942e | Done | Archive on the designer's yes |
| horizon_break never lowers | local_71a1a7f4-d984-4f60-8948-52b6841bdd62 | art-pass | Done (A-067 merged) | Archive on the designer's yes |
| Art-deco / Graffiti concept renders | local_05591f85-5e7e-43e0-afd9-52dcaa9aef41 / local_d16966a0-0a8f-4f92-a79b-55ed0b87af39 | art-pass | Idle style studies | Archive on the designer's yes |

Not managed by art-pass, for reference only:
- the build session "Resume per HANDOFF.md" (local_aa799908-e44d-4a41-b49f-2f1c55e227c9, D:/Godot/rebel_cell);
- its "Raid design lab" (local_05b0606e-cf14-4893-86ac-ea102b70d3b5), which owns the raid redesign.

### Toolbox: module 19, street detail density, on art/look-toolbox-8
The street matched the golden plate's camera, but lacked the plate's small bright points. Ruled by art-pass and the designer
(DIRECTION_REVIEW 2026-10-22):

| Step | State | What |
|---|---|---|
| (d) | done, b2ae906d | The outer land is id class 7, counted as background. |
| (c) | closed as a finding | The designer said **keep the sky**: no infill blocks. |
| (a) | done, 314a783b | Clustered hot windows (b55w7) and r2 face washes. |
| (b) | in progress, 177cf088 | Wet reflections. |
| (e) | approved, not started | Denser frontage signs and edges. |

Owed in (a) and (b):
- **(a) fix:** no face wash on a block next to a route column. On decision seed 2, the VOLTA neighbour became a flat pink column.
- **(b) scope:** street-only `look.post` wet_refl overrides applied by route_rig, with no city_post code change. I lifted the
  city_post hold only that far. Judge the city cars' light brightness against the plate's trails here too.
- **Live stomp fix:** in live play, `CityViewMotion.set_night_share` rewrites whole_building, which drops the street's overrides.
  route_rig must re-apply them after every night_share and look change. This must be proved by an **unfrozen** live test.
- **(e) scope:** denser frontage signs and edges via the r2 rules, updating both twins and the art-pass oracle fixtures.

Gates and what follows:
- Each step is judged per band (facades and floor, not frame totals), on R-DET-2 toward the plate (facades 1421, floor 4–6k),
  over_085, R-HUE-1 ≥ 3.8 and the lit-blocks squint read. Non-street frames must stay max 0.
- Then -8 comes to art-pass for **one** READY (A-100 or the next free number).
- After that: module 18 (perf), measured on the final street.

### Solace: the visual list
- Done today:
  - the Bloom port (A-096, merged);
  - REST / WORKSHOP / CACHE (A-099, merged);
  - the district S4 re-shoot (accepted, no branch).
- Owed: one hospital frame from the game path, the shifted Site point.
- **Now:** the culture garden EX-11 concept round. The brief is `D:/rc_scratch/solace_v1/BRIEF_garden.md`, approved with 5 additions:
  - route and door readability over the building;
  - Solace green and cream, with lime kept apart from the helix green and plum Bloom, and no red cross;
  - the HQ in the map frame;
  - a stacking note per direction;
  - Cycles only where needed.
- Directions: A "Glass ward", B "Culture stack", C "Hanging mountain".
- Frames: the map / HQ view, the street plaza with the Bloom CREEPING, and an inside cutaway with the Bloom CATCHING. No raid zoom.
- **Next designer touch:** the garden direction pick. Review the sheet first, then AskUserQuestion with a recommendation.
- Deferred: the district raid-zoom re-shoot (when the raid redesign lands); key_intel and key_breach stay placeholders (B-061).

## Rulings logged today (DIRECTION_REVIEW, 2026-10-22)
- Bloom reach in layers.
- Street slab: concrete lift, and the deck hidden in the street view.
- Car lights: the slot fix only, judged in 19.
- The street gap is detail density, not exposure.
- Skyline: keep the sky.
- Module 19 (a)/(b) fence and the live stomp.
- Nodes: C icons, A pages, the CACHE header; CACHE #D22C40 with tritan 9 vs ELITE glow accepted; no RUN column; event-level backdrop;
  no plan arrows.
- Archived sheets are under `docs/concepts/look_parity/{a093,slab,gap}`.

## How to resume
1. Read this file and the tail of DIRECTION_REVIEW.md.
2. Read build's mailbox (above). Prune A-099 (and A-098 when it merges); bump "last read".
3. `ListAgents`, or list_sessions with linked = true, and check whether the toolbox or Solace has sent a sheet. Review it against
   the plate with a squint crop (`D:/rc_scratch/review/crop_*.py` pattern) before any reply.

## Recreate the sessions (new art-pass session)
Start a new session in `D:/rc_art/art-pass` with: "Resume art-pass per .claude/HANDOFF.md". Then:

1. **Check what's still alive.** Run list_sessions with linked = true, then `ListAgents`. If the toolbox
   (local_59edc93f…) or Solace (local_92774ce2…) still exists and is idle, **message it instead of re-spawning it**, so its
   context is kept.
2. **If one is gone,** re-spawn it with `start_session` (initiation "user_asked" once the designer says to resume; context "fresh";
   no worktree, because each owns its folder). Use the briefs below. Each brief points at that session's own handoff, which holds
   the detail.
3. **Toolbox sub-sessions** (m13 vinyl, m14 CRT, m16 bits, grease pencil, decrypted holo) are the toolbox's to re-spawn, from its
   handoff, and only when the work needs them. All are lab-only or finished today. Don't re-spawn them from art-pass directly.
4. **Finished sessions** (L2 twin, first HQ parity, horizon_break, the deco / graffiti studies) need no re-spawn.

### Brief: look-toolbox
> You are the LOOK-TOOLBOX session for REBEL_CELL. You work in `D:/rc_art/godot_look_toolbox_5` (plus `D:/rc_art/godot_look`), on
> the art/look-toolbox-* branches.
>
> First read `.claude/HANDOFF_TOOLBOX.md` in that worktree, then CLAUDE.md, ART_BIBLE §1.2 and the tail of art-pass
> `docs/concepts/DIRECTION_REVIEW.md`.
>
> - You report only to art-pass (the session in D:/rc_art/art-pass). Every sheet, question and design pick goes to art-pass, never
>   to the designer. Warn art-pass before any permission prompt.
> - Proof standard:
>   - frozen captures with `--reduce-effects=1`;
>   - plate | now | after sheets with squint rows (1/8 scale plus blur) and per-band tables;
>   - max 0 on frames you didn't mean to change;
>   - targeted tests only (build runs the full gate).
> - Hard rules:
>   - Never write in D:/Godot/rebel_cell.
>   - Never `python -`.
>   - Never `taskkill /IM`, and never touch the designer's Blender.
>   - D: drive only.
>   - Redirect Godot output, never pipe it.
>   - Commit by explicit paths with "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>".
>   - Never commit .uid or scratch files.
>   - Don't move a branch head that art-pass has posted READY; stack new work on a new branch.
> - Art-pass assigns all mailbox numbers.
> - Resume where the handoff says: module 19, then module 18 (perf).

### Brief: Solace visual list
> You are the Solace visual-list session for REBEL_CELL. You work in `D:/rc_art/godot_look_hqport` (Godot) and
> `D:/rc_art/art-pass` (sheets, under docs/concepts/solace_vertical/).
>
> First read `D:/rc_art/art-pass/.claude/HANDOFF_SOLACE.md`, then CLAUDE.md, ART_BIBLE §1.2 and the tail of art-pass
> `docs/concepts/DIRECTION_REVIEW.md`.
>
> - You report only to art-pass. Every sheet and design pick goes to art-pass, never to the designer.
> - Concept agents research real-world refs first and cite them in NOTES.md.
> - Every review needs plate | now plus squint rows.
> - Raid screens are paused: no raid-zoom renders.
> - Hard rules: the same as the toolbox. Don't post READY before art-pass approves; art-pass assigns the A numbers and does all
>   pruning.
> - Resume where the handoff says: the culture garden EX-11, waiting for the designer's direction pick through art-pass, then the
>   Godot implementation.
