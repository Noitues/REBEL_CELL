# Route map overview: V3 AAA key art (2026-10-14)

Three AAA-finish key-art stills of the netrun route map **overview**, built on the V3 dynamic scene:
- the same 19-node run, mid-run state (fight, event, shop walked; option 1 the fight, option 2 the Rack);
- the same layout, columns, floors and the 10 connection types;
- the same overview camera (`cam_rig.overview`, yaw 0°, pitch 6°, 40 mm);
- the same seeded build stream (4207), so every V3 dynamic building, room and link is where it was.

Rendered with **Cycles on the CPU** (the RX 6700 XT is not available to Cycles here: HIP lists only the CPU), plus Eevee for the data passes. Nothing is committed. The Godot build is untouched.

The work went through four review rounds while it was in progress:
1. the designer's first note (lights down, keep the puddles, streaky fog);
2. the Cyberpunk 2077 screencaps as a quality bar (light, air, density and grade only; no designs, signage or pixels copied);
3. the critic's `CRITIQUE.md` (§7 recipe), applied in full where feasible (see "Critique checklist");
4. the designer's second note (the backdrop lines must read as traffic; the helix holo goes; the Orbital globe must read).

## Files

| File | What it is |
|---|---|
| `AAA3_hybrid.png` | **The hero (recommended).** 2560 × 1440. Our low-poly cel geometry, ink and toon bands at hybrid strength; path-traced light, haze, wet street; the full frame UI. |
| `AAA3_hybrid_hover.png` | The hero with option 2 (the Rack) hovered. The power cut is done **in 3D**: every light and emitter outside the branch drops to 22 % before rendering, then the V3 2D grade adds its gentler cut. The tag, node file and cursor show. |
| `AAA1_premium_cel.png` | AAA-1: the locked cel look at full strength (3 toon bands at 1.25 stops, full ink, violet ramp floor) with the same real light, air and wet ground. |
| `AAA2_realistic_night.png` | AAA-2: PBR study (no ink, no bands, flat facades, metal links, concrete grime), with the route also projected as **3D holo tubes** in world space. **Off-style:** see "Designer call". |
| `plates/*_plate.png` | The same four images without UI (clean key-art plates). |
| `compare_aaa.jpg` | 3 × 2: current V3 dynamic `O_overview`, the critiqued test (`keep/c_real_test_designer_liked.png`, "before"), AAA-1, AAA-2, AAA-3, AAA-3 hover. Each tile shows its median luma, % under 0.10 and % over 0.85. |
| `scripts/` | Everything needed to rebuild (see "Rebuild"). |
| `CRITIQUE*.{md,jpg}`, `critique_scripts/`, `keep/` | The critic's and designer's files, untouched. |

## Render times (CPU: i5-9600K, 6 cores; Blender 5.2.2)

Per still:

| Pass | Settings | Time |
|---|---|---|
| Cycles main (surfaces) | 2560 × 1440, 32 spp adaptive (threshold 0.015), OIDN (albedo + normal, accurate prefilter) | 403 s (AAA-3), 433 s (hover), 440 s (AAA-1), 486 s (AAA-2) |
| Cycles volume | 800 × 450, 16 spp, OIDN, holdout surfaces | 19–20 s |
| Eevee data passes | 3840 × 2160, 5 passes | 17–18 s |
| Scene build + post + compose | numpy / PIL | about 1.5 min |

**Total: about 9–10 minutes per still**, inside the ~10-minute budget. The four finals took about 36 minutes of wall time, run back to back. The tuning loop used 1280 × 720 tests (about 2 minutes each).

## Measured value structure (the critic's acceptance numbers)

Measured with `scripts/stats_aaa.py`, which also runs the critic's `critique_scripts/crit_stats.py` on a 1280 copy. sRGB luma.
- **Targets:** median 0.14–0.18; p95 0.65–0.75; at least 25 % of pixels under 0.10; at most 2.5 % over 0.85; saturation of bright pixels at least 0.25.
- **Reference values:** the screencaps measure median 0.13–0.16, 29–41 % under 0.10 and 1–3 % over 0.85.

