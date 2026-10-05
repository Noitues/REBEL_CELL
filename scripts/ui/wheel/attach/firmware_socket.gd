class_name FirmwareSocket
extends RefCounted
## The socketed firmware die (ART_BIBLE v2 §3.9, round 34 `firmware_socket.png`): a faceted
## octagonal die, 3-tone facets, a gold pin comb on the edge facing the core, a DIP notch opposite,
## an LED and a lip in the rarity colour, 1-3 white rarity pips, the effect glyph upright on the dark
## top plate. Small dies (below SIMPLE_BELOW px) keep the die, LED, pins and lip only. Drawing only.

## Below this chip width (px) the die drops its glyph and pips (§3.9: "Below r = 150").
const SIMPLE_BELOW := 14.0
## Octagon corner cut (share of the half size), top plate (share), lip growth (share).
const CORNER := 0.38
const PLATE := 0.7
const LIP := 1.14
## Pin comb: pins, their length and width (share of the half size).
const PINS := 5
const PIN_LEN := 0.34
const PIN_W := 0.11
## The notch radius, LED radius and pip radius (share of the half size).
const NOTCH := 0.16
const LED := 0.13
const PIP := 0.07
## The LED's glow ring (times its radius) and alpha.
const LED_GLOW := 2.2
const LED_GLOW_ALPHA := 0.35
## The effect glyph's size (share of the half size).
const GLYPH := 0.46
## Facet shading.
const FACET_LIGHT := 0.28
const FACET_DARK := 0.35


## Draws the die of `fw` at `at` (local to `ci`), `size` px wide, its pins toward `core`.
## `flash` (0..1) lights LED, lip and pins in the rarity colour (the trigger cue's FLARE, ART-3).
static func draw_die(ci: CanvasItem, at: Vector2, size: float, core: Vector2, fw: FirmwareData, flash: float = 0.0) -> void:
	var h := size * 0.5
	var inward := (core - at).normalized() if core != at else Vector2.DOWN
	var theta := atan2(-inward.x, inward.y)  # local +y (the pins) points at the core
	var rare := AttachStyle.rarity_color(fw.rarity if fw != null else RC.Rarity.COMMON)
	var simple := size < SIMPLE_BELOW
	ci.draw_set_transform(at, theta, Vector2.ONE)
	# Pins first: they run under the die's edge into the core side.
	var pin_col := Palette.RESIST_GOLD.lerp(rare, flash)
	for k in PINS:
		var x := lerpf(-h * 0.6, h * 0.6, float(k) / (PINS - 1))
		ci.draw_rect(Rect2(Vector2(x - h * PIN_W * 0.5, h * 0.62), Vector2(h * PIN_W, h * (0.38 + PIN_LEN))), pin_col)
	# Lip (rarity), body (gunmetal), facets, top plate.
	ci.draw_colored_polygon(octagon(h * LIP), Color(rare, 0.75 + 0.25 * flash))
	ci.draw_colored_polygon(octagon(h), Palette.DESK_METAL)
	var o := octagon(h)
	var p := octagon(h * PLATE)
	for k in 8:
		var quad := PackedVector2Array([o[k], o[(k + 1) % 8], p[(k + 1) % 8], p[k]])
		var lit := (o[k] + o[(k + 1) % 8]).normalized().dot(Vector2(-0.6, -0.8))
		var face := Palette.DESK_METAL.lightened(FACET_LIGHT * maxf(lit, 0.0)).darkened(FACET_DARK * maxf(-lit, 0.0))
		ci.draw_colored_polygon(quad, face)
	ci.draw_colored_polygon(p, Palette.DESK_DARK)
	ci.draw_polyline(_closed(o), Color(Palette.INK, 0.8), maxf(1.0, h * 0.06), true)
	# DIP notch on the outer edge.
	ci.draw_circle(Vector2(0, -h * 0.98), h * NOTCH, Palette.DESK_DARK)
	# LED (rarity) in the outer corner.
	var led_at := Vector2(h * 0.48, -h * 0.48)
	ci.draw_circle(led_at, h * LED * LED_GLOW, Color(rare, LED_GLOW_ALPHA * (0.6 + 0.4 * flash)))
	ci.draw_circle(led_at, h * LED, rare.lightened(0.3 * flash))
	if not simple and fw != null:
		var pips := AttachStyle.rarity_pips(fw.rarity)
		for k in pips:
			ci.draw_circle(Vector2((k - (pips - 1) * 0.5) * h * 0.24, -h * 0.55), h * PIP, Palette.TEXT_HI)
	ci.draw_set_transform(Vector2.ZERO)
	if not simple and fw != null:
		AttachStyle.draw_firmware_glyph(ci, fw.id, at + inward * h * 0.08, h * GLYPH, Palette.TEXT_HI)


## A regular-ish octagon of half size `h` (corners cut by CORNER), centred on the origin.
static func octagon(h: float) -> PackedVector2Array:
	var c := h * CORNER
	return PackedVector2Array([Vector2(-h + c, -h), Vector2(h - c, -h), Vector2(h, -h + c), Vector2(h, h - c),
		Vector2(h - c, h), Vector2(-h + c, h), Vector2(-h, h - c), Vector2(-h, -h + c)])


static func _closed(pts: PackedVector2Array) -> PackedVector2Array:
	var out := pts.duplicate()
	out.append(pts[0])
	return out
