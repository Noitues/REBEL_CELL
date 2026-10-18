# S5 results (round W0 S5): balance measurement sweeps

Measurement only. No content or config value was changed. Tool: `tools/balance/balance.py` (N19 metrics, `docs/handoff/N19_METRICS_SCHEMA.md`).
Base: main `b8d7ea73` (W0 rules foundation merged: N1-N4, N11, N13, N14, N19, N21, N22). Machine: this PC, 2 Godot processes at a time.
Raw JSON stayed under `%TEMP%\w0_s5\runs` (not in the repo). Variant files are in `docs/balance/variants/s5_*.json`. The `balance.py compare` outputs are in `docs/balance/S5_cmp/CMP_*.md`.
Class order in the enrage tables is `[NORMAL, ELITE, MINI_BOSS, BOSS]`; the sweeps only touched the BOSS entry.

## 0. Headline numbers

1. Boss win rate at ICE 0 (builtin bot, starter-to-breach campaign state, 97 usable fights of seeds 1000:1099): **6 %** against the 50 % target. Mean 23.5 turns, median 20, p90 56. Phase 1 alone averages 19.4 turns (target 3-4); the boss heals on 22.5 of its 23.5 turns.
2. Enrage defaults barely move it. Start 6 / 14, step 10 / 50 %, every 3 / 8 turns all land inside noise at 20 seeds, and start 14 + every 8 gives 8 % (vs 6 %) at 100 seeds, also noise. The lever that moved it is boss HP: x0.35 gives **19 %** win (+12 points, interval excludes 0) and 19.6 turns.
3. Calibration (Step 0), pooled dealt per turn on normals, builtin bot: skill 1.0 = **14.4 to 14.9** (flat across tiers), 0.6 = 10.6 to 11.1, 0.4 = 7.0 to 7.9, 0.2 = 5.8 to 6.3. Heuristic lookahead 1 = 17.4 to 19.3, lookahead 2 = 18.6 to 21.0. The proposed `reference_dpt_by_tier` [9, 11, 14, 18] sits between skill 0.6 and the heuristic; it rises with tier, the measured curve does not.
4. "Both wheels in one turn" share (Q16 baseline, mean of per-fight share): builtin 1.0 = **0.35** (normals 0.39, elites 0.25, mini-bosses 0.26, boss 0.21 to 0.24); skill 0.6 = 0.29; skill 0.2 = 0.21; heuristic = 0.52 (lookahead 2: 0.52). The expert play both-wheels more, so the share falls with weaker play, not by itself.
5. Campaign (ICE 0, 20 seeds): win **20 %**, loss 5 %, 48 runs, 22 deaths, 746 minutes (GDD ~395), 257 fights, Heat peak 92. None of the seven single-lever variants moved minutes or win outside noise; only `map_terminal_ratio` 0.4 changed something (heals available +52 %, used +55 %, still 0.68 of 3.07).

Determinism (S0h, S0i): rerun JSON identical excluding the name and wall clock, at skill 1.0 and 0.6. The tool is sound.

## 1. Step 0 calibration

Commands (all `python tools/balance/balance.py run fight --enemy all --tiers 1,2,3,4 --categories enemy,elite,mini_boss -j 2 --seeds 1000:1019` unless noted; 12 groups x 20 seeds = 720 records, ~65 s):

| id | name | extra flags |
|---|---|---|
| S0a | cal_builtin_s100 | (none) |
| S0h | cal_det_s100_rerun | (none; determinism) |
| S0b | cal_builtin_s060 | `--skill 0.6` |
| S0i | cal_det_s060_rerun | `--skill 0.6` (determinism) |
| S0c | cal_builtin_s040 | `--skill 0.4` |
| S0d | cal_builtin_s020 | `--skill 0.2` |
| S0e | cal_heur1_s100 | `--policy heuristic --lookahead 1` |
| S0g | cal_heur1_s060 | `--policy heuristic --lookahead 1 --skill 0.6 --seeds 1000:1009` |
| S0f | cal_heur2_s100 | `--policy heuristic --lookahead 2 --seeds 1000:1009` |

