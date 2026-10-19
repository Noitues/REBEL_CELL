# NA-22: shader parameter table

Round W1 NA-22. Spec: `docs/handoff/netrun_art/PIPELINE_SPEC.md` (art-pass b7a4bf33) 4.3, 5.3, 7.1 rule 0, 7.4, 11.1-11.3, 12.0, 12.5.
Config: `content/config/city_shaders.tres` (`CityShaderConfigData`); the occlusion colours, ghost, edge and LOD bands stay in
`netrun_art.tres` (`NetrunArtConfigData`), one copy. Kit: `NetrunShaderKit` sets every uniform below from those two files.

## Rulings used

1. Reduce effects freezes the clock at the plate's recorded `anim_t`. Every animated netrun shader reads
   `nr_clock(anim_t, anim_t_frozen)` (`shaders/lib/netrun_clock.gdshaderinc`): `anim_t` while effects play, `anim_t_frozen`
   under the global `reduce_effects`. The view sets both (`NetrunShaderKit.set_clock`; `frozen` NaN = config
   `reduce.anim_t_default`). Ghost and cut are not animated in the shader (the view eases the per-instance values over
   `occlusion.ease_s`; with reduce effects `reduce.ease_s` = 0 writes the end state at once).
2. The per-instance cut, Bayer ghost and dissolve are NOT applied at `look_blend` 0 (the HQ page stays within 1/255).
   Everything starts above 0. The street section is its own switch (`sec_on`), off on the HQ page.

## INSTANCE_CUSTOM packing (`city_building`, MultiMesh)

x = taper, y = trim ink slot, z = seed (unchanged). `w = crest + 2 * bits`, `bits` an integer below 2^23, exact in float32.
Class `NetrunInstancePack` (pack / unpack / `is_occluded` / `bayer4`). Every field is stored so that 0 = nothing happens, so
an untouched building keeps the old `w` (0 or the crest flag).

