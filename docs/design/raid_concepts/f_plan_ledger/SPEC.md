# F — PLAN LEDGER (pre-commit board, guaranteed outcome)

**One line.** Solace's strike order is intercepted as a dossier and laid out as a ledger. The ledger has one row per threat
and one column per step. Each cell shows where the threat stands, what it hits and its HP left. You drop defenses on cells or
nodes, and every affected cell rewrites. The totals row gives the guaranteed per-node result. Sign the orders, and the map
replays the ledger.

## The decision
The defense pieces act on the ledger:
- **Turret.** Placed on a node, it marks every cell in reach with a crosshair and takes 4 off that row's HP track.
- **ICE Lock.** Dropped on a cell, it hatches that cell and the next. The threat stays put and deals no damage there.
- **Decoy.** Placed on a node, it rewrites a row's later cells to walk toward the Decoy.

The player reads which column hurts most and which row is the real danger, and spends pieces on the cells that matter.
The planning is spreadsheet-precise.

## The information shown
- **Dossier (warning).** One line per threat: silhouette → target node icon, HP, crossed swords and damage, a routing hint.
  The Heat that caused it (51 > 50) and when it executes (on return to HQ).
- **Ledger grid.** Each cell shows:
  - the node icon where the threat stands;
  - the red damage it deals (−5);
  - the threat's HP bar after the step;
  - a red X where it dies;
  - a teal hatch where it is held;
  - a turret mark where a shot lands.
- **Totals row**, one cell per node: node icon, `integrity − damage`, and the verdict word coloured by state.
- **Guaranteed panel.** The verdict, the losses with their repair cost, and Heat. **SIGN ORDERS** commits.
- **Mini-map** with the DOWN and TAKEN marks for the plan.

## Resolution
- **The playout replays the plan.** A cursor walks the ledger column by column while a larger map plays the same step.
- **Floaters, tracers and kills** appear on the map.
- **Timing.** About 25 s. No input.

## Consequences
- **The totals row becomes the receipt**, and the stamp prints over it.
- **A "paid" strip** lists asset wear and spend.
- **Marks persist** on the HQ map, as in the other concepts.

## Rule changes
- **The resolver is unchanged.** The ledger is its step trace.
- **One new rule (designer decision):** an ICE Lock is placed **on a threat at a step** instead of on a node. It holds that
  threat for 2 steps wherever it is, and a held threat deals no damage.

## Key frames
`r1/mockups/`, `r1/scrambled/`.
