# W6 — VFX tiers and shader library (branch `art/w6-vfx`)

ART_BIBLE §8 (VFX tiers), §13 (shader library), §12 (reduce effects). Presentation only:
no rule, content value or save format changed.

## Review images

| File | What it shows |
|---|---|
| `perfect_before_after.png` | Top: the old Perfect landing, a full-screen CELL_PINK flash (captured from the unchanged code first). Middle and bottom: the new T3 `wheel_burst` (glow + ring pulse on that wheel only). |
| `phase_before_after.png` | Top: the old boss-phase full-screen corp-colour flash. Below: the new T3 broken ring in the corp hue on the boss's wheel. |
| `hits_<kind>.png` (7) | Each slice type's hit shape, real size x1.5, 67 ms apart: crit, attack, shield, evade, afflict, heal, miss. |
| `hits_greyscale.png` | All seven side by side at four moments, greyscale only: each reads by shape. |
| `shaders.png` | The shader lab (`tools/design_lab/shader_lab.tscn`): glass_blur, crt_overlay, paper_burn, glitch_dissolve, marker_stroke, halftone. |
| `reduce_effects.png` | With reduce effects on: the shader lab is static (no roll, flicker or fringe; glitch_dissolve is a plain cross-fade), and hit shapes and bursts draw nothing (the end state at once). |

## What changed (files)

- `shaders/lib/rc_common.gdshaderinc` (new): the shared include. It holds the one `global uniform float reduce_effects` and the helpers `rc_live()`, `rc_time()`, `rc_hash()`, `rc_noise()`, `rc_luma()` and `rc_scanline()`.
- `project.godot`: `[shader_globals] reduce_effects` (float).
- Every existing shader includes it, and its animated parts go static under reduce effects: `city_lights` (clock stops), `city_live` / `city_sketch` / `crt_panel` (flicker), `distortion` (off), `jack_cover` (roll), `scanline` (flicker and aberration). `influence_reveal` and `zine_paper` were already static. The scripts still zero these values themselves too.
- `shaders/glow.gdshader`: deleted. A grep of `.gd`, `.tscn`, `.tres`, `.gdshaderinc` and `project.godot` found no reference to it.
- New shaders: `glass_blur`, `crt_overlay`, `paper_burn`, `glitch_dissolve`, `marker_stroke` and `halftone`.
- `tools/design_lab/shader_lab.gd/.tscn` (new). It takes `--progress=`, `--animate` and `--reduce` (the reduce flag lasts for that run only and is never saved).
- `scripts/data/ui_motion_entry_data.gd`: schema change, `tier: Tier` (T0–T4, default T1), validated. `tools/schema_smoke_test.gd` covers the round-trip and checks every shipped entry.
- `content/config/ui_motion.tres`: an explicit `tier =` on all 201 entries. There are 9 new entries: `wheel_burst_perfect`, `wheel_burst_phase` and `hit_vfx_{crit,attack,shield,evade,afflict,heal,miss}`. No existing duration or ease changed; `raid_move` is T2.
- `scripts/data/ui_motion_data.gd`: the 9 new ids are added to `REQUIRED_IDS`.
- `scripts/ui/fx/vfx_tier.gd` (new, `VfxTier`): the tier limits and the clamps.
- `scripts/autoload/fx.gd`:
  - sets the global uniform from Settings;
  - `flash(..., tier)` is T4 only and does nothing under reduce effects;
  - adds `request_flash()`, `shake_px(id)` and `refused_flashes`;
  - caps the hit-stop by tier.
- `scripts/ui/kit/combat_fx_layer.gd`:
  - adds `wheel_burst`;
  - puts `disc_flash` through the limiter, held to its tier;
  - adds the seven hit shapes and wires them to the layer's existing triggers.
- `scripts/ui/kit/raid_fx_layer.gd`: adds `FX_MOTION` / `fx_tier`; the hit ring's reach and the district wash's alpha are held to their tiers.
- `scripts/ui/combat_scene.gd` (grant): changed only the two flash call sites (Perfect and boss phase).
- `tools/design_lab/motion_lab.gd`:
  - demos for the new ids;
  - `precision_perfect` and `boss_phase_flash` now show their real motion (the burst);
  - the `screen_flash` demo is T4;
  - new flags `--demo-hits-row` and `--demo-reduce` (lasts for that run only).
- Tests (all fast): `test_shader_library.gd`, `test_vfx_tiers.gd`, `test_hit_vfx.gd`. In `test_motion.gd`, `Fx.flash` now passes T4 and expects the T4-clamped alpha.

## Tier table as implemented (`VfxTier`)

| Tier | Coverage | Max duration | Flash alpha | Shake | Hit-stop | Entries |
|---|---|---|---|---|---|---|
| T0 ambient | backdrop | loop (period floor 3 s) | 0 | 0 | 0 | 10 |
| T1 feedback | element + 16 px | 0.25 s | 0.2 (+20% glow) | 0 | 0 | 70 |
| T2 outcome | element + 25% of region | 0.6 s | 0.6, local | 2 px | 2 frames | 87 |
| T3 moment | the region | 1.2 s | 0.7, local | 4 px | 3 frames | 24 |
| T4 cinematic | full screen | 2.5 s | 0.4 white, once | 0 (camera) | 0 | 10 |

