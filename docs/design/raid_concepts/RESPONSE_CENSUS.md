# Response census: how often does the RESPONSE matter in the real game?

Measured on main f45afc31 with `tools/raid_tide/response_census.gd` (read-only on the rules; nothing under `scripts/` changed).
Raw data and aggregation scripts: `D:/rc_tmp/raid_tide_3e/measure/` (`*.jsonl`, `agg.py`, `byidx.py`, `go.sh`).

## Method
- 32 seeded Solace campaigns (seeds 2000..2031, builtin `CampaignSimulator` bot, breaker, 60 runs max), per placement policy. The
  tide raid is opened through `SolaceTideRaid.open`, measured, then resolved through the real core. **500 raids per policy**
  (15.6 raids per campaign). All randomness is the campaign's own `RngService` streams; the census draws none.
- Placement policies (both play the response that has the least damage over the 4 rows of the real sealed A, ties keep HOLD):
  - **auto** = `SolaceTideCampaign.auto_plan` (the tide_sim skilled player: least damage under HOLD, first of equals).
  - **oracle** = the placement with the least expected damage when the best response is chosen per real A, over all legal
    placements. This mirrors the lab's `greedy_plan` (but searches every placement, not the lab's TOP_KEYS), in the game's
    damage weights (HOME 4, TAKEN 3, DOWN 1).
- Per raid, for every response option, the 12-row forecast (A x B x hunter) is compared row by row with HOLD's:
  - **differs** = tier, HOME, every district's condition, INFECTED added or lost differ on some row (Heat not counted: every card
    response costs +2 Heat, so counting it would make every card response "differ").
  - **lab metric** = the played response's tier on the real draw differs from HOLD's tier on the same draw (`tr != real_hold`).
  - LOCKED = all 12 HOLD tiers equal.
- **Two boards.** `real` = the campaign as the bot played it. `healthy` = the same raid on a counterfactual board where every
  TAKEN district is back to OK, lines and hand redrawn from the same raid stream (measured, never played). `healthy` is not a
  state the bot reaches; it shows what the screen does when the player holds more districts.

## Result 1: on the real boards the response almost never matters (the lab number is not reproduced)
Live districts (OK or DOWN) at raid time: **0 in 21 % of raids, exactly 1 in 79 %, never more** (mean 0.79). TAKEN districts
pile up (a campaign shows `t1_a`, `t1_b`, ... TAKEN, one new live one claimed per cadence) and nothing returns them. With one
live district, one HOME and about 4.7 beams (1.66 known + sealed A + sealed B + hunter), nothing can be decided.

| Metric (500 raids)                                   | Lab oracle (H6) | Game, real board, auto | Game, real board, oracle | Game, healthy board, auto | Game, healthy board, oracle |
|------------------------------------------------------|-----------------|------------------------|--------------------------|---------------------------|------------------------------|
| `response_decides` (played tier != HOLD tier, real draw) | 0.439       | **0.360**              | **0.360**                | 0.362                     | 0.728                        |
| same, excluding SACRIFICE (rows that differ without it)  | n/a         | 0.002                  | 0.012                    | 0.660                     | 0.782                        |
| share of raids with >= 2 options that differ from HOLD   | n/a         | 0.000                  | 0.002                    | 0.678                     | 0.736                        |
| share with >= 1 option that differs                      | n/a         | 0.362                  | 0.370                    | 0.796                     | 0.860                        |
| mean options (excl. HOLD) / mean that differ             | n/a         | 4.56 / 0.36            | 4.58 / 0.37              | 9.05 / 5.13               | 9.63 / 5.29                  |
| mean options that beat HOLD / are worse than HOLD        | n/a         | 0.36 / 0.00            | 0.37 / 0.00              | 3.26 / 1.80               | 4.18 / 0.99                  |
| LOCKED (all 12 HOLD tiers equal)                         | n/a         | 1.000                  | 1.000                    | 0.370                     | 0.816 (see note)             |
| share with >= 1 option whose worst or best tier differs  | n/a         | 0.360                  | 0.360                    | 0.744                     | 0.846                        |
| INFECTED delta vs HOLD, share of options non-zero        | n/a         | 0.000                  | 0.000                    | 0.384                     | 0.232                        |
| live districts at raid time (mean)                       | n/a         | 0.79                   | 0.79                     | 3.93                      | 3.93                         |
| sentries placed (mean)                                   | n/a         | 0.01                   | 0.004                    | 1.50                      | 1.49                         |
| ghost used (all on HOME)                                 | n/a         | 0.128                  | 0.128                    | 0.128                     | 0.128                        |
| no SHIFT / no JAM in the response hand                   | n/a         | 0.28 / 0.27            | 0.28 / 0.26              | 0.45 / 0.44               | 0.41 / 0.40                  |

