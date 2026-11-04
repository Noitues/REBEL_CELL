# T5 / T6 bits FX (option A) and storyboard T2 / T3 / T5 / T6 on the rebuilt combat board

**Status 2026-11-04: re-rendered on the rebuilt board** (`../final/` after the 2026-11-03 rebuild and gate 1), on both skins. AD review items **1.7** and **3.12** are fixed here; see "2026-11-03 rebuild". What is still open is under "Not done". The sections after "History" describe the older passes and are kept as a record only.

What T5 and T6 must show is the designer's ruling **DR-10** (`../../VISUAL_PLAN.md`, ART CALL 49 items 5 and 6). How the bits look is ART_BIBLE 1.2 (LOCKED). Bits option A (O-25) and failure screen A (O-26) are art-pass picks.

## 2026-11-03 rebuild (re-rendered 2026-11-04; review 1.7, 3.12)

Every frame is rendered at 1920x1080 by `scripts/render3.py` from the board generator's own layers (`locked/corp/src`, imported read-only, never edited). Nothing is enlarged and nothing is painted. No game number, word or rule changed.

### Files

| File | What it is |
|---|---|
| `t5_A.gif` | T5, room to combat, neutral skin. 1.2 s, 16 frames at 80 ms (stored as 13: the 4 identical opening frames are one 320 ms frame), 960 px, 3.17 MB. Frame L* as decoded: 28.0 at K1, 37.9 at the end (the 960 px plate) |
| `t6_A.gif` | T6, combat to netrun (win path), neutral skin. 0.8 s, 11 frames (stored as 10: the last two are one 160 ms frame), 2.36 MB. The camera holds on the room (see Not done) |
| `strip_t5.jpg`, `strip_t6.jpg` | 8 key frames each, neutral skin, badged |
| `strip_t5_solace.jpg`, `strip_t6_solace.jpg` | The same keys on the Solace skin. The Solace GIFs (3.22 MB and 2.38 MB) stay in scratch: `D:/rc_scratch/combat_redesign/locked/rebuild/transitions/out/solace/` |
| `t02_raid_to_select_jackin.jpg`, `t03_jackin_zoom.jpg` | Storyboard T2 and T3. The frames are the v3 frames; neither shows a combat board |
| `t05_room_to_combat.jpg`, `t05_room_to_combat_solace.jpg` | Storyboard T5, neutral and Solace |
| `t06_combat_to_netrun_or_fail.jpg` | Storyboard T6, win path and FAIL branch |
| `sheet.jpg` | T2, T3, T5 (both skins) and T6 in one sheet, badged |
| `metrics.json` | Per skin: GIF sizes, frame L*, flash counts (whole frame and 120 px tiles), the wheel-face check, the bit colour stats per stream, the parameters, and a verdict. Also the method, the O-30 verdicts and the old option A numbers |
| `scripts/` | The scripts (copies). They run from `D:/rc_scratch/combat_redesign/locked/rebuild/transitions/src/`. The O-30 scripts (`fx2lib`, `fx_a2`, `render2`, `build_sb`, `quick2`, `publish`, `mk_graded_room`) were removed from here; they are in git history |

### How the board is taken apart

`staged.py` is a copy of the current `f1_render._render` (with `lw_render` installing `rb_patch`, `rb2_patch` and `rb3_patch`, as the board build does). It keeps each stage on its own RGBA layer:
- the plate's room (rb2-1 grade with the board scrim), and the HUD scrim;
- the plate and bezel; the tower (spinner, shadow, HP ring, pips, trim);
- the enemy marks below the guns; the guns;
- the landing arcs and labels; the W4-W6 tickets; the tags and digits;
- the HUD; the YOU strip; each hand card; the nameplate; SEND IT with UNDO;
- the v3.1 bare room, for K1.

Put back together, the layers match the published `../final/p1_decide.png` and `p1_decide_solace.png` to within 2/255, with 0 pixels over 8, on both skins. T5's last frame and T6's first frame are the published plate (difference 0). T5's first frame and T6's last frame are the bare room (difference 0).

