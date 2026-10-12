class_name RaidRouteMark
extends Control
## ART-6 3A: a raid route's letter (A, B, C) in a red ring (ART_BIBLE v2 §4.8 "A/B/C
## circles at entry Sites"; round 19 `ui19._draw_rows` "route" rows), beside a THREAT INTEL
## row so the intel and the map's routes name the same entry.

const SIZE := 24.0
## M14 12Q-RAID: the reticle ticks' radius (x the ring's): they cross the ring and stay in the box.
const RETICLE_FIT := 0.79

var letter: String = "A"


func _init(p_letter: String = "A") -> void:
	letter = p_letter
	name = "Route_%s" % p_letter
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2.ONE * SIZE * Settings.text_scale
	size_flags_vertical = Control.SIZE_SHRINK_CENTER


func _ready() -> void:
	Settings.changed.connect(queue_redraw)  # M14 12Q-RAID: the colour-blind setting's reticle


## The letter of entry `i` (0 = A).
static func letter_of(i: int) -> String:
	return String.chr(65 + posmod(i, 26))


func _draw() -> void:
	var c := size * 0.5
	var r := minf(size.x, size.y) * 0.42
	var red := Palette.HARM  # B1b audit: the concept's crisp HARM ring (ui19 route row), not pencil
	var ink_w := maxf(2.0, r * 0.16)
	draw_arc(c, r, 0.0, TAU, 28, red, ink_w, true)
	if RaidPencil.hostile_cues():
		# M14 12Q-RAID: hostile by shape as well as red (the map's entry marks carry the same).
		for t in RaidPencil.reticle_ticks(c, Vector2(r, r) * RETICLE_FIT):
			draw_line(t[0], t[1], red, ink_w, true)
	var f := Palette.display()
	var px := roundi(r * 1.25)
	var w := f.get_string_size(letter, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	draw_string(f, c + Vector2(-w * 0.5, f.get_ascent(px) * 0.5 - px * 0.08), letter, HORIZONTAL_ALIGNMENT_LEFT, -1, px, red)
