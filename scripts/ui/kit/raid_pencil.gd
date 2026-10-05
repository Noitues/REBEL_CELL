class_name RaidPencil
extends RefCounted
## ART-6 3A: the Cell's grease pencil on the raid (ART_BIBLE v2 §1.2 "Grease pencil", §4.8
## "Pencil rules"): opaque wax (alpha 0.96), thick, a rough edge, a sheen line and a dark
## under-shadow so it reads day and night; yellow = our plan / valid, red = threat / invalid /
## loss; solid = what will happen, dashed = what-if. It writes on by its length and wipes off
## with a cloth wipe that trims it from its start (never an alpha fade). Static helpers that
## draw on any CanvasItem; no state, no RNG (the wobble is a hash of the stroke's seed).
##
## Seam: 1B's material kit brings the production grease pencil (a Line2D with a wax shader);
## the raid draws through these helpers so the swap is one file (DECISIONS "Art direction —
## ART-6 3A raid presentation"). Ported from art-concepts-r43 round 19-23 `ui19.pen_*`,
## `ui20.Pencil`, `ui21.Pencil` (jitter, circle turns 1.12, arrow heads, scribble, heavy word).

## Wax body alpha (§1.2: opaque wax 0.96).
const WAX_ALPHA := 0.96
## The under-shadow's offset (x the stroke width) and width (x the stroke width).
const SHADOW_OFFSET := Vector2(0.22, 0.34)
const SHADOW_WIDTH := 1.12
## The sheen line: width and offset to the stroke's left (x the stroke width), lift toward
## white and alpha.
const SHEEN_WIDTH := 0.22
const SHEEN_OFFSET := 0.2
const SHEEN_LIFT := 0.55
const SHEEN_ALPHA := 0.55
## The rough edge: resample step (px x width) and wobble (px x width).
const ROUGH_STEP := 1.6
const ROUGH_AMP := 0.16
## A hand circle goes round this many turns (it overlaps where it started; round 19).
const CIRCLE_TURNS := 1.12
const CIRCLE_SEGMENTS := 56
## Dashes (what-if): on and off lengths (x width).
const DASH_ON := 3.2
const DASH_OFF := 2.0
## Arrow head length (x width) and its spread (radians).
const HEAD_LEN := 3.0
const HEAD_SPREAD := 0.5
## Pencil words (§2.9 Permanent Marker rendered as wax): tracking (x the size), the wax
## keyline (x the size), the heavy pass's keyline (BREACHED), the underline's drop (x the
## size) and its overshoot.
const WORD_TRACKING := 0.06
const WORD_KEYLINE := 0.07
const WORD_HEAVY_KEYLINE := 0.13
const UNDERLINE_DROP := 0.22
const UNDERLINE_OVERSHOOT := 0.06
## The cloth wipe's smear: alpha of the faint smear the wipe leaves while it passes.
const SMEAR_ALPHA := 0.16


## A repeatable pseudo-random value in [-1, 1] for stroke `seed` at `i` (a hash: no RNG).
static func noise(seed: int, i: float) -> float:
	var v := sin(float(seed) * 12.9898 + i * 78.233) * 43758.5453
	return (v - floorf(v)) * 2.0 - 1.0


## A smooth wobble in [-1, 1] along a stroke (`t` in samples).
static func wobble(seed: int, t: float) -> float:
	var a := floorf(t / 3.0)
	var f := t / 3.0 - a
	f = f * f * (3.0 - 2.0 * f)
	return lerpf(noise(seed, a), noise(seed, a + 1.0), f)


## The total length of polyline `pts`.
static func length_of(pts: PackedVector2Array) -> float:
	var total := 0.0
	for i in pts.size() - 1:
		total += pts[i].distance_to(pts[i + 1])
	return total


