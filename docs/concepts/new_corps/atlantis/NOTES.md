# TETHYS DEEP (the Atlantis corporation): concept package (2026-10-15)

An exploratory sixth/seventh corporation: a corporate deep-sea arcology. It is not locked content, and nothing is
committed. The Godot build is untouched.

## Files

| File | Section | What it is |
|---|---|---|
| `identity.md` + `identity_board.png` | A | Name, tagline, what they sell, the slots, the house rule, palette with the clash check, type accent, voice |
| `crest_options.png` | B | Four wave-crest options; pick A TIDE WHIRL (designer, review 2); where the nautilus went |
| `crest_icons.png` | B | The crest (vinyl, flat, 64/32/16 px), Site marker states, 6 Site-type stickers, the 32 px + twin check, the boss emblem (reference), the letterhead |
| `district.png` | C | The drowned ward, underwater, in the AAA-2 look adapted to water (Blender) |
| `building_kit.png` | C | Every building generator on a plinth |
| `hq_overview.png` | D | ATLANTIS STATION: the HQ netrun as a side cutaway, the route, the tide, the TARGET on THE BLACK SMOKER |
| `hq_mechanic.png` | D | THE BALLAST TIDE: four tide steps and the visual states (PROPOSAL) |
| `site_street.png` | F | A Site run in the V3 side-view street, underwater |
| `boss_wheel_options.png`, `boss_wheel.png` | E | **Reference only**: boss wheels moved to `docs/concepts/boss_wheel_v2/` |
| `boss_wheel_ideas.md` | E | Ideas for the Boss Wheel v2 agent |
| `scripts/` | | Everything needed to rebuild (the shared scripts are identical to `roman/scripts`) |

## Design rationale
- **Distinct from the four corps:**
  - Solace sells implant subscriptions and Halcyon runs city water pipes. Tethys sells **the waterline itself** (who
    stays dry) and **the air** in the flooded wards, and it keeps the city's memories in cold storage under the sea.
  - Its villainy is quiet: it never attacks, it just lowers the water.
- **Distinct from Aurelian:**
  - **Down versus up:** water, depth and silence against stone, sky and crowds.
  - **Hue:** abyss blue against verdigris.
  - **HQ mechanic:** a vertical cycle (the tide) against a rotating plan (the gates).
- **Corporate arcology, not a fairy tale:**
  - "Atlantis" is a product name: ATLANTIS STATION.
  - The domes are pressure hulls with portholes, the drowned towers are old tenements the company leased back to
    squatters, and the subs are traffic.
  - Bioluminescence (photophore) is world light only. The corp's own light is a hard abyss-blue neon plus red security
    lights.
- **Water replaces rain, everywhere:**
  - fog becomes one absorbing and scattering water medium (red dies first, so the LIGHTLESS RED lore is literally
    true in the render);
  - rain becomes marine snow (in the post);
  - car streaks become sub lanes with wakes;
  - the night sky becomes the bright wavy surface seen from below, with light shafts;
  - puddle reflections become caustics on every upward surface.
- **One idea across all scales:** the TIDE is the combat house rule, the HQ mechanic (the BALLAST TIDE) and the special
  slice on the boss wheel.

## Designer review round (2026-10-15), applied

