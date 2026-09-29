class_name CorpPattern
extends RefCounted
## ART_BIBLE §3.6: each corporation's pattern, which separates the corps without colour
## (district hatches, enemy wheel bezels, threat routes). Static painters that draw onto
## any CanvasItem from its `_draw()`: a rect, a polygon or a ring (annulus) fill, and a
## dashed line for threat routes. Deterministic (no RNG): the same arguments always draw
## the same marks, and fills are anchored to the canvas origin so neighbouring fills
## line up. Each pattern is a different texture (dots on a wave, diagonal stripes, ring
## seals, a dot-and-star lattice, broken horizontal bars), so they read in greyscale.
## Use `Palette.corp_pattern_id(corp_id)` for a corporation's kind.
##
## Cost: a fill issues one draw call per dot and one per clipped line; draw large areas
## from a CanvasItem that redraws only when its state changes, not every frame.

## The pattern kinds. NONE draws nothing (fills) or plain even dashes (dashed_line).
enum Kind { NONE, HELIX_DOTS, CONTAINER_STRIPES, CIVIC_RINGS, STAR_GRID, SCAN_GLITCH }

## Every drawn kind, in corp order (Solace, Meridian, Halcyon, Orbital, REBEL_CELL).
const KINDS: Array[int] = [Kind.HELIX_DOTS, Kind.CONTAINER_STRIPES, Kind.CIVIC_RINGS, Kind.STAR_GRID, Kind.SCAN_GLITCH]
## A short name per kind (labs, logs; not player-facing).
const KIND_NAMES := {
	Kind.NONE: "none", Kind.HELIX_DOTS: "helix dots", Kind.CONTAINER_STRIPES: "container stripes",
	Kind.CIVIC_RINGS: "civic rings", Kind.STAR_GRID: "star-dot grid", Kind.SCAN_GLITCH: "scan-glitch bars",
}

# Spacing at pattern_scale 1.0, in reference pixels.
## Solace: distance between helix rows, dot step along a strand, strand amplitude and
## wavelength, dot radius (the back strand's dots are smaller: depth without colour).
const HELIX_ROW_GAP := 18.0
const HELIX_DOT_STEP := 6.0
const HELIX_AMP := 4.5
const HELIX_WAVELENGTH := 30.0
const HELIX_DOT_R := 1.6
const HELIX_BACK_DOT_R := 1.0
## Meridian: 45° stripes, gap between stripe centres and stripe width.
const STRIPE_GAP := 10.0
const STRIPE_WIDTH := 3.5
## Halcyon: a lattice of two-ring civic seals: cell size, outer and inner radius, stroke.
const RING_CELL := 22.0
const RING_OUTER_R := 7.5
const RING_INNER_R := 3.5
const RING_WIDTH := 1.4
## Segments per full circle for seal rings and ring-fill clip shapes.
const CIRCLE_SEGMENTS := 20
const CLIP_CIRCLE_SEGMENTS := 64
## Orbital: a dot lattice with a four-point star on every other node (checkerboard).
const STAR_CELL := 12.0
const STAR_DOT_R := 1.2
const STAR_ARM := 3.5
const STAR_WIDTH := 1.2
## REBEL_CELL: horizontal broken bars: row gap, bar width, and the bar/gap lengths drawn
## from a fixed integer hash per row and bar (so the glitch never changes frame to frame).
const GLITCH_ROW_GAP := 7.0
const GLITCH_WIDTH := 2.5
const GLITCH_MIN_BAR := 8.0
const GLITCH_MAX_BAR := 40.0
const GLITCH_MIN_GAP := 3.0
const GLITCH_MAX_GAP := 14.0
## The hash's resolution (lengths are picked in GLITCH_STEPS even steps).
const GLITCH_STEPS := 16
## Dashed lines: the base dash and gap lengths along a threat route.
const DASH_LEN := 10.0
const DASH_GAP := 6.0


## Fills `rect` on `ci` with pattern `kind` in `color` (alpha is the caller's).
static func fill_rect(ci: CanvasItem, rect: Rect2, kind: int, color: Color, pattern_scale: float = 1.0) -> void:
	var r := rect.abs()
	fill_polygon(ci, PackedVector2Array([r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)]), kind, color, pattern_scale)


