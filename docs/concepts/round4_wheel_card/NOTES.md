# Round 4: wheel and card versions (Cv2 base, sticker overlay)

Everything is built in Pillow from seeded scripts. Run `scripts/wheels.py`, `scripts/cards.py`, `scripts/mockups.py` and `scripts/compare.py` to rebuild.

All wheels share these rules:
- **Glyphs:** flat silhouettes (blade, shield, hex, chevrons, cross, drop, drone, slashed ring), so slice type reads in greyscale by shape.
- **Pointer read first:** the active slice is always marked twice, by geometry (lift, size or ring offset) and by a pointer or hub readout of its value.
- **Status marks:** the CORRUPTED mark is glitch shards plus a violet broken-square badge.
- **Owners:** the player wheel has a hazard-striped rim, the enemy wheel has Meridian orange container ribs, and the boss wheel has a red spiked rim.

## Wheels

**W-A: salvaged faceted.**
- **Strengths:** the strongest under-pointer read. The active slice is lifted, brightened and outlined in cream. The notched blade pointer carries the value in its own window, so "6" can be read twice. The calm 2-band slice fill keeps Anton values large (r×0.19). It is clearly the Cv2 wheel, gritty and hazard-striped.
- **At r=60:** the best of the four. The values stay legible (about 12 px), the lifted slice still pops, and the pointer value window is about 7 px, decorative only.
- **Greyscale:** good. The glyphs and the lift carry it.
- **Godot:** the wheel is a `Node2D`. Each slice is a `Polygon2D` fan with a baked facet vertex-colour, plus a `Label`/glyph sprite. The active slice gets a tweened radial offset, a `Line2D` outline and a modulate boost. The rim and pointer are static textures, and the pointer value is a `Label`.

**W-B: instrument dial.**
- **Strengths:** precise and calm, the least toy-like. The hub screen ("ATK 6") is a second, unambiguous readout. The printed ticks and numerals make the 30-tick logic visible, which is useful for nudge and spin cards.
- **At r=60:** weak. The badges shrink to about 9 px and the numerals and screen text disappear. Only the colour band under the needle reads.
- **Greyscale:** the thin colour bands lose their meaning, so the badges carry it.
- **Godot:** the bands are `Line2D` arcs or a ring shader with per-slice colour uniforms. The badges are sprites, the needle is a rotated `Sprite2D`, and the hub screen is a `Label` with a mono font. This is the cheapest version to animate.

**W-C: layered physical stack.**
- **Strengths:** the most tactile and "hero hardware". The chips cast shadows on the disc, the bezel shadows the slices, and there is a glass sheen and a needle with a counterweight. Values sit on raised chips with their glyphs.
- **At r=60:** the chips become 4 px labels and the pie colours dominate. The active slice is only marked by the needle.
- **Greyscale:** the colours merge. The chips still read at hero size.
- **Godot:** build it as layered `Sprite2D`s/`Polygon2D`s, with `CanvasGroup` drop shadows (offset blurred alpha). The glass is an additive texture. Parallax-offset the layers by a few px while spinning to sell the depth.

**W-D: segmented ring with sticker values.**
- **Strengths:** the open centre gives the hub a big HP number (36) and a free inner ring. Sticker values tie the wheel to the overlay language. The "NOW" sticker arrow is unmistakable, and the active segment is thicker and outlined.
- **At r=60:** the stickers become about 20 px tiles with unreadable values. The NOW arrow and the HP number survive.
- **Greyscale:** fine. The glyphs are printed on the stickers.
- **Godot:** the ring is `Polygon2D` segments. The stickers are pre-baked textures (from the round-3 sticker pipeline) parented to segments, with counter-rotation optional. The NOW tab is one sticker sprite with an idle wobble tween.

## Cards

**C-A: faceted print.**
- **Strengths:** the most readable at hand size. It has a full-width type band, a large pictogram row (about 22 px tall at 112×148), a rarity edge plus corner flag, and the cost gem. It is the closest to the current game.
- **Weak spots:** Common and Uncommon are told apart only by edge colour (steel vs cyan), so the rarity word helps.
- **Godot:** a `PanelContainer` with a 9-slice paper texture, a faceted art `TextureRect`, and `HBoxContainer` pictogram icons. The edge colour is a shader parameter.

**C-B: data chip.**
- **Strengths:** a strong physical identity. The shell colour gives the type at a glance, the LED shows cost, and the contact edge reads as "plug it in". Matte, clear and holo shells show rarity well.
- **Weak spots:** at hand size the label window carries everything, and the type text is tiny (shell colour does that job).
- **Godot:** one shell texture per type, the label as a child panel, and the LED as an emissive sprite. Holo and clear are a CanvasItem shader (shared with the sticker holo).

**C-C: sticker card.**
- **Strengths:** this unifies cards with the overlay. White die-cut, gloss band, holo border for Rare, and a peel curl on hover. The yellow cost dot reads best of the four at hand size, and the "peel and slap on the wheel" motion is free storytelling. Can't-afford greys the dot and adds a marker NEED tag.
- **Weak spots:** a lot of white in a hand of 6–8 cards. Use a thinner border at hand size (already about 5 px).
- **Godot:** reuse the round-3 sticker pipeline (baked albedo + mask, holo shader, curl shader). Play is a peel tween, then flight, then a "slap" scale-squash onto the target wheel.

**C-D: terminal card.**
- **Strengths:** the most "system". It has a neon edge in the type colour, a monospace title, crisp pictograms in the type colour, and scanline art. Rarity is shown by edge treatment: single edge, double edge, then double edge with gold corners.
- **Weak spots:** at hand size the mono title is about 7 px and the dark glass blends into the dark combat backdrop. Greyscale loses the type-colour coding.
- **Godot:** a `Panel` with a `StyleBoxFlat` (dark, alpha 0.92) and an emissive border shader, a `Label` in Share Tech Mono, and a scanline overlay shader on the art.

## Mockups
- `mockup_1.png`: W-A + C-C, my best pairing.
- `mockup_2.png`: W-D + C-D, the second pairing. It is the cleanest centre, but the most "UI-panel" look.

## Recommendation
- **Wheel:** W-A, salvaged faceted, as the shipping wheel. It wins on the one test that matters: the slice under the pointer and its value read instantly at r=200 and are still readable at r=60 and in greyscale.
- **Borrow from W-B** the hub readout ("ATK 6") for accessibility.
- **Borrow from W-D** the HP number in the hub for multi-enemy small wheels.
- **Card:** C-C, the sticker card. It has the best hand-size cost read, it unifies with the locked sticker overlay, and the peel-and-slap play animation explains what a card does to a wheel.
- **Fallback card:** C-A, if the white borders prove too loud in an 8-card hand.
