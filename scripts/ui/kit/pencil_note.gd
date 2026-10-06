class_name PencilNote
extends Control
## ART-9 4A (ART_BIBLE v2 §1.2 "Grease pencil"): a wax-pencil note true to the rules ("TOP 3
## ONLY", "BIN IT", "+1 = 18", "PLAY IT SAFE??"), yellow for our plan, red for a threat or a loss,
## with an optional arrow to what it means. Drawn by 1B's grease pencil: each line is a
## GreasePencilWord and the arrow a GreasePencilMark (PencilShapes.arrow), so the wax, its grain,
## its under-shadow and PencilLint's "no UI covers pencil" are 1B's. This control only lays the
## note out (its size is its words'). View only.

const FONT_PX := 20
## The arrow's head (px) and its seed.
const HEAD := 14.0

var text: String = ""
var colour: Color = Palette.PENCIL_PLAN
var tilt: float = 0.0
var font_px: int = FONT_PX
var arrow_from: Vector2 = Vector2.ZERO
var arrow_to: Vector2 = Vector2.ZERO
var arrow_bend: float = 0.0
var _words: Array[GreasePencilWord] = []
var _mark: GreasePencilMark = null


func _init(p_text: String = "", p_colour: Color = Palette.PENCIL_PLAN, p_tilt: float = 0.0, p_font_px: int = FONT_PX) -> void:
	text = p_text
	colour = p_colour
	tilt = p_tilt
	font_px = p_font_px
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var ink := GreasePencilMark.Ink.THREAT if colour == Palette.PENCIL_THREAT else GreasePencilMark.Ink.PLAN
	var holder := Node2D.new()
	holder.name = "Wax"
	holder.rotation = tilt
	add_child(holder)
	var f := Palette.pencil()
	var y := f.get_ascent(font_px)
	for line in text.split("\n"):
		if line == "":
			continue
		var w := GreasePencilWord.new()
		w.text = line
		w.ink = ink
		w.text_step = maxi(1, roundi(font_px / maxf(0.01, Settings.text_scale)))
		w.position = Vector2(0, y)
		holder.add_child(w)
		_words.append(w)
		y += f.get_height(font_px)
	_mark = GreasePencilMark.new()
	_mark.name = "Arrow"
	_mark.ink = ink
	add_child(_mark)
	custom_minimum_size = text_size()


## The words' size at their lettering (px).
func text_size() -> Vector2:
	var f := Palette.pencil()
	var w := 0.0
	var lines := text.split("\n")
	for l in lines:
		w = maxf(w, f.get_string_size(l, HORIZONTAL_ALIGNMENT_LEFT, -1, font_px).x)
	return Vector2(w, f.get_height(font_px) * lines.size()) + GreasePencilMark.SHADOW_OFFSET


## Adds an arrow from `from` to `to` (local px) bent sideways by `bend` px (redraws it).
func with_arrow(from: Vector2, to: Vector2, bend: float = 0.0) -> PencilNote:
	if from == arrow_from and to == arrow_to and bend == arrow_bend:
		return self
	arrow_from = from
	arrow_to = to
	arrow_bend = bend
	_mark.clear()
	if from != to:
		var mid := (from + to) * 0.5 + (to - from).orthogonal().normalized() * bend
		for stroke in PencilShapes.arrow(PencilShapes.bezier(from, mid, to, 24), HEAD, absi(text.hash()) % 97):
			_mark.add_stroke(stroke)
	return self