## Fills the simple polygon `points` on `ci` with pattern `kind` in `color`.
static func fill_polygon(ci: CanvasItem, points: PackedVector2Array, kind: int, color: Color, pattern_scale: float = 1.0) -> void:
	if points.size() < 3 or kind == Kind.NONE:
		return
	var m := marks(kind, _bounds(points), pattern_scale)
	for d in m.dots:
		if Geometry2D.is_point_in_polygon(d.p, points):
			ci.draw_circle(d.p, d.r, color, true, -1.0, true)
	for line: PackedVector2Array in m.lines:
		for piece in Geometry2D.intersect_polyline_with_polygon(line, points):
			ci.draw_polyline(piece, color, m.width, true)


## Fills the ring (annulus) between `inner_r` and `outer_r` around `center`, e.g. a wheel
## bezel, with pattern `kind` in `color`.
static func fill_ring(ci: CanvasItem, center: Vector2, inner_r: float, outer_r: float, kind: int, color: Color, pattern_scale: float = 1.0) -> void:
	if outer_r <= inner_r or kind == Kind.NONE:
		return
	var outer := _circle(center, outer_r, CLIP_CIRCLE_SEGMENTS)
	var inner := _circle(center, inner_r, CLIP_CIRCLE_SEGMENTS)
	var m := marks(kind, Rect2(center - Vector2(outer_r, outer_r), Vector2(outer_r, outer_r) * 2.0), pattern_scale)
	for d in m.dots:
		var dist: float = d.p.distance_to(center)
		if dist <= outer_r and dist >= inner_r:
			ci.draw_circle(d.p, d.r, color, true, -1.0, true)
	for line: PackedVector2Array in m.lines:
		for piece in Geometry2D.intersect_polyline_with_polygon(line, outer):
			for part in Geometry2D.clip_polyline_with_polygon(piece, inner):
				ci.draw_polyline(part, color, m.width, true)


## Draws a threat route from `from` to `to` as a dashed line that carries pattern `kind`
## (§3.6; STYLE_GUIDE 5.3 adds the chevrons). `phase` (px) marches the dashes along the
## line; `width` is the dash stroke.
static func dashed_line(ci: CanvasItem, from: Vector2, to: Vector2, kind: int, color: Color, width: float = 2.0, pattern_scale: float = 1.0, phase: float = 0.0) -> void:
	for mark in dash_marks(from, to, kind, width, pattern_scale, phase):
		match mark.type:
			&"line":
				ci.draw_line(mark.a, mark.b, color, mark.w, true)
			&"dot":
				ci.draw_circle(mark.a, mark.r, color, true, -1.0, true)
			&"ring":
				ci.draw_arc(mark.a, mark.r, 0.0, TAU, CIRCLE_SEGMENTS, color, mark.w, true)


## The marks of a fill of `kind` over `bounds` (before clipping): {dots: [{p, r}], lines:
## [PackedVector2Array], width}. Anchored to the canvas origin; deterministic.
static func marks(kind: int, bounds: Rect2, pattern_scale: float = 1.0) -> Dictionary:
	var s := maxf(pattern_scale, 0.01)
	var out := {"dots": [], "lines": [], "width": 1.0}
	match kind:
		Kind.HELIX_DOTS:
			_helix(out, bounds, s)
		Kind.CONTAINER_STRIPES:
			_stripes(out, bounds, s)
		Kind.CIVIC_RINGS:
			_rings(out, bounds, s)
		Kind.STAR_GRID:
			_stars(out, bounds, s)
		Kind.SCAN_GLITCH:
			_glitch(out, bounds, s)
	return out


