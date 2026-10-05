class_name HeatGlitchPreview
extends Control
## ART-10 4C: the HEAT GLITCH preview in Options (ART_BIBLE v2 §4.13, §5.5; round 31
## `settings_menu.jpg` "HEAT GLITCH PREVIEW (HUNTED, 82)"): two small terminal frames side by
## side, each a drawn wheel over the city line. ON: the slip and split (the wheel's slices
## shifted in bands, a pink / green fringe); OFF: the static corp edge tint only. The frame
## that matches the setting is outlined in cyan; under the flash limiter or reduce effects
## the ON frame reads LIMITED (tears only at NOTICED strength). It draws a still: the
## motion itself belongs to the Heat glitch layer. View only.

## One frame's size (px at 1280x720) and the gap between the two.
const FRAME := Vector2(200, 92)
const GAP := 12.0
## The drawn wheel's radius (share of the frame's height) and its slices.
const WHEEL_SHARE := 0.36
const SLICES := 6
## The ON frame's band slip (px) and fringe split (px).
const SLIP := 6.0
const SPLIT := 2.5
## The OFF frame's edge tint width (px).
const TINT_W := 6.0
const CAPTION_STEP := UiTheme.CAPTION


func _init() -> void:
	name = "HeatGlitchPreview"
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _ready() -> void:
	Settings.changed.connect(_changed)


func _exit_tree() -> void:
	if Settings.changed.is_connected(_changed):
		Settings.changed.disconnect(_changed)


func _changed() -> void:
	update_minimum_size()
	queue_redraw()


## True when the glitch is held to its limited form (flash limiter or reduce effects).
static func limited() -> bool:
	return Settings.flash_limiter or Settings.reduce_effects


func _get_minimum_size() -> Vector2:
	var cp := Chrome.px(CAPTION_STEP)
	return Vector2(FRAME.x * 2.0 + GAP, FRAME.y + Palette.mono().get_height(cp) + 6.0)


func _draw() -> void:
	var f := Palette.mono()
	var cp := Chrome.px(CAPTION_STEP)
	for i in 2:
		var on := i == 0
		var r := Rect2(Vector2(i * (FRAME.x + GAP), 0), FRAME)
		draw_rect(r, Palette.NIGHT_SKY)
		# The city line under the wheel.
		for k in 9:
			var bx := r.position.x + 6.0 + k * (FRAME.x - 12.0) / 9.0
			var bh := FRAME.y * (0.18 + 0.05 * float((k * 7) % 5))
			draw_rect(Rect2(Vector2(bx, r.end.y - bh), Vector2((FRAME.x - 12.0) / 9.0 - 2.0, bh)), Palette.NIGHT_BLOCK_LIT)
		var c := r.position + Vector2(FRAME.x * 0.62, FRAME.y * 0.5)
		var rad := FRAME.y * WHEEL_SHARE
		if on:
			_wheel(c + Vector2(-SPLIT, 0), rad, Color(Palette.CELL_PINK, 0.7), 0.0)
			_wheel(c + Vector2(SPLIT, 0), rad, Color(Palette.CORP_SOLACE, 0.7), 0.0)
			for b in 3:
				var y := c.y - rad + b * rad * 0.7
				draw_rect(Rect2(Vector2(r.position.x, y), Vector2(FRAME.x, 3.0)), Color(Palette.HARM, 0.35))
			_wheel(c, rad, Palette.TEXT_HI, SLIP)
		else:
			_wheel(c, rad, Palette.TEXT_HI, 0.0)
			draw_rect(r.grow(-TINT_W * 0.5), Color(Palette.HARM, 0.55), false, TINT_W)
		var chosen := Settings.heat_glitch == on
		draw_rect(r, Palette.NET_CYAN if chosen else Color(Palette.NET_CYAN, 0.3), false, 2.0 if chosen else 1.0)
		var words := (tr("LIMITED // slow layer only") if limited() else tr("ON // slip + split")) if on else tr("OFF // static edge tint")
		draw_string(f, Vector2(r.position.x, r.end.y + 4.0 + f.get_ascent(cp)), words, HORIZONTAL_ALIGNMENT_LEFT, FRAME.x, cp,
			Palette.NET_CYAN if chosen else Palette.TEXT_LO)


## A plain wheel: its rim and slice spokes; `slip` shifts its lower half sideways.
func _wheel(c: Vector2, rad: float, col: Color, slip: float) -> void:
	draw_arc(c, rad, 0.0, TAU, 32, col, 2.0, true)
	draw_arc(c, rad * 0.35, 0.0, TAU, 16, col, 1.5, true)
	for k in SLICES:
		var a := TAU * float(k) / SLICES
		var d := Vector2(cos(a), sin(a))
		var shift := Vector2(slip, 0) if d.y > 0.0 else Vector2.ZERO
		draw_line(c + d * rad * 0.35 + shift, c + d * rad + shift, col, 1.5)
