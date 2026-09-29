class_name LogoArt
extends Control
## The REBEL_CELL logo as baked art (ART_BIBLE §4.3 rule 5, §11 Title; critique §6: the live-
## text logo scrambled with the language): `assets/art/logo_rebel_cell.svg`, original drip-
## graffiti letters in CELL_PINK on INK, drawn as a texture (never live text), plus a T0 idle
## drip (`logo_drip`, §8: a slow loop, >= 3 s): one pink drop at a time swells at a drip's
## end and runs down. Static under reduce effects and headless (no drop at all). Ignores the
## mouse; decoration. View only.

## The logo's height at text scale 1.0 (px). It grows with the text up to MAX_SCALE (art, so
## it never needs the full 2.0).
const HEIGHT := 88.0
const MAX_SCALE := 1.3
## The drip ends in the art, normalised to the image (tools/art/w8a_svgs.py prints them).
const DRIP_ENDS: Array[Vector2] = [Vector2(0.0474, 0.8376), Vector2(0.2979, 0.7539), Vector2(0.4407, 0.8752),
	Vector2(0.6508, 0.7718), Vector2(0.7998, 0.8572), Vector2(0.9418, 0.7524)]
## The drop's radius as a share of the logo's height.
const DROP_SHARE := 0.035
const MOTION := &"logo_drip"

var texture: Texture2D
var _t: float = 0.0


func _init() -> void:
	name = "Logo"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	tooltip_text = ""
	_load()


func _ready() -> void:
	if not Settings.changed.is_connected(_load):
		Settings.changed.connect(_load)
	set_process(Motion.live(MOTION))


## The height drawn now (px).
static func drawn_height() -> float:
	return HEIGHT * minf(Settings.text_scale, MAX_SCALE)


func _load() -> void:
	var h := drawn_height()
	texture = SvgArt.texture(SvgArt.LOGO, h)
	var nat := SvgArt.natural_size(SvgArt.LOGO)
	custom_minimum_size = Vector2(h * nat.x / maxf(1.0, nat.y), h)
	if is_inside_tree():
		set_process(Motion.live(MOTION))
	queue_redraw()


func _process(delta: float) -> void:
	if not Motion.live(MOTION):
		set_process(false)
		queue_redraw()
		return
	_t += delta
	queue_redraw()


## Where the running drop is (local px) and its size share 0..1 (0: no drop), for its
## drip `i` at time `t` (one drip at a time, in turn).
func drop_at(t: float) -> Array:
	var period := maxf(3.0, Motion.seconds(MOTION))
	var n := DRIP_ENDS.size()
	var i := int(floor(t / period)) % n
	var k := fmod(t, period) / period
	var start := Vector2(DRIP_ENDS[i].x * size.x, DRIP_ENDS[i].y * size.y)
	var fall := Motion.amplitude(MOTION) * size.y / HEIGHT
	# Swell for the first half, then run down and thin away.
	if k < 0.5:
		return [start, k * 2.0]
	return [start + Vector2(0, fall * (k - 0.5) * 2.0), 1.0 - (k - 0.5) * 2.0]


func _draw() -> void:
	if texture != null:
		draw_texture_rect(texture, Rect2(Vector2.ZERO, size), false)
	if not Motion.live(MOTION):
		return
	var d := drop_at(_t)
	var r := size.y * DROP_SHARE * float(d[1])
	if r > 0.5:
		draw_circle(d[0], r + 1.5, Palette.INK)
		draw_circle(d[0], r, Palette.CELL_PINK)
