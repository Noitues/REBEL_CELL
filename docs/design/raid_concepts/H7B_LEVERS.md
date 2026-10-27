# H7b: levers that keep raid cadence 3 and bring Solace's skilled loss back into 0.08-0.15

Designer ruling 2026-10-26: cadence stays at every 3 netruns. With R-L (a sentry shields its Site for the rest of the raid) the
skilled loss is 0.050. Oracle only (`tools/raid_concepts/sweep_g1.py`, variants `H7B:KEY=VAL;KEY=VAL`); nothing in `scripts/`, `content/`
or the golden changed. Same runs as the H6/H7 table: 200 campaigns per claim policy (greedy / keys / random), 600 pooled per cell.
G = skilled (greedy planner), N = careless (naive placement). H4..H7 reproduce byte for byte (checked on 6 seeds x 3 policies x
2 players per variant).

## Levers (keys in `sweep_g1.py`, all off by default)
- a. `SHIELD_BEAMS=n`: a block shields the Site for the next n beams only (0 = the rest of the raid, as H7).
- b. `SHIELD_HEAT=n`: +n Heat per sentry whose block shielded a live Site. `SHIELD_WEAR=1`: a shielded OK Site ends the raid DOWN.
  `SHIELD_WEAR=2`: the sentry card that shielded sits out the next hand.
- c. `SEALED3_HEAT=50`: from Heat 50 the third candidate beam fires too (the extra sealed beam is the candidate that is neither A
  nor B). `BEAM_HEAT=a+b`: lower thresholds for the extra known beams (H7: 75+100).
- d. `HUNTER=1`: the hunter beam ignores shields. `HUNTER=2`: it also hits twice (OK to TAKEN).
- e. `DECAY_FAST=1`: when a raid closes, every DOWN Site with no sentry on it goes TAKEN at once (no repair window).
- f. `RETAKE_HEAT=n`: +n Heat per retake. `RETAKE_CD=1`: a retaken Site is live again one netrun later.
- g. `MAX_PLACED=1`: one sentry per raid.

## Targets (all at once)
G loss 0.08-0.15; N loss >= 0.6; response_decides (G) >= 0.44; locked (G) <= 0.45; live owned Sites (G) >= 3;
raids per netrun about 0.39. The last column counts how many of the six hold.