## The marks of a dashed threat line (see dashed_line): an array of {type: &"line" | &"dot"
## | &"ring", a, b, r, w}. Deterministic.
static func dash_marks(from: Vector2, to: Vector2, kind: int, width: float = 2.0, pattern_scale: float = 1.0, phase: float = 0.0) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var length := from.distance_to(to)
	if length <= 0.0:
		return out
	var s := maxf(pattern_scale, 0.01)
	var dir := (to - from) / length
	var nrm := Vector2(-dir.y, dir.x)
	var period := (DASH_LEN + DASH_GAP) * s
	var start := -fposmod(phase, period)
	var i := 0
	var t := start
	while t < length:
		var a := from + dir * clampf(t, 0.0, length)
		var b := from + dir * clampf(t + DASH_LEN * s, 0.0, length)
		var mid_t := t + DASH_LEN * s * 0.5
		var mid := from + dir * clampf(mid_t, 0.0, length)
		var seq := i + int(floor(phase / period))
		match kind:
			Kind.HELIX_DOTS:
				# Two strands of dots crossing along the route.
				for k in 3:
					var tt := t + DASH_LEN * s * (k / 2.0)
					if tt < 0.0 or tt > length:
						continue
					var off := sin(TAU * tt / (HELIX_WAVELENGTH * s)) * HELIX_AMP * s * 0.6
					var p := from + dir * tt
					out.append({"type": &"dot", "a": p + nrm * off, "r": width * 0.6})
					out.append({"type": &"dot", "a": p - nrm * off, "r": width * 0.4})
			Kind.CONTAINER_STRIPES:
				# A dash with a 45° tick across it (container stripe).
				if b != a:
					out.append({"type": &"line", "a": a, "b": b, "w": width})
				var tick := (dir + nrm).normalized() * width * 2.0
				out.append({"type": &"line", "a": mid - tick, "b": mid + tick, "w": width * 0.8})
			Kind.CIVIC_RINGS:
				# A short dash, then a small ring (a civic seal) in the gap.
				var half := from + dir * clampf(t + DASH_LEN * s * 0.5, 0.0, length)
				if half != a:
					out.append({"type": &"line", "a": a, "b": half, "w": width})
				if mid_t + DASH_GAP * s * 0.5 <= length and t >= 0.0:
					out.append({"type": &"ring", "a": from + dir * (t + DASH_LEN * s * 0.85), "r": width * 1.6, "w": width * 0.6})
			Kind.STAR_GRID:
				# Dot, dot, star.
				if posmod(seq, 3) == 2:
					out.append({"type": &"line", "a": mid - dir * width * 2.0, "b": mid + dir * width * 2.0, "w": width * 0.7})
					out.append({"type": &"line", "a": mid - nrm * width * 2.0, "b": mid + nrm * width * 2.0, "w": width * 0.7})
				else:
					out.append({"type": &"dot", "a": mid, "r": width * 0.7})
			Kind.SCAN_GLITCH:
				# Uneven dashes knocked sideways off the line.
				var len_k := _pick(seq, 0, GLITCH_STEPS)
				var bb := from + dir * clampf(t + DASH_LEN * s * lerpf(0.4, 1.3, len_k), 0.0, length)
				var shift := nrm * width * (float(posmod(_hash(seq * 7 + 3), 3)) - 1.0)
				if bb != a:
					out.append({"type": &"line", "a": a + shift, "b": bb + shift, "w": width})
			_:
				if b != a:
					out.append({"type": &"line", "a": a, "b": b, "w": width})
		t += period
		i += 1
	return out


# --- pattern generators ------------------------------------------------------------------

static func _helix(out: Dictionary, r: Rect2, s: float) -> void:
	var row := HELIX_ROW_GAP * s
	var step := HELIX_DOT_STEP * s
	var y := floorf(r.position.y / row) * row
	while y <= r.end.y + row:
		var x := floorf(r.position.x / step) * step
		while x <= r.end.x + step:
			var ph := TAU * x / (HELIX_WAVELENGTH * s)
			var off := sin(ph) * HELIX_AMP * s
			# The strand in front (cos > 0) gets the big dot; they swap where they cross.
			var front := cos(ph) >= 0.0
			out.dots.append({"p": Vector2(x, y + off), "r": (HELIX_DOT_R if front else HELIX_BACK_DOT_R) * s})
			out.dots.append({"p": Vector2(x, y - off), "r": (HELIX_BACK_DOT_R if front else HELIX_DOT_R) * s})
			x += step
		y += row


static func _stripes(out: Dictionary, r: Rect2, s: float) -> void:
	out.width = STRIPE_WIDTH * s
	var gap := STRIPE_GAP * s
	# Lines x - y = c (45°, rising to the right on screen); c spans the rect's corners.
	var c0 := floorf((r.position.x - r.end.y) / gap) * gap
	var c1 := r.end.x - r.position.y
	var c := c0
	while c <= c1 + gap:
		var y0 := r.position.y - gap
		var y1 := r.end.y + gap
		out.lines.append(PackedVector2Array([Vector2(c + y1, y1), Vector2(c + y0, y0)]))
		c += gap


