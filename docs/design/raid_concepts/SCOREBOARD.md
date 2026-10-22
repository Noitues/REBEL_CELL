# Raid concepts: scoreboard

A fresh Opus critic scores each round. No critic sees earlier reviews or scores. The rubric is fixed (1–10 per axis):
1. **W** — what / why / when.
2. **P** — outcome predictability.
3. **N** — no-words test (scrambled frames).
4. **D** — decision depth.
5. **C** — consequences.

Phase 3 adds **V**, visual quality against AAA. The full reviews are in `_reviews/`. The critics' comparison sheets
(they use third-party screenshots, so they stay out of the repo) are in `D:/rc_tmp/raid_design_lab/critic_r<N>/`.

## Round 1: divergent concepts (low-fidelity PIL mockups, hand-set numbers)

| Concept | W | P | N | D | C | Total /50 |
|---|---|---|---|---|---|---|
| A Telegraph | 8 | 8 | 7 | 6 | 7 | **36** |
| B Siege Lanes | 8 | 6 | 6 | 6 | 8 | **34** |
| E Countdown + Allocation | 9 | 4 | 6 | 6 | 6 | **31** |
| D Auto-battler Loadout | 6 | 4 | 8 | 7 | 4 | **29** |
| C Strength Duel | 7 | 6 | 7 | 3 | 5 | **28** |
| F Plan Ledger | 7 | 6 | 3 | 6 | 4 | **26** |

- **Critic's pick:** A as the base, B second. Their ideas will likely merge.
- **Cross-cutting fault:** the hand-set mockup numbers contradicted themselves in A, C, D, E and F.
- **Response:** in round 2, every number is computed by a rule or by the resolver-mirror sim.

## Round 2: every concept reworked on R1 findings (numbers from code: sim.py or a rule function)

| Concept | W | P | N | D | C | Total /50 | Δ vs R1 |
|---|---|---|---|---|---|---|---|
| A Telegraph | 8 | 8 | 7 | 6 | 6 | **35** | −1 |
| B Siege Lanes | 8 | 6 | 6 | 6 | 8 | **34** | 0 |
| D Auto-battler | 7 | 7 | 7 | 6 | 5 | 32 | +3 |
| E Countdown | 9 | 7 | 6 | 4 | 6 | 32 | +1 |
| F Plan Ledger | 7 | 7 | 6 | 5 | 7 | 32 | +6 |
| C Strength Duel | 7 | 4 | 6 | 5 | 4 | 26 | −2 |

- **The critic's pick:** merge A (base) and B.
  - **From B:** the reach rings and the "next raid" frame.
  - **From F:** the path rows on the warning card.
  - **From E:** the countdown on the netrun map.
  - **From D:** the per-threat strip as a hover.
- **Its main finding:** the ceiling now sits in the **rules**, not the UI. The issues it lists:
  - Decoy routing can pass through home, with ties broken alphabetically.
  - "Clean" is defined three ways.
  - SCUFFED has no price.
  - Cascades are drawn nowhere.
  - No clean defense exists in the scenario.
- **Next:** round 3 merges A and B and tests those rule fixes as designer-decision options in `sim.py`.

## Round 3 (every concept under the rule package; fresh critic; `_reviews/REVIEW_R3.md`)

| Concept | W | P | N | D | C | Total |
|---|---|---|---|---|---|---|
| **G Merged** | 8 | 7 | 6 | 6 | 8 | **35** |
| E Countdown | 8 | 5 | 5 | 7 | 5 | 30 |
| D Auto-battler | 6 | 7 | 6 | 4 | 5 | 28 |
| F Plan Ledger | 6 | 7 | 6 | 5 | 4 | 28 |
| C Strength Duel | 6 | 5 | 4 | 5 | 5 | 25 |

- **The critic's pick:** take G forward, with E's two-visit countdown and its priced sacrifice. Build G as the playable
  prototype.
- **The ceiling has not moved (35).** The critic names 13 barriers, all designer decisions:
  - the D27 Heat payout and its all-or-nothing reward;
  - SCUFFED counted as clean while the patch can exceed the payout;
  - D26 pacing with only 4 steps;
  - D28 verdicts;
  - cobalt contrast;
  - undrawn cascades;
  - the hidden crew ×1.5;
  - icon silhouettes;
  - content scale;
  - a blind draft;
  - when the raid lands.

  Round 4 challenges them on G.
