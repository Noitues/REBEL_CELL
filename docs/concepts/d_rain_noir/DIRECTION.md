# D · RAIN NOIR CINEMATIC

**Pitch:** It is always 3 a.m. and raining. The city goes near-black blue-grey, and colour only shows up where it matters: the two spinners, the pink marker, the one verb you're about to press.

## Three pillars
1. **Darkness is the layout.** About 85% of the frame is desaturated blue-grey. Saturated neon means "look here". The screen's brightest object is always its most important one (Bible 3.1), taken to its limit.
2. **Every light touches something.** Nothing glows in a vacuum. Each emitter spills onto the wet ground, the glass panels, the rain and the stickers' edges. Light explains depth (feedback 10).
3. **Filmed, not drawn.** Shallow depth of field, anamorphic horizontal streaks, a slight vignette, grain and lateral chroma fringe. It stays restrained enough to read as game UI.

## Palette
| Hex | Name | Role |
|---|---|---|
| `#05070B` | Night Ink | Base black, letterbox, sheet ground |
| `#1A2230` / `#2E3A4C` | Rain Slate / Wet Steel | Building masses, console housings, bezels |
| `#6B7A8F` | Haze Grey | Fog, far skyline glow, glass edges at rest |
| `#C9D6E6` | Streak White | Rain streaks, rim catches, dome reflections |
| `#3A4E6C` | Horizon Glow | Light-polluted sky that the skyline silhouettes against |
| `#FF3DA8` | Cell Pink | The marker, the operative's wheel, the Modem sign. The Cell's only voice |
| `#5CE1FF` | Net Cyan | Glass rules, net links, defend slices |
| `#D4FF00` | Acid | Pointer, focus, claimed turf, prices |
| `#FF4433` / `#3D6BFF` | Harm / Siren Blue | Damage, Heat, police rims, drones. Only at Heat 50+ |
| `#8C7BFF` / `#FF8C1A` | Corp hues | Enemy hardware, threat routes |
| `#FFC98A` | Sodium | Street-lamp pools, warm windows (sparingly) |

## Materials and layering (back to front)
1. **Sky glow plane:** a gradient emitter, so the skyline reads as a silhouette.
2. **City:** tinted-slate boxes, per-window random lights, rooftop Grease Pencil (GP) linework, dim neon blades.
3. **Haze:** a bounded fog box plus patchy noise volumes.
4. **Wet ground:** puddle-noise roughness from 0.02 to 0.3, so reflections break into patches.
5. **Rain:** 2–8k GP streaks in 3D, thin and long. The drops near a sign take its colour.
6. **Wheel hardware or map:** real meshes and lights.
7. **Glass UI:** dark navy, glossy, so spill shows as a sheen. It has a 1 px GP edge and rain beads running down it.
8. **Paper stickers:** they receive light but never emit it.
9. **Marker ink:** GP, unlit, the top layer. It ignores light and fog because it's on the screen glass.

## Lighting and spill (feedback 10, the lead)
- Every emitter has a real light partner:
  - each spinner has a coloured point light in front and a lower one that tints the forecast panels, HP text, cards and the wet floor;
  - the Modem sign has five pink lights and one cyan light that paint its plate, the rain in front of it and the street pool below;
  - the HQ hex sign pools pink onto the street;
  - hologram boards light their rooftops.
- Rim light comes from a cool backlight: moonlit haze behind the skyline, plus a thin emissive rim catch on the bezels.
- Marker and stickers never emit (per feedback 10). The paper takes the spinner's tint like real paper would.
- In Godot: a `PointLight2D`/`Light2D` per emitter with `range_item_cull_mask` on the UI and backdrop layers, and `CanvasTexture` normal maps on the glass and housings. Marker and sticker layers sit on a cull mask no light targets as an emitter.

## Motion
- **Marker write-on and drips (6):**
  - Strokes draw in font stroke order (the `stroke_font.py` glyph data is the stroke order) over 0.45 s, with the nib riding the last point.
  - Four drips swell at the letters' lowest points for 0.8 s, then **hold** while the game waits.
  - On press, the drips run the height of the screen as the page slides out *under* the glass.
- **Sticker slaps (8):**
  - Cards arrive over 3 frames at 112% scale with a soft, far shadow.
  - They land at 100% with a hard, tight shadow, a ±4° settle and a 2-frame hit-stop.
  - Speed lines and a spray of rain droplets fly off the wet glass on impact.