How the limits are enforced:
- Only T4 may cover the whole screen. `Fx.flash` refuses any lower tier (a debug warning) and defaults to T3, so a caller has to say T4 explicitly.
- One limiter (at most 3 flashes a second) governs every flash: full-screen, `wheel_burst` and `disc_flash`.
- Every effect the FX layers draw is clamped to its entry's tier: alpha, seconds and reach.
- The duration cap covers only what the FX layers draw. UI motion (spins, typing, holds, number rolls, page moves) keeps the ART_BIBLE §10 budgets.
- 30 such entries run past their tier's VFX duration. None of them is drawn by an FX layer:
  - T1: saved_stamp, toast, wheel_spin, site_outline_draw, map_camera_ease, route_pulse, visited_dim, loot_fan, count_up, drip_grow, drip_halo, number_roll, drop_zone_pulse, wheel_respin, inner_ring_turn, pointer_migrate, pointer_orbit, enemy_turn_spin, minimap_pulse, ram_pending_blink, send_it_ready, toast_note_hold, city_bake_fade, route_target_pulse, ram_spend_float, asset_drop_wait, ram_refill_float;
  - T2: resolve_sequence, forecast_change;
  - T4: jack_arrival_wait.

## ART_BIBLE §14 checklist (for what W6 touched)

| Item | Result |
|---|---|
| §3 tokens only | **Pass**. Colours come from `Palette`, including `slice_color` for hit shapes. Shader colour defaults are uniform defaults that views override. The `glass_blur` tint waits for W1's `SCRIM` (marked `W1-TOKEN: SCRIM` in the lab). |
| Materials not mixed | **Pass**. The CRT stays on city and glass only; paper_burn, marker_stroke and halftone are PAPER. |
| Focal order / states / text scale / pad | **n/a** (effects, not components). Hit shapes are sized in px from the motion table and do not scale with text. |
| Readable in greyscale | **Pass** (`hits_greyscale.png`). |
| Motion within §10 and VFX within tier; reduce effects shows end states; no full-screen flash below T4 | **Pass**. The tests check each of these, including a grep test over every `Fx.flash(` call. |
| No leftover elements after transitions | **Pass**. `clear()` drops bursts and hit shapes, and nothing is added when motion doesn't play. |
| Review stills and strips | **Pass** (this folder). |

## Decisions (one line each)

1. `Fx.flash` defaults to `tier = T3`, so a full-screen flash must pass `VfxTier.T4` explicitly (§8).
2. `screen_flash`'s 0.45 amplitude is clamped to T4's 40% at runtime. The value itself is unchanged (§8).
3. Local flashes (`wheel_burst`, `disc_flash`) share the one limiter through `Fx.request_flash()`, so `victory_flash`'s 0.8 alpha is held to T3's 0.7 (§8).
4. The Perfect and phase bursts have entries of their own (`wheel_burst_*`). The old `precision_perfect` and `boss_phase_flash` still act as on/off switches and keep their values (§8, §15).
5. The phase ring alternates long and short dashes, a CorpPattern-like broken ring, until W1's `CorpPattern` lands (marked `W1-CORPPATTERN`) (§3.6).
6. DEPLOY maps to the attack slash, because a deploy's effect lands as drone hits. DEFEND and SHIELD share the hex plates (§8).
7. The existing triggers are mapped by the data the layer already receives:
   - a crit number shatters (this replaces the old star burst);
   - a travelling "+N" shows plus signs, any other travelling number a slash;
   - a guard glyph shows hex plates or a smear;
   - a status stamp shows the glitch crawl.
8. Tier assignment:
   - loops and ambience are T0;
   - hover, focus, UI moves and holds are T1;
   - hits, stamps, drops, buys and refusals are T2;
   - Perfect, kill or break, phase, Heat band, claim or influence, and VICTORY or DEFEAT are T3;
   - the jack and `screen_flash` are T4.
9. `raid_move` is T2, the threat token's step (an outcome).
10. `glass_blur` stays on under reduce effects, because it doesn't move; high contrast's opaque panels are W9's call (§12).
11. `glitch_dissolve` becomes a plain cross-fade under reduce effects (§8: "T4 becomes a cross-fade").

## Couldn't do / known gaps

- **Miss static is not triggered in play yet.** The Miss landing lives in `combat_scene._land` (W3's file). The API is ready: `fx_layer.hit_vfx(v.slot_spot(slot), CombatFxLayer.HIT_MISS)`.
- **Corrupted self-damage shows a slash.** A travelling damage number doesn't carry its source slice, so W3 should pass the real kind (`slice_hit`) at the impact.
- **The hit shake and hit flash are outside my files.** `WheelView.hit_shake` (3 px, over T2's 2 px) and `hit_flash` belong to W3. W3 should use `Fx.shake_px(&"hit_shake")` and `Fx.request_flash()`.
- **The motion lab's "copy values" drops the tier.** `Motion.tres_lines` (in `motion.gd`, not my file) doesn't print `tier`.
- **The new shaders aren't used on any screen yet.** That wiring belongs to W7 (city, crt_overlay), W8 and W2 (glass_blur, marker_stroke, paper_burn, halftone, glitch_dissolve).
- **Captures are lab captures, not in-context combat.** The motion lab's wheel stands in for the combat scene.

## Bible rules I think need a look (not changed)

- **T1's 0.25 s cap clashes with §10.** §10 allows 0.35 s page moves and 0.4 s number rolls, and many T1 UI motions run 0.3–0.6 s. I suggest the §8 duration column bind only drawn effects and flashes, with UI motion kept to §10's budgets. That is how it's implemented here.
- **§8 gives T4 two limits.** It says "2.5 s (skippable)" but also has a jack arrival wait of up to 4 s (a reading and building wait, not an effect). Worth saying explicitly that waits aren't VFX.
