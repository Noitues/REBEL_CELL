# o_d_light_pen: AR light-pen / light painting

**Medium.** The Cell writes on the world in hand-drawn light, like a long-exposure light painting or an AR stylus. Each mark is simulated as a moving pen. It slows into corners and at the ends, so slow parts come out thick and hot and fast runs come out thin. Every stroke has a white-hot core, a coloured body with faint wand "bristle" streaks, a soft halo, a 2 px chromatic fringe (red one side, blue the other) and an afterglow ghost. Where the pen lifts, the tail goes dry and throws a few sparks. Each mark also casts light onto the Cv2 facets beneath it: a big soft light map multiplies the base, so the button, the wheel slice and the buildings visibly pick up pink.

**Palette.** Hot pink `#FF2299` is the signature, used for every verb and every target. Cyan `#4CDBFF` appears only twice: friendly marks (OURS, price tags) and the crew hologram. A cool white is used for the small tactical note. Nothing else.

**Lettering.** A custom single-line stroke alphabet: italic, about 0.3 slant, with per-letter jitter, gestural overshoot flicks and a calligraphic nib factor. It is not a font, so no two letters render the same. Big verbs are about 85–100 px tall. Notes are about 23 px.

**Why it reads as AAA.** It is one coherent light model, not stickers. The base is flat and hard-edged, while the overlay is emissive, soft and in motion, so the two layers never blur together. Light falling on the world sells that the overlay is *there*.

**Godot 2D build.**
- **Strokes.** Author them as `Line2D`/`Curve2D` point lists with per-point width (a `Curve` driven by recorded pen speed). Alternatively, bake an SDF ribbon to a texture. Write-on is `points` revealed by time; the pen head is a `GPUParticles2D` emitter with a star-flare sprite.
- **Shader.** One `canvas_item` shader does it all. It reads core and halo from the distance to the ribbon centre, scrolls a noise UV for flicker and the travelling idle highlight, and offsets R/B samples for the fringe. Use additive blend.
- **Glow and projected light.**
  - The glow is a `WorldEnvironment` 2D glow pass (HDR 2D), or a cheap blurred copy of the stroke layer.
  - The projected light is a `PointLight2D`/`TextureLight2D` per mark, using the blurred stroke as its texture, so the base facets really get lit.
- **Exit.** A dissolve threshold over noise plus an x-sweep, with `GPUParticles2D` emitting from the stroke mask and drifting upward.
- **Crew card.** A `SubViewport` portrait with a scanline/RGB-split shader, framed by stroke brackets.

**Risks.**
- **Neon-sign read.** At small sizes it can look like neon tubes rather than a brush. The calligraphic contrast has to be guarded, with thick slow corners and dry tails.
- **Over bright faces.** Overlay over bright faces (the pink wheel slice) loses contrast. Every mark needs its dark veil.
- **Cost and repetition.**
  - Full-screen glow and lighting cost fill-rate on low-end hardware.
  - Writing by hand needs authored stroke data per word, or a stroke font plus jitter, as done here.
  - Too many marks turn the screen into a light show, so cap it at about 5 per screen.
