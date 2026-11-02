# T5 / T6 bits FX (option A) and storyboard T2 / T3 / T5 / T6 on the final locked board (roadmap step 7)

This pass recolours bits FX option A (inked glyph bits, picked in O-25) to the locked palette and rebuilds it on the final locked board (`../final/`, after the O-29 fix pass). It also updates the storyboard frames. Everything is compositing only (PIL and numpy) at 960x540 for the GIFs and 1920x1080 for the storyboard. No game number, word or rule changed. The board is never redrawn: every board pixel comes from the locked generator.

## Files

| File | What it is |
|---|---|
| `t5_A.gif` | T5, room to combat, neutral skin. 1.2 s, 15 frames at 80 ms, 960 px, 3.27 MB |
| `t6_A.gif` | T6, combat to netrun (win path), neutral skin. 0.8 s, 10 frames, 2.45 MB |
| `strip_t5.jpg`, `strip_t6.jpg` | 8 labelled key frames each, neutral skin |
| `strip_t5_solace.jpg`, `strip_t6_solace.jpg` | The same keys on the Solace skin. The Solace GIFs (3.3 MB and 2.5 MB) are kept in scratch: `D:/rc_scratch/combat_redesign/locked/transitions_work/out/solace/` |
| `t02_raid_to_select_jackin.jpg`, `t03_jackin_zoom.jpg` | Storyboard T2 and T3. The frames are unchanged; see "T2 and T3" |
| `t05_room_to_combat.jpg`, `t05_room_to_combat_solace.jpg` | Storyboard T5 on the final board, neutral and Solace |
| `t06_combat_to_netrun_or_fail.jpg` | Storyboard T6 on the final board |
| `sheet.jpg` | The four transitions, five rows (T5 twice), with their badges |
| `metrics.json` | Flash metrics for both skins, the method, and the old option A numbers for comparison |
| `scripts/` | The scripts, copied here. They run from the scratch folder `D:/rc_scratch/combat_redesign/locked/transitions_work/src/` |

## How the board is taken apart (no mask guessing)

`staged.py` is a copy of `f1_render._render` that keeps each stage on its own transparent layer. It imports the shared locked generator (`locked/corp/src`) read-only and writes its caches to its own folder. The layers are:
- the room;
- the HUD scrim;
- the plate and bezel;
- the spinner (`tower` layer: the tower, its shadow, HP ring, pips and trim);
- the enemy marks below the guns;
- the guns;
- the enemy marks above the guns (landing arcs, labels, tags, digits, and the W4-W6 tickets);
- the HUD;
- the YOU strip;
- each hand card on its own layer;
- the nameplate;
- SEND IT with UNDO.

When the layers are put back together they match `R.render('p1')` to within 2/255 (`px_over_8 = 0`), on both skins. That render matches the published `../final/p1_decide.png` and `p1_decide_solace.png` to within 1/255. The last frame of T5 and the first frame of T6 are the published plate itself (box-downsampled), so they differ from it by 0.

The old option A cut the wheel out of the plate with a radius mask. The new split comes from the generator's own layers, so the spinner flies in as the real spinner layer, and the hand overlapping the rim is no problem.

## What changed in option A (the recolour)

Radii are those of the locked board (NOTES of `../final/`), centre (536, 540).

| Element | Colour | Was (E10 option A) |
|---|---|---|
| Ring 0 (NOW), ring 1, ring 2: glyphs, keyline core and head dot | Corp skin colours. Neutral: steel greys (217,225,234), (166,180,198), (128,144,166). Solace: lime #96FF46, leaf (96,210,110), teal (64,178,132). | cream, LANE_PLUS1 blue, HARM red |
| 1 glyph in 5 on the rings | Corp accent. Neutral: line (188,200,214). Solace: porcelain (226,238,216). | SCHEDULE orange |
| Frame band (THIS TURN tape, lanes, rim): a 4th keyline at r 204 | Neutral silver tape #E8EEF4. It is the same for every corp, because the tape is time grammar. | (no 4th band) |
| W4-W6 tickets (corp layer, outside the wheel) | A short glyph stream in the corp colours, landing as the frame band locks | (the old tickets were part of the HUD cut) |
| Spinner: T5 settle and T6 eat keyline | Player pink #FF3DA8. A 90 ms snap round the halo at 0.56 s in T5; in T6 a 9 px keyline at r 100 eats the spinner. | T6 hub keyline in NET_CYAN |
| Spinner glyphs (T6) | The spot ink of the slice under each glyph, sampled from the spinner layer: BURST pink, SHIELD blue #2A58F0, TURRET yellow #FFD21F, REPAIR green #4BD67E. Pink otherwise. | cyan |
| Guns | Their own player-pink layer. They arm over 0.98-1.10 s, at the lock, and go first in T6. | part of the plate |
| Hand | Each card deals from the bottom (1.05 s plus 30 ms per card) with a trail of glyphs in its WPAP type colour: TOWER cobalt #2F5BFF, WAVE orange #FF8A1F, and Trace violet #A03CFF sparks on Trigger, the +Trace card. In T6 each card drops 40 px and fades while shedding the same glyphs. Cobalt and violet glyphs take the card paper (241,234,214) as their keyline, because ink on cobalt vanishes on the night room. | slid in, no glyphs |
| Destination ghosts (T5, 0.28 s on) | One solid hairline per path. The old ghosts were 48-segment dashed arcs; no dashed lines is a designer rule. | dashed |
| Keylines, glyph outlines | INK #0C0A16, unchanged. No glow, no bloom. | same |