| Note | Change |
|---|---|
| Crest is the wrong choice | A new crest built from waves. Four options are on `crest_options.png`: A TIDE WHIRL, B MOONWAVE, **C CRESCENT SURF** (picked), D DEEP SWELL |
| The nautilus | Kept: it is now the **ATLANTIS STATION sub-brand mark** (the arcology's own signage, the dossier footer, the HQ gate sticker). It also takes the "shell" read out of the Site icons, so no twin |
| Cable head doesn't fit | Replaced by **BUOY RELAY**: a striped relay buoy riding a swell, its mast light sending signal arcs. It is the same Site type: the sea-cable head's relay |
| Desal doesn't make sense | Replaced by **TAP HOUSE**: a tap on a wall plate with a falling drop. Fresh water sold by the litre: clearer, and nearer the player's life than "desalination" |
| Theme and overall design good | Kept |
| Boss wheel weak | Three options on the real D4 kit (diver helmet, octopus, jellyfish; coral is in the jellyfish rim, a sand dollar was not pursued). B OCTOPUS was picked. The work then moved to Boss Wheel v2 |
| Boss icon | Redrawn to match the octopus wheel (`g_octopus`). Kept here as reference |
| Icon set check | Every icon at 32 and 16 px on `crest_icons.png`. Soft IoU max 0.61 across both corps' 18 new icons, crests and emblems: no twins |

**Why CRESCENT SURF.**
- It is one bold silhouette that says both *moon* and *wave*: the wave is the crescent's inner edge, breaking into a
  barrel, with spray at the lip. It reads at 16 px.
- A (the three-crest whirl) reads as a triskele, and the wave gets lost.
- B and D (stacked swells) fill in or stripe at 32 px.

**Originality.** The mood reference was flowing waves in one round emblem. C does not reuse any existing emblem's
layout: there is no circle with a crescent above three wave lines. Its key idea (the crescent *is* the wave) is our
own.

## Designer review round 2 (2026-10-15), applied

| Note | Change |
|---|---|
| Crest: switch to the TIDE WHIRL (wave and octopus vibes) | The crest is now `g_wave_a`, TIDE WHIRL: three crests turning round a calm centre. It reads as waves and as curling arms, so it rhymes with the octopus boss and with the TIDE cycle. Updated: `crest_icons.png` (crest, Site markers, letterhead), `identity_board.png`, `crest_options.png` (pick A, C kept as the alternative) |
| The octopus boss direction is approved | Passed to Boss Wheel v2 in `boss_wheel_ideas.md` |
| Other icon and Site-type changes approved | Kept |
| Re-check | Twin check across both sets after round 2: **max soft IoU 0.58**. No twins |

The CRESCENT SURF reasoning above is history; the TIDE WHIRL is now the crest.

## GDD fit

| Element | Status |
|---|---|
| A corporation = Sites, enemies, elites, a final boss at the Central Server, 3 Exploits, story paths, raids, events | Fits: `identity.md` fills every slot |
| Boss rule "X every turn unless its Hub is breached" | Fits the existing pattern (OVERCLOCK self, like Orbital's Solar Flare family) |
| TIDE house rule | **New rule** (a visible four-turn cycle). It uses existing SANDBOX shield and adds a per-turn modifier. Needs a GDD line, a HUD element and a test (seeded start = deterministic) |
| THE BALLAST TIDE (HQ mechanic) | **New rule (proposal)**, round 43 family. It depends on the HQ compound proposal |
| Flooded drops as "closed" links | Fits round 43's link grammar (de-power and re-make) |
| An underwater district on the shared City Grid | **Needs a ruling:** the unified city (bible 4.1) is one model with one camera. A drowned ward could be a flooded district of that model (the water surface as a plane at street level, the camera above it), not a separate world. This is the main open question |

## The HQ: ATLANTIS STATION and THE BALLAST TIDE (proposal)

| Element | Rule (`tethys_preset.PRESET["hq"]`) |
|---|---|
| Trench | Walls of jittered rock strata, `trench_w` 370, the surface at z 380 with a dock on top |
| Decks | 5 pressure hulls hung across the trench on a spine, at z 320, 258, 196, 134, 72, with 5, 4, 4, 3, 2 rooms. The rooms are cutaways on the front (the camera side) |
| Drops | Glass tubes between decks (`drops`). State **open** (dry, a dive-light strip), **flooded** (water fill, link closed) or **airlock** (red hatch ring: open every other step) |
| Ballast column | A glass column beside the decks. The water inside stands at `tide_z`, and the glowing waterline is the tide gauge. `tide_next_z` is the pencil telegraph |
| The cycle | LOW > RISING > HIGH > FALLING, one step per move. A drop whose lower end is under the line is flooded |
| Server | THE BLACK SMOKER: vent chimneys with hot mouths, a dark plume medium, a hull ring with abyss-blue strips and a white core ring |
| Camera | A side cutaway (the V3 side view), lens 24 |

## Procedural rules and preset keys (`scripts/tethys_preset.py`)

| Key | Drives |
|---|---|
| `palette` | Abyss, red, trench, photophore, dive, hull, titan, rock, sand |
| `light` | Neon, photophore, window, room, sub head/trail, shafts, sun, surface, **caustic** (strength), dome, red, vent, uplight |
| `water` | density, scatter colour, **absorb** colour (red absorbed first), anisotropy (0.65, forward: the shafts), noise |
| `district` | Avenue length, surface z, block widths, tower heights, domes, the sub lanes `(x, z)`, shafts, camera |
| `hq` | Above |
| `street` | As Roman, plus `surface_z` |
| `kit_sheet` | The grid and the camera |
| `seeds` | district 7101, kit 7102, hq 7103, street 7104, jitter 7105, shafts 7106, snow 7107, kelp 7108, bubbles 7109 |
| `VARIANTS` | `tethys_deep` (default) and `tethys_shallow` (thinner water, stronger shafts: a ward near the surface) |

**Generators** (`tethys_scene.py`):

| Generator | What it builds |
|---|---|
| `drowned_tower` | Wet hull, sparse lit floors, a broken crown, an algae skirt, photophore strips, a red beacon |
| `dome` | Titanium ring with portholes, a glass shell with meridian and parallel ribs, a lit township inside, a point light |
| `glass_tube` | Ribs every 6 m and a dive-light strip |
| `pump_tower` | Abyss rings and red lights |
| `kelp` | A swaying stalk with leaves and a photophore tip |
| `bubbles` | Rising columns |
| `sub` | A capsule hull with an abyss stripe, a headlight and spot, a glowing wake (replaces the car streaks) |
| `seabed`, `surface` | Wavy grids; the surface is emissive from below |
| `room_cut` | The cutaway route room |

**Caustics** are a material rule (`caustic_mat`): two voronoi edge layers on world xy, warped by z, kept only on
up-facing faces and faded by depth (exp(-0.012 · (surface − z))). Every roof, rock and the seabed uses it.

## Godot 4.7 feasibility (the water)
- **Water volume / fog swap:**
  - Volumetric fog with a global density, `albedo` blue-green and `emission` 0, plus height and distance falloff.
  - The "red dies first" look is an absorption tint: Godot's fog has no spectral absorption. Use a per-material
    depth-tinted fade (a shader include: mix toward the water colour by view distance, with red falling off fastest)
    plus the fog.
  - The fog swap between a dry district and a drowned ward is a `WorldEnvironment` resource swap per district (or a
    `FogVolume` box covering the drowned ward only, with its own density), cross-faded on the camera move.
- **Light shafts from above:** SpotLight3D with `light_volumetric_fog_energy` (as the r3 beams), 2-6° cones pointing
  down, shadows on for a few heroes. Or cheaper: additive card shafts (r1's card recipe) under VfxTier low.
- **Caustics:**
  - A `Decal` with an animated caustic texture (two scrolling voronoi layers) projected from above over the visible
    area. It respects normals (up-facing only), and the depth fade comes from the decal's `upper_fade`.
  - Or a triplanar term in the shared material (world xy, as here).
  - Cost: one decal draw over the screen area.
- **The surface from below:** a plane with an unshaded, emissive scrolling normal-noise shader. With SSR off, it is a
  bright wavy ceiling, matching the stills.
- **Marine snow:** GPUParticles3D near the camera (slow fall, a little drift), plus a screen-space layer for the far
  field. It replaces the rain particles one for one.
- **Bubbles:** GPUParticles3D columns at rule-placed emitters (domes, vents).
- **Sub lanes:** the street-streak shader rotated into 3D lanes at depth. The head is a small mesh, the wake an
  additive ribbon. Headlights: only the hero lanes get a SpotLight3D.
- **Kelp sway:** vertex shader (sin of height + TIME, seeded phase).
- **Perf:** comparable to r3. One fog field, 6-10 shaft spots, one caustic decal, particles. VfxTier low: no shafts
  (cards), static caustics.

## Open questions for the designer (for DECISIONS.md)
1. **Where does Tethys live on the unified City Grid?** It could be a flooded district of the one city (the map shows
   the waterline; the netrun dives under it), or a separate campaign map. Recommended: a flooded district, so the one
   model and one camera rule holds.
2. **TIDE:** is a four-step HUD clock acceptable as a new HUD element for one corp?
3. **BALLAST TIDE:** may you swim a flooded drop for an HP cost (a third choice), or are flooded drops strictly closed?
4. **Airlock cadence:** every other step, or tied to the tide (open only at LOW and HIGH)?
5. **Lightless red against HARM.** Material only, never a UI signal. Is that enough, or should tier II be the dive-light
   cream instead?
6. **Abyss blue against Halcyon violet** (ΔE 27). Accept with material and crest separation, or shift the hue a little toward cyan-blue
   (further from Halcyon, but nearer NET_CYAN)?
7. **Central Server name:** THE BLACK SMOKER (alternatives: THE COLD VAULT, THE TRENCH).

## Render log
See the end of this file (filled after the GPU queue).

## Rebuild
As `roman/NOTES.md`, with `tethys_scene.py`, `look=deep` in `nc_post.py`, and `python nc_sheets.py tethys crestopt` for
the crest options.

## Render log (the same block)
All shots: Cycles HIP, plain BVH2, 2560 x 1440, 64 spp with OIDN. Post: `look=deep`, exposure 0.6, marine snow.

| Shot | Render time | Output |
|---|---|---|
| HQ | 253 s | `hq_overview.png` |
| District | 47 s | `district.png` |
| Street | 43 s | `site_street.png` |

- `building_kit.png` is the Eevee preview.
- **Known look gap.** The light shafts are faint in the district. Raise `light.shaft` and narrow the cones for the next
  pass. The trench HQ uses its own thinner water (`water.hq_density`) so all five decks stay readable.
