# B — SIEGE LANES, round 2 (current)

The SPEC.md base still holds: a tower-defense read of today's resolver, wave previews, and a hands-off playout.

## What changed in round 2
- **One HP ribbon per threat** replaces the chip stacks.
  - The lane's **width is the threat's HP**, and it narrows after each hit.
  - Numbered dots mark the step at which the threat reaches each node.
  - A skull marks where it dies.
  - During the playout the ribbons stay faint, as the ruler the playout is checked against.
- **Reach is shown on the map.** Holding a turret over a node puts a yellow ring on every node it reaches. The polygon is gone.
- **Wave chips** at each entry: two numbers (HP, damage), speed chevrons and a route glyph. A countdown dial and the Heat chain sit with them.
- **The result panel** shows:
  - home before > after;
  - the DOWN and TAKEN counts;
  - threats killed out of the total;
  - the coin cost;
  - one line keeping the alternative plan.
- **The aftermath** names each loss once, with its fix as an icon path: a TAKEN node → netrun hex, a DOWN node → coins.
  TAKEN nodes point a dashed lane at home.
- **Frame 6, the next raid** (Heat 76). This raid's TAKEN nodes are Solace entries one hop from home, so the loss reshapes the next lanes.
- **The data is real.** Frames come from sim plans BARE (as it stands), SHIELD (committed) and LURE (compared).

## Rule changes
None.
