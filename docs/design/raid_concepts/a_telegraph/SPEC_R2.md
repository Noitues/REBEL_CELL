# A — TELEGRAPH, round 2 (current)

The SPEC.md base still holds: exact intents on the network, the resolver unchanged, a fixed camera, and no input during the playout.

## What changed in round 2
- **ALL first.**
  - The scrubber opens on an ALL cell showing the whole raid at once: every path, every node's end-of-raid tag (HOLDS,
    SCUFFED −N, DOWN or TAKEN), and the total loss in striped pips.
  - Per-step cells (1…N) carry the silhouettes that strike in that step. A red corner means a node falls in that step.
- **The what-if is a delta.** Dragging a piece shows the home loss and lost-node count before > after. For example, Decoy
  on the Firewall gives home −20 > −12 and lost 4 > 0.
- **Plan compare.** Two saved plans sit side by side, each with home −N, the DOWN and TAKEN counts, the coin cost, and
  +N netruns to reclaim.
- **CLEAN box.** It shows the threat that breaks the clean defense, where it lands, and the HP it still has there. The
  payout (+5 Heat, +12 Schematics) is shown dimmed.
- **The end-of-raid panel** lists home first, then every changed node, as before > after.
- **The warning shows:**
  - dashed routes;
  - two-number threat chips at the Solace sites, with a route glyph and speed chevrons;
  - the countdown (netrun map nodes until home);
  - the Heat chain 51 > 50 → raid.
- **Glyph stats** on the asset cards. Loss icons in the stamp. The aftermath shows the patch cost, the scuffed count and
  the missed payout.
- **The data is real.** Frames come from sim plans BARE (as it stands), DECOY ONLY (what-if), LURE (committed) and SHIELD
  (compared).

## Rule changes
None. The in-step strike order is shown, but the resolver already fixes it.
