# V3 AAA: art-direction critique against the Cyberpunk 2077 bar (first pass)

**Critiqued:** `keep/c_real_test_designer_liked.png` (the "real" look test, 1280 × 720, Cycles plus `post_aaa.py`).

**Final renders:** AAA-1 (cel), AAA-2 (real) and AAA-3 (hybrid) were not in `v3_aaa/` when this was written. This critique covers the test render only. I also looked at the work-in-progress `scratch/vol_strata.png` for the fog section.

**Files made with this critique:**
- `CRITIQUE_markup.jpg`: the render with the 10 gaps numbered on it, and a key panel.
- `CRITIQUE_side_by_side.jpg`: the render cropped next to the matching screencap crops (street, skyline, fog, density), with measured stats under each crop.
- `critique_scripts/`: the scripts that made these files and the numbers below.
  - `crit_stats.py`
  - `ref_stats.py`
  - `crit_markup.py`
  - `crit_side_by_side.py`

**References, in order of weight:**
- **The designer's screencaps** in `../cyberpunk 2077 screencaps/` (primary). They are reference only and must never be copied into our renders or assets.

  | Ref | File | Content | What to use it for |
  |---|---|---|---|
  | **R1** | `EbXy1G7WAAE6iep.jpg` | Japantown street at night, in rain | Wet asphalt, steam, neon, value structure. The key reference. |
  | **R2** | `all-cyberpunk-2077-ncw3-4k-...-p02h2jzr2yn51.webp` | Japantown gate at night | Windows, billboards with content, practical lights, teal/red contrast. |
  | **R3** | `xkjuWSYJPxdEwzSFbPJ72A.jpg` | City Center in the **morning, a day shot** | Scale, ad drums, greeble and cable density. Not for lighting. |
  | **R4** | `images.jpg` | The Afterlife key art, 596 px | One dominant hue (lime/teal) and black depth. Low resolution, so only for value and hue structure. |

