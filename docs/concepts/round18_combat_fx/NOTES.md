# Round 18: combat FX (card play, damage shards, heat glitch)

All three are rendered on the locked combat screen: the round 13 D4 frame over the round 11 night boss fight (`combat_d4.png`). The wheels are re-rendered from the copied round 13 scripts, not pasted. This means the boss can really spin (the glyph blocks stay upright), and the HP arcs really drain after a hit. The overlay language is unchanged: vinyl stickers for cards and words, opaque grease pencil, light spill from glowing FX, and no spray paint.

## Files
| File | What it is |
|---|---|
| `card_play.gif` | 4.4 s, 960Ã—540, the full screen. HEAVY SPIN goes from the hand to THE MANIFEST, using dissolve A. |
| `card_play_storyboard.png` | 8 key frames (1:1 crops), plus the three dissolve options (A, B, C) at three moments each. |
| `damage_shards.gif` | 4.9 s, 960Ã—540 (a 1440Ã—810 crop scaled â…”). Four beats: your hit, the boss hitting your HP arc, a crit, and a blocked hit. |
| `damage_shards_storyboard.png` | 8 key frames, a severity tier strip (S, M, L, XL), and the reduce-effects end state. |
| `heat_glitch.gif` | 12 s, 960Ã—540, the full screen. COOL, NOTICED, FLAGGED, HUNTED, then the Options switch turned OFF. |
| `heat_glitch_storyboard.png` | 8 key frames (1:1 crops). |
| `fx_sheet.png` | A one-page overview of all three, with the timing, Godot and reduced-version table. |
| `scripts/` | Everything needed to rebuild (see Build). |

All timings below are in ms. The GIFs run at 25 fps (40 ms frames).

---

