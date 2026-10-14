# Claude playtest batch PB-PT-003

4 report(s).

| Tester | Persona | Focus | Outcome | Netruns | Deaths | Raids | Min | Enjoy | RNG | Bugs |
|---|---|---|---|---|---|---|---|---|---|---|
| [blue_hour](blue_hour.md) | PB-PT-003 | raids | INCOMPLETE | 7 | 7 | 0 | 40 | 3 | 3 | 5 |
| [byte_rat](byte_rat.md) | PB-PT-003 | onboarding | INCOMPLETE | 0 | 2 | 0 | 40 | 3 | 3 | 4 |
| [nullpoint](nullpoint.md) | PB-PT-003 | pacing | INCOMPLETE | 0 | 3 | 0 | 40 | 3 | 3 | 4 |
| [parallax](parallax.md) | PB-PT-003 | economy-difficulty | INCOMPLETE | 0 | 2 | 1 | 60 | 5 | 3 | 7 |

**Averages:** enjoyment 3.5 (n=4) · RNG fairness 3.0 (n=4) (1 fair – 5 cheated) · playtime 45.0 (n=4) min · bugs 5.0 (n=4)
**Outcomes:** INCOMPLETE 4
**Netrun length:** too long 3, too short 1
**Campaign length:** too long 4
**Called overpowered:** Jolt ×2, Nudge Driver ×2, Fine Tune ×1, Patch Up ×1, Mirror Flip ×1, Patch+ ×1
**Called weak:** Overdrive ×1, Gear Shift ×1, Ring Tap ×1, Inner Snap ×1, Sanitize ×1, Reroll ×1, Inner Drift ×1

## Combat skill (from the testers' FIGHT lines)

Difficulty signals only count from testers who play well (designer: Perfects on high slices take almost no damage).

| Tester | Tier | Fights | Won | Avg turns | Avg HP lost | Perfects / turn |
|---|---|---|---|---|---|---|
| blue_hour | novice | 14 | 9 | 9.0 | 44.6 | 0.00 |
| byte_rat | novice | 4 | 2 | 10.5 | 31.5 | 0.02 |
| nullpoint | novice | 9 | 7 | 9.4 | 34.0 | 0.05 |
| parallax | intermediate | 9 | 6 | 6.8 | 28.9 | 0.05 |

## Combat skill, ground truth (fights rebuilt from replays)

| tester | turns | perfect_reachable_pct | tester_perfect_pct | tester_perfect_when_reachable_pct | perfect_with_no_action_pct | turns_with_any_action_pct | dealt_tester | dealt_best | taken_tester | taken_best | taken_no_action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PB-PT-003/blue_hour | 98 | 94 | 16 | 17 | 21 | 16 | 4.2 | 16.6 | 3.5 | 0.7 | 3.5 |
| PB-PT-003/byte_rat | 42 | 95 | 21 | 22 | 12 | 55 | 3.4 | 14.5 | 2.9 | 0.7 | 3.2 |
| PB-PT-003/nullpoint | 64 | 100 | 28 | 28 | 25 | 38 | 4.0 | 21.9 | 3.8 | 1.0 | 4.2 |
| PB-PT-003/parallax | 54 | 96 | 24 | 25 | 15 | 46 | 7.0 | 21.4 | 3.9 | 0.8 | 4.3 |

## Top frustrations

- **blue_hour** (PB-PT-003): Both Breakers died and the map said recruit at HQ but showed no way to get there.
- **byte_rat** (PB-PT-003): GOOD/NULL and wheel aiming never explained, and no way found to reach HQ after both operatives died
- **nullpoint** (PB-PT-003): 16-turn fights where the wheels were unreadable and damage barely moved
- **parallax** (PB-PT-003): No healing between forced Rack and Elite fights at 16 HP, plus the Undo lock after a random pick

## One change each

- **blue_hour** (PB-PT-003): Add a clear HQ route and a permadeath warning, and shorten fights.
- **byte_rat** (PB-PT-003): Explain GOOD/NULL/WEAK/PERFECT/chips in the tutorial and mark HQ and Site links on the map
- **nullpoint** (PB-PT-003): Explain free nudges and damage in the tutorial and shorten fights
- **parallax** (PB-PT-003): Add a heal node before the Rack and Elite, and make the Undo-lock reason more visible