Other changes:
- **Glyph sources:** each ring now starts from its own part of the lab. The old option A notes recommended this before shipping.
- **Glyph shapes:** a few "10" and "01" pair clusters are mixed in, also from those notes.
- **T6 order:** the frame band first (0.04 s), then ring 2, ring 1 and ring 0, then the spinner (0.26 s). The keylines are drawn above the glyphs, so the pink keyline stays visible through the glyph cloud.
- **Card exit:** the cards no longer dissolve as pixel blocks. My first render did that, and it read as option B, the one that was not picked.

Timing is unchanged: T5 1.2 s and T6 0.8 s, with the same keys, easings, 90 ms lock and 4 % overshoot.

## Flash rate (`metrics.json`)

The method is the same as `transitions/bits_fx/metrics.json`: mean frame luma per GIF frame at 12.5 fps, and changes over 10 % of the brighter frame counted as swings. A flash is an opposing pair of swings. I added two stricter checks: the same measure at 25 fps, and a local check on 60 px tiles at 25 fps.

| | Neutral T5 | Neutral T6 | Solace T5 | Solace T6 |
|---|---|---|---|---|
| Largest frame-to-frame luma change | 0.022 | 0.026 | 0.022 | 0.028 |
| Swings over 10 % (whole frame, 12.5 fps) | 0 | 1 | 0 | 1 |
| Whole-frame flashes | 0 | 0 | 0 | 0 |
| Worst 60 px tile, flashes in the whole clip (25 fps) | 2 in 1.2 s | 2 in 0.8 s | 2 in 1.2 s | 2 in 0.8 s |

Every clip is within the limit of 3 flashes per second, including the local tiles. No frame is brighter than the plate (max mean luma 0.232 neutral, 0.237 Solace). The single 10 % swing in T6 is the HUD and cards leaving in the first 80 ms, a one-way change rather than a flash. The old option A measured 0.021, with 3 swings in T5.

## Storyboard frames

The badges follow the v3 rules: REAL is an existing render; COMP is real renders composed here; CONCEPT is invented FX, stamped.

- **T5 (neutral and Solace).**
  - K1, the bare v3.1 bio room: **REAL**.
  - K2, the real spinner layer scaled 1.35x to 1.0x over the dimming room, at full resolution: **COMP**. It is sampled at 0.38 s, because at 0.25 s the spinner is still transparent.
  - K3 at 0.55 s, K4 at 0.85 s and K5 at 1.12 s are the recoloured FX: **CONCEPT**. They are rendered at 960 px and enlarged.
  - K6, the published final p1 plate (`p1_decide` / `p1_decide_solace`): **REAL**.
- **T6.**
  - K1, the final plate: **REAL**. As in v3, a decide-beat plate stands in for the won state, because no won-state plate exists.
  - K2 and K3, the recoloured FX: **CONCEPT**.
  - K4, the r6 street with mock tags: **COMP**, unchanged.
  - K5, the fail glitch tear, now made from the final plate: **CONCEPT**.
  - K6, the failure screen: **CONCEPT**, unchanged.
- **T2 and T3: no change to the frames.** Neither shows a combat board. The old wheel-circle zoom was removed in v3 (see the T3 easing line), so v3 T2 ends on the r7b highlighted target and T3 on the netrun street. There was no old board to replace. The strips are re-rendered from the v3 sources with the same badges, and the CHANGE block says so. I did not invent a combat cameo for them.

## Choices made without asking (overrulable)