## The part of `pts` from `from_u` to `to_u` of its length (0..1 each).
static func trimmed(pts: PackedVector2Array, from_u: float, to_u: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	if pts.size() < 2 or to_u <= from_u:
		return out
	var total := length_of(pts)
	if total <= 0.0 or not is_finite(total):
		return out
	var a := clampf(from_u, 0.0, 1.0) * total
	var b := clampf(to_u, 0.0, 1.0) * total
	var run := 0.0
	for i in pts.size() - 1:
		var seg := pts[i].distance_to(pts[i + 1])
		var s0 := run
		var s1 := run + seg
		run = s1
		if s1 < a or s0 > b or seg <= 0.0:
			continue
		var p0 := pts[i].lerp(pts[i + 1], clampf((a - s0) / seg, 0.0, 1.0))
		var p1 := pts[i].lerp(pts[i + 1], clampf((b - s0) / seg, 0.0, 1.0))
		if out.is_empty():
			out.append(p0)
		out.append(p1)
	return out


## `pts` resampled every `step` px and wobbled sideways by up to `amp` px (deterministic).
static func roughen(pts: PackedVector2Array, seed: int, amp: float, step: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	if pts.size() < 2 or step <= 0.0:
		return pts
	var total := length_of(pts)
	if total <= 0.0 or not is_finite(total):
		return pts
	var n := clampi(ceili(total / step), 1, 2048)
	for k in n + 1:
		var u := float(k) / n
		var p := _at(pts, u * total)
		var dir := _dir_at(pts, u * total)
		out.append(p + dir.orthogonal() * wobble(seed, k) * amp)
	return out


static func _at(pts: PackedVector2Array, d: float) -> Vector2:
	for i in pts.size() - 1:
		var seg := pts[i].distance_to(pts[i + 1])
		if d <= seg:
			return pts[i].lerp(pts[i + 1], d / maxf(seg, 0.0001))
		d -= seg
	return pts[pts.size() - 1]


static func _dir_at(pts: PackedVector2Array, d: float) -> Vector2:
	for i in pts.size() - 1:
		var seg := pts[i].distance_to(pts[i + 1])
		if d <= seg and seg > 0.0:
			return (pts[i + 1] - pts[i]) / seg
		d -= seg
	var n := pts.size()
	return (pts[n - 1] - pts[n - 2]).normalized() if n >= 2 else Vector2.RIGHT


## Lays one wax run (already trimmed and roughened) on `ci`: shadow, body, sheen, round caps.
static func _wax(ci: CanvasItem, pts: PackedVector2Array, col: Color, width: float) -> void:
	if pts.size() < 2:
		return
	var shadow := RaidSkin.pencil_shadow()
	var off := SHADOW_OFFSET * width
	var sh := PackedVector2Array()
	for p in pts:
		sh.append(p + off)
	ci.draw_polyline(sh, shadow, width * SHADOW_WIDTH, true)
	ci.draw_circle(sh[0], width * SHADOW_WIDTH * 0.5, shadow)
	ci.draw_circle(sh[sh.size() - 1], width * SHADOW_WIDTH * 0.5, shadow)
	var body := Color(col, col.a * WAX_ALPHA)
	ci.draw_polyline(pts, body, width, true)
	ci.draw_circle(pts[0], width * 0.5, body)
	ci.draw_circle(pts[pts.size() - 1], width * 0.5, body)
	var sheen := PackedVector2Array()
	for i in pts.size():
		var d := (pts[mini(i + 1, pts.size() - 1)] - pts[maxi(i - 1, 0)]).normalized()
		sheen.append(pts[i] - d.orthogonal() * width * SHEEN_OFFSET)
	ci.draw_polyline(sheen, Color(col.lerp(Palette.PAPER, SHEEN_LIFT), col.a * SHEEN_ALPHA), maxf(1.0, width * SHEEN_WIDTH), true)


## A pencil stroke along `pts`, written from `from_u` to `to_u` of its length (write-on:
## raise `to_u`; cloth wipe: raise `from_u`); dashed for a what-if.
static func stroke(ci: CanvasItem, pts: PackedVector2Array, col: Color, width: float, from_u: float = 0.0, to_u: float = 1.0,
		seed: int = 1, dashed: bool = false) -> void:
	if pts.size() < 2 or to_u <= from_u or width <= 0.0:
		return
	var rough := roughen(pts, seed, width * ROUGH_AMP, width * ROUGH_STEP)
	var part := trimmed(rough, from_u, to_u)
	if part.size() < 2:
		return
	if not dashed:
		_wax(ci, part, col, width)
		return
	var total := length_of(rough)
	var period := width * (DASH_ON + DASH_OFF)
	var on := width * DASH_ON
	var start := from_u * total
	var stop := to_u * total
	var d := floorf(start / period) * period
	var guard := 0
	while d < stop and guard < 512:
		guard += 1
		var a := maxf(d, start)
		var b := minf(d + on, stop)
		if b > a:
			_wax(ci, trimmed(rough, a / total, b / total), col, width)
		d += period


## Points of a hand-drawn ellipse round `c` (radii `rx`, `ry`) that goes round CIRCLE_TURNS
## times, starting top left, with a wobble.
static func circle_points(c: Vector2, rx: float, ry: float, seed: int = 1, turns: float = CIRCLE_TURNS) -> PackedVector2Array:
	var out := PackedVector2Array()
	var n := ceili(CIRCLE_SEGMENTS * turns)
	var a0 := -PI * 0.75 + noise(seed, 3.0) * 0.3
	for k in n + 1:
		var u := float(k) / n
		var a := a0 + TAU * turns * u
		# The pencil drifts outward a little on its second pass (round 19 hand_circle).
		var grow := 1.0 + 0.06 * u + 0.025 * wobble(seed, k * 0.5)
		out.append(c + Vector2(cos(a) * rx, sin(a) * ry) * grow)
	return out


## A hand circle round `c`, written to `to_u` (and wiped from `from_u`).
static func circle(ci: CanvasItem, c: Vector2, rx: float, ry: float, col: Color, width: float, from_u: float = 0.0, to_u: float = 1.0, seed: int = 1) -> void:
	stroke(ci, circle_points(c, rx, ry, seed), col, width, from_u, to_u, seed)


## An X over `c` (arm `r`): two strokes, the second after the first.
static func cross(ci: CanvasItem, c: Vector2, r: float, col: Color, width: float, to_u: float = 1.0, seed: int = 1) -> void:
	var a := PackedVector2Array([c + Vector2(-r, -r * 0.85), c + Vector2(r, r * 0.8)])
	var b := PackedVector2Array([c + Vector2(r, -r * 0.85), c + Vector2(-r * 0.95, r * 0.9)])
	stroke(ci, a, col, width, 0.0, clampf(to_u * 2.0, 0.0, 1.0), seed)
	stroke(ci, b, col, width, 0.0, clampf(to_u * 2.0 - 1.0, 0.0, 1.0), seed + 7)


## A tick at `c` (size `s`), written to `to_u`.
static func tick(ci: CanvasItem, c: Vector2, s: float, col: Color, width: float, to_u: float = 1.0, seed: int = 1) -> void:
	var pts := PackedVector2Array([c + Vector2(-s * 0.5, -s * 0.05), c + Vector2(-s * 0.1, s * 0.4), c + Vector2(s * 0.6, -s * 0.55)])
	stroke(ci, pts, col, width, 0.0, to_u, seed)


## An arrow along `pts` with a head at its end (drawn once the shaft is written), dashed or
## solid; `to_u` writes it on.
static func arrow(ci: CanvasItem, pts: PackedVector2Array, col: Color, width: float, to_u: float = 1.0, seed: int = 1, dashed: bool = false) -> void:
	if pts.size() < 2:
		return
	var shaft := clampf(to_u / 0.85, 0.0, 1.0)
	stroke(ci, pts, col, width, 0.0, shaft, seed, dashed)
	if to_u <= 0.85:
		return
	var head_u := (to_u - 0.85) / 0.15
	var tip := pts[pts.size() - 1]
	var dir := (tip - pts[pts.size() - 2]).normalized()
	var k := pts.size() - 2
	while k > 0 and tip.distance_to(pts[k]) < width * 2.0:
		k -= 1
	dir = (tip - pts[k]).normalized()
	var head_len := width * HEAD_LEN
	for s: float in [-1.0, 1.0]:
		var wing := tip - dir.rotated(s * HEAD_SPREAD) * head_len
		stroke(ci, PackedVector2Array([wing, tip]), col, width, 0.0, head_u, seed + int(s * 3.0))


## A tight zigzag scribbled through `pts` (the part of a route a what-if would remove).
static func scribble_points(pts: PackedVector2Array, amp: float, pitch: float, seed: int = 1) -> PackedVector2Array:
	var out := PackedVector2Array()
	var total := length_of(pts)
	if total <= 0.0 or pitch <= 0.0:
		return out
	var n := clampi(ceili(total / pitch), 2, 512)
	for i in n + 1:
		var d := total * i / n
		var p := _at(pts, d)
		var dir := _dir_at(pts, d)
		var side := 1.0 if i % 2 == 0 else -1.0
		out.append(p + dir.orthogonal() * amp * side * (0.85 + 0.15 * noise(seed, i)))
	return out


## The pencil face (§2.9 Permanent Marker).
static func font() -> Font:
	return Palette.marker()


## The size of pencil word `text` at `px` (its advance with the tracking, and the face's height).
static func word_size(text: String, px: int) -> Vector2:
	var f := font()
	var w := 0.0
	for i in text.length():
		w += f.get_string_size(text[i], HORIZONTAL_ALIGNMENT_LEFT, -1, px).x + px * WORD_TRACKING
	return Vector2(maxf(0.0, w - px * WORD_TRACKING), f.get_height(px))


## A pencil word centred on `centre`, tilted `tilt` radians: written letter by letter to
## `write_u` and wiped letter by letter from the left to `wipe_u` (a cloth wipe, with the
## faint smear it leaves passing). `heavy`: one slow heavy wax pass (BREACHED) with an
## underline written after the word (`underline_u`).
static func word(ci: CanvasItem, text: String, centre: Vector2, px: int, col: Color, write_u: float = 1.0, wipe_u: float = 0.0,
		tilt: float = -0.03, heavy: bool = false, underline_u: float = 0.0, seed: int = 1) -> void:
	if text == "" or px <= 0 or write_u <= 0.0 or wipe_u >= 1.0:
		return
	var f := font()
	var size := word_size(text, px)
	var n := text.length()
	ci.draw_set_transform(centre, tilt, Vector2.ONE)
	var x := -size.x * 0.5
	var base := f.get_ascent(px) - size.y * 0.5
	var keyline := maxi(1, roundi(px * (WORD_HEAVY_KEYLINE if heavy else WORD_KEYLINE)))
	var shadow := RaidSkin.pencil_shadow()
	var body := Color(col, col.a * WAX_ALPHA)
	var wiped_to := -size.x * 0.5
	for i in n:
		var ch := text[i]
		var adv := f.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
		var shown := clampf(write_u * n - i, 0.0, 1.0)
		var gone := clampf(wipe_u * n - i, 0.0, 1.0)
		var bob := wobble(seed, i * 3.0) * px * 0.04
		if gone > 0.0:
			wiped_to = x + adv * gone
		if shown > 0.0 and gone < 1.0:
			var a := minf(shown * 2.0, 1.0) * (1.0 - gone)
			var at := Vector2(x, base + bob)
			var off := SHADOW_OFFSET * keyline * 1.6
			ci.draw_string_outline(f, at + off, ch, HORIZONTAL_ALIGNMENT_LEFT, -1, px, keyline + 2, Color(shadow, shadow.a * a))
			ci.draw_string_outline(f, at, ch, HORIZONTAL_ALIGNMENT_LEFT, -1, px, keyline, Color(body, body.a * a))
			ci.draw_string(f, at, ch, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color(body, body.a * a))
		x += adv + px * WORD_TRACKING
	if wipe_u > 0.0:
		# The cloth's smear trails its front.
		var smear := Rect2(Vector2(-size.x * 0.5, -size.y * 0.25), Vector2(maxf(0.0, wiped_to + size.x * 0.5), size.y * 0.5))
		ci.draw_rect(smear, Color(col, SMEAR_ALPHA * (1.0 - wipe_u)))
	if heavy and underline_u > 0.0:
		var y := size.y * 0.5 + px * UNDERLINE_DROP * 0.4
		var over := size.x * UNDERLINE_OVERSHOOT
		var line := PackedVector2Array([Vector2(-size.x * 0.5 - over, y), Vector2(size.x * 0.5 + over, y + px * 0.05)])
		ci.draw_set_transform(Vector2.ZERO)
		var xf := Transform2D(tilt, centre)
		stroke(ci, xf * line, col, maxf(2.0, px * WORD_HEAVY_KEYLINE * 1.4), clampf(wipe_u, 0.0, 1.0), underline_u, seed + 11)
	ci.draw_set_transform(Vector2.ZERO)
