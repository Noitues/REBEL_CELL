# Claude playtest batch PB-PT-003b

4 report(s).

| Tester | Persona | Focus | Outcome | Netruns | Deaths | Raids | Min | Enjoy | RNG | Bugs |
|---|---|---|---|---|---|---|---|---|---|---|
| [ferrite](ferrite.md) | explorer-completionist | raids-cell-defense | INCOMPLETE | 0 | 0 | 0 | 60 | 4 | 3 | 9 |
| [nullpoint](nullpoint.md) | PB-PT-003b | bug hunting and edge cases | INCOMPLETE | 0 | 0 | 0 | 40 | 4 | 3 | 9 |
| [saltlamp](saltlamp.md) | PB-PT-003b | pacing | INCOMPLETE | 0 | 3 | 0 | 40 | 4 | 3 | 5 |
| [tinroof](tinroof.md) | PB-PT-003b | economy and difficulty curve | INCOMPLETE | 0 | 3 | 1 | 40 | 3 | 4 | 4 |

**Averages:** enjoyment 3.8 (n=4) · RNG fairness 3.2 (n=4) (1 fair – 5 cheated) · playtime 45.0 (n=4) min · bugs 6.8 (n=4)
**Outcomes:** INCOMPLETE 4
**Netrun length:** too long 4
**Campaign length:** too long 3, just right 1
**Called overpowered:** Brute Spin ×3, Fine Tune ×2, Nudge Driver ×1, Sanitize ×1, Patch+ ×1, Inner Snap ×1, Jolt ×1
**Called weak:** Jolt ×2, Mirror Flip ×2, Overdrive ×1, Fine Tune ×1

## Combat skill (from the testers' FIGHT lines)

Difficulty signals only count from testers who play well (designer: Perfects on high slices take almost no damage).

| Tester | Tier | Fights | Won | Avg turns | Avg HP lost | Perfects / turn |
|---|---|---|---|---|---|---|
| ferrite | intermediate | 2 | 2 | 10.0 | 3.0 | 0.10 |
| nullpoint | novice | 6 | 6 | 9.2 | 17.5 | 0.00 |
| saltlamp | novice | 11 | 8 | 9.2 | 35.3 | 0.00 |
| tinroof | novice | 6 | 3 | 9.8 | 45.0 | 0.00 |

## Combat skill, ground truth (fights rebuilt from replays)

| tester | turns | perfect_reachable_pct | tester_perfect_pct | tester_perfect_when_reachable_pct | perfect_with_no_action_pct | turns_with_any_action_pct | dealt_tester | dealt_best | taken_tester | taken_best | taken_no_action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PB-PT-003b/ferrite | 20 | 100 | 20 | 20 | 25 | 45 | 4.0 | 17.1 | 3.0 | 0.4 | 2.5 |
| PB-PT-003b/nullpoint | 33 | 91 | 21 | 23 | 15 | 39 | 5.0 | 14.7 | 3.2 | 0.3 | 2.9 |
| PB-PT-003b/saltlamp | 60 | 95 | 17 | 18 | 18 | 47 | 3.2 | 20.1 | 3.8 | 0.9 | 3.8 |
| PB-PT-003b/tinroof | 60 | 95 | 15 | 16 | 13 | 27 | 3.7 | 18.8 | 4.0 | 1.0 | 3.7 |

## Top frustrations

- **ferrite** (explorer-completionist): Undo locked after random spins and aim mode that would not cancel
- **nullpoint** (PB-PT-003b): Never learned what FREE NUDGE or nudge means, and clicks, Esc and UNDO did not respond as expected.
- **saltlamp** (PB-PT-003b): Fights run 10-13 turns of slow wheel resolve, and low HP carries over with no heal until run end.
- **tinroof** (PB-PT-003b): Free nudge and staged-card rules never explained, and UNDO would not cancel a bad staged Jolt

## One change each

- **ferrite** (explorer-completionist): Make cancel and undo reliable and explain the RAM debt on screen
- **nullpoint** (PB-PT-003b): Define nudge and FREE NUDGE in plain words on the combat screen, make Esc cancel a selected card, and fix UNDO.
- **saltlamp** (PB-PT-003b): Shorten fights and the tutorial, add a skip for the wheel animation, and offer a heal mid-run.
- **tinroof** (PB-PT-003b): Explain the free nudge in the tutorial and make staged cards and UNDO clear and cancellable
