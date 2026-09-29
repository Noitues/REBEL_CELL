# C · RISO PUNK ZINE

**Pitch:** the whole game is printed matter. The Cell photocopies the city, cuts it up, tapes it to the terminal and scrawls on it in fluoro marker. The corp's cold system text keeps printing underneath, washed out, and the marker writes over it.

## Pillars
1. **Spot ink, not RGB.** Three inks: fluoro pink, aqua and black. Acid and amber are sticker stock only. Plates misregister by 2 px, and halftone dots stand in for gradients.
2. **Real paper physics.** Every layer is a cut card at its own height, so depth comes from shadows between the layers, not from outlines.
3. **Marker verbs over system words.** SEND IT over EXECUTE, GRAB IT over PURCHASE, BAIL over DISCONNECT, RUN over EVASIVE ROUTE, HIT THIS over TARGET_ACQUIRED.

## Palette
| Hex | Role |
|---|---|
| `#FF48B0` fluoro pink | The Cell: the marker, attack and crit slices, the MODEM tubes. Its darker edge `#C81E78` is ink pooling. |
| `#00A9E0` aqua ink / `#5CE1FF` as light | System glass, defend slices, operative rim. |
| `#1A181C` riso black | Key plate, shading screens, silhouettes. |
| `#F2EEE4` paper, `#F2DC7A` note yellow | Tags, cards, captions. |
| `#D4FF00` acid | Cell turf links, node stickers, the tick pointer. Never on glass. |
| `#FFB000` amber, `#FF4433` harm | Heat (NOTICED and HUNTED), damage. The HUNTED overprint is a harm plate. |
| `#FF8C1A` Meridian | Corp hue, stripes on the enemy bezel, threat routes. |
| `#0D1026` night stock | City card stock, darker for nearer rows. |

## Materials and layering (back to front)
City cards → vellum sheets (they dim and desaturate the city) → glass panels (lit and self-lit) → paper tags and cards with tape → vinyl stickers (die-cut white border, gloss band, peeling corner) → Grease Pencil marker, which is unlit and casts no shadow.

## Lighting and spill (10)
Neon parts emit (rims, tubes, HP arcs, holograms, windows). Each one also carries a real coloured point light, so the pink MODEM sign tints the glass beside it, the cyan rim lights the forecast panel and the billboards light nearby rooftops. The marker and stickers never emit. A single low sun throws the drop shadows.

## Motion (for the animation pass)
- **Marker (6):** a stroke-order reveal in the stroke font's own order, with a pen sprite at the tip.
  - Drips grow from the lowest point of a letter and hold as beads while input is awaited.
  - On press the page slides away. The ink stays on the glass and the drips run to the bottom of the screen.
- **Sticker slap (8):** the card drops from +Z, bigger and with a wide soft shadow, and overshoots down with a 2-frame squash. Its shadow snaps tight, the gloss band sweeps across, and one corner may stay lifted.
- **Binary shards (5):** die-cut 0s and 1s in pink and aqua burst from the landed slice with a paper tumble (3D spin, so the white backs flash). They fade in their own glow. Tier T2.
- **Heat glitch (11):** the screen is split into horizontal slices that shift, the pink and aqua plates separate, and faint scan bands appear. Amplitude scales with the Heat band, and HUNTED adds a red halftone overprint that creeps in from the edges. One toggle turns it off.

## Spinner depth (4)
1. **Stacked discs with real gaps:** plate, bezel, slice ring, dial, then the hub sticker, each 0.1–0.3 higher than the last. The sun drops each layer's shadow onto the one below.
2. **Visible paper edges:** each disc has a white core wall, so any tilt or parallax shows its thickness.
3. **Glass dome:** a lens with one specular highlight sits over the stack.
4. **Neon rim tube and HP arc:** these float above the bezel and light it.
5. **Slice gaps:** slices are separate cut pieces, so hairline shadows show between them. The enemy wheel is plastered with the collector's stickers, some peeling.

## Feedback answers
- **2 Modem sign:** kept as a vertical neon sign, redrawn with original bent tubes. MODEM is pink and CYBER SHOP is cyan, with circuit traces and solder rings. There are no BUY or SHRED stickers.
- **3 Combat backdrop:** the city sits two vellum sheets back, with saturation at 30% and windows dimmed.
- **4 Spinners:** see above.
- **5 Damage:** binary shards.
- **6 Marker:** still 05.
- **7.1 HQ:** fully framed and circled OURS.
- **7.2 Fog:** vellum patches, each blurred differently (3–40 px), some with halftone dots.
- **7.3 Tilt-shift:** an ortho camera plus a blur that grows with screen height.
- **7.4 Grid:** node stickers and marker links lie flat on the map sheet.
- **7.5 Traffic:** three highway decks on stilts carry car cut-outs, and flyers hang on thread.
- **7.6 Billboards:** acetate billboards on projector beams.
- **7.7 Incursions:** helicopters with searchlights and a drone swarm.
- **8 Cards:** the hand and the shop cards are stickers, one of them mid-slap.
- **9 Marker over digital:** everywhere.
- **10 Light spill:** see above.
- **11 Heat glitch:** in post.

## Building it in Godot 4.7
- **Mostly pre-rendered and 2D:**
  - City cards, stickers and cards are Pillow/Blender-printed textures.
  - Layers are `Sprite2D`/`TextureRect` nodes at parallax depths, with drop shadows from an offset, blurred copy of the sprite's alpha (a cheap shader).
  - Spinners are 4–5 `TextureRect` discs, each rotated as its own ring with its own shadow offset.
- **Shaders:**
  - misregistration, which offsets the pink plate by 1–2 px;
  - halftone, a screen-space dot mask for shading;
  - vellum, a blur plus desaturation behind combat;
  - the Heat glitch as a full-screen `CanvasLayer` shader;
  - tilt-shift, a vertical blur ramp over the city.
- **Marker:** stroke polylines stored as data and revealed with `Line2D` point counts. Drips are `Line2D` with a bead sprite.
- **Spill:** `PointLight2D` on neon parts with light masks that exclude marker and sticker layers.

## Risks
- **The page gets busy.** Grain, dots and misregistration on every surface can bury data (Readable is pillar 1). Glass text must stay un-halftoned and un-misregistered. Only the city and paper take the print pass.
- **Dark city silhouettes vanish at night.** They need their printed rim ink and the haze cards.
- **Marker overuse dilutes it.** Keep to one verb and one hand mark per screen.
- **Peeling corners and the 3D slap** need a mesh or skew in 2D. Pre-rendered frames are safer.
- **The heat glitch** must stay subtle and switchable. Still 03 shows its upper bound.
