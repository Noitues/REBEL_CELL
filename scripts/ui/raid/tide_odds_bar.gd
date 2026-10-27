class_name TideOddsBar
extends Control
## Phase 3d: the odds of a forecast as one bar: a segment per raid tier, wide as its share of the outcomes, worst tier on the left (SolaceTideTally.tier_odds).
## Each segment carries its count; a wide enough one also its tier glyph. A view: it draws the odds it is given and tells the screen which segment the
## pointer is on (the screen draws that tier's outcomes on the map).

## The pointer entered a segment (its tier) or left the bar ("").
signal segment_hovered(tier: String)
## A segment was clicked.
signal segment_pressed(tier: String)

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
		parts.append("%d of %d %s" % [int(o["n"]), total, TideFx.tier_word(String(o["tier"]))])
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
	TideFx.odds_bar(self, odds, segments(), lit)


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