| Field | Bits (low to high) | Code | Meaning |
|---|---|---|---|
| cut | 0-8 | 0..511 | Share of the height removed from the top, `cut_h = h * (1 - code / 511)`; 0 = no cut. Above `cut_h` nothing is drawn; back faces below it draw the poche |
| ghost | 9-13 | 0..16 | `16 - round(opacity * 16)`: the Bayer 4 x 4 screen door draws `16 - code` of 16 pixels (opacity 0.5 = 8 / 16). Windows dim by `opacity` (`ghost_dim`) |
| edge | 14-16 | 0..7 | Ghost edge-line strength `code / 7` (edge band `edge_band` BU from a wall's corners and the cut / top line). Edge pixels get `edge_boost` more Bayer coverage |
| dissolve | 17-21 | 0..16 | Route-wall dissolve share (the transposed Bayer order; that share of pixels is discarded) |

Cut resolution is `h / 511` (0.2 BU at 100 BU). The ghost opacity is quantized to 1/16 (the default 0.18 draws 3/16).

## `city_building.gdshader` (new uniforms; old ones untouched)

| Uniform | Type | Default | Source (config / derive key) |
|---|---|---|---|
| `look_blend` | float | 0 | view (`NetrunSection.look_w`); `CityView3D.set_look_blend` |
| `emission_multiplier` | float | 1 | view; flicker / strobe tables (dress) |
| `sec_on` | bool | false | view |
| `sec_a`, `sec_c`, `sec_nrm` | vec2 | (0,0), (0,1), (1,0) | derive street `a`, `c`, `nrm` (plan x, y; plan y = -world Z) |
| `sec_pad`, `sec_side` | float | 30, -0.4 | `building.corridor_pad`, `building.side_test` (spec 5.3) |
| `sec_ground` | float | 0 | derive room boxes `ground_z` |
| `z_cut` | float | 1e4 | `NetrunSection.zcut` (`section.no_cut` while the smoothstep is 0) |
| `plinth_on` (vec2), `plinth_off`, `plinth_albedo`, `plinth_blue` | | (5,1.5), 4.2, 0.012, 1.2 | `building.*` |
| `poche`, `edge_col` | vec3 | (0.01,0.01,0.013), (0.55,0.68,0.85) | `section.poche`, `section.edge_col` |
| `edge_gain`, `edge_band`, `edge_boost`, `ghost_dim` | float | 0.6, 0.095, 0.22, 1 | `occlusion.edge`, `building.edge_band_bu`, `building.edge_alpha_boost`, `building.window_dim` |
| `id_mode`, `id_class` | bool, float | false, 2 | id pass (NA-ID): unlit R = class, G = 255 and B = 0 for a cut / ghosted / dissolved building (12.0) |

At `look_blend` > 0 the toon band blends to a smooth lambert ramp over the same three colours. Specular and a true PBR
mix are not part of the building (specular stays disabled); the ink fade is in `city_post` (`ink_fade`, config `look.ink_fade`).
The occlusion `KEYS` (28 flat `occ_*` scalars of DERIVE_V2_REVIEW item 11) are read by the CPU helper of spec 7.4 (NA-24),
which writes the per-instance `w`; the shader does not take them.

## `city_post.gdshader`

`ink_fade` (float, 0): multiplies the ink alpha by `1 - ink_fade`. `CityView3D.set_look_blend` sets
`min(look_blend * look.ink_fade, 1 - look.ink_floor)`, fades the mainline `fog_amount` by `1 - look_blend` and sets the
Environment `tonemap_exposure` to `lerp(1, look.exposure, look_blend)` (the value-band solve, calibrated with `fog.peak`).

## `wet_street.gdshader` (ground and lane strips; same parameters as `city_ground`)

`CityView3D.set_look_blend` swaps the ground materials' shader between `city_ground` (look_blend 0, the old shader itself)
and `wet_street`.

| Uniform | Type | Default | Source |
|---|---|---|---|
| `look_blend`, `emission_multiplier` | float | 0, 1 | as above |
| `noise_scale`, `noise_octaves` | float, int | 0.09, 5 | `wet.noise_scale`, `wet.noise_octaves` |
| `rough_noise`, `rough_wet` | vec2 | (0.45,0.6), (0.3,0.03) | `wet.rough_noise`, `wet.rough_wet` |
| `wet_specular`, `albedo_mul` | float | 0.7, 0.55 | `wet.specular`, `wet.albedo_mul` |
| `puddles_sharp` | float | 1 | `NetrunArtConfigData.lod.bands.puddles_sharp` weight at the zoom |

## `streak_lane.gdshader` (one lane; unshaded additive strip)

| Uniform | Type | Default | Source (dress `streak_lanes[]`) |
|---|---|---|---|
| `streaks` | sampler2D N x 1 RGBAF | none | `streaks[]` = (`u0`, `len`, `bright`), at most `streak.max_streaks` |
| `streak_count`, `lane_len` | int, float | 0, 80 | count; \|`b` - `a`\| |
| `speed`, `dir` | float | 20, 1 | `speed` quantized: `L = k speed T` (`NetrunShaderKit.quantize_speed`); direction +1 a -> b |
| `loop_s` | float | 4 | `streak.loop_s` |
| `anim_t`, `anim_t_frozen` | float | 0, 0 | clock |
| `lane_col`, `emit`, `bright_floor`, `bright_pow`, `emission_multiplier`, `look_blend` | | | palette, `streak.emit` 2.5, `floor` 0.15, `power` 1.6 |

Each streak slides by `dir * speed * mod(t, loop_s)` and wraps on its own modulo `lane_len`; with `L = k speed T` the frame at
`t = 0` equals the frame at `t = loop_s`. Width `streak.width` is the mesh half width (`NetrunShaderKit.streak_mesh`).

## `beam_shaft.gdshader` (one shaft; unshaded additive open tube)

| Uniform | Default | Source (dress `beams[]`, config `beam.*`) |
|---|---|---|
| `beam_col` | | palette `pal` |
| `beam_len`, `start_radius`, `end_radius` | | `length_front` x H_FRONT; `start_radius` 0.18; `len * tan(half_deg)` |
| `lean_deg` (vec2) | | `lean` = [x_deg, y_deg]: direction (tan x, tan y, 1) in plan axes |
| `sweep_deg`, `phase`, `loop_s`, `pitch_share` | 0, 0, 4, 0.25 | `sweep_deg`, `phase`; x lean += sweep sin(2 pi (t / loop_s + phase)), y lean += pitch_share sweep cos(...) |
| `core_sigma`, `core_w`, `skirt_sigma`, `skirt_w` | 0.13, 1, 0.42, 0.5 | `beam.*` |
| `efold`, `fade_from`, `fade`, `fade_in` | 0.22, 0.27, 0.6, 0.025 | `beam.*` |
| `noise_scale`, `noise_range`, `hot`, `emit` | 0.09, (0.35,0.65), 0.5, 3 | `beam.noise_*`, `hot`, `emit` |
| `anim_t`, `anim_t_frozen`, `emission_multiplier`, `look_blend` | | clock / view |

Radial: `r = 1 - facing`, `core = core_w exp(-(r / core_sigma)^2 / 2)`, `skirt = skirt_w exp(-(r / skirt_sigma)^2 / 2) (1 - r^2)`;
both vanish at the silhouette. The spec text writes the skirt factor as `(1 - s^2)`; rule 2 (no hard silhouette) wins, so the
factor is `1 - r^2` with `r` the offset from the axis side. Axial: `exp(-t / efold)`, to 0 over `fade_from .. fade`, fade-in.

## `city_fog.gdshader` (`shader_type fog`, FogVolume)

All terms of spec 4.1 "Fog": `peak`, `h_front`, `h_sky` (= `h_sky_k` x `h_front`), strata (`strata_k`, `warp_k`, `tilt`), octaves
(`bank_freq`, `wisp_freq`, `bank_mix`, `remap_oct`, `clump_freq`, `remap_clump`), wisp layer, `front`, `floor_range`, ground
bank (`gb_off`, `gb_top`, `ground_bank`), mid banks, back haze, `scatter`, glow tints and `emit_gain`, `wind`, the street
(`sec_a`, `sec_c`, `sec_nrm`, `kerb`), `octave_w` (the `fog_octaves` LOD weights, `NetrunShaderKit.octave_weights`),
`density_mul`, `front_sym` (1 = fog on both sides of the street line, for a canyon view along the street; 0 = behind the street face only), `look_blend` (scales the whole density), clock. All from `fog.*`. `NetrunShaderKit.configure_environment` sets
the volumetric fog on the Environment (global density 0, the volume carries it); `fog_volume` builds the box.
Calibration (12.1, golden `street_overview`, the game-city canyon frame of `tools/city/na22_lab.gd`): `fog.peak` 0.1014 (2 x the spec's 0.0507) and `look.exposure` 0.4 give median luma 0.134 (plate 0.136), under 0.10 29.1 % (26.9 %), over 0.85 0.0 % (0.5 %), all inside the 12.8 provisional tolerances. Composition metrics (hue, signage, detail) are not matched: the game city has no signage or district hue spread.
