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

## Round 4 (G4 alone; fresh critic; `_reviews/REVIEW_R4.md`)
| Concept | W | P | N | D | C | Total |
|---|---|---|---|---|---|---|
| G4 | 7 | 7 | 6 | 5 | 7 | 32 |

- **What the critic confirmed:** the telegraph contract now works.
- **What it rejected:** the depth claim. The next-raid trade-off ignored patching, used the wrong roster, and was fed by a misleading draft preview. It also found a rounding mismatch with the game (`roundi`).
- **Round 5 (G5):** fixes all of these and is rendered in `g_merged_telegraph/r5/`. It is kept as the calibration anchor for round 6, not scored on its own.
- **Plateau finding:**
  - The best score has run 36, 35, 35, 32 over four rounds. Decision depth never got past 7.
  - The sweep finds a single best answer per raid.
  - The real Heat-75 raid has 0.34 % clean plans, best net +2 (`r5_marginal.json`).
  - The user chose a divergent round 6: three new cores aimed at decision depth, scored next to G5 by two independent critics.

## Round 6 (two independent fresh critics; G5 as the anchor; `_reviews/REVIEW_R6A.md`, `REVIEW_R6B.md`)

| Concept | Critic A (W P N D C) | A total | Critic B (W P N D C) | B total | Mean |
|---|---|---|---|---|---|
| **H Bastion** | 7 6 6 6 7 | 32 | 8 6 6 6 7 | 33 | **32.5** |
| G5 (anchor) | 8 8 6 4 7 | 33 | 7 8 6 4 6 | 31 | 32 |
| HP | 7 6 5 6 8 | 32 | 8 5 5 6 7 | 31 | 31.5 |
| P Stakes | 7 5 6 6 7 | 31 | 7 5 5 7 7 | 31 | 31 |

- **Depth rose from 4 to 6–7, as measured in code.** Predictability fell to 5–6 on consistency errors:
  - P's patch ignores DOWN/TAKEN.
  - H's shop forecast hides the payoff: −33 vs −35 shown, against a real 34 vs −3.
  - A CLEAN raid at net −1.
  - The Lockdown link is drawn teal.
- **Both critics chose H** as the base and the first prototype, with P's node jobs and the carry rule.
- **Both say G's draft coins and its top-3 list are solver output.** G4's depth claim had already failed for related reasons.
- **Round 7 (H7)** takes the fixes both agree on.

## Round 8: pitches, kill tests, Manhunt

**Pitch critic** (one paragraph per pitch; the score is the expected score "if executed well"):

| Pitch | Score |
|---|---|
| Pursuit | 39 |
| Ring Pursuit | 38 |
| Ghost | 37 |
| Bastion H7 | 35 |
| Rack | 34 |
| Ring Siege | 33 |
| Honeypot | 33 |
| Offer | 30 |
| Counterstrike | 30 |
| Mirror | 29 |
| Signal | 28 |
| Deck | 26 |

**Kill tests** (details in MEASURE_R8.md):
- Ring Siege passes: about 9.5 viable layouts per raid and a skill gap of 53.
- Pursuit's routing passes, but its catches fail: the best line averages 0–1.4 per campaign.
- Ghost passes: the greedy rule is best on only 13% of networks.

**Manhunt (Pursuit + Ghost), mocked, one fresh critic:**

| Concept | W | P | N | D | C | Total | Fit | V |
|---|---|---|---|---|---|---|---|---|
| M8 Manhunt | 6 | 7 | 6 | 6 | 5 | **30** | 6 | 4 |

**The critic's reasons:**
- The playout replays an answer the exact forecast already showed.
- Contact runs on a fixed clock, so Heat isn't the cause.
- Losses are a small tax with no failure state.

**The finding: the pitch scored 39, the mockup 30.** Every mocked raid since R3 has landed at 30–36. With a fully
forecast, hands-off raid, P and D trade off against each other: a known outcome has no suspense, and a hidden
outcome breaks predictability.

## Round 9: suspense variants and the Spinner (one fresh critic)

