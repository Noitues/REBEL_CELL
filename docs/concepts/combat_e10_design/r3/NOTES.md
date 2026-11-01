# R3 latent elements: options and code locations

Generator copy: `D:/rc_scratch/e10_design/r3_latent/src` (copied from `final/src`; state copies in `r3_latent/`). Nothing in `final/`, the approved plates, the sim, or `state_e10.json` was changed. All renders are the final p1 plate (bio cutaway) via `asm_r2.render(beat, check=False)`; draw asserts are not run on these latent renders (they add marks the asserts do not know). Per-option full plates: `r3/plates/`.

Machinery added in the copy (all in `r3_latent/src`):
- `asm_r2.py`: hook lists `HOOK_GHOST` (board layer, under the HUD), `HOOK_PRE` (before the sticker layer), `HOOK_TOP` (after everything), `STACK_SEL` (passed to `stack_layer`).
- `kscene2.py`: `HOVER_CARD` (lift a named card) and `HIDE` (empty a hand slot while dragging).
- `a2_stick.py`: `hint_line` option `KEYB`, `hint_dy` in `stack_layer`.
- `r3_lib.py`: render wrapper, crops, sheet builder.

## 1. send_it_key_hint (Space = end turn) — `s1_sendkey.py`, sheet_send_it_key_hint.jpg
- A, kit keycap on the sticker corner: `opt_A` / `cap_wide` (same cap as UNDO [Z]: dark glass, cyan 2 px, mono 18, plus an ink keyline); straddles the lower-right corner, tilted with the sticker. Nowords form: space-bar bracket glyph (the `words=False` branch of `cap_wide`).
- B, the cursor is the key: `a2_stick.hint_line(opt='KEYB')`; the block cursor becomes a 44x28 cap with the space-bar bracket. Selected with `STACK_SEL hint='KEYB'`.
- C, vinyl tab: `opt_C` (HOOK_PRE, drawn under the sticker); `a_kit.vinyl2` tab with Anton 19 ink SPACE, hint line drops 4 px.

## 2. card_hover_ghosts (Brace, Twist shown) — `s2_ghosts.py`, sheet_card_hover_ghosts.jpg
Common: ghost = the real drawing of the result at 55 percent (`GA`), the card's library glyph in PENCIL_PLAN is the only new mark (`plan_glyph`, `KA_twist` / `KA_brace`). Twist ghost: ring-1 units shifted one sector (`shifted`, `twist_ghost`), drawn with `AU.draw_unit` + `W2C.screen`; one wax arc old to new. Brace ghost: `wc2.brace_plate2('A')` on slice 2 (default target), glyph on top.
- A, lifted copy: originals untouched.
- B, focus ghost: what the card leaves (moving units; the other five slices) under a 60 percent ink veil (`VEIL`).
- C, dashed hollow: dashed outline in the source colour, hollow chevrons (`W2U.chevrons(...,0,hit)`), bare glyph; Brace as a dashed clamp outline.
Pull, Shove, Firewall, Trigger are not rendered: each option extends the same way (Pull and Shove = the unit's ghost one ring in or out via `shifted`-style helper; Trigger = the existing killed-unit ghost; Firewall = a ghost of its ring effect). Their rules are not in the state, so the mapping needs a designer check.

## 3. card_drag_aim (Trigger dragged onto unit 6) — `s3_drag.py`, sheet_card_drag_aim.jpg
Common: valid-target ticks and lime focus brackets from `a2_tgt.cues`, the Trigger slot emptied (`HIDE`), a wax tether from the gap (`curve`).
- A, pencil reticle (`aim_A`): wax ring plus four ticks around the token.
- B, card as cursor (`aim_B`): 44 percent card copy at the hotspot, thin tether.
- C, verb disc (`aim_C`): yellow disc with the Trigger glyph on a stem, pencil arrowhead tether.
Not shown: over-no-target and invalid-drop states (suggest dropping the ring to 40 percent and removing the lime brackets).

## 4. no_target_tag placement — `s4_notarget.py`, sheet_no_target_tag.jpg
Showcase: `showcase()` makes a local deep copy of f1 with units 2 and 5 removed (the sector-0 column is empty) and the sector-0 gun's shots cleared; restored after the run; nothing written. The E10 tag in `wc2.idle_stub` is suppressed in the copy (`words=False` wrapper), so the options draw the tag.
- A, gutter tag with leader (`opt_A`): upright tag off the axis, nearest corner pushed out to r 164, 1.6 px leader to the stub start. Note: an upright 116x26 tag cannot sit inside the 8 px gutter; this is the tightest upright fit that leaves the slice, trim and HP ring clear.
- B, tag at the stub end (`opt_B`): upright, centred on the axis just past the open ring, the ring-0 cell under it dimmed (band -20..19 deg, 55 percent ink).

## Notes
- One slip: an empty `python -` (no input) was run once by mistake in a longer command; it did nothing and was killed. No other stdin Python.
- Twist and Brace ghosts at 55 percent read faintly on the busy ring plate (option C most so); that is a finding for the art director.