- **CDPR's own statements.** Lighting/FX art director Jakub Knapik described dynamic, physically based lighting at believable proportions between street lamps, neon, shop light and sky. He described a film-style 3D-LUT grade built in Nuke instead of a stock tonemapper, and matching against a path-traced reference ([Foundry interview](https://foundry.com/insights/film-tv/cyberpunk-2077-night-city-nuke)). The GDC 2022 talk "Bringing Light to Night City" (Knapik, Yablonsky, Poo) frames the city as a "living digital film set" ([Game Developer summary](https://www.gamedeveloper.com/marketing/find-out-how-cyberpunk-2077-lit-up-night-city-in-this-gdc-2022-session)). CDPR's path-tracing post notes that steam and dark tunnels are lit by nearby lights ([cyberpunk.net](https://cyberpunk.net/en/news/49747/lighting-up-the-dark-future-with-nvidia-and-cyberpunk-2077)).

**Measured value structure** (sRGB luma, from `critique_scripts/ref_stats.py`):

| Image | Median L | p95 | % of pixels < 0.10 | % of pixels > 0.85 | Mean saturation | Saturation of bright pixels (L > 0.6) |
|---|---|---|---|---|---|---|
| **Ours** (c_real_test) | **0.43** | 0.93 | **9 %** | **11.0 %** | **0.32** | **0.17** |
| R1 Japantown rain | 0.14 | 0.53 | 29 % | 1.5 % | 0.54 | 0.24 |
| R2 Japantown gate | 0.16 | 0.71 | 29 % | 2.8 % | 0.45 | 0.27 |
| R4 Afterlife | 0.13 | 0.51 | 41 % | 1.0 % | 0.76 | 0.35 |
| R3 (day, for comparison) | 0.15 | 0.76 | 36 % | 2.1 % | 0.49 | 0.19 |

**What the numbers say:**
- Our median is **3× too bright**.
- We have about **a third of the black area** the references have.
- We have **4–7× more near-white area**.
- Our bright pixels are **the least saturated of any image**.
- The single sentence version: 2077 is a **dark frame with small, saturated, hot lights**. Ours is a **bright, milky frame with large, pale lights**.

> **The style lock still applies.** ART_BIBLE v2 §1.2 locks the World look as Cv2 low-poly plus E cel: 3 toon bands, wobbly ink, grime, bloom, spill, haze and rain. The "real" look sets `band=0` and `ink=0`, so it is **off-style as a ship look**.
>
> Treat it as a lighting and atmosphere study. Carry its value structure, fog and wet ground into the hybrid or cel look (`post_aaa.LOOKS["hybrid"]`), not the reverse. "2077 quality" here means 2077's **light, air, density and grade**, not its surfaces.

---

## 1. Overall verdict

Today this is a **good mobile or indie neon-city mood frame, about 4/10 against the 2077 bar**. The bones are right: wet street, rain, layered skyline, coloured alley light and a strong route overlay. But it is **lit like a showroom, not a night**.

Four things put it far from 2077, and they are cheap to fix:
- the exposure;
- the haze veil;
- neon that clips to white;
- a flat emissive hierarchy.

Two things are a bigger job: **density** (greebles, signage, windows) and **scale** (megastructures, depth layers).

| Axis | Score /10 | One line |
|---|---|---|
| Lighting | **3** | Everything is lit, so nothing is lit. There are no dark pools, the hierarchy is inverted (white ahead rooms out-shine the orange options), and neon cores clip. |
| Atmosphere / fog | **4** | Rain and street mist work. The upper fog is cotton-ball noise, not strata. One lavender veil sits in front of every layer. |
| Materials / wet surfaces | **5** | The puddle break-up is genuinely good. It is missing vertical specular streaks, roughness variation and wet facades; rain has one layer. |
| Detail density | **3** | Facades are bare slabs with a dot grid. There is almost no signage content, no cables and no clutter. R1/R2/R3 are dense at every scale. |
| Scale / depth | **3** | The towers top out inside the frame at similar heights. There is one mid-ground plane, no near silhouettes, and nothing vanishes up into fog. |
| Colour and grade | **3** | Pastel candy (lavender, mint, baby pink) with lifted blacks. 2077 is saturated hue against near-black, with a dominant pair per shot (R1 red/magenta and cyan; R2 teal and red-orange; R4 lime and teal). |
| Composition | **5** | The route band reads left to right and the TARGET tower is the darkest mass (good). There is no focal pool at the decision, a horizontal laser line cuts the frame, and the brightest blobs sit away from the choice. |
| UI readability | **6** | The overlay is crisp and its colours are right. The 3D fights it: the white ahead rooms are the hottest objects, rain crosses the stickers, and city neon reuses lime, orange and white. |

---

## 2. What already works (keep these)

1. **The puddles and reflections** (designer-approved). The mottled puddle mask, the colour pickup from shop fronts and the dark gaps between puddles are the right pattern. Keep the mask and the shader; only add what §3 #10 says.
2. **Rain lit by the glow** (`post_aaa` rain alpha follows the blurred bloom). Streaks catch light near signs and stay dark elsewhere. This is exactly how R1's rain reads.
3. **Room spill.** The Rack room (option 2) throws gold onto its facade and the street, and the elite rooms read warm. This is the one place the render behaves like 2077: a practical light shaping its surroundings. Make every option do it.
4. **Alley up-lights in alternating hues** (pink / cyan / violet between columns). They separate the columns in depth. Keep them; just dim them (§5).
5. **The TARGET tower is the darkest mass in the frame**, so the red pencil circle pops. Use this principle everywhere: dark mass behind important things.
6. **Street-level storefront glow** gives a believable base layer of light (R1 and R2 both build their light from street level up). Keep it, at about half strength.
7. **Searchlights and sky-traffic elements exist.** They are just lost in the veil.
8. **The overlay craft:** the lime walked cable, the orange dashed options, the numbered chips, the red pencil TARGET. It is on-bible and sharp.

---

## 3. The top 10 gaps, ranked by impact

The numbers match `CRITIQUE_markup.jpg`. Value targets are sRGB luma after the tonemap, unless marked "scene-linear". "Blender" means `light_aaa.py`, `mats_aaa.py` and `post_aaa.py`. "Godot" means 4.7 Forward+.

### 1. Exposure and veil: the frame has no night in it
- **2077 (R1, R2, R4):**
  - The median is 0.13–0.16, and 29–41 % of the frame is under 0.10.
  - The darkness is *designed*: facades fall to near-black between light sources, so every neon reads as a light.
  - Haze lives **between** depth layers, never as a uniform screen in front of them.
- **This render:**
  - The median is 0.43; only 9 % of the frame is under 0.10, and the street crop has 2 %.
  - `front_air` (0.00045), `back_haze` (0.0055 in "real"), `vol_k=2.6`, `lift=(0.006, 0.016, 0.022)` and `exposure=1.25` stack into a lavender milk over everything. That milk is also what makes the colours pastel (#3).
- **Fix (Blender):**

  | Setting | From | To |
  |---|---|---|
  | `exposure` | 1.25 | **0.75** (−0.74 EV) |
  | `vol_k` | 2.6 | **1.3** |
  | `front_air` density | 0.00045 | **0.00008** (keep it only so the lamp cones show) |
  | `back_haze` density | 0.0055 | **0.0025** |
  | `lift` | (0.006, 0.016, 0.022) | **(0, 0, 0.004)** |
  | `tint_k` | 0.55 | **0.30** |

  - Keep `street_mist` (0.008): it pools at the base, like R1.
  - Targets to check with `crit_stats.py`:
    - median L **0.14–0.18**;
    - p95 **0.65–0.75**;
    - **≥ 25 %** of pixels under 0.10;
    - **≤ 2.5 %** over 0.85.
- **Feasible:**
  - **Blender: now** (parameter changes only).
  - **Godot:** yes.
    - Set `Environment.tonemap_exposure`.
    - Keep `volumetric_fog_density` low (about 0.002–0.005 per BU equivalent) and use `FogVolume`s for the local layers.
    - Do not lift blacks in the LUT.

### 2. The emissive hierarchy is inverted: the wrong things are the brightest
- **2077:** the brightest thing in a frame is where the designer wants the eye.
  - In R1 that is the truck's headlights and the reflection under them. The neon signs are bright but small, and the windows are dim.
  - In R2 it is the ALL FOODS sign and the gate's red tubes. The office windows sit around 0.4–0.6 and are tiny.
- **This render:**
  - The **white "ahead" rooms (L5)** and the **white option 1 room** are blown to 0.95+, as are the **pink billboards at street level** (bottom centre, bottom left) and the **pink holo panel** mid-right.
  - The orange options are *not* the peak. Option 1's interior is a white void.
  - `room_k` for ahead rooms is 1.0 against 1.8 for options, but the white interiors plus the ACES shoulder flatten that difference to nothing.
- **Fix:** apply the ladder in §5.
  - `room_k`:

    | Rooms | From | To |
    |---|---|---|
    | Ahead (white ring) | 1.0 | **0.35**, tinted cool (6500–8000 K) and desaturated |
    | Past (grey) | 0.3 | **0.12**, plus a visible interior (#9) |
    | Options | 1.8 | **1.8**; give the interior the **type colour plus a warm 2700 K key**, never pure white |
    | Current room | — | **1.1** |
    | TARGET | — | **1.7**, red-amber |

  - Cap street billboards at **35 %** of their current emission.
  - Allow **one** hero sign per screen, which must sit **off the decision set**.
  - Run `crit_stats.py` on the route band: options must be the top 1 % of 3D luminance.
- **Feasible:**
  - **Blender: now** (job `room_k` and `mats_aaa` strengths).
  - **Godot:** yes. Room emission is a per-instance uniform driven by node state, which is already planned for the hover power cut.

### 3. Neon clips to white, and the grade is pastel
- **2077:**
  - Neon tubes keep their hue right up to a thin hot core: R1's "24時間" red and the cyan sign at left; R2's green vertical sign and red gate tubes.
  - The halo is **more saturated than the core**.
  - The palette per shot is **2 dominant hues plus 1 accent** on near-black (R1: magenta/red and cyan, warm headlight accent; R2: teal and red-orange; R4: lime and teal).
  - Knapik graded with a film-style 3D LUT, not a stock tonemapper (Foundry interview).
- **This render:**
  - `neon=6.0` through a per-channel ACES fit pushes every strip to white; the saturation of bright pixels is 0.17, the lowest of all images.
  - With the veil, the scene reads as lavender, mint and baby pink.
  - The palette also sprays every hue (lime, orange, gold, mint, pink, violet, cyan), so nothing dominates.
- **Fix:**
  - **(a) Hue-preserving shoulder.** Tonemap on `m = max(r, g, b)`: `out = c · T(m) / m`. Blend 20 % toward the per-channel ACES result only where m > 4, so the hottest pixel still whitens.
  - **(b) Split the neon.**
    - Hero signs: `neon_hero = 6–8`, at most 6 per frame.
    - Trims and ledges: `neon_trim = 1.2–1.8`.
    - Today every ledge has the same strip at 6.0.
  - **(c) Palette lock for the route screen.**
    - City neon uses **magenta #FF2A8A, cyan #2AD4FF, violet #8A3DFF, red #FF2A2A**, and sodium amber only at street level, 2000 K.
    - **Exclude hues within ±18° of lime #D4FF00, the run orange #FF8C1A and pencil yellow #FFE200 anywhere near the route** (see §6).
    - Pick one dominant pair per corp district (Meridian: cyan and magenta).
  - **(d) Grade.**
    - `sat` 1.12 → **1.0** globally (the hue-preserving tonemap brings the colour back).
    - Contrast **1.25 around a pivot of 0.18**, not 0.5.
    - Shadow tint **teal-navy (0.25, 0.45, 0.6) at 0.3**.
    - Highlight tint stays warm.
- **Feasible:**
  - **Blender: now** (`post_aaa.aces` and grade; one material split in `mats_aaa`).
  - **Godot:**
    - Use `tonemap_mode = AgX` (Godot ≥ 4.4), which is more hue-stable than ACES.
    - Add `adjustment_color_correction` with a **3D LUT (33³) baked from the Blender post grade**, so the concept and the game match.
    - Keep neon energy at ≤ 4× white and let **glow** carry the hot look:
      - `glow_hdr_threshold 1.0`, `glow_intensity 0.6`, levels 3–6;
      - blend mode **Additive** for the neon layer.

### 4. The fog is cotton-ball blobs, not strata
- **2077:** R1's steam is a **dense column with a lit underside** (cyan and magenta from the signs below), against dark air. Badlands and City Center haze is **layered**: each depth plane has its own haze value, so tower bases fade before tower tops.
- **This render:** the upper sky has isotropic FBM blobs, lavender, lit from the top. They read as clouds of cotton wool behind glass, and the same density veils the near and far towers alike. See §4 for the full recipe.
- **Fix:** see §4. In short: stretched noise at 20:1 or more, domain warp, crisp remap, an asymmetric profile, underlight, edge fade, and clear air between the bands.
- **Feasible:** **Blender: now** (`strata_mat` edits). **Godot:** use cards (froxel fog cannot resolve thin, distant bands); see §4.

### 5. No megastructure scale; one depth plane
- **2077:**
  - R3 is a megabuilding drum with **floors of ad screens, running out of frame**, and towers behind it receding in at least 4 value steps.
  - R1 is a canyon whose walls exit the top of the frame, with sky showing only as a slot.
  - R2 has towers rising past the frame top, a gate in front, and a car and bollard as **near silhouettes**.
  - Scale reads because **you never see the top** and **layers separate by value**.
- **This render:**
  - Most crowns end at about y 120–300 px, at similar heights, under a lot of sky.
  - The far city is a flat dot field.
  - There is no foreground silhouette: the lamp posts and van are culled or lost in the haze. The sky traffic is invisible.
- **Fix:**
  - **Heights:**
    - At least **3 mid-row towers run out of the top** of the usable area (60–110 BU tall at the current scale).
    - Use **2 megastructure masses** (a 40–60 BU-wide slab or drum with set-backs and ad bands) behind L2 and L6. Never behind an option room; see §6.
  - **Value stepping by layer** (facade value, scene-linear):

    | Layer | Facade value |
    |---|---|
    | Near silhouettes | 0.00–0.02 |
    | Route row | 0.03–0.08 |
    | Mid row | 0.06–0.10, with 0.15 more haze |
    | Far 1 | 0.10–0.14 |
    | Far 2 | 0.16–0.20, against a sky glow of 0.12 at the horizon falling to 0.04 at the top |

  - **Near layer:** 2–3 **near-black foreground silhouettes** (gantry, cables, a sign back) at the frame edges. The existing occluder rule keeps them off protected rooms.
  - **Sky traffic:** **one lane in front of the far city** at 1.5× its current emission, with **2–4 s light-trail streaks** (the motion-blurred tails R1 and R3 imply).
- **Feasible:**
  - **Blender: now** (`dress_aaa` and `city_view` heights, the layer dims).
  - **Godot:** yes. The far layers are impostor cards (already planned), and the megastructures are 2–3 more meshes.

### 6. Bare facades: no greeble density
- **2077:**
  - At every scale, R3 shows AC units, ducts, bracket-mounted signs, hanging cables, an elevated track and set-back balconies.
  - R1 has **power and data cables across the street**, bay windows with frames, rails, umbrellas and lanterns.
  - R2 has the gate's tile roof, shutters, a trash pile and lanterns.
  - The greebles are at **0.3–1.5 m** (window-frame scale) **and 3–8 m** (sign boxes, tanks, balconies).
- **This render:** flat slabs with emissive window rectangles and ledge neons. The architecture sheet's connection types are rich; the facades around them are empty.
- **Fix:** a seeded greeble kit, with counts per column at the current scale (1 BU ≈ 1 m):

  | Greeble | Count / placement | Size |
  |---|---|---|
  | AC boxes | **12–20** | 0.8 × 0.6 × 0.5 BU |
  | Vertical ducts or pipes | **3–5** | 0.3–0.6 BU diameter |
  | Sign brackets with blade signs | **2–4** | 1.2 × 4 BU |
  | Balcony or ledge strips | every **2–3 floors** | 0.4 BU deep |
  | Rooftop tanks, antennas, fans | **4–8** per roof | — |

  - **Catenary cables:** 6–10 across each alley **behind** the route links, 0.06 BU thick, sag 3–6 %. Keep them **out of the route-link screen corridor** (12 px margin, the same rule as the occluders).
  - Greebles take **spill only** (no emission), so they add silhouette and the facades stay dark.
- **Feasible:**
  - **Blender:** about a day. A kit plus seeded scatter in `dress_aaa`, through the existing `RngService`-style seeds.
  - **Godot:** yes. One MultiMesh per greeble type per building family (the §6.1 `CityModel` already plans prop MultiMeshes).

### 7. Blank signs and holograms: no ad content
- **2077:**
  - Signage is the identity: in R1 the "WET DREAM" screen, the vertical pink and purple blade signs and the kanji neon; in R2 a face billboard on the tower, ALL FOODS, a KIROSHI logo and lanterns; in R3 the ad drum.
  - Ads have **imagery plus type plus a frame**.
  - Holos have scanlines and a slight RGB split.
- **This render:** the billboards are flat glowing pink and white rectangles, the holo is a faint wire sphere, and HALCYON is the only legible sign. NOTES.md already lists "Mid-row signs show stripes and a disc" as not done.
- **Fix:**
  - **Draw** 12–16 ad textures in our language (corp logos from `emblems20.py`, Anton type, product silhouettes, the Meridian/Solace/Halcyon kits). **Do not copy 2077 ads.**
  - Use **3 sign classes**:
    - blade signs, vertical, 1:4;
    - box billboards, 16:9, with a dark frame and 4 floodlights;
    - holo panels with 3–4 px scanlines, a ±1.5 px RGB split on the edge, 30–50 % alpha and a slow band.
  - **Emission:**
    - billboard content **1.2–2.0** scene-linear (content readable, not blown);
    - the floodlights carry the hot points.
  - Signage lives in the **mid row and street level**, never directly behind an option room (§6).
- **Feasible:**
  - **Blender:** texture work (about a day for the set).
  - **Godot:** trivial. An emissive material with an atlas and a scanline shader, with the flicker on a seeded `RngService` stream.

### 8. Window confetti
- **2077:** in R2 the office towers are **floor-banded grids**:
  - mostly one warm-white temperature (3000–4000 K), lit in **runs** (whole floors or bays) with dark floors between;
  - some windows have blinds or interior silhouettes;
  - a few are cool fluorescent.
  - In R1 the residential windows are mostly **dark**, with frames visible by spill.
- **This render:** same-size squares in random pink, amber, cyan and white, randomly lit, evenly spread. They read as Christmas lights, not floors, and add a pastel noise layer everywhere (`win=1.85`, `gs=0.65`, far `×0.55`).
- **Fix:**
  - **Lighting logic:**
    - Light by **floor run**: P(floor lit) = 0.35, then P(window lit | floor lit) = 0.75, with occasional 2–4-window dark gaps.
    - Colour: **80 % warm 3200 K, 15 % cool 5500 K, 5 % accent** (from the district pair only).
    - Per-window intensity varies log-normally (σ 0.5).
  - **Strengths:**

    | Setting | From | To |
    |---|---|---|
    | `win` | 1.85 | **0.55** |
    | `gs` | 0.65 | **0.18** |
    | Far windows | ×0.55 | **×0.30** |

  - **Shape:** **2 window shapes per building family** (a tall office strip; a residential 2×3 with a frame). Add a blinds mask on 30 % of windows.
- **Feasible:**
  - **Blender: now** (the `mats_aaa` window grid shader; replace the `wsep` thresholds with floor-hash logic).
  - **Godot:** yes. It is a procedural window shader on the building material (hash of floor index and bay index), with no textures needed.

### 9. Dead grey plaques: unlit rooms read as UI holes
- **2077:** even unlit interiors have *some* light: the R4 bar interior and the R2 under-gate cavity hold soft cyan fill and visible props. Darkness is never a flat grey card.
- **This render:** the past and unavailable rooms (L2 and L3 upper floors, among others) are flat mid-grey boxes with a ring. They are **brighter than a night facade** (L ≈ 0.25), so they read as empty UI slots pasted on the buildings rather than dark rooms.
- **Fix:**
  - Past and cut rooms go **dark (interior L 0.06–0.10)**.
  - Keep **one dim practical**: a monitor glow or an exit sign at 0.15–0.20 in the room's type colour at 40 % saturation.
  - Keep the props visible through 15 % fill.
  - The grey ring stays as the state carrier (the bible's option A).
- **Feasible:**
  - **Blender: now** (`room_k` past 0.12, plus one small emissive prop per room in `dress_aaa`).
  - **Godot:** yes (per-room state uniform).

### 10. Street and rain: a laser line, no spec streaks, flat rain
- **2077 (R1):**
  - Wet asphalt reflects lights as **vertical streaks** (rough-wet BRDF at a grazing view), clearest under the headlights.
  - There is **roughness variation**: puddles are mirrors, damp asphalt is glossy-rough, and painted lines and grates break it up.
  - Kerb strips are short, broken light segments.
  - Rain falls in depth layers, with a few bright near streaks.
- **This render:**
  - The puddles are great, but the reflections are round blobs (mirror puddles only).
  - A **lavender neon line runs across the full 1280 px** at y ≈ 600 and fights the route's horizontal cables.
  - The rain is one uniform layer of long streaks, including over the stickers.
- **Fix:**
  - **Street roughness:** three levels.

    | Surface | Roughness |
    |---|---|
    | Puddles | 0.03 |
    | Damp asphalt | **0.22–0.32**, with a noise-modulated normal (ripples 0.5 BU, strength 0.15) |
    | Paint and grates | 0.5 |

    In Cycles, roughness 0.25 at the 6–9° camera pitch gives the vertical elongation for free.
  - **Post fallback:** a vertical-only blur (σ_y = 3 × σ_x) of the reflected emit buffer inside the street mask.
  - **The laser line:**
    - break it into **2–6 BU kerb segments** with gaps;
    - lower it to 30 % emission;
    - or delete it. The route needs that horizontal to itself.
  - **Rain, 3 layers:**

    | Layer | Density | Length | Alpha |
    |---|---|---|---|
    | Far mist | 4000 | 4 px | 0.05 |
    | Mid | 1800 | 18 px | 0.10 |
    | Near | 60 | 60–90 px | 0.25, motion-blurred, lit by the glow |

    - Add **splash ticks** on puddles and ledges (seeded, 2–3 frames each).
    - Cut rain **to ×0.25 inside the protected room boxes and a 6 px dilation of the route cables**.
- **Feasible:**
  - **Blender: now.**
  - **Godot:**
    - SSR (`ssr_max_steps 64`, `ssr_fade_in 0.15`, `ssr_depth_tolerance 0.4`) on the street.
    - A **street-material screen-texture smear** (sample `SCREEN_TEXTURE` with a vertical kernel above the fragment): the cheap, always-on version of streaks, and it also reflects signs that SSR loses off-frame.
    - A ReflectionProbe for the base.
    - Rain as the planned screen-space shader with 3 layers.

---

## 4. Fog and smoke: streaky, wind-sheared strata lit from below

### What is wrong now
- **The test render:** the visible "fog" is the haze boxes plus FBM noise with little anisotropy. It reads as cotton.
- **The strata work in progress** (`scratch/vol_strata.png`) is the right direction (horizontal bands now exist), but:
  1. **Hard rectangular edges** show where the volume boxes end (top band, upper right). The density is not faded at the box x, y and z bounds.
  2. **The bands are lit from the top and back** (moon and backglow), so their undersides are dark. That is the opposite of "lit from below".
  3. **There is no clear air between the bands.** The base haze fills the gaps, so the bands merge into one smeared sheet.
  4. **The noise is still too isotropic at the small scale.** The streaks are short scratches, not long sheets.

### The look to hit
Think of R1's steam column (dense, with a sign-lit underside against dark air), turned sideways and stretched by wind:
- **4–6 thin, long bands** at different heights and depths;
- each band has a **crisp, bright underside** (the city light) and a **soft, dark top**;
- the bands are **sheared** and drift at different speeds;
- tower tops **pierce** the bands;
- the air between the bands is **dark and clear**.

### Blender recipe (edit `strata_mat` and `STRATA` in `light_aaa.py`)
1. **Anisotropic coordinates.** Change the noise vector from (x·0.006, y·0.04, z·0.35) to **(x·0.0035, y·0.02, z·0.6)**, so features are about 285 BU long and about 1.7 BU thick (a 170:1 ratio). Replace the shear term.
   - **The problem:** the current `x + z·shear` adds only 0.006 · 2.5 ≈ 0.015 per BU of z, against a z scale of 0.35. That is negligible, so the bands show no wind tilt.
   - **The fix:** tilt the vertical coordinate instead: `z' = z − x·tan(θ)` with **θ = 2–4° (0.035–0.07)**, applied before the 0.6 scale. Give each band its own θ and sign variation (±1°), so the bands are not parallel.
2. **Domain warp along the wind.** Add a second noise (scale 0.01, detail 2) times **35 BU** to x before the main noise. This gives the torn, combed edges.
3. **Crisp remap.** Change `MapRange` From_Min/From_Max from 0.50/0.78 to **0.56/0.70**, then apply power 1.4 (keep it). This produces gaps.
4. **Asymmetric profile** (v = 0 at the bottom of the band, 1 at the top): `prof = smoothstep(0, 0.12, v) · (1 − v)^1.6`. The bottom is sharp and the top feathers out.
5. **Edge fade.** Multiply by `smoothstep(0, 0.15, u_x) · smoothstep(0, 0.15, 1 − u_x)`, and the same for y (generated coordinates). This kills the box rectangles.
6. **Clear air between the bands.** `back_haze` 0.0055 → **0.0020**. The strata peak can rise to **0.035–0.045**. The target band:gap in-scatter ratio is **≥ 6:1**.
7. **Light from below.**
   - Option (a): raise the `cityglow_*` area lights from 2.5e5 to **6e5**, narrow them to the district pair (magenta and cyan), place them **at z 6–20 under each band**, and reduce the moon and backglow by 50 % in the volume pass.
   - Option (b), cheaper and controllable: add an **emission term** to the strata shader:

     `emit = density · underlight_rgb · (1 − v)^3 · 0.35`

     Here `underlight_rgb` is a 1D x-gradient of the street's dominant hues.
   - Do both, and use (b) to tune.
8. **Anisotropy.** Change 0.3 to **0.55**. The bands sit between the camera and the backglow and the far searchlights, and forward scatter gives the silver lining on the band edges.
9. **Heights and depth.**
   - Space the bands so they **thicken and get further apart with height**: z 28–32, 44–49, 64–71, 92–100, 130–140.
   - Push the higher bands deeper in y (the farther layers).
   - The lowest band must sit **above the highest option room plus 6 BU**, so it never crosses a room.
10. **Motion** (video and Godot):
    - x scroll per band of **3, 4.5, 6, 8 and 10 BU/s** (parallax: faster near);
    - plus a W evolution of 0.05/s, so the shapes morph without boiling.

### Godot 4.7 Forward+ recipe
Froxel volumetric fog (`volumetric_fog_length` with 64 depth slices) **cannot resolve 2–6 BU bands at 150–500 BU**, so the bands would smear into a single slab. Build them as cards instead:
- **Per band:** 1–2 `MeshInstance3D` quads, 600 × 14 BU, placed at the band's depth: 5 bands give about 10 draws.
- **Shader** (unshaded, `blend_mix`, `depth_draw_never`, `cull_disabled`):
  - `uv_n = vec2(x·0.0035 + TIME·wind_i, v·0.6 + x·shear) + warp·35/600`;
  - sample a **seamless `NoiseTexture2D` (FastNoiseLite FBM, 1024 × 128, 5 octaves)**;
  - `smoothstep(0.56, 0.70, n)`;
  - multiply by the asymmetric profile and the edge fade from the Blender recipe;
  - colour = `mix(underlight_rgb(x), top_rgb, v)`;
  - alpha ≤ 0.55.
- **`proximity_fade` 25 BU**, so towers pierce the bands softly; `distance_fade` for the far layer.
- **Blend mode:** **mix, not additive**. Additive bands are the veil again. Add a separate low-alpha additive "underlight lip" on a second UV row for the glow.
- **Real volumetrics** stay only on the street: a `FogVolume` box, `FogMaterial.density 0.03`, `height_falloff 0.4`, with `light_energy`/`volumetric_fog_energy` on the kerb lights at 1.5 so the lamp cones read.
- **Settings:** VfxTier low = 2 bands, static; "reduce motion" = no scroll (bible §5.4).

---

## 5. Brightness: the exposure and emissive hierarchy

**The rule:** **route > lit rooms > signage > windows > sky**, with the darkness *between* them doing the work. All targets are sRGB luma after the tonemap, measured with `crit_stats.py`. Area limits stop "small but hot" from turning into "big and hot".

| Tier | Element | Target L (display) | Max frame area | Blender lever (scene-linear, after `exposure 0.75`) |
|---|---|---|---|---|
| 0 | **Route overlay** (cables, stickers, chips, the red pencil) | 0.85–1.0, drawn 2D on top | — | Plus a **local darken** under it (§6) |
| 1 | **Option rooms** (orange) | interior **0.70–0.82**; spill on the facade 0.25–0.35 | 2 % | `room_k` 1.8; interior emission in the type colour plus 2700 K, never white |
| 1b | TARGET room | 0.70–0.80, red-amber | 0.5 % | `room_k` 1.7 |
| 2 | Current room / lime walked rooms | 0.45–0.60 / 0.30–0.40 | — | `room_k` 1.1 / 0.6 |
| 3 | Ahead rooms (white ring) | **0.28–0.38**, cool | — | `room_k` 0.35, 7000 K |
| 4 | Hero signs (at most 6, off the decision set) | core 0.80–0.90, halo 0.35–0.5 | 0.6 % | `neon_hero` 6–8, hue-preserving tonemap |
| 5 | Billboards (content) | 0.35–0.55 | 3 % | emission 1.2–2.0 |
| 6 | Trim neon, kerb strips | 0.30–0.50 | 1 % | `neon_trim` 1.2–1.8 |
| 7 | Street light pools / reflections | pools 0.15–0.30; streaks up to 0.6 | — | kerb 2600 → **1800** (sodium 2000 K); fg lamps 2200 → **1400** |
| 8 | Windows | 0.12–0.30 | 4 % | `win` 0.55, `gs` 0.18, far ×0.30 |
| 9 | Fog bands | underside 0.18–0.28, top 0.06 | — | §4 |
| 10 | Facades (spill only) | 0.03–0.10 | — | `alb` 0.85 is fine, once the veil is gone |
| 11 | Sky | 0.04–0.10; horizon glow 0.12–0.20 | — | `backglow_m` 8e7 → **3e7**, `backglow_c` 4.5e7 → **1.8e7** |

**Whole-frame acceptance:**
- median **0.14–0.18**;
- p95 **0.65–0.75**;
- **≥ 25 %** of pixels under 0.10;
- **≤ 2.5 %** over 0.85, and nearly all of those must be the overlay or the option rooms;
- saturation of bright pixels **≥ 0.25**.

The references measure: median 0.13–0.16, 29–41 % under 0.10, 1–3 % over 0.85, bright-pixel saturation 0.19–0.35.

**Hover power cut.** The bible's ×0.32 cut now applies to a much darker base. Check that the cut rooms stay above L 0.04, so the street shape remains.

---

## 6. Readability risks: where the realism fights the route

1. **Hue collisions.**
   - City emissives currently use lime (the L2 crown strip), orange and gold (L4 windows, kerb sodium near option 1) and white (every trim). Those are the **route's state colours**: lime = walked, orange = next, white = ahead.
   - **Rule:** inside the decision set's screen box plus 80 px, no city emissive within ±18° of hue of #D4FF00, #FF8C1A or #FFE200, and no white emissive above L 0.5.
   - 2077's signature yellow (#FCEE0A) sits between lime and pencil yellow. **Do not adopt it as a city neon colour here.**
2. **White rooms equal the "ahead" state.** If ahead rooms are rendered white-hot, white means "brightest", not "not yet". Keep them cool and dim (tier 3).
3. **Bloom bleeding onto the chips.**
   - The option-1 room's bloom halos the number chip and the fight sticker.
   - Mask bloom out of the overlay (the overlay is composited after bloom, as now).
   - Clamp room bloom to radius ≤ 8 px at 1080p near the chips.
4. **Rain over the stickers.** Rain at full alpha crosses the stickers and the room openings. Cut it to ×0.25 inside the protected boxes plus a 6 px cable dilation (#10).
5. **Fog over the rooms.** The lowest stratum must sit above the highest option + 6 BU. The front air must stay ≤ 0.0001, so the rooms never sit behind milk.
6. **Busy backgrounds behind the options.**
   - Megastructures, billboards and greebles **never sit directly behind an option room**.
   - Use a **"calm zone"**: the option's screen box plus 40 px has background facade L ≤ 0.08, with no signage and no cables.
   - Apply it in placement (the seeded scatter rejects positions whose projected box hits a calm zone), like the existing occluder rule.
7. **A local darken under the route** (a cheap insurance that 2077 also uses via UI scrims):
   - a soft 0.15–0.25 multiply (radius 24 px) along the route cables and option rooms, in the post or a Godot `CanvasLayer` before the overlay;
   - invisible at a glance, and it buys contrast for the dashed lines.
8. **The horizontal laser line** (#10) is a false route line. Break it up or remove it.
9. **Greyscale check.**
   - Bible pillar 1: "readable first", including in greyscale.
   - After the fixes, desaturate the frame: options 1 and 2 must be the two brightest 3D objects in the route band, and the cables must still separate from the facades.
   - Add this to the 3-second check.

---

## 7. Next render recipe (one pass)

Apply this to the hybrid look first; the real look is a study only.

**Exposure and grade (`post_aaa.py`)**
- [ ] `exposure` 1.25 → **0.75**
- [ ] `lift` → **(0, 0, 0.004)**
- [ ] `tint_k` → **0.30**
- [ ] shadow tint **(0.25, 0.45, 0.6)**
- [ ] `sat` → **1.0**
- [ ] contrast **1.25 around a 0.18 pivot**
- [ ] Replace the per-channel `aces()` with a **max-RGB, hue-preserving shoulder**, with a 20 % per-channel blend above m > 4.
- [ ] Bloom: threshold 0.75 → **1.2**, weights → **(0.12, 0.10, 0.08)**, widest radius ×1.5
- [ ] `vol_k` 2.6 → **1.3**

**Volumes (`light_aaa.py`)**
- [ ] `front_air` → **0.00008**
- [ ] `back_haze` → **0.0020–0.0025**
- [ ] keep `street_mist`
- [ ] Strata, all per §4:
  - [ ] coordinates (0.0035, 0.02, 0.6)
  - [ ] warp 35 BU
  - [ ] remap 0.56 / 0.70
  - [ ] asymmetric profile
  - [ ] 15 % edge fade
  - [ ] peak 0.035–0.045
  - [ ] anisotropy 0.55
  - [ ] underlight emission term 0.35
  - [ ] lowest band ≥ the highest option + 6 BU

**Lights**
- [ ] `room_k`: options 1.8, TARGET 1.7, current 1.1, walked 0.6, **ahead 0.35 (cool)**, **past 0.12**
- [ ] Option interiors: type colour plus 2700 K, never white.
- [ ] kerb 1800 (2000 K)
- [ ] fg lamps 1400
- [ ] backglow 3e7 / 1.8e7
- [ ] cityglow 6e5, placed under the bands

**Materials (`mats_aaa.py`)**
- [ ] Split `neon` into **hero 6–8** (at most 6, off the decision set) and **trim 1.2–1.8**.
- [ ] `win` 0.55, `gs` 0.18, far ×0.30
- [ ] Floor-run window logic: P 0.35 / 0.75; colour 80 / 15 / 5 %.
- [ ] Street roughness 0.03 / 0.25 / 0.5, with a ripple normal.

**Palette**
- [ ] Use the district pair magenta #FF2A8A and cyan #2AD4FF, plus violet and red accents.
- [ ] No lime, orange, yellow or white emissives within 80 px of the decision set.

**Dressing (`dress_aaa.py`)**
- [ ] Greeble kit: AC 12–20 per column, ducts 3–5, blade signs 2–4, ledges every 2–3 floors, roof clutter 4–8.
- [ ] Alley cables: 6–10, 0.06 BU, sag 3–6 %, out of the route corridor.
- [ ] 3 towers running out of the frame top.
- [ ] 2 megastructure masses, out of the calm zones.
- [ ] 2–3 near-black foreground silhouettes at the frame edges.
- [ ] One sky-traffic lane in front of the far city, at 1.5× emission, with trails.
- [ ] Past and cut rooms dark, with one dim practical each.
- [ ] Ad textures: 12–16, our own art (corp kits); blade, box and holo classes.

**Street and rain**
- [ ] Kerb laser line: 2–6 BU segments at 30 %, or removed.
- [ ] Rain in 3 layers (4000 / 1800 / 60) plus splash ticks.
- [ ] Rain ×0.25 in the protected boxes.

**Overlay**
- [ ] Local darken 0.2 under the cables and options.
- [ ] Bloom masked from the chips.

**Check (`python critique_scripts/crit_stats.py <render> <outdir>`)**
- [ ] median 0.14–0.18
- [ ] p95 0.65–0.75
- [ ] ≥ 25 % of pixels under 0.10
- [ ] ≤ 2.5 % over 0.85
- [ ] saturation of bright pixels ≥ 0.25
- [ ] The greyscale check: options are the brightest 3D objects in the route band.
- [ ] Re-run `check_occlusion.py`.

**Style lock**
- [ ] Keep the ink and the 3 toon bands (hybrid `ink 0.62`, `band 0.45`). The realism carries over in **value, air and wet ground**, not in surfaces.
