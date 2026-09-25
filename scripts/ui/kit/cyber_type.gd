class_name CyberType
extends RefCounted
## A drawn "cybernetic" display face: letters as chamfered strokes on a 4x6 grid (circuit
## traces, 45-degree corners), with optional traces branching off the strokes and ending in
## round solder pads. Used for neon signs (MODEM, CYBER SHOP). Covers the letters the signs
## need plus a few spares; unknown characters draw as a gap.

const W := 4.0
const H := 6.0
## Each letter: a list of polylines in grid units (x 0-4, y 0-6, y down).
const GLYPHS := {
	"M": [[Vector2(0, 6), Vector2(0, 1), Vector2(1, 0), Vector2(2, 2), Vector2(3, 0), Vector2(4, 1), Vector2(4, 6)]],
	"O": [[Vector2(1, 0), Vector2(3, 0), Vector2(4, 1), Vector2(4, 5), Vector2(3, 6), Vector2(1, 6), Vector2(0, 5), Vector2(0, 1), Vector2(1, 0)]],
	"D": [[Vector2(0, 0), Vector2(3, 0), Vector2(4, 1), Vector2(4, 5), Vector2(3, 6), Vector2(0, 6), Vector2(0, 0)]],
	"E": [[Vector2(4, 0), Vector2(0, 0), Vector2(0, 6), Vector2(4, 6)], [Vector2(0, 3), Vector2(3, 3)]],
	"C": [[Vector2(4, 0), Vector2(1, 0), Vector2(0, 1), Vector2(0, 5), Vector2(1, 6), Vector2(4, 6)]],
	"Y": [[Vector2(0, 0), Vector2(0, 2), Vector2(1, 3), Vector2(3, 3), Vector2(4, 2), Vector2(4, 0)], [Vector2(2, 3), Vector2(2, 6)]],
	"B": [[Vector2(0, 0), Vector2(3, 0), Vector2(4, 1), Vector2(4, 2), Vector2(3, 3), Vector2(4, 4), Vector2(4, 5), Vector2(3, 6), Vector2(0, 6), Vector2(0, 0)], [Vector2(0, 3), Vector2(3, 3)]],
	"R": [[Vector2(0, 6), Vector2(0, 0), Vector2(3, 0), Vector2(4, 1), Vector2(4, 2), Vector2(3, 3), Vector2(0, 3)], [Vector2(2, 3), Vector2(4, 5), Vector2(4, 6)]],
	"S": [[Vector2(4, 0), Vector2(1, 0), Vector2(0, 1), Vector2(0, 2), Vector2(1, 3), Vector2(3, 3), Vector2(4, 4), Vector2(4, 5), Vector2(3, 6), Vector2(0, 6)]],
	"H": [[Vector2(0, 0), Vector2(0, 6)], [Vector2(4, 0), Vector2(4, 6)], [Vector2(0, 3), Vector2(4, 3)]],
	"P": [[Vector2(0, 6), Vector2(0, 0), Vector2(3, 0), Vector2(4, 1), Vector2(4, 2), Vector2(3, 3), Vector2(0, 3)]],
	"A": [[Vector2(0, 6), Vector2(0, 1), Vector2(1, 0), Vector2(3, 0), Vector2(4, 1), Vector2(4, 6)], [Vector2(0, 3), Vector2(4, 3)]],
	"T": [[Vector2(0, 0), Vector2(4, 0)], [Vector2(2, 0), Vector2(2, 6)]],
	"L": [[Vector2(0, 0), Vector2(0, 6), Vector2(4, 6)]],
	"U": [[Vector2(0, 0), Vector2(0, 5), Vector2(1, 6), Vector2(3, 6), Vector2(4, 5), Vector2(4, 0)]],
	"N": [[Vector2(0, 6), Vector2(0, 0), Vector2(4, 6), Vector2(4, 0)]],
	"I": [[Vector2(1, 0), Vector2(3, 0)], [Vector2(2, 0), Vector2(2, 6)], [Vector2(1, 6), Vector2(3, 6)]],
}
## Circuit traces per letter: [start point on the letter, direction pattern] in grid units;
## a trace runs out along the pattern and ends in a pad.
const TRACES := {
	"M": [[Vector2(0, 6), [Vector2(-1, 1), Vector2(-1, 0)]], [Vector2(2, 2), [Vector2(0, 1.5)]]],
	"O": [[Vector2(4, 3), [Vector2(1, 0), Vector2(1, 1)]]],
	"D": [[Vector2(0, 0), [Vector2(0, -1), Vector2(1, -1)]]],
	"E": [[Vector2(3, 3), [Vector2(1, 0), Vector2(1, 1)]], [Vector2(4, 6), [Vector2(1, 1)]]],
	"M2": [[Vector2(4, 6), [Vector2(1, 1), Vector2(1, 0)]], [Vector2(4, 1), [Vector2(1, -1)]]],
	"C": [[Vector2(1, 0), [Vector2(0, -1), Vector2(-1, -1)]]],
	"S": [[Vector2(0, 6), [Vector2(-1, 1)]]],
	"P": [[Vector2(4, 1), [Vector2(1, -1)]]],
}


## Width in px of `text` at cell size `u` (px per grid unit).
static func width(text: String, u: float) -> float:
	return text.length() * (W + 1.6) * u - 1.6 * u


## Draws `text` with its top-left at `at`, `u` px per grid unit, glowing in `col`.
## `traces` adds the circuit branches; `traces_last_m` uses the M2 set for a final M.
static func draw_text(ci: CanvasItem, at: Vector2, text: String, u: float, col: Color, stroke: float = 3.0, traces: bool = true) -> void:
	var x := at.x
	for i in text.length():
		var ch := text[i]
		var o := Vector2(x, at.y)
		if GLYPHS.has(ch):
			for line in GLYPHS[ch]:
				var pts := PackedVector2Array()
				for p in line:
					pts.append(o + p * u)
				ci.draw_polyline(pts, Color(col, 0.14), stroke * 5.0, true)
				ci.draw_polyline(pts, Color(col, 0.35), stroke * 2.4, true)
				ci.draw_polyline(pts, col.lightened(0.35), stroke, true)
			if traces:
				var key := ch
				if ch == "M" and i == text.length() - 1:
					key = "M2"
				for t in TRACES.get(key, []):
					var p: Vector2 = o + t[0] * u
					var pts := PackedVector2Array([p])
					for step in t[1]:
						p += step * u
						pts.append(p)
					ci.draw_polyline(pts, Color(col, 0.25), stroke * 2.0, true)
					ci.draw_polyline(pts, Color(col, 0.85), maxf(1.0, stroke * 0.5), true)
					ci.draw_circle(p, stroke * 1.3, Color(col, 0.9))
					ci.draw_circle(p, stroke * 0.55, Palette.NIGHT_SKY)
		x += (W + 1.6) * u