1. **Neutral skin colours.** The neutral skin has no corp hue, so its ring glyphs are its own steel greys. The neutral T5 therefore reads mostly as ink and grey, with colour coming only from the player (pink spinner, guns, WPAP cards). The Solace strips show the corp colour story.
2. **The tape band gets its own keyline.** The frame band (THIS TURN tape, landing lanes, rim) is drawn as a 4th path in neutral silver on every skin, so that the time grammar never takes the corp hue (O-27 follow-up).
3. **Pink stays the player's.** No enemy glyph is pink. On the spinner, the BURST spot ink is the same pink as the player, which is correct, because the slice is the player's.
4. **Hand deal stagger is 30 ms, not the storyboard's 60 ms,** so that 4 cards plus SEND IT fit the 1.05-1.20 s window the storyboard gives.

## Open points

- **Frame rate.** The GIFs are 12.5 fps, as in the O-25 set. The game will run the FX at the display rate. The 25 fps metrics show the same motion sampled more finely stays within the flash limit.
- **Other fight rooms.** The srv and gh rooms are not checked. The glyph source points sit in the bio lab, so a room with its building elsewhere needs other source points.
- **Godot cost** is unchanged from O-25 (low to medium):
  - one ring-reveal shader, now with 4 angle-sweep uniforms;
  - the spinner as a sprite;
  - 4 `GPUParticles2D` for the rings plus small emitters for the tickets and cards;
  - the spinner glyph colours come from the slice type, not from sampling the image.
- **Process.** I ran a bare `python -` by mistake once, and a stray empty `python -c` once early on. The `python -` hung waiting on stdin; I stopped it (my own task), and it wrote nothing. All real work ran from script files.
- **Not done:** no Godot, no Blender, nothing committed, nothing written under D:/Godot/rebel_cell, no shared generator file edited.

## Rebuild

From `D:/rc_scratch/combat_redesign/locked/transitions_work/`, with one process per skin:
```
CORP=neutral python src/staged.py p1      # about 6.5 min: layers/neutral_p1.npz + compose check
CORP=solace  python src/staged.py p1
CORP=neutral python src/render2.py        # GIFs, strips, keys, metrics_neutral.json -> out/neutral/
CORP=solace  python src/render2.py
python src/build_sb.py                    # storyboard strips + sheet -> sb/
python src/publish.py                     # copies to this folder, writes metrics.json
```

## O-30 pass

O-30 pass (2026-11-02): T5, T6, both storyboard strips and `sheet.jpg` are rebuilt on the O-30 board, on both skins. That board uses the step-6 room grade (`bd_grade`), which is now the default in `corp/src`. The FAR threat trim is one solid tapered stroke, and the HUD hover fixes do not show on p1. The layers were re-staged from `corp/src`. They match `R.render('p1')` to within 2/255 (`px_over_8 = 0`), and that render matches the published `final/p1_decide.png` to within 1/255.
- T5 K6 and T6 K1 are the new published plates. The last GIF frame of T5 differs from the box-downsampled plate by 0, on both skins.
- **One room reference.** T5 K1 and the room T6 returns to are now the v3.1 bio bare room with the same default grade, without the board scrim (`scripts/mk_graded_room.py`, which calls `bd_grade.room_grade`). Before, they were the ungraded bare room. Every board frame sits on that room. The room still dims to the plate's scrimmed room on the old 0.20-0.60 s curve.
- **What did not change:** timing, keys, easings, glyph colours and game numbers. The storyboard K1 label and the CHANGE blocks carry an O-30 line.
- **Flash (`metrics.json`).**
  - Whole-frame flashes are 0 in T5 and T6 on both skins. A first run with the ungraded K1 counted 1 in each: a dip from the bright bare room to the dark graded room and back up.
  - Mean frame luma now runs from 0.078 (graded room) up to 0.208 neutral and 0.213 Solace, which is the plate. No frame is brighter than the plate.
  - The worst 60 px tile is 3 in 1.2 s for T5 and 3 in 0.8 s for T6, on both skins (both were 2 before). The darker room makes 10 % swings easier to reach in tiles the glyph streams cross.
  - Every clip still passes the limit of 3 flashes in any 1 s, but the local tiles are now at that limit. If the designer wants margin, the glyph density over the room is the knob. It was not changed here.
- Scripts now run from `D:/rc_scratch/combat_redesign/locked/fx_o30b/tr/src/`. The commands are the ones under Rebuild, with the paths redirected, plus `python src/mk_graded_room.py` first. The copies in `scripts/` are those files.
