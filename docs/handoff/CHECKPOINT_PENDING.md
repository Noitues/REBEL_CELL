# Checkpoint queue

Pending: **CP-002** (below), shipped with PT-001 at the M14 gate (2026-10-12). Add items as they come up (template
`docs/process/templates/CHECKPOINT.md`); BLOCKING questions go to chat at once, not here.

# CP-002 — M14 completion gate (PT-001)            2026-10-12 · main @ 4780b5c0

Answer as a numbered list (`1A 2C 3: free text`). Unanswered items keep their default.
Report: `docs/handoff/gates/PT-001.md`. Playtest: `docs/playtest/PT-001_m14-close-out-group-2.md`.

## Questions (GATE class)
Full replan: `docs/handoff/gates/M14_REPLAN.md`. Retrospective: `docs/handoff/gates/M14_RETROSPECTIVE.md`.

### 1. What starts after M14
Context: M14 is complete and work is paused. Remaining: about 30–45 waves and 12–18 gates (replan §4).
- **A (recommended)**: replan order: wave 1 = R7 re-audit + housekeeping + sim baseline, with your G1–G16 ruling
  session in parallel; then R7 A–E with F1 / F2 (4–5 waves, gate PT-002); H25; balance; G-passes; daily modifiers last.
- B: gameplay first: G rulings and G-passes, R7 and H25 once at the end (replan §5 alt B).
- C: ship scope: R7, H25 and the Queued passes only, plus small G items (replan §5 alt C).
- D: wait.
Default if unanswered: D (nothing starts without you). Blocks: all post-M14 work.

### 2. How R7 closes
- **A (recommended)**: H25 is R7's closing audit loop (saves a separate audit wave).
- B: a separate R7 audit loop, then H25.
Default: A. Blocks: nothing until R7 ends.

### 3. M0–M4 acceptance boxes (33 never ticked)
Context: replan §2: 29 done (named tests), 2 superseded, 1 partial (Firmware / Daemon per-id coverage), 1 open (netrun minutes).
- **A (recommended)**: tick the 29 with evidence, reword Pierce / WEAK / DOWN-TAKEN, mark the 2 superseded, add a per-id
  Firmware / Daemon coverage test.
- B: leave them.
Default: B. Blocks: nothing.

### 4. M2 "tier 1 netrun takes 12–18 min"
- **A (recommended)**: a timed step in the next PT list (you time one run).
- B: drop it in favour of the simulator's run counts.
Default: A. Blocks: nothing.

### 5. Overkill wording (ruling 9; "→ N LEFT" still live, combat_scene.gd:3429 / :4677)
- **A (recommended)**: "→ 0 HP" plus a skull on a kill (R7 A5).
- B: keep "→ N LEFT".
Default: A. Blocks: R7 batch A.

### 6. Pacing (last sim: ~43–49 runs at ICE 5 vs the 24-run target)
- **A (recommended)**: sim baseline now (wave 1), tuned in the balance pass.
- B: wait until the G-passes are done.
Default: A. Blocks: the balance pass.

### 7. Raid hostile cue without colour
Context: it shows only with the colour-blind setting on; ART_BIBLE §5.1 says never colour alone.
- **A (recommended)**: always shown.
- B: only with the colour-blind setting.
Default: A. Blocks: nothing (rides R7 batch C).

## Defaults taken (FYI class; veto by number, otherwise they stand)
- D6. `tools/precommit.sh` re-imports when the staged diff adds or renames a `class_name` (a stale class cache failed one merge run) — gate report PT-001 §2.
- D7. Brief footer adds "stop your own background runs before the RESULT block; one precommit at a time" — gate report PT-001 §2.
- D8. `run_tests.py` uses a fresh shard directory per invocation (overlapping runs collided) — gate report PT-001 §2.
- D9. Agents commit WIP on their own branch at least every ~30 min and before long runs (three losses of uncommitted work in M14) — `docs/handoff/gates/M14_RETROSPECTIVE.md` §5.
- D10. Fast tier on main must be green before a wave is spawned; reds fixed first — M14 retrospective §5.
- D11. One comparison sheet per group is the only review unit for every art pass, incl. R7 — M14 retrospective §5.
- D12. Gate reports record agents × model × effort; more than 5 agents at once or any Opus agent needs a stated reason in the brief — M14 retrospective §5.
- D13. G10 (raid zoom, built as `RaidZoomFit`) and G13 (HQ actions, answered by HQ direction B) close as done; G16 keeps only its per-card type field — replan §3.
- D14. A mechanical rule-5 slice moves the ~190 literals the cleanup listed (absolute px in ~15 kit files) into consts / config, in R7 wave 1 — replan §3.

## Already ruled, not re-asked (for reference)
- This PC is the target PC; tier 1 here is the Deck tier → DECISIONS "M14 gate (PT-001)" (2026-10-12).
- Group 2 look → art-pass session APPROVED (R1–R3 + polish), DECISIONS "M14 G2R*" / "G2 polish" (2026-10-12).

## Answered
- **CP-001** (2026-10-10 → answered 2026-10-11): 1A rule 6 scoped to rule-bearing code; 2A full suite once per
  gate, **never ×3**; 3A Batch API lane in use (key still to be set by the designer); 4A playtest gates per
  group. Logged: DECISIONS "2026-10-11 — Designer rulings CP-001"; CLAUDE.md rule 6 and "Commands" updated.
  Defaults D1–D5 stood unvetoed.

## Items queued for CP-002
- none open. Settled by the art director (2026-10-11, close-out group review), reported to the designer as
  "settled unless you object": Mainframe pegboard at 0.86 at text 2.0 (art, not text: the text floor does not apply);
  corp letterheads use a short `letterhead_name` per corp instead of an ellipsis (M14 FOLLOW-UP slice).
