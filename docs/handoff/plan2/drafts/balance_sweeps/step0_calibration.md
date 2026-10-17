<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01PDEyQB42bgSjCYUK2iMTqj, custom_id bsweep__step0_calibration; status ok; tokens in 25920 cache-write 32585 cache-read 0 out 4022; cost $0.087. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# balance sweeps: Step 0 calibration (reference_dpt_by_tier, HP bands, tier tables)

## 1. Question and hypotheses

**Question:** what damage per turn does a realistic player deal at each tier (T1-T4), and how does that spread across policy and skill? The answer sets `reference_dpt_by_tier` (proposed [9, 11, 14, 18]) and the HP bands. It also tells N2 what to author for `hp_by_tier` and `enemy_damage_by_tier` (proposed [1.0, 1.3, 1.69, 2.2]).

Baseline reference points: builtin skill 1.0 deals about 16-20 dealt/turn on normals, 30-39 on the Claims Adjuster, and 11-14 on the Recall Unit at T3-T4. Testers deal 3.2-5.0 per turn (per the V2 text).

- **H1:** dealt/turn falls roughly linearly with skill. Skill 0.2 gives 3-6, skill 0.6 gives 8-12, and builtin 1.0 gives 16-20. Direction: monotonic. Size: skill 0.6 lands close to the proposed [9, 11, 14, 18] midpoint, within ±3.
- **H2:** dealt/turn drops with tier at fixed skill, because high-tier enemy HP and defense absorb more (baseline normals: 17.7 at T1 vs 16.5 at T4; Recall Unit 16.6 → 11.7). Expected drop is 0-30 %, concentrated on sustain enemies. A reference rising [9..18] across tiers is therefore not supported by the policy; it only holds if the operative grows with rank. The sim uses a starter operative, so that growth is not measured. Flag this in the write-up.
- **H3:** heuristic (lookahead 1, 2) deals ≥ builtin on the same seeds, by 0-25 %.
- **H4:** the turn target of 3-4 turns per phase (3.5) at the mid-skill tester is infeasible with today's HP. Today's T3 normal at skill 0.6 should run about 9-12 turns against a 3.5 target.
- **H5:** the damage-scale mismatch (config 1.3 vs GDD 1.2 vs schema 1.6) shows up as taken/turn growth per tier. Baseline: Collections Agent 1.79 → 2.60 → 2.78 → 3.79 (T1→T4 is ×2.1), versus 1.3^3 = 2.2. Expect the observed ratio to stay at 2.0-2.3 across skills.

## 2. Sweep table

Shared flags: `--corp solace --class breaker --ice 0` are the defaults. All runs use `-j 2`, seeds 1000:1019 (20 seeds), `--fast` omitted so per-fight pools are kept.

| id | mode | command | variants | seeds | wall | metric | decision rule |
|---|---|---|---|---|---|---|---|
| S0a | fight | `python tools/balance/balance.py run fight --name cal_builtin_s100 --enemy all --tiers 1,2,3,4 --categories enemy,elite,mini_boss --seeds 1000:1019 -j 2` | none | 20 | ~125 s (equals the baseline sweep) | dealt/turn, turns, taken/turn, win % per enemy × tier | Must match BASELINE fight sweep exactly (sanity). Mismatch means the tool changed; stop. |
| S0b | fight | `... --name cal_builtin_s060 --skill 0.6 ...` (otherwise S0a) | none | 20 | ~130 s | same | H1: pooled dealt/turn at 0.6 within 8-12. |
| S0c | fight | `... --name cal_builtin_s040 --skill 0.4 ...` | none | 20 | ~130 s | same | H1: 5-9. |
| S0d | fight | `... --name cal_builtin_s020 --skill 0.2 ...` | none | 20 | ~130 s | same | H1: 3-6; the tester band is 3.2-5.0, so 0.2-0.3 maps to testers. |
| S0e | fight | `... --name cal_heur1_s100 --policy heuristic --lookahead 1 ...` | none | 20 | ~3-6 min (unmeasured) | same | H3: vs S0a, compare. If ≤ builtin, builtin is the ceiling. |
| S0f | fight | `... --name cal_heur2_s100 --policy heuristic --lookahead 2 --seeds 1000:1009 ...` | none | 10 | ~5-15 min | same | H3 and "is it a puzzle" ceiling. |
| S0g | fight | `... --name cal_heur1_s060 --policy heuristic --lookahead 1 --skill 0.6 --seeds 1000:1009 ...` | none | 10 | ~3 min | same | Checks whether skill scales the same on heuristic. |
| S0h | fight | `python tools/balance/balance.py run fight --name cal_det_s100_rerun --enemy all --tiers 1,2,3,4 --seeds 1000:1019 -j 2` | none | 20 | ~125 s | whole JSON | Determinism: `cmp docs/balance/runs/cal_builtin_s100.json docs/balance/runs/cal_det_s100_rerun.json` must be byte-identical. Repeat with `-j 1` against S0a. |
| S0i | fight | `... --name cal_det_s060_rerun --skill 0.6 ...` | none | 20 | ~130 s | whole JSON | Determinism with the skill RNG (random legal actions). Must equal S0b. |
| S0j | fight | `... --name cal_scale_probe --enemy collections_agent,compliance_officer,billing_daemon --tiers 1,2,3,4 --variant docs/balance/variants/cal_damage_table.json` | cal_damage_table | 20 | ~20 s | taken/turn per tier | H5: the override reproduces the target table; check `enemy_damage_scale_per_tier` is honored. Rejects if taken/turn doesn't change. |