| Image | Median | p95 | % < 0.10 | % > 0.85 | Bright saturation | Verdict |
|---|---|---|---|---|---|---|
| **AAA-3 hybrid, plate** | 0.147 | 0.749 | 36.1 % | 2.0 % | 0.26 | **all 5 targets met** |
| AAA-3 hybrid, with UI | 0.152 | 0.831 | 34.9 % | 4.2 % | 0.25 | p95 and > 0.85 high from the UI (see below) |
| **AAA-1 cel, plate** | 0.144 | 0.708 | 37.0 % | 1.7 % | 0.26 | **all 5 targets met** |
| AAA-1 cel, with UI | 0.148 | 0.826 | 35.9 % | 4.1 % | 0.26 | as above |
| AAA-2 real, plate | 0.132 | 0.793 | 40.1 % | 2.7 % | 0.26 | slightly dark median and slightly hot top; it is the off-style study, so it was not chased further |
| AAA-2 real, with UI | 0.140 | 0.835 | 37.7 % | 4.3 % | 0.25 | |
| AAA-3 hover, plate | 0.062 | 0.504 | 64.3 % | 1.0 % | 0.29 | darker by design: the 3D power cut |
| Before (`c_real_test`) | 0.431 | 0.929 | 9.0 % | 11.0 % | 0.17 | the critiqued frame |

**Greyscale check** (`scripts/grey_check_aaa.py`, mean luma of each room opening on the plate). **The two options are the two brightest rooms in every look:**

| Look | Option 1 (L4_0) | Option 2 (L4_1) | Current room (L3_0) |
|---|---|---|---|
| AAA-1 | 0.76 | 0.68 | 0.67 |
| AAA-2 | 0.81 | 0.78 | 0.76 |
| AAA-3 | 0.79 | 0.76 | 0.74 |

The margins over the current room are small, 0.01–0.05. The overlay's orange frames and number chips carry the rest.

- **The frame UI** (the white dossier, the lime toggle, the stickers) adds about 1.5–2 % of pixels over 0.85 on its own. The critic allows it ("nearly all of those must be the overlay or the option rooms"), so both numbers are given; the plate number is the 3D's own.
- **The before frame** (`c_real_test`, critiqued) measured median 0.43, 9 % under 0.10 and 11 % over 0.85.

## The shared pipeline (all three looks)

`jobs_aaa.py` → `scene_aaa.py` (Blender) → `post_aaa.py` → `compose_aaa.py`.

1. **Scene.** `scene_aaa.py` is V3 dynamic's `scene3.py` with the materials swapped for Cycles. Four files are exec'd into it **after** the V3 build, each with its own seeded stream (so the layout is unchanged):

   | File | Stream | What it adds |
   |---|---|---|
   | `dress_aaa.py` | 5150 | AC units, balconies, pipes, cables, roof clutter, 240 pedestrians (some with lit umbrella rims), vendor stalls, shop signs, two holograms (Orbital globe, Solace lotus), a 4th skyline layer and arcology masses |
   | `holo_route_aaa.py` | — | AAA-2 only: the route as 3D holo tubes, by state |
   | `dress2_aaa.py` | 6161 | The critique's density and scale: greebles, alley cables, 3 out-of-frame towers, 2 megastructures, 11 ad textures, near-black edge silhouettes, a closing far skyline wall |
   | `light_aaa.py` + `fogcards_aaa.py` | — | Lights, haze volumes, the room-state power, fog strata cards |

2. **Three renders per still.**
   - **Main** (Cycles, no volume objects): Combined, Emission, Denoising Albedo, Depth, Diffuse Color, as multilayer EXR, read by OpenImageIO and saved as `.npy`.
   - **Volume** (Cycles, half res or less): every surface is wrapped as *holdout for camera rays, real material for every other ray*. Surfaces still block light (real god rays through the alleys) and emitters still light the haze. Combined is then the in-scattered light only.
   - **Data** (Eevee, 1.5× res): id, normal, depth, semantic class and world z, for the ink, the masks and the background grade.
3. **Post** (`post_aaa.py`, per look):
   - Surfaces × T plus the in-scatter. T is computed exactly per pixel by intersecting the camera rays with the homogeneous haze boxes up to the Cycles depth.
   - Toon bands of the lighting, `(Combined − Emission) / Albedo`, on the cel and hybrid looks.
   - Ink, the background grade, exposure, HDR bloom, a hue-preserving tone map, 3-layer rain, the grade, the display knee, vignette, edge chromatic aberration and grain.
