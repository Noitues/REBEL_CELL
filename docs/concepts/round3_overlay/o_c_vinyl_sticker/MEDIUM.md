# o_c_vinyl_sticker: premium vinyl sticker bomb + paint pen

**The medium.** The Cell speaks through collectible-grade die-cut vinyl stickers slapped onto the screen. Each sticker has a thick white die-cut border, crisp vector print, a black keyline, a chunky extrude, a glossy specular band, a vinyl rim light and a soft contact shadow. Some corners curl back to show the matte adhesive side. There are four material grades:
- **Holographic foil** for verbs and the crew ID (SEND IT, BUY, LEAVE, VOSS).
- **Gloss white** for callouts and the Heat poster.
- **Matte kraft** tags for notes, written in black paint pen.
- **Clear vinyl** with white print (OURS).

A yellow Posca-style paint pen is used only for circles, arrows and two- or three-word shouts.

**Palette.** Vinyl white `#F6F3EC`, ink `#141118`, signal yellow `#FFDE1E` (and the pen `#FFE42E`), coral `#FF4656` for threats and flags, kraft `#B68E5C`, plus the holo foil (a pastel hue sweep over silver with a fine diffraction grating). The base has no outlines and is a dirty palette of faceted shapes. The overlay's keylines, white borders and gloss make it read as a different, physical material.

**Lettering.** Verbs and callouts use Anton (already in `assets/fonts`). Each glyph gets a seeded ±4° jitter and baseline wobble, a black keyline, an 8 px extrude, and a top bevel highlight. The whole word is then die-cut as one smooth blob (a dilate-then-erode "closing"). Pen words use Permanent Marker. System words stay in IBM Plex, tracked out and washed grey, so the human sticker is always visibly laid over the machine word.

**Why it reads AAA.** Every mark has real material response: light, gloss, thickness, a shadow and a lift. The marks are few: four or five per screen. They use one type family, one accent colour, and holo foil only for what matters. It sits in the same register as premium merch and Hi-Fi Rush / Persona-style UI stickers, without borrowing anyone's marks.

**Godot 2D build.**
- **Textures.** Each sticker is a pre-baked texture set: an albedo atlas of the print with its border, plus a mask texture. The mask uses R for the holo region, G for the die-cut alpha and B for gloss strength. A distance field of the die-cut edge drives the rim light.
- **Holo shader.** A CanvasItem shader does the foil: hue = f(UV, `TIME`, screen tilt or cursor offset), plus a grating texture and a specular band whose position is a uniform.
- **Corner curl shader.** The curl is a vertex/fragment fold. Pixels past a fold line are reflected across it and shaded with the backside colour. The fold distance is a uniform, used for the idle flutter (0.08↔0.19) and the peel (0 → 0.6).
- **Shadows.** One blurred alpha sprite per sticker, with offset and blur driven by "lift".
- **Animation.** The appear, idle and leave beats are tweens on scale, rotation, shadow lift and the gloss uniform. They fit the existing motion-helper rules: skippable, with short ones registered as passive.
- **Paint pen.** `Line2D` with round caps, a slight width curve and a 2 px drop shadow. Pen text uses pre-rendered sprites.

**Risks.**
- Holo can look cheap or rainbow-garish if it is overused. Keep it to verbs and IDs only.
- White borders are bright on a dark game. Too many stickers and the screen turns into a laptop lid, so cap the count per screen.
- Clear vinyl loses legibility over busy neon city blocks and may need a faint frost.
- Each new sticker is authored content, which costs more per item than marker text. Localised verbs need re-cut lettering.
- The peel's fold is a flat reflection. A real cylinder curl would need a mesh or a stronger shader to look right in motion.
