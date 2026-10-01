# o_b_stencil_spray: Stencil & Spray

**Medium.** The Cell tags the screen glass the way a crew tags a wall. There are three kinds of mark:
- **Cut stencils** for verbs and labels.
- **Freehand can lines** for loops and arrows.
- **Wheat-paste photocopies** for the Heat poster and the crew ID.

Old overlay marks are **buffed** with black spray, as a city buffs graffiti, and new paint goes over the top.

**Palette.** Three spray colours plus a black stencil shadow:
- **Hot pink** `#FF2488` for the verbs and calls to action.
- **Toxic yellow** `#DEFF22` for targeting, loops, threats and price tags.
- **White** `#F4F2EA` for notes and labels, and as a mis-registered key layer under the pink verbs.
- **Black** `#0A090C` for the offset shadow layer. Posters are off-white paper `#E8E2D2` with black toner.

**Lettering.**
- **Verbs:** a heavy condensed grotesque with cut stencil bridges. Counters are bridged at the stem, the way a real D stencil is cut, and the big verbs get a horizontal slice. Edges are hand-cut, with slight wobble.
- **Layers:** each verb is sprayed in three passes: a black shadow offset down-right, a white key offset up-left, then the pink face.
- **Small text:** notes stay at bridges-only, so they remain readable. The system word (GO, PURCHASE, EXIT) stays visible, washed and desaturated, under the human verb.

**Why it reads as AAA.** The paint has real material response:
- Fine atomised overspray that is densest at the stencil edge.
- Mottled coverage with edge build-up and a faint semi-gloss lift on the paint skin.
- Wet drips that are darker than the letter, with a lit flank, a dark flank and a tight specular on the bulb.

Paper gets the same treatment: fibre noise, paste wrinkles and bubbles, a brushed wet sheen, torn bites with pale fibre rims, and a curled corner that shows the paper back with ink ghosting through. Against the flat, outline-free Cv2 facets, everything reads as a physical layer on the glass. The marks are restrained: 4–6 per screen.

**Godot 2D build.**
- **Stencil masks:** each mark is a pre-cut stencil mask, an SDF or a high-res alpha texture.
- **Spray shader** (CanvasItem): it takes the mask, a `reveal` sweep (a 0→1 band texture driven by an AnimationPlayer), a blue-noise speckle texture and a halo mask (the blurred SDF). It writes the core, edge build-up, overspray dots and mist, and a normal from the SDF gradient for the sheen.
- **Drips:** Line2D or a strip mesh per drip, with a glossy shader (rim, spec on the bulb). The length is tweened in steps with eased pauses for the crawl, from a seeded RNG stream for the view.
- **Solvent wipe:** a shader pass that offsets UVs along the wipe direction and multiplies by a streak texture behind a moving front. A few thin wet runs fall from the front.
- **Freehand lines:** baked strokes, revealed by arc length.
- **Posters:** baked textures (photocopy plus paper) with a separate flap sprite whose curl is a small skew/scale tween. The Heat number is re-rendered into the paste texture through a SubViewport so it stays live.

**Risks.**
- **Readability:** thin bridges and slices hurt legibility below about 40 px. Small text must drop the slice; I learned this from FLAGGED and BURN.
- **Pink on pink:** pink on the magenta Cv2 cards and banners can get lost, so the white key layer and black shadow are doing real work.
- **Cost:** speckle and halo are fill-rate heavy at 4K, so bake the static marks and animate only reveal and drips.
- **Wear:** the buff patches could feel heavy-handed if used often.
- **Portrait:** it is procedural, made of tonal shapes. A real art pass would want a proper illustrated or photo source run through the photocopy step.
- **Covered system words:** the bases have no "EXECUTE", "PURCHASE" or "EXIT".
  - **Combat:** the verb goes over the base's GO button, washed.
  - **Shop:** washed PURCHASE and EXIT buttons are drawn in the base UI style to cover the old stickers.

Scripts are in `scripts/` (Pillow and numpy, seeded). Run `python scripts/build_all.py`.
