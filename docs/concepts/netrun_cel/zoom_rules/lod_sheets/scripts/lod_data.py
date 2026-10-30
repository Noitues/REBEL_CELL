"""Per-element data of the LOD sheets: title, what to look at, the built status per band and the spec text per band (condensed from ZOOM_RULES.md section 2 / 3 / 4).

Status per band (B0 City, B1 District, B2 Near-street, B3 Street, B4 Close):
  built   the code builds what the spec asks for this band (round 1, art/netrun-zoom 9a5069c1)
  partial some of it is built (the note says what is missing)
  asis    the r43 look carries this band; the spec's additions for it are not built
  none    nothing is built for this band: the cell shows the spec text only (NOT YET BUILT)
"""

BANDS = ["CITY", "DISTRICT", "NEAR-STREET", "STREET", "CLOSE"]
RANGES = ["< 8 px/BU", "8 - 16", "16 - 28", "28 - 56", ">= 56"]

SHEETS = [
    {
        "id": "tower", "file": "lod_tower.jpg", "title": "Building: tall tower (45+ BU, neon edge)",
        "look": "Does the facade stay a dark wall with sparse lit windows at street scale, or does it read as a flat colour? Floor lines, panel kinds, mechanical band, corner neon strip.",
        "status": ["built", "partial", "partial", "built", "none"],
        "notes": ["r43 look, zoom rules change nothing here.",
                  "Same r43 window lattice; facade grammar is still faded out (it starts at 22 px/BU). Ink width is already pixel-constant.",
                  "Facade grammar fading in (22 - 34): 1.5 x 1.8 BU cells, panel kinds, tone steps. Missing: ledges, pilasters, balcony/AC/pipe geometry.",
                  "Full grammar: window cells with frame/mullion, lit ribbons, mechanical bands, corner neon. Missing: crown ring, side-wall rule, no-blank-wall plan assert.",
                  "Nothing Close-specific (panel seams, rivets, cable runs)."],
        "spec": [
            "r43 unchanged: facet prism, jittered tones, corp parapet rim, crown LED band, mast + aviation light. Windows 3.0 x 3.6 BU cells, 0.30 lit.",
            "Facet jitter x0.4; tone by height bands (storefront zone 1.0 then 0.78 ... 0.24); pilasters every 6 BU on walls >= 24 BU. Cells 3.0 x 3.6 start splitting 2 x 2 over 12.8 - 19.2. Vertical edge neon from 8 px/BU. Ink 2.0 px.",
            "Cells 1.5 x 1.8 BU, window 0.9 x 0.75 with frame + mullion + transom; setback ledges with rims (<= 6 per tower); floor lines on the floor grid; panel kinds start. Ink 1.6 px.",
            "Plate look: jitter 0.05, grime + rain streaks, blinds, glass sheen, per-pane light; zones base / podium / shaft / crown; mechanical band every 22-30 m; a feature every 8 m of height. Ink 1.4 px.",
            "Panel seams 0.1 m, rivets, wall stains, cable runs, curtain and person silhouettes in lit cells. First frontage row only. Ink 1.2 px."]
    },
    {
        "id": "midrise", "file": "lod_midrise.jpg", "title": "Building: mid-rise with storefront (20 BU)",
        "look": "The ground floor is the brightest horizontal of the plate. Check the storefront band is continuous, the fascia text reads, and the upper facade stays darker than the band.",
        "status": ["built", "partial", "partial", "built", "none"],
        "notes": ["r43 look.", "r43 lattice; storefront band not built below 16 px/BU.",
                  "Bays, awnings, fascia glyph bars appear late (fade 22 - 34); facade grammar blending in. Missing: balconies, AC, pipes, fire escape.",
                  "Continuous storefront band (shop windows, awnings, lanterns, OPEN boards, fascia text), pavement, kerb, lamp. Missing: modules, roof clutter set.",
                  "Nothing Close-specific."],
        "spec": [
            "r43: lit window lattice, parapet rim, no ground-floor treatment.",
            "Lit ground strip (one shop hue per wall) + 1.2 BU pavement skirt; floor lines; tone steps; neon strip on 1 in 3.",
            "Bays: dark frame, lit window in a shop hue, 2 shelves of goods, two-tone awning on 50 percent, ribbed shutter on 16 percent, shop spill on the pavement. Balconies, AC units, pipes fade in 16 - 22.",
            "Per bay: door recess, mullion, OPEN / menu board 1 in 4, lantern pair 1 in 5, fascia sign with text; bay width 3.6 - 5.2 m with 0.3 m pilasters. Band is always continuous (no holes > 10 percent).",
            "Awning seams and drip, goods with price tags, door handle, street reflection in the glass."]
    },
    {
        "id": "storefront", "file": "lod_storefront.jpg", "title": "Storefront band (floors 1-2, 0 - 8.4 m)",
        "look": "Brightness and continuity: the band must out-shine the facade (target >= 2.5x), with no holes. Bay rhythm, shop hues, awnings, spill on the pavement.",
        "status": ["none", "none", "partial", "built", "none"],
        "notes": ["Not specified below the District band.", "Spec asks for a lit strip + pavement skirt here; the zr dressing starts at 16 px/BU.",
                  "Built from 16 but only fully visible from 34 (fade 22.4 - 33.6).",
                  "Built: continuous band, bays 1.8 - 2.6 BU, goods, awnings, shutters, lanterns, spill. Missing: band luminance not measured against the 2.5x target.",
                  "Nothing Close-specific."],
        "spec": [
            "Not part of the City band.",
            "Lit ground strip (existing), one shop hue per wall; 1.2 BU pavement skirt as a bright horizontal.",
            "Bays with dark frame, lit window in a shop hue, 2 shelves with 4-6 goods blocks, awnings on 50 percent, ribbed shutters on 16 percent (lit seams); additive shop spill (5 BU fade).",
            "Door recess (2.1 m) on 1 in 3, mullion, neon OPEN / menu 1 in 4, lantern pair 1 in 5, fascia sign with text, bay width 3.6 - 5.2 m, 0.3 m pilasters; always continuous along a frontage.",
            "Awning seams and drip, goods with price tags, door handle, street reflection in the glass (20 percent gradient)."]
    },
    {
        "id": "sign_fascia", "file": "lod_sign_fascia.jpg", "title": "Signs: fascia (tier T5, one per shop bay)",
        "look": "Does the text read (>= 7 px letters) or fall back to glyph bars? Neon frame on 1 building in 3, lit box on the rest. Text clipped at wall ends is a known fault.",
        "status": ["none", "none", "partial", "built", "none"],
        "notes": ["Signs are not drawn here.", "Not drawn below 16 px/BU.", "Fascia boards with 3 x 5 glyph text from the invented name list; fades in 22 - 34.",
                  "Text fascia on every bay: neon tube frame (1 in 3) or lit box. Missing: SDF atlas, text is cut at wall ends.", "Nothing Close-specific."],
        "spec": [
            "No signage detail.", "T5 fascia not built yet in the spec at this band (glyph bars start at B2).",
            "T5 fascia as glyph bars: bay width x 0.9 m, one per shop bay (80 percent), lit text on a dark board with a neon frame on neon buildings (1 in 3).",
            "T5 with real text (SDF atlas, height >= 7 px else glyph bars); T6 small signs (OPEN, menu, address) 1 in 4 bays; 2 hues per building at most.",
            "Letter edges, tube mounts, sign wear."]
    },
    {
        "id": "lamp", "file": "lod_lamp.jpg", "title": "Lamp (street lamp, kerb)",
        "look": "Toy versus real: r43 lamp is a cube + pole + panel. From 16 px/BU a 7 m pole with arm, 0.8 m head and a glow pool replaces it. Check the replace does not pop.",
        "status": ["built", "asis", "partial", "partial", "none"],
        "notes": ["r43 lamp.", "r43 lamp; the real-scale lamp is built from 16 px/BU, not in the District band.",
                  "Real-scale lamp: pole 7 m, arm, head, glow pool, 1 in 12 dark. Missing: double arm on avenues, replace-in-kind cross-fade with the toy lamp.",
                  "As Near-street. Missing: base plate, glass underside, bokeh halo, wet hot-spot, cable.", "Nothing Close-specific."],
        "spec": [
            "r43 lamp: cube base + pole + panel from CityLampPlan, brightness drift, outages.",
            "Same positions; size by the min-pixel rule: plinth 0.6 m, pole 7 m, head 0.5 m, 3 px additive glow dot.",
            "Pole + curved arm + luminaire box 0.8 x 0.3 m + warm cone pool decal (6 m); outage 1 in 12; double arm on avenues.",
            "Base plate, tapered pole, arm, glass-underside luminaire, bokeh halo 0.3, pool with wet hot-spot reflecting in the road, cable on 1 in 4 poles.",
            "Bolts, banner bracket, small sign plate."]
    },
    {
        "id": "tree", "file": "lod_tree.jpg", "title": "Tree / bush",
        "look": "How far the blocky dome goes: the spec turns it into lumps with a trunk (District), a tiered canopy (Near) and leaf cards (Street). Only the r43 dome exists.",
        "status": ["built", "asis", "asis", "asis", "none"],
        "notes": ["r43 dome (spec B0 = r43).", "Still the r43 dome: no lumps, no trunk, no bush.", "Still the r43 dome, no street-tree scale, no pit, no bush.",
                  "Still the r43 dome: no leaf cards, no bark, no fairy lights.", "Nothing Close-specific."],
        "spec": [
            "Blocky dome 1.6 x 2.1 BU, dark green, one colour of park_tree_colors. Bushes are part of the lawn tone.",
            "3 overlapping 12-tri spheres filling the dome silhouette + trunk (0.4 m, min 2.5 px, 35 percent of the height); 1-2 bush lumps on lawn edges 1 in 4 clumps.",
            "6-9 lumps in 2 layers (tilted 3-tier canopy), trunk with 2 branch stubs, 6-9 m street-tree height; tree pit ring + grate; hedge along medians; pit uplight 1 in 4 on avenues.",
            "Lump clusters wrapped in 18-24 alpha-cut leaf cards each, bark bands, 3-5 branches, fairy lights 1 in 3; clipped hedges; planters at 1 in 4 bays.",
            "Leaf-card density x1.5, individual branches, bark texture, grass blades within 1 m of the camera."]
    },
    {
        "id": "park", "file": "lod_park.jpg", "title": "Park / lawn",
        "look": "Flat lawn tone with scattered domes at every band. The spec adds mow stripes, path edges, grass tufts, flowers and soil edge. None are built.",
        "status": ["built", "asis", "asis", "asis", "none"],
        "notes": ["r43 lawn (spec B0 = r43).", "r43 lawn, no mow stripes or path edge.", "r43 lawn, no tufts or soil edge.", "r43 lawn, no flower dots or path stones.", "Nothing Close-specific."],
        "spec": [
            "Lawn flat colour + noise.", "Mow-stripe noise, path edge.", "Real mow stripes, grass tuft quads 1 in 6 m, soil edge at the lawn, gravel noise in courtyards.",
            "Tufts, flower dots (palette) 1 in 12 m^2, path edge stones, clipped hedges, planters.", "Instanced grass blades within 1 m of the camera."]
    },
    {
        "id": "road", "file": "lod_road.jpg", "title": "Road surface",
        "look": "Wet asphalt: markings, utility plates, tyre tracks and the planar reflection. Does the street read as a street (not a diagram) and is the wet look believable at the plate's scale?",
        "status": ["built", "partial", "partial", "partial", "none"],
        "notes": ["r43 flat street colour + lane glow.", "Road shader starts fading in at 14 px/BU (zr_fade_road 14 - 28); little visible at 12.",
                  "Asphalt noise, patches, tyre tracks, utility plates, edge / centre / double-yellow lines, zebra, wetness map + planar reflection. Missing: kerb drains, manholes, parking bays, bike lanes.",
                  "Same shader fully faded in with the reflection. Missing: manholes, steam, crack lines, tactile strips, speckle, aggregate.", "Nothing Close-specific."],
        "spec": [
            "r43 flat street colour + lane glow strips + network ground decal; street cars as points.",
            "Dark asphalt with 2-octave value noise; lane glow narrowed to 0.4 m lines; faint centre dashes; kerb line; wet sheen 0.2, no mirror.",
            "Patches, tyre tracks, utility plates 3 x 1.2 m, dashed centre, edge lines, double yellow, zebra, stop lines, arrows; pavement slabs, kerb face, drains; wetness map + planar reflection 1/4 res; car streaks.",
            "Speckle, cracks, manholes with steam, tactile strips, worn paint, bike lane, kerb chamfer, gutter strip, puddles with ripple warp and vertical smear, bokeh reflections.",
            "Micro-normal, puddle rings, rain ripples within 15 m, litter, kerb joints, wheel spray."]
    },
    {
        "id": "sign_blade", "file": "lod_sign_blade.jpg", "title": "Signs: blade (tier T3, vertical, floors 2-8)",
        "look": "Nothing is built under the rules for T3 yet; the in-context row shows what the facade carries instead. Check the spec: 1 blade per 8-12 m of frontage, no two adjacent the same hue.",
        "status": ["none", "none", "none", "none", "none"],
        "notes": ["", "", "T3 blades are not rebuilt in zr mode (the prototype zl layer is off).", "", ""],
        "spec": [
            "No blade signs in the City band.", "T3 blade sign: not before 14 px/BU.",
            "T3 blade 1.0-1.2 x 3-8 m, 1 m out from the wall, floors 2-8, one per 8-12 m of frontage on 40 percent of walls; <= 14 per frame; no two adjacent the same hue.",
            "Same, with kana / text strips and lit faces; neon tube frame on neon buildings.", "Mounting bracket, tube joints."]
    },
    {
        "id": "sign_roof", "file": "lod_sign_roof.jpg", "title": "Signs: roof (tier T2, on posts)",
        "look": "r43 roof logos / screens exist at every band. The spec wants 5-9 x 1.5-3 m roof signs on posts, 1.5 m up, on roofs >= 36 m. Compare what the roof carries now.",
        "status": ["built", "built", "partial", "partial", "none"],
        "notes": ["r43 roof logos / screens.", "r43 roof logos / screens.", "r43 roof sign remains; T2 post-mounted sign not rebuilt.", "Same; the hero cap drops most roof screens at the street camera.", ""],
        "spec": [
            "Existing roof billboard panels, mast, aviation light.", "T2 roof sign (8-14 px/BU): 5-9 x 1.5-3 m on posts 1.5 m, roofs >= 36 m, half of them, neon dim; <= 4 per frame.",
            "T2 as B1, lit faces and post detail; roof sign + tank + shed lit door.", "T2 with lettering; <= 4 per frame; roof clutter around it.", "Wear and mounting."]
    },
    {
        "id": "sign_hero", "file": "lod_sign_hero.jpg", "title": "Signs: hero billboard (tier T1)",
        "look": "One hero per frame, <= 6 percent of the frame. r43 has many giant screens; the rules drop all but one at the street camera. Does the hierarchy hold?",
        "status": ["built", "built", "partial", "partial", "none"],
        "notes": ["r43 screens.", "r43 screens.", "Screens exist; hero cap (4 percent) applies once the camera is perspective at melt 1.", "As Near-street; one pink / white panel of unknown source still dominates some frames.", ""],
        "spec": [
            "Existing roof / holo screens.", "T1 hero: glyph blocks (existing screens) on 1 in 8 towers >= 60 m, 12-16 x 5-7 m, street-facing, top third.",
            "T1 stays glyph blocks; animation not before 28.", "T1 hero animated; exactly 1 per frame, screen area <= 6 percent of the frame; the others count as T4.", "Pixel structure of the screen."]
    },
    {
        "id": "clutter", "file": "lod_clutter.jpg", "title": "Street clutter (bollards, vending, bins, crates, vents, wires, lanterns)",
        "look": "Mostly not built. What exists: hanging lanterns and shop spill. Everything else is the spec plan: look at the density and placement rules.",
        "status": ["none", "none", "partial", "partial", "none"],
        "notes": ["", "", "Only lanterns, shop spill and real lamps exist.", "Same; no bollards, vending, bins, crates, steam, wires, street signs, stalls.", ""],
        "spec": [
            "Nothing of section 3 is built below the Near-street band.", "Nothing; lamps are the only exception (min-pixel).",
            "Bollards (2 per kerb ramp), vending machine 1 per 40 m (lit 1.2), overhead wires on poles every 24 m, telecom cabinet / hydrant / mailbox (Router anchor), real lamps.",
            "Bins beside lamp bases, crate stacks, steam vents on manholes, hanging lanterns / string lights 1 in 5 bays, street-name plates, stalls on pavements >= 5 m, benches, bike racks; <= 600 small emissive quads.",
            "Gum stains, litter, kerb joints."]
    },
    {
        "id": "roofprops", "file": "lod_roofprops.jpg", "title": "Roof clutter (tanks, sheds, antennas, dishes, roof signs)",
        "look": "r43 roof props show up when zoomed in. The spec adds bulkheads, rails, cables, catwalks, neon roof props (cat, fish, bowl). None of the extras are built.",
        "status": ["built", "built", "partial", "partial", "none"],
        "notes": ["r43 mast + aviation light.", "r43 CityRoofProps (tanks, antennas, AC boxes, billboards) at this zoom.", "r43 props only; no bulkheads, rails or cables.", "r43 props only; no catwalks, neon roof props, roof garden pots.", ""],
        "spec": [
            "Mast, aviation light, existing roof billboard panels.", "Water tank on legs (1 in 4 mid-rise roofs in view), AC boxes, shed with lit door (1 in 6), roof sign.",
            "Stair bulkhead, railings (1 px), dish, vents, cables between boxes, small roof lamps on 1 in 3 bulkheads (hash 9840).",
            "Catwalks, tank ladders, hand rails, neon roof props (cat / fish / noodle bowl, 1 per 10 roofs), roof garden pots; only roofs visible to the camera.", "Wooden slats on tanks, rust streaks."]
    },
    {
        "id": "modules", "file": "lod_modules.jpg", "title": "Facade modules (balconies, AC units, pipes, fire escapes)",
        "look": "The geometry that gives the plate its detail per metre. Not built: only AC boxes and louvres exist as shader panel kinds on the wall.",
        "status": ["none", "none", "none", "partial", "none"],
        "notes": ["", "", "", "AC box and louvre panel kinds are painted by the shader; no balcony slabs, pipes or fire escapes.", ""],
        "spec": [
            "No modules in the City band.", "Floor lines (shader), vertical edge neon.",
            "Balcony slab + rail on 30 percent of residential floors 3-12 (fade 16 - 22), AC units 5 percent of cells (<= 150 as a MultiMesh), drain pipes 1 per 12 m, fire escapes from 18 on side walls (<= 6 buildings).",
            "Full balconies with underlamp, AC units with LED, pipes with brackets, fire escapes with ladder, wall posters, hanging laundry; <= 60 balconies, <= 40 pipes per frame.",
            "Cable runs and conduits between modules, first row only."]
    },
    {
        "id": "highway", "file": "lod_highway.jpg", "title": "Highway deck and traffic",
        "look": "The elevated deck at each band: r43 ribbon with rail glow and pylons. The spec adds underside tone, barriers, lamp rows, road signs and reflections. None of it exists yet.",
        "status": ["built", "asis", "asis", "asis", "none"],
        "notes": ["r43 deck ribbon + traffic.", "r43 deck; no parapet, underside tone, pylon caps.", "r43 deck; no lane markings, barriers or underside lamps.", "r43 deck; no road signs, scuppers, cables, wet reflections.", ""],
        "spec": [
            "Deck ribbon at 12 BU lift, side faces, rail glow lines, pillars every a2_pillar_every_bu, traffic dots.",
            "Darker underside tone, 1 px edge parapet, separated lane glow lines, pylon cap + 3 px base, ramp rails.",
            "Dashed centre marking, crash barrier 0.9 m (posts every 4 m), underside lamp row (warm 0.5, every 12 m), chevron signs, round pylons with ink and cap beam.",
            "Green road signs on 1 in 4 spans, drain scuppers, underside cables, guard rails, base plates, reflections on the wet road below, under-deck street -15 percent value + fog bump.",
            "Rivets, stains."]
    },
    {
        "id": "water", "file": "lod_water.jpg", "title": "Water / quay",
        "look": "Sea, shore foam, quay promenade. The r43 water shows at every band; the spec wants real-scale quay detail: rails, mooring rings, steps, reflections of quay lights, benches.",
        "status": ["built", "asis", "asis", "asis", "none"],
        "notes": ["r43 water + promenade.", "r43 water; no sharpened foam line or bollard dots.", "r43 water; no wave highlights, railings or mooring rings.", "r43 water; no wet-ground reflection of the quay, benches or bins.", ""],
        "spec": [
            "city_water (sea, void, ripple, caustic, reflect gain), promenade, warehouse blocks, lamp points.",
            "Foam line sharpens; promenade lamps real size; bollard dots every 12 m; seawall coping lit strip; crane cross-braces; ship deck lights.",
            "Wave highlights; quay-light reflections as vertical smear at real scale; railings, mooring rings, steps; container stacks; gantry lights.",
            "Quay as wet ground (planar reflection); pier lamp at real size; benches, bins; warehouse doors with lamps; ship name signs; crane warning lights.",
            "Ripple rings, planks."]
    },
    {
        "id": "sky", "file": "lod_sky.jpg", "title": "Sky / fog (lab: six towers at 15 - 360 BU)",
        "look": "The depth ramp: fog curve over distance (6 percent at 50 m ... 85 percent at 600 m), the sky gradient above the horizon, haze cards. Adjacent depth layers should differ by >= 8 percent luminance.",
        "status": ["built", "asis", "partial", "partial", "none"],
        "notes": ["r43 fog 0.22, haze_k 0.34.", "r43 (the ground mist layer is not built).", "Sky gradient + fog curve fade in 16 - 28 by fragment ppb. Missing: 1 BU mist, per-corp sky tint.",
                  "Sky, fog curve, 3 haze cards, ambient beams (not visible in the street frame). Missing: mist 6 m, lamp light shafts, depth-layer value targets.", ""],
        "spec": [
            "r43 fog (0.22) and haze_k (0.34); dark sky; r43 post.",
            "Ground mist layer fades in (0.5 BU high, additive violet 0.08); r43 post.",
            "Mist 1 BU (2 m) on the focus streets; distance fog curve 1 - exp(-(d/D)^1.4) blends in; ink in px; bloom radius scales with ppb; sky dome fades in by pitch.",
            "Full depth haze with 3 depth cards (60 / 180 / 450 m), mist 6 m, light shafts at lamps, rain +20 percent; sky gradient #1a0c28 - #2c1233 - #58294f; two ambient searchlight beams.",
            "As Street."]
    },
]
