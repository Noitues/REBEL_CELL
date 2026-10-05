class_name RaidTerminal
extends TerminalWindow
## ART-6 3A: the Cell's own raid screens as CRT terminals (ART_BIBLE v2 §1.2 "CRT terminal",
## §4.8 YOUR NETWORK, IF PLACED, the Speed/Skip strip): navy glass, a cyan edge, the
## `> TITLE` header strip with its block cursor, a faint scrolling hex dump behind the rows
## and the shared CRT scanlines (UiTheme.crt_material). Ported from art-concepts-r43 round 19
## `ui19.terminal`. A TerminalWindow, so every terminal-window check and pad path still
## holds; seam: 1B's CRT terminal component replaces `_draw`'s dump and header.

const HEX_MOTION := &"raid_hex_scroll"
## The header strip's height (px at 1.0) and the cursor block's size.
const HEAD_H := 34.0
const CURSOR := Vector2(8, 10)
## The hex dump: line pitch (px at 1.0), bytes per line and its alpha.
const HEX_PITCH := 12.0
const HEX_BYTES := 24
const HEX_ALPHA := 0.16

var _t: float = 0.0
var _seed: int = 1


func _init(p_title: String = "", p_accent: Color = Palette.NET_CYAN) -> void:
	super._init("> " + p_title, p_accent)
	_seed = absi(hash(p_title)) % 997 + 1
	var head := find_child("TerminalTitle", true, false) as Label
	if head != null:
		head.add_theme_color_override("font_color", p_accent)
		head.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.BODY))
	# The terminal has a header strip, not the zine's pink underline.
	var outer := get_child(0) if get_child_count() > 0 else null
	if outer != null and outer.get_child_count() > 1 and outer.get_child(1) is ColorRect:
		(outer.get_child(1) as ColorRect).color = Color(p_accent, 0.0)
		(outer.get_child(1) as ColorRect).custom_minimum_size.y = 1


func _process(delta: float) -> void:
	if Motion.live(HEX_MOTION) and is_visible_in_tree():
		_t += delta
		queue_redraw()


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	var k := Settings.text_scale
	# The faint hex dump scrolling up behind the rows.
	var mono := Palette.mono()
	var px := UiTheme.font_px(UiTheme.CAPTION)
	var pitch := HEX_PITCH * k
	var speed := Motion.amplitude(HEX_MOTION) if Motion.live(HEX_MOTION) else 0.0
	var scroll := fposmod(_t * speed, pitch)
	var first := int(floorf(_t * speed / pitch))
	var y := HEAD_H * k + pitch - scroll
	var line := 0
	while y < r.size.y - 4.0:
		var bytes := PackedStringArray()
		for b in HEX_BYTES:
			bytes.append("%02X" % int((RaidPencil.noise(_seed, (first + line) * HEX_BYTES + b) * 0.5 + 0.5) * 255.0))
		draw_string(mono, Vector2(6.0 * k, y), " ".join(bytes), HORIZONTAL_ALIGNMENT_LEFT, r.size.x - 12.0 * k, px, Color(accent, HEX_ALPHA))
		y += pitch
		line += 1
	# The header strip and its block cursor.
	draw_rect(Rect2(1, 1, r.size.x - 2, HEAD_H * k), Color(accent, 0.12))
	draw_rect(Rect2(r.size.x - (CURSOR.x + 8.0) * k, (HEAD_H - CURSOR.y) * 0.5 * k, CURSOR.x * k, CURSOR.y * k), accent)
	super._draw()
