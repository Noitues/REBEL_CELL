# Raid lab L6: readability pass and no dead raids (brief)

## Goal
Raise the no-words (N) and legibility (W) axes and remove the dead raid, without changing the L5 rules. The L5 critic's
findings are in `docs/design/raid_concepts/_reviews/REVIEW_LAB_L5.md`. Scope is `tools/raid_lab_m10/` only. Rules stay
`sweep_l5.py`, so parity on `l5_golden.json` must still pass unchanged.

## No-words pass
Every item below must read with the scramble on.
- **Node value:** pips or ring size on the node, one pip per 2 value, not only a number. Income chips use the same pip.
- **Go dark** gets its own look: a hollow, dimmed node with a closed-eye glyph and its income pip struck. It must not
  read like a damaged (DOWN, wrench) node.
- **Heat meter:** a danger gradient (calm to hot) with two hard notches at 50 and 75. Each notch carries a glyph for
  what it adds: +1 beam, +1 beam. The same glyph appears on the beam it adds.
- **Beams in fixed lanes:** parallel beams on the same row or column draw side by side in fixed, ordered lanes, never
  on top of each other or offset between rows. Fix `shots_jam/36_r3_no_spoof_left`.
- **Sealed-line outcomes on the board:** each candidate's outcome is marked on its own line, at the cell it hits, with
  the shape plus a small result glyph (DOWN, TAKEN, HOME −1). The side panel keeps the table.
- **Good play reads as good:** add a leg-level verdict on the record ("CELL KEPT 4/6, HOME 3/3") so three BATTERED
  stamps on the best line don't read as losing. Rank it against the leg's careless line if that is cheap.

## No dead raids
- **Settle a certain loss at once.** When `breach_risk` for the next raid is 3/3 on every intensity, the between
  screen shows the breach as decided. "Launch" plays the raid fast (1 beat per beam, no decision screens) straight to
  the BREACHED card, under a "the cell falls" banner. No pointless forecast or decision screens.
- **Warn one step earlier, in the plan.** On the plan screen show a "kit after this raid" strip: ghosts, decoys,
  spoofs and dark left, against the next raid's beam count at the Heat this plan leaves (with the 50 and 75 glyphs).
  When the plan spends the last lever and the next raid will add a beam, mark it amber: "next raid: N beams, M levers
  left". This is presentation from numbers the rules already produce. Do not add a new rule.

## Checks
- `parity_check.gd`: unchanged, passes.
- `flow_check.gd`:
  - all L5 checks;
  - the settled breach plays straight to the card with no decision screen;
  - the kit strip equals the kit after the raid and the beam count at the Heat after.
- Captures in `D:/rc_tmp/raid_design_lab/lab_l6/`: `shots/`, `shots_breach/`, `shots_scrambled/` and `shots_jam/`.
  Re-read every frame after the last fix.
