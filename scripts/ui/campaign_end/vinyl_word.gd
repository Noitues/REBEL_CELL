class_name VinylWord
extends Control
## ART-11 4D: a vinyl sticker (ART_BIBLE v2 §1.2: things that never change; refs
## `campaign_end/round20_raid_world/campaign_lost.jpg` title and tray, round 21 buttons): a
## white die-cut plate round Anton lettering with an ink keyline and extrude and a bevelled
## fill, or a defence card (WORD / CARD). It can curl at one corner (the plate is cut along the
## fold and the cream backing folds over) for the campaign lost lock, where the Cell's stickers
## curl and drop off the glass. A seam for 1B's vinyl material: same job, drawn here until the
## material lands. Look only; the screen moves it (position, rotation) and sets `curl`.

enum Kind { WORD, CARD }

## The words (already translated by the caller, or a key: shown through tr).
var text: String = ""
var kind: int = Kind.WORD
## The fill's top and bottom (a Palette END_VINYL_* pair).
var fill: Array[Color] = Palette.END_VINYL_YELLOW
## The lettering size at text scale 1.0 (px).
var font_size: int = UiTheme.HEADING
## A defence card's asset (its icon and accent).
var asset_id: StringName = &""
## 0 flat .. 1 the corner folded far over; the corner it lifts (0 top-left, clockwise).
var curl: float = 0.0:
	set(v):
		curl = clampf(v, 0.0, 1.0)
		_redraw_all()
var curl_corner: int = 1
## The word's key reaches the words as given (TextDb.shown_as_given pages).
var pre_translated: bool = false
## The run end's verdict sticker: the verdict word and whether it has landed (a result).
var verdict: String = ""
var resolved: bool = true

var _body: Control = null
var _ink: Control = null
var _flap: Control = null

## The die-cut border, the plate's inner pad round the words and the extrude (px at 1.0), the
## corner radius as a share of the height, the keyline and the bevel (px at 1.0).
const BORDER := 7.0
const PAD := Vector2(14, 6)
const EXTRUDE := Vector2(2.5, 3.5)
const RADIUS_SHARE := 0.42
const KEYLINE := 5
const BEVEL := 1.5
## A card's size and its accent bar (px at 1.0), and how far a full curl folds (share of the
## shorter side).
const CARD_SIZE := Vector2(76, 92)
const CARD_BAR := 3.0
const CURL_REACH := 0.85
## Segments per rounded corner.
const CORNER_STEPS := 6


func _init(p_text: String = "", p_fill: Array[Color] = Palette.END_VINYL_YELLOW, p_font_size: int = UiTheme.HEADING, p_kind: int = Kind.WORD) -> void:
	text = p_text
	fill = p_fill
	font_size = p_font_size
	kind = p_kind
	verdict = p_text
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	_body = Control.new()
	_body.name = "Plate"
	_body.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_body.clip_children = CanvasItem.CLIP_CHILDREN_AND_DRAW
	_body.draw.connect(_draw_plate)
	add_child(_body)
	_ink = Control.new()
	_ink.name = "Ink"
	_ink.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_ink.draw.connect(_draw_ink)
	_body.add_child(_ink)
	_flap = Control.new()
	_flap.name = "Flap"
	_flap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_flap.draw.connect(_draw_flap)
	add_child(_flap)
	resized.connect(_on_resized)
	refit()


## A defence card sticker for asset `id` with its name `title` (translated).
static func card(id: StringName, title: String) -> VinylWord:
	var v := VinylWord.new(title, Palette.END_VINYL_YELLOW, UiTheme.LABEL, Kind.CARD)
	v.asset_id = id
	v.pre_translated = true
	v.refit()
	return v


## Slaps the sticker on with motion `id` (a pop about its centre; at rest at once when the
## motion does not play). Returns the tween or null.
func slap(id: StringName) -> Tween:
	pivot_offset = size * 0.5
	# A short motion: it completes with any press another helper takes (MotionSkip, ANIM-R6 D7).
	MotionSkip.register_passive(self)
	return Motion.pop(self, id)


## MotionSkip: the slap's pop plays.
func motion_running() -> bool:
	return is_inside_tree() and Motion.held(self, ^"scale")


