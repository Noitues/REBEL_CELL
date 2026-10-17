<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01PDEyQB42bgSjCYUK2iMTqj, custom_id bsweep__economy_heat_attrition; status ok; tokens in 25862 cache-write 0 cache-read 32585 out 4554; cost $0.052. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# balance sweeps: D2 attrition, D3 fight length, D5 flatline Heat, D6 Schematics economy

Baseline reference: BASELINE_e2e13918 (builtin bot, skill 1.0, breaker vs Solace, ICE 0, seeds 1000:1019). Every sweep uses `-j 2`. The sweeps measure only and edit no files.

## 1. Question and hypotheses

**D2 (HP attrition).** HP on arrival falls from 1.00 at L1 to about 0.59 at L7. Heals available are 1.94 per run and used 0.37.
- **H2a:** the bot rarely routes to or uses Terminal heals. Raising heal strength should move heals used only a little (+0.1) because the use-rate, not the heal size, is the bottleneck. NO LEVER: heal node frequency (`map_terminal_ratio` is the closest; it covers all events).
- **H2b:** raising `map_terminal_ratio` from 0.25 to 0.40 gives about +0.5 heals available and raises L7 HP by about 0.04–0.06.
- **H2c:** removing the Mainframe floor and the shop-stock Heat penalty has no direct effect on HP. Skipped.
- **H2d:** attrition comes mostly from elites and mini-bosses (6–10 HP each), so fewer elites (`map_elites_per_layer` 1→0 for T1 comparison) lifts L7 HP by about 0.10. This tests where the loss comes from rather than proposing it as a fix.
- NO LEVER: heal amount per Terminal event. It lives in event content, not config.

**D3 (fight length, enemy self-heal).** Normal fights run about 2.5–3.8 turns in campaigns and elites run 7.5 at T3. The long ones are Recall Unit T3/T4 (20/36 turns), Account Manager (21/31) and the boss (41–50).
- **H3a:** enemy HP is the main driver. `enemy_scale_per_tier` 1.6→1.4 cuts T3 fights by about 25 %, and T4 elite win rates rise from 75 % to 90 %.
- **H3b:** `enemy_damage_scale_per_tier` 1.3→1.2 (the GDD value) lowers HP lost per fight by about 15 % at T3.
- **H3c:** self-heal is a minor driver except for Triage Unit (3.9 heal turns at T4). Lowering `triage_unit` HP, or its heal, shortens it by about 25 %. NO LEVER: heal amount as a standalone property; test via per-enemy `hp`.
- Boss length: `renewal_engine.hp` ×0.5 is expected to give about 20 turns.

**D5 (flatline Heat).** 0.75 raids per campaign come from flatline Heat (Heat that death alone pushed over a threshold), and the Heat peak is 84. Death Heat is `death_heat_base` 10 plus tier.
- **H5a:** `death_heat_base` 10→5 halves flatline raids to about 0.4 and drops the peak by 5–8.
- **H5b:** `lost_raid_heat` 5→0 removes a feedback loop (3.6 raids lost per campaign, about 18 Heat). The peak drops by about 10, with fewer raids from actions.
- **H5c:** `heat_purchase_amount` 5→10 lets the bot cut Heat faster. Heat at breach falls by about 5.

**D6 (Schematics).** Income is 1410, spent 1238 and unspent 191. Recruits average 10.2 per campaign at `rookie_cost` 15, driven by 10.5 deaths.
- **H6a:** `rookie_cost` 15→25 cuts recruits by about 20 % and leaves more unspent (+100). Its cost-effect shows up as win rate.
- **H6b:** `rack_schematics_by_tier` ×0.75 lowers income by about 20 % and brings unspent to about 100.
- **H6c:** `node_base_cost` 20→15 raises spending and shrinks unspent.

## 2. Sweep table

Campaign wall time: about 20–60 s per seed. 20 seeds at -j 2 is roughly 10–20 min, matching the baseline of 745 s. Fight and netrun runs are minutes.

