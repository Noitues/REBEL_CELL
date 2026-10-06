class_name CrtHum
extends Control
## The deck screen's hum (Animation pass ANIM-6, ANIMATION_HANDOFF 4.13): a faint bright band
## rolls down the glass once per `hq_crt_hum` period and the glass brightens by the entry's
## amplitude as it passes, like a CRT's mains hum. Added over a terminal window's content
## (`attach`); idle motion only, off under reduce effects and headless (not added). Draws
## only; clicks pass through.

## The band's height as a share of the screen's.
const BAND_SHARE := 0.18
const NODE_NAME := "CrtHum"

var _t: float = 0.0


## Hums `window` (the HQ's deck monitor); returns the hum, or null when it doesn't play.
static func attach(window: Control) -> CrtHum:
	if not Motion.live(&"hq_crt_hum"):
		return null
	var old := window.get_node_or_null(NodePath(NODE_NAME)) as CrtHum
	if old != null:
		return old
	var h := CrtHum.new()
	h.name = NODE_NAME
	h.mouse_filter = Control.MOUSE_FILTER_IGNORE
	h.focus_mode = Control.FOCUS_NONE
	window.add_child(h)
	return h


func _process(delta: float) -> void:
	if not Motion.live(&"hq_crt_hum"):
		visible = false
		return
	visible = true
	_t += delta
	queue_redraw()


func _draw() -> void:
	var period := maxf(0.1, Motion.entry(&"hq_crt_hum").duration)
	var k := fmod(_t, period) / period
	var amp := Motion.amplitude(&"hq_crt_hum")
	var band := size.y * BAND_SHARE
	var y := lerpf(-band, size.y, k)
	var r := Rect2(0.0, y, size.x, band).intersection(Rect2(Vector2.ZERO, size))
	if r.has_area():
		draw_rect(r, Color(PaletteSkins.chrome(Palette.NET_CYAN), amp))
	# The whole glass swells a touch as the band crosses its middle.
	draw_rect(Rect2(Vector2.ZERO, size), Color(Palette.PAPER, amp * 0.25 * sin(PI * k)))
