<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01PDEyQB42bgSjCYUK2iMTqj, custom_id bsweep__boss_length; status ok; tokens in 25845 cache-write 0 cache-read 32585 out 6297; cost $0.061. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# balance sweeps: boss length (V4)

## 1. Question and hypotheses

**Question:** which data levers bring the Solace boss (`renewal_engine`) to 12-20 turns, and which win rate should we propose for open question 12?

**Baseline:** 38.1 turns and 25 % win (fresh, 8 seeds); 41-50 turns and 4-8 % win inside campaigns. Damage taken is 2.08 per turn. Phases split 17 / 13 / 9 turns, and the boss heals on about 37 of its 38 turns.

- **H1 (HP):** turns scale about linearly with boss HP, because the heal is roughly constant per turn.
  - `renewal_engine.hp` ×0.6 gives about 23 turns, ×0.45 about 17, ×0.35 about 13.
  - Win rate rises because the operative's 60 HP is spent over fewer turns. Ending HP is 60 − turns × 2.1, so the operative dies at roughly 29 turns.
  - Expected win rate at ≤ 20 turns is above 80 % at skill 1.0.
- **H2 (skill):** at skill 0.6 the win rate is 20-40 points lower than at skill 1.0 for the same HP. Turns rise by about 30 %, because damage per turn falls.
- **H3 (damage):** raising the boss damage scale compensates for the short fight.
  - Each +0.15 on `enemy_damage_scale_per_tier` is about +7 % damage at T4.
  - It trades about 2-4 points of win rate for little change in turns.
- **H4 (pointers):** the only existing pointer lever is ICE 18, which adds a pointer to the final boss. It is confounded with ICE 1-17 and shortens turns by at most 10 %.
- **H5 (ICE 9):** "Bosses +25 % HP and damage" lengthens the fight by about 20 %. At the chosen HP, ICE 9 must stay ≤ 20 turns.

**Levers with no data property (do not invent):**
- NO LEVER: boss phase count, thresholds and per-phase HP. The data field names were not given; this needs N3 or a field list.
- NO LEVER: enrage turn (N4, not built).
- NO LEVER: boss pointer count at ICE 0 (only ICE 18 or phase data).
- NO LEVER: Exploit effects on the boss fight. `--source fresh` applies no Exploits, and `min_exploits_for_breach` only gates launching the breach. Exploit-disabled heal or pointer can only be approximated by hand-editing the boss.

## 2. Sweep table

Common flags: `-j 2`, `--policy builtin`, `--out-dir docs/balance/runs`. Boss fresh runs take about 15-25 s per seed (estimate), since fresh skips the campaign.

| id | mode | command | variants | seeds | wall time | metric | decision rule |
|---|---|---|---|---|---|---|---|
| S0 | boss | `python tools/balance/balance.py run boss --name boss_fresh_base --source fresh --seeds 1000:1019 -j 2` | none | 20 | ~4 min | turns, win %, damage taken per turn | Reproduces ~38 turns and ~25 %. If it is more than ±8 turns off, re-anchor every threshold below. |
| S1 | boss | `... --name boss_hp060 --source fresh --seeds 1000:1019 --variant docs/balance/variants/boss_hp060.json -j 2` | hp060 | 20 | ~4 min | turns mean and p90 | Confirms H1 if turns are within ±15 % of 23. |
| S2 | boss | same, `--name boss_hp045` | hp045 | 20 | ~3 min | turns, win % | Candidate A if turns are 14-20. |
| S3 | boss | same, `--name boss_hp035` | hp035 | 20 | ~3 min | turns, win % | Candidate B if turns are 11-16. |
| S4 | boss | `... --name boss_hp045_s06 --skill 0.6 --variant boss_hp045.json` | hp045 | 20 | ~4 min | turns, win % | Tester-proxy. Must stay ≤ 25 turns and keep a win rate in 30-70 %. |
| S5 | boss | `--name boss_hp035_s06 --skill 0.6 --variant boss_hp035.json` | hp035 | 20 | ~3 min | same | same |
| S6 | boss | `--name boss_hp045_d145 --variant boss_hp045_d145.json` | hp045_d145 | 20 | ~3 min | win %, ending HP | H3. Keep it only if the win rate drops by ≥ 8 points at the same turns. |
| S7 | boss | `--name boss_hp045_d160 --variant boss_hp045_d160.json` | hp045_d160 | 20 | ~3 min | same | same |
| S8 | boss | `--name boss_hp045_ice9 --ice 9 --variant boss_hp045.json` | hp045 | 20 | ~4 min | turns | H5. Reject if > 22 turns. |
| S9 | boss | `--name boss_hp045_ice18 --ice 18 --variant boss_hp045.json` | hp045 | 20 | ~4 min | turns vs S8 | H4. The pointer effect is the S9 − S8 delta; ICE 18 also includes ICE 10-17, which change no boss stat (ICE 10 and 15 are reserved), so the delta is clean. |
| S10 | boss | `--name boss_hp045_h2 --policy heuristic --lookahead 2 --seeds 1000:1004 -j 2 --variant boss_hp045.json` | hp045 | 5 | ~6 min | win %, turns | "Is it a puzzle". The expert should win ≥ the bot. |
| S11 | boss | `--name boss_camp_hp045 --source campaign --seeds 1000:1007 --variant boss_hp045.json -j 2` | hp045 (or the winner) | 8 | ~3 min | win %, turns | Campaign-realistic confirmation. Target ≥ 35 %. |
| S12 | campaign | `... run campaign --name camp_ice0_bosshp --ice 0 --seeds 1000:1019 --variant <winner> -j 2` | winner | 20 | ~12 min | minutes, win %, boss fights | Run only after S11. Reads minutes against ~395; the baseline is 605. |

