### 8.4 Family looks (what each draws; must keep; `effects/NOTES_MPST.md` and `NOTES_CDHL.md`, rebuild 2026-11-03)
- **M motion:**
  - **no print echoes** (retired in the rebuild: on the shared loudness meter the echo copies were the loudest light of every motion effect);
  - the arrow is one solid line, never dashed: a 3 px core with a 2.5 px ink casing and an 11 px open head. On spin, twist, shove, rings step and Hold it is a stub (`ARROW_STUB`) that runs ahead of the mover and is eaten when the mover arrives; pull and the bump keep their short whole arrow;
  - colour by owner (VISUAL_PLAN E, R51): cards (spin, twist, pull, shove, bump, the commit ping) are CELL_PINK; the clock (rings step, Hold's slide) is SCHEDULE and the Hold stamp is the clock's gunmetal; the wave feed is neutral ENAMEL; the corp hue moves only as the `fx_wave_enter` scan line that draws the new cell edges (DR-6). Yellow never appears in resolve.
- **P protect:** everything on the **P stock** (`p_stock`, section 3), never the card bone PAPER. The shield plate is small, on the trim band; the brace is four clamp brackets on the wedge corners and a small stamp that slams to size; the sparks are P stock. The flat wedge tint and the SOAK wash are retired; SOAK stays a mark (the soak funnel, DR-5). No starburst, no red, no glow.
- **S system:** the glitch shader (5.7), one glitch band per 33 ms step.
- **T commit:**
  - pencil yellow becomes pink along each mark in route order, with a narrow white-hot burn edge: a Line2D gradient whose offset is tweened along a per-mark distance-along-path;
  - then a pink ping at the route end.
- **C corp:** one clean vector scan line with an ink key, in the skin's own `c_scan_ink` (section 7), then one flat 4-frame flash on the new mark only. BOSS_GOLD for the ward. No slab, no texture, no trail; never pink and never the clock's colours.
- **D damage:** the player-owned comic hit frame: a painted pink tracer (a tapered ribbon with an ink key), an ink-keylined CELL_PINK starburst with a white core, converging white speed lines cut at the tower rim, and flat vector shards. Kills are in the cause colour. No Ben-Day.
- **H harm:**
  - misregistered red print: the X-only halftone flood (5.8; crossed marks, never round dots);
  - black krackle with a red 2 px offset (sprites);
  - the red stencil X;
  - slice-wide, with the icon seat (r 37) clear except on shield_break and slice_break; the broken shield is the P-stock plate in shards.
- **L life:** the only soft glow, with additive blend and small radius:
  - brush strokes, plus signs, a painted check, four-point sparkles;
  - GAIN on dark; mint with an ink key on the green REPAIR wedge;
  - the RAM coin in NET_CYAN. L ranks with the state changes.
- **No family** draws dashed or dotted lines (trails are one continuous tapered ribbon), uses the needle, or adds cross-hatch (an effect resolves hatch into a gone socket or a dark pip). Pink stays the player's; gold is the boss's.
- **Loudness order** (review 2.10), measured on 60 fps frames, every skin:

<!-- gen:loudness begin -->
<!-- gen:loudness end -->

---

