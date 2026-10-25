# Raid lab L3: the sweep lab, round 3 (brief)

## Goal
Update `tools/raid_lab_m10/` (currently the L2 rules) to the L3 rules. This round targets **decision depth across the
leg**. It also fixes the L2 critic's bugs. Scope is `tools/raid_lab_m10/` only. Replace the L2 code; git keeps it.

## Source of truth (python, read-only)
- `tools/raid_concepts/sweep_l3.py`: the rules. It builds on `sweep_l2.py`; it does not replace it.
- Golden: `tools/raid_lab_m10/data/l3_golden.json` (from `tools/raid_concepts/l3_golden.py`). It now carries:
  - `extra2`, plus every constant in `config`;
  - 6 legs with planned, greedy and naive lines, including the between-raid choices;
  - 200 random raids and 200 random between steps.
- Drop `l2_extra.json` and its generator if they are no longer needed.

## Rule changes from L2 (read `sweep_l3.py`)
- **Leg kit.** 2 ghosts, 2 decoys and 2 spoofs for the whole 3-raid leg.
  - Per raid: at most 1 ghost, up to 2 decoys, and go dark on at most 1 asset.
  - Decoys come from the kit and cost no Schematics.
  - A spoof is spent only if used after the reveal.
- **Between raids**, one screen, three choices:
  1. **Repairs:** v // 2 each.
  2. **One shop buy:** ghost 6, decoy 4 or spoof 5.
  3. **Run intensity:**

     | Intensity | Heat | Income |
     |---|---|---|
     | LOW | +6 | ×0.5 |
     | NORMAL | +12 | ×1 |
     | HOT | +18 | ×1.5, rounded down |

  Show what each intensity does to the next raid's Heat band. Extra beams start at 50 and 75.
- **Heat carries:** the leg score charges 1.0 per Heat point above the start (Heat feeds later raids). Show "Heat
  carried" in the leg ledger and record.
- **Outcome tiers:** EVADED, HOLDS, DAMAGED (home hit) and BREACHED (campaign lost). Stamps and record pips follow the
  tier.

## Presentation fixes
From the L2 critic (`docs/design/raid_concepts/_reviews/REVIEW_LAB_L2.md`).
- **The forecast must not name the best spoof.**
  - Show, per sealed line, which nodes the spoof *could* save.
  - Show the result with and without a spoof as a range.
  - The player picks.
- **One mark per meaning.** Ghost, spoof and sealed beam currently share a dashed ring. Give each its own mark:
  - ghost: a dashed ring;
  - spoof: a teal skip-chevron;
  - sealed beam: a shape-capped dashed line.
- **Bugs:**
  - There is no spoof decision after a breach; the sweep ends at the breach.
  - No CELL HOLDS stamp when home took damage; that is DAMAGED.
  - Pips follow losses.
  - The repair panel shows that repairs are paid before income.
  - "Leg value" includes pending income.
  - The record marks per-raid changes versus carried-over states.
  - Fix the clipped "HOME -" pill and the stamp sub-line.
  - The campaign-lost card shows no "Leg score: -100".
- **The scramble** must not be a one-to-one letter substitution. Use a per-word random replacement of the same
  length, seeded by the word, so it can't be decoded.
- **The kit tray** is shown on every plan screen: remaining ghosts, decoys and spoofs.

## Checks
- **`parity_check.gd`:** every golden leg step on all three lines, all random raids and all random between steps.
  Exit non-zero on a mismatch.
- **`flow_check.gd`:**
  - the planned leg 0 through the model;
  - a naive breach leg;
  - forecast equals result for the chosen spoof;
  - the ledger reconciles;
  - the kit is conserved.
- **Captures,** in `D:/rc_tmp/raid_design_lab/lab_l3/`:
  - `shots/`: planned leg 0, every beat, including the between-raid screens;
  - `shots_breach/`;
  - `shots_scrambled/`.

  Re-read every frame after the last fix.