| id | mode | command | variants | seeds | wall | metric | decision rule |
|---|---|---|---|---|---|---|---|
| D2-A | campaign | `balance.py run campaign --name d2_terminal40 --ice 0 --seeds 1000:1019 -j 2 --variant docs/balance/variants/d2_terminal40.json` | d2_terminal40 | 20 | 13 min | heals available/used, L7 HP T1–T3, deaths, win % | confirm if heals available ≥ 2.4 and L7 HP ≥ +0.04 over baseline |
| D2-B | netrun | `balance.py run netrun --name d2_noelite --tier 2 --seeds 1000:1019 -j 2 --variant docs/balance/variants/d2_noelite.json` | d2_noelite | 20 | 1 min | HP at end, death rate, L4–L7 arrival | diagnostic: HP loss share from elites. Compare against netrun@t2 baseline (death 60 %). |
| D2-C | campaign | `... --name d2_terminal40_elite1 ...` | d2_terminal40 plus `config.elite_heat=0` | 20 | 13 min | L7 HP, Heat peak | only if D2-A passes; checks the Heat side-effect |
| D3-A | fight | `balance.py run fight --name d3_scale14 --enemy all --tiers 1,2,3,4 --seeds 1000:1019 -j 2 --variant docs/balance/variants/d3_scale14.json` | d3_scale14 | 20 | 2 min | turns mean/p90 by category and tier, win % | confirm if T3 elite turns ≤ 11 (from 14.5) and T4 win ≥ 85 % |
| D3-B | fight | `... --name d3_dmg12 ... --variant d3_dmg12.json` | d3_dmg12 | 20 | 2 min | HP lost mean, win % | confirm if HP lost at T3 drops ≥ 10 % with turns unchanged |
| D3-C | fight | `... --name d3_outliers --enemy recall_unit,account_manager,triage_unit,care_swarm --tiers 3,4 ... --variant d3_outliers.json` | d3_outliers | 20 | 1 min | turns, heal turns, win % | confirm if each lands in 8–14 turns at T3 |
| D3-D | boss | `balance.py run boss --name d3_boss --source fresh --seeds 1000:1007 -j 2 --variant docs/balance/variants/d3_boss.json` | d3_boss | 8 | 3 min | total turns, win %, turns per phase | confirm if turns ≤ 25 and win rate ≥ 40 % |
| D5-A | campaign | `... --name d5_death5 ... --variant d5_death5.json` | d5_death5 | 20 | 13 min | raids from flatline, Heat peak, raids total, win % | confirm if flatline raids ≤ 0.4 and peak ≤ 78 |
| D5-B | campaign | `... --name d5_nolostheat ...` | d5_nolostheat | 20 | 13 min | Heat peak, raids lost, raids from actions | confirm if peak drops ≥ 8 |
| D5-C | campaign | `... --name d5_sink10 ...` | d5_sink10 | 20 | 13 min | Heat at breach, Heat curve | confirm if breach Heat ≤ 50 |
| D6-A | campaign | `... --name d6_rookie25 ...` | d6_rookie25 | 20 | 13 min | recruits, unspent, win %, deaths | read the recruit-count drop and win-rate change |
| D6-B | campaign | `... --name d6_rack75 ...` | d6_rack75 | 20 | 13 min | income, unspent, win % | confirm if unspent ≤ 120 with win rate within noise |
| D6-C | campaign | `... --name d6_node15 ...` | d6_node15 | 20 | 13 min | spent, unspent | confirm if unspent ≤ 120 |

## 3. Variant files

All use property paths under `config.`. The per-enemy `hp` path assumes `EnemyData.hp`; the `ground_control.hp=40` example in the tool header confirms the form.

