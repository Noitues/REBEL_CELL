class_name TideOddsBar
extends Control
## Phase 3d: the odds of a forecast as one bar: a segment per raid tier, wide as its share of the outcomes, worst tier on the left (SolaceTideTally.tier_odds).
## Each segment carries its count; a wide enough one also its tier glyph. A view: it draws the odds it is given and tells the screen which segment the
## pointer is on (the screen draws that tier's outcomes on the map).

## The pointer entered a segment (its tier) or left the bar ("").
signal segment_hovered(tier: String)
## A segment was clicked.
signal segment_pressed(tier: String)

const GLYPH_MIN_W := 26.0
const COUNT_PX := 13

var odds: Array = []
var total: int = 0
var lit: String = ""


## A bar of `p_odds` ([{tier, n}], worst first) in `size_px`.
static func make(p_odds: Array, size_px: Vector2) -> TideOddsBar:
	var b := TideOddsBar.new()
	b.odds = p_odds
	for o in p_odds:
		b.total += int(o["n"])
	b.custom_minimum_size = size_px
	b.mouse_filter = Control.MOUSE_FILTER_PASS
	b.tooltip_text = b.words()
	return b


## "7 of 12 HOLDS, 5 of 12 SITES LOST".
func words() -> String:
	var parts := PackedStringArray()
	for o in odds:
		parts.append("%d of %d %s" % [int(o["n"]), total, TideGlyphs.tier_word(String(o["tier"]))])
	return ", ".join(parts)


## The segment rectangles, in order.
func segments() -> Array[Rect2]:
	var out: Array[Rect2] = []
	var x := 0.0
	for o in odds:
		var w := size.x * float(int(o["n"])) / float(maxi(1, total))
		out.append(Rect2(x, 0.0, w, size.y))
		x += w
	return out


func _draw() -> void:
	var segs := segments()
	var f := ThemeDB.fallback_font
	for i in segs.size():
		var t := String(odds[i]["tier"])
		var r := segs[i].grow_individual(-1.0, 0.0, -1.0, 0.0)
		var col := TideGlyphs.tier_color(t)
		if t == "BREACHED":
			draw_rect(r, TideGlyphs.BLACK)
			draw_rect(r, TideGlyphs.RED, false, 2.0)
		else:
			draw_rect(r, Color(col, 0.55 if lit == "" or lit == t else 0.25))
			draw_rect(r, col, false, 2.0 if lit == t else 1.0)
		var x := r.position.x + 3.0
		if r.size.x >= GLYPH_MIN_W + 14.0:
			TideGlyphs.tier(self, Vector2(x + 8.0, r.get_center().y), t, minf(8.0, r.size.y * 0.4), col)
			x += 19.0
		if r.size.x >= 14.0:
			draw_string(f, Vector2(x, r.get_center().y + 5.0), "%d" % int(odds[i]["n"]), HORIZONTAL_ALIGNMENT_LEFT, r.end.x - x, COUNT_PX, TideGlyphs.INK)


func _segment_at(x: float) -> String:
	var segs := segments()
	for i in segs.size():
		if x >= segs[i].position.x and x < segs[i].end.x:
			return String(odds[i]["tier"])
	return ""


func _gui_input(ev: InputEvent) -> void:
	if ev is InputEventMouseMotion:
		var t := _segment_at((ev as InputEventMouseMotion).position.x)
		if t != lit:
			lit = t
			queue_redraw()
			segment_hovered.emit(t)
	elif ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT:
		segment_pressed.emit(_segment_at((ev as InputEventMouseButton).position.x))


func _notification(what: int) -> void:
	if what == NOTIFICATION_MOUSE_EXIT and lit != "":
		lit = ""
		queue_redraw()
		segment_hovered.emit("")
