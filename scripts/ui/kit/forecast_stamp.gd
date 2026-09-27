class_name ForecastStamp
extends Control
## A forecast, not a result (H22 #9: the raid setup's solid BREACHED stamp read as if the
## raid had already run, beside rows such as "50 > 40 HOLDS"). Drawn like combat's dashed
## NEXT plate: a dashed ring, a small caption over the verdict ("IF THE RAID RUNS NOW:")
## and the verdict ("HOME HIT"), the verdict's icon above it. The tooltip says it is a
## projection and how to change it. Display only (no focus, clicks pass).
## H23 S18: icon, caption and verdict are stacked from their measured heights and centred
## in the ring (fixed shares of the radius let the icon sit on the caption at 1.6), the
## whole stack shrinking together when it is taller than the ring holds. H23 S16: the words
## drawn are translated (and measured as translated).

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
## Gap between the stacked parts (share of the caption's line height).
const STACK_GAP := 0.35
## Share of the ring's diameter the stack may take (the rest is the ring's curve).
const STACK_ROOM := 0.8

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


## The caption as drawn: translated (H23 S16).
func shown_caption() -> String:
	return atr(caption)


## The verdict as drawn: translated (H23 S16).
func shown_verdict() -> String:
	return atr(verdict)


## The caption's font size: the text scale's, shrunk to fit the ring's width.
func caption_size() -> int:
	var fs := roundi(CAPTION_SIZE * Settings.text_scale)
	for l in shown_caption().split("\n"):
		fs = mini(fs, _fit(l, Palette.mono(), CAPTION_SIZE))
	return fs


## The verdict's font size: the text scale's, shrunk to fit the ring's width.
func verdict_size() -> int:
	return _fit(shown_verdict(), Palette.display(), VERDICT_SIZE)


func _fit(text: String, font: Font, base: int) -> int:
	var fs := roundi(base * Settings.text_scale)
	var room := _radius() * 2.0 - INSET * 2.0
	var w := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	if w > room and w > 0.0:
		fs = maxi(1, floori(fs * room / w))
	return fs


func _radius() -> float:
	return minf(size.x, size.y) * 0.5 - RING_W


## The stack's parts (local px): {"icon": Rect2, "caption": Rect2, "verdict": Rect2,
## "caption_size": int, "verdict_size": int}; the icon rect is empty without an icon.
func layout() -> Dictionary:
	var c := size * 0.5
	var r := _radius()
	var lines := shown_caption().split("\n")
	var cs := caption_size()
	var vs := verdict_size()
	var cf := Palette.mono()
	var vf := Palette.display()
	var ir := r * ICON_SHARE if icon_kind != &"" else 0.0
	var gap := cf.get_height(cs) * STACK_GAP
	var cap_h := cf.get_height(cs) * lines.size()
	var ver_h := vf.get_height(vs)
	var total := (ir * 2.0 + gap if ir > 0.0 else 0.0) + cap_h + gap + ver_h
	var room := r * 2.0 * STACK_ROOM
	if total > room and total > 0.0:
		# Too tall for the ring: everything a size smaller together.
		var k := room / total
		cs = maxi(1, floori(cs * k))
		vs = maxi(1, floori(vs * k))
		ir *= k
		gap = cf.get_height(cs) * STACK_GAP
		cap_h = cf.get_height(cs) * lines.size()
		ver_h = vf.get_height(vs)
		total = (ir * 2.0 + gap if ir > 0.0 else 0.0) + cap_h + gap + ver_h
	var y := c.y - total * 0.5
	var width := r * 2.0 - INSET * 2.0
	var icon := Rect2()
	if ir > 0.0:
		icon = Rect2(c.x - ir, y, ir * 2.0, ir * 2.0)
		y += ir * 2.0 + gap
	var cap := Rect2(c.x - width * 0.5, y, width, cap_h)
	y += cap_h + gap
	var ver := Rect2(c.x - width * 0.5, y, width, ver_h)
	return {"icon": icon, "caption": cap, "verdict": ver, "caption_size": cs, "verdict_size": vs}


func _draw() -> void:
	var c := size * 0.5
	var r := _radius()
	draw_circle(c, r, Color(Palette.NIGHT_SKY, 0.85))
	var step := TAU / DASHES
	for k in DASHES:
		draw_arc(c, r, k * step, k * step + step * DASH_FILL, 6, color, RING_W)
	var l := layout()
	var icon: Rect2 = l["icon"]
	if icon.has_area():
		StatIcon.draw(self, icon.get_center(), icon.size.x * 0.5, icon_kind, color)
	var cs := int(l["caption_size"])
	var cf := Palette.mono()
	var cap: Rect2 = l["caption"]
	var y := cap.position.y + cf.get_ascent(cs)
	for line in shown_caption().split("\n"):
		draw_string(cf, Vector2(cap.position.x, y), line, HORIZONTAL_ALIGNMENT_CENTER, cap.size.x, cs, Color(Palette.PAPER, 0.85))
		y += cf.get_height(cs)
	var vs := int(l["verdict_size"])
	var ver: Rect2 = l["verdict"]
	draw_string(Palette.display(), Vector2(ver.position.x, ver.position.y + Palette.display().get_ascent(vs)), shown_verdict(), HORIZONTAL_ALIGNMENT_CENTER, ver.size.x, vs, color)