### Calls (art-pass, overrulable)

1. **The colour of the source (3.12).** Each bit reads its colour once from the board pixel it becomes (T5) or leaves (T6). Over a 9 px disc of the layer it belongs to, it takes the pixel at the 90th percentile of C*ab, so it gets the element's own colour (glass tint, chevron, slice ink, card art) and not a light edge line or an ink keyline. Its L* is held in 55-80 with a* and b* kept, so it reads on the night room and stays under the K type value (L* 84). The sources are:
   - the board layers without the tower and guns, for the rings and the frame band;
   - the ticket layer, for the ticket bits;
   - the tower layer, for the spinner bits;
   - each card, for its own bits (start points only on its coloured body, C*ab 20 or more).
   There is no skin colour list any more: the colour comes with the board.
2. **What that gives, measured (`metrics.json` `bits`).**

   | Stream | Neutral: C* median, share with C* ≥ 20 | Solace |
   |---|---|---|
   | Ring NOW | 27.6, 61 % | 27.6, 61 % |
   | Ring +1 | 11.1, 23 % | 9.2, 23 % |
   | Ring +2 | 6.6, 1 % | 6.3, 1 % |
   | Frame band | 8.2, 12 % | 6.3, 21 % (the green rim) |
   | Tickets | 7.3, 0 % | 6.1, 23 % |
   | Spinner (T6) | 57.6, 88 % | 57.6, 88 % |
   | Cards | 37.8-53.6, 100 % | the same |

   The ring +1, +2 and frame-band bits are slate grey-blue at L* 55 (median), because that is what those rings are: the cell fills are a neutral slate ladder by review call 1.3. The old bits were fixed skin colours, near white (neutral ring NOW was (217, 225, 234), L* about 89). Hue is kept to within dE 1.5 of the source on every stream.
