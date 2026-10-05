class_name FirmwareSocket
extends RefCounted
## The socketed firmware die (ART_BIBLE v2 §3.9, round 34 `firmware_socket.png`). The die is the art
## pass's own: `assets/wheel/firmware/die_<rarity>.png` exported by `tools/art/export_firmware_daemons.py`
## from the round 34 generator (`fwlib.put_chip`: socket recess with its rarity lip, faceted body, gold
## pin comb, DIP notch, rarity LED and pips), and `die_<rarity>_lit.png`, the same with the trigger
## flare. The view rotates it pins-in, cross-fades to the lit image for a flash and stamps 1C's atlas
## glyph upright on it, as `put_chip` does. Small dies (below SIMPLE_BELOW px) carry no glyph.
## Drawing only.

## Below this chip width (px) the die drops its glyph (§3.9: "Below r = 150"; `put_chip`: s < 20 at 1x).
const SIMPLE_BELOW := 14.0
## The exported die: the chip's width in the image (px) and the glyph's size and lift (share of the
## chip width, `put_chip`: gs = 0.50 s, lifted 0.04 s).
const DIE_PX := 128.0
const GLYPH := 0.5
const GLYPH_LIFT := 0.04
const DIES: Array[Texture2D] = [preload("res://assets/wheel/firmware/die_common.png"),
	preload("res://assets/wheel/firmware/die_uncommon.png"), preload("res://assets/wheel/firmware/die_rare.png"),
	preload("res://assets/wheel/firmware/die_boss.png")]
const LIT: Array[Texture2D] = [preload("res://assets/wheel/firmware/die_common_lit.png"),
	preload("res://assets/wheel/firmware/die_uncommon_lit.png"), preload("res://assets/wheel/firmware/die_rare_lit.png"),
	preload("res://assets/wheel/firmware/die_boss_lit.png")]


## Draws the die of `fw` at `at` (local to `ci`), `size` px wide, its pins toward `core`.
## The effect glyph goes on `glyphs` (1C's atlas). `flash` (0..1) cross-fades to the lit die (the
## trigger cue's FLARE, ART-3).
static func draw_die(ci: CanvasItem, glyphs: GlyphBatch, at: Vector2, size: float, core: Vector2, fw: FirmwareData, flash: float = 0.0) -> void:
	var inward := (core - at).normalized() if core != at else Vector2.DOWN
	var theta := atan2(-inward.x, inward.y)  # local +y points at the core
	var rarity := clampi(fw.rarity if fw != null else RC.Rarity.COMMON, 0, DIES.size() - 1)
	# The image has its pins on the top edge: turned half a turn more, they face the core.
	ci.draw_set_transform(at, theta + PI, Vector2.ONE)
	var tex := DIES[rarity]
	var sz := tex.get_size() * (size / DIE_PX)
	var rect := Rect2(-sz * 0.5, sz)
	if flash < 1.0:
		ci.draw_texture_rect(tex, rect, false)
	if flash > 0.0:
		ci.draw_texture_rect(LIT[rarity], rect, false, Color(Color.WHITE, flash))
	ci.draw_set_transform(Vector2.ZERO)
	if size >= SIMPLE_BELOW and fw != null:
		var g := AttachStyle.firmware_glyph(fw.id)
		var gat := at + Vector2(0.0, -size * GLYPH_LIFT)
		if glyphs != null and GlyphBatch.has_glyph(g):
			glyphs.add(g, gat, size * GLYPH)
		else:
			AttachStyle.draw_firmware_glyph(ci, fw.id, gat, size * GLYPH * 0.5, Palette.TEXT_HI)


## The die's texture for `rarity` (lit: the trigger flare), for tests and labs.
static func die_texture(rarity: int, lit: bool = false) -> Texture2D:
	var k := clampi(rarity, 0, DIES.size() - 1)
	return LIT[k] if lit else DIES[k]
