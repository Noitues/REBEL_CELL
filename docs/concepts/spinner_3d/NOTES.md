# Spinner depth study (feedback item 4)

The same Breaker wheel (30 ticks, 10 slices, game slice colours, white glyphs with ink outlines, hub name, top needle, segmented HP arc, stickered bezel with a pink rim) is shown over the same dimmed, desaturated city in every image. Each technique is shown on its own first, then in combinations. Costs are for a 1080p combat screen with two to four wheels on a mid-range GPU.

| # | Technique | Build in Godot 4.7 | Runtime cost | Readability risk | Verdict |
|---|---|---|---|---|---|
| 1 | **Physical stack** (bezel above, slices sunk, glass dome) | Each wheel is a `Node2D` holding `Sprite2D` layers: slices, hub, bezel and dome. Shadows are the layer's own alpha, blurred once at import, drawn offset by a light vector (`CanvasItem` modulate black at 45%). The dome is a sprite with an additive highlight that stays still while the wheel turns. | Very low: 3–4 extra sprites per wheel. | Low. The shadow falls on the slice rim, not the glyphs. Keep the dome highlight small and on the upper-left rim, away from the glyph band. | **Yes. The cheapest large win.** |
| 2 | **Parallax** (layers slide with pointer/camera) | The same layers get a `depth` value, and a tiny script offsets `position = pointer_offset * k * depth`, with k about 6–10 px (or `Parallax2D` for the backdrop). Ease the pointer through a critically damped spring. Set it to 0 during resolution. | Negligible: position writes only. | Medium. Layers that move shift the pointer relative to the slices; if the needle drifts over a boundary, the read of "which slice" becomes ambiguous. Lock the needle and slices to the same depth while spinning, and let only the bezel, hub and dome float. Also needs an Options toggle (motion sensitivity). | Yes, subtle (≤ 8 px) and **frozen during spins**. |
| 3 | **Normal-lit 2D** (glows rake the bevels) | Use a `CanvasTexture` (diffuse + normal) on each layer. Normals are baked offline from the height maps (this study's `*_h.png`). `PointLight2D` nodes go on the neon signs, HQ glows, hit flashes, and the other wheel's rim. `Light2D` height is about 30 px for a grazing rake. | Low to medium: one pass per light per lit item in 2D. Cap it at 3–4 lights per wheel. | Low if the slice fills stay emissive (`unshaded` glow overlay) so a lamp can't darken the slice colour's meaning. Glyphs keep a white core at full brightness. | **Yes.** It ties the wheel to feedback 10 (light spill). |
| 4 | **Pre-rendered 3D** (machined bezel, recessed inlays, needle with counterweight) | Bake in Blender (or a `SubViewport` rendering real 3D at load time) into sprites: a static bezel, a hub, the needle in 3 tick poses, and a slice inlay **baked flat without the glyphs**. Glyphs and numbers are drawn live on top in 2D so they rotate crisply and can change per fight. With a camera tilt of 0–10° the rotating inlay stays correct. A `SubViewport` with live 3D can do real tilt but costs more. | Baked: the same as 1. Live `SubViewport`: one small 3D render per wheel, about 1–2 ms each. | Medium. Real metal speculars and deep recesses can bury slice colour; the brushed bezel competes with glyph whites. Keep the metal dark and the inlays emissive. | Yes, **baked**, for the bezel, hub and needle only. |
| 5 | **Motion depth** (needle tick with shadow, overshoot wobble, rim-weighted blur) | The wheel angle comes from the existing resolver timeline plus a cosmetic overshoot curve (a damped sine, never changing the result). The needle flap angle is derived from the distance to the next peg. The spin blur is a canvas shader on the slice layer that samples along the tangent, with strength ∝ radius × angular speed, so the hub and glyphs near the middle stay readable. The needle's shadow is a second sprite offset along the light vector. | Low: one 8–12-tap shader on one sprite per spinning wheel. | Low at rest (the blur is 0). The overshoot must not make the pointer visit a neighbour slice, so cap the wobble below the distance to the nearest boundary (the preview must equal the result: rule 6). | **Yes.** This is where "physical" is felt most. |
| 6 | 1+2+3 | As above, combined. | Low. | Medium: moving lights plus parallax can shimmer. | Good, all 2D. |
| 7 | 4+5 | Baked 3D sprites plus the motion shader. | Low. | Low to medium. | Good. |
| 8 | Everything (readable) | Baked bezel, hub and needle (4); live 2D slice layer + glyphs (crisp); drop shadows and dome (1); normal-lit bevels (3); ≤ 8 px parallax on bezel/dome only (2); tick, wobble, rim blur (5). | Low to medium (≈ 1 draw call per layer, 1 blur shader, ≤ 4 lights). | Managed by the rules below. | **Recommended target.** |

**Top recommendation: combination 8, delivered in two steps.** First ship 1 + 5 (stack shadows, dome, ticking needle, rim blur, wobble). It's all cheap 2D and gives most of the "physical wheel" feeling. Then add 3 (normal maps plus the scene's glow lights) and the baked 3D bezel/needle from 4. Keep 2 (parallax) small, and freeze it during spins.

**Readability rules for any of these:**
- glyphs and numbers are always a separate unlit layer (white core, ink outline) above every effect;
- no bloom threshold is ever reached by glyph white;
- specular highlights live only on the bezel or the dome rim;
- the backdrop stays at ≤ 45% brightness and 35% saturation;
- enemy ownership is shown by bezel shape (the notched edge), not colour alone.

**Blender notes for reuse:**
- coplanar alpha planes in EEVEE (dithered) hide each other, so offset them by ≥ 1 cm;
- a lathed open profile needs its point order reversed or the normals face in, which turns the glass black;
- `light.specular_factor = 0` on the key light stops a giant reflection on the dome;
- `to_track_quat` on a near-top-down camera rolls it, so build the camera basis by hand;
- set `keyframe_new_interpolation_type = 'LINEAR'` before keying, so the motion blur follows the real speed.

Scripts: `scripts/make_textures.py` → `t01`–`t09` (Blender, `-b --factory-startup --python`) → `compose.py`.