static func _rings(out: Dictionary, r: Rect2, s: float) -> void:
	out.width = RING_WIDTH * s
	var cell := RING_CELL * s
	var y := floorf(r.position.y / cell) * cell
	var row := int(floorf(r.position.y / cell))
	while y <= r.end.y + cell:
		# Every other row shifts half a cell (a staggered seal lattice).
		var shift := cell * 0.5 if posmod(row, 2) == 1 else 0.0
		var x := floorf(r.position.x / cell) * cell - shift
		while x <= r.end.x + cell:
			var c := Vector2(x + cell * 0.5, y + cell * 0.5)
			var outer := _circle(c, RING_OUTER_R * s, CIRCLE_SEGMENTS)
			outer.append(outer[0])
			out.lines.append(outer)
			var inner := _circle(c, RING_INNER_R * s, CIRCLE_SEGMENTS)
			inner.append(inner[0])
			out.lines.append(inner)
			x += cell
		y += cell
		row += 1


static func _stars(out: Dictionary, r: Rect2, s: float) -> void:
	out.width = STAR_WIDTH * s
	var cell := STAR_CELL * s
	var j := int(floorf(r.position.y / cell))
	var y := j * cell
	while y <= r.end.y + cell:
		var i := int(floorf(r.position.x / cell))
		var x := i * cell
		while x <= r.end.x + cell:
			var p := Vector2(x, y)
			if posmod(i + j, 4) == 0 and posmod(j, 2) == 0:
				var arm := STAR_ARM * s
				out.lines.append(PackedVector2Array([p - Vector2(arm, 0), p + Vector2(arm, 0)]))
				out.lines.append(PackedVector2Array([p - Vector2(0, arm), p + Vector2(0, arm)]))
			else:
				out.dots.append({"p": p, "r": STAR_DOT_R * s})
			x += cell
			i += 1
		y += cell
		j += 1


static func _glitch(out: Dictionary, r: Rect2, s: float) -> void:
	out.width = GLITCH_WIDTH * s
	var row_gap := GLITCH_ROW_GAP * s
	var row := int(floorf(r.position.y / row_gap))
	var y := row * row_gap
	while y <= r.end.y + row_gap:
		# Each row starts at a fixed hashed offset left of the canvas-anchored rect, then
		# alternates bars and gaps of hashed length.
		var span := (GLITCH_MAX_BAR + GLITCH_MAX_GAP) * s
		var x := floorf(r.position.x / span) * span - _pick(row * 31, 0, GLITCH_STEPS) * span
		var k := 0
		while x <= r.end.x:
			var bar := lerpf(GLITCH_MIN_BAR, GLITCH_MAX_BAR, _pick(row * 131 + k, 1, GLITCH_STEPS)) * s
			var gap := lerpf(GLITCH_MIN_GAP, GLITCH_MAX_GAP, _pick(row * 131 + k, 2, GLITCH_STEPS)) * s
			out.lines.append(PackedVector2Array([Vector2(x, y), Vector2(x + bar, y)]))
			x += bar + gap
			k += 1
		y += row_gap
		row += 1


# --- helpers -----------------------------------------------------------------------------

## A fixed integer hash (no RNG): the same n always gives the same value.
static func _hash(n: int) -> int:
	var h := (n * 374761393 + 668265263) & 0x7FFFFFFF
	h = ((h ^ (h >> 13)) * 1274126177) & 0x7FFFFFFF
	return h ^ (h >> 16)


## A hashed fraction in [0, 1] in `steps` even steps for seed `n` and channel `salt`.
static func _pick(n: int, salt: int, steps: int) -> float:
	return float(posmod(_hash(n * 3 + salt), steps + 1)) / float(steps)


static func _bounds(points: PackedVector2Array) -> Rect2:
	var r := Rect2(points[0], Vector2.ZERO)
	for p in points:
		r = r.expand(p)
	return r


static func _circle(c: Vector2, radius: float, segments: int) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for k in segments:
		var a := TAU * k / segments
		pts.append(c + Vector2(cos(a), sin(a)) * radius)
	return pts
