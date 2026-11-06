## G. Effect overlays (designer note 7)

**Rewritten 2026-11-04 (art-pass, round 2 docs pass)** to describe the effects as they are published in `locked/effects/`: the 2026-11-03 rebuild, rendered on 2026-11-04 between 03:38 and 04:45. The plan this replaces (wedge-wide plates, three print echoes, white block sparks, an orange Twist sweep, lengths in frames) is in git at b26022f5 and earlier. Sources: `locked/effects/timings_MPST.json`, `timings_CDHL.json`, `NOTES_MPST.md`, `NOTES_CDHL.md` and `locked/port/fx_timings.json`. Their numbers are measured on the 60 fps frames that the published keyframes are cut from, as those notes state. Every row here is an art-pass call, not a designer ruling, except where a DR is named.

**Round-2 status.** The effects set was **not** re-rendered on the round-2 board. Its bases are the gate-1 board: the pencil before C1, the HUD rows before C8, the ticket edges before C5 and the leaf-green Solace rim before C16. On Solace, `fx_wave_enter`'s scan line is #96FF46. The set reads P stock from its own `fxk_lib` (#F6C8DE, the same value as the `P_STOCK` token, C15). The block-vs-break comparison copy on `fx_block_vs_break.png` throws white sparks, while the real P block throws P-stock sparks. The C12 skip hint is not in the published beat. All four are open.

**What holds for every effect**
- **Footprint.** One overlay per event, on a slice (the wedge or its trim band), a cell, an arc, a ring, or a path from the rim to the HUD. No slab and no flat wedge tint: both were retired in the rebuild.
- **Length.** Every effect is 600 ms or less (`CAP_MS` / `T2_CAP_MS` 600, no per-effect override; both registries assert it). Lengths and keyframes are given in ms.
- **Layer (review 1.6).** First the board layer (room, scrim, board, tower, units, arcs, guns, tags, digits). Then the effect. Then the HUD, YOU strip, hand, UNDO, nameplate and SEND IT. Three effects draw over the HUD, all allowed: `fx_hp_through` (up to 6580 px on the HUD), `fx_refund` (1091) and `fx_trace_add` (1696). Every other effect changes 0 HUD or hand px.
- **Flash (GDD 9.6).** In full motion every effect is at 2 flashes per second or less (`fx_slice_crack` and `fx_trace_add` 2, the rest 0-1); in reduce motion 1 or less. The limit is 3. Each effect has a reduce-motion form: no travel, no sparks, no glitch; the marks appear, hold and dissolve. Each strip ends in a yellow-framed reduce-motion tile.
- **Loudness (review 2.10).** On the shared gated meter (`fxk_lib.loud_frame`) the order is damage > kill > block > state on all three skins. Neutral values: damage 2817 (`fx_hit_land`) to 9540 (`fx_firewall_burn`); kill 1813; block 841 (`fx_soak_take`) to 1677 (`fx_brace_block`); state 85 (`fx_clear`) to 761 (`fx_hold`). The thinnest margin is block over state: 80 (73 on Solace).
- **Colour by cause and owner (E).** `CELL_PINK` for anything the player or a card does; `HARM` for what the enemy does to you; `SCHEDULE` for the clock; `GAIN` only on the L family; the skin's own enamel ink for corp state; `BOSS_GOLD` for the ward. On every 60 fps frame: 0 `GAIN` px on every non-L effect and 0 `FOCUS` or lime px on every effect. Yellow is in the resolve only as the commit's pencil marks while they burn into pink.

**The families, as drawn**

