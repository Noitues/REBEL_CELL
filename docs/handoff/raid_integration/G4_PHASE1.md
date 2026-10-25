# Phase 1: the Infected Tide with real numbers, the port spec and the golden (designer 2026-10-25: "Proceed")

**Rulings:** docs/DECISIONS.md, the 2026-10-25 entry "Solace raid: the Infected Tide" (R-A to R-H; D and F revised).
Design: docs/design/raid_concepts/INTEGRATION_DECISION.md. Oracle: tools/raid_concepts/sweep_g1.py, variant H3 (see
G3_RESULTS.md).

## 1. Re-measure with the real game numbers (variant H4 in sweep_g1.py; keep H3 reproducible)
- **HOME:**
  - Use the game's integrity and damage from content/config/campaign_config.tres via scripts/data/campaign_config_data.gd:
    the Home integrity, `raid_home_hit_damage`, and the repair prices (`home_repair_price`; repair rules in
    campaign_rules.gd).
  - Replace HOME 3 pips and PATCH 8.
  - Map "bank" to the real campaign currency where the game uses one. Check GDD §11: Schematics are the campaign
    currency, Cycles the netrun currency.
- **Solace content:**
  - Site values and tiers, exploits, links and locked links, Heat per claim and objectives, from
    content/corporations/solace.tres and GDD §4.1, §4.3 and §11.5.
  - Use the real Heat thresholds (25 / 50 / 75 / 100) for the extra beams and the extra hand cards.
- **R-D, the virus front:**
  - Model a netrun's risk: each INFECTED card starts the street virus front one step closer.
  - Read scripts/core/netrun_session.gd bloom_* and bloom_rules.gd for what "one step" means.
  - Abstract it as a per-netrun failure chance, so a failed netrun is a death: no claim, plus the death Heat
    (heat_rules death_heat). The chance rises with front distance. Pick a monotone curve with a clear assumption.
  - Calibrate against scripts/core/campaign_simulator.gd if a cheap hook exists; otherwise state the curve as
    assumed.
- **R-F, the final netrun:**
  - The campaign ends by breaching the Genome Core once 3 exploits are held.
  - Its success chance falls with the INFECTED count at the breach (the final run's strength). Use an assumed curve:
    the base success from today's boss balance if documented, otherwise 0.85, minus k per INFECTED card.
  - Win = a successful breach. There is no purge.
  - Doses are antidote samples: each cures one INFECTED card or district.
- **R-E:** CITY LOST happens when INFECTED cards outnumber healthy cards.
- **R-G:** no step infection and no tide timer.
- **R-H:** DECAY, a DOWN Site goes TAKEN at the next raid.
- **Campaign length:** free. A campaign ends at the breach, CITY LOST, BREACHED, or a cap of 30 netruns.
- **Policies:** the claim policies as before, plus a "breach when ready" decision.
- **Targets (keep tuning within the rulings; flag any target that needs a rule change):**
  - skilled loss 5–15 %;
  - careless loss 55–85 %;
  - win 35–60 %;
  - locked at plan ≤ 0.5;
  - response decides ≥ 0.4;
  - HOME hit 0.15–0.30;
  - raids per netrun about 0.33–0.5;
  - median campaign of 12–20 netruns.
- **Also report** the INFECTED count at the breach (distribution) and its effect on the final-run success.

## 2. The port spec: docs/handoff/raid_integration/SOLACE_RAID_SPEC.md
Freeze the H4 rule set as the contract for the GDScript port into scripts/core. Follow the style of
docs/handoff/raid_lab_l8/GD_CONTRACT.md and L14_RULES.md, and cover:
- the data shapes: board graph, lines, deck and cards, INFECTED, doses;
- every phase in order;
- the corp path rule (P-target) and the corp's B lean;
- the responses;
- the tiers and verdict words (CELL HOLDS / BREACHED / CITY LOST, plus the raid tiers);
- the seeds and RNG streams: name RngService streams; no global randi;
- every config key with its default, all new keys going in campaign_config (no magic numbers);
- which existing scripts each part touches or replaces (raid_resolver.gd stays for the other corps behind a per-corp
  switch);
- the save fields;
- the tests the port needs: preview equals result; seeded replays match; golden parity.

## 3. The golden: tools/raid_concepts/solace_raid_golden.py → tools/raid_concepts/data/solace_raid_golden.json
- Seeded Solace campaigns, step by step:
  - the state before and after each phase;
  - the lines drawn;
  - the hand;
  - the placement;
  - the response;
  - the trace;
  - the tiers;
  - the INFECTED changes;
  - the between choices.
- Plus random legal raids, as in tools/raid_concepts/l8_golden.py.
- The future port's parity check reads it.

## Rules
- Write only in tools/raid_concepts/, docs/handoff/raid_integration/ and docs/design/raid_concepts/G4_RESULTS.md
  (the table, assumptions and tuning).
- Never edit scripts/, content/, scenes/ or GDD.md.
- No commits.