## Table (G = skilled, N = careless; decides, locked, HOME hit, live Sites, raids/netrun are G)
| Variant (H7 at cadence 3 plus) | Loss G | Loss N | Win G / N | Decides G | Locked G | HOME hit G | Live Sites G | Raids/netrun G | Targets met |
|---|---|---|---|---|---|---|---|---|---|
| H7 at cadence 2 (reference) | 0.113 | 0.702 | 0.642 / 0.298 | 0.466 | 0.373 | 0.082 | 4.75 | 0.538 | 5/6 |
| none (H7 at cadence 3) | 0.050 | 0.623 | 0.688 / 0.375 | 0.440 | 0.393 | 0.054 | 5.16 | 0.388 | 5/6 |
| DECAY_FAST=1 | 0.065 | 0.742 | 0.590 / 0.257 | 0.485 | 0.409 | 0.063 | 4.94 | 0.386 | 5/6 |
| HUNTER=1 | 0.078 | 0.620 | 0.635 / 0.378 | 0.433 | 0.403 | 0.070 | 4.90 | 0.385 | 4/6 |
| HUNTER=2 | 0.077 | 0.648 | 0.620 / 0.352 | 0.423 | 0.389 | 0.074 | 4.71 | 0.387 | 4/6 |
| MAX_PLACED=1 | 0.118 | 0.655 | 0.608 / 0.345 | 0.631 | 0.981 | 0.169 | 4.24 | 0.389 | 5/6 |
| RETAKE_CD=1 | 0.040 | 0.608 | 0.700 / 0.390 | 0.442 | 0.398 | 0.051 | 5.14 | 0.386 | 5/6 |
| SEALED3_HEAT=50 | 0.130 | 0.625 | 0.625 / 0.373 | 0.555 | 0.874 | 0.158 | 4.78 | 0.389 | 5/6 |
| SHIELD_BEAMS=1 | 0.098 | 0.632 | 0.643 / 0.367 | 0.432 | 0.410 | 0.078 | 4.68 | 0.389 | 5/6 |
| SHIELD_HEAT=2 | 0.040 | 0.647 | 0.700 / 0.353 | 0.453 | 0.369 | 0.045 | 5.02 | 0.405 | 5/6 |
| BEAM_HEAT=25+50 | 0.043 | 0.622 | 0.663 / 0.375 | 0.450 | 0.510 | 0.075 | 5.03 | 0.386 | 4/6 |
| BEAM_HEAT=50+100 | 0.048 | 0.625 | 0.670 / 0.373 | 0.438 | 0.414 | 0.061 | 5.22 | 0.388 | 4/6 |
| BEAM_HEAT=50+75 | 0.060 | 0.625 | 0.662 / 0.373 | 0.441 | 0.435 | 0.066 | 5.10 | 0.387 | 5/6 |
| RETAKE_HEAT=5 | 0.048 | 0.618 | 0.678 / 0.380 | 0.449 | 0.393 | 0.051 | 5.14 | 0.385 | 5/6 |
| SHIELD_BEAMS=1;BEAM_HEAT=50+75 | 0.107 | 0.633 | 0.622 / 0.365 | 0.447 | 0.459 | 0.087 | 4.56 | 0.387 | 5/6 |
| SHIELD_BEAMS=1;DECAY_FAST=1 | 0.112 | 0.742 | 0.558 / 0.258 | 0.459 | 0.428 | 0.084 | 4.65 | 0.388 | 6/6 **ALL** |
| SHIELD_BEAMS=1;HUNTER=1 | 0.100 | 0.632 | 0.632 / 0.368 | 0.428 | 0.415 | 0.079 | 4.62 | 0.388 | 5/6 |
| SHIELD_BEAMS=1;RETAKE_CD=1 | 0.097 | 0.622 | 0.667 / 0.377 | 0.431 | 0.416 | 0.077 | 4.61 | 0.389 | 5/6 |
| SHIELD_BEAMS=1;SHIELD_HEAT=1 | 0.080 | 0.637 | 0.642 / 0.362 | 0.439 | 0.390 | 0.062 | 4.74 | 0.394 | 5/6 |
| SHIELD_BEAMS=1;SHIELD_WEAR=2 | 0.105 | 0.633 | 0.633 / 0.365 | 0.429 | 0.412 | 0.077 | 4.70 | 0.388 | 5/6 |
| SHIELD_BEAMS=2 | 0.057 | 0.623 | 0.650 / 0.375 | 0.445 | 0.384 | 0.058 | 5.03 | 0.387 | 5/6 |
| SHIELD_BEAMS=2;DECAY_FAST=1 | 0.088 | 0.743 | 0.577 / 0.255 | 0.481 | 0.419 | 0.069 | 4.87 | 0.387 | 6/6 **ALL** |
| SHIELD_BEAMS=2;HUNTER=1 | 0.085 | 0.620 | 0.623 / 0.378 | 0.437 | 0.400 | 0.068 | 4.86 | 0.387 | 5/6 |
| SHIELD_BEAMS=3 | 0.048 | 0.623 | 0.675 / 0.375 | 0.442 | 0.395 | 0.054 | 5.13 | 0.387 | 5/6 |
| SHIELD_WEAR=1 | 0.137 | 0.660 | 0.523 / 0.340 | 0.363 | 0.550 | 0.138 | 3.27 | 0.383 | 4/6 |
| SHIELD_WEAR=2 | 0.058 | 0.622 | 0.662 / 0.377 | 0.443 | 0.394 | 0.060 | 5.11 | 0.386 | 5/6 |
| DECAY_FAST=1;BEAM_HEAT=50+75 | 0.058 | 0.743 | 0.580 / 0.255 | 0.479 | 0.440 | 0.070 | 4.95 | 0.386 | 5/6 |
| DECAY_FAST=1;HUNTER=1 | 0.102 | 0.740 | 0.572 / 0.258 | 0.467 | 0.427 | 0.082 | 4.69 | 0.385 | 6/6 **ALL** |
| DECAY_FAST=1;RETAKE_HEAT=5 | 0.060 | 0.687 | 0.587 / 0.312 | 0.488 | 0.405 | 0.059 | 4.94 | 0.384 | 5/6 |
| DECAY_FAST=1;SHIELD_HEAT=2 | 0.050 | 0.710 | 0.580 / 0.290 | 0.494 | 0.386 | 0.053 | 4.87 | 0.402 | 5/6 |
| SHIELD_BEAMS=1;DECAY_FAST=1;HUNTER=1 | 0.113 | 0.738 | 0.565 / 0.262 | 0.452 | 0.434 | 0.087 | 4.56 | 0.388 | 6/6 **ALL** |
| SHIELD_BEAMS=1;HUNTER=1;BEAM_HEAT=50+75 | 0.107 | 0.633 | 0.618 / 0.367 | 0.443 | 0.461 | 0.087 | 4.50 | 0.387 | 5/6 |
| SHIELD_BEAMS=1;SHIELD_HEAT=1;BEAM_HEAT=50+75 | 0.117 | 0.635 | 0.620 / 0.363 | 0.450 | 0.460 | 0.088 | 4.41 | 0.395 | 5/6 |
| SHIELD_BEAMS=1;SHIELD_HEAT=1;RETAKE_HEAT=3 | 0.075 | 0.635 | 0.650 / 0.363 | 0.438 | 0.394 | 0.064 | 4.69 | 0.392 | 4/6 |
| SHIELD_BEAMS=1;SHIELD_HEAT=2 | 0.087 | 0.653 | 0.623 / 0.347 | 0.443 | 0.384 | 0.067 | 4.58 | 0.403 | 6/6 **ALL** |
| SHIELD_BEAMS=3;DECAY_FAST=1 | 0.065 | 0.742 | 0.583 / 0.257 | 0.485 | 0.415 | 0.062 | 4.90 | 0.386 | 5/6 |