Record in every run (already in the S2 schema): per-fight turns, dealt/turn, taken/turn, HP lost, Perfect %, heal turns, win %. Derive N2 inputs from the JSON (offline, no new levers):
- **dpt_ref[t]** = pooled median dealt/turn over normals at tier t, per policy/skill.
- **hp_by_tier[e][t]** = dpt_ref[t] × 3.5 × needle share (class phase count) + sustain; compare to today's HP per enemy.
- **damage factor[t]** = taken/turn[t] ÷ taken/turn[1] per enemy, against 1.3^(t−1).

## 3. Variant files

`docs/balance/variants/cal_damage_table.json`, a diagnostic that sets the tier damage factor to the V2 table. `enemy_damage_by_tier` is a **new** field and does not exist: **NO LEVER: enemy_damage_by_tier / hp_by_tier / reference_dpt_by_tier / hp_bands.** The nearest existing lever is a scalar, so S0j probes with that:

```json
{"name": "cal_damage_table", "set": ["config.enemy_damage_scale_per_tier=1.3"]}
```

This changes nothing (it is the current value). It is a no-op control for the override path. Run it only as the determinism and override control; an A/B vs S0a must show zero delta. To test the GDD value, a second file:

`docs/balance/variants/cal_damage_12.json`
```json
{"name": "cal_damage_12", "set": ["config.enemy_damage_scale_per_tier=1.2"]}
```

Use it as `--variant docs/balance/variants/cal_damage_12.json` in S0j (replace the control). Expected: T4 taken/turn falls by about 1.3^3/1.2^3 = 1.27× (−21 %).

## 4. Order and stop rules

1. S0a and S0h first (about 4 min). If the two JSON files differ, stop; fix determinism before anything else.
2. S0b, S0i (skill 0.6 and its rerun). If they differ, stop; the skill RNG is not seeded.
3. S0c, S0d. Skip S0c if S0b and S0d are already near-linear (the midpoint is predictable).
4. S0e, then S0g.
5. S0f only if S0e shows heuristic beats builtin by more than 10 %.
6. S0j last, 1.2 vs control.

Stop after S0a-S0d if pooled dealt/turn is flat across skill (spread < 20 %); then the skill knob is not a usable tester proxy, and the answer to question 1 would need a different lever (**NO LEVER: tester-equivalent bot beyond --skill**).

Other-corporation fights: a `--corp` flag exists, but only Solace enemies are in the baseline. After S0 passes, repeat S0a and S0b once per corp (4 more runs, about 2 min each) to extend the calibration.

## 5. Compare plan

| pair | output | what it reads |
|---|---|---|
| cal_builtin_s100 vs cal_builtin_s060 | CMP_cal_skill_100_060.md | skill effect on dealt/turn and turns |
| cal_builtin_s060 vs cal_builtin_s020 | CMP_cal_skill_060_020.md | tester band |
| cal_builtin_s100 vs cal_heur1_s100 | CMP_cal_policy_heur1.md | policy ceiling |
| cal_builtin_s100 vs cal_heur2_s100 | CMP_cal_policy_heur2.md | lookahead (only if S0f run; seeds overlap 1000:1009) |
| cal_builtin_s100 vs BASELINE_e2e13918 fight sweep | CMP_cal_vs_baseline.md | sanity, expected all "noise" |

## 6. Options write-up skeleton (BALANCE_OPTIONS.md)

- **Step 0 calibration: measured dealt/turn by tier × policy × skill** (table from S0a-S0g).
- **Option A: reference_dpt_by_tier = [9, 11, 14, 18]** (midpoint; fight turns predicted per class).
- **Option B: tester-tuned** (the S0d/S0c numbers; resulting hp bands per class and tier).
- **Option C: bot-tuned** (S0a/S0f ceiling; the same).
- **HP bands implied per option** (normal / elite / mini-boss / boss; T1-T4).
- **Damage table fit:** observed taken/turn ratios vs 1.2 / 1.3 / 1.6 (S0j).
- **Caveat:** starter operative only; no rank growth.
- **Determinism result** (S0h/S0i).
- **Recommendation and risks.**

## 7. Q:

- Q: Is the starter operative (fresh, rank 0) the right reference at T3-T4, or should the calibration use a campaign-state operative? The fight mode cannot supply one (**NO LEVER: fight mode from a campaign state**).
- Q: Which skill values map to "tester"? Proposed 0.2-0.3 from the 3.2-5.0 dealt/turn figure; do you want a tester session to confirm?
- Q: Should calibration also be run for Perfect-rate-limited play (testers hit 15-25 % Perfect vs the bot's ~90 %)? There is no data lever for that; `--skill` is the only proxy.
- Q: Add `hp_by_tier`, `enemy_damage_by_tier` and `reference_dpt_by_tier` to the data first (N2) so later sweeps can set them, or keep the sweeps measuring only?