3. **White-hot, flip, tumble (ART_BIBLE 1.2).** Every bit, the card trails included, starts at `HIT_PAPER` #DED8CA (the board's capped white) and turns to its colour over its first 80 ms. It flips 0 ↔ 1 every 70 ms and tumbles at 200-600 °/s, settling as it lands. The glyphs are Share Tech Mono (`corp/src/fonts`) with a same-colour outline of 1/22 of the size.
4. **Round the rim.** A bit goes from the lab out to an orbit at r 506-532 (the rim is r 500), round the rim the shorter way, then straight in along its target's radius. T6 runs the same path backwards. Every draw is logged: inside r 492, 0 draws sit off their own radial, on both skins (neutral T5: 3593 draws, 1774 inside the rim; T6: 3319 and 1655).
5. **K1 is the room as T4 leaves it (1.7).** K1 is the v3.1 bare room, which is the last frame of T4: frame mean L* 28.2; in the reviewer's room box (x 1200-1800, y 450-800) mean 47.8 and p95 80.3. It dims to the plate's room from K2 to the lock (`smoothstep((t - 0.25) / 0.75)`), which is what the v3 storyboard says ("The room dims to 55 % behind the board from K2 on"; the dimmed level is now the plate's own room grade) and what port spec 10 asks for ("bare to graded"). This withdraws the O-30 call of a graded K1 (frame mean L* 20.1, and 10.4 left of x 1100, where the board goes), which is what made K1 read black. T6 ends on the same bare room.
6. **Keylines and lock.** Each band's keyline head, destination ghost and lock arc take the median colour of that band's bits (L* at least 60), with the INK keyline. The spinner snap in T5 and the keyline that eats the spinner in T6 stay player pink #FF3DA8. The guns are their own pink layer.
7. **Bits in flight at 85 % alpha.** This gives margin on the local flash test over the dark city.
8. **Badges.** REAL = an existing render used as is (the published plate, the v3.1 room render, failure screen A). RENDER (violet) = rendered here by a generator from the board layers (`render3.py`, or `nf_trans.py` for the FAIL branch). COMP (cyan) = real renders composed. CONCEPT is retired: no frame carries it.
9. **T6 FAIL branch = failure screen A (O-26).** K5 is the netrun_fail glitch-in (`transitions/netrun_fail/scripts/nf_trans.py`) run on the published plate at 0.12 s. K6 is its frame at 0.60 s, which equals `transitions/netrun_fail/A_crt_feed.png` (max difference 0). The v3 concept terminal frame and tear are retired. The screen's numbers are its own tagged placeholders.
10. **T6 K4 is the v3 street** (r6 street render with mock room tags, the cleared room ticked): COMP. The T4-reverse iris and pull-out into it is not composited (Not done).

Timing is unchanged: T5 1.2 s, T6 0.8 s, with the same keys, easings and 90 ms lock. The spinner now does the storyboard's 4 % overshoot; the O-25 code did 1.4 % while the strips said 4 %. All the numbers and the 1080p radii are in `../GODOT_PORT_SPEC.md` section 10.

### Flash and frame values (CIE L*, `metrics.json`)

The method is in `metrics.json` `method`. Frame values are CIE L* of the frame-mean relative luminance, as in the reviewer's `measure.py`. Two flash tests run on the whole frame and on 120 px tiles (60 px at 960), at 25 fps:
- rel10, the O-25 method: a swing is a change of more than 10 % of the brighter frame;
- WCAG 2.x: a change of 0.10 or more in relative luminance with the darker frame under 0.80.

In both, a flash is an opposing pair of swings. The limit is 3 in any 1 s.

| | Neutral T5 | Neutral T6 | Solace T5 | Solace T6 |
|---|---|---|---|---|
| Frame mean L*, lowest to highest (25 fps) | 27.7-39.0 | 24.2-39.0 | 27.7-39.5 | 24.3-39.5 |
| Largest frame-to-frame step, L* (25 fps / GIF 12.5 fps) | 2.88 / 3.62 | 2.41 / 4.64 | 2.80 / 3.53 | 2.62 / 4.90 |
| Whole-frame flashes, rel10 / WCAG | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Worst 120 px tile, flashes in any 1 s, rel10 / WCAG | 3 / 0 | 3 / 0 | 3 / 0 | 3 / 0 |
| GIF | 3.17 MB | 2.36 MB | 3.22 MB | 2.38 MB |

No frame is brighter than the plate (L* 39.0 neutral, 39.5 Solace). The worst tiles are at the left frame edge (x 0, y 600 in T5; x 0, y 720 in T6), where the bit streams cross the dark street.

### Storyboard frames

- **T5 (neutral and Solace).** K1 is the bare room: REAL. K2 (0.38 s), K3 (0.55), K4 (0.85) and K5 (1.12) are RENDER. K6 is the published p1 plate: REAL.
- **T6.** K1 is the published plate: REAL. As in v3, a decide-beat plate stands in for the won state, because no won-state plate exists. K2 (0.20 s) and K3 (0.40) are RENDER. K4 is the street: COMP. K5 is the FAIL glitch-in: RENDER. K6 is failure screen A: REAL.
- **T2 and T3: no change to the frames.** Neither shows a combat board: the wheel-circle zoom was removed in v3 (ART CALL 49 item 3). The strips are rebuilt from the v3 sources with their badges.

### Not done

- **The T4-reverse pull-out inside T6.** `sbkit.pull_out` (the T4 iris and a 3.4x to 1x zoom back to the street) is written. Composited into T6, it fails the strict tile test: 5 opposing pairs in one 120 px tile in 0.8 s, over the limit of 3. So `t6_A.gif` holds the camera on the room and ends on the bare room, and storyboard K4 is the v3 street composite. To do: an iris with no bright ring, or a longer pull-out, then measure again (`PULL=1` in `render3.py`).
- **The local tile flash has no margin.** The worst tile is at 3 in any 1 s (rel10) in T5 and T6 on both skins, which is the limit. WCAG on tiles is 0. If the designer wants margin, the knobs are the bit density over the street and `BIT_A`.
- **Board defects carried into every board frame.** The frames are made of the published plate's layers, so the board items the gate-2 check found (pencil, W5/W6 ticket edge, FOCUS bracket colour, token disc peaks, thin structure lines) show in T5 K4-K6 and T6 K1-K3. They are fixed in `corp/src` by the board owner. When the plate changes, re-run the rebuild below: it re-stages and re-renders everything here.
- **Not checked:** the srv and gh rooms. The bit source points sit in the bio lab, so another room needs its own source points.

### Process

- Everything ran from script files. One slip: a stray `python -c "print(1)" 2>/dev/null | head -0` early in the pass. It is not a bare `python -` and wrote nothing, but it broke the "scripts by path" rule.
- Not done by rule: no Godot, no Blender, nothing committed, nothing written under D:/Godot/rebel_cell, no shared generator file edited. Only my own processes were stopped (two of my own `render3.py` runs, restarted with a fix).

### Rebuild

From `D:/rc_scratch/combat_redesign/locked/rebuild/transitions/`, one process per skin:
```
CORP=neutral python src/staged.py p1     # layers/<corp>_p1.npz + the compose check against ../final/
CORP=solace  python src/staged.py p1
CORP=neutral python src/bitstats.py     # bit colours per stream -> out/bits_<corp>.json + swatches out/bits_<corp>.png
CORP=solace  python src/bitstats.py
CORP=neutral python src/render3.py       # GIFs, strips, keys, metrics_<corp>.json (with the bits stats) -> out/<corp>/
CORP=solace  python src/render3.py
python src/build_sb3.py                  # storyboard strips + sheet -> sb/ (checks the FAIL K6 against A_crt_feed.png)
python src/publish3.py                   # copies to this folder, writes metrics.json
```

---

## History (superseded; kept as a record)

### Option A recolour on the O-29 board (roadmap step 7)

That pass recoloured bits option A (O-25) to the locked palette on the O-29 board, at 960 px for the GIFs and 1920 px for the storyboard. It ran from `D:/rc_scratch/combat_redesign/locked/transitions_work/src/` (`staged.py`, `render2.py`, `build_sb.py`, `publish.py`).

It gave these calls, all now replaced:
- ring glyphs in fixed corp skin colours (neutral steel greys (217,225,234), (166,180,198), (128,144,166); Solace lime #96FF46, leaf, teal);
- a 1-in-5 accent;
- a silver #E8EEF4 fourth keyline for the frame band;
- spinner glyphs by slice type, not by sampling.

Its storyboard K3-K5 (T5) and K2, K3, K5, K6 (T6) were CONCEPT, rendered at 960 px and enlarged. Review 1.7 and 3.12 were raised against that set.

Still in force from that pass:
- pink stays the player's;
- no dashed ghosts;
- the cards no longer dissolve as pixel blocks (that read as option B);
- the hand deal stagger is 30 ms, not the storyboard's 60 ms, so 4 cards plus SEND IT fit 1.05-1.20 s.

In that pass a bare `python -` was run once by mistake and was stopped; it wrote nothing.

### O-30 pass (2026-11-02)

T5, T6, both storyboard strips and the sheet were rebuilt on the O-30 board on both skins. The scripts ran from `D:/rc_scratch/combat_redesign/locked/fx_o30b/tr/src/`: the commands above with `render2.py`, `build_sb.py` and `publish.py`, and `mk_graded_room.py` first. Those copies were in `scripts/` until this rebuild and are now in git history.

The O-30 calls:
- K1 and the room T6 returns to were the bio bare room with the default grade and no scrim. That call is withdrawn by call 5 above.
- The flash results were measured on gamma luma, not L*: 0 whole-frame flashes, and a worst 60 px tile (at 960) of 3 per clip in T5 and T6. Its verdicts are kept in `metrics.json` `previous_o30`.
