<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01PDEyQB42bgSjCYUK2iMTqj, custom_id bsweep__campaign_pace; status ok; tokens in 25838 cache-write 0 cache-read 32585 out 3326; cost $0.046. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# balance sweeps: campaign pacing

## 1. Question and hypotheses

**Question:** which data levers cut campaign minutes from 605 (median 793) toward ~395 without moving the 50 % win rate (ICE 0)?

Baseline facts:
- 38.6 runs, 203 fights, 10.5 deaths per campaign.
- The median campaign hits the 60-run cap (runs p90 60, median 51).
- Win rate is 50 % and the other half run out the cap. Loss is 0 %.
- Minutes track runs and fights, so the cap-hitting campaigns drive the mean.
- Boss fights average 41 turns at T4, win 8 %.

Hypotheses:
- **H1 (deaths):** deaths dominate run count, since each death costs a run, an operative and Heat (+10 base). Lowering `death_heat_base` (10 → 5) should cut raids and Heat peak and shorten the campaign by about 5–10 %. Win rate may rise slightly.
- **H2 (heal availability):** heals used is 0.37 of 1.94 available per run, so it is not a supply limit. The bot barely uses heals. Expect an unchanged outcome. A **NO LEVER** exists for heal amount or the bot's heal-use rate, since heal power lives in event and node data not shown.
- **H3 (run cap):** `max_runs` 60 → 40 cuts minutes mechanically for capped campaigns (median 793 → about 550). This is a measurement artifact lever, not a design lever. It can turn capped campaigns into losses, so the win rate falls toward the completed share.
- **H4 (enemy HP scale):** `enemy_scale_per_tier` 1.6 → 1.4 shortens T3 fights (enemy T3 6.6 turns, elite 14.5, mini-boss 20.7) by about 15–25 %. Fights per campaign are fixed by the layer count, so minutes fall roughly 8–12 %. Win rate rises, so pair it with the damage scale for a net-neutral test.
- **H5 (layers):** `map_layers` 7 → 6 cuts fights per run by about 1/7 (14 %). Heat per run stays about the same, so Heat accrues slower per fight, and the minutes cut is probably 10–14 %. Rack layers (4, 7) need `rack_layers=[4,6]` with it.
- **H6 (boss length):** the boss fights are long (41 turns, 123 fights). `enemy_scale_per_tier` affects them via the tier factor. Boss HP is a content value. Test `renewal_engine.hp*=0.6`; expect about −15 turns and a higher boss win rate. This affects win rate directly, so it is paired with a damage lever.

## 2. Sweep table

Common flags: `--policy builtin --skill 1.0 --ice 0 --seeds 1000:1019 -j 2`. Campaign wall time ≈ 750 s at 20 seeds at -j 2.

| id | mode | command | variants | seeds | wall | metric | decision rule |
|---|---|---|---|---|---|---|---|
| S0 | campaign | `python tools/balance/balance.py run campaign --name pace_base --seeds 1000:1019 -j 2` | none (baseline, reuse BASELINE JSON if sha matches) | 20 | 0 (reuse) | minutes mean/median, win | reference |
| S1 | campaign | `... --name pace_deathheat --variant docs/balance/variants/pace_deathheat.json` | death_heat_base=5 | 20 | 750 s | minutes, deaths, raids, win | confirms H1 if minutes −5 % or more and win within ±10 pts |
| S2 | campaign | `... --name pace_layers6 --variant docs/balance/variants/pace_layers6.json` | map_layers=6, rack_layers [4,6] | 20 | 700 s | minutes, fights, win | confirms H5 if fights −10 % or more and win within ±10 pts |
| S3 | campaign | `... --name pace_hp --variant docs/balance/variants/pace_hp.json` | enemy_scale_per_tier=1.4 | 20 | 700 s | fights table turns, minutes, win | confirms H4 if T3 turns −15 % or more |
| S4 | campaign | `... --name pace_hp_dmg --variant docs/balance/variants/pace_hp_dmg.json` | scale 1.4 and damage scale 1.4 | 20 | 700 s | win, minutes | rule: win within ±10 pts means HP and damage are interchangeable |
| S5 | campaign | `... --name pace_cap40 --variant docs/balance/variants/pace_cap40.json` (also `--max-runs 40`) | max_runs=40 | 20 | 550 s | minutes, win | reads the mechanical cap effect only |
| S6 | boss | `python tools/balance/balance.py run boss --name pace_boss --source fresh --seeds 1000:1007 --variant docs/balance/variants/pace_boss.json -j 2` | renewal_engine.hp*=0.6 | 8 | 150 s | total turns, win | confirms H6 if turns ≤ 25 |
| S7 | campaign | `... --name pace_combo --variant docs/balance/variants/pace_combo.json` | S1 + S2 + S3 | 20 | 650 s | minutes, win | the candidate option |
| S8 | campaign | `... --name pace_ice5_combo --ice 5 --variant docs/balance/variants/pace_combo.json` | S7 at ICE 5 | 20 | 650 s | win vs baseline ICE 5 (35 %) | checks the ladder is not distorted |