4. **Compose** (`compose_aaa.py`): the V3 dynamic overlay code (`compose3` / `sidekit` / `ui31` / `kit44`) is reused unchanged.
   - It draws at 1920 × 1080. Every overlay op is per-pixel affine in the plate, so the overlay is drawn on two flat plates (0 and 0.5) and solved for `out = plate·m + b`. `m` and `b` are upscaled to 2560 × 1440 and applied to the real plate.
   - The world grade (room state tints, the hover cut) and a new **local darken under the route** (0.2 multiply, 24 px at 1080p) are redone at full resolution.

### Lighting (shared numbers, `light_aaa.py`)

**Rooms.** Each room has a ceiling area light of 650 W in its type colour, plus a spill light of 220 W out of the opening.
- **State ladder** (light and room-face emission scale together):

  | State | Factor |
  |---|---|
  | Option | 0.9 |
  | TARGET | 0.85 |
  | Current | 0.55 |
  | Walked | 0.3 |
  | Ahead | 0.3, cooled toward about 7000 K |
  | Past | 0.06 |

  This is the critique's ladder × 0.5, because our exposure is higher (see "Critique deviations").
- Options, the current room and the TARGET also get a **2700 K key** at 25 % of the room light.

**Street.**
- Kerb spots: 1800 W, sodium 2000 K (two in three) or cool LED, 82° cone.
- Foreground lamp heads: 1400 W.
- Alley up-lights: 1500 W, alternating pink, cyan and violet.
- Stall lights: 500 W.
- Holo point lights: 9000 W (two).

**Sky.**
- Searchlights: 2e6 W, 2.6° cones, synced to the V3 cones.
- 3 aerial downlights on the front lane: 5e4 W, 5.5°.
- Backglow: magenta 3.5e8 W and cyan 2.1e8 W area lights at y = 1000, beyond the haze, **haze only**: no diffuse, glossy or transmission rays, so they never flood facades.
- 6 city-glow up-lights: 1.2e5 W each, magenta and cyan, at z 6, **light-linked to the fog cards only**.
- Moon: 0.12 W/m², cool.

No light is visible to the camera.

**Haze** (homogeneous Volume Scatter; anisotropy 0.2, because 0.42 made a blown forward-scatter halo):

| Box | Density | Colour | Notes |
|---|---|---|---|
| back haze | 0.0022 (AAA-2: 0.0025) | (0.82, 0.78, 1.0) | behind the route row, y > 16 |
| street mist | 0.006 (AAA-2: 0.008) | | z < 4 |
| front air | 0.00008 | | in front of the route; effectively none, so there is no veil |

**Fog strata** (`fogcards_aaa.py`): six cards, at
- z 40–45, 52–58, 66–73, 92–100, 130–140 and 168–180;
- y 30 to 420 (deeper as they rise).

The lowest card sits above the highest option room + 6 BU.
- **Noise:** 4D noise on `(x′·0.010, z_tilted·0.15)`.
  - x′ is x plus a 120 BU domain warp.
  - z_tilted is z − x·tan(θ), with a per-band wind tilt θ of ±2–4°.
- **Tearing:** an x-only noise (0.035) tears each band into 20–60 BU wisps.
- **Shape:** soft remap 0.46–0.68, then power 1.4.
- **Profile:** `smoothstep(0, 0.12, v) · (1 − v)^1.6`, so the underside is sharp and the top is feathered.
- **Edge fade:** 15 % in x.
- **Shading:** Translucent BSDF plus an underlight emission of `(1 − v)^3 · 2.1` in the district colour along x. Alpha is capped at 0.55.

### Materials (`mats_aaa.py`)

**Surfaces.** A Principled BSDF on the V3 vertex colours (facet jitter 0.86–1.12).
- **Wet ground** (all looks):
  - puddle mask: noise scale 0.09, remap 0.47–0.56;
  - roughness 0.03 in puddles and 0.25 on damp asphalt, with a 0.5 BU ripple bump (strength 0.15);
  - albedo ×0.35–0.62.
- **Window grid** (mid row and far city): lit by **floor runs**.
  - P(floor lit) = 0.35, then P(window lit) = 0.75, with dark bays.
  - Colours: 80 % warm 3200 K, 15 % cool 5500 K, 5 % magenta.
  - Log-normal intensity, σ 0.5; strength 0.18.
  - Unlit panes are darker and glossier.

