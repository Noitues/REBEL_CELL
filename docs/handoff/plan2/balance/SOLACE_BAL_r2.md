# SOLACE_BAL_r2: Solace focus setting and Q8 campaign pace

2026-10-20, branch `sol-focus`, base main @ b1afeda0. Scope: Solace, class breaker, ICE 0, `--fast` sims. Every number names its
policy. **reference** = `--policy reference` (heuristic strategist, lookahead 2). **L1** = `--policy heuristic --lookahead 1`
(same strategist, cheaper, weaker in the boss fight). **builtin** = CombatBot. Minutes are the sim's model (15 per run + 5 per raid,
GDD 11.8). Raw reports: `D:/rc_tmp/solfocus/m2..m8` (not committed).

## 1. Solace focus setting
`CampaignConfigData.campaign_focus_corp: StringName`, shipped `&""` (all corporations). Non-empty: `RunManager.new_campaign`, the
corporation picker (`available_corporations`), and `CampaignSimulator` all use that corporation, so a playtest is Solace end to end
(its Grid and Sites, events, raids and HQ all key off `campaign.corporation_id`). One helper: `CampaignRules.focused_corporation_id`.
Other corporations' content is untouched. Tests: `test_campaign_focus_corp.gd` (off = byte-identical campaign state, on = Solace-only
Grid and picker, simulator, unknown id falls back); smoke check for the shipped default; DECISIONS "Solace focus". To use it in a
sim: `--set config.campaign_focus_corp=solace`; in the game, edit the `.tres` locally.

## 2. Where the runs went (Q8)
Reference traces on seeds 1000-1002 (old config, old policy menu), then L1 traces. The pace is not rank gating and not Site counts:
- **Structural floor is 8 runs**: three Ranks (a Rank is one full netrun; Tier 4 needs Rank 3), three Exploit Sites, the path to
  the core (`t1_a, t2_intel, t2_breach (Intel opens the lock), t1_b?, t1_c, t2_virus, t3_b`). Fast seeds hit exactly 8.
- **The tail is Heat.** The reference policy breaches only at Heat <= 10 (`breach_max_heat`). Each Exploit is +10 Heat on top of the
  run's own 8, so the crew has Heat 30+ at three Exploits. Solace has four Heat sink Sites and each cuts Heat **once**.
  The strategist's launch menu said a cleared sink still cut Heat, so it re-ran `scrub_records` 6 to 40 times with Heat flat or
  rising (patrols apply no objective). Net result on the old numbers: runs 11 to 60 (r1: 6 of 8 reference campaigns long).
- A second tail: a policy that loses the breach (L1 does most of the time) loses its best operative, re-ranks 3 runs, gains death
  Heat and crosses the Heat gate again; that is the remaining 60-run-cap seeds.
- Per run Heat is about +3 at T1 and +8 at T2; Heat purchases (25 Schematics, +10 each) were the only renewable sink.

## 3. Changes (all shipped)
| change | kind |
|---|---|
| `AgentSimulator.launch_meta`: a patrol's Heat change is 0 (test `test_agent_launch_meta.gd`) | tool (the policy's menu), not a game rule |
| `exploit_heat` 10 -> 5 | config |
| `heat_purchase_increment` 10 -> 5 | config |
| `heat_purchase_amount` 5 -> 7 (price still 25) | config |
| GDD 11.4 / 11.5 numbers and `test_campaign_config.gd` / `test_campaign_rules.gd` pins follow | docs, tests |
Tried and not shipped: Solace sink Sites at -10 / -14 (no effect: one-shot); `min_exploits_for_breach` 2 (GDD 11.7 says 3; Virus is the
garden vertical); `death_heat_base` 5 (no effect); policy `breach_max_heat` 25 / 100 (a policy knob, not game gating).

## 4. Before and after
**L1, campaign mode, ICE 0, 12 seeds (1000-1011), win = campaign won:**
| config | win % | runs mean | minutes mean | raids | seeds at 59-60 runs (the cap) |
|---|---|---|---|---|---|
| BEFORE (main) | 58 | 48.8 | 751 | 3.7 | 7 of 12 |
| exploit_heat 5 + increment 5 | 67 | 36.2 | 561 | 3.4 | 4 |
| **AFTER (shipped: + amount 7)** | **83** | **29.3** | **454** | 2.8 | 2 |
| amount 8 instead (noise check) | 58 | 36.0 | 555 | 2.9 | 5 |
Median runs: 59.5 before, 23 after. Amount 7 versus 8 versus 5 is within noise (n = 12, chaotic trajectories); 7 is the best of the
three measured and is shipped. L1 boss-mode runs to the first breach (8 seeds): 25.3 before, 10.8 after.

**Reference (lookahead 2), 4 seeds (1000-1003), 29 minute cap per seed (`--max-runs 40`):**
| | seed 1000 | 1001 | 1002 | 1003 |
|---|---|---|---|---|
| BEFORE (new policy menu, old config) | won, 15 runs | 40 runs, not won | won, 11 | 30 runs at the cap, still scrubbing |
| AFTER (shipped) | won, 11 runs | won, 9 | won, 9 | 13 runs at the cap, in breach attempts |
After: the three finished campaigns are 9 to 11 runs (about 135 to 180 minutes, GDD "fast campaign" 8 runs / 135 min). The 24-run
average is therefore not what the reference policy shows; it is what the lookahead-1 policy shows (29 runs, 454 min). Note that an HQ
ladder breach that hits the sim's per-run step cap appears to end with outcome NONE and be relaunched, so each ladder costs the sim 1 to 3 runs.

**Win % at ICE 0 (TARGETS bands):**
- Boss, reference: unchanged mechanics. The reference policy still breaches only at Heat <= 10 (breach Heat after: 0 to 3 on the
  three won seeds), so the boss fight sees the same Heat band as before. SOLACE_BAL_r1's 52 % (n = 50, saved states) stands; not
  re-sampled at n >= 50 (hours of CPU).
- Builtin campaign floor (`--policy builtin --fast`, 20 seeds, shipped config): **25 % win** (floor 25 %: met, at the line), runs 50.0,
  minutes 778, deaths 13.5. The floor is the boss stall of Q9; Heat does not move it.

## CALLS
1. Pace is anchored on lookahead 1 (average-skill proxy), not on the reference: the reference is an expert and now plays the GDD's
   fast campaign (9 to 11 runs). Designer: confirm, or supply tester data (BAL-02) for the 24-run anchor.
2. The launch-menu fix is a tool change that alters every earlier reference campaign number (r1's 45 runs / 700 min was the bugged menu).
3. Three Heat numbers changed in config (and GDD 11.4 / 11.5, which marks them "tune in playtest"); sinks, `min_exploits_for_breach`
   and rank rewards (class content) untouched.
4. `amount` 7 chosen on 12 L1 seeds; the sample cannot separate 7 from 8.

## Still open
- Weak-boss spirals (lookahead 1 at the 60-run cap), the HQ ladder `NONE` relaunches, and the reference boss win at n >= 50 after the Heat change.