Noise: 600 campaigns per cell, so a loss rate has a standard error near 0.012 and `response_decides` near 0.015. Differences under
0.02 are not signals.

## What the data says
- Single levers that miss: partial shield alone (0.098, decides 0.432), shield cost +2 Heat alone (0.040), extra known beams (0.043-0.060),
  retake Heat or cooldown (0.040-0.048), shield wear 2, a hunter that pierces (0.078), a hunter that hits twice (0.077). None reaches 0.08 with decides >= 0.44.
- `SEALED3_HEAT=50` lifts loss to 0.130 but locks 0.874 of raids: all three candidates fire, so the plan decides nothing. Rejected.
- `MAX_PLACED=1` (g) lifts loss to 0.118 but locks 0.981 of raids. Rejected, as in H7.
- `SHIELD_WEAR=1` lifts loss to 0.137 but removes live Sites (3.27) and decides falls to 0.363. Rejected.
- Partial shield (a) is the base of every winner: it is the part of R-L that makes cadence 3 too easy. A one-beam shield alone brings
  loss to 0.098 and the extra rule only has to give back the 0.003 of `response_decides` and a little margin.
- `DECAY_FAST` raises response_decides by about 0.04 (sentries now decide which Sites fall), but costs wins (G 0.59 vs 0.69, N 0.26 vs 0.38).

## Variants that hit all six targets
| Rank | Variant | Loss G / N | Win G / N | Decides | Locked | HOME | Live | Raids/netrun |
|---|---|---|---|---|---|---|---|---|
| 1 | `SHIELD_BEAMS=1;SHIELD_HEAT=2` | 0.087 / 0.653 | 0.623 / 0.347 | 0.443 | 0.384 | 0.067 | 4.58 | 0.403 |
| 2 | `SHIELD_BEAMS=1;DECAY_FAST=1` | 0.112 / 0.742 | 0.558 / 0.258 | 0.459 | 0.428 | 0.084 | 4.65 | 0.388 |
| 3 | `DECAY_FAST=1;HUNTER=1` | 0.102 / 0.740 | 0.572 / 0.258 | 0.467 | 0.427 | 0.082 | 4.69 | 0.385 |

Also all six: `SHIELD_BEAMS=2;DECAY_FAST=1` (loss 0.088, decides 0.481) and `SHIELD_BEAMS=1;DECAY_FAST=1;HUNTER=1`
(0.113, 0.452), both with the same win cost as DECAY_FAST.

## Ranking (simplest rule a player can read first)
1. **A sentry shields its Site against the next beam only, and each shielding sentry costs +2 Heat.** Reads on screen: "BLOCK: this
   Site is safe from the next beam. +2 HEAT per sentry that blocks." Keeps the win rate (0.62 G, 0.35 N, the same as H7 at cadence 2) and
   puts the price where the player sees it, on the sentry. Margins are thin: `response_decides` 0.443 (target 0.44), loss 0.087 (floor 0.08).
2. **A sentry shields its Site against the next beam only, and a DOWN Site without a sentry is TAKEN when the raid ends.**
   Reads: "BLOCK: safe from the next beam. A hit Site with no sentry falls at once; no repair window." Best response_decides margin
   but wins fall to 0.56 G / 0.26 N, and it removes the repair-between-raids decision for unguarded Sites.
3. **A DOWN Site without a sentry is TAKEN when the raid ends, and the hunter beam ignores shields.** Reads: "Unguarded Sites fall at
   once. The hunter ignores BLOCK." Leaves R-L whole except against the hunter; same win cost as 2.

## Recommendation
Rank 1: `SHIELD_BEAMS=1` with `SHIELD_HEAT=2`. It is the smallest change to R-L (shield lasts one beam, not the raid), the cost is a number
already in the Heat vocabulary, and it is the only hit that keeps the win rate where H7 at cadence 2 left it. Because its margins are
thin, port it with `solace_tide_sentry_shield_beams` and `solace_tide_sentry_shield_heat` in config and re-check with
`tools/raid_tide/response_census.gd`; if the real `response_decides` lands under 0.44, rank 2 is the fallback.

Caveats: the oracle treats a "beam" as one scan in the order known, sealed A, sealed B, hunter. The sentry-wear (b) and cooldown (f) readings,
and the extra sealed beam as the third candidate (c), are my interpretations of the brief.

Reproduce: `python tools/raid_concepts/sweep_g1.py --campaigns 200 --variants "H7B:SHIELD_BEAMS=1;SHIELD_HEAT=2" --out <file>`.