## MotionSkip: the sticker at rest.
func complete_motion() -> void:
	Motion.settle(self, ^"scale")


## The words as drawn.
func shown_text() -> String:
	return text if pre_translated else tr(text)


## The most the sticker grows with the text size (0 = with it all the way): a sticker is a
## whole object (bible §2.9), and a big verdict at 2.0 would push its window off the screen.
var scale_cap: float = 0.0


## The lettering size now (px).
func font_px() -> int:
	return roundi(font_size * _s())


func _s() -> float:
	return minf(Settings.text_scale, scale_cap) if scale_cap > 0.0 else Settings.text_scale


## Measures the sticker at the text size now.
func refit() -> void:
	var s := _s()
	if kind == Kind.CARD:
		custom_minimum_size = CARD_SIZE * s
	else:
		var f := Palette.display()
		var w := f.get_string_size(shown_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, font_px()).x
		var h := f.get_height(font_px())
		custom_minimum_size = Vector2(w, h) + (PAD + Vector2(BORDER, BORDER)) * 2.0 * s + EXTRUDE * s
	size = custom_minimum_size
	_on_resized()


func _on_resized() -> void:
	pivot_offset = size * 0.5
	for c: Control in [_body, _ink, _flap]:
		if c != null:
			c.position = Vector2.ZERO
			c.size = size
	_redraw_all()


func _redraw_all() -> void:
	queue_redraw()
	for c: Control in [_body, _ink, _flap]:
		if c != null:
			c.queue_redraw()


## The plate's outline (local px): a rounded rect.
func plate_polygon() -> PackedVector2Array:
	var r := Rect2(Vector2.ZERO, size - EXTRUDE * _s() * 0.5)
	var rad := minf(r.size.y * RADIUS_SHARE, r.size.x * 0.5) if kind == Kind.WORD else BORDER * 1.6 * _s()
	var pts := PackedVector2Array()
	var centres := [r.position + Vector2(r.size.x - rad, rad), r.end - Vector2(rad, rad), r.position + Vector2(rad, r.size.y - rad), r.position + Vector2(rad, rad)]
	var starts := [-PI * 0.5, 0.0, PI * 0.5, PI]
	for i in 4:
		for k in CORNER_STEPS + 1:
			var a: float = starts[i] + PI * 0.5 * k / CORNER_STEPS
			pts.append(centres[i] + Vector2(cos(a), sin(a)) * rad)
	return pts


## The corner the curl lifts and the two points where the fold meets the edges (local px).
func fold() -> Dictionary:
	var r := Rect2(Vector2.ZERO, size - EXTRUDE * _s() * 0.5)
	var corners := [r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)]
	var c: Vector2 = corners[curl_corner % 4]
	var e1: Vector2 = (corners[(curl_corner + 1) % 4] - c).normalized()
	var e2: Vector2 = (corners[(curl_corner + 3) % 4] - c).normalized()
	var d := curl * minf(r.size.x, r.size.y) * CURL_REACH
	var p1 := c + e1 * d
	var p2 := c + e2 * d
	# The corner reflected over the fold line lands inside the plate.
	var mid := (p1 + p2) * 0.5
	var lifted := mid * 2.0 - c
	return {"corner": c, "p1": p1, "p2": p2, "lifted": lifted}


## The plate with the folded-away corner cut off.
func cut_plate() -> PackedVector2Array:
	var plate := plate_polygon()
	if curl <= 0.0:
		return plate
	var f := fold()
	var tri := PackedVector2Array([f["corner"] + (f["corner"] - (f["p1"] + f["p2"]) * 0.5) * 2.0, f["p1"], f["p2"]])
	var parts := Geometry2D.clip_polygons(plate, tri)
	var best := plate
	var area := -1.0
	for p: PackedVector2Array in parts:
		var a := absf(_area(p))
		if a > area:
			area = a
			best = p
	return best


static func _area(p: PackedVector2Array) -> float:
	var a := 0.0
	for i in p.size():
		var q := p[(i + 1) % p.size()]
		a += p[i].x * q.y - q.x * p[i].y
	return a * 0.5


