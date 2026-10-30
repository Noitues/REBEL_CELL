# Netrun zoom rules: every city element, by zoom band, down to street level

Status: SPEC (art-pass, 2026-10-30). No code, no renders. For the implementation agent working in the art clone of `D:/rc_art/godot_look_tide` (branch `art/netrun-zoom`).
Authority: designer ruling 2026-10-30 (DIRECTION_REVIEW, "Godot zoom prototype review"): the netrun ends at street level, framed like `golden_plates/street_overview.png`; new logic-based procedural rules phase in detail as the camera nears; camera rules clear the view; every netrun sub-element is a real city object; every city element has zoom phases.
Scope: view only. No game rules, no new node types (GDD 4.2 lists Router, Elite Router, Terminal, Mainframe, Server Rack). Nothing here changes the City band: at ppb < 6.4 the output must stay pixel-identical to r43 (test it).

Units: 1 BU = 2 m. 1 lot = 6 BU = 12 m. `ppb` = screen pixels per BU at a 1080 px tall viewport (scale by `viewport_h / 1080` otherwise). px per metre = ppb / 2.
Existing code this builds on: `CityZoomPlan` / `CityZoomLayers` / `city_zoom_layer.gdshader` (fade by ppb, per-building hash, neon share 0.34), `CityMeshKit.hash01`, `CityLampPlan`, `CityNeonKit`, `CityRoofProps`, `CityParkKit`, `CityA2Features`, `CityWater`, `CityHeatRig`, `CityIsoCamera`, `CityConfig` (`zl_*`, `r6_*`, `park_tree_*`). New numbers go in `CityConfig` as `zr_*` (no magic numbers).

---

## 0. What the plates actually contain (the target, itemised)

`street_overview.png` (the target for the final camera), 1920x1080:
- Framing: frontal, parallel verticals, no visible convergence (long lens). The base of the facades sits at y ~860 of 1080 (80% down). The horizon is about y 800-820 (eye ~4 m up, the frontage ~80-100 m away). The lower 20% is wet street. The top 25% is sky.
- Scale: a ground-floor storefront band is ~45-60 px tall (~4 m), so ~13-15 px/m = **ppb 26-30 at the frontage**. A near mid-rise block is ~500 px (33 m); the tallest tower ~800 px (55 m). Frame width at the frontage ~ 130 m (~11 lots).
- Value structure: ~65% of the frame is near-black plum. The brightest horizontal is the storefront band + its reflection. Neon is ~8-10% of the frame area. Small windows are dark slots with 8-12% lit.
- Facade detail, per building, all flat colour with hard steps:
  - mid-grey/violet wall tone bands that step by height (storefront zone lightest, upper floors darkest);
  - horizontal floor lines and a few long window ribbons;
  - many small rectangles (lit windows in warm amber, teal, white; pale AC boxes; louvre bands) scattered irregularly, 6-30 px;
  - one vertical neon strip on a corner or edge of ~1 tower in 3 (cyan, pink, yellow, orange);
  - parapet neon lines on mid-rises; crown rings and a mast on spires.
- Sign hierarchy (5 tiers, none dominant except one hero): (1) one hero curved billboard high on a tall tower ("THE SKY IS LEASED", ~7% of frame width); (2) roof signs on 2-3 roofs (KARAOKE, BAR); (3) tall vertical blade signs on mid walls (PHARMA, TEA, VOLTA, ~3% of width x 12% of height); (4) horizontal wall panels at floors 3-8 (small, 4-6% of width); (5) one fascia sign per ground bay (SOLACE, BAR, ARCADE, TEA, ORBITAL, DATA ...), 4% of width each, lit text on dark board with a neon frame.
- Street clutter: many thin lamp poles with warm heads along the pavement (~40 visible, mostly small), glow pools, hanging-lantern dots at the storefront line, a low violet ground mist at the facade foot that separates depth layers.
- Road: wet asphalt with dark rectangular utility plates (~3 m x 1.2 m), long soft vertical reflections of every sign and window, bokeh discs, 8-10 horizontal car-light streaks (orange, red, yellow, white, lilac, 10-40% of frame width, 2-4 px thick) just below the base line.
- Sky and depth: dark plum sky, slightly lighter near the skyline; two searchlight beams (cyan, pink) from tower tops at 10-20 degrees off vertical; distant towers are lighter, bluer silhouettes with few lights (3-4 depth layers separated by haze); faint rain streaks.

`hq_rebel_cell_overview.png` (the target for the **district / near-street** zoom, and for density per metre):
- Windows are dense lit grids (3 m pitch) at ~35-45% lit on mid-rises; the far field is a carpet of dots with a few tall neon-ringed towers (crowns: stepped rectangular neon rings + a long vertical edge line).
- Roof dressing on nearly every mid-rise: wooden water tanks on legs (~1 in 4), rooftop sheds with lit doors, stairs and rails, antennas, dishes, AC boxes, roof billboards, a cat and a fish neon (decorative roof props), fire escapes on side walls (zig-zag), vertical ladders.
- Vertical blade signs at every 8-12 m of frontage (pink, cyan, yellow, red, with kana), a continuous multi-colour storefront band, overhead wires on poles every ~12 m, glowing awning cubes, stepped entrance canopies with big lit boxes.
- Wet street + elevated rail deck + service lane: lit station kiosks, lamp pairs on posts, round vents.

The gap list from the prototype (blank prisms, flat asphalt, toy lamps and trees, no sky, one dominant billboard, thick ink, near-plane cut) is the to-do for this document.

---

## 1. Zoom bands

### 1.1 Definition

Bands are defined by `ppb`, the screen scale. The same maths works in ortho and perspective:
- ortho: `ppb = 1080 / ortho_height_BU` (= `1920 / ortho_width`).
- perspective, at a point at view depth `d` BU: `ppb = 540 / (d * tan(fov_v / 2))`.
Two readings are used and must not be confused:
- **focus ppb** (CPU): ppb at the camera focus (the netrun node facade, or the ortho centre). It decides what geometry gets built and prefetched.
- **fragment ppb** (shader): ppb at the fragment's own depth. It drives every cross-fade. Near things get more detail than far things automatically (a natural LOD); the skyline stays in City-band look at street level.

| Band | Focus ppb (centre) | Cross-fade zone (centre -20% / +20%) | Ortho width / typical camera | Intent |
|---|---|---|---|---|
| **City** | < 8 | enters District over 6.4 - 9.6 | >= 200 BU wide (r43 plan is 394 = 4.9 ppb) | plan read: massing, rims, windows as dots; identical to r43 |
| **District** | 8 - 16 | to Near-street over 12.8 - 19.2 | 200 - 120 BU wide; iso ortho x2-x3 (stage 3 = 14.6) | block read: lit grid, floor lines, strip, roof clutter, trees get trunks |
| **Near-street** | 16 - 28 | to Street over 22.4 - 33.6 | iso ortho 120 - 68 BU, or the perspective dolly (fov 12 -> 40) | street read: shop bays, blade signs, props, wet ground, real-scale lamps |
| **Street** | 28 - 56 | to Close over 44.8 - 67.2 | perspective, hero facade at 36 - 40 (final netrun camera) | the plate: full facade grammar, sign hierarchy, reflections, sky |
| **Close** | >= 56 | none | perspective < 25 m from the subject; only if the camera dips in | sub-0.2 m detail on the node object and the first frontage row only |

