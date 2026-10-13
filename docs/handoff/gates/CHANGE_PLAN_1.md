# Change plan 1 — from the 2026-10-12 playtest analysis            main @ b2f8e5c9

**Status: APPROVED basis (CP-003 confirmed by the designer 2026-10-12).** Wave 0 starts on the designer's go; the gate
playtest cost is being reviewed first (designer request), which may change §"Cost" and the gate routine.
Evidence: `docs/playtest/claude/ANALYSIS_2026-10-12.md`; checkpoint `docs/handoff/gates/CP-003.md`.

Standing rules this plan follows:
- CP-002 1: only the approved sets.
- CP-002 5: overkill shows "→ 0".
- CP-002 7: no tick marks or reticles.
- D9: WIP commits.
- D10: main green before a wave.
- D11: one comparison sheet per group.
- D12: agents × model recorded.
- At most 5 agent worktrees at a time.

## Wave 0 — verify before building (no game code)
| # | Item | Who | Output |
|---|---|---|---|
| V1 | **A2 check:** what the live preview already shows after aiming (chips, chained queued actions, kills) at 1.0 / 2.0 | fix-visual, read-only captures | a gap list: what A2 still needs |
| V2 | **B-bug repro:** reproduce B1, B2, B3, B5, B6, B7, B8 and B9 headless or from the testers' saves and replays; record the steps | fix-mechanical | `docs/handoff/plan1/B_REPRO.md` (a bug that won't reproduce is reported, not fixed) |
| V3 | **Genome Core (3A):** a deeper-search state run with 2-turn lookahead in `tools/agent/turn_planner.gd` (~$5) | orchestrator runs `tools/playtest` | numbers for the boss ruling |
| V4 | **Genome Core, human (3A):** one attempt from a strong library save (`tools/playtest/streamline.py`) | designer | a short note |
| V5 | **M0–M4 ticks (8A):** tick the systems criteria with state-sweep / test evidence; hold "readable / learnable" until A+B pass a re-test | fix-mechanical (docs) | MILESTONES ticks |

## Wave 1 — B: flow bugs (one group, one sheet)
| Slice | Items | Area / agent |
|---|---|---|
| B-tutorial | B1 FIGHT WON has no Continue · B6 undo blocked after a random event (the tutorial teaches it as free) | screens + rules / fix-visual |
| B-loot | B2 loot Continue silently blocked by a Firmware that doesn't fit (toast ~0.25 s): say why, keep the choice | screens / fix-visual |
| B-input | B3 an aim that Esc / Z / undo can't clear · B5 Quit ignores input in some states (only those that reproduce) | combat + screens / fix-visual |
| B-city | B7 Map Key opens empty · B8 raid banner stays "RAID IN PROGRESS" after the raid · B9 START unreachable at text 2.0 | city + screens / fix-visual |

Every fix gets a test (rule 6). Then the merge, one group sheet to the art-pass session, then **gate PT-002a**: the
human list for B plus `tools/playtest/gate.py` (9A, ~$50).

## Wave 2 — A: combat legibility (one group, one sheet)
| Slice | Items |
|---|---|
| A1 precision tag | PERFECT / GOOD / WEAK tag on each pointer and in the preview, live as cards and nudges are queued (2A). It reads the same resolver the preview uses, so preview equals result (rule 6). |
| A2 planned outcome | Only V1's gaps: chips show the queued plan's result chained across actions, kills shown "→ 0" (CP-002 5, `combat_scene.gd:3429` / `:4677`). |
| A3 labels + legend | HP / RAM chips, negative "(-N)" RAM, the Null "1/0", OVFL / SHIM / DFRG, the "D 0" badge, all labelled in place; a legend reachable from combat. |
| A4 + 6A card faces | Full card text (no "Blocked while th…"), with direction and tick distance; conditions stated on card and chip faces (Static Coat, Siphon, Ring Tap). Offers unchanged. |
| A5 teach nudges | The tutorial teaches nudge, Free Nudge and Q / E; Q / E get a visible state. |

Then the merge, one sheet, and **gate PT-002**: the human list, `gate.py`, a re-test of A+B by coached screen
testers, and the parity / Perfect probes re-run against the PB-013 / PB-015 baselines. The "readable / learnable"
M0–M4 ticks are decided here (8A).

## Wave 3 — C: city and campaign clarity (after PT-002)
| Item | Note |
|---|---|
| C4 reachable Sites | Which Site is reachable, and why a Site isn't (2.5 h lost across 5 testers) |
| C3 Heat preview | Heat delta before acting; a warning before a threshold |
| C6 crew recovery | What to do when every operative is dead |
| C7 + 7A route map | Prompt, node shapes, all links, **HP recovery and carry-over visible** (7A), then a re-check with coached testers |
| C9 raid setup | Warn when there is 0 crew; one name for the home server |
| F1 / F2 (M14 follow-ups) | CLAIMED stamps never stack; the raid-queued note moves to the foot band. These are art follow-ups but land on the same HQ screens, so they ride here |

Gate PT-003.

## Later (recorded, not planned)
- **D1, boss:** ruled from V3 and V4.
- **D2 / 4A, pacing:** CP-002 ruling 6, after polish.
- **D3 / 5A, Schematics:** re-measured with the v2 HQ agent at the next gate.
- **D5:** depends on 7A's re-check.
- **E, motion:** the animation pass stays paused (D2).
- **Hostile ticks:** removed for good (CP-002 7, long term).
- **Rule-5 sweep:** D14. Rides whichever wave touches the same kit files, or a mechanical slice after PT-002.

## Cost and size (rough)
| Phase | Agents and size | Cost | Gate |
|---|---|---|---|
| Wave 0 | 3 agents + 1 state run | ~$5 API | — |
| Wave 1 | 4 fix-visual | — | PT-002a (~$50) |
| Wave 2 | 5 fix-visual (A1 may need Opus for the resolver hook, stated as OPUS-BECAUSE) | — | PT-002 (~$50 plus re-tests) |
| Wave 3 | 4–5 slices | — | PT-003 |

Three waves and three gates before D is revisited.