## 1. Card play: the sticker lifecycle
| Phase | t (ms) | What happens | Easing |
|---|---|---|---|
| Idle | loop | Hand cards bob 2 px (2.4 s loop). The top-right corner curl breathes, fold 0.02â€“0.04. | sine |
| Hover | 560â€“860 | The card lifts 100 px and scales to 1.36 (144â†’196 px wide), tilting âˆ’9Â°â†’âˆ’3Â°. The peel corner lifts to 0.17. The shadow grows from (3,5) blur 3 to (9,15) blur 8. Neighbours shift 14 px. The RAM meter hatches the cost. | out-back 1.3 |
| Peel off | 860â€“1100 | On press, the fold sweeps to 0.28 (140 ms), then the sticker pops free: Ã—1.1, fold relaxes to 0.07, shadow (22,34) blur 16 Î± 0.38. A faint die-cut liner outline stays in the slot. | in-out, then out-back 1.6 |
| Drag / aim | 1100â€“1700 | The card trails the cursor (spring lag 0.35, tilt = âˆ’vxÂ·0.012, clamped Â±12Â°). The yellow grease line writes on in 160 ms from the card's leading edge to the hub edge, and shortens as the card closes in. At 160 ms before the snap, a grease loop writes on around the wheel (valid target) and a `SPIN 9: THE MANIFEST` chip shows. | in-out |
| Slap | 1700â€“1940 | Drop 80 ms (Ã—1.1â†’1, shadow snaps to (2,3) blur 2 Î± 0.7). Squash 1.13/0.86 at contact (55 ms), overshoot 0.97/1.04, settle by 160 ms. A white contact ring (120 ms) and a gloss sweep (160 ms). RAM is paid here. The grease is wiped off stroke-first (wax doesn't fade). | in-cubic, then out-cubic / in-out |
| Dissolve A | 1940â€“2560 | A scan front runs topâ†’bottom in 300 ms. Each 13 px cell it passes decodes into a 0/1 glyph (Share Tech Mono, 14â€“20 px, white-hot for 80 ms, flips 0â†”1 every 90 ms). It holds 40 ms, then spirals **clockwise** (the spin direction) into the hub along a BÃ©zier in 260â€“430 ms, with a 2-copy trail. It is absorbed over the last 30 %, so nothing piles up. The hub ring brightens with each arrival. | t^1.5 (accelerates in) |
| Effect | 2380â€“3420 | The hub ring snaps out (180 ms). The wheel spins 108Â° (9 ticks) in 900 ms with an overshoot, and rotational blur proportional to the per-frame angle. A yellow arc on the telemetry ring marks the distance travelled, with a notch per tick and a `n / 9` counter. | out-back 1.25 |
| Close | 3500â€“3800 | The hand closes the gap, and the liner fades. | in-out |

**Dissolve options** (in the storyboard):
- **A, bit stream (picked).** It reads as "the card's data goes into the wheel", the swirl foreshadows the spin, and it reuses the damage-shard glyph atlas.
- **B, scanline decode wipe.** Rows turn into code, squeeze to 2 px scan lines and retract into one beam. It is calm and very legible, but reads as "printed out" more than "sent in".
- **C, glyph-pixel crumble.** The card turns into a mosaic of 0/1 tiles that crumble and are sucked in. It is the most physical, but the busiest, and it fights the slice art.

**Godot 4.7**
- **Card:** a `Control` (the sticker) with one CanvasItem shader for the peel and the gloss.
  - Uniforms: `fold` (0â€“1), `corner`, `gloss_t` and `backing_color`.
  - The shader reflects the UV across the fold line, draws the backing colour where the flap lands, and adds a 1 px crease and a flap shadow. This is exactly `fxlib.peel`.
- **Shadow:** a child `TextureRect` with the same texture, modulated black, plus a blur shader with an `offset`/`blur`/`alpha` tween.
- **Sequence:** a single `Tween` chain (hover, press, peel, follow, drop, squash, dissolve, effect).
  - The follow phase is a per-frame lerp in `_process`, not a tween.
  - Squash is a `scale` tween with the pivot at the card's bottom-centre.
- **Grease line:** a `Line2D` with a wax texture (or the existing marker shader), its points rebuilt each frame from the card to the target. Write-on and wipe use `points` slicing or a `trim` uniform; they never fade alpha.
- **Dissolve A:** a one-shot `GPUParticles2D` with the 0/1 atlas (shared with damage).
  - `emission_shape = POINTS`, with the points baked from the card's opaque cells. The scan order comes from the point list order plus `lifetime_randomness`.
  - A small particle process shader moves each particle along `bez(start, swirl_ctrl, hub)`, with `t = pow(age, 1.5)` and alpha â†’ 0 over the last 30 %. The stock attractors are 3D only.
  - The card sprite itself is masked with a `scan_y` uniform (the same shader as the peel).
- **Spin:** the existing wheel spin tween. The tick trail is a `Line2D` arc (or a ring shader with `from`/`to` angles), plus notch sprites.

**Reduced**
- *Reduce effects:* no peel or curl. The card slides to the target in 150 ms, shows a 1-frame white outline and fades out, with no glyphs. The spin plays at 2Ã— speed with no blur and no tick trail.
- *Reduce motion:* no hand bob, no tilt while dragging, and no squash. The card moves in a straight line.
- **Tier:** T2. The longest single segment is the 900 ms spin, which is the existing wheel motion, not FX.

## 2. Damage shards
**Rule:** shards are the **attacking slice's colour** in both directions. Pink for your ZERO-DAY, Meridian orange for the boss EXPLOIT. They burst from the hit point, so you always see *where* the hit landed.

| Beat | t (ms) | Notes |
|---|---|---|
| Tracer | âˆ’200 â†’ 0 | A comet along a BÃ©zier from the attacker's blade: a white head and a slice-colour tail. |
| Hit (T2) | 0â€“80 | Slice wedge flash â‰¤ 55 %, an impact disc 60 % (2 frames), and a pixel tear on the hit slice (3 frames, bands Â±10 px). Wheel shake 2 px for 90 ms. |
| Shards | 0â€“720 | Damped flight (k = 5.5/s) plus gravity of 260 px/sÂ² (520 when blocked) and spin of Â±900Â°/s. White-hot core for 100 ms, a 0â†”1 flip every 90 ms, a fade over the last 40 %, and "bit rot": from 72 % of life each glyph breaks into 3 pixels. |
| Number | 0 â†’ +620, fly 200 | Anton with an ink stroke and a lower half in the hit colour. It pops 1.5â†’1 in 120 ms (out-back 2.0), rises 24 px, then flies into the HP number (in-cubic, scale â†’0.45). The HP number ticks, and the wheel's HP arc is redrawn at the new value. |
| Your HP arc | | When you are hit, the drained arc segments flash white (80 ms) and *become* the shards. The spray goes sideways, away from the HP number, so the number is never covered. |
| Crit (T3) | | A 3-frame hit-stop (120 ms). The wheel region gets a 6 px RGB split during the stop and 3 px after it, plus 7 white crack lines (200 ms). 7 code streaks (`0110 1001`) fly 170 ms and then shatter into 42 shards. The burst is 44 shards up to 34 px with a 3 px RGB split for 220 ms. Shake 4 px for 140 ms. The number shows âˆ’24 with a `CRIT x2 PERFECT` chip. |
| Blocked | | The player's FIREWALL wall (crenellated cyan bricks) pops up 120 ms before the hit, **outside** the rim and between the hit and the wheel (the round 17 rule). It ripples white on impact. 22 dim shards bounce back off it under heavy gravity. 3 orange shards pass through. The result shows âˆ’2 with a `BLOCK 12 -> 2` equation chip. |

**Severity tiers** (put in content config, not code). The tier comes from the damage after block; a crit always uses XL.

| Tier | Damage | Shards | Glyph px | Speed px/s | Streaks | Shake |
|---|---|---|---|---|---|---|
| S | 1â€“4 | 9 | 13â€“18 | 420â€“720 | 0 | 0 |
| M | 5â€“12 | 18 | 16â€“24 | 520â€“960 | 0 | 2 |
| L | 13â€“24 | 30 | 20â€“30 | 600â€“1100 | 2 | 2 |
| XL | 25+ / crit | 44 | 22â€“34 | 700â€“1300 | 7 | 4 |

**Godot 4.7**
- **Shards:** pool one `GPUParticles2D` per hit in `CombatFxLayer`, configured as follows. The CPU fallback is `CPUParticles2D`, which is fine at â‰¤ 44 particles.
  - `one_shot`, `explosiveness = 1`.
  - `amount` taken from the tier table.
  - `CanvasItemMaterial` with `particles_animation`, `h_frames = 2` (`0`, `1`) and `anim_speed` set for the flip.
  - `damping` and `gravity` as above.
  - A `color_ramp` that fades over the last 40 %.
  - Blend add.
  - The bit-rot is a third atlas cell (a 3-pixel cluster) switched in with `anim_offset` at 72 % of the lifetime by the process shader.
- **Atlas:** the `binary_damage` concept's 0/1 atlas (Share Tech Mono with a same-colour outline of about 1/22 of the size). Dissolve A uses the same one.
- **Crit:**
  - Streaks: 7 pooled `Label`s, rotated to their velocity, tweened over 170 ms.
  - The second emitter uses `emission_points` at the streak ends.
  - Cracks: a `Line2D` fan.
  - RGB split: one short-lived `BackBufferCopy` + `ColorRect` (screen texture, `split_px` uniform) clipped to the wheel's rect.
- **Slice flash / pixel tear:** uniforms on the slice shader (`hit_flash`, `tear_seed`, `tear_amount`). They are per-slice, so they are never full-screen.
- **Numbers:** a pooled `Label` (Anton, outline) with a gradient material, tweened. The view precomputes the arrival time and schedules the HP tick, so the view never changes game state.
- **Limits:** VfxTier T2 (T3 for a crit). The burst radius is clamped by `VfxTier.clamp_radius`, and flashes go through the flash limiter (â‰¤ 3/s). When a flash is denied, the particles stay.

**Reduced**
- *Reduce effects:* no emitters, no flash, no shake and no tear. The HP is set at once, and a static `-n` chip sits next to the HP number (in the storyboard strip). Colour and number carry the meaning.
- *Reduce motion:* shards are kept, but there is no shake, no hit-stop and no streaks, and the number doesn't fly. It appears beside the HP number.

## 3. Heat glitch
One post effect with one `band` uniform. Each band **adds** to the one before it. The bands follow the Heat bands in `art_asset.md` A3 (and GDD 4.3: MAJOR thresholds at 25, 50 and 75). The effect runs as short periodic bursts, with nothing in between except the ambient layers.

| Band | Heat | Burst / period | Layers |
|---|---|---|---|
| COOL | 0â€“24 | 80 ms / 3.2 s | Luminance dip â‰¤ 7 % and two 2 px line jitters. |
| NOTICED | 25â€“49 | 160 ms / 2.6 s | Adds chromatic tears: 10 bands (4â€“44 px tall) slip â‰¤ 18 px, with a 4 px RGB split inside the band. |
| FLAGGED | 50â€“74 | 260 ms / 2.0 s | Adds a scanline roll (a bright band with 3 px lines and a sine row shift, running topâ†’bottom during the burst) and 48 macroblocks (copied from nearby, posterised, 80 % pulled to the corporation colour). |
| HUNTED | 75+ | 320 ms / 1.6 s | Adds a 14 px vertical-hold slip (2 frames), a 6 px full RGB split, 96 blocks, and ambient 7 % scanlines plus a corporation-colour edge tint. |

- **Never hides values:**
  - The glitch is a `CanvasLayer` **between** the world (city and wheels) and the HUD. The HUD, the hand, the stickers and the Heat chip are drawn above it, untouched.
  - The wheel discs (slice values) get only 35 % of the effect, through a protect mask texture.
  - Bursts are â‰¤ 320 ms with â‰¥ 1.3 s of calm between them.
  - Glitch states hold for 80 ms (2 frames). This looks right (steppy) and keeps it cheap.
- **Options:** Settings â€º Accessibility gets **HEAT GLITCH** (on by default), next to reduce effects, reduce motion and the flash limiter. When it is off, nothing moves at any Heat. The static corporation edge tint (HUNTED) and the HEAT chip still show the level.

**Godot 4.7**
- Use a `ColorRect` (full rect) on `CanvasLayer` layer = HUD âˆ’ 1, with a `canvas_item` shader that reads `hint_screen_texture`.
- Uniforms:
  - `intensity` (0â€“1, the burst envelope, driven by a small script on a timer: `period` and `burst` from the band table in `campaign_config.tres`);
  - `band` (0â€“3);
  - `seed` (changes every 80 ms);
  - `protect_mask` (`sampler2D`, from a `SubViewport` with the wheel discs, or two circle uniforms);
  - `corp_color`, `split_px`, `slip_px`, `roll_y`.
- Each layer is a few lines in the fragment shader:
  - tears: `floor(UV.y * rows)` hashed with `seed`, giving an x offset and a per-channel split;
  - roll: a Gaussian in y around `roll_y`, with a 3-row line mask;
  - blocks: a 16â€“64 px grid hashed with `seed`, then a UV offset, posterise and a mix to `corp_color`;
  - slip: a `UV.y` offset;
  - scanlines and edge tint: always on at HUNTED.
- The script sets `visible = Settings.heat_glitch and not Settings.reduce_effects_full`. **Schema/settings change needed:** add a `heat_glitch: bool = true` to `settings.gd` (snapshot/restore and save keys), and log it in DECISIONS.md.
- **Tier:** T0 ambient (the coverage is full-screen, but it carries no flash and the bursts are short). If the tier gate refuses full-screen below T4, register it as a post layer that is exempt because it never adds light. **This is open for the designer.**

**Reduced**
- *Reduce effects:* tears only, at the NOTICED strength, at most one burst per 3 s. No roll, no slip and no RGB split.
- *Flash limiter on:* the COOL luminance dip counts as a flash and is skipped.
- *Reduce motion:* no slip and no roll; tears and blocks are kept.
- *HEAT GLITCH off:* static edge tint only.

---

## Layer order (combat, back to front)
1. City base plus light spill.
2. Wheels (slice shaders, with the tear and flash uniforms).
3. **Heat glitch post** (CanvasLayer).
4. FX world layer: tracers, shards, the dissolve stream and the wall. These are additive and spill light.
5. HUD (tags, HP numbers, RAM, buttons).
6. Overlay stickers (name plate, SEND IT).
7. Hand.
8. The moving card and its shadow.
9. Damage numbers and equation chips.
10. Grease pencil.
11. Cursor.

The dissolve stream sits on layer 4, but it is spawned *after* the card's slap, so it reads as coming out of the card.

## Recommendation
- **Dissolve:** **A, bit stream.**
- **Damage:** keep shard colour = attacking slice colour, and let the drained HP segments themselves become the shards when you are hit (new this round). It ties the burst to the value that changed.
- **Heat glitch:** ship it with the protect mask from day one. Without the mask, HUNTED makes the boss's slice values unreadable during a burst.

## Weakest parts / open questions
- **Crit burst:** the 44 large shards with a 3 px RGB split read as a red/blue clump for about 100 ms before they spread (frame 06 of the damage storyboard). A real particle system with additive blending should open up faster; otherwise lower the XL count to 36.
- **Dissolve A density at the hub:** the stream reads as a golden swirl rather than individual 0/1 glyphs at 960Ã—540. Individual glyphs show at 1080p. A lower cell count (16 px cells) would make the glyphs more legible.
- **Heat COOL** is nearly invisible by design. The designer should confirm that band 0 should glitch at all (the alternative is nothing below 25).
- **The boss banner** is part of the wheel render, so it glitches at HUNTED (frame 05). If it should stay clean, move the banner into the HUD layer.
- **Open:** does the Heat glitch need its own setting, or should it fold into reduce effects? This round shows its own switch, as ART_FEEDBACK_R2 item 11 asks.

## Build
Run everything from `scripts/`. It needs Pillow and numpy, and the round 11 backdrop cache (`round11_combat_target/scratch/backdrops`, read-only).

1. `python plates.py warm` renders the two D4 wheels (about 25 s).
2. `python card_play.py` (about 3 min the first time, including about 20 spin renders).
3. `python damage_shards.py` (about 2 min, including 4 HP-state renders).
4. `python heat_glitch.py` (about 1 min).
5. `python make_sheet.py`.

Renders are cached in `scratch/r` (git-ignored). The copied round 13 scripts are unchanged. The new files are `plates.py` (the layered combat plate), `fxlib.py` (glyphs, glow, RGB split, peel, GIF and storyboard output), the three FX scripts and `make_sheet.py`.
- The GIFs use one global palette, no dither, and unchanged pixels â†’ transparent, which keeps them at 2â€“3.5 MB.
- Seeds are fixed, so reruns match.
