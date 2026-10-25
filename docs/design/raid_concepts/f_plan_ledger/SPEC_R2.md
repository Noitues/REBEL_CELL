# F — PLAN LEDGER, round 2 (current)

## What changed in round 2
- **The ledger is the sim's step trace**, under today's resolver rules. The round-1 "ICE on a cell" rule is dropped.
  Defenses are dropped on the map's nodes, and the ledger rewrites.
- **Cells are icon-only.** A cell shows:
  - the node icon where the threat stands (a cobalt shield at a Solace site);
  - a red −N for what it hits;
  - an HP bar;
  - a skull where it dies;
  - a house when it is spent at home;
  - a teal hatch with an ICE icon while it is held.
- **The totals row** has one cell per node: before > after, with a check, bolt or flag icon. TAKEN cells are crossed.
- **The guaranteed panel** shows home −N and the DOWN and TAKEN counts, with the alternative plan below it. SIGN ORDERS commits.
- **The warning** is the intercepted strike order as icon rows: two-number chip, then the full path as node icons. The
  countdown, the Heat chain and the routes on the map go with it.
- **The playout is the big map.** The ledger shrinks to a strip with a cursor.
- **The receipt is on the map.** TAKEN nodes keep the X and now point at home (1 hop). Each loss is listed with its fix:
  a netrun hex, or coins.
- **The data is real.** Frames come from sim plans BARE, DECOY ONLY (what-if), SHIELD (committed) and LURE (compared).

## Rule changes
None.
