# Claude playtest batch PB-PT-002

4 report(s).

| Tester | Persona | Focus | Outcome | Netruns | Deaths | Raids | Min | Enjoy | RNG | Bugs |
|---|---|---|---|---|---|---|---|---|---|---|
| [neon_moth](neon_moth.md) | PB-PT-002 | economy_difficulty_curve | INCOMPLETE | 0 | 4 | 2 | 60 | 4 | 3 | 9 |
| [openloop](openloop.md) | PB-PT-002 | menus_navigation_information | ABANDONED | 0 | 4 | 1 | 30 | 2 | 3 | 5 |
| [parallax](parallax.md) | PB-PT-002 | first-hour-onboarding | INCOMPLETE | 0 | 3 | 0 | 60 | 3 | 4 | 9 |
| [saltlamp](saltlamp.md) | PB-PT-002 | City Grid, HQ and Heat | INCOMPLETE | 2 | 0 | 0 | 40 | 3 | 3 | 5 |

**Averages:** enjoyment 3.0 (n=4) · RNG fairness 3.2 (n=4) (1 fair – 5 cheated) · playtime 47.5 (n=4) min · bugs 7.0 (n=4)
**Outcomes:** INCOMPLETE 3, ABANDONED 1
**Netrun length:** too long 3, just right 1
**Campaign length:** too long 3, not encountered 1
**Called overpowered:** Firewall ×2, Patch+ ×2, Nudge Driver ×2, Jolt ×1, Mirror Flip ×1, Sanitize ×1
**Called weak:** Fine Tune ×3, Overdrive ×2, Jolt ×1, Mirror Flip ×1, Gear Shift ×1, Freeze ×1, Brute Spin ×1

## Combat skill (from the testers' FIGHT lines)

Difficulty signals only count from testers who play well (designer: Perfects on high slices take almost no damage).

| Tester | Tier | Fights | Won | Avg turns | Avg HP lost | Perfects / turn |
|---|---|---|---|---|---|---|
| neon_moth | intermediate | 11 | 7 | 9.0 | 27.0 | 0.00 |
| openloop | novice | 9 | 6 | 10.9 | 35.3 | 0.03 |
| parallax | intermediate | 6 | 5 | 7.5 | 20.0 | 0.11 |
| saltlamp | novice | 5 | 5 | 6.0 | 14.0 | 0.07 |

## Combat skill, ground truth (fights rebuilt from replays)

| tester | turns | perfect_reachable_pct | tester_perfect_pct | tester_perfect_when_reachable_pct | perfect_with_no_action_pct | turns_with_any_action_pct | dealt_tester | dealt_best | taken_tester | taken_best | taken_no_action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PB-PT-002/neon_moth | 99 | 96 | 21 | 21 | 18 | 43 | 4.1 | 18.4 | 2.9 | 0.5 | 2.9 |
| PB-PT-002/openloop | 76 | 96 | 28 | 29 | 26 | 22 | 3.8 | 17.6 | 3.3 | 0.5 | 3.6 |
| PB-PT-002/parallax | 47 | 98 | 30 | 30 | 21 | 38 | 5.8 | 20.3 | 3.8 | 0.9 | 4.1 |
| PB-PT-002/saltlamp | 13 | 100 | 15 | 15 | 23 | 46 | 6.2 | 18.2 | 3.6 | 0.0 | 4.8 |

## Top frustrations

- **neon_moth** (PB-PT-002): Aiming needs a mouse and the arc gets stuck; forced low-HP elites after each flatline.
- **openloop** (PB-PT-002): Wiped roster and no visible way to recruit or rest at HQ; a dead end.
- **parallax** (PB-PT-002): Card aim stuck for ~30 minutes on a lethal Rack turn with UNDO blocked and no keyboard way to cancel
- **saltlamp** (PB-PT-002): Free nudge aiming was never explained, and the Turn 4 nudge could not be aimed or undone.

## One change each

- **neon_moth** (PB-PT-002): Add keys for aim and cancel, and show key hints on every button.
- **openloop** (PB-PT-002): Add an obvious Rest/Recruit action to HQ and warn about permadeath and an empty roster.
- **parallax** (PB-PT-002): Show a key hint on every button and add a visible aim-cancel key, with a clear on-screen reason when UNDO is blocked
- **saltlamp** (PB-PT-002): Explain the aim arrow, nudge cost, cancel key and threat tags on screen, and name the random event that blocks UNDO.