(`...` stands for `python tools/balance/balance.py run boss`.)

## 3. Variant files

Save under `docs/balance/variants/`. `*=` and `+=` are the documented multiply and add forms. If `*=` on an int field rounds oddly, switch to absolute values (`renewal_engine.hp=<json>`), which needs the current `hp` first (see Q1).

`boss_hp060.json`
```json
{"name": "boss_hp060", "set": ["renewal_engine.hp*=0.6"]}
```
`boss_hp045.json`
```json
{"name": "boss_hp045", "set": ["renewal_engine.hp*=0.45"]}
```
`boss_hp035.json`
```json
{"name": "boss_hp035", "set": ["renewal_engine.hp*=0.35"]}
```
`boss_hp045_d145.json`
```json
{"name": "boss_hp045_d145", "set": ["renewal_engine.hp*=0.45", "config.enemy_damage_scale_per_tier=1.45"]}
```
`boss_hp045_d160.json`
```json
{"name": "boss_hp045_d160", "set": ["renewal_engine.hp*=0.45", "config.enemy_damage_scale_per_tier=1.6"]}
```
Note: `config.enemy_damage_scale_per_tier` is global, but boss mode only fights the boss, so it is clean there. It would NOT be clean in S12. Run S12 only with an HP-only variant, or accept a confounded campaign.

## 4. Order and stop rules

1. Run S0 first. Stop and re-anchor if the baseline does not reproduce.
2. Run S1, S2 and S3 together as a pair (2 processes). If S2 lands in 14-20 turns, skip S3 and S5 unless the designer wants a tighter fight.
3. Run S4 (and S5 if S3 ran) next. If the skill-0.6 win rate is under 20 %, the fight is too lethal for testers: go to S6/S7 with a lower damage scale, not a higher one (see Q2).
4. Run S6 and S7 only if the win rate at skill 1.0 is above 85 %.
5. Run S8 and S9 once, with the chosen HP.
6. Run S10 and S11 for the chosen option. Run S12 only if S11 passes.
7. Stop early on any candidate whose turn p90 is above 24 at skill 1.0.

## 5. Compare plan

| compare | output |
|---|---|
| `compare boss_fresh_base.json boss_hp060.json --name boss_hp060` | `CMP_boss_hp060.md` |
| `compare boss_fresh_base.json boss_hp045.json --name boss_hp045` | `CMP_boss_hp045.md` |
| `compare boss_fresh_base.json boss_hp035.json --name boss_hp035` | `CMP_boss_hp035.md` |
| `compare boss_hp045.json boss_hp045_d145.json --name boss_dmg145` | `CMP_boss_dmg145.md` |
| `compare boss_hp045_ice9.json boss_hp045_ice18.json --name boss_pointer` | `CMP_boss_pointer.md` |
| `compare <baseline campaign json> camp_ice0_bosshp.json --name camp_bosshp` | `CMP_camp_bosshp.md` |

## 6. Options write-up skeleton (BALANCE_OPTIONS.md, section "Boss length")

- **Problem:** baseline numbers and the V4 quote.
- **Levers measured / NO LEVER list.**
- **Option A, HP ×0.6:** turns, win % at skill 1.0 and 0.6, ICE 9 check, the cost to the designer.
- **Option B, HP ×0.45:** same fields. Recommended by default if it lands in 14-20 turns.
- **Option C, HP ×0.35 plus damage 1.45-1.6:** same fields.
- **Win-rate proposal (open question 12):** fresh skill 1.0 about 75 %, skill 0.6 about 45 %, in campaigns about 40 %, ICE 9 about 55 %.
- **Campaign impact:** minutes against ~395 and the number of boss fights.
- **What needs new systems:** N3 phases, N4 enrage, N5 Exploits, plus the unmeasured levers.
- **Noise caveats:** n = 20, the 90 % interval from compare.

## 7. Q:

- **Q1:** What is the current `renewal_engine.hp`, and does `*=` on an int field round or truncate? The variants are written as multipliers because the base value was not provided.
- **Q2:** Should the boss target the bot's skill 1.0 or the testers' skill ~0.6? The proposal above asks for ~75 % and ~45 % respectively; please pick one as binding.
- **Q3:** Are turn targets for "fresh" a starter operative (S0-S10) or a campaign-leveled one (S11)? The two differ by about 10 turns today.
- **Q4:** May the single global `config.enemy_damage_scale_per_tier` change stand as a boss-only lever, or do you want a boss-specific damage field (NO LEVER today)?
