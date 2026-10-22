class_name RcWaxFont
extends RefCounted
## LOOK-TOOLBOX module 12: RC Wax, the grease pencil's own face, as pen strokes. Built with its TrueType twin
## (assets/fonts/RcWax-Regular.ttf, Palette.FONT_PENCIL) from one stroke source by
## addons/rc_look/tools/build_wax_font.py, so a word laid here has the advances Font.get_string_size measures.
## `layout` gives a word's strokes in writing order (local px, baseline at y 0, y down) with a seeded hand on top of the
## face's own (KitNoise hashes, never an RNG): each letter turns, drops and sizes a little, each stroke wobbles.
## Characters the face lacks come back as `missing` (the caller draws them in the TrueType face). Pure.

const STROKES_PATH := "res://addons/rc_look/pencil/rc_wax_strokes.json"

static var _data: Dictionary = {}


static func _load() -> Dictionary:
	if _data.is_empty():
		var f := FileAccess.open(STROKES_PATH, FileAccess.READ)
		if f != null:
			var v: Variant = JSON.parse_string(f.get_as_text())
			if v is Dictionary:
				_data = v
	return _data


## The face's units per em.
static func upm() -> float:
	return float(_load().get("upm", 1000.0))


## True when the face draws `ch` as strokes.
static func has_char(ch: String) -> bool:
	return (_load().get("glyphs", {}) as Dictionary).has(str(ch.unicode_at(0)))


## Character `ch`'s advance at `px` (local px).
static func advance(ch: String, px: float) -> float:
	var g: Dictionary = (_load().get("glyphs", {}) as Dictionary).get(str(ch.unicode_at(0)), {})
	return float(g.get("adv", 0.0)) * px / upm()


## Word `text` at font `px` laid as strokes: {strokes: Array[PackedVector2Array], letter: PackedInt32Array (each
## stroke's letter index), x: PackedFloat32Array (each letter's pen x), missing: [{index, x}], width: float (the advance
## sum, as the TrueType face measures it)}. `seed` picks the hand; `look` its sizes.
static func layout(text: String, px: float, seed: int, look: RcPencilLook) -> Dictionary:
	var glyphs: Dictionary = _load().get("glyphs", {})
	var k := px / upm()
	var strokes: Array[PackedVector2Array] = []
	var letter := PackedInt32Array()
	var xs := PackedFloat32Array()
	var missing: Array[Dictionary] = []
	var pen := 0.0
	var cap := float(_load().get("cap", 740.0)) * k
	for i in text.length():
		var ch := text[i]
		xs.append(pen)
		var key := str(ch.unicode_at(0))
		if not glyphs.has(key):
			missing.append({"index": i, "x": pen})
			pen += Palette.pencil().get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1, int(px)).x
			continue
		var g: Dictionary = glyphs[key]
		var adv := float(g["adv"]) * k
		var turn := KitNoise.h11(seed, i, 1) * look.word_letter_turn
		var drop := KitNoise.h11(seed, i, 2) * look.word_baseline_jitter * px
		var size := 1.0 + KitNoise.h11(seed, i, 3) * look.word_size_jitter
		var pivot := Vector2(pen + adv * 0.5, -cap * 0.5)
		var s_i := 0
		for flat: Array in g["strokes"]:
			var pts := PackedVector2Array()
			var n := flat.size() / 2
			for j in n:
				var p := Vector2(pen + float(flat[2 * j]) * k, -float(flat[2 * j + 1]) * k)
				p = pivot + ((p - pivot) * size).rotated(turn) + Vector2(0.0, drop)
				pts.append(p)
			strokes.append(_wobble(pts, seed * 31 + i * 7 + s_i, look.word_wobble_em * px, px))
			letter.append(i)
			s_i += 1
		pen += adv
	return {"strokes": strokes, "letter": letter, "x": xs, "missing": missing, "width": pen}


## `pts` moved sideways by a smooth seeded wobble of up to `amp` px (waves about a third of `px` long).
static func _wobble(pts: PackedVector2Array, seed: int, amp: float, px: float) -> PackedVector2Array:
	if pts.size() < 2 or amp <= 0.0:
		return pts
	var out := PackedVector2Array()
	var d := 0.0
	var wave := maxf(px * 0.35, 1.0)
	for j in pts.size():
		if j > 0:
			d += pts[j].distance_to(pts[j - 1])
		var a := pts[maxi(0, j - 1)]
		var b := pts[mini(pts.size() - 1, j + 1)]
		var nrm := (b - a).normalized().orthogonal()
		out.append(pts[j] + nrm * (KitNoise.smooth(seed, d / wave) * 2.0 - 1.0) * amp)
	return out