| Concept | W | P | N | D | C | Total | Fit | V | S (suspense) |
|---|---|---|---|---|---|---|---|---|---|
| M9a sealed beam, zero input | 6 | 8 | 5 | 5 | 6 | 30 | 6 | 5 | 5 |
| M9b timed spoof | 6 | 7 | 6 | 4 | 6 | 29 | 6 | 5 | 6 |
| **M9c sealed + reactive spoof** (critic's pick) | 6 | 7 | 4 | 7 | 6 | 30 | 6 | 5 | **7** |
| S9 Spinner ring siege + snap | 7 | 6 | 6 | 6 | 5 | 30 | 7 | 6 | 6 |

- **Suspense and depth rose where predicted.** M9c's reactive press got D 7 and S 7, the first 7 on suspense.
- **The total did not move.** No-words and consequences fell on presentation errors:
  - colliding number sets;
  - hidden missed values;
  - a CLEAN stamp over five survivors;
  - one X glyph for two meanings.
- **The Spinner** breaks GDD pillar 4 (wheel mechanics only in combat), a designer decision. Its stakes are flat.

## H7 Godot lab (playable, real captures; one fresh critic)

| W | P | N | D | C | Total | Fit | V | S |
|---|---|---|---|---|---|---|---|---|
| 6 | 9 | 4 | 4 | 5 | 28 | 4 | 2 | 2 |

**The exact forecast gives P 9 but suspense 2.** The visit is a place / check / undo loop until it reads CLEAN.

**Bugs to fix:**
- The raid view shows the bank before spending.
- The record chart clamps negative values to 0.
- A truncated "lost" column.
- A "HOLDS" stamp over 5 TAKEN nodes.

## Calibration: shipped systems on the same rubric (one fresh critic; ours as unnamed X and Y)

| System | W | P | N | D | C | Total | S | V |
|---|---|---|---|---|---|---|---|---|
| Into the Breach: enemy turn | 10 | 10 | 8 | 9 | 8 | 45 | 5 | 8 |
| Slay the Spire: elite intents | 9 | 8 | 8 | 9 | 8 | 42 | 6 | 7 |
| Invisible, Inc.: guard sweep / alarm | 9 | 7 | 7 | 9 | 7 | 39 | 9 | 7 |
| FTL: combat + rebel pursuit | 7 | 5 | 7 | 8 | 8 | 35 | 8 | 7 |
| Kingdom Rush: one wave | 8 | 5 | 8 | 6 | 6 | 33 | 8 | 8 |
| Teamfight Tactics: one round | 6 | 4 | 6 | 8 | 7 | 31 | 8 | 7 |
| X = M9c (low-fi mockup) | 7 | 8 | 5 | 5 | 7 | 32 | 6 | 3 (layout 6) |
| Y = H7 Godot lab | 7 | 9 | 4 | 5 | 5 | 30 | 3 | 5 |

**Findings:**
- **Acclaimed games score 31–45** (median about 37). Only turn-based telegraph games reach 40+.
- **Watched systems** (Kingdom Rush, TFT, FTL) score 31–35 and are carried by S and V, which sit outside the /50.
- **Our concepts sit in the bottom third of the shipped range,** level with Kingdom Rush and TFT on the /50 but far below them on S and V.
- **The rubric over-rewards P:** an exact table earns it cheaply and lowers D.
- **N tops out at 8** for every shipped game.
- **Invisible, Inc. is the only system above 7 on both P and S.** It forecasts locally and keeps the escalation unknown.

## Target (after calibration, 2026-10-22)
A hands-off or one-press raid is a **watched** system. The shipped watched systems score:
- FTL: 35;
- Kingdom Rush: 33;
- TFT: 31.

All three score S 8 and V 7–8. The target is about **35/50 plus S ≥ 8 and V ≥ 7**, not 40+. 40+ is only reached by
turn-based telegraph games (Into the Breach, Slay the Spire).

## Round 10: M10 Manhunt (one fresh critic, calibrated against the six shipped systems)

| W | P | N | D | C | Total | S | V (shown/layout) | Fit |
|---|---|---|---|---|---|---|---|---|
| 6 | 6 | 4 | 6 | 6 | 28 | 6 | 4/5 | 6 |

**Critic noise.** The same M9c rules scored 30 (R9) and 32 (calibration, as "X"), and M10 now scores 28. Rounds differ
by about ±3, the size of every change since R3.

**Each fresh critic finds a new set of hand-drawn ledger and consistency errors**, which cost 3–5 points. In this
round:
- Heat is not charged for the ghost.
- The decoy cost is not taken off the key.
- The third beam is never drawn.
- The legend moves between frames.

**Designer decisions raised:**
- The timing press against GDD pillar 4.
- Repair = value against GDD 3.3 (50% of install cost).
- A key in Schematics against GDD 1.3 (win = Exploits).