| FX family | Material on the plates | Colour |
|---|---|---|
| **FX-P Protect** (your defence holds) | P stock, never the card bone `PAPER` (review 3.10). The shield block is a small plate on the slice's trim band (r 186-204, 26 deg) that slams 1.2 to 1.0 with its tally ticks; the incoming chevrons stop dead at its edge and throw P-stock sparks. Brace is four clamp brackets on the wedge corners, a bar the chevrons crumple on, and a 16 px stamp on the arc glyph. Soak is the funnel and the pip fill. No wedge tint, no soak wash | `P_STOCK` #F6C8DE (shade #D696B8); `SOAK` on the funnel |
| **FX-H Harm** (the enemy hurts you) | Misregistered red print: an X-only halftone flood (crossed marks, never round dots), black krackle with a 2 px red offset, a red stencil X. A broken shield is the P-stock plate in shards | `HARM` + `INK` |
| **FX-D Damage** (we hurt them) | The player's comic hit frame: a painted pink tracer (a tapered ribbon with an ink key), an ink-keylined starburst with a white core, converging white speed lines cut at the tower rim (r 199), flat vector shards. A kill is in the cause colour, with a pink-tint core and no word | `CELL_PINK` (kill marks L* 59.4) + white |
| **FX-L Life** (gain) | The one soft glow: brush strokes, plus signs, a painted check, four-point sparkles. Ranked with the state changes | `GAIN` on dark; mint (214, 255, 206) with an ink key on the green REPAIR wedge; `NET_CYAN` for the RAM coin |
| **FX-M Motion** (things move) | No echoes and no smear: the print echoes were the loudest light of every motion effect, and are retired. One solid arrow: a 3 px core, a 2.5 px ink casing and an 11 px open head. On spin, twist, shove, rings step and Hold it is a stub (60 / 30 / 30 / 32 / 22 deg) that runs ahead of the mover and is eaten when the mover arrives; pull and the bump keep a short whole arrow. The mover turns or slides, overshoots a little and settles back | By owner: `CELL_PINK` for the cards (spin, twist, pull, shove, bump); `SCHEDULE` for the clock (rings step, Hold's slide), with the Hold stamp in the clock's gunmetal; neutral `ENAMEL` for the wave feed. The corp hue is only `fx_wave_enter`'s scan line that draws the new cell edges (DR-6) |
| **FX-C Corp** (the enemy changes state) | One 1.6 px vector scan line with a 1 px ink key, then one flat 4-frame flash on the new mark only. No slab, texture or trail | The skin's enamel ink: `ENAMEL` #D9E1EA (neutral), celadon #B8DCCC (Solace), rust #D88A4E (Meridian); `BOSS_GOLD` for the ward |
| **FX-S System** (Trace) | One glitch band per 33 ms step, 4-7 px tall, over the card and then the Trace row, while the next Trace pip lights | `TRACE_VIOLET` |
| **FX-T Commit** (SEND IT) | A burn front runs the pencil marks from yellow to pink paint, with a white-hot edge of 1.8 % of the route at 60 %. A ping at the route end, then the board, HUD and hand step from preview to resolve | `PLAN` to `CELL_PINK` |

**Every published effect** (32 ids; total ms; the main phases in ms; "latent" means no source in the E10 state, drawn on real units with stand-in marks)

| Id | Event (state source) | FX | Footprint | What it draws | ms |
|---|---|---|---|---|---|
| `fx_shield_block` | SHIELD slice absorbs a landing (f1: absorbed 6) | P | Trim band | Chevrons arrive (0-160); the P-stock plate slams 1.2 to 1.0 (110-170); impact, stop dead, P-stock sparks (160-280); hold; the plate lifts off (440-600) | 600 |
| `fx_brace_block` | Brace blocks a whole landing (f2: TURRET, braced_hit) | P | Slice and arc | The lane draws in; four clamp brackets close 1.12 to 1.0 (60-180); the chevrons run the lane and crumple on the bar (80-330); the stamp slams 1.2 to 1.0 on the arc glyph (330-400); all lift off, the printed glyph stays | 600 |
| `fx_soak_take` | A soaked slice takes the overflow (f2: SHIELD sector 1, soaked 1) | P | Slice | The overflow chevron arrives; the funnel draws in (80-220); the chevron shrinks into its mouth; the pip fills (300-420) | 600 |
| `fx_shield_break` | Our SHIELD slice breaks while blocking (f1: sector 1 hp_after 0) | H | Slice | The plate cracks (20-90) and splits into P-stock shards (100-460); red flood, krackle; the wedge darkens (160-420); the pips go | 600 |
| `fx_hit_land` | Landing hit, one pip lost (f1 log "hit") | H | Slice | Chevrons in (0-80), a frame flash, the X-halftone flood (80-200), krackle (100-440); the pip goes dark at 200 | 600 |
| `fx_hit_land_worm` | Worm wear (variant) | H | Slice | As `fx_hit_land`, plus a hook mark | 600 |
| `fx_hit_land_adjuster` | Adjuster strike (variant; latent) | H | Slice | As `fx_hit_land`, plus a gold rim flash | 600 |
| `fx_slice_crack` | Slice goes 2 to 1 | H | Slice | Flood pulse, a jagged crack across the glass off the icon (50-220), a tip spark, krackle | 500 |
| `fx_slice_break` | Slice goes to 0 (ability lost) | H | Slice | Flood, frame flash, a red stencil X stamped in the outer corner, never on the icon (100-170), black-out (130-400), a halftone fade over the icon | 600 |
| `fx_hp_through` | HP gets through (diamonds to YOU) | H | Rim to the YOU strip, over the HUD | The diamonds lift off at 44 deg, before the arc's "3" (0-140), fly (60-460) and slap onto the YOU strip (400-520); the hatched segments go dark | 600 |
| `fx_gun_hit` | Gun shot hits (f1 guns: hit) | D | Cell | The pink tracer paints (0-80); the hit frame opens: starburst R 44 (80-140), 14 converging speed lines, shards; the HP tick goes gone (140-230) | 600 |
| `fx_strike` | Strike card hits for 2 (latent) | D | Cell | A painted slash (0-90), starburst, speed lines, shards; two ticks go | 600 |
| `fx_trigger_hit` | Trigger hits units along its path (f2 tlog trig_unit) | D | Cells on the path | The route ignites from pencil to pink paint (0-240); a burst at s3 at 120 ms and at s4 at 240 ms | 600 |
| `fx_firewall_burn` | Firewall burns a sector (latent) | D | Sector column | Pink flame bands ring by ring (0-160, 60-220, 120-280), cut clear of the tokens and the wave tags' dots; the ticks; embers (380-600) | 600 |
| `fx_kill` | A unit dies (f1: Worm 2 shot dead; f2: Packet 1 Trigger-killed) | D | Cell | A flare on the token (17-50), the KO starburst, speed lines, vector shards; the cell empties (160-380). No word | 600 |
| `fx_ricochet` | Shot glances off armour (latent) | D | Cell | Tracer, a steel glint and sparks off the L10 cap | 500 |
| `fx_ricochet_gold` | Shot weakened by the ward (f2: BURST 4 to Packet 6, ward x2) | D | Cell | Tracer and a gold streak off the lozenge; no starburst. In E10 the warded shots deal 0, so no HP changes | 500 |
| `fx_repair_mend` | REPAIR mends 1 pip (latent) | L | Slice | Brush strokes rise (0-450), plus signs, the pip fills (260-400) | 600 |
| `fx_refund` | Trigger-kill refund, +1 RAM (f2) | L | Cell to the RAM row, over the HUD | The coin pops 14 px off the board's own refund coin with one thin cyan ping (0-90), flies to the RAM row (90-400), and the slot and the REFUND tab light | 600 |
| `fx_clear` | Nothing gets through (arc check) | L | Arc | A painted check at r 443, 78 deg, clear of the arc's diamonds and its "3"; glow and sparkles | 400 |
| `fx_spin` | Spin 3 turns the tower | M | Whole tower | A pink arrow stub runs ahead and the gun preview fades (0-100); the tower turns 183 deg (100-500) and settles back 3 | 600 |
| `fx_twist` | Twist turns ring +1 one sector (f2: [1, 1]) | M | Ring +1 | Pink arrow stubs draw (0-90); the ring turns 61.5 deg (90-430) and settles back 1.5 | 540 |
| `fx_pull` | Pull drags a unit inward | M | Two cells | A short pink arrow; the cell slides 59 px (90-400) and settles back 2 | 500 |
| `fx_shove` | Shove slides a unit one sector | M | Two cells | A pink arrow stub; the cell slides 62 deg (90-400) and settles back 2 | 500 |
| `fx_shove_bump` | Shove collision (variant) | M | Both cells | Arrow; the cell slides toward the shared edge; a bump line, two small pink starbursts and shards (200-320); it springs back. No HP change is drawn (RULES, open) | 480 |
| `fx_rings_step` | The rings step in at END TURN | M | All rings | A `SCHEDULE` tape arrow stub (0-100); every ring spirals in, -57 px and +120 deg (100-480) | 600 |
| `fx_hold` | Hold puts a 0 in the schedule | M | Bezel | The gunmetal hourglass stamp slams (0-100) and hands over to the printed HOLD glyph; the band turns over while a `SCHEDULE` stub runs the slot (100-420) | 560 |
| `fx_wave_enter` | The next wave enters ring +2 | M | Ring +2 and the queue | The feed arrow lights and the W4 ticket lifts (0-80) and rides into the entry (80-360); the cells scan in and the glyphs drop (300-480); the queue moves up one slot (360-540) | 600 |
| `fx_grow` | A unit grows +1 hit | C | Cell | The enamel scan line (0-133), then a flash on the new hollow chevron (133-200) | 400 |
| `fx_ward_on` | Ward applies to the units in the Adjuster's sector | C | Cell | A gold scan line (0-133), a flash on the lozenge, one thin ping | 400 |
| `fx_trace_add` | A loud card adds Trace (Trigger +1) | S | Card and the Trace row, over the HUD | The card glitches in 5 steps (0-166); the next pip pops in 3 steps while the row glitches (166-266) | 400 |
| `fx_commit` | SEND IT, or a Trigger resolving now | T | Plan marks, then the whole frame | SEND IT press (0-60); the burn front runs the marks (60-400); a ping at the route end (400-520); preview to resolve (400-600) | 600 |

The C/D/H/L designer also keeps a 500 ms `fx_shield_block` copy, used only on `fx_block_vs_break.png` (see Round-2 status). **Pruned (R51 review):** `fx_worm_wear` and `fx_adjuster_strike` are the `fx_hit_land` variants; `fx_armor_bounce` and `fx_ward_bounce` are `fx_ricochet` and `fx_ricochet_gold`. **Parked (latent):** `fx_jam`, `fx_shield_pop`, `fx_boss_phase` and `fx_lockdown`, which are not drawn.

**The resolve beat** (E10 p3; review 2.11; `timings_MPST.json` `resolve_beat_e10`, `resolve_beat_strip.jpg`, `resolve_beat.gif`)
- **Length.** 3800 ms against a 4000 ms limit. 17 tracks overlap, each its designer's own effect at its own timing, in the HUD chain order: commit 0-600, twist 420-960, trace_add 600-1000, trigger_hit 760-1360, kill (Packet 1) 1000-1600, refund 1100-1700, gun_hit 1300-1900, gun_hit on the Adjuster 1360-1960, ricochet_gold 1420-1920, kill (Worm 2) 1560-2160, shield_block and brace_block 1900-2500, soak_take 1930-2530 (under the shield plate), clear 2400-2800, the board settle 2640-2840, rings_step 2800-3400, wave_enter 3200-3800.
- **Skip.** Any input dissolves the frame to the settled frame in 200 ms (easeInOutCubic). The published beat has no on-screen word. C12 (a "SKIP" key hint at the HUD edge) is not published.
- **Flash over the whole beat** (neutral): whole frame 0, track boxes 1, 240 px tiles 2, 120 px tiles 2. One 60 px tile holds 3 in one second: the kill and gun-hit cluster on Worm 2, at the limit. Reduce motion: 2 at most.
- **Kills.** Both kills are `CELL_PINK`, with 0 `GAIN`, `FOCUS` or lime px.
- **NOT TO SHIP (RULES).** The beat draws ring +1 one sector back from SEND IT until Twist turns it (0-960 ms), because f2 holds ring +1 where Twist leaves it while the plates draw it untwisted. The bump draws no HP change. Both wait for the designer and the GDD.
- **Open.** Packet 1 is never seen alive, because p2 already draws it trigger-dead. The Adjuster shot has no HP-tick change in the beat.

