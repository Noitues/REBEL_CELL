# Claude playtest batch PB-010

8 report(s).

| Tester | Persona | Focus | Outcome | Netruns | Deaths | Raids | Min | Enjoy | RNG | Bugs |
|---|---|---|---|---|---|---|---|---|---|---|
| [byte_rat](byte_rat.md) | PB-010 | animation_feel | INCOMPLETE | 0 | 4 | 2 | 60 | 5 | n/a | 10 |
| [copperjack](copperjack.md) | PB-010 | cards-firmware-daemons | INCOMPLETE | 5 | 5 | 0 | 97 | 3 | 3 | 8 |
| [ferrite](ferrite.md) | PB-010 | menus-navigation-information | INCOMPLETE | 0 | 1 | 0 | 60 | 3 | 3 | 9 |
| [gridlock](gridlock.md) | PB-010 | City Grid, HQ and Heat | INCOMPLETE | 0 | 3 | 0 | 60 | 3 | 4 | 7 |
| [halfmoon](halfmoon.md) | PB-010 | first-hour-onboarding | LOST | 0 | 6 | 2 | 78 | 3 | 3 | 10 |
| [neon_moth](neon_moth.md) | PB-010 | economy_difficulty_curve | INCOMPLETE | 0 | 2 | 0 | 60 | 4 | 3 | 9 |
| [quietcarrier](quietcarrier.md) | PB-010 | pacing | INCOMPLETE | 0 | 5 | 2 | 95 | 4 | 3 | 9 |
| [rustbelt](rustbelt.md) | PB-010 | readability-accessibility | INCOMPLETE | 0 | 0 | 0 | 151 | 2 | 1 | 7 |

**Averages:** enjoyment 3.4 (n=8) · RNG fairness 2.9 (n=7) (1 fair – 5 cheated) · playtime 82.6 (n=8) min · bugs 8.6 (n=8)
**Outcomes:** INCOMPLETE 7, LOST 1
**Netrun length:** just right 4, too long 3, too short 1
**Campaign length:** too long 6, just right 2
**Called overpowered:** Firewall ×1, Patch+ ×1
**Called weak:** Static Coat ×2, Mirror Flip ×2, Ring Tap ×1, Siphon ×1, Overdrive ×1, Sanitize ×1, Fine Tune ×1

## Combat skill (from the testers' FIGHT lines)

Difficulty signals only count from testers who play well (designer: Perfects on high slices take almost no damage).

| Tester | Tier | Fights | Won | Avg turns | Avg HP lost | Perfects / turn |
|---|---|---|---|---|---|---|
| byte_rat | intermediate | 0 | — | — | — | — |
| copperjack | intermediate | 0 | — | — | — | — |
| ferrite | novice | 0 | — | — | — | — |
| gridlock | novice | 0 | — | — | — | — |
| halfmoon | intermediate | 0 | — | — | — | — |
| neon_moth | novice | 0 | — | — | — | — |
| quietcarrier | intermediate | 0 | — | — | — | — |
| rustbelt | expert | 0 | — | — | — | — |

(No FIGHT lines yet: testers from before 2026-10-12 evening did not log them.)

## Top frustrations

- **byte_rat** (PB-010): Card aiming got stuck and cards or nudges showed no visible effect, so I couldn't see cause and effect.
- **copperjack** (PB-010): Hunting for the jackable site on the grid, and nudge buttons silently doing nothing without nudge cards
- **ferrite** (PB-010): Core terms (nudge, RAM, negative RAM, ticks) never defined in the tutorial or Codex, plus the tutorial result screen dead end
- **gridlock** (PB-010): Heat and Site locks unreadable on the grid, and the quit flow never worked
- **halfmoon** (PB-010): Wheel aim ignored clicks and had no keyboard step, so I died in fights I could have won.
- **neon_moth** (PB-010): Locked map nodes gave no feedback, so I lost most of the hour clicking them, and the tutorial never explained SEND IT.
- **quietcarrier** (PB-010): Fights of 10-30 turns against resistance enemies, plus ~25 min lost hunting for a reachable site on the HQ map
- **rustbelt** (PB-010): Could not find START on the New Campaign setup at 2.0x text; scrolling kept overshooting

## One change each

- **byte_rat** (PB-010): Add bold hit feedback on resolve and a visible card-to-slot animation.
- **copperjack** (PB-010): Explain nudge buttons on screen and clearly mark the starter site on the City Grid
- **ferrite** (PB-010): Add a how-to-play page and a Codex search, and put a visible Continue button on the tutorial result screen
- **gridlock** (PB-010): Show Heat deltas on actions and Sites, label grid nodes and locks, fix Quit
- **halfmoon** (PB-010): Show key hints on every button, add keyboard wheel targeting, and label the HP/RAM chips.
- **neon_moth** (PB-010): Show the lock reason on the node itself and draw the gate links on the map.
- **quietcarrier** (PB-010): Make reachable sites obvious on the HQ map and shorten or unblock resistance-heavy fights
- **rustbelt** (PB-010): Pin START as a fixed control and make scrolling predictable at large text scales
