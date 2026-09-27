class_name ForecastStamp
extends Control
## A forecast, not a result (H22 #9: the raid setup's solid BREACHED stamp read as if the
## raid had already run, beside rows such as "50 > 40 HOLDS"). Drawn like combat's dashed
## NEXT plate: a dashed ring, a small caption over the verdict ("IF THE RAID RUNS NOW:")
## and the verdict ("HOME HIT"), the verdict's icon above it. The tooltip says it is a
## projection and how to change it. Display only (no focus, clicks pass).

## Ring dashes, the dash share of each step and the ring's width (px).
const DASHES := 28
const DASH_FILL := 0.6
const RING_W := 3.0
## Caption and verdict lettering at text scale 1.0 (they grow with it, fitted to the ring).
const CAPTION_SIZE := 10
const VERDICT_SIZE := 20
## Inner padding of the lettering from the ring (px) and the icon's radius share.
const INSET := 12.0
const ICON_SHARE := 0.17
## Where the icon, the caption's last line and the verdict sit (shares of the radius from
## the centre, up negative).
const ICON_Y := -0.62
const CAPTION_Y := -0.08
const VERDICT_Y := 0.2

var caption: String = ""
var verdict: String = ""
var color: Color = Palette.CELL_PINK
var icon_kind: StringName = &""


func _init(p_caption: String = "", p_verdict: String = "", p_color: Color = Palette.CELL_PINK, p_icon: StringName = &"") -> void:
	name = "Projection"
	caption = p_caption
	verdict = p_verdict
	color = p_color
	icon_kind = p_icon
	mouse_filter = Control.MOUSE_FILTER_PASS  # its tooltip explains the forecast
	focus_mode = Control.FOCUS_NONE


## The caption's font size: the text scale's, shrunk to fit the ring's width.
func caption_size() -> int:
	var fs := roundi(CAPTION_SIZE * Settings.text_scale)
	for l in caption.split("\n"):
		fs = mini(fs, _fit(l, Palette.mono(), CAPTION_SIZE))
	return fs


## The verdict's font size: the text scale's, shrunk to fit the ring's width.
func verdict_size() -> int:
	return _fit(verdict, Palette.display(), VERDICT_SIZE)


func _fit(text: String, font: Font, base: int) -> int:
	var fs := roundi(base * Settings.text_scale)
	var room := _radius() * 2.0 - INSET * 2.0
	var w := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	if w > room and w > 0.0:
		fs = maxi(1, floori(fs * room / w))
	return fs


func _radius() -> float:
	return minf(size.x, size.y) * 0.5 - RING_W


func _draw() -> void:
	var c := size * 0.5
	var r := _radius()
	draw_circle(c, r, Color(Palette.NIGHT_SKY, 0.85))
	var step := TAU / DASHES
	for k in DASHES:
		draw_arc(c, r, k * step, k * step + step * DASH_FILL, 6, color, RING_W)
	var lines := caption.split("\n")
	var cs := caption_size()
	var cf := Palette.mono()
	var y := c.y + r * CAPTION_Y - (lines.size() - 1) * cf.get_height(cs)
	if icon_kind != &"":
		StatIcon.draw(self, Vector2(c.x, c.y + r * ICON_Y), r * ICON_SHARE, icon_kind, color)
	for l in lines:
		draw_string(cf, Vector2(c.x - r + INSET, y), l, HORIZONTAL_ALIGNMENT_CENTER, r * 2.0 - INSET * 2.0, cs, Color(Palette.PAPER, 0.85))
		y += cf.get_height(cs)
	var vs := verdict_size()
	draw_string(Palette.display(), Vector2(c.x - r + INSET, c.y + r * VERDICT_Y + Palette.display().get_ascent(vs) * 0.5), verdict, HORIZONTAL_ALIGNMENT_CENTER, r * 2.0 - INSET * 2.0, vs, color)
