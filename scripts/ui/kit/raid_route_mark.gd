class_name RaidRouteMark
extends Control
## ART-6 3A: a raid route's letter (A, B, C) in a red pencil circle (ART_BIBLE v2 §4.8 "A/B/C
## circles at entry Sites"; round 19 `ui19._draw_rows` "route" rows), beside a THREAT INTEL
## row so the intel and the map's routes name the same entry.

const SIZE := 24.0

var letter: String = "A"


func _init(p_letter: String = "A") -> void:
	letter = p_letter
	name = "Route_%s" % p_letter
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2.ONE * SIZE * Settings.text_scale
	size_flags_vertical = Control.SIZE_SHRINK_CENTER


## The letter of entry `i` (0 = A).
static func letter_of(i: int) -> String:
	return String.chr(65 + posmod(i, 26))


func _draw() -> void:
	var c := size * 0.5
	var r := minf(size.x, size.y) * 0.42
	var red := RaidSkin.pencil_threat()
	RaidPencil.circle(self, c, r, r, red, maxf(2.0, r * 0.22), 0.0, 1.0, letter.unicode_at(0))
	var f := Palette.display()
	var px := roundi(r * 1.25)
	var w := f.get_string_size(letter, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	draw_string(f, c + Vector2(-w * 0.5, f.get_ascent(px) * 0.5 - px * 0.08), letter, HORIZONTAL_ALIGNMENT_LEFT, -1, px, red)