- `d2_terminal40.json`: `{"set": ["config.map_terminal_ratio=0.4"]}`
- `d2_noelite.json`: `{"set": ["config.map_elites_per_layer=0"]}`
- `d3_scale14.json`: `{"set": ["config.enemy_scale_per_tier=1.4"]}`
- `d3_dmg12.json`: `{"set": ["config.enemy_damage_scale_per_tier=1.2"]}`
- `d3_outliers.json`: `{"set": ["recall_unit.hp*=0.7", "account_manager.hp*=0.7", "triage_unit.hp*=0.8", "care_swarm.hp*=0.8"]}`
- `d3_boss.json`: `{"set": ["renewal_engine.hp*=0.5"]}`
- `d5_death5.json`: `{"set": ["config.death_heat_base=5"]}`
- `d5_nolostheat.json`: `{"set": ["config.lost_raid_heat=0"]}`
- `d5_sink10.json`: `{"set": ["config.heat_purchase_amount=10"]}`
- `d6_rookie25.json`: `{"set": ["config.rookie_cost=25"]}`
- `d6_rack75.json`: `{"set": ["config.rack_schematics_by_tier*=0.75"]}`
- `d6_node15.json`: `{"set": ["config.node_base_cost=15"]}`

NO LEVER: heal amount per Terminal event or Hub heal, and the care_swarm lethality knob other than HP. NO LEVER: bot heal-routing preference (a policy change, not data).

## 4. Order and stop rules

1. **Fight sweeps first** (D3-A, B, C, D). They take minutes in total, and the T3/T4 results set the HP assumptions for everything else.
2. **Netrun D2-B**, 1 minute.
3. **Campaign sweeps**, one at a time at -j 2, in this order: D5-A, D2-A, D6-A, D5-B, D6-B, D3 combined. Run D5-C, D6-C and D2-C only if the earlier result in the same issue is within noise or the direction is unclear.
4. **Stop rule:** if a campaign variant moves win rate by less than the 90 % interval, flag it as noise and do not run the follow-ups for that issue.
5. **Combined run:** after the single-lever runs, one campaign with the best lever per issue stacked (`d3_scale14` + `d5_death5` + `d2_terminal40`). If its minutes do not fall toward 395 (baseline 605), report that as a finding.

## 5. Compare plan

Baseline JSON: `docs/balance/BASELINE_e2e13918/campaign_ice0.json`. Names below assume matching baseline file names.

- `compare <baseline> d2_terminal40.json --name D2_terminal40`
- `compare <baseline> d3_scale14.json --name D3_scale14`
- `compare <baseline> d3_dmg12.json --name D3_dmg12`
- `compare <baseline> d5_death5.json --name D5_death5`
- `compare d5_death5.json d5_nolostheat.json --name D5_death5_vs_nolost`
- `compare <baseline> d6_rookie25.json --name D6_rookie25`
- `compare <baseline> d6_rack75.json --name D6_rack75`
- Stacked: `compare <baseline> stacked.json --name STACK`

## 6. Options write-up skeleton (BALANCE_OPTIONS.md)

- Issue (D2 / D3 / D5 / D6)
  - Baseline numbers (from the baseline file)
  - Diagnosis (hypothesis confirmed or rejected, with CI)
  - Option A / B / C: lever, value, measured deltas (metric, delta, 90 % interval, noise flag), side effects (win rate, minutes, Heat peak)
  - Recommended option and reason
  - NO LEVER items (need code or content work)
- Stacked result and minutes against 395
- Open items for the designer

## 7. Q:

- Q: Is the policy gap (the bot using 0.37 of 1.94 heals) a bot limitation or a real player behavior? If it is a bot limit, D2 may need no content change at all.
- Q: Should the fight-length targets follow R1 (normal 3–4 turns, elite 6–8) instead of today's campaign numbers? Phase work will supersede the HP-scale sweeps.
- Q: Is a win rate near 50 % at ICE 0 the intended target, or should the D5/D6 levers aim higher?
- Q: Are raids from flatline Heat considered a bug (remove `death_heat_base` effect) or a pressure feature (keep)?