Notes: the LOCKED row is a share of raids. In the oracle `healthy` column it reads 0.816 with `response_decides` 0.728, so a raid can be
LOCKED under HOLD (every tier equal) and still be decided by a response that changes the tier on every row; LOCKED as the
lab defines it does not mean "no choice" once a response can move the whole tier. (Not investigated further.)

By raid index (real board, same for both policies): raids 0 and 1 are 0.00 (nothing to protect, SACRIFICE unavailable or
useless), raid 2/4/6 are about 1.00 (SACRIFICE is available, the cadence gap `solace_tide_sacrifice_gap` alternates it), raids 3/5/7 are
0.00. The whole 0.36 is **one response**: SACRIFICE (trade the cheapest district for a HOME shield), chosen because
HOME 4 points outweighs TAKEN 3 in the damage weights: DAMAGED becomes BATTERED in 179 of 180 picks. Everything else
(DEPLOY, MOVE, JAM, JAM_B, DIVERT) changes the outcome in 0.2 to 1.2 % of real-board raids.

Per response type, real board, mean options per raid -> raids where any differs from HOLD (auto / oracle):
DEPLOY 1.94 options in 76 % of raids -> 0.0 % / 0.8 %; JAM 0.73 in 73 % -> 0.2 % / 0.2 %; JAM_B -> 0.0 % / 0.2 %;
DIVERT 0.79 in 15 % -> 0 %; SACRIFICE 0.36 in 36 % -> 36 % (its availability is its use).
Healthy board (oracle): DEPLOY differs in 1.44 options per raid and beats HOLD in 70 % of raids; MOVE (REDEPLOY) 1.18 and 18 %;
JAM 21 %; JAM_B 39 % differ, 23 % beat HOLD; DIVERT 6 % (1 %); SACRIFICE 52 %.

## Result 2: why options tie with HOLD (ranked, share of tied options; real board, auto policy; the oracle is within 1 point)
1. **Type mismatch on a covered district: 31 %** (DEPLOY). The sentry blocks only beams of its own type; the district is also
   crossed by a beam of another type, and `scan` hits a district once per raid (`seen`), so a block only moves the hit to the next beam. Example
   (seed 2000 raid 0): HOLD trace `known0 -> t1_a hit`; DEPLOY D on t1_a gives `known0 block`, then `sealed_a -> t1_a hit`.
   Same end state. Confirmed by trace on 3 cases.
2. **DIVERT bends a beam onto the same result: 19 %.**
3. **JAM_B (both B candidates give the same outcome): 17 %**; **JAM (the hunter beam touches nothing): 17 %.** Both are moot
   because there is one live district and the hunter (and B) cannot reach anything that has not been hit already.
4. **DEPLOY with only matching-type beams, still unchanged: 15 %.** Another beam in a later row (or HOME, hit by the next beam) takes the hit.
5. JAM with a touching hunter but same outcome: < 0.1 %.
Behind all of them is the board: one live district (or none) and every beam still reaches HOME. HOME is hit in all 12 rows in
87 % of raids (`home_all_rows` 0.872; hit by a *known* beam in all rows in 11.6 %, so only the ghost on HOME stops it,
12.8 % of raids). In 28 % of raids the hand has no SHIFT, in 27 % no JAM, so MOVE/DIVERT/JAM are not offered at all.
On the healthy board the ranking is: type mismatch 52 %, DIVERT 18 %, DEPLOY-matching-but-unchanged 8 %, JAM touching nothing 7 %,
JAM_B 4 %, MOVE where the source blocks and the target adds nothing 4 %; type mismatch is the dominant tie reason in both worlds.

## Result 3: the fold rule (`scripts/ui/raid/tide_raid_flow.gd` `_build_responses`, lines ~598-606)
The rule folds a response into HOLD's "+N same as hold" when its head is in `SolaceTideRules.CARD_RESPONSES`
(REDEPLOY, DEPLOY, JAM, JAM_B, DIVERT; never SACRIFICE) and `_signature(fc)` equals HOLD's. `_signature` is, per row,
`tier / ns.home / every district's condition`.
- It does **not** compare Heat, INFECTED added, or "ends the campaign". It is therefore narrower than the criterion
  "full outcome distribution, Heat change and INFECTED change all equal HOLD's".