**Emitters.** The emissive strength of the V3 neon geometry follows the critique ladder:
- **Trim:** 1.6.
- **Room faces:** ×4, × the room's state factor.
- **Signs:** hero signs at **7** (5 of them: HALCYON, SOLACE, MERIDIAN, HOTEL, NOODLE, all off the decision set); every other sign at the trim 1.6.
- **Ads:** 1.6–1.8.
- **Windows:** 0.32.
- **By class:** far city ×0.14, mid row ×0.6, street paint ×0.35, link glazing ×0.6, route storefronts at street level ×0.5.

**Palette lock.** City trims and signs use only the magenta #FF2A8A / cyan #2AD4FF district pair, plus violet, pink and red. There is no lime, run orange, pencil yellow or white emissive near the route. The trim list kept its length, so the seeded choices did not move.

### Post (shared numbers, `post_aaa.py`)

| Step | Value |
|---|---|
| Volume weight `vol_k` | 1.3 (with a soft clamp of the in-scatter at 0.08, against forward-scatter hot spots) |
| Tone map | max-RGB, hue-preserving: `c · ACES(m)/m`, blending to 20 % per-channel ACES only where m > 4. Neon keeps its hue in the core. |
| Bloom | threshold 1.2; weights 0.12 / 0.10 / 0.08 at σ 6 / 24 / 135 px (at 2560) |
| Rain | 3 layers: 4000 × 3–6 px at α 0.05; 1800 × 14–24 px at α 0.10; 60 × 60–95 px at α 0.25, width 3. Lit by the bloom; ×0.25 over the protected rooms and a 6 px dilation of every route cable. |
| Grade | teal-navy shadow tint (0.25, 0.45, 0.6) at 0.30; warm highlight tint; saturation 1.0; lift (0, 0, 0.004) |
| Contrast | 1.25 around 0.18 in display space |
| Display knee | from 0.66 to 0.93, so the 3D frame stays under 2.5 % above 0.85 |

## The three looks

### AAA-1 "Premium cel" (`AAA1_premium_cel.png`)
**Recipe:** the shared light and air, plus:
- **Toon bands:** the path-traced lighting is banded at 1.25 stops (soft width 0.10), with the hue kept. Bands are floored at the cel ramp's violet (0.035, 0.028, 0.075).
- **Ink:** 0.95 on the route row and 0.35 on the background, from the id, normal and depth edges, wobbled, and faded with depth.
- **Additive air:** 0.12, so the V3 light shafts and searchlight cones still show faintly.
- **Grade and exposure:** exposure 2.6; grain 0.022; chromatic aberration 1.6 px at the corners; vignette 0.30.

**Reads as:** the bible's world look with real light. This is the safest option, but the full bands flatten the wet-ground and haze gradients the most.

### AAA-2 "Realistic night" (`AAA2_realistic_night.png`)
**Recipe:**
- **Surfaces:** no facet jitter (flat walls), albedo ×0.85, concrete grime (noise 0.35 for albedo 0.78–1.08, vertical streaks), roughness 0.38–0.82, fine bump, metal link structure (metallic 0.8), glossier glass.
- **Haze:** back haze 0.0025, street mist 0.008.
- **The route as 3D holo tubes:** lime walked solid, orange options dashed, white ahead dashed, grey past faint. Each is a core (strength 7–16) plus a translucent sheath (0.7–1.6). The tubes light the haze and reflect in the street. The 2D cables are still drawn on top at 55 %, because the tunnel and some lift lanes run behind structure.
- **No ink, no bands.**
- **Grade and exposure:** exposure 2.6; grain 0.03; chromatic aberration 2.4; vignette 0.38.

> **Designer call: this departs from the locked low-poly cel look** (ART_BIBLE v2 §1.2: Cv2 low-poly + E cel, ink, toon bands). It is a lighting and atmosphere study. Its value structure, air and wet ground are what AAA-3 carries over.

### AAA-3 "Hybrid" (`AAA3_hybrid.png`, the hero)
**Recipe:** the shared light and air, plus:
- **Toon bands** at 45 % (1.25 stops, soft width 0.18).
- **Ink** at 0.62 on the route row and 0.22 on the background.
- **Facet jitter on:** the low-poly geometry and the bible's sticker, wax-pencil and holo overlays are kept. The holo layer is the in-world holo ads and panels, with scanlines and an RGB split.
- **Grade and exposure:** exposure 2.8; grain 0.026; chromatic aberration 2.0; vignette 0.34.