- **Binary shards (5):** 0/1 glyphs burst in a 150° cone away from the hit and arc down under gravity. White-hot at the core, cooling to pink, HARM red and amber. Short trails, like embers in rain. The dome gets a cracked-glass flash on a crit.
- **Heat glitch (11):** screen-space slice displacement, R/B band split, 1-in-3 scanline dimming, rare HARM tear lines and dropout blocks, plus a 25% desaturation grade at HUNTED. Intensity scales with the Heat band. Off in Options and under reduce effects.
- **Ambient:** rain streak scroll, window toggles every ~20 s, hologram band scroll with a 1-frame flicker every 4–7 s, and traffic trails.

## How the spinners get depth (4)
1. **Instrument well:** the wheel sits in a recessed dark console housing with a raised lip, and casts real shadow into it.
2. **Stacked planes at different depths:** bezel above the slices, a chrome ring between them, and the hub recessed below. The small parallax and occlusion between planes reads as 3D. In Godot: 4–5 sprites with per-layer offset and a subtle tilt.
3. **Glass dome:** a fresnel-edged glass cap with a painted window-pane reflection that stays fixed while the wheel spins under it. That fixed highlight is the strongest depth cue.
4. **Rim light and emissive inlays:** a cool rim catch on the upper-left bezel edge, plus an owner-coloured emissive inlay ring. Light defines the edge, not an outline.
5. **Slight tilt and perspective:** 13° back and ±7° toward each other, like two dials on one console. Pre-rendered per angle, or done with a normal-mapped sprite.

## Feedback items 2–11
| # | Answer |
|---|---|
| 2 | The vertical MODEM / CYBER SHOP sign is redrawn as real bent neon tubes with circuit traces, raining in front of the shop. The BUY/SHRED paper stickers are gone; buying uses the acid glass buttons. |
| 3 | The combat city is a DOF-blurred silhouette against horizon glow: no saturated colour, dim windows only. The two wheels are the only hot objects. |
| 4 | See the five techniques above. |
| 5 | 0/1 shards with trails burst from the enemy rim at the hit point. |
| 6 | See still 05 and the motion section. |
| 7.1 | Night version. The HQ is a stepped tower with cyan light strips, framed with room above its mast. |
| 7.2 | 10 fog patches, each blurred by its own amount, on top of a thin haze layer. |
| 7.3 | The depth pass drives a tilt-shift that gets blurrier into the distance. |
| 7.4 | All nodes, links, chevrons and a faint grid sit on **one** net plane above the rooftops. There are no street-to-roof lines; the HQ pierces the plane. |
| 7.5 | Three highway levels (z 9 / 16 / 23) on pillars, two-lane long-exposure traffic, street traffic and flyers with trails. |
| 7.6 | Seven projected hologram boards on rooftops: projector, beam, illegible glyph rows and a bright frame. |
| 7.7 | At HUNTED: three helicopters with searchlight cones and ground pools, three red/blue drone swarms converging on the HQ, red/blue tower rims and heavier haze. |
| 8 | Hand cards are die-cut stickers with tape and a hard shadow. The centre card is caught mid-slap. |
| 9 | Pink marker SEND IT is scrawled over a dim, washed-out mono EXECUTE. It carries through as LEAVE THE MODEM over the shop. |
| 10 | See the lighting section. |
| 11 | See the motion section. Still 03 shows the glitch at HUNTED. |

## Building it in Godot 4.7
- **Pre-rendered from this Blender rig:**
  - the city backdrops, rendered per district and Heat band as colour + depth + emission-mask layers;
  - the spinner layer stack (housing, bezel, chrome, dome highlight) as separate sprites;
  - the neon sign as colour + glow sprites.
- **Real time:**
  - `Light2D` spill with normal-mapped glass and housings;
  - a rain particle layer (GPUParticles2D, streak texture) in two depths;
  - a tilt-shift shader that reads the depth layer;
  - the Heat glitch as a full-screen `CanvasItem` shader on a top `BackBufferCopy`;
  - bloom and streaks via `WorldEnvironment` glow (HDR 2D on);
  - marker strokes as `Line2D`s animated along `stroke_font` glyph data, with drips as `Line2D` + tween;
  - shards as pooled `Label`/MSDF glyph particles.
- **Budget:** 2 rain layers + about 12 lights per screen is safe. Heat searchlights are additive cone sprites plus a moving light.

## Risks
- **Too dark:** body text must still reach 4.5:1 through the grade. The vignette and grain must switch off for reduce effects and small screens.
- **Rain fatigue:** rain over UI must stay sparse and never cross numbers. Heavy rain belongs behind the scrim.
- **Light spill can muddy semantic colour:** pink spill on a cyan slice. Spill on UI is capped at about 15% and never touches slice faces.
- **Pre-rendered city vs. reactive city:** Heat and turf changes need layered emission masks, not re-renders.
- **Spinner cost:** the pre-rendered layered wheel multiplies asset work per class and corp ornament.
