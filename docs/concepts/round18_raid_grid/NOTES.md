# Round 18: raid grid on the street plane

Designer feedback ART_FEEDBACK_R2 item 7, mainly 7.4: the raid nodes were drawn as rooftop pins with
lines from the street up to them. Here **nodes and links are on the same plane: the road surface.**
Nodes are pads at intersections, links are markings along the streets, and threat routes are lanes
on the same asphalt. Defences stand on the pads at street level. Nothing on the grid sits on a roof.

## Files
| File | What |
|---|---|
| `raid_options.png` | Three ways to build nodes and links on the road, same district, night. **C is the pick.** |
| `raid_setup_night.png` / `raid_setup_day.png` | Setup phase with approach C |
| `raid_wave_night.png` | A wave in progress at Heat 52 |
| `raid_heat_levels.png` | The same district at Heat 25 / 50 / 75 |
| `contact_sheet.jpg` | All of the above |
| `scripts/` | `layout.py` (district, camera, network), `district.py` (Blender scene), `netdecal.py` (the ground decals), `finish.py` (post), `screens.py` (UI overlay + sheets), `run_blender.py` |

Rebuild: `python scripts/run_blender.py` (4 Blender 5.2 headless renders, about 15 s each), then
`python scripts/screens.py`. Everything is seeded.

## The three approaches (raid_options.png)
- **A: Painted light.** Glowing road paint: a double lane line with flow chevrons, and roundel pads with
  a stencil glyph. It's the cheapest, but it reads as traffic paint and the chevrons compete with the real lane marks.
- **B: Holo floor tiles.** Tiles projected onto the asphalt, hex-tile pads, and a glyph built out of tiles. It looks the most
  "cyber", but tiles, fog and rain together get busy, and the bloom turns the status colours white.
- **C: Circuit inlay (recommended).** A 3-trace bus is cut into each linked street, with vias in dark grooves. Each node pad
  is a **chip socket** at the intersection: a dark plate, a glowing frame, pins on four sides, a pin-1 notch and the
  node glyph (round 17 set). Why C wins:
  - the defences visibly plug into the socket, so "an asset placed on a node" reads well;
  - the plate darkens the asphalt, so the status colour (green holds / amber disabled / red seized /
    pink CORE) stays saturated under bloom;
  - it is the art_asset C1 "net reading", the city as circuit traces, without a floating lattice.

## What each frame shows
- **Setup.** Node outcome = socket colour plus a vinyl label beside the pad (HOLDS / DISABLED / SEIZED,
  CORE HOME −8). Threat routes are red trace lanes on the street (offset beside our own links where
  they share a street), with the red grease pencil tracing them from the circled spawn points A/B/C.
  The yellow pencil marks a plan: the FLAK ARRAY card lifted from the tray onto the proxy. Also shown: the YOUR NODES,
  THREAT INTEL and RAID INCOMING cards (forecast stamp), the loadout tray (armory 5/6) and START DEFENSE.
- **Wave.** Threat vehicles (Halcyon violet with a neon rim and a red/blue light bar) sit on the routes, each on a
  hostile ring on the street. Shown: tracers from the turret, railgun, flak and sentry; integrity bars over every pad;
  damage numbers; a live feed; the 1x/2x/4x/SKIP strip; the Heat badge. Heat appears as choppers with
  searchlight cones, drones and corner strobes. During the playout the pencil only marks where each threat is heading.
- **Heat 25/50/75.** Everything is added above the street; the grid itself never changes. Band 1: one
  chopper and a few drones. Band 2: three choppers sweeping nodes, a drone swarm, corner strobes, holo ads switched to
  Halcyon, and a violet creep from the entries. Band 3: a gunship over CORE, every node in a spotlight, 26 drones, sky beams,
  and the creep flooding the streets.
- City (all frames): elevated two-deck highway plus a single-deck spur with traffic, flying-car lanes,
  hologram billboards on roofs and facade banners, patchy fog, tilt-shift, and rain at night (7.1-7.6).

## How to build it in Godot
1. **Ground plane decal layer.** One shader on the street mesh (or a `Decal`/full-screen ground pass
   that reads world XZ). It gets the network as uniforms or a small data texture: link segments
   (axis-aligned street runs, a flow direction toward CORE), pads (position, radius, status colour,
   glyph index into an atlas), route lanes (segment + offset), and threat ring positions. Per fragment
   it computes distance along and across each segment, then the trace / via / socket masks.
   `netdecal.py` is a line-for-line prototype of that shader (numpy over a world-position pass).
   The decal writes emission (for bloom and light spill) and a multiply term (grooves, socket plate).
   It must clip to the road surface: lots and sidewalks sit 0.35 m up and are excluded.
2. **Node pads as sprites.** The socket can also be a ground-aligned `Sprite3D` or quad per node (atlas: frame,
   pins, glyph, status tint), with the links left in the shader. Defences are 3D props or billboards
   anchored at the pad centre, at street level.
3. **Routes as Line2D with a dash shader.** The grease pencil route is screen-space: project the lane
   polyline (world, trimmed at the pads) to the canvas, jitter it, and draw a `Line2D` with a waxy
   texture and an animated dash offset ("route dashes crawl home"). The street lane underneath is the decal.
4. **Fog patches.** Noise-masked quads or sprites at street height (0–14 m), each with its own blur
   (pre-blurred textures in 4–6 softness steps, or a mip bias), depth-tested so nearer buildings hide them
   and tinted by the blurred glow buffer. They thin out near pads so nodes stay readable (7.2).
5. **Tilt-shift.** A depth-blur post pass: blur grows with |depth − focus depth| outside a sharp band
   on the network (5 blur levels blended per pixel here; in Godot, a DOF post shader on an orthographic
   camera, driven by depth rather than screen y) (7.3).
6. **Heat props.** Choppers, drones, strobes and cones are scene props switched on per Heat band. The
   searchlight pool on the ground is the same decal pass (world-space falloff around a target point).

## Choices / open points
- Toy scale: defences ×1.6, threats ×1.6, choppers ×1.9, so units read at map zoom (pad ≈ 110 px).
- Our links use net cyan with green / amber / red / pink sockets. STYLE_GUIDE says `cell_turf` #D4FF00
  for Cell links; the brief's MODEM palette was used here. The designer should pick one.
- The raid is Halcyon (corp violet #8C7BFF); threats are violet with HARM red lights, and routes are red.
- Weakest: the **day** frame. The patchy fog turns into grey smudges and the toon city goes pastel, so
  night carries this concept. The threat vehicles still need the stickers and pencil to read at
  this zoom, and choppers sit mostly above the crop in the heat strip.
- The overlay kit (stickers, grease pencil) is imported in place from `round3_overlay/combined_v2/scripts`;
  the glyphs come from `round17_slice_system/glyphs`.