Fresh starter operative (rank 0), Solace enemies only, so this does not include operative growth (the `fight` mode cannot supply a campaign-state operative). dealt/turn is sum(dealt) / sum(turns) over the group.

### 1.1 Builtin bot, skill 1.0 (S0a)

| category | tier | n | win % | turns | dealt/turn | taken/turn | both-wheels share |
|---|---|---|---|---|---|---|---|
| enemy | 1 | 120 | 100 | 2.8 | 14.4 | 1.67 | 0.39 |
| enemy | 2 | 120 | 100 | 4.3 | 14.8 | 2.11 | 0.38 |
| enemy | 3 | 120 | 99 | 7.0 | 14.6 | 2.50 | 0.41 |
| enemy | 4 | 120 | 82 | 10.5 | 14.9 | 2.99 | 0.39 |
| elite | 1 | 40 | 100 | 4.7 | 23.2 | 3.91 | 0.27 |
| elite | 2 | 40 | 92 | 8.0 | 21.8 | 4.39 | 0.30 |
| elite | 3 | 40 | 30 | 12.4 | 19.5 | 4.58 | 0.25 |
| elite | 4 | 40 | 0 | 11.8 | 19.2 | 5.06 | 0.22 |
| mini_boss | 1 | 20 | 100 | 8.2 | 18.4 | 2.37 | 0.31 |
| mini_boss | 2 | 20 | 90 | 12.8 | 18.7 | 2.95 | 0.29 |
| mini_boss | 3 | 20 | 0 | 20.2 | 15.9 | 2.97 | 0.23 |
| mini_boss | 4 | 20 | 0 | 20.2 | 15.1 | 2.96 | 0.20 |

### 1.2 Skill ladder, normals only (dealt/turn | turns | win %)

| policy | T1 | T2 | T3 | T4 |
|---|---|---|---|---|
| builtin 1.0 | 14.4 / 2.8 / 100 | 14.8 / 4.3 / 100 | 14.6 / 7.0 / 99 | 14.9 / 10.5 / 82 |
| builtin 0.6 | 10.6 / 3.8 / 100 | 11.0 / 5.8 / 96 | 10.9 / 9.1 / 75 | 11.1 / 11.8 / 44 |
| builtin 0.4 | 7.0 / 5.8 / 100 | 7.6 / 8.5 / 89 | 7.9 / 11.0 / 48 | 7.7 / 12.6 / 22 |
| builtin 0.2 | 5.8 / 7.0 / 96 | 6.1 / 10.0 / 72 | 6.3 / 11.8 / 29 | 5.9 / 12.6 / 7 |
| heuristic L1, 1.0 | 17.4 / 2.3 / 100 | 18.6 / 3.4 / 100 | 19.1 / 5.4 / 100 | 19.3 / 8.4 / 85 |
| heuristic L1, 0.6 (10 seeds) | 11.1 / 3.6 / 100 | 12.2 / 5.3 / 98 | 12.9 / 7.8 / 90 | 12.9 / 10.8 / 50 |
| heuristic L2, 1.0 (10 seeds) | 18.6 / 2.1 / 100 | 20.1 / 3.2 / 100 | 20.7 / 4.9 / 100 | 21.0 / 7.7 / 88 |

Full per-category tables for each run are in the `balance.py report` markdown (`cal_*.md`); the elite and mini-boss rows follow the same pattern (heuristic L2 elites 26.7 to 28.4, mini-bosses 23.8 to 27.4 dealt/turn).

Hypotheses against the data:

