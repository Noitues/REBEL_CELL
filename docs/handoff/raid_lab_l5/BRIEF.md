# Raid lab L5: the sweep lab, round 5 (brief)

## Goal
Update `tools/raid_lab_m10/` (currently L4) to the L5 rules, and fix the L4 critic's findings
(`docs/design/raid_concepts/_reviews/REVIEW_LAB_L4.md`). Scope is `tools/raid_lab_m10/` only. Replace the L4 code;
git keeps it.

## Source of truth (python, read-only)
- `tools/raid_concepts/sweep_l5.py`: the rules. It builds on `sweep_l4.py` and `sweep_l2.py`.
- Golden: `tools/raid_lab_m10/data/l5_golden.json`, from `tools/raid_concepts/l5_golden.py`.
  - A spoof is `null`, `[x, y]` (SKIP) or `"JAM"`.
  - Each leg-line between step carries `risk`, a map from intensity to breach_risk of the next raid.
  - The first 40 random between steps carry `risk_raid` and `risk`.
- Drop `l4_golden.json`.

## Rule changes from L4
- **The response after the reveal has two forms.** Both use one spoof from the kit, and both add `SPOOF_HEAT` (2)
  Heat after the sweep:
  - **SKIP:** beam 2 skips one node, as before.
  - **JAM:** the hunter does not run this raid.
- **Re-drawn candidates.** `make_leg` in sweep_l5 re-draws each raid's sealed candidates (seeded) until each one hits a
  different, non-empty set of asset/HOME cells. Use the golden leg data as given.
- **One repair per between step** (`REPAIR_SLOTS` = 1). DOWN assets now pile up across the leg.
- **breach_risk(leg, i, state).** Over every allocation, the fewest sealed lines on which every response breaches. 0
  means some plan avoids a breach on every line. Port it as a rule, with parity.

## Presentation (from the L4 critic)
- **The response is a real decision screen.**
  - After the reveal, show HOLD, every SKIP target and JAM side by side.
  - Each option shows its result: what goes DOWN or TAKEN, HOME, and the Heat after, including +2 and whether it
    crosses 50 or 75.
  - JAM draws the hunter's turn it would take, struck out.
  - Auto-skip the screen only when the kit has no spoof. Then show "no spoof left" for a beat.
- **Breach risk on the between screen.** Every intensity card shows the next raid's risk, for example "BREACH on 2/3
  lines" in red, or "safe with levers". It updates live as the repair and buy change. The pre-launch warning stays.
- **Damage that sticks is visible.**
  - DOWN assets show how many raids they have stayed down.
  - The repair panel shows "1 crew: pick one".
  - The record shows the DOWN and TAKEN count at leg end.
- **Hunter word.** When nothing is touched, show the hunter's own line as a glyph, not the word "OWN LINE".
- **Turn arrow.** It ends on the column, not beside it.

## Checks
- **`parity_check.gd`:**
  - every golden leg step on all three lines, including `risk` for every intensity;
  - all random raids, JAM included;
  - all random between steps, `risk` included.

  Exit non-zero on a mismatch.
- **`flow_check.gd`:**
  - planned leg 0;
  - a naive breach leg;
  - forecast equals result for every response option on the decision screen;
  - the risk shown on each intensity card equals `breach_risk`;
  - the ledger reconciles;
  - the kit is conserved.
- **Captures** in `D:/rc_tmp/raid_design_lab/lab_l5/`:
  - `shots/` (planned leg 0, every beat);
  - `shots_breach/`;
  - `shots_scrambled/`.

  Re-read every frame after the last fix. At least one capture must show JAM chosen; the planned lines use it on legs
  3, 5 and 11.
