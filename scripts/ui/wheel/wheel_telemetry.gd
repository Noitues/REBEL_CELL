class_name WheelTelemetry
extends Node2D
## The telemetry ring (ART-2 2A; ART_BIBLE v2 3.2 "Telemetry ring (V2)"): class / corp telemetry
## written round the bezel's glass channel, scrolling slowly (`wheel_telemetry_scroll`, T0 ambient;
## still under reduce motion and reduce effects). It turns as a whole node (a Node2D: a Control
## redraws on every rotation change, ART-12 12p), so neither it nor the view redraws
## for it; the view's rail is drawn over it (static). Sits under the WheelView's own drawing.

## The ring's text radius (master units: the channel 368..404, the recipe's mid less 5).
const TEXT_R := 381.0
const TEXT_MASTER := 13.0
## The two thin hairlines inside the channel (frames.telemetry), master units.
const LINE_IN := 372.0
const LINE_OUT := 400.0

var text: String = ""
var accent: Color = Palette.CELL_PINK
var k: float = 1.0
var _turn: float = 0.0


func _init() -> void:
	show_behind_parent = true
	set_process(false)


## Places the ring on `center` (local to the parent) at `px_per_master`, with `p_text` in `p_accent`.
func setup(center: Vector2, px_per_master: float, p_text: String, p_accent: Color) -> void:
	position = center
	var changed := p_text != text or not is_equal_approx(px_per_master, k) or p_accent != accent
	k = px_per_master
	text = p_text
	accent = p_accent
	if changed:
		queue_redraw()
	set_process(visible and scrolls())


## Whether the ring scrolls now: its entry live (effects on, a real display) and motion allowed.
static func scrolls() -> bool:
	return Motion.live(&"wheel_telemetry_scroll") and Motion.parallax_allowed()


func _process(delta: float) -> void:
	if not scrolls():
		set_process(false)
		return
	_turn = fposmod(_turn + Motion.amplitude(&"wheel_telemetry_scroll") * delta, 360.0)
	rotation = deg_to_rad(_turn)


func _draw() -> void:
	if text == "":
		return
	var c := Vector2.ZERO
	var dim := Color(accent, 0.5)
	draw_arc(c, LINE_IN * k, 0.0, TAU, 96, dim, maxf(1.0, k))
	draw_arc(c, LINE_OUT * k, 0.0, TAU, 96, dim, maxf(1.0, k))
	var fs := roundi(TEXT_MASTER * k)
	if fs < WheelFace.MIN_TEXT_PX:
		WheelFace._dashes(self, c, k, TEXT_R, 0.0, 360.0, Color(accent, 0.8))
		return
	WheelFace._text_arc(self, c, k, TEXT_R, 0.0, 360.0, text, Palette.mono(), fs, Color(accent, 0.95))