- Heat: every folded row costs `solace_tide_card_response_heat` = +2 Heat that HOLD does not. Measured: 1724 of 2098
  folded options (auto) differ from HOLD in Heat (the rest are clamped at `heat_max`). So the label "changes nothing" is true of the
  board and false of the Heat. The screen does say "same result as HOLD" and the ghost row keeps a reason, but the +2 is hidden.
- INFECTED and lethal: in all 2098 (auto) and 2102 (oracle) folded options, INFECTED and lost state equal HOLD's, so the rule never hid
  an INFECTED or CITY LOST difference on these 1000 raids. The code does not guarantee it (a HOME hit that infects without
  changing HOME points, or a loss that depends on the INFECTED count, would fold), and `_uniform()` already checks both for another purpose.
- Folded rows do not differ in tier or in any district. Example of a fold that differs in Heat only: seed 2000 raid 0,
  `["DEPLOY","D","t1_a"]`: same tier HOLDS, same owned districts, Heat +2.
Verdict: **folds exactly the rows whose tier/HOME/districts equal HOLD's; it also folds rows that differ in Heat (almost always), and
could fold a row that differs only in INFECTED or in a campaign-ending result.** Not fixed (another agent is editing scripts/ui).

## What the critic saw
"15 of 16 choices change nothing, only DEPLOY changed the odds" matches the real board: one live district, the hand's DEPLOY is
the only card that can ever block, and SACRIFICE is gap-limited. The game is not giving the player fewer choices than the lab by a
bug; it is giving them a board where most choices cannot exist.

## Recommendation
Target: `response_decides` of the real (bot-reachable) board at or above the lab's 0.44, with at least 2 options that differ in 0.5 of raids.
The healthy-board oracle gets 0.73 and 0.74 for the second figure, so the response design works once the board holds districts.
1. **Rules or content (the cause): keep 3 or more live districts on the lines at raid time.** Either (a) a TAKEN district comes back (a
   re-take run, as Exploit Sites already have via `is_retake`), (b) fewer districts are TAKEN per raid (TAKEN needs DOWN twice), or (c) claims arrive
   faster than raids. Measure the cause with `tools/raid_tide/response_census.gd` after any such change: `live_owned` mean >= 3 is the check.
   A designer decision; the current bot may also under-claim (it claims one district per cadence and never retakes), so confirm with a human-like
   claim policy before changing rules.
2. **Rules: widen what a DEPLOY can do.** 31 % to 52 % of ties are type mismatch plus the one-hit-per-district rule. Options: a sentry blocks the district
   (all types) while a typed one also stops the beam; or the first hit is not final (a second beam of another type still hits). Cheap to test: the census gives the new tie share directly.
3. **Content: SACRIFICE should not be the only live choice.** Its pick is driven by HOME 4 vs TAKEN 3 in `solace_tide_auto_*_weight` (it turned 179 DAMAGED into BATTERED),
   which is a weight artifact. Gate or price it, or raise the TAKEN weight, and re-run: the real-board figure then drops to about 0.00 to 0.01, which shows how little else decides.
4. **UI: fold on Heat as well, or show the cost.** Either add the Heat change (and INFECTED, lethal) to the fold test or print "+2 Heat" on the "+N same as hold" row so the label is true.

## Tool
`godot --headless --path . -s tools/raid_tide/response_census.gd -- --seeds 2000:2007 --policy auto|oracle --out file.jsonl`
(one `RAID {json}` line per measured raid; `mode` is `real` or `healthy`). Aggregation: `D:/rc_tmp/raid_tide_3e/measure/agg.py`.

## H7 re-measure (2026-10-26, branch raid-tide-h7)
Same tool, same seeds (2000..2031), after R-K (retake TAKEN Sites), R-L (a sentry shields its Site), R-M (SITES LOST), the cadence
3 -> 2, and the bot retaking TAKEN Sites and claiming every cleared Site. Real board (`mode` real); raw data in
`D:/rc_tmp/raid_tide_h7/census/`.

| Metric | before auto | H7 auto | before oracle | H7 oracle |
|---|---|---|---|---|
| live owned Sites at raid (mean) | 0.79 | 4.78 | 0.79 | 5.43 |
| `response_decides` | 0.360 | 0.415 | 0.360 | 0.698 |
| >= 2 options differ from HOLD | 0.000 | 0.752 | 0.002 | 0.801 |
| >= 1 option differs from HOLD | 0.362 | 0.831 | 0.370 | 0.905 |
| LOCKED | 1.000 | 0.360 | 1.000 | 0.701 |

Targets: live >= 3 met; >= 2 differing options in about half the raids met; `response_decides` >= 0.44 met by the oracle placement,
not by `auto_plan` (0.415). Full entry: DECISIONS "2026-10-26 Solace tide H7".
