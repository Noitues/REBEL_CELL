class_name CyberType
extends RefCounted
## A drawn "cybernetic" display face: letters as chamfered strokes on a 4x6 grid (circuit
## traces, 45-degree corners), with optional traces branching off the strokes and ending in
## round solder pads. Used for neon signs (MAINFRAME, CYBER SHOP). Covers the letters the signs
## need plus a few spares; unknown characters draw as a gap.

const W := 4.0
const H := 6.0
## Alpha of the dark backing stroke behind a letter.
const BACKING_ALPHA: float = 0.9
## Width multiplier of the dark backing stroke.
const BACKING_WIDTH_MULT: float = 4.0
## Alpha of the outer glow stroke.
const GLOW_OUTER_ALPHA: float = 0.14
## Width multiplier of the outer glow stroke.
const GLOW_OUTER_WIDTH_MULT: float = 5.0
## Alpha of the inner glow stroke.
const GLOW_INNER_ALPHA: float = 0.35
## Width multiplier of the inner glow stroke.
const GLOW_INNER_WIDTH_MULT: float = 2.4
## Lightening amount of the core stroke colour.
const CORE_LIGHTEN: float = 0.35
## Alpha of a trace's glow stroke.
const TRACE_GLOW_ALPHA: float = 0.25
## Alpha of a trace's core stroke and pad.
const TRACE_CORE_ALPHA: float = 0.85
## Width multiplier of a trace's glow stroke.
const TRACE_GLOW_WIDTH_MULT: float = 2.0
## Width multiplier of a trace's core stroke.
const TRACE_CORE_WIDTH_MULT: float = 0.5
## Minimum width of a trace's core stroke, in px.
const TRACE_CORE_MIN_PX: float = 1.0
## Radius multiplier of a trace's pad.
const PAD_RADIUS_MULT: float = 1.3
## Alpha of a pad's fill.
const PAD_ALPHA: float = 0.9
## Radius multiplier of a pad's inner dot.
const PAD_DOT_MULT: float = 0.55
## Alpha of an auto trace's glow stroke.
const AUTO_GLOW_ALPHA: float = 0.22
## Alpha of an auto trace's core stroke.
const AUTO_CORE_ALPHA: float = 0.8
## Width multiplier of an auto trace's glow stroke.
const AUTO_GLOW_WIDTH_MULT: float = 1.8
## Width multiplier of an auto trace's core stroke.
const AUTO_CORE_WIDTH_MULT: float = 0.45
## Radius multiplier of an auto trace's pad.
const AUTO_PAD_RADIUS_MULT: float = 1.15
## Radius multiplier of an auto trace pad's inner dot.
const AUTO_PAD_DOT_MULT: float = 0.5
## Minimum run length of an auto trace, in grid units.
const AUTO_RUN_MIN: float = 0.6
## Run length range added by the roll, in grid units.
const AUTO_RUN_RANGE: float = 1.2
## Minimum length of the auto trace jog, in grid units.
const AUTO_JOG_MIN: float = 0.5
## Each letter: a list of polylines in grid units (x 0-4, y 0-6, y down).
const GLYPHS := {
	"M": [[Vector2(0, 6), Vector2(0, 1), Vector2(1, 0), Vector2(2, 2), Vector2(3, 0), Vector2(4, 1), Vector2(4, 6)]],
	"O": [[Vector2(1, 0), Vector2(3, 0), Vector2(4, 1), Vector2(4, 5), Vector2(3, 6), Vector2(1, 6), Vector2(0, 5), Vector2(0, 1), Vector2(1, 0)]],
	"D": [[Vector2(0, 0), Vector2(3, 0), Vector2(4, 1), Vector2(4, 5), Vector2(3, 6), Vector2(0, 6), Vector2(0, 0)]],
	"E": [[Vector2(4, 0), Vector2(0, 0), Vector2(0, 6), Vector2(4, 6)], [Vector2(0, 3), Vector2(3, 3)]],
	"F": [[Vector2(4, 0), Vector2(0, 0), Vector2(0, 6)], [Vector2(0, 3), Vector2(3, 3)]],
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


## Whether every character of `text` has a drawn letter (H24 S3: a translated sign word
## the face cannot draw is written in a plain font instead).
static func can_draw(text: String) -> bool:
	if text == "":
		return false
	for i in text.length():
		if not GLYPHS.has(text[i]):
			return false
	return true


## Width in px of `text` at cell size `u` (px per grid unit).
static func width(text: String, u: float) -> float:
	return text.length() * (W + 1.6) * u - 1.6 * u


## Draws `text` with its top-left at `at`, `u` px per grid unit, glowing in `col`.
## `traces` adds the circuit branches; `traces_last_m` uses the M2 set for a final M.
static func draw_text(ci: CanvasItem, at: Vector2, text: String, u: float, col: Color, stroke: float = 3.0, traces: bool = true, density: float = 0.0) -> void:
	var x := at.x
	for i in text.length():
		var ch := text[i]
		var o := Vector2(x, at.y)
		if GLYPHS.has(ch):
			for line in GLYPHS[ch]:
				var pts := PackedVector2Array()
				for p in line:
					pts.append(o + p * u)
				# Dark backing so the letter reads over busy circuitry.
				ci.draw_polyline(pts, Color(Palette.NIGHT_SKY, BACKING_ALPHA), stroke * BACKING_WIDTH_MULT, true)
				ci.draw_polyline(pts, Color(col, GLOW_OUTER_ALPHA), stroke * GLOW_OUTER_WIDTH_MULT, true)
				ci.draw_polyline(pts, Color(col, GLOW_INNER_ALPHA), stroke * GLOW_INNER_WIDTH_MULT, true)
				ci.draw_polyline(pts, col.lightened(CORE_LIGHTEN), stroke, true)
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
					ci.draw_polyline(pts, Color(col, TRACE_GLOW_ALPHA), stroke * TRACE_GLOW_WIDTH_MULT, true)
					ci.draw_polyline(pts, Color(col, TRACE_CORE_ALPHA), maxf(TRACE_CORE_MIN_PX, stroke * TRACE_CORE_WIDTH_MULT), true)
					ci.draw_circle(p, stroke * PAD_RADIUS_MULT, Color(col, PAD_ALPHA))
					ci.draw_circle(p, stroke * PAD_DOT_MULT, Palette.NIGHT_SKY)
			if density > 0.0:
				_auto_traces(ci, o, ch, i, u, col, stroke, density)
		x += (W + 1.6) * u


## Extra circuit branches: from stroke ends and corners, out and away from the letter's
## centre (one straight run, one 45-degree jog), each ending in a solder pad.
static func _auto_traces(ci: CanvasItem, o: Vector2, ch: String, index: int, u: float, col: Color, stroke: float, density: float) -> void:
	var centre := Vector2(W, H) * 0.5
	var k := 0
	for line in GLYPHS[ch]:
		for p in [line[0], line[line.size() - 1], line[line.size() / 2]]:
			k += 1
			var roll := float(absi(hash([ch, index, k])) % 1000) / 1000.0
			if roll > density:
				continue
			var away: Vector2 = p - centre
			var d := Vector2(signf(away.x), signf(away.y))
			if d == Vector2.ZERO:
				d = Vector2(0, 1)
			var first := Vector2(d.x, 0) if absf(away.x) > absf(away.y) else Vector2(0, d.y)
			if first == Vector2.ZERO:
				first = d
			var run := AUTO_RUN_MIN + roll * AUTO_RUN_RANGE
			var a: Vector2 = o + p * u
			var b := a + first * u * run
			var c := b + d.normalized() * u * (AUTO_JOG_MIN + roll)
			var pts := PackedVector2Array([a, b, c])
			ci.draw_polyline(pts, Color(col, AUTO_GLOW_ALPHA), stroke * AUTO_GLOW_WIDTH_MULT, true)
			ci.draw_polyline(pts, Color(col, AUTO_CORE_ALPHA), maxf(TRACE_CORE_MIN_PX, stroke * AUTO_CORE_WIDTH_MULT), true)
			ci.draw_circle(c, stroke * AUTO_PAD_RADIUS_MULT, Color(col, PAD_ALPHA))
			ci.draw_circle(c, stroke * AUTO_PAD_DOT_MULT, Palette.NIGHT_SKY)
