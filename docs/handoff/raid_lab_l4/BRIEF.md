# Raid lab L4: the sweep lab, round 4 (brief)

## Goal
Update `tools/raid_lab_m10/` (currently L3) to the L4 rules, and fix the L3 critic's findings
(`docs/design/raid_concepts/_reviews/REVIEW_LAB_L3.md`). Scope is `tools/raid_lab_m10/` only. Replace the L3 code;
git keeps it.

## Source of truth (python, read-only)
- `tools/raid_concepts/sweep_l4.py`: the rules. It builds on `sweep_l3.py` and `sweep_l2.py`.
- Golden: `tools/raid_lab_m10/data/l4_golden.json`, from `tools/raid_concepts/l4_golden.py`. Each raid now carries:
  - `real`: the corp's actual sealed line;
  - `shapes`: the shape per candidate (0 triangle, 1 square, 2 circle).

## Rule changes from L3
- **No reveal tell.** The real sealed line is `raid.real` (seeded per raid), never always candidate 0.
  - Draw candidate k with shape `raid.shapes[k]`.
  - The forecast and the reveal use these.
- **Go dark is a kit item.**
  - It starts at 2 per leg, at most 1 per raid, and still costs that asset's next income.
  - The shop sells it.
- **Cheaper shop:** ghost 4, decoy 3, spoof 3, dark 3.
- **New tier: BATTERED.** The home is intact and 2+ assets went newly DOWN, or any asset was newly TAKEN.
  - It sits between HOLDS and DAMAGED.
  - Give it its own stamp and pip color (amber).

## Presentation fixes (L3 critic)
- **Draw the hunter's rule on the grid** as a glyph: an arrow from the first touch turning down its column, shown
  live in the plan and the playout. Replace the word "TURNS".
- **"Worst case" counts everything.** Home integrity and the assets that would go DOWN or TAKEN, for example
  "worst: 2 DOWN, 1 TAKEN, home −1".
- **Show "Assets kept" live** on the plan, aftermath and between screens, not only on the record.
- **Labels:**
  - "INCOME (last)" becomes "INCOME (next run)" for the selected intensity.
  - One "+N" meaning per position.
  - The "Heat carried" sign is the same on every screen.
  - "Leg value" can be rebuilt from the numbers shown beside it.
  - The README says a breach has no leg score: the campaign is lost.
- **When a lever is placed, draw its effect on the grid:**
  - ghost: a dashed ring, and the beams that skip it;
  - decoy: the beam's stop;
  - dark: a greyed node with its income chip struck.
- **The between screen marks committed choices:** a check and a frame on the picked repair, buy and intensity.
- **A breach must not be a one-beam non-event.** When the forecast already shows BREACH on every line, the plan screen
  shows a red BREACH warning before launch, naming the lever that would avoid it if one exists. The playout still
  plays to the home touch.

## Checks
- **`parity_check.gd`:** every golden leg step on all three lines (planned, greedy, naive), plus all random raids and
  all random between steps, including `real` and `shapes`. Exit non-zero on a mismatch.
- **`flow_check.gd`:**
  - planned leg 0;
  - a naive breach leg;
  - forecast equals result for the chosen spoof;
  - the ledger reconciles;
  - the kit is conserved, dark included.
- **Captures** in `D:/rc_tmp/raid_design_lab/lab_l4/`:
  - `shots/`: planned leg 0, every beat and between screen;
  - `shots_breach/`;
  - `shots_scrambled/`.

  Re-read every frame after the last fix. Check that the revealed shape differs between raids in at least one leg.