**Reads as:** our world, lit and aired like a AAA night: dark facades between light sources, saturated neon that keeps its hue, wet ground, layered haze. The route is the hottest, cleanest thing in the frame.

## The 3-second check (every final, at full size)
- **Is the route the clearest thing in the frame?** Yes.
  - The lime walked cable, the orange numbered options and the red pencil TARGET sit on a local darken.
  - In greyscale, the two option rooms are the brightest 3D rooms in every look (the Rack in gold, option 1's fight room in cyan), just ahead of the current shop.
  - Ahead rooms are dim and cool; past rooms are dark with a dim practical.
- **Does the background stay subordinate?** Yes.
  - The far layers step lighter only through haze.
  - Far emitters are at ×0.14; the mid row is desaturated 38–40 % and dimmed to 58–60 %.
  - Hero signs and ads are kept out of the calm zone behind the decision set (x 70–114): the ORBITAL blade sign that stood behind option column L4 was moved.
- **Is there any IP-looking signage?** No. Every sign and ad is our corps or invented:
  - **Corps:** MERIDIAN FREIGHT "WE MOVE. YOU WAIT."; SOLACE "SLEEP IS A PRESCRIPTION" / DOSE+; HALCYON "CLEAN AIR. CLEAN BLOOD."; ORBITAL "THE SKY IS LEASED" / LEO-9.
  - **Invented:** KAIRO NOODLE, VOLTA, HOTEL CAPSULES, CLINIC 24 H, NOODLE 9, OPEN 24, PAWN, NETCAFE, CAPSULES, REPAIR, RAMEN, YAKI, SOBA, CHAI, DUMPLING.
  - **Fonts and marks:** Anton and Share Tech Mono (OFL, in the repo), Blender's built-in font, and our `emblems20.py` corp marks.
  - Nothing in the frame is taken from the reference screencaps.

### Fixed during the checks

| Problem | Fix |
|---|---|
| Too bright and milky (median 0.43) | The critique's exposure, veil and black-level recipe |
| Neon clipped to white cores | Hue-preserving tone map; neon split into hero and trim |
| A blown orb at the frame top | Light shapes made camera-invisible; backglow moved out of the haze and lowered; anisotropy 0.42 → 0.2; in-scatter soft clamp; a closing far skyline wall |
| A magenta "laser" bar on the left | A near fog card was lit hard by a close city-glow light. The light was moved down and dimmed, and the band torn along x. |
| Cotton-ball fog | Wind-sheared, torn strata cards |
| Thin ruler-straight lines across the sky (designer note 2) | They were the far roof trims, the full-width tower bands and long lane trails. Far trims went to ×0.14; the bands were removed; the far traffic lane was hidden. The two front lanes now show short red tail streaks of 5–19 BU behind white or warm head lights, with the car bodies visible. |
| The helix holo (designer note 2) | Removed. A readable HALCYON holo billboard (emblem, name and tagline) stands in its place. |
| The Orbital globe (designer note 2) | Kept, with an ORBITAL / LEO-9 holo panel right under it, so the globe and the name read as one ad |
| Option interiors washed to white | The state ladder was halved, the warm key went from 0.45 to 0.25, and the compose ×1.15 on options was removed |
| The full-width lavender kerb line read as a false route line | Broken into 2–6 BU segments at 30 % |
| The VOLTA billboard rendered behind its panel | It ignored the column's depth offset; the ad now sits at the panel face |

## Critique checklist (`CRITIQUE.md` §7)

**Done:**
- **Exposure, veil and grade:** the veil, black level and pivot contrast; the hue-preserving shoulder; bloom.
- **Volumes and lights:** front air 0.00008; back haze 0.0022 / 0.0025; the room ladder (scaled); cool ahead rooms; warm keys; kerb 1800 W at 2000 K; fg lamps 1400 W; the backglow (moved and re-powered, see "Critique deviations").
- **Neon:** the hero / trim split and the palette lock.
- **Windows:** `win` 0.32, `gs` 0.18, far ×0.14, and floor-run windows.
- **Street:** roughness 0.03 / 0.25 with ripples; 3-layer rain, cut on the route.
- **Dressing:** the greeble kit; alley cables kept out of room and link heights; 3 out-of-frame towers; 2 megastructures outside the calm zone; 2 near-black edge silhouettes.
- **Overlay:** the route-band darken.
- **Style lock:** kept in AAA-3 (`band` 0.45, `ink` 0.62).
- **Stats:** measured on every final.

**Deviated** (see "Critique deviations"):
- the exposure value;
- the strata built as cards, not a volume;
- `cityglow` at 1.2e5 W.

**Also note:** AAA-2's plate misses by a little (median 0.132, 2.7 % over 0.85).

**Not done** (see "Not done / limits"):
- paint and grate roughness 0.5;
- splash ticks;
- 2 window shapes and a blinds mask;
- re-running `check_occlusion.py`.

## Critique deviations
1. **Exposure 2.6 (AAA-1, AAA-2) and 2.8 (AAA-3) instead of 0.75.**
   - The 0.75 was set against the old frame, whose median of 0.43 came mostly from the veil.
   - With the veil gone, the facades dark and every emitter at the critique's (lower) strengths, 0.75 measured a median of 0.05.
   - The acceptance numbers are the real target, so exposure was set to hit them.
   - The room ladder was scaled by 0.5 to match, so the ratios are the critique's.
2. **The strata are cards, not a heterogeneous volume.**
   - The §4 volume recipe works in Cycles: `light_aaa.py` keeps it behind the job flag `vol_strata`. But it cost **about 7× the volume pass** on this CPU (62 s against 8 s at 480 × 270). Volumetric steam has the same cost and is behind `vol_steam`.
   - The cards follow the same recipe: anisotropy, wind tilt, domain warp, crisp-then-soft remap, asymmetric profile, edge fade, underlight emission and clear air between bands.
   - They are also exactly what §4 prescribes for Godot.
3. **City glow at 1.2e5 W, not 6e5 W.**
   - At 6e5 W the nearest card lit up as a crisp magenta bar.
   - Light linking already restricts the glow to the cards.

## Godot 4.7 Forward+ feasibility and performance

| Feature | AAA-1 cel | AAA-2 real | AAA-3 hybrid | Godot route |
|---|---|---|---|---|
| Lit rooms, spill, keys | yes | yes | yes | Real time. About 40 OmniLight3D / SpotLight3D (clustered, Forward+ handles hundreds). Shadows only on about 6 (the options, current and TARGET). The state factor is a per-room uniform (already planned for the hover cut). |
| Neon bounce on facades | approximated | approximated | approximated | SDFGI picks up emissive at coarse scale, but its cascades blur at 268 BU and it costs 2–4 ms. **Recommended:** no GI; the room spill lights plus alley up-lights do the visible bounce. LightmapGI is out, because the street is generated per run. |
| Toon bands | full | — | 45 % | Real time and cheap: a custom `light()` with stepped diffuse per light (better than the post band: per light, no albedo division). |
| Ink | full | — | 0.62 | A post outline from depth and normal-roughness (a 4.3+ `CompositorEffect`), about 0.4 ms at 1440p. |
| Wet street | yes | yes | yes | SSR on the street material (`ssr_max_steps` 64), a ReflectionProbe as the base, plus a vertical screen-texture smear for the streaks. SSR loses off-screen signs, which the smear and the probe cover. About 1–1.5 ms. |
| Puddles | yes | yes | yes | A noise mask in the street shader, or Decal nodes. Free. |
| Back haze and street mist | yes | yes | yes | Volumetric fog (froxel) plus 2 FogVolume boxes; spot `volumetric_fog_energy` gives the lamp cones and searchlight shafts. About 1–2 ms at medium. |
| Fog strata | cards | cards | cards | 6 unshaded mix-blend quads with the same noise maths on a `NoiseTexture2D`, plus `proximity_fade`. Froxels cannot resolve 4–10 BU bands at 300 BU. Negligible cost. |
| God rays through alleys | yes | yes | yes | Volumetric fog with shadowed spots gives them, at cost. Cheap version: additive light-shaft cards, as in V3 dynamic. |
| Holo ads, panels, globe | yes | yes | yes | Unshaded additive materials with scanlines and an RGB split; a seeded flicker. Free. |
| Ad textures | yes | yes | yes | One atlas (11 textures, about 4 MB at 1024²). |
| Greebles, crowds, cables | yes | yes | yes | A MultiMesh per kit piece; crowds as a MultiMesh of 240 boxes. About 30 extra draws. |
| Window grid | yes | yes | yes | A procedural building shader (floor and bay hash); no textures. |
| Hue-preserving tone map | yes | yes | yes | `tonemap_mode = AgX` (4.4+) plus a 33³ LUT baked from `post_aaa`. Glow at HDR threshold 1.0, intensity 0.6, additive. |
| Rain (3 layers) | yes | yes | yes | A screen-space shader sampling a quarter-res glow buffer, as planned in V3 dynamic. |
| PBR concrete and metal | — | yes | — | Needs texture sets (albedo, roughness, normal) per building family: memory plus artist time. |
| 3D holo route tubes | — | yes | — | MeshInstance3D tubes per edge (about 25), unshaded additive. They cannot glow in fog without real lights, and they occlude, so the 2D overlay stays anyway. |

**Estimated cost over V3 dynamic** (at 1440p on the target spec):

| Look | Added cost | 60 fps budget |
|---|---|---|
| AAA-1 | about +3 ms (fog, SSR, outlines, extra lights) | fits |
| AAA-3 | about +3.5 ms | fits |
| AAA-2 | about +5–6 ms, plus texture memory and a materials pass | tight |

Volumetric fog quality is the main lever: use the low VfxTier, no volumetrics on the street, with cards only.

## Recommendation
**Ship AAA-3 hybrid as the direction.** It is the critic's call too.
- It keeps the bible's identity: the low-poly kit, wobbly ink, toon bands, stickers, wax pencil and holo.
- It takes the AAA bar where the bar actually lives: the value structure (a dark frame with small, saturated, hot lights), the wet ground, layered and wind-sheared air, density and scale.
- It is the cheapest of the AAA options to build in Godot after AAA-1, and every piece of it is real time.

AAA-1 is the fallback if the full bands are preferred. AAA-2 is a reference for lighting and grade, not a ship look.

## Not done / limits
- **No GPU.** The AMD card is not visible to Cycles here (HIP lists only the CPU), so everything rendered on 6 CPU cores. That set the budget: 32 spp main plus OIDN, and a volume pass at 800 × 450. The haze is soft, partly by design and partly by budget.
- **The UI is a 1.33× upscale.** The V3 overlay kit draws at 1920 × 1080; it is solved as an affine matte and upscaled, so the UI is slightly softer than the 3D.
- **Volumetric strata and steam** exist but are off (cost, above). The steam is the V3 additive noise plumes.
- **From the critique, not done:**
  - paint and grate roughness 0.5;
  - splash ticks;
  - 2 window shapes per family and a blinds mask;
  - a drum-shaped megastructure (they are set-back slabs);
  - ad flicker (stills);
  - `check_occlusion.py` was not re-run. It is V3 dynamic's checker, built on that semantic pass. Nothing new is placed in front of the route row except the 2 edge silhouettes, which are far outside the protected rooms' screen boxes.
- **The ad art is simple** (type, emblem and line-art product). It reads as ads at this size; up close it would need an illustrator.
- **The holo route tubes (AAA-2) are partly hidden** where links run behind structure. That is why the 2D cables stay at 55 %.
- **Option 1's interior** (a cyan monitor wall) still reads paler than the Rack's gold. Cyan is the type colour, but it is close to the cool "ahead" rooms. A per-type exposure trim could separate them further.

## Rebuild
Run everything from `scripts/`. Nothing launches Godot. Blender runs headless and logs to `scratch/`.
1. `python emblems20.py` (the corp marks), then `python ads_aaa.py` (the 11 ad textures, into `scratch/ads`).
2. `python jobs_aaa.py <cel|real|hybrid> final [hover]`. This renders the passes into `scratch/bl_<look>[_hover]/`.
   - `test` and `mini` are the quick qualities.
   - Extra flags: `vol_strata`, `vol_steam`, `no_fogcards`, `hide_prefix=...`.
3. `python finish_aaa.py still <look> [hover]` (post plus compose, into the root and `plates/`).
4. `python finish_aaa.py compare`.
5. `python stats_aaa.py <png>` (the acceptance numbers plus the critic's `crit_stats.py`).

**Seeds** (everything is seeded):
- the V3 build: 4207;
- atmosphere: 91;
- dressing: 5150 and 6161;
- kerb segments: 4242;
- the post rain and grain: numpy 41 and 107;
- the ads: 9;
- the noise W values are fixed per fog card.

`sgraph3.py`, `cam_rig.py` and the overlay kit are copies from `../v3_dynamic/scripts/` (the same folder depth, so their paths are unchanged).
