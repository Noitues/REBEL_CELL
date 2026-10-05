class_name ToonInkMaterial
extends RefCounted
## The cel / toon + ink material for the 3D world (ART-1 1B; ART_BIBLE v2 §1.2 "World", §6.1):
## a 3-band toon ramp with per-triangle tone jitter, grime, banded light spill and depth haze
## (`shaders/kit/toon_ink.gdshader`) and an inverted-hull ink line as its next pass
## (`shaders/kit/toon_ink_hull.gdshader`). Area 1D (the city spike) owns the city and uses
## this shared material; props, busts and HQs use it too. Builders only; a view.

const TOON := preload("res://shaders/kit/toon_ink.gdshader")
const HULL := preload("res://shaders/kit/toon_ink_hull.gdshader")
## The three bands (round 2 E cel: lit / mid / shadow).
const BAND_HI := 0.55
const BAND_LO := 0.12
const SHADE_MID := 0.62
const SHADE_LOW := 0.32
## Ink line width (screen px) and its wobble.
const INK_PX := 2.5
const INK_WOBBLE := 0.35


## A toon material in `albedo` with the ink hull as its next pass (`ink_px` 0: no ink).
static func make(albedo: Color, ink_px: float = INK_PX) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = TOON
	m.set_shader_parameter(&"albedo", albedo)
	m.set_shader_parameter(&"band_hi", BAND_HI)
	m.set_shader_parameter(&"band_lo", BAND_LO)
	m.set_shader_parameter(&"shade_mid", SHADE_MID)
	m.set_shader_parameter(&"shade_low", SHADE_LOW)
	m.set_shader_parameter(&"shadow_tint", Palette.NEON_VIOLET.darkened(0.7))
	m.set_shader_parameter(&"haze_color", Palette.NIGHT_BLOCK)
	if ink_px > 0.0:
		m.next_pass = ink(ink_px)
	return m


## The ink hull pass on its own (`width_px` screen px).
static func ink(width_px: float = INK_PX) -> ShaderMaterial:
	var h := ShaderMaterial.new()
	h.shader = HULL
	h.set_shader_parameter(&"ink", Palette.TOON_INK)
	h.set_shader_parameter(&"width_px", width_px)
	h.set_shader_parameter(&"wobble", INK_WOBBLE)
	return h


## Sets `m`'s light spill sources (LightSpill.uniforms_3d's input).
static func set_spill(m: ShaderMaterial, sources: Array) -> void:
	var u := LightSpill.uniforms_3d(sources)
	for k in u:
		m.set_shader_parameter(StringName(k), u[k])


## The band a lit share falls in (0 shadow, 1 mid, 2 lit): the shader's ramp, for tests.
static func band_of(ndl: float) -> int:
	if ndl > BAND_HI:
		return 2
	if ndl > BAND_LO:
		return 1
	return 0
