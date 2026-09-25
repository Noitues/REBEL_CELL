class_name DripButton
extends Button
## Words in dripping marker (the Cell's voice) that still press like a button: no box,
## no circle, just the tag. Drips hang from chosen letters (`drips`), attached to the
## letter's bottom edge: thick where they leave the letter, thin through the middle, a
## round raindrop at the end. An optional key hint sits underneath in system mono.
## Hover/focus brighten the paint and add a halo so pad and mouse players see it.

## Hot pink of the combat concepts (DECK & TONEARM).
const DRIP_PINK := Color("#FF3DA8")
## Drip presets: long -> short, left to right.
const SEND_IT_DRIPS := [[0, 44, 0.3], [2, 28, 0.88], [6, 14, 0.5]]
const LEAVE_MODEM_DRIPS := [[0, 42, 0.25], [7, 26, 0.85], [10, 14, 0.2]]

var tag_text: String = ""
var key_hint: String = ""
var paint: Color = DRIP_PINK
var font_size: int = 44
## Each drip: [letter index, length (px at size 44, scales with size), anchor 0-1 across
## the letter's width].
var drips: Array = []
var _hot: bool = false


func _init(p_text: String = "SEND IT", p_hint: String = "", p_color: Color = DRIP_PINK, p_size: int = 44, p_drips: Array = []) -> void:
	tag_text = p_text
	key_hint = p_hint
	paint = p_color
	font_size = p_size
	drips = p_drips
	flat = true
	focus_mode = Control.FOCUS_ALL
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	var longest := 0.0
	for d in drips:
		longest = maxf(longest, float(d[1]))
	var w := Palette.marker().get_string_size(tag_text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x
	custom_minimum_size = Vector2(w + 24, font_size * 1.05 + longest * font_size / 44.0 + 14 + (18 if key_hint != "" else 0))
	mouse_entered.connect(func() -> void: _hot = true; queue_redraw())
	mouse_exited.connect(func() -> void: _hot = false; queue_redraw())
	focus_entered.connect(func() -> void: _hot = true; queue_redraw())
	focus_exited.connect(func() -> void: _hot = false; queue_redraw())


## Draws `text` with drips on any CanvasItem at baseline `base` (shared with views that
## paint the lettering themselves).
static func draw_drip_text(ci: CanvasItem, base: Vector2, text: String, size: int, col: Color, p_drips: Array, shadow: bool = true) -> void:
	var f := Palette.marker()
	if shadow:
		ci.draw_string(f, base + Vector2(3, 3), text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color(0, 0, 0, 0.7))
	ci.draw_string(f, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, col)
	var scale := size / 44.0
	for d in p_drips:
		var idx: int = d[0]
		if idx < 0 or idx >= text.length():
			continue
		var x0 := f.get_string_size(text.substr(0, idx), HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
		var cw := f.get_string_size(text[idx], HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
		var x := base.x + x0 + cw * float(d[2])
		# Start inside the letter's bottom stroke so the drip is attached to it.
		var top := base.y - size * 0.12
		_drip(ci, Vector2(x, top), float(d[1]) * scale + size * 0.12, maxf(3.5, 9.5 * scale), col)


## One drip: thick at the top, a thin neck, a round raindrop at the end.
static func _drip(ci: CanvasItem, top: Vector2, length: float, w: float, col: Color) -> void:
	var neck := w * 0.42
	var bulb := w * 0.78
	var end := top + Vector2(0, length)
	var pts := PackedVector2Array()
	var steps := 10
	for k in steps + 1:
		var t := float(k) / steps
		# Width: wide at the top, pinching to the neck by 40%, holding thin to the bulb.
		var hw := lerpf(w * 0.5, neck * 0.5, smoothstep(0.0, 0.4, t))
		pts.append(top + Vector2(hw, t * (length - bulb)))
	for k in range(steps, -1, -1):
		var t := float(k) / steps
		var hw := lerpf(w * 0.5, neck * 0.5, smoothstep(0.0, 0.4, t))
		pts.append(top + Vector2(-hw, t * (length - bulb)))
	# Flare into the letter at the top so the join reads as paint, not a stick.
	ci.draw_colored_polygon(PackedVector2Array([top + Vector2(-w * 0.9, -w * 0.2), top + Vector2(w * 0.9, -w * 0.2), top + Vector2(w * 0.5, w * 0.6), top + Vector2(-w * 0.5, w * 0.6)]), col)
	ci.draw_colored_polygon(pts, col)
	# Raindrop: a circle with a soft point up into the neck.
	var c := end - Vector2(0, bulb)
	ci.draw_colored_polygon(PackedVector2Array([c + Vector2(-bulb * 0.55, -bulb * 0.2), c + Vector2(0, -bulb * 1.6), c + Vector2(bulb * 0.55, -bulb * 0.2)]), col)
	ci.draw_circle(c, bulb, col)
	ci.draw_circle(c + Vector2(-bulb * 0.3, -bulb * 0.3), bulb * 0.22, Color(1, 1, 1, 0.35))


func _draw() -> void:
	var col := paint if not disabled else Color(paint, 0.35)
	if _hot and not disabled:
		col = paint.lightened(0.2)
	var base := Vector2(12, font_size * 1.0)
	if _hot and not disabled:
		for k in 6:
			draw_string(Palette.marker(), base + Vector2(k - 3, (k * 7) % 5 - 2), tag_text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, Color(Palette.CELL_ACID, 0.12))
	DripButton.draw_drip_text(self, base, tag_text, font_size, col, drips)
	if key_hint != "":
		draw_string(Palette.mono(), Vector2(14, size.y - 6), key_hint, HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color(Palette.PAPER, 0.75))