func _draw() -> void:
	# The sticker's shadow on the glass (it lifts as it curls).
	var sh := cut_plate()
	var off := Vector2(2, 3) * _s() * (1.0 + curl * 2.0)
	var moved := PackedVector2Array()
	for p in sh:
		moved.append(p + off)
	if moved.size() >= 3:
		draw_colored_polygon(moved, Palette.SHADOW)


func _draw_plate() -> void:
	var poly := cut_plate()
	if poly.size() >= 3:
		_body.draw_colored_polygon(poly, Palette.END_VINYL_BORDER)


func _draw_ink() -> void:
	var s := _s()
	var inner := Rect2(Vector2(BORDER, BORDER) * s, size - Vector2(BORDER, BORDER) * 2.0 * s - EXTRUDE * s * 0.5)
	if kind == Kind.CARD:
		_draw_card(inner)
		return
	var f := Palette.display()
	var fs := font_px()
	var word := shown_text()
	var base := Vector2(inner.position.x + PAD.x * s, inner.position.y + (inner.size.y + f.get_ascent(fs) - f.get_descent(fs)) * 0.5)
	var w := inner.size.x - PAD.x * 2.0 * s
	var key := maxi(1, roundi(KEYLINE * s))
	# Extrude: the keyline again, pushed down-right; then the keyline; then the bevelled fill.
	_ink.draw_string_outline(f, base + EXTRUDE * s, word, HORIZONTAL_ALIGNMENT_CENTER, w, fs, key, Palette.INK)
	_ink.draw_string(f, base + EXTRUDE * s, word, HORIZONTAL_ALIGNMENT_CENTER, w, fs, Palette.INK)
	_ink.draw_string_outline(f, base, word, HORIZONTAL_ALIGNMENT_CENTER, w, fs, key, Palette.INK)
	_ink.draw_string(f, base + Vector2(0, -BEVEL * s), word, HORIZONTAL_ALIGNMENT_CENTER, w, fs, fill[0])
	_ink.draw_string(f, base + Vector2(0, BEVEL * s * 0.5), word, HORIZONTAL_ALIGNMENT_CENTER, w, fs, fill[1])


func _draw_card(inner: Rect2) -> void:
	var s := _s()
	var col := AssetIcon.color_of(asset_id)
	_ink.draw_rect(inner, Palette.NIGHT_SKY)
	_ink.draw_rect(Rect2(inner.position, Vector2(inner.size.x, CARD_BAR * s)), col)
	AssetIcon.draw_icon(_ink, inner.position + Vector2(inner.size.x * 0.5, inner.size.y * 0.36), inner.size.x * 0.2, asset_id, false)
	var f := Palette.display()
	var fs := roundi(font_size * s)
	var name_w := inner.size.x - BORDER * s
	# The name steps down to the caption floor to fit the card.
	while fs > UiTheme.font_px(UiTheme.CAPTION) and f.get_string_size(shown_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > name_w:
		fs -= 1
	_ink.draw_string(f, Vector2(inner.position.x + BORDER * 0.5 * s, inner.end.y - BORDER * s), shown_text(), HORIZONTAL_ALIGNMENT_LEFT, name_w, fs, Palette.TEXT_HI)


func _draw_flap() -> void:
	if curl <= 0.0:
		return
	var f := fold()
	var flap := PackedVector2Array([f["p1"], f["lifted"], f["p2"]])
	var off := Vector2(2, 3) * _s()
	_flap.draw_colored_polygon(PackedVector2Array([f["p1"] + off, f["lifted"] + off * 2.0, f["p2"] + off]), Palette.SHADOW)
	# The cream backing, lighter along the fold where it catches the light.
	_flap.draw_colored_polygon(flap, Palette.PAPER_ALT)
	var mid: Vector2 = (f["p1"] + f["p2"]) * 0.5
	var toward: Vector2 = f["lifted"] - mid
	_flap.draw_colored_polygon(PackedVector2Array([f["p1"], f["p1"] + toward * 0.35, f["p2"] + toward * 0.35, f["p2"]]), Palette.PAPER)
	_flap.draw_polyline(PackedVector2Array([f["p1"], f["lifted"], f["p2"]]), Color(Palette.INK, 0.35), 1.0, true)
