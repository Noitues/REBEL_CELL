# Claude playtest batch PB-SOL-1

5 report(s).

| Tester | Persona | Focus | Outcome | Netruns | Deaths | Raids | Min | Enjoy | RNG | Bugs |
|---|---|---|---|---|---|---|---|---|---|---|
| [cinder_ivy](cinder_ivy.md) | PB-SOL-1 | bug hunting and edge cases | INCOMPLETE | 0 | 0 | 0 | 37 | 3 | 4 | 10 |
| [copperjack](copperjack.md) | PB-SOL-1 | City Grid, HQ and Heat | ABANDONED | 0 | 0 | 0 | 18 | 4 | 4 | 8 |
| [mothball](mothball.md) | PB-SOL-1 | raids | INCOMPLETE | 0 | 4 | 1 | 61 | 3 | 4 | 13 |
| [static_fox](static_fox.md) | min-maxer | pacing | INCOMPLETE | 0 | 3 | 1 | 104 | 3 | 4 | 9 |
| [tinroof](tinroof.md) | PB-SOL-1 | economy-difficulty | INCOMPLETE | 2 | 2 | 0 | 30 | 3 | 4 | 9 |

**Averages:** enjoyment 3.2 (n=5) · RNG fairness 4.0 (n=5) (1 fair – 5 cheated) · playtime 50.0 (n=5) min · bugs 9.8 (n=5)
**Outcomes:** INCOMPLETE 4, ABANDONED 1
**Netrun length:** too long 3, just right 2
**Campaign length:** too long 3, just right 1, too short 1
**Called overpowered:** Jolt ×2, Patch+ ×1, Brute Spin ×1, Flick ×1, Calibrate ×1, Mirror Flip ×1, Firewall ×1
**Called weak:** Jolt ×2, Inner Drift ×1, Respin ×1, Mirror Flip ×1, Fine Tune ×1, Ring Tap ×1, Gear Shift ×1, Overdrive ×1

## Combat skill (from the testers' FIGHT lines)

Difficulty signals only count from testers who play well (designer: Perfects on high slices take almost no damage).

| Tester | Tier | Fights | Won | Avg turns | Avg HP lost | Perfects / turn |
|---|---|---|---|---|---|---|
| cinder_ivy | intermediate | 6 | 6 | 7.3 | 3.0 | 0.02 |
| copperjack | intermediate | 4 | 4 | 5.2 | 39.8 | 0.14 |
| mothball | novice | 7 | 3 | 9.1 | 42.3 | 0.00 |
| static_fox | expert | 10 | 7 | 8.8 | 29.5 | 0.05 |
| tinroof | novice | 9 | 8 | 7.0 | 38.0 | 0.00 |

## Combat skill, ground truth (fights rebuilt from replays)

| tester | turns | perfect_reachable_pct | tester_perfect_pct | tester_perfect_when_reachable_pct | perfect_with_no_action_pct | turns_with_any_action_pct | dealt_tester | dealt_best | taken_tester | taken_best | taken_no_action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PB-SOL-1/cinder_ivy | 20 | 100 | 15 | 15 | 15 | 70 | 6.1 | 17.1 | 4.7 | 0.3 | 4.7 |
| PB-SOL-1/copperjack | 14 | 100 | 57 | 57 | 36 | 71 | 8.7 | 17.3 | 6.4 | 0.7 | 6.4 |
| PB-SOL-1/mothball | 64 | 95 | 17 | 18 | 25 | 55 | 4.2 | 18.0 | 4.5 | 1.5 | 4.0 |
| PB-SOL-1/static_fox | 88 | 98 | 24 | 24 | 17 | 75 | 4.4 | 18.9 | 3.0 | 0.7 | 3.3 |
| PB-SOL-1/tinroof | 34 | 94 | 18 | 19 | 29 | 50 | 6.9 | 17.8 | 4.2 | 0.6 | 4.4 |

## Top frustrations

- **cinder_ivy** (PB-SOL-1): Aim kept snapping to the enemy wheel, Undo said "nothing to undo", and a Respin left me soft-locked at 4 HP.
- **copperjack** (PB-SOL-1): Respin left Undo dead and a LETHAL preview on 5 HP, and quit/continue did not fix it
- **mothball** (PB-SOL-1): Free Nudge and targeting never explained, and raid stationing would not register, so permadeath and raids felt like an unreadable tax
- **static_fox** (min-maxer): Marathon combats (23 turns vs Recall Unit) and forced fights at near-zero HP
- **tinroof** (PB-SOL-1): Could not station Breaker 3 for the first Solace raid; Raid Setup stayed at Stationed 0 and nothing responded.

## One change each

- **cinder_ivy** (PB-SOL-1): Default aim to my own wheel and make Undo reliable, including after a Respin.
- **copperjack** (PB-SOL-1): Let Undo clear staged cards after a Respin, and give a way out when HP is too low
- **mothball** (PB-SOL-1): Explain Free Nudge and card targeting in plain on-screen text and make stationing in raid setup work
- **static_fox** (min-maxer): Add heal/rest options after big HP losses and fix the stuck loot CONTINUE button
- **tinroof** (PB-SOL-1): Explain wheels, RAM and RESPIN in plain words early, make stationing crew in Raid Setup obvious and responsive, and add a heal between fights.