- H1 (dealt/turn roughly linear in skill): holds. Spread skill 1.0 to 0.2 is 14.7 to 6.0 (2.4x), well above the 20 % stop threshold. Skill 0.6 lands at 10.6 to 11.1, inside the spec band 8-12; 0.4 gives 7.0 to 7.9 (spec 5-9); 0.2 gives 5.8 to 6.3 (spec 3-6, the testers' 3.2-5.0 sits just under skill 0.2).
- H2 (dealt/turn falls with tier at fixed skill): **not supported** on normals; dealt/turn is flat (14.4 to 14.9). It falls only on elites (23.2 to 19.2) and mini-bosses (18.4 to 15.1). Fights get longer because enemy HP and damage grow, not because the operative deals less.
- H3 (heuristic >= builtin): holds and is large: +21 % to +30 % on normals, +19 % to +21 % on elites, +13 % to +60 % on mini-bosses. Lookahead 2 adds another ~6 to 9 % over lookahead 1. The builtin bot is therefore not the ceiling.
- H4 (3.5 turns per phase at mid skill is infeasible with today's HP): confirmed for any tier above 1. Skill 0.6 normals take 3.8 / 5.8 / 9.1 / 11.8 turns on T1-T4 in a single phase; only builtin skill 1.0 and the heuristic reach 3-4 turns, and only at T1 to T2.
- H5 (damage scale): see 1.3.

### 1.3 Damage table fit (S0j; collections_agent, compliance_officer, billing_daemon, 20 seeds)

`config.enemy_damage_scale_per_tier` no longer exists; the lever is now `config.enemy_damage_by_tier` (current [1.0, 1.3, 1.69, 2.2]). Variants: `s5_cal_noop` (current values, control), `s5_cal_damage_12` ([1, 1.2, 1.44, 1.728]), `s5_cal_damage_16` ([1, 1.6, 2.56, 4.096]).

| table | T1 taken/turn | T2 | T3 | T4 | T4 win % | T4 turns |
|---|---|---|---|---|---|---|
| current (control) | 1.71 | 1.96 | 2.26 | 3.09 | 97 | 11.7 |
| 1.2 per tier | 1.71 | 1.79 | 1.92 | 2.62 | 100 | 11.3 |
| 1.6 per tier | 1.71 | 2.17 | 3.02 | 3.76 | 55 | 11.6 |

The observed taken/turn ratios against T1 for the current table are 1.15 / 1.32 / 1.81 (table 1.3 / 1.69 / 2.2): the realized damage grows slower than the table because longer fights spend more turns with the bot blocking and winning. Control equals the baseline values (override path is a no-op), as required. See `CMP_cal_dmg_12.md`, `CMP_cal_dmg_16.md`.

### 1.4 What this means for N2 inputs (offline)

- dpt_ref measured (normals): 14.4 to 14.9 builtin, 10.6 to 11.1 at skill 0.6, 17.4 to 21.0 heuristic. No tier trend. Proposed [9, 11, 14, 18] is only reachable if the operative's power grows with rank (not measured here, "fresh" operative only) or the tester band is skill ~0.6 at T1 and ~0.9 at T4. Flagged as a designer decision.
- Elite and mini-boss fights are lost at T3 and T4 by a fresh operative (elite T3 30 %, T4 0 %; mini-boss T3 and T4 0 % at skill 1.0), which is expected for a fresh T1 operative but means the fight sweep cannot calibrate those cells.

## 2. Boss length (`boss_length.md`)

The draft was written before N3 (phases) and N4 (enrage) existed. Adapted: boss HP via `renewal_engine.hp*=`, enrage via the three `config.enrage_*_by_class` tables (BOSS entry). Two sources:

- `--source fresh` (a starter operative against the boss): 0 % win in every variant tried, 7.7 turns mean (4.7 at ICE 9, 6.5 at skill 0.6). The fresh operative dies in phase 1 (boss HP stays at 0.99). Useless as a balance anchor under the new rules; dropped after the first three runs.
- `--source campaign` (a bot-played campaign to the breach, then the boss fight). The real anchor. Usable fights: 97 of 100 seeds (3 campaigns never reached the breach) in the 100-seed runs, 19 of 20 in the screen.

### 2.1 Baseline and the 100-seed runs (campaign source, ICE 0, builtin, skill 1.0)

Command: `python tools/balance/balance.py run boss --name <n> --source campaign --seeds 1000:1099 -j 2 [--variant ...]` (~21 min each).

| run | fights | win % | turns mean / median / p90 | phase 1 turns | phase 2 (n) | phase 3 (n) | enrage step mean | taken/turn | boss heal turns |
|---|---|---|---|---|---|---|---|---|---|
| boss100_base | 97 | 6 | 23.5 / 20 / 56 | 19.4 | 9.6 (31) | 8.3 (12) | 3.35 | 4.99 | 22.5 |
| boss100_hp050 (hp x0.5) | 97 | 10 | 21.4 / 17 / 53 | 13.8 | 10.7 (53) | 6.3 (28) | 2.93 | 5.06 | 20.4 |
| boss100_hp035 (hp x0.35) | 97 | 19 | 19.6 / 16 / 37 | 10.9 | 9.0 (62) | 7.3 (40) | 2.60 | 5.10 | 18.6 |
| boss100_enrage14_every8 (start 14, every 8) | 97 | 8 | 25.0 / 21 / 60 | 21.0 | 9.6 (30) | 8.2 (13) | 1.97 | 4.86 | 24.1 |

`balance.py compare` against the base (90 % bootstrap): hp x0.35 is the only one outside noise (won +12.4 points, [+5.1, +19.6]; turns -3.9, [-7.4, -0.4]; heal turns -3.9). hp x0.5 won +4.1 points ([-2.1, +10.3], noise). Gentler enrage: noise. Files: `CMP_b100_hp035.md`, `CMP_b100_hp050.md`, `CMP_b100_enr.md`.

### 2.2 The 20-seed enrage and HP screen (campaign source, seeds 1000:1019, 19 usable fights)

Baseline for this screen: 5 % win, 20.9 turns, enrage step 2.84. One win equals 5.3 points, so every win-rate difference here is one or two fights; read turns and heal turns instead.

| variant | override | win % | turns mean / median / p90 | phase 1 | enrage step | op HP at end |
|---|---|---|---|---|---|---|
| base | none | 5 | 20.9 / 15 / 51 | 16.2 | 2.84 | 5.7 |
| enrage6 | start turn 10 -> 6 | 5 | 16.6 / 13 / 36 | 13.9 | 2.84 | 2.5 |
| enrage14 | start turn 10 -> 14 | 11 | 21.7 / 19 / 51 | 16.7 | 2.53 | 7.2 |
| step10 | damage step 25 -> 10 % | 11 | 22.3 / 20 / 51 | 17.3 | 3.16 | 7.2 |
| step50 | damage step 25 -> 50 % | 5 | 19.6 / 14 / 51 | 14.9 | 2.63 | 5.7 |
| every3 | every 5 -> 3 turns | 5 | 20.5 / 14 / 51 | 15.8 | 4.47 | 5.7 |
| every8 | every 5 -> 8 turns | 11 | 21.3 / 18 / 51 | 16.4 | 2.05 | 7.2 |
| hp070 | boss hp x0.7 | 11 | 18.2 / 15 / 30 | 14.4 | 2.26 | 4.3 |
| hp050 | boss hp x0.5 | 16 | 18.2 / 15 / 36 | 12.4 | 2.26 | 8.1 |
| hp035 | boss hp x0.35 | 16 | 17.5 / 15 / 27 | 9.8 | 2.16 | 7.7 |
| e6+every3+hp050 | start 6, every 3, hp x0.5 | 11 | 14.8 / 13 / 28 | 10.9 | 3.63 | 5.0 |
| ice9 | `--ice 9`, no variant | 0 | 21.3 / 26 / 43 (7 fights only) | 21.3 | 2.86 | 0.0 |
| skill 0.6 | `--skill 0.6`, no variant | - | no campaign reached the breach | - | - | - |

ICE 9 and skill 0.6 never get through the campaign to the boss (7 of 20 and 0 of 20 reach it), so the ICE ladder and tester proxy cannot be read from boss runs yet; the campaign win rate itself is the limiter.

### 2.3 What misses a target

- Win 6 % (target ~50 % at ICE 0, warning band 35 to 65 %).
- Turns per phase: phase 1 averages 19.4 turns (target 3 to 4; "in target" share 0.02). Phases 2 and 3 average 9.6 and 8.3, also over 4.
- Heal turns per phase up to 60 (limit 1): the boss self-heals on essentially every turn (22.5 of 23.5).
- Boss length vs other fights: the boss is not yet clearly "the longest fight". Mean 23.5 turns against builtin T4 mini-bosses 20.2 and (heuristic) 26.1; and the median boss fight (20) is the same as the T4 mini-boss mean. The bot dies at ~turn 20 with enrage step 3.35 (so the boss kills the bot, the bot does not outlast it).
- Win rate cannot reach 50 % through enrage alone: the best enrage-only variant moves 6 % to 8 % (noise). Q29 asks to tune enrage first and not shorten phases; the data say enrage in this range changes the fight's end by a few turns but not who wins.

## 3. Campaign pace and economy (`campaign_pace.md`, `economy_heat_attrition.md`)

Commands: `python tools/balance/balance.py run campaign --name <n> --ice 0 --seeds 1000:1019 -j 2 [--variant docs/balance/variants/s5_<v>.json]` (~6.2 min per run, 192 campaigns/hour). The old committed baseline (BASELINE_e2e13918) predates N1 to N22, so a fresh `camp_base` was run and used as the comparison base.

| run | override | win % | runs | deaths | raids | flatline raids | raids lost | Heat peak | minutes | fights | Sch income | Sch unspent | recruits | heals avail / used |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| camp_base | none | 20 | 48 | 22 | 6.0 | 1.50 | 4.35 | 92 | 746 | 257 | 1276 | 134 | 21 | 2.02 / 0.44 |
| camp_deathheat5 | death_heat_base 10 -> 5 | 20 | 50 | 23 | 6.0 | 1.05 | 4.40 | 94 | 787 | 270 | 1347 | 138 | 23 | 2.01 / 0.39 |
| camp_layers6 | map_layers 7 -> 6, rack [4,6] | 5 | 55 | 23 | 6.0 | 1.95 | 4.40 | 96 | 853 | 256 | 1431 | 126 | 22 | 1.71 / 0.33 |
| camp_nolostheat | lost_raid_heat 5 -> 0 | 25 | 48 | 21 | 5.6 | 1.60 | 3.95 | 88 | 747 | 254 | 1304 | 160 | 21 | 1.99 / 0.42 |
| camp_terminal40 | map_terminal_ratio 0.25 -> 0.4 | 15 | 50 | 23 | 6.2 | 1.70 | 4.80 | 92 | 778 | 261 | 1336 | 132 | 23 | 3.07 / 0.68 |
| camp_rookie25 | rookie_cost 15 -> 25 | 15 | 47 | 22 | 6.1 | 1.50 | 4.45 | 92 | 741 | 255 | 1261 | 121 | 21 | 2.04 / 0.44 |
| camp_rack75 | rack_schematics_by_tier x0.75 | 20 | 48 | 22 | 6.0 | 1.45 | 4.40 | 92 | 746 | 256 | 1128 | 116 | 21 | 2.02 / 0.42 |
| camp_sink10 | heat_purchase_amount 5 -> 10 | 25 | 49 | 22 | 5.8 | 1.60 | 4.30 | 91 | 759 | 262 | 1344 | 169 | 21 | 2.02 / 0.42 |

(Win rate is a bimodal 0 / 1 outcome over 20 seeds: one campaign = 5 points. Treat all win-rate differences above as noise unless a `CHANGED` flag says otherwise.)

Compare flags (`CMP_camp_*.md`, 90 % interval excludes 0), selected:

- layers6: layers per run -0.87 (-14 %); heals available -0.31, used -0.11; Heat at breach +16 and Heat at end +14. Raids from Heat actions +0.55. Minutes are not lower (853 vs 746): fewer layers just means more runs.
- terminal40: heals available +1.05 (+52 %) and used +0.24 (+55 %), the only config lever here that changes heal use. No win-rate change outside noise.
- deathheat5, nolostheat, rookie25, rack75, sink10: nothing outside noise at 20 seeds. Flatline raids 1.50 -> 1.05 under deathheat5 is a direction, not a proof.

What misses a target:

- Win 20 % (ICE 0 target ~50 %), loss 5 %, the rest hit the 60-run cap: median runs 60, p90 60.
- Minutes 746 mean, median 930, against the GDD 11.8 target ~395. Minutes track fights and runs; 257 fights and 22 deaths per campaign.
- Deaths per campaign 22 (21.9): each costs a run and Heat. Operatives recruited 21.
- HP on arrival at L7 is 0.46 (T1), 0.58 (T2), 0.61 (T3); heals used 0.44 of 2.02 available. The bot underuses heals, a policy fact the data cannot separate from a player behavior.
- Schematics: income 1276, spent 1162, unspent 134 (fine).
- Boss fights inside campaigns: 95 per 20 campaigns at T4 (mean 32.3 turns, win 4 %): more than 4 per campaign, because the bot loses and retries.

Netrun (D2-B), `net_t2_base` vs `net_t2_noelite` (map_elites_per_layer 0, tier 2, 20 seeds): the run is lethal today (died 100 %); with no elites died 60 %, HP on arrival at L5 to L7 rises from 0.27 / 0.22 / 0.14 to 0.68 / 0.65 / 0.56, layers 5.0 -> 5.95 (`CMP_net_t2_noelite.md`). The loss is concentrated in elite fights.

Not run (time or draft stop rules): D3 per-enemy `hp*=` outliers, `enemy_scale_per_tier` / `enemy_hp_scale_by_tier` fight sweeps (the draft's lever was replaced by N2 `hp_bands` / `hp_by_tier`, so the old sweep value is meaningless), campaign `--ice 5` combos, stacked combos, and the C/D/E campaign variants that the draft gated behind earlier results (all earlier results were noise, so the gate says do not run them).

## 4. Proposed tuning list (for the designer; nothing applied)

In the order asked: enrage defaults first, then reference DPT / bands, then the rest.

### 4.1 Enrage defaults (BOSS entry of the three class tables)

The sweeps say the enrage defaults do not control the boss win rate: start turn 6 to 14, step 10 to 50 %, every 3 to 8 turns all land in noise at 20 and 100 seeds. The fight's length is bound by the bot dying around turn 20, with the boss healing every turn. So:

1. Keep the BOSS enrage defaults as they are (10 / 5 / 25 %) until the heal and HP problems are fixed; changing them now only shifts a few turns and cannot be told from noise.
2. If the designer wants enrage to bound the fight (a hard ceiling around 30 turns), the only visible knob is a *faster* ramp: start 6 and every 3 shortens the mean to 14.8 and p90 to 28 (with hp x0.5), at the cost of operative HP at the end (-3 HP). Candidate: BOSS start 8, every 4, step 25 %. Re-measure at 100 seeds before accepting.
3. A softer enrage (start 14, every 8) is a pure loss: +1.5 turns, noise-level win rate. Do not use it as a "make the boss winnable" lever.

### 4.2 Boss HP and heal (the lever that moves the win rate)

4. `renewal_engine` HP x0.35 (about 126 at T4 from 360) gives 19 % win and p90 37 turns at 100 seeds, the only interval that excludes the baseline. It still misses 50 %. A second lever on the heal (boss heal turns are 18.6 of 19.6 turns) or on intake (5.1 HP per turn on a 60 HP operative) is needed to reach ~50 %; the sim has no heal or per-boss damage lever beyond HP and the global `enemy_damage_by_tier`. Needs a design call: boss self-heal amount or cadence (NEEDS: a data field if one does not exist).
5. Phase 1 averages 10.9 to 21.0 turns across variants against a 3-4 target. Q29 says never shorten phases; the data say phase 1 is where the problem sits (the other phases are 6 to 10 turns). Most fights end in phase 1 (97 enter it, 31 enter phase 2, 12 enter phase 3), so the fight is a phase-1 wall, not a three-phase fight.

### 4.3 Reference DPT / HP bands (Step 0)

6. Replace the rising [9, 11, 14, 18] with a measured flat band, or accept it as aspirational: the starter operative deals 14.4 to 14.9 per turn on normals at every tier. Tester-equivalent (skill 0.4 to 0.6) is 7 to 11. If the bands are tuned so a tester finishes a normal in 3 to 4 turns, `hp_band_normal` T1 (28 to 36) fits skill 0.6 (10.6 x 3.5 = 37) and the T4 band (56 to 70) is 5 to 7 times too high for any skill (8 to 12 turns at 1.0 and 0.6). Candidate: lower the T3 and T4 normal band maxima toward ~50 and ~60, then re-run S0a to S0d.
7. Elite bands T3 and T4 (88 to 112, 112 to 144) are unwinnable for a fresh operative (30 % and 0 %). Fine if the design assumes a grown operative, but then the fight sweep needs a campaign-state source (NEEDS: a `--source campaign` for `fight` mode; touches the tool, not `scripts/core`).
8. Damage table: realized taken/turn grows 1.15 / 1.32 / 1.81 against a 1.3 / 1.69 / 2.2 table. Lowering to 1.2 per tier raises T4 normal win from 97 % to 100 %; raising to 1.6 per tier drops it to 55 %. The current table is closest to the 1.6 end at T3 to T4 in effect, so it is not a safe value to raise.

### 4.4 Both wheels in one turn (Q16)

9. The share is 0.35 (builtin, skill 1.0), 0.52 (heuristic), 0.21 (skill 0.2). A strong player plays both wheels every other turn; the tester proxies play fewer. If the designer wants it to fall, the bot cannot show it: the share depends on the bot's policy, not only on content. Needs a rule-level lever (NEEDS: a cost or limit on the second wheel per turn, which touches `scripts/core`). Sweep to repeat after that: S0a, S0e.

### 4.5 Campaign pace and economy

10. Minutes: none of the seven levers moves minutes or win outside noise. The big numbers are deaths (22) and the 60-run cap. Reduce deaths first (heal use, elite HP loss; netrun without elites cuts the death rate 100 % to 60 %).
11. `map_terminal_ratio` 0.4 is the only lever that visibly changes heal supply (2.02 to 3.07 available, 0.44 to 0.68 used). Re-run at 60 seeds to see whether win moves.
12. `map_layers` 6 is worse (win 5 %, minutes 853): do not shorten the map as a pace lever.
13. `death_heat_base` 5, `lost_raid_heat` 0 and `heat_purchase_amount` 10 move flatline raids and Heat peak by a few points (inside noise at 20 seeds); not enough to justify a change.

## 5. Open items and caveats

- Win rates at n = 20 (campaign) and n = 19 (boss 20-seed screen) are bimodal; one seed = 5 points. Only the 100-seed boss runs and the explicit `CHANGED` flags carry weight.
- Fresh-operative fight calibration cannot represent T3 to T4 elites and mini-bosses; boss runs use the campaign state (rank ~5.7, 16 cards).
- Not measured: Q2 (tester proxy at the boss; skill 0.6 never reaches it), ICE ladder on boss (ICE 9 reaches it in 7 of 20), heuristic or lookahead on the boss, `--tier` netrun for tiers 1, 3, 4.
- No `NEEDS` touches `scripts/core` beyond items 4, 9; no tool change was required (the `s5_*` variant files use the existing override syntax).

## 6. How to reproduce

```
python tools/balance/balance.py run fight --name cal_builtin_s100 --enemy all --tiers 1,2,3,4 --categories enemy,elite,mini_boss --seeds 1000:1019 -j 2
python tools/balance/balance.py run boss --name boss100_base --source campaign --seeds 1000:1099 -j 2
python tools/balance/balance.py run boss --name boss100_hp035 --source campaign --seeds 1000:1099 -j 2 --variant docs/balance/variants/s5_boss_hp035.json
python tools/balance/balance.py run campaign --name camp_base --ice 0 --seeds 1000:1019 -j 2
python tools/balance/balance.py compare <A>.json <B>.json --name <n> --out docs/balance/S5_cmp/CMP_<n>.md
```
