# JINX SCRIBBLE (punk concept: player wheel + cards)

Refs 4 (Arcane Jinx neon scribbles) and 3 (Spider-Verse glitch). Built from a copy of the F1 generator; F1 itself is untouched.
Files: `style_board.jpg`, `plate_A.png`, `plate_B.png` (p1_decide, bio cutaway, 1920x1080), `wheel_crop.jpg` (A and B at 2x), `hand_crop.jpg` (1x), `src_snapshot/` (js_* files are the new style; the rest is the F1 generator).

## Idea
The Cell's wall: a dark painted disc, neon pink and cyan chalk/marker, doodled stars, X marks, tallies, spirals and crude faces, spray mist, and Spider-Verse misregistration (a cyan plate and a pink plate shifted off the key line and off every icon and title). The corp stays clean enamel and glass; ours is paint that does not line up.
- **A, Night wall**: violet painted wedges with a thick pink chalk key line and a cyan plate; cards are dark painterly boards with a pink chalk frame.
- **B, Hot paint**: hot-pink painted wedges with ink key and cyan plate; cards have a pink painted body with dark panels. Louder, closer to F1's pink.
- **Cards** keep the black-book layout (cost coin top-left, big icon in an art band, title, type band, rules text, Trace tab). Title is chalk-white Anton on an ink strip with pink/cyan plates (readable, answers ART CALL 52 note 1). Rules text is chalk-white marker on a dark panel. Cost coin stays system cyan, Trace tab stays violet.
- SEND IT keeps the pink spray slab plus a cyan plate; nameplate and YOU strip lose the paper and tape and become dark boards with a neon rim, so the whole player family reads as one hand (the F1 "two hands" risk).
- **No needle.** Its call is removed; the THIS TURN tape starts on its own. Side effect: the sector 0 digit it covered now shows, and I redraw all six sector digits on top (they were half-clipped by ring plates). The 3 digit sits on the HOLD cell edge; check it.

## Grammar kept
No dashes anywhere (dash audit not re-run; no dashed call was added). HOT/COLD/FAR trim, HP blocks, pips, pending cross-hatch in cause colour, arrowed outline, W4-W6 tickets, enemy enamel: all unchanged (f1_tower functions reused). To protect the hatch, normal wedges use NO parallel hatching: only loose loops and squiggles at random angles, so parallel runs still mean pending loss. Cardinal grammar bits unchanged: pink = ours, pending hatch colour = cause.
Break-state slices get glitch tears (cyan/pink sheared slivers) where a loss is pending.

## Legibility risks
1. Doodles are 1.7-2.4 px lines: invisible at 1x, they read as texture. Honest: at 1x the wheel is mostly neon outline + painted fill; the scribble character shows at 2x.
2. A: red pending hatch on violet is lower contrast than on pink; B has it better but is loud (same as F1).
3. Cyan doodles and the cyan plates are near the system cyan (RAM, NET); ownership is told by the pink key and the paint, not cyan alone.
4. Hub text BREAKER is small; the spiky badge outline competes with the HP ring at r52-64 (same crowding as F1).
5. Rules text on cards is larger than F1 but the last card in the fan clips nothing; the first three are covered ~20 px at the right by the next card, text was moved left to stay clear.
6. Not run: squint/greyscale checks, game-info asserts (the draw asserts were off for these plates). Colour-blind checks skipped per ART CALL 52.

## Godot build
- Wheel: one 940x940 painted page texture (baked, no runtime brushwork) plus six wedge sprites (A: dark painted fill; B: pink fill) with a baked chalk key outline; the cyan plate is a second sprite offset (-2,+1.5) using the same alpha, or a shader that samples the outline mask twice. Icons: white sprites with two tinted copies offset (cyan, pink) = misregistration; the horizontal glitch slice is a tiny scrolling-offset shader band, animated on hits only.
- Scribbles: a pool of ~20 doodle sprites (star, X, tally, spiral, bolt, crown, face), tinted at runtime, placed per slice from a seed; chalk grain = one shared noise mask multiplied into the alpha; neon glow = additive blurred copy (or WorldEnvironment glow limited to the player layer).
- HP blocks, pips, trim, hatch: unchanged draw code (hatch is a tiled stripe shader in the cause colour).
- Cards: one Control scene per card; art band, title strip, tape and text panel are baked 9-slice textures; title is a Label with Anton, ink outline, and two offset Label copies behind (cyan, pink); icon gets the same two-copy plate. Hover lift keeps the pink offset print from F1.
- Needle: do not instantiate the node; THIS TURN tape stays.