Cross-fade width = **+-20% of the centre (a ratio of 1.5 across the zone)**. Per-class fade tables in `CityConfig` use these zones as the default and may shift a class by up to one zone width (the prototype's `zl_fade_*` become `zr_fade_*` on the same maths: `smoothstep(in.x, in.y, ppb) * (1 - smoothstep(out.x, out.y, ppb))`).

The final netrun camera sits at hero-facade ppb 36 - 40: fully inside Street (full from 33.6), never in a fade zone, so the shipped view has no half-faded classes. Close exists only so a close dip does not run out of detail.

### 1.2 Why the thresholds sit where they do (real-world scale, 1 px/BU = 0.5 px/m)

| Centre | px/m | Window pane 1.5 m | Floor 3.6 m | Person 1.7 m | Sign letter 0.5 m | Lamp head 0.5 m / pole 7 m | Storefront bay 4 m | Reading rule that sets it |
|---|---|---|---|---|---|---|---|---|
| 8 | 4 | 6 px (a dot) | 14 px | 7 px blob | 2 px | 2 px / 28 px | 16 px | A floor period >= 12 px makes floor lines readable; 3 m window cells (12 px) become a grid. Below 8 a window is a dot and the r43 lattice (6 m pitch) is right. |
| 16 | 8 | 12 px (frame + mullion readable at >= 10 px) | 29 px | 14 px (figure) | 4 px | 4 px / 56 px | 32 px | A bay reads as a shop (lit window + sign) at >= 30 px wide; a person-sized lamp/pole reads as a pole; a tree trunk (0.4 m) is 3 px. |
| 28 | 14 | 21 px | 50 px | 24 px | 7 px (the minimum legible text) | 7 px / 98 px | 56 px | Letters need >= 7 px to read as text; below that signs use glyph bars. Kerbs (0.15 m) are 2 px = the ink width. |
| 56 | 28 | 42 px | 100 px | 48 px | 14 px | 14 px / 196 px | 112 px | Paving slabs (0.6 m, 17 px), panel seams (0.1 m, 3 px), bolts and cable ties become visible. |

Plate calibration: the plate's storefront band (4 m = ~55 px) gives 14 px/m = ppb 28 at the frontage, so the Street band starts exactly where the plate's detail density begins. The final camera is set a little closer (ppb 36-40) so the sign text reaches 9-10 px and the plate's detail per frame is matched when the frame is cropped to ~107 m (9 lots).

Minimum-pixel rule (applies to every view-only prop and line, it is what removes the "toy" look): `size_BU = max(real_size_BU, min_px / ppb_fragment)`. So a lamp head is `max(0.25, 3 / ppb)` BU: at City ppb 5 it is 0.6 BU (~r43's plan-readable lamp), at ppb 28 it is the real 0.25 BU. Scale converges to real size by itself, with no pop. Min px: lamp head 3, pole 1.5, wire 1.2, trunk 2.5, route ribbon 3, node disc 10, ink 1.2.

### 1.3 Transition method (the rule: no visible pop)

Four mechanisms, chosen per element type:
1. **Parametric (shader).** Windows, panels, floor lines, wall tone, grime, road texture, wetness: one continuous parameter driven by fragment ppb through smoothstep. The same cells exist at every band; only their contrast, subdivision and share change. This is the default and covers the biggest area of the frame.
2. **Additive dither-fade (geometry that was not there).** Signs, bays, balconies, pipes, props, lamps' heads: the instance exists from the build threshold; opaque parts use an alpha-hash / 4x4 Bayer screen-door dither keyed to the fade value (static pattern, so no shimmer), emissive parts ramp their intensity with the fade. Zone = the +-20% zone above. Ink on a new part fades by width (0 -> full) over the same zone.
3. **Replace-in-kind (the object gets a better model).** Trees, lamps, building roof props, landmarks: the better tier is built so its silhouette sits inside the lower tier's (containment +-10%). Cross-fade in two overlapped steps: the new tier fades IN first (over the centre -20% to +10%), then the old tier fades OUT (centre 0% to +20%). There is never a frame with neither. The lower tier is dropped once its fade is 0 and it has been invisible for 1 s.
4. **Subdivide (windows only).** City cell 3.0 x 3.6 BU splits 2x2 into 1.5 x 1.8 BU cells (the real 3 m x 3.6 m module) across the District -> Near-street zone. Child lit state: a lit parent keeps >= 1 lit child (hash picks which); an unlit parent lights a child with a small chance (so the lit share rises smoothly from 0.30 to the street share). A window "stays where it was".

**Hysteresis on the way back out.** Fragment fades have no state, so zooming out retraces exactly. For CPU decisions (what to build, which tier of mesh, which occluders are dissolved) use the focus ppb with: build when focus ppb > 0.8 x centre-of-next-band's fade start; free when it falls below 0.6 x that value for >= 2 s. A mesh-tier swap may not flip twice within 0.5 s. Occluder state (section 5.2) uses hysteresis of -12% on the way out and a minimum dwell of 0.5 s.

**Prefetch.** The camera path is known (section 5.4). While the camera is in band N, the chunk build for band N+1 runs on worker threads for the lots in the corridor, <= 1.5 ms main-thread per frame. Pop is impossible because the fade value is 0 until the build has finished (a build not ready delays the fade, never the camera).

**Identity.** Every choice is a hash of the element's own id (`CityMeshKit.hash01(id, SALT, index)`), never an RNG stream and never the camera or the band. The band only decides what is visible. Salts: 9700-9799 are the prototype's (`zl_*`); this spec reserves 9800-9899: 9810 window cell, 9811 panel kind, 9812 floor module, 9813 balcony, 9814 AC unit, 9815 pipe, 9816 fire escape, 9817 setback, 9818 mechanical band, 9820 bay, 9821 awning, 9822 shutter, 9830 sign tier, 9831 sign text, 9832 sign hue, 9840 roof clutter, 9850 tall-tower grammar, 9860 lamp, 9861 street prop, 9862 wire, 9870 tree, 9880 node anchor. Element ids: building = prism key; tree = hash(lot, clump, tree); lamp = hash(lot, side, index); street prop = hash(street lot, side, slot); road = street lot; node anchor = FNV-1a of the node id string (view-side hash only, no game state touched).

---

## 2. Per-element phase tables

Conventions in the tables: **B0** City, **B1** District, **B2** Near-street, **B3** Street, **B4** Close. "Build" = geometry exists. Budgets are per frame at the final street camera unless stated. Emission is relative to a lit r43 window = 1.0.

### 2.1 Buildings

Real data from the model: prism footprint (square / hex / octagon families, Cv2 facets), height classes 8 / 20 / 45 / 1000 BU (16 / 40 / 90 m), taper tiers, corp colour (`CityCorpColor`), which walls face a street (`street_walls`), terrain height. Real-world module used for street scale: floor 3.6 m (1.8 BU), ground floor 4.8 m (2.4 BU), window module 3.0 m wide x 3.6 m high (1.5 x 1.8 BU), window 1.8 x 1.5 m.

#### 2.1.1 Massing, facets, ink, rims

| Band | What | How generated | Budget |
|---|---|---|---|
| B0 | r43 unchanged: facet prism, per-triangle tone jitter, corp parapet rim, corner rims, crown LED band (tall), roof mast (`r6_mast_share` 0.4, 3-9 BU), tier setbacks, aviation light | existing | existing |
| B1 | Facet jitter amplitude x0.4 (the triangle mosaic was the prototype's top complaint); tone follows height bands instead (storefront zone 1.0, then 0.78, 0.56, 0.40, 0.30, 0.24, hard steps); side faces +-0.28, roofs +0.35. Walls >= 24 BU wide get vertical pilasters every 6 BU (darker 12% strips) | shader, `tone = band(h) * mix(jitter, 1, k)` | 0 geometry |
| B2 | Facet jitter x0.15; wall seams on the floor grid; setback ledges 0.4 BU deep get their own rim; corner rim thickens to real scale (0.25 m: max(0.125 BU, 1.5 px)) | shader + 0.4 BU ledge quads at tier steps | <= 6 ledge quads / tower |
| B3 | Jitter 0.05 (almost flat, plate-like); painted wall noise: two-octave grime, vertical rain streaks below ledges and signs (value -6%); mechanical bands and parapet caps (2.1.5) | shader | 0 |
| B4 | Panel seams at 0.1 m, rivets, wall stains, cable runs (per module, see 2.1.3) | shader + instanced modules | first row only |

Ink: replaces the ortho formula everywhere. `ink_px` at 1080p: B0/B1 2.0 (matches r43 at stage 1; measure it), B2 1.6, B3 1.4, B4 1.2; world width = `ink_px / ppb_fragment` (vertex-shader depth), wobble +-35% kept, minimum 1.0 px; when `ppb_fragment < 3` (far skyline) ink alpha fades to 0 and the silhouette is carried by value. This fixes "thick wobbly ink" (the prototype's 3.9x blow-up). Ink outlines the building and the big modules (balcony slabs, tanks), not the small ones.

#### 2.1.2 Windows (all by shader, same cells in every band)

| Band | Cell pitch | Window | Panes / frame | Lit share (by height) | Colour |
|---|---|---|---|---|---|
| B0 | 3.0 x 3.6 BU | 1.1 x 0.95 BU, one quad | none | r43: 0.30 | r43 palette |
| B1 (8-16) | 3.0 x 3.6 -> subdividing 2x2 over 12.8 - 19.2 | 55% of cell | frame line (1 px) from 12 | 0.30 -> 0.36 | + corp tint share 0.24 |
| B2 (16-28) | 1.5 x 1.8 BU (3 x 3.6 m) | 0.9 x 0.75 BU (1.8 x 1.5 m) | frame + centre mullion from 20; transom from 24 | see table below | warm 60%, corp tint 24%, cyan-white 10%, pink 6% |
| B3 (28-56) | 1.5 x 1.8 BU | same, aspect jittered +-15% per cell | frame, mullion, transom, sill line; glass sheen on unlit; blinds (half-lit) on 12% of lit | table below | same + per-pane independent light |
| B4 | same | same | adds 0.05 m reveal shadow, curtain silhouette, a person silhouette in ~1 in 60 lit cells | same | same |

Lit share by floor at street scale (night factor 1.0; `night_k` scales all):
- ground floor: 0.60 (shop glass; actually the storefront band, see 2.1.4)
- floors 2-5: 0.38
- floors 6-15: 0.24
- above floor 15 and tall towers: 0.12, plus 1 in 8 floors lit as a whole ribbon (office floor): the plate's long window ribbons.
Share is the mean, with per-building bias `+-0.10` from `hash(key, 9810)`, and per-column clustering (cells in a column lit together with p 0.3, so lit windows form short vertical runs as in the plates).

Panel kinds per cell (hash 9811), street scale: 56% dark glass, 15% warm lit, 6% teal lit, 4% white lit, 5% pale AC box (a small light rectangle with a vent line), 4% louvre (3 dark slits), 4% blinds, 6% empty (wall). At B1 only "lit / dark" shows, so identity holds.
Light contribution: window emission 1.0 (r43 `win_emit` 3.4); teal and white lit 0.8; the sum of window light stays under 3% of frame luminance (they are small and dark-dominant: the plates read dark).

#### 2.1.3 Facade modules (geometry, instanced; B2 from 16, full at B3)

Placed on street-facing walls (and the visible side wall of the corner), by floor module, seeded by `hash(key, 9812 + kind, floor)`. Rules from real buildings: modules sit on floor lines; they repeat with a bay rhythm (3 m); upper floors repeat less than lower floors.

| Module | Size | Rule | Band | Budget |
|---|---|---|---|---|
| Floor lines (shader, not geometry) | 0.15 m darker band + 0.05 light edge | every floor at B1+; every 2nd at B0.5 | B1 -> B3 | 0 |
| Balcony slab + rail | 3 m wide x 1.2 m deep x 0.2 m; rail 1 m, ink on slab | on 30% of residential-looking floors 3-12 (floors where windows are 3 m cells and the building is not a storefront-heavy block); same bay on the floor above gets no balcony; slab 0.2 m dark, underside lit by a small lamp on 1 in 5 | fade in 16-22 (B2), full B3 | <= 60 / frame |
| AC unit | 0.9 x 0.6 x 0.6 m grey box, vent grille line, 20% with a small red LED | per window cell: 5% of cells at floors 2-14; cluster under balconies | B2 | <= 150 / frame as a MultiMesh |
| Drain / pipe | 0.15 m diameter vertical run; ink only if >= 3 px | 1 per 12 m of wall, from ground to roof, with 2-3 brackets | B2 | <= 40 |
| Fire escape | zig-zag stairs + landing slabs every floor, 1.0 m wide; ladder at the bottom (the hq plate's red ladder) | on side / alley walls only (walls that face a street but are narrower than 14 BU, or the 2nd wall of a corner lot); 35% of eligible buildings 4-12 floors | B2 from 18, full B3 | <= 6 buildings, 40 slabs each |
| Setback | step 0.5-1.5 BU inward every 20-30 m of height on towers; ledge gets rim colour of the corp | `hash 9817`; already in tier setbacks for prisms; extend to every prism > 24 BU | B1 | via taper tiers |
| Vertical edge neon | 0.18 m tube, corp or palette colour, full height or 60% from the top | on neon buildings only (1 in 3), one corner | B1 from 8 (as 3 px), real 0.18 m (min 1.5 px) | 1 quad |
| Cable run / conduit | 0.06 m lines between modules | B4 only | B4 | first row |
| Wall posters, hanging lanterns, hanging laundry | small quads | storefront floors 1-3, 1 per 20 m | B3 | <= 30 |

#### 2.1.4 Storefront band (floors 1-2, 0 - 8.4 m)

Prototype bay system kept and scaled (bays 1.8-2.6 BU = 3.6-5.2 m; `zl_store_share` 0.8 of street walls; shutter share 0.16). Added:
| Band | Content |
|---|---|
| B1 (8-16) | lit ground strip (existing), one shop hue per wall; 1.2 BU pavement skirt strip; as a bright horizontal. |
| B2 (16-28) | bays: dark frame, lit window in a shop hue, 2 shelves with goods blocks (4-6 per shelf), two-tone slanted awning on 50% of bays, ribbed shutters on 16% (lit seams). Shop floor spill quad on the pavement (additive, 5 BU fade). |
| B3 (28-56) | per bay: door recess (2.1 m high) on 1 in 3 bays; window mullion; neon "OPEN" or menu board on 1 in 4; hanging lantern pair on 1 in 5 (warm dot + 0.3 m cord); fascia sign (tier 5) with text; bay width varies by `hash(9820)` 3.6-5.2 m, with a 0.3 m pilaster between bays. A storefront band is **always continuous along a frontage**: the walls that do not draw as a shop draw as a shutter, never as a blank wall (the plate's brightest horizontal must never have holes > 10% of its length). |
| B4 | awning seams and drip, goods with price tags, door handle, reflection of the street in the glass (a darker 20% gradient). |
Light: shop window 0.7 (spills 0.35 on the pavement); neon bays 1.6; the band mean luminance targets >= 2.5x the facade mean (squint test target). Budget: <= 80 bays / frame (the front row ~ 10 lots x 1.5 bays/lot x 2 sides + corners).

#### 2.1.5 Signage hierarchy (tiers, caps, corp weighting)

Neon rule: `is_neon(key)` hash < **0.34** (1 in 3 buildings carry glowing tube frames, lit blade, lit awning edge and the vertical edge strip). The other two thirds carry lit-box signs (emissive face at 0.35 of neon, **no tube frame**) or painted/dim signs. Per-building hue = `CityCorpColor.sign_color(cfg, key, u, palette)`: 55% corp colour or its complement, 45% the neon palette (cyan, magenta, green, orange, cream); within 90 m (45 BU) of a corp HQ the corp share is 70%+. Never more than 2 hues per building. No real brands; text from the invented set in `netrun_cel/NOTES.md` (SOLACE, LEAFLET, HELIX, CHLORO, BIO-TEA, PETAL, SPORE BAR, VIRIDIAN, GENEBAR, SOLACE RX; generic NOODLE, KARAOKE, PAWN, VOLTA, HOTEL, DATA, PHARMA, TEA, BAR, ARCADE, ORBITAL).

| Tier | Size (m) | Where | Share | Band in | Cap per frame |
|---|---|---|---|---|---|
| T1 hero billboard (curved or flat screen) | 12-16 x 5-7 | top third of a tower >= 60 m, street-facing | 1 in 8 tall towers | glyph blocks B1 (existing screens), animated B3 | **1 hero per frame; its screen area <= 6% of the frame** (the prototype's single dominant ad wall violated this) |
| T2 roof sign | 5-9 x 1.5-3, on posts 1.5 m | roofs with height >= 36 m | 0.5 (`zl_roof_share`) x neon dim | B1 (8-14) | <= 4 |
| T3 blade sign | 1.0-1.2 x 3-8 (vertical), 1 m out from the wall | floors 2-8, one per 8-12 m of frontage | 0.4 of walls | B2 (14-26 -> keep) | <= 14; no two adjacent blades the same hue |
| T4 wall panel | 3-6 x 1.2-2.4 | mid walls floors 3-12 | 1 in 6 walls | B2 | <= 10 |
| T5 fascia | bay width x 0.9 m | one per shop bay | 0.8 | B2 (glyph bars) -> B3 text | all bays |
| T6 small (open, menu, address) | 0.3-0.8 | storefront | 1 in 4 bays | B3 | <= 30 |
Total emissive sign area at street level 8-12% of the frame (the plate's). Text: SDF atlas (one draw per sign family), height >= 7 px or fall back to glyph bars. Kana: decorative strings only, no semantics; designer check item 5 in section 9.

#### 2.1.6 Roof clutter

| Band | What | Rule |
|---|---|---|
| B0 | mast, aviation light, existing roof billboard panels | existing |
| B1 | + water tank on legs (cylinder 3 m x 3.5 m, conical cap; 1 in 4 mid-rise roofs in the camera window), AC boxes, shed with lit door (1 in 6), roof sign | existing `CityRoofProps` rules (`roof_tank_share` 0.18, `roof_antenna_share` 0.45 above 22 BU, billboard share 0.16 above 14 BU) lifted to the plate's 1 in 4 tanks only in the street band of lots in the camera window; do not change the city-wide shares |
| B2 | + stair bulkhead, railings (1 px lines), satellite dish, vents, cables between boxes, small roof lamps (1 in 3 bulkheads, warm 0.8) | hash 9840 |
| B3 | + catwalks, water-tank ladders, hand rails, neon roof props (cat / fish / noodle bowl: 1 per 10 roofs, from a small kit, decorative only), roof garden pots | only roofs visible from the camera (top elevation angle < upper frame edge) |
| B4 | + wooden slats on tanks, rust streaks | first row |
Budget: <= 120 roof props / frame, shared meshes. Roofs above the frame top cost nothing (not built).

#### 2.1.7 Tall-tower rule (80 m prisms must not be blank)

At the plate's scale a 55 m tower fills the frame height; most of the wall above the 4th floor is the facade the player sees. Every building > 24 BU gets the **grammar of `hash(key, 9850)`**, a vertical stack of zones, all by shader + the modules above; the rules guarantee a feature every <= 8 m of height and horizontal rhythm every 3 m:
1. **Base (0-9 m)**: storefront band 2.1.4 + canopy line (awning or ledge rim) at 4.8 m.
2. **Podium (9-24 m)**: densest module zone: blade signs, balconies / fire escape, AC boxes, wall panels, pipes. Floor lines every floor.
3. **Shaft (24 m to top - 18 m)**: window grid with panel kinds (2.1.2), lit ribbons (1 in 8 floors), one vertical neon strip (neon buildings), a wall panel (T4) every ~20 m of height at 1 in 3 floors zones, a **mechanical band** every 22-30 m: one storey of dark louvres (3 slit pattern) with a thin horizontal tube (corp colour) on the lower edge. The wall tone steps by 8% at each mechanical band so a long wall is visibly segmented.
4. **Crown (top 18 m)**: setback ledge with rim, crown LED band (existing for tall) or stepped ring (rectangle ring on 1 in 5 tallest, as the hq plate), roof clutter, mast + red tip (1 per tower, existing), a T2 roof sign.
5. **Side and back walls** (not street-facing but visible): zones 3-4 only, windows + mechanical bands, no signs.
Result per 80 m tower in the frame: ~2 blade signs, 1 panel, 1 mechanical band per 25 m, floor lines, ~120 module instances: no 20 m x 20 m blank patch anywhere. Test: "no blank wall": a render of the facade with all lit modules removed must show floor lines or panel kinds in every 8 m x 8 m cell (assert on the plan, not the pixels).

### 2.2 Trees, bushes, lawn (parks, medians, apron tree lines)

Data: park lots (`K_PARK`), Solace park organic region with paths and ponds, apron tree lots, veg domes on land. Existing tree: a low dome, w 1.6 x h 2.1 BU (3.2 x 4.2 m), r 0.63-1.32 BU, 3-5 per clump.

| Band | Tree | Bush | Lawn | Light |
|---|---|---|---|---|
| B0 | the blocky dome (r43), dark green, 1 colour of `park_tree_colors` | none (part of the lawn tone) | lawn flat colour + noise | 0 |
| B1 (from 8) | 3 overlapping spheres (lumps of 0.55-0.7 of the dome radius, offsets 0.35 r) filling the dome silhouette (containment 90-110%) + a trunk (0.4 m, min 2.5 px, height 35% of the tree); lumps are faceted spheres (12 tris) with the dome's colour +-8% | 1-2 lump clusters on lawn edges (0.5-1 m) 1 in 4 clumps | lawn mow-stripe noise; path edge | 0 |
| B2 (from 16) | 6-9 lumps in 2 layers (a tilted 3-tier canopy), trunk with 2 branch stubs; tree height scaled to street-tree real size 6-9 m (the dome may grow up to 1.6x in height as the trunk grows; canopy footprint stays); a tree pit ring and a grate on street trees (kerb planting) | 3-5 lumps, a hedge line along medians (0.6 m) | grass tufts quads 1 in 6 m | pit uplight 0.3 (1 in 4 trees on avenues, cyan or warm) |
| B3 (from 28) | lump clusters wrapped with leaf cards (alpha-cut quads, 2-tone cel texture, 18-24 cards per lump; ink on the canopy hull only), visible trunk bark bands, branches 3-5, fairy lights (small warm dots, 1 in 3 street trees) | clipped hedge with block steps, planters with 1-2 plants at storefronts (1 in 4 bays) | tufts, flower dots (palette) 1 in 12 m^2, path edge stones | fairy 0.8; planter glow 0.2 |
| B4 | leaf-card density x1.5, individual branches, bark texture, birds? **no** | leaf detail | grass blades (instanced, 1 m radius around camera only) | - |
Seed: `hash(lot, clump, tree)` (stable; the lump layout is a function of it). Budget: B1 <= 1500 trees at 80 tris = 120k tris; B2 <= 400 trees x 300 tris; B3 <= 120 trees x 800 tris (+ leaf cards) in view; trees beyond 80 m at B3 stay at B1 (fragment ppb). Existing `park_tree_w/h` unchanged at B0 (the whole-city plate parity depends on them). Trees are not blocked by the lens rule: any tree within 12 m of the camera is removed (5.3).

### 2.3 Lamps (see also section 3)

| Band | Lamp |
|---|---|
| B0 | r43 lamp (cube base + pole + panel), position from `CityLampPlan` (kerb lamps along built streets, corner lamps, bridge lamps; brightness drift; outages) |
| B1 | the same positions, size via the min-pixel rule: base cube shrinks to a 0.6 m plinth, pole 7 m, head 0.5 m; glow dot (additive, 3 px) |
| B2 | pole + curved arm + luminaire (box 0.8 x 0.3 m) + warm cone pool decal on the ground (6 m diameter, 0.2), outage 1 in 12 lamps dark (existing `lamp outages`); double arm on avenues |
| B3 | base plate, tapered pole (ink only), arm, luminaire with glass underside, bokeh halo sprite (soft, 0.3 intensity), pool decal with wet-ground hotspot reflecting in the road; cable on 1 in 4 poles |
| B4 | bolts, banner bracket, small sign plate |
Seed: lamp lot + side + index. Budget: <= 60 lamps in view at B3, each ~120 tris, one MultiMesh.

### 2.4 Streets, roads and road surface (full spec)

Data: street lots (`K_STREET`, plazas), avenue strips (lane glow in the lane material), A2 road classes, network ground decal, `road_deck_offset_bu` 12 BU for decks.
Cross-section (view-side template by the street lot count; real widths, 1 lot = 12 m): 1-lot street = pavement 2.5 m + carriageway 7 m (two lanes 3.5) + pavement 2.5 m; avenue (2 lots) = pavement 3 + parking 2.5 + 2 lanes 7 + parking 2.5 + pavement... scale to 24 m; boulevard (3 lots, 36 m) = pavement 5 + parking 2.5 + lanes 7 + median 6 + lanes 7 + parking 2.5 + pavement 5. Kerb 0.15 m high x 0.2 m. Only the *visible* part of the cross-section matters; the road surface mesh stays the lot quad, and the cross-section is painted by the shader from the lot's local coordinates (so no geometry change).

| Band | Surface | Markings | Kerb and pavement | Wetness / reflection | Traffic |
|---|---|---|---|---|---|
| B0 | r43 flat street colour + lane glow strips + network decal | none | none | none | street cars as points |
| B1 | dark asphalt with 2-octave value noise (+-5%); avenue glow strips (existing) narrow to 0.4 m lane glow lines at the lane centres (fixes "flat neon slabs") | centre dashes as faint lines; crossings as 4 stripe blocks at intersections | kerb line as a lighter 1 px edge + pavement tone (+8%) | wet sheen: a faint value gradient, no mirror (wet amount 0.2) | existing |
| B2 (16-28) | + patched asphalt (rect repairs 1-3 m, +-6% value, 1 per 8 m of lane), tire-track darkening in the lanes (two 0.8 m strips, +-4%), utility plates (3 x 1.2 m, dark, 1 per 15 m along the lane edge: the plate's rectangles) | dashed centre (3 m dash / 9 m gap, 0.15 m wide), solid edge lines 0.12 m, double yellow on avenues, crossings (0.5 m stripes, 0.5 m gaps, 3 m long) at every intersection and mid-block on boulevards each ~2 lots, stop lines 0.4 m, arrows 1 per block | pavement slab grid (0.6 m slabs, lines at 1 px), kerb face quad 0.15 m (darker, ink line), kerb drains 0.5 x 0.3 m every 12 m | wetness map on; puddle mask; reflection (planar, 1/4 res) of emissive layer; light streaks of shop windows (existing 'wet' class) become real reflections | street car streaks (below) |
| B3 (28-56) | + asphalt aggregate speckle (0.05 m, only < 25 m from the camera), crack lines 1 per 30 m, manholes (0.8 m, 1 per 30 m, steam on 1 in 4 (3.4)), tactile strips at crossings (yellow, 0.4 m) | worn paint (alpha noise on markings 0.7-1.0), bike lane green strip on 1 avenue in 4, hatched islands | kerb with chamfer highlight (0.05 m), pavement joints and a darker gutter strip 0.3 m, tree pits | full: roughness 0.05 puddle / 0.35 wet / 0.85 dry; planar reflection with ripple warp (normal noise 0.1-0.3 m, 2 octaves) and vertical smear (stretch 1:3), bokeh reflections of lamps | cars, lights, streaks |
| B4 | micro-normal on asphalt, puddle edge rings, rain ripples (1 ring/s per m^2 within 15 m of the camera), litter quads | paint chips | kerb joints, gum stains | same | wheel spray (additive) only for cars < 15 m |
Wetness map: world-space `W(x,z)` = `0.55 * valuenoise(x,z; period 24 m) + 0.45 * valuenoise(period 6 m)` thresholded at 0.62 for puddles (about 25-30% coverage) plus gutters (the 0.6 m next to the kerb is +0.3). Same map in every band; the shader multiplies its effect by `smoothstep(14, 28, ppb)` so the city view stays dry-flat (identical to r43 below 12.8) and the wet look arrives with the camera.
Reflection method (primary): **planar mirror at 1/4 resolution, emissive-only.** A second Camera3D mirrored about the road plane renders only render-layer `REFLECT` (lit windows' emissive quads, sign faces, lamp heads, car lights, neon tubes, the sky gradient, and a flat-colour proxy of the facades at 20% value). Output texture sampled in the road shader with: `uv.y` stretched x3 (the vertical smear), warp = 0.15 * normal-noise * (puddle ? 1 : 2), gain = `0.9 * W_wet + 0.35` and a Fresnel term (frontal low angle: high). Cost ~0.9 ms (budget 7). Fallback ladder if over budget: 1/8 resolution -> only the lowest 12 m of the scene -> the prototype's additive streak quads (kept as the lowest tier). Screen-space reflection is not used (it does not reflect what is off-screen, and the frontal view reflects the signs just under the frame edge; planar is also stable under the cel post).
Car streaks: the road's street cars (existing `CityTraffic` data, seeded `city_traffic`) at B2+ become long-exposure streaks: length = `speed * 1.5 s` (about 12-30 m), 0.12 m thick, at 0.6 m (tail) and 0.8 m (head) above the road, additive, colours from the lane palette weighted orange 28%, red 22%, white 20%, yellow 15%, lilac 15%; <= 24 streaks in view, 3-4 on the focus carriageway, drifting at 1/20 of the real speed (they are streaks, not cars). A faint reflection comes for free from the reflection layer. At B4 within 15 m real cars (box + 2 head lights + 2 tail lights) may pass, never in the lens corridor (5.3).
Highways, decks, ramps, pylons, rail, corporate walls (`CityA2Features`): see 2.5.

### 2.5 Highways, decks, ramps, pylons, rail, walls, undercity entrances

| Band | Deck / highway | Ramp / interchange | Pylons | Rail | Corporate wall + checkpoint |
|---|---|---|---|---|---|
| B0 | r43: deck ribbon at `road_deck_offset` 12 BU, side faces, rail glow lines (`hwy_rail_*`) | existing Bezier decks | boxes `a2_pillar_bu` every `a2_pillar_every_bu` | glow lines at `a2_rail_lift` | wall prism, gates open, checkpoint box |
| B1 | + deck underside tone (darker), edge parapet 1 px, lane glow lines separated | + ramp rails | + pylon cap, 3 px base | + station kiosk boxes lit | + gate lights |
| B2 | + lane markings on the deck (dashed centre), crash barrier (0.9 m, repeated posts every 4 m), underside lamp row (warm 0.5, every 12 m) | + chevron signs (1 per ramp) | round pylon (octagon) with ink, cap beam | + sleepers, catenary posts (every 24 m), station canopy, platform edge strip | + wall panels with seams, floodlights every 24 m, gate boom |
| B3 | + road signs (green, 1.5 x 0.6 m) on 1 in 4 spans, drain scuppers, cables along the underside, reflections of deck glow on wet road below | + guard rails | + base plate, bolts, pigeon-netting (no) | + the hq-plate rail deck: lit station kiosks, yellow dashed edge, lamp posts | + cameras on poles, barrier striping |
| B4 | + rivets, stains | - | - | - | + guard silhouette (none: no characters) |
Streets run under decks (the plate has an elevated rail deck): under-deck streets get a darker value (-15%), a lamp row and a fog bump (+0.1). Seed: A2 road id + segment index; pylon positions are a function of arc length so they do not move between bands. Budget: <= 200 pylons / frame, instanced; decks are existing meshes.

### 2.6 River, bay, quay and apron, seabed, islands, port

Almost never in frame at the street camera; they matter for the skyline (section 4) and the in-between bands.
| Band | Water | Quay / apron / seawall / pier | Port, ships, islands |
|---|---|---|---|
| B0 | existing `city_water` (sea, void, ripple, caustic, reflect gain) | existing promenade + warehouse blocks + lamp points | r43 port, cranes, freighters, fort, lighthouse |
| B1 | ripple scale stays (9 BU); foam line at the shore (1.5 lots, existing) sharpens | promenade lamps real size; bollard dots every 12 m; seawall coping lit strip | cranes get cross-braces (lines), ships get deck lights (2 px) |
| B2 | + wave highlights; reflection of quay lights as vertical smear (existing `water_smear_w_bu` 3.5) at the real scale | + railings, mooring rings (small dark dots), steps | + container stacks as coloured boxes (existing), gantry lights |
| B3 | + the same wet-road reflection method (the quay is wet ground); pier lamp (0.7 BU -> real 0.3) | + benches, bins (3.2), warehouse doors with lamps, quay cranes' lit cabs | + ship name signs (decorative), crane warning lights (red blink 0.5 Hz) |
| B4 | + ripple rings | + planks | - |
These are a function of the shore field and the lot, seed = lot id; budget unchanged (they are farther than 150 m at the final camera; only the skyline silhouette of the cranes/lights shows). At street level, if the bay is in the background it contributes a flat water tone with 8-12 point lights (ships, cranes) at haze value.

### 2.7 Terrain and ground

| Band | Ground |
|---|---|
| B0 | r43 terrain colour by height (`CityTerrainColor`), hills, foothills, mountains (distance, snow caps) |
| B1 | terrain keeps; city ground under blocks gets a grid pattern fade-in (lot edges 0.2 m darker) |
| B2 | bare ground in courtyards: gravel noise; lawn lots get real mow stripes; soil edge at the lawn |
| B3 | + terrain far past the city is part of the skyline (4.4): mountains as a 1-colour silhouette at haze value, with a few far lights |
| B4 | + ground micro texture |
Hills under the city give the street a gentle slope: the camera rule keeps the focus facade row at one elevation (terrain smoothed within +-1 m inside the corridor so the street plane is flat for the reflection, section 5.1).

### 2.8 Landmarks: HQs, Site landmarks, helix, plaza, Solace pods, A2 HQs

Data: `CityLandmarks` (glTFs per corp HQ and Site), the Solace helix (compound), plaza rings and spokes, pods in the park, Circus Aurelius, Pier City. These are authored meshes with their own materials (lm_toon, lm_win, lm_neon).
| Band | Detail |
|---|---|
| B0-B1 | as r43 (glTF at LOD0 with window materials) |
| B2 | + signage on the landmark podium from the same sign tiers (T4/T5 for the landmark's corp), plaza ground rings 0.2 m inlay lines glow (existing), street lamps at the plaza edge (2.3) |
| B3 | + bays on the landmark's podium (2.1.4), planters, a lit entrance canopy, wet reflections of the helix strand light on the plaza (the planar layer includes lm_neon) |
| B4 | + helix strand panel seams, rung light fixtures, plaza pavers |
The netrun never stops on a landmark; they appear in the skyline and may host a Server Rack entrance (layer 7).

### 2.9 Traffic overhead, sky lanes, aviation, heat rig

| Band | Sky lanes / cars / helicopters / beacons |
|---|---|
| B0-B1 | existing sky lanes (guide dots + car LOD tiers), aviation lights on the tallest roofs, holo billboards (existing) |
| B2 | + sky cars become 3-light shapes with a streak tail; helicopters/drones with spotlight cones (Heat rig, only when Heat state asks; not ambient) |
| B3 | sky cars < 200 m: box + 3 lights, 8 per frame max, none in the lens cone (5.3); aviation red blinks (0.5 Hz) on the tallest 12 masts visible |
| B4 | n/a |
Ambient tower-beam searchlights are a separate, always-on element (section 4.3) and must not be confused with the Heat rig's searchlights (those follow the Heat state).

### 2.10 Fog, haze, post (ink, bloom, rain, grade)

| Band | Fog / haze | Post |
|---|---|---|
| B0 | r43 (`fog` 0.22, `haze_k` 0.34) | r43 |
| B1 | + a ground mist layer fades in (0.5 BU high, additive violet 0.08) | r43 |
| B2 | + mist 1 BU (2 m) high on the focus streets; distance fog uses the section 4.4 curve | ink in px; bloom radius scales with ppb (radius_px = 0.012 * viewport_h at street band) |
| B3 | full: depth haze with 3 depth cards, mist 6 m high, light shafts at lamps | rain streaks (existing) +20%, lens-free (no lens dirt) |
| B4 | as B3 | as B3 |

### 2.11 Other elements the city builds (anything not above)

| Element | Rule |
|---|---|
| Holo billboards (ambient) | existing roof panels; at B3 their screen content = animated scroll (existing shader), cap with the T1 hero rule |
| Hotspot giant screens (`CityNeonKit`) | at B1-B2 existing; at B3 count as T1/T4 signs; all hotspot screens obey the 6% cap |
| Crowns (LED bands) | B0 existing; B2+ real 0.25 m tube, a 3 px lit band |
| Aviation lights | B0 red dots; B3 + a 2 px halo sprite |
| Network ground decal (CityNetworkData) | B0-B1 as r43; B2+ fades out under the road surface (the road takes over) so the road reads as a road, not a diagram |
| Undercity entrances | B0 existing marks; B3 a stair-down door with a lit sign, hash by id |
| Drowned quarter water sheet | a water look (2.6), B3 only on the skyline |
| Whatever else `CityView3D` adds | default rule: **every instance family gets three tiers (plan blob, mid, real) with the min-pixel rule and the replace-in-kind transition; none stays at plan scale past ppb 16** |

---

## 3. Street clutter and small lights

All clutter is a function of the street lots, seeded by `hash(street_lot, side, slot)`, placed by frontage logic, never random scatter. The frontage side faces a building wall; the **kerb line** is 0.6 m inside the pavement edge; the **building line** is 0.4 m from the wall.

| Item | Real size | Placement (spacing, frontage, corners) | Band in | Light | Budget in view |
|---|---|---|---|---|---|
| Street lamp (replaces the toy lamp) | pole 7 m, head 0.8 x 0.3 m | `CityLampPlan` positions kept; on avenues alternate sides 12 m apart, on 1-lot streets one side 18 m, jitter +-1.5 m; corner: 1 per intersection corner (double arm); never within 4 m of a bay door, never on a crossing | B1 min-pixel, B2 real | head 2.0 (bloom), pool 0.2, 12 of the nearest lamps become real shadowless omni lights | <= 60 |
| Bollard | 0.15 m dia x 0.9 m | at crossings (2 per kerb ramp), 1 per 4 m in front of shop bays on 1 in 3 shop walls | B2 | top ring 0.3 (cyan or amber) | <= 80 |
| Vending machine | 0.9 x 0.8 x 1.8 m | on a blank or shutter wall, building line, 1 per 40 m of frontage; always lit, colour from a 6-hue vending palette | B2 | 1.2 (a bright rectangle that helps the storefront band) | <= 10 |
| Bin (trash) | 0.6 x 0.6 x 1.0 m | beside every lamp base on the pavement side at 1 per 24 m, and at alley mouths | B3 | 0 (dark) | <= 20 |
| Crate / box stack | 0.5 m cubes, 1-4 stacked | in alley mouths and beside shutters, 1 in 5 shutter bays | B3 | 0 | <= 20 |
| Steam vent | grate 1 m + plume | manholes: 1 in 4 of the road manholes (2.4); plume = 3 billboard strips 1.5 m wide, 4 m high, additive, slow drift | B3 | scattered 0.25 | <= 4 |
| Overhead wire | 0.02 m (min 1.2 px) | along the far pavement on poles every 24 m at 6.5 m height: 3 catenary spans (sag 3% of span) between poles, in front of the storefront band; none crossing the frame centre (5.3); lit insulator dots every span (0.3) | B2 | 0.3 dots | <= 3 spans visible per side |
| Hanging lantern / string lights | 0.3 m | across shop bays: cord + 3-5 lanterns, 1 in 5 bays | B3 | 1.0 warm | <= 20 |
| Telecom cabinet, hydrant, mailbox | 0.9 x 0.5 x 1.3 / 0.3 x 0.9 / 0.5 x 0.5 x 1.2 | pavement edge at block ends; the telecom cabinet is the **Router** anchor (6) | B2 | status LED 0.4 | <= 10 |
| Street sign (name plate) | 0.6 x 0.2 m on a pole | each corner | B3 | 0.4 (blue) | <= 6 |
| Pavement stall / awning stand | 2 x 2 m | on pavements >= 5 m wide only, 1 per 60 m | B3 | 0.8 | <= 4 |
| Bike rack, bench | 1 x 0.4 | pavements >= 4 m, 1 per 40 m | B3 | 0 | <= 12 |
Rules:
- **Frontage**: a prop stands on the building-line half of the pavement when it belongs to a building (vending, crates, stall), on the kerb half when it belongs to the street (lamp, bin, bollard, hydrant).
- **Spacing**: min 3 m between any two props except bollard pairs; lamps and bins are placed first, then others; ties broken by (slot hash, lot i, lot j).
- **Corners**: kerb ramps with 2 bollards, a lamp, a street sign, a crossing; no vending or crates within 3 m of a corner.
- **Small extra lights (not lamps)**: shop-window spill quads, bay LEDs, awning tubes, bollard rings, neon open signs, vending panels, lantern dots, car lights, kerb reflectors (0.04 m amber dots every 6 m along the lane line: 0.5), tower aviation reds. Total emissive small-light count in view <= 600 quads; real lights <= 12 (the 12 brightest lamps / node highlights nearest the camera, shadowless).
- **Light budget in luminance**: sum of non-window, non-sign small lights <= 6% of frame luminance (they are accents; the storefront band, signs and neon carry the brightness, as in the plate).
- **Bands**: nothing of 3 is built below B2 (focus ppb < 12.8); lamps (2.3) are the exception since they already exist.

---

## 4. Sky and skyline at street level

### 4.1 Sky gradient
The plate's sky is a calm dark plum with a slightly lighter, warmer band just above the skyline; no stars (the sky is lit by haze). Spec (sample the plate rows y=40, 400, 760 to retune; these are approximations):
- zenith `#1a0c28`, mid sky (30-60% of the way down to the horizon) `#2c1233`, horizon band `#58294f`, smooth 3-stop gradient on a sky dome (unlit, no ink), in screen space for the portion above the horizon and in direction space for yaw-stable behaviour; a 6% noise cloud modulation (very low contrast) and a vertical glow just above the skyline (height 15 m worth of haze, value +8%).
- Sky colour per corp district: +-6% hue shift by the nearest HQ (`CityCorpColor`), so the Solace street has a faint green-violet band and the city stays one world.
- The city view (B0-B1) keeps r43's dark sky; the sky dome fades in over the B2 zone (16-28) by camera pitch: sky is only visible when the camera pitch is below ~25 degrees, so the fade is driven by `pitch` and `ppb` jointly: `sky_k = smoothstep(16, 28, ppb) * smoothstep(40, 8, pitch_deg)`.
- Rain: faint streaks (existing) 1 px, 8% opacity.

### 4.2 Skyline silhouette (real far buildings)
- The skyline is the city itself: every prism beyond 120 m from the camera, drawn at B0-B1 look by fragment ppb (windows as dots, rims, masts, crowns). Three depth layers, each with its own haze value (section 4.4): near (60-180 m), mid (180-450 m), far (450-1000 m) so the plate's layered silhouettes are produced by real buildings at different distances, not by cards.
- The far layer (> 450 m): only massing + lit dots + red aviation + crown LEDs, wall tone = haze colour + 10% (lighter, bluer than near), ink off.
- Silhouette variety guarantee: the horizon line needs height variation; the camera rule (5.2) hides low foreground buildings only, never the tall far ones.
- Terrain beyond the city (hills, mountains) is a smooth silhouette at far value with 20-40 distant lights (cabin dots) so the skyline is not a flat edge.
- Real-tower beacons: the 4 tallest buildings in the frame (ties by key) get a crown ring (stepped rectangle, plate-like) and an aviation red; no extra buildings are invented.

### 4.3 Searchlights (ambient, view-only)
- 2 beams in frame at the final camera (cap 3), from the roofs of the 3 tallest visible towers (ties by key), colour cyan, pink, (white); beam = 2 crossed alpha quads, length 300 m fading along the length (alpha 0.5 -> 0), width 3 m at the base -> 20 m at the top, angle 8-20 degrees off vertical, a slow sway (period 60-90 s, amplitude +-6 degrees); the base has a 6 m glow disc.
- Separate from the Heat rig's searchlights (those are a game-state view); the ambient beams are always the same for a seed and carry no information.

### 4.4 Haze layers and the distance fog curve
- Distance fog (violet `#3b1f55` at street band; the existing `fog` is `Color(0.20,0.17,0.33)`): `f(d) = 1 - exp(-(d / D)^1.4)`, with D = 260 m for the street band (f = 6% at 50 m, 14% at 100 m, 36% at 200 m, 55% at 300 m, 85% at 600 m, clamp 0.9). At B0-B2 the existing r43 fog is kept; the curve blends in with `smoothstep(16, 28, ppb)`.
- Fog colour grades with height: horizon +8% value, above 30 m it lerps toward the sky colour (so tall towers dissolve into the sky: the plate's tower tops are darker than the lower, hazier midsections).
- Haze layers (3 depth cards): translucent camera-facing gradient cards at 60 m, 180 m, 450 m behind the focus row, additive violet 0.06-0.10, height 0 - 40 m with a soft top, each also lighting the backgrounds by +6% value, so adjacent layers always differ by >= 8% luminance (the squint test target).
- Ground mist: 0 - 6 m high, density 3x the fog, in the street corridor within 120 m of the camera; light shafts around lamps (1 in 3 lamps, cone sprite 0.15).
- Depth separation target: foreground facade row value ~ 0.18, next layer 0.26, third 0.34, far 0.42 (relative luminance), measured on a masked render.

---

## 5. Camera rules

### 5.1 Framing for the street-level netrun view (the street_overview composition)
- Projection: perspective; **vertical fov 40 degrees** (default; allowed range 34-45; the plate's frontal, parallel verticals need a long lens), aspect 16:9 (horizontal fov ~65 degrees).
- Position: on the street plane (terrain smoothed inside the corridor), **eye height 2 BU (4 m)**, horizontally centred on the layer window of the route (3.5 layers; the camera dollies along the street axis with the route, 5.5), facing the **far frontage** along the street normal; yaw error < 2 degrees (frontal). Distance to the far frontage is derived: `d = 540 / (tan(20 deg) * ppb_target)`; with `ppb_target` 36-40 at the frontage that is `d = 37-41 BU = 74-82 m`.
- Pitch 0 with a **vertical lens shift** (frustum offset) so the horizon is at 0.74 of the frame height from the top (y ~ 800 of 1080): verticals stay parallel and the frame shows ~ 42 m above eye at the frontage (the plate: 55 m of 60 px/4 m ground floors), 17 degrees below the horizon at the bottom edge (ground starts ~ 13 m from the camera). If a host building is taller than the visible height, the camera lowers the horizon to 0.68 (tops cropped; sky shows above the lower buildings and through gaps).
- Frame fill: frontage row occupies y 22%-80% of the frame, wet street 80-100%, sky 0-25% above lower frontage. Min sky share 12% of frame area (if less, raise the horizon 3 px at a time up to 0.80, or lower the eye).
- Left-right: the focus node is placed at the horizontal third (x 0.33 or 0.66) alternating by layer parity, never centre, never within 8% of an edge.
- ppb at the hero facade: 36-40 (Street band, fully faded in).
- This is the **final** camera of the netrun. The framing in the plate is one frontage; the horizon, fov and eye are the same for every street; only the focus lot changes.

### 5.2 Occluder handling (flatten, hide, dither, cut away)
Inputs: camera pose `C`, route window `W` (the street segment from layer k-1 to k+2 in arc length), node set `N` in `W` with anchor positions `A_i`, the street-facing wall data (`street_walls`).
Classes (computed once per camera pose; cached per route window):
1. **HOST**: the building that carries an anchor (6). Always shown, full detail.
2. **FAR FRONTAGE**: buildings on the far side of the route street within `W +- 1 lot`: shown, full detail; this is the plate's frontage row.
3. **NEAR SIDE**: buildings on the camera's side of the route street inside `W +- 1 lot`.
4. **OCCLUDER**: any non-HOST, non-FAR-FRONTAGE building whose footprint intersects the **sight corridor**: the convex ground polygon of {C, the base segment of the far frontage over `W` padded 1 lot}, inflated 6 m; or whose roof lies in the frustum below the skyline needed for sky (a roof with height > camera eye + `tan(angle_to_skyline)` x distance, where the building stands in front of the far frontage and covers > 8% of frame area).
5. **BACKDROP**: everything else (never altered; they form the skyline).
Treatment (decided by class, distance and size):
- **Hide**: OCCLUDER inside the corridor, or any building whose nearest point is < 24 m (12 BU) from C: dissolved by the dither (instance `occ` 0 -> 1) over the focus-ppb range 16 - 26 (it melts as the camera descends); ink and roof props fade with it; the ground under it takes the pavement texture (the forecourt) and its street-lamp row stays.
- **Flatten**: NEAR SIDE and OCCLUDER buildings that lie beside the corridor and whose wall would still cut into the frame edge: scaled in Y to **4 BU (8 m, two storeys: podium)** with the storefront band at its ground floor, so the street keeps its enclosure and the lamps/bays continue at the frame edge. Transition: height scale eases 1 -> 0.2 over the same ppb range with a dither on the top 10% (never a visible pop; the building sinks, which reads as a deliberate reveal).
- **Cut away**: a building that is both a HOST/FAR FRONTAGE and has a taller neighbour that hides its top (a "stepped" skyline problem): the neighbour is hidden (rule above), the host stays. No building is ever sectioned (no cut plane) except the Near-plane rule below.
- The hide/flatten decision uses footprint area inside the corridor: > 25% -> hide; 0-25% -> flatten; none -> keep.
- Ties and order: by distance to C, then building key. State changes have hysteresis (-12% on ppb) and 0.5 s dwell.
- Non-netrun traffic: sky cars and street cars in the corridor are removed (5.3).
- The hide set is **view-only**; the same city appears again on zoom-out (the dissolve reverses).

### 5.3 Lens-clutter avoidance
Given the camera ray `R` (eye to the focus) and the lens corridor = capsule of radius 3 m around R from the eye to 40 m, plus the screen-space rule:
- **Suppress** (dissolve, 0.25 s) any lamp, pole, bin, tree, bollard, wire span, sign, sky car, street car or debris whose camera-space depth < **12 m (6 BU)** OR whose projected bounding box (a) overlaps the central 60% of the frame width and (b) is taller than 35% of the frame height and (c) is closer than 25 m.
- **Push aside**: lamps and poles (the street's rhythm must stay) whose projected x is within the central 40% and depth < 40 m are shifted laterally to the nearest valid kerb slot not in the central 40%; when no slot exists they are suppressed; the lamp row spacing is re-hashed after the shift (the lamp keeps its id).
- **Wires**: no span crosses the central 50% of the frame at height > 5 m; spans run along the facade.
- **Trees**: street trees in the forecourt (the cleared foreground) are suppressed entirely; trees on the far pavement stay.
- **Debris and small props**: no prop within 8 m of the camera or in front of the focus node (within 3 m of the line of sight to any anchor `A_i`).
- **Anchor sight line**: a capsule of radius 1.5 m from the eye to each anchor of the current layer; anything intersecting it is suppressed (the nodes are the point of the view).
- All suppressions are dither-dissolves, never pops, with the same hysteresis as 5.2.

### 5.4 Near plane, depth, ink width (perspective)
- Near plane: **0.25 BU (0.5 m)**, far 4000 BU, reversed-Z. The prototype's near 1 BU (2 m) cut walls in the street stage.
- Soft near clip: geometry within 2 - 4 m of the eye is dissolved by distance dither (alpha 0 at 2 m, 1 at 4 m); nothing is hard-clipped.
- Ink: pixel-constant width from `ink_px / ppb_fragment` (2.1.1). The old ortho formula `0.6 + 160 / ortho` and the `* 1.6` perspective patch are removed; at stage 1 the ortho result is re-derived to give the same pixel width as r43 (test by image diff of the stage-1 frame).
- Thin items obey the min-pixel rule (1.2); ink of small modules (< 3 px) is not drawn.
- Depth of field: none (the cel look); a tilt-shift blur is available only in the backdrop-look component, not here.

### 5.5 Camera path between bands
- One continuous path from the city plan camera to the final street camera; **no cut, no ortho/perspective jump**:
  1. City -> District: iso ortho, yaw 135, pitch 40, ortho width 394 -> 130 (ppb 4.9 -> 14.8) log-space ease (existing stage 1-3).
  2. District -> Near-street: swap to perspective at ppb ~ 13 using a **dolly-zoom**: a start fov of 8 degrees (near-orthographic; difference imperceptible) at distance `d0 = 540 / (tan(4 deg) * ppb)`, then `fov` rises to 40 degrees while the distance shrinks to keep the focus ppb constant (ppb = 540 / (d tan(fov/2))), so the focus plane does not change scale during the swap; only the parallax grows. Pitch 40 -> 12 and yaw 135 -> the street normal ride the same easing (smoothstep over the focus ppb 13 - 24).
  3. Near-street -> Street: pitch 12 -> 0 and the lens shift 0 -> 0.24 (horizon from the centre to 0.74), eye height 30 m -> 4 m by `ppb` (log-space ease), focus ppb 24 -> 38.
- Rate: 0.5 octaves of ppb per second max (a x3 zoom ~ 2.2 s). Easing: smootherstep on log(ppb), no overshoot.
- Zoom out is the same path in reverse, with the hysteresis rules of 1.3.
- Along-route dolly at street level: the camera slides along the street axis at <= 12 m/s with a 0.6 s ease when the current layer changes, never closer than 2 lots to the frame edge of the focus node.
- The prototype's lerp-the-eye path (which swung the camera into the sky) is replaced by this scheme (focus-point dolly, in log space).
- Performance ordering: prefetch of the next band's chunks during the band before (1.3).

---

## 6. Netrun node attachment (every node is a real city object)

GDD 4.2 node types: **Router** (standard combat), **Elite Router** (elite combat), **Terminal** (event), **Mainframe** (shop), **Server Rack** (elite-strength combat + banking; layer 4 optional, layer 7 the single final node). 7 layers, 2-4 nodes per layer. No other types are added. Colours per type are the existing placeholder (readability, not GDD); see section 9.

### 6.1 The route on real streets
- The route lies on the street lot graph (`K_STREET` lots, plaza lots): A* on lot centres from the run's entry lot to the destination lot (the layer-7 Rack), preferring the longest straight street run and fewest turns; ties by lot id (i, then j). The route is not a free line: it is a polyline on the street graph.
- The 7 layers are arc-length stations along that path at `s_k = (k - 0.5) / 7 * L`; with `L` >= 21 lots (252 m, 36 m per layer); if shorter, the path is extended along the next street in the graph.
- Branches (2-4 nodes per layer): alternate nodes at `s_k +- up to 1 lot` on opposite frontages / the pavement edges of the route street. A branch that must leave the street takes a side street for <= 2 lots (an alley route) and rejoins at the next layer.
- Drawn as: a lit inlay in the pavement (the far frontage's walkway centre line) 0.7 m wide (min 3 px), lime `#96FF46` at emission 1.2 (existing route colour; Solace theme; confirm per corp), crossing the carriageway at the nearest crossing (zebra) when it changes sides, running along real kerb lines. At B0-B1 it is a thin ribbon in the street centre lines (3 px).
- Visited stretch: dimmed 40%; the next 3 layers: full; beyond: 30% with dashes.

### 6.2 Anchor object per node type (selection logic from the lots on the street)
For each node (sorted by layer, then node id), candidates come from the lots within +-1.5 lots of its station on both frontages (`street_walls` data: wall length, kind SHOP / SHUTTER / BLANK from `CityZoomPlan.wall_kind`, building height, host key). Score = type fit (below) + wall length bonus (0.1 per BU up to 1.0) + corp colour match with the layer's theme (+0.5); ties by (`hash(node id, 9880)`, lot i, lot j). One anchor per building; a building hosts at most one node. If no candidate exists, a free-standing street-furniture instance on the pavement is created at the station (still a real object).

| Node | Anchor object (real city object) | Fit condition | What it is at street level |
|---|---|---|---|
| **Router** | Telecom/street cabinet on the kerb-side pavement beside a building entrance | wall of any kind; prefer BLANK/SHUTTER walls so no shop front is covered | 0.9 x 0.5 x 1.3 m cabinet, hazard stripe, status LED (type colour), a pole-mounted antenna 3 m, an access hatch; node highlight = tube ring on the pavement (1.2 m) + beacon |
| **Elite Router** | Rooftop relay on a building of the far frontage (dish + antenna + red aviation light) | host height <= the frame's visible height (~ 42 m) so the roof is in frame; else the highest balcony / blade mount | 3 m dish, 6 m mast, a red blink (the elite cue; Heat +1 is game state, not drawn here), a thin vertical beacon to the roof |
| **Terminal** | Public terminal kiosk on the pavement, or a lit alley door with a buzzer panel | BLANK wall of a corner lot or a street-end building (alley mouth) | 0.8 x 0.6 x 2 m kiosk with a lit screen 0.5 m (text "TERMINAL"), or a steel door 1 x 2.1 m with a lamp and an intercom; type colour tube frame |
| **Mainframe** | Storefront of the largest SHOP wall in the window (the shop) | SHOP kind; widest wall; far frontage preferred | double bay (1.6x width) with shelves, awning, blade sign T3 and fascia T5 with the shop name, a "CYCLES" neon (no real brand), a lit door |
| **Server Rack** (layer 4 and 7) | A building entrance of a data hall: loading dock / roller door and a lit rack window band (2 floors) | wall length >= 8 BU; host height >= 14 BU; layer 7 = the tallest HOST in the final window | rack windows (columns of small lit rectangles, cyan/white, 1.0), a vertical cable duct, a roller door with a lit sign, a roof mast; layer 7: a crown ring + vertical edge neon |
The node object is attached to the same building keys that the plan dresses: the host key's signs are suppressed where the object stands (no overlap); the object receives the building's corp hue.

### 6.3 Marker look per band (selected / available / visited / locked)
| Band | Marker (the node's real object plus a readable highlight) |
|---|---|
| B0 City | ground disc (>= 10 px) in the type colour on the street at the station; the host roof rim lit in the type colour (3 px) |
| B1 District | disc + ring + a 5 px glyph (type) + the host building's corner rim lit; a vertical pole 9 m with diamond cap (existing placeholder, only for the selected node) |
| B2 Near-street | the anchor object appears (dither fade, 2.1-like), outlined by a 2 px tube; a thin beacon (0.3 m x 12 m, fading) above it; glyph diamond floating at 8 m (>= 24 px) |
| B3 Street | object at full detail, a holo label chip (type name + layer number, 0.8 m high letters, 8 px) hovering at 3 m; the beacon; the object's emission 1.6 (the brightest small thing in the frame); selected: white ring at the foot, pulse 1 Hz +-15% (reduce-motion: no pulse); visited: desaturated + a tick; locked: dim 40% |
| B4 Close | screen content, door detail, LED sequences (no game info beyond the type) |
Readability rule: at the final camera, every available node must be >= 40 px tall including its beacon; nodes never sit within the left/right 8% of the frame; at most 6 nodes in frame (3.5 layers x 2-4, with the unreachable ones dimmed).

---

## 7. Performance budget per band (GPU p95 limit 12.57 ms)

The prototype measured p95: stage 3 (district) 9.13 ms; stage 5 (street, layers on) 6.80 ms; city mean ~4.2 ms. The street band has ~4.5 ms of headroom up to 11.3 ms (10% reserve).

| Band | Target p95 | New cost allowed (over the prototype) | Breakdown (ms) |
|---|---|---|---|
| City | <= 8.6 (r43 baseline, nothing added; assert the zr class count 0) | 0 | - |
| District | <= 9.5 | +0.4 | window subdivision/panels shader 0.2, ink px formula 0.0, trees B1 lumps 0.2 |
| Near-street | <= 10.6 | +1.7 | modules (balconies, AC, pipes) 0.4, bays/signs 0.4, wetness + planar reflection 1/8 res 0.4, props/lamps 0.3, sky/haze 0.2 |
| Street | <= 11.3 | +4.5 vs 6.8 | facade shader 0.8, modules 0.7, sign atlas 0.4, planar reflection 1/4 res 1.0, sky + haze cards + searchlights 0.5, clutter/lamps 0.4, wires/steam/particles 0.2, trees B3 0.3, node objects 0.1, margin 0.1 |
| Close | <= 11.8 | +0.5 | adds only inside 25 m |
CPU (main thread): <= 1.5 ms per frame for build/prefetch; <= 6 draw-call families for the zoom layers (signs atlas, modules MultiMesh x 3, lamps, props).
Memory: modules MultiMesh <= 3000 instances; atlas 2048^2.
Cull order when over budget (first dropped first):
1. Close-only detail and rain ripples; 2. steam particles; 3. wires; 4. small props (bins, crates, benches); 5. hanging lanterns / string lights / fairy lights; 6. balcony + pipe geometry on non-focus rows; 7. roof clutter beyond 150 m; 8. planar reflection: 1/4 -> 1/8 -> lowest 12 m only -> additive streak quads; 9. leaf cards (trees fall to lumps); 10. haze cards (kept: fog only); 11. ink on far buildings (already off); 12. sign text (glyph bars).
Never culled: the storefront band, the lamp row, the node objects, the fog curve, the sky.

---

## 8. Implementation order (ranked by gap closed per effort)

1. **Camera + framing + ink + near plane** (5.1, 5.4, 5.5): perspective 40 degrees, eye 2 BU, lens shift, near 0.25, px-constant ink, the dolly-zoom path. Cheap; removes the near-plane cut, the thick ink and the aerial look in one step.
2. **Occluder classes + hide/flatten with dither** (5.2, 5.3): the corridor and lens rules; the first step that makes the frontage a plate-like row with space and sky.
3. **Sky dome + fog curve + 3 haze cards + searchlights** (4.1-4.4): the missing sky and layered depth are among the largest plate differences and are mostly shaders.
4. **Tall-tower facade grammar + window subdivision + panel kinds + wall tone steps** (2.1.1-2.1.2, 2.1.7): kills the blank 80 m prisms; all shader, ~0.8 ms.
5. **Continuous storefront band at real scale + fascia signs + pavement/kerb** (2.1.4, 2.4 pavement): creates the brightest horizontal; squint test.
6. **Wet road: wetness map, planar reflection, lane markings, crossings, utility plates, car streaks** (2.4): the plate's lower 20% and the doubling of light.
7. **Sign hierarchy with caps, atlas text and the 1-in-3 neon rule** (2.1.5): removes the single dominant billboard, fills the mid-walls.
8. **Real-scale lamp + clutter placement + min-pixel rule + lens-clutter suppression** (2.3, section 3, 5.3): removes the toys.
9. **Trees: lumps -> leaf cards, trunks** (2.2) and facade modules geometry (balconies, AC, fire escapes, roof clutter) (2.1.3, 2.1.6): detail density per metre.
10. **Node attachment, route on streets, markers per band** (section 6): the netrun's actual function, built on the real objects above. It needs 1-9 visually but the placement logic (selection, routing) can be built and tested in parallel from step 2.
Parallel: decks/rail/quay phases (2.5, 2.6) are the last, since they are rarely in frame.
Gate for each item: render the 5-stage strip, put the plate beside it (parity against the golden plate), do the 1/16 squint, then perf (p95 table 7). Tests: determinism (same dressing whatever the rect, per `test_city_zoom_layers` pattern), the band fade table is monotone, the City band is image-identical to r43, the no-blank-wall plan assert, sign-area cap (<= 6% hero, 8-12% total), neon share 0.34 +- 0.04, lens suppression (nothing within 12 m of the lens).

---

## 9. Unresolved items for the designer

1. **How much foreground may be hidden or flattened?** With a long lens the camera sits ~75-80 m (6-7 lots) back from the frontage; on a 12 m street the near side is entirely removed or flattened to 8 m podiums. The alternative (fov 62, 30 m back) shows the near-side walls but re-creates the prototype's canyon look. Recommendation: long lens + cleared forecourt.
2. **One frame or a dolly?** The 7 layers span ~250 m; the view shows ~110 m. The spec dollies along the route (3.5 layers visible). If the designer wants the whole map in one frame, the camera must stay at the District band (ppb ~14) for the map and only drop to street level for a node.
3. **Node type to object mapping** (6.2: cabinet, rooftop relay, kiosk/alley door, storefront, data hall entrance) and the **type colours** (pink fight, yellow event, cyan rest, lime shop, white HQ are the earlier placeholders and do not match the GDD node names). Designer pick.
4. **Palette**: the plates are warm magenta/pink and cyan on near-black plum; the city's r6 cel look is blue-violet with lime/teal. At the Street band the grade should lean to the plate. Allowed? The spec keeps the corp-colour rule (55% corp, 45% palette) and morphs the fog/sky/ground grade toward the plate's by `smoothstep(16, 28, ppb)`.
5. **Kana and brand text**: decorative strings only, no native-reader check (as before); invented brand names from `netrun_cel/NOTES.md`.
6. **Day look**: this spec is the night look (the netrun is night). The day variant is the same rules with `night_k` and a day grade; not specified.
7. **Reflection technique**: planar mirror at 1/4 res is the primary; if Godot's pipeline forbids a second camera in this viewport, fall back to SSR or the streak quads; engine check needed on the implementer's side.
8. **Road widths**: the real city streets are 12 m and 36 m (1 and 3 lots); the plate's street looks ~30 m wide. The cross-section templates (2.4) keep real widths and do not widen the street.
9. **Tower cropping**: with the 40 m of visible height, towers above ~55 m are cropped by the top edge in the frontage row. If the designer wants whole towers visible, the camera must be farther (fov 28) or tower heights in the frontage row must be capped (not recommended: they are real data).
10. **Reduced motion**: pulses and streak drift obey the existing reduce-motion setting (motion off = static streaks, no pulse).
