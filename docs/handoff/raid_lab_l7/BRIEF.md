# Raid lab L7: look and motion pass, to the target frames (brief)

## Goal
Bring the lab (`tools/raid_lab_m10/`, after the L6 readability pass) up to the look of the target frames in
`docs/design/raid_concepts/raid_target/`. Then add the motion that carries suspense in the playout.

This is a lab-only pass. The designer ruled on 2026-10-22 that the raid lab does its own visual and motion pass here
rather than routing it through art-pass.

- **Scope:** `tools/raid_lab_m10/` only.
- **Rules:** do not change them. Parity on `l5_golden.json` must still pass unchanged.
- **Motion must follow** `docs/STYLE_GUIDE.md` §5.3: raids play from the resolver's events and are never recomputed.

## Look (match the target frames)
- **Palette, materials and lighting:** port them from the frames' README.
  - Threats are cobalt `#3D6BFF`; the cell and HOME are warm.
  - Use shaders or gradients in Godot 2D or 3D, whichever matches the frames best.
  - Every screen must still read in grayscale.
- **Shared look:** the board, nodes, beams, sealed candidates, levers, HOME, the Heat meter and the stamps all take
  the frames' design. Keep every L6 no-words glyph; restyle it, do not remove it.
- **Panels:** the side panel and between screen take the frames' panel style. Text stays at 1.0 scale, US English.

## Motion (the suspense beats)
All timings live in one config resource in `tools/raid_lab_m10/`. Add a 1x / 2x / 4x speed toggle and an instant
toggle for captures.

1. **Launch:**
   - The known beams sweep cell by cell along their fixed lanes.
   - Each cell they touch flashes. A decoy pulls the beam aside and stops it.
2. **Unseal:**
   - The three candidate lines shimmer, then two collapse.
   - The real line ignites end to end, with a short hold before it fires.
3. **Spoof window:**
   - The SKIP targets and JAM pulse.
   - A countdown ring is drawn but never forces a choice, since the lab is turn-based.
   - On a pick, show the skipped node's bypass arc, or the hunter's turn being struck out.
4. **Hunter:** the turn arrow draws from the first touch, then the beam runs down the column.
5. **Impact:**
   - An asset going DOWN: the wrench drops in, with a short shake.
   - A second hit TAKES it: the node flips to corp ground.
   - HOME hit: a drain with a white lag bar.
6. **Stamp:** the outcome stamp slams in. The leg verdict counts up on the record.
7. **Heat:** one pulse per threshold crossed, with the notch glyph stamped.
   - The next raid's beam count is shown as the meter fills on the between screen.
8. **Settled breach:** the fast play from L6 under the "the cell falls" banner, ending with HOME draining to 0 and
   the BREACHED card.

## Checks
- `parity_check.gd`: unchanged, passes.
- `flow_check.gd`: all L6 checks, plus:
  - instant mode yields the same final state and ledger as animated mode;
  - the event order of the animation equals the resolver's touch order.
- **Captures** in `D:/rc_tmp/raid_design_lab/lab_l7/`:
  - stills in `shots/`, `shots_breach/`, `shots_scrambled/` and `shots_jam/`;
  - Movie Maker clips (`--write-movie`, via `run_windowed.py`) of one planned raid and the breach raid, in `clips/`.
    Then extract 6 to 8 key frames per clip into `clips/frames/` for review.
- **Comparison sheet:** each target frame next to the matching lab still.
- Re-read every frame after the last fix.