## 3. Variant files

`pace_deathheat.json`
```json
{"name":"pace_deathheat","set":["config.death_heat_base=5"]}
```
`pace_layers6.json`
```json
{"name":"pace_layers6","set":["config.map_layers=6","config.rack_layers=[4,6]"]}
```
`pace_hp.json`
```json
{"name":"pace_hp","set":["config.enemy_scale_per_tier=1.4"]}
```
`pace_hp_dmg.json`
```json
{"name":"pace_hp_dmg","set":["config.enemy_scale_per_tier=1.4","config.enemy_damage_scale_per_tier=1.4"]}
```
`pace_cap40.json`
```json
{"name":"pace_cap40","set":[]}
```
(the cap is a CLI option, `--max-runs 40`, not a config property.)

`pace_boss.json`
```json
{"name":"pace_boss","set":["renewal_engine.hp*=0.6"]}
```
`pace_combo.json`
```json
{"name":"pace_combo","set":["config.death_heat_base=5","config.map_layers=6","config.rack_layers=[4,6]","config.enemy_scale_per_tier=1.4"]}
```

NO LEVER: heal amount per Terminal and the bot's heal-use rate (data not shown in the config). Check the event `.tres` before sweeping heals.

## 4. Order and stop rules

1. S6 first (150 s, cheapest); it also informs the boss share of the minutes.
2. S1, S2, S3 in sequence (one at a time with -j 2). Stop a branch if win moves more than ±15 pts.
3. S4 only if S3 shifts win by more than 10 pts.
4. S5 once, as a reference only.
5. S7 only after S1–S3 each show a minutes cut. Drop any lever with a cut under 3 % (inside noise at n=20).
6. S8 only if S7 holds win within ±10 pts.

Total: about 2.5 hours serial.

## 5. Compare plan

- `compare pace_base.json pace_deathheat.json --name pace_deathheat`
- `compare pace_base.json pace_layers6.json --name pace_layers6`
- `compare pace_base.json pace_hp.json --name pace_hp`
- `compare pace_hp.json pace_hp_dmg.json --name pace_hp_dmg_neutral`
- `compare pace_base.json pace_combo.json --name pace_combo`
- `compare BASELINE ICE 5 pace_ice5_combo --name pace_combo_ice5`

All files are CMP_<name>.md. Note that 20 seeds with a bimodal outcome (win or capped) produces wide intervals, so read "noise" flags strictly.

## 6. Options write-up skeleton (BALANCE_OPTIONS.md)

- Problem and baseline (minutes, runs, fights, deaths).
- Option A: reduce deaths and Heat (S1).
- Option B: shorten the map (S2).
- Option C: lower enemy HP scale (S3/S4).
- Option D: combined (S7/S8).
- For each: delta table (minutes, win, deaths, raids, boss turns), noise flags, risk to the win rate, files to edit.
- Rejected: the cap-only change (S5), because it hides the loss.
- Not testable: heal levers (NO LEVER).
- Recommendation, and rulings needed.

## 7. Q:

- Q: Is win rate 50 % counted with capped campaigns as non-wins? If so, any minutes cut raises the win rate by converting capped runs. Should the target be the win rate among completed campaigns?
- Q: Is the 395 min target for a winning campaign only, or the mean over all?
- Q: Is the minutes estimate per fight or per run? The formula is not shown, so the cuts to layers or fights may map nonlinearly.
- Q: Should the boss tuning wait for the R1–R4 phase redesign, so the S6 numbers are only a proxy?
