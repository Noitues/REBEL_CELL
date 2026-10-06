class_name FxDraw
extends RefCounted
## ART-2 2C (ART_BIBLE v2 §3.18, §3.20): how the combat FX layer draws the locked effect
## set's shapes (the slap's contact ring, the card's liner, DEFRAG bricks and SANDBOX hex
## plates, the evade token, glitch tears, the drone's hex, crack lines and code streaks, a
## shockwave). Static draw calls on the layer's canvas item; every shape takes its progress
## `p` (0..1) and its alpha, so a shape is a pure function of time. Colours are tokens.

## Bricks: a course's depth and a brick's angular share of the wall (shares of the rim),
## the gap between bricks (px) and how far they pop from (scale) before settling.
const BRICK_DEPTH := 0.13
const BRICK_COURSES := 2
const BRICK_GAP := 2.0
const POP_FROM := 1.3
## A brick's pop shape (named, ANIM-R6 rule: no inline tween shapes).
const POP_TRANS := Tween.TRANS_BACK
const POP_EASE := Tween.EASE_OUT
## A wall spans this angle (rad) round the side facing the foe, standing this far past the
## rim (share of the radius).
const WALL_SPAN := 1.2
const WALL_OUT := 0.06
## Hex plates: their radius as a share of the wheel's, and the ripple's width (share of p).
const HEX_SHARE := 0.11
const RIPPLE_W := 0.25
## A shape's outline width (px) and the wall's settled alpha (it settles to 60 %).
const LINE_W := 2.0
const SETTLED_ALPHA := 0.6
## The evade token (the art pass's own sticker, `assets/fx/stickers/evade_token.png`): its size (px at
## text scale 1.0).
const TOKEN_PX := 44.0
const TOKEN_TEX := preload("res://assets/fx/stickers/evade_token.png")
## Glitch tears: bands across the slice, their height (px) and how far they shift (px).
const TEAR_BANDS := 8
const TEAR_H := 6.0
const TEAR_SHIFT := 9.0
## Crack lines and code streaks (§3.20 crit): their count comes from the motion entry.
const CRACK_SEGMENTS := 4
const CRACK_JITTER := 0.35
const STREAK_TEXT := "0110 1001"
const STREAK_FONT := 14
## Drone hex outline radius (px at text scale 1.0).
const DRONE_HEX := 21.0
## The art pass's drone sticker and its six pieces (`assets/fx/stickers/drone*.png`, exported at 1x): the
## hex's radius and centre in `drone.png`, and where the pieces' offsets are measured from (the image centre).
const DRONE_TEX := preload("res://assets/fx/stickers/drone.png")
const DRONE_TEX_HEX_R := 40.0
const DRONE_TEX_HEX_CENTRE := Vector2(64.5, 65.0)
const DRONE_PIECE_TEX: Array[Texture2D] = [
	preload("res://assets/fx/stickers/drone_piece_0.png"), preload("res://assets/fx/stickers/drone_piece_1.png"),
	preload("res://assets/fx/stickers/drone_piece_2.png"), preload("res://assets/fx/stickers/drone_piece_3.png"),
	preload("res://assets/fx/stickers/drone_piece_4.png"), preload("res://assets/fx/stickers/drone_piece_5.png"),
]
## Each piece's centre offset (px at 1x, from the image centre) and flight direction (rad), as the manifest
## records them for `fx_r22._pieces_from`.
const DRONE_PIECES := [
	[Vector2(24.5, -26.5), -1.0472], [Vector2(25.5, 0.5), 0.0], [Vector2(25.0, 30.5), 1.0472],
	[Vector2(-25.0, 30.5), 2.0944], [Vector2(-26.0, 0.5), 3.1416], [Vector2(-24.5, -26.5), 4.1888],
]
## The clamp that springs open when a drone goes (rad it swings).
const CLAMP_SWING := 1.1
const SEGMENTS := 40


## Hash noise 0..1.
static func _h(a: int, b: int, c: int = 0) -> float:
	return BitPath.noise(a, b, c)


## The slap's white contact ring at `c` growing from `r0` by `grow` px, with four impact
## ticks (§3.18 step 5).
static func slap_ring(ci: CanvasItem, c: Vector2, r0: float, grow: float, p: float, alpha: float) -> void:
	var r := r0 + grow * p
	var a := alpha * (1.0 - p)
	ci.draw_arc(c, r, 0.0, TAU, SEGMENTS, Color(Palette.PAPER, a), lerpf(6.0, 1.5, p), true)
	for k in 4:
		var ang := PI * 0.25 + k * PI * 0.5
		var d := Vector2(cos(ang), sin(ang))
		ci.draw_line(c + d * (r + 4.0), c + d * (r + 4.0 + 10.0 * (1.0 - p)), Color(Palette.PAPER, a), 2.0, true)


## The faint liner left in the hand slot when a sticker peels off (§3.18 step 3).
static func liner(ci: CanvasItem, rect: Rect2, rot: float, alpha: float) -> void:
	var c := rect.get_center()
	var hs := rect.size * 0.5
	var pts := PackedVector2Array()
	for v in [Vector2(-hs.x, -hs.y), Vector2(hs.x, -hs.y), Vector2(hs.x, hs.y), Vector2(-hs.x, hs.y), Vector2(-hs.x, -hs.y)]:
		pts.append(c + (v as Vector2).rotated(rot))
	ci.draw_polyline(pts, Color(Palette.PAPER, alpha), LINE_W, true)


## DEFRAG bricks (§3.20 block gain): `n` bricks in BRICK_COURSES courses round the side of
## the wheel (`c`, radius `r`) facing angle `face`, popping in course by course (inner
## course first) over the first half of `p`, then the wall settles to SETTLED_ALPHA and
## fades over its last quarter. `col` is the wall's colour.
static func bricks(ci: CanvasItem, c: Vector2, r: float, face: float, n: int, col: Color, p: float, alpha: float) -> void:
	var per := maxi(1, ceili(float(n) / BRICK_COURSES))
	var depth := r * BRICK_DEPTH
	var fade := 1.0 - clampf((p - 0.75) / 0.25, 0.0, 1.0)
	for k in n:
		var course := k / per
		var i := k % per
		var appear := float(k) / maxf(1.0, float(n)) * 0.5
		var q := clampf((p - appear) / 0.12, 0.0, 1.0)
		if q <= 0.0:
			continue
		var pop := lerpf(POP_FROM, 1.0, Tween.interpolate_value(0.0, 1.0, q, 1.0, POP_TRANS, POP_EASE))
		var r0 := r * (1.0 + WALL_OUT) + course * (depth + BRICK_GAP)
		# Each course is offset by half a brick (a running bond).
		var step := WALL_SPAN / per
		var a0 := face - WALL_SPAN * 0.5 + step * (i + (0.5 if course % 2 == 1 else 0.0))
		var a1 := a0 + step - BRICK_GAP / r0
		var mid := (a0 + a1) * 0.5
		var hw := (a1 - a0) * 0.5 * pop
		var poly := PackedVector2Array()
		for v in [[mid - hw, r0], [mid + hw, r0], [mid + hw, r0 + depth * pop], [mid - hw, r0 + depth * pop]]:
			poly.append(c + Vector2(cos(v[0]), sin(v[0])) * float(v[1]))
		var settle := lerpf(1.0, SETTLED_ALPHA, clampf((p - 0.5) / 0.25, 0.0, 1.0))
		var a := alpha * fade * settle
		ci.draw_colored_polygon(poly, Color(col, 0.55 * a))
		poly.append(poly[0])
		ci.draw_polyline(poly, Color(col.lerp(Palette.PAPER, 0.4), a), LINE_W, true)


## SANDBOX hex plates (§3.20 shield gain): `n` plates tiling out over the facing side from
## the middle, a white ripple running across them after they land, fading at the end.
static func hexes(ci: CanvasItem, c: Vector2, r: float, face: float, n: int, col: Color, p: float, alpha: float) -> void:
	var hr := r * HEX_SHARE
	var fade := 1.0 - clampf((p - 0.75) / 0.25, 0.0, 1.0)
	var ring := r * (1.0 + WALL_OUT) + hr
	var step := hr * 1.8 / ring
	for k in n:
		# Out from the middle: 0, +1, -1, +2, -2 ...
		var off := ((k + 1) / 2) * (1 if k % 2 == 1 else -1)
		var course := 0 if absi(off) % 2 == 0 else 1
		var ang := face + off * step * 0.5
		var appear := float(k) / maxf(1.0, float(n)) * 0.45
		var q := clampf((p - appear) / 0.12, 0.0, 1.0)
		if q <= 0.0:
			continue
		var pop := lerpf(POP_FROM * 0.6, 1.0, Tween.interpolate_value(0.0, 1.0, q, 1.0, POP_TRANS, POP_EASE))
		var at := c + Vector2(cos(ang), sin(ang)) * (ring + course * hr * 1.55)
		var ripple := 1.0 - clampf(absf((p - 0.55) * 4.0 - float(k) / maxf(1.0, float(n))) / RIPPLE_W, 0.0, 1.0)
		var fill := Color(col.lerp(Palette.PAPER, ripple * 0.7), (0.4 + 0.4 * ripple) * alpha * fade)
		var hex := _hex(at, hr * pop * 0.92)
		ci.draw_colored_polygon(hex, fill)
		hex.append(hex[0])
		ci.draw_polyline(hex, Color(col.lerp(Palette.PAPER, 0.5), alpha * fade), LINE_W, true)


static func _hex(at: Vector2, r: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	for k in 6:
		var a := PI / 6.0 + k * PI / 3.0
		out.append(at + Vector2(cos(a), sin(a)) * r)
	return out


## The `>>` token sticker (§3.20 evade): the art pass's own sticker at `at`, `s` its scale, alpha `alpha`.
## `_col` is kept for the callers: the sticker carries its own green.
static func token(ci: CanvasItem, at: Vector2, s: float, _col: Color, alpha: float) -> void:
	var size := TOKEN_PX * Settings.text_scale * s
	ci.draw_texture_rect(TOKEN_TEX, Rect2(at - Vector2(size, size) * 0.5, Vector2(size, size)), false, Color(Palette.NO_TINT, alpha))


## Glitch tears (§3.20 corrupt): TEAR_BANDS shifted bands over `rect`, revealed left to
## right up to `wipe` (0..1), doubled (a second offset copy) in `col2`.
static func tears(ci: CanvasItem, rect: Rect2, wipe: float, col: Color, col2: Color, alpha: float, seed: int) -> void:
	var w := rect.size.x * clampf(wipe, 0.0, 1.0)
	if w <= 0.0:
		return
	for k in TEAR_BANDS:
		var y := rect.position.y + rect.size.y * _h(seed, k)
		var shift := (_h(seed, k, 1) - 0.5) * 2.0 * TEAR_SHIFT
		ci.draw_rect(Rect2(Vector2(rect.position.x + shift, y), Vector2(w, TEAR_H)), Color(col, 0.9 * alpha))
		ci.draw_rect(Rect2(Vector2(rect.position.x - shift * 0.6, y + TEAR_H), Vector2(w, TEAR_H * 0.5)), Color(col2, 0.5 * alpha))


## The drone's hex outline packing in as its bits arrive (`fill` 0..1) and its sticker
## slapping on at the end (`slap` 0..1, a squash).
static func drone_hex(ci: CanvasItem, at: Vector2, col: Color, fill: float, slap: float, alpha: float) -> void:
	var r := DRONE_HEX * Settings.text_scale
	var hex := _hex(at, r)
	var n := maxi(2, roundi(7.0 * clampf(fill, 0.0, 1.0)))
	var outline := hex.duplicate()
	outline.append(hex[0])
	ci.draw_polyline(outline.slice(0, n), Color(col, alpha), LINE_W + 1.0, true)
	if slap > 0.0:
		var sc := CardFx.slap_scale(clampf(slap, 0.0, 1.0)) * (r / DRONE_TEX_HEX_R)
		ci.draw_set_transform(at, 0.0, sc)
		ci.draw_texture(DRONE_TEX, -DRONE_TEX_HEX_CENTRE, Color(Palette.NO_TINT, alpha))
		ci.draw_set_transform(Vector2.ZERO)


## A cracked hex popping apart and its clamp springing open (§3.20 drone destroyed v3).
static func drone_burst(ci: CanvasItem, at: Vector2, _col: Color, p: float, fly: float) -> void:
	var r := DRONE_HEX * Settings.text_scale
	var a := 1.0 - p
	var sc := r / DRONE_TEX_HEX_R
	# The six pieces of the art pass's sticker fly out along their own directions.
	for k in DRONE_PIECES.size():
		var piece := DRONE_PIECE_TEX[k]
		var row: Array = DRONE_PIECES[k]
		var centre := at + (row[0] as Vector2) * sc + Vector2.from_angle(float(row[1])) * fly * p
		var size := piece.get_size() * sc
		ci.draw_texture_rect(piece, Rect2(centre - size * 0.5, size), false, Color(Palette.NO_TINT, a))
	# The clamp: two arms off the bezel side swing open.
	for s in [-1.0, 1.0]:
		var arm := Vector2(0, -r * 1.4).rotated(s * CLAMP_SWING * p)
		ci.draw_line(at + Vector2(0, -r), at + Vector2(0, -r) + arm * 0.6, Color(Palette.PAPER, a), LINE_W, true)
	# The crack: a white zigzag across the hex, at its start.
	if p < 0.4:
		ci.draw_polyline(PackedVector2Array([at + Vector2(-r, -r * 0.2), at + Vector2(-r * 0.2, r * 0.15), at + Vector2(r * 0.3, -r * 0.25), at + Vector2(r, r * 0.2)]),
			Color(Palette.PAPER, 1.0 - p / 0.4), LINE_W, true)


## Crack lines (§3.20 crit / enemy defeated): `n` jagged lines from `at` out to `reach` px,
## drawn on over the first half of `p` and fading over the rest.
static func cracks(ci: CanvasItem, at: Vector2, n: int, reach: float, p: float, seed: int, col: Color = Palette.PAPER) -> void:
	var grow := clampf(p * 4.0, 0.0, 1.0)
	var a := 1.0 - clampf((p - 0.3) / 0.4, 0.0, 1.0)
	for k in n:
		var ang := TAU * (k + _h(seed, k)) / maxf(1.0, float(n))
		var pts := PackedVector2Array([at])
		for s in CRACK_SEGMENTS:
			var t := float(s + 1) / CRACK_SEGMENTS * grow
			var jig := (_h(seed, k, s + 2) - 0.5) * CRACK_JITTER
			pts.append(at + Vector2(cos(ang + jig), sin(ang + jig)) * reach * t)
		ci.draw_polyline(pts, Color(col, a), LINE_W + 1.0, true)


## Code streaks (§3.20 crit): `n` `0110 1001` streaks flying out from `at` along the crack
## angles over the first `fly` share of `p`, then gone (they shatter into shards).
static func streaks(ci: CanvasItem, at: Vector2, n: int, reach: float, p: float, fly: float, col: Color, seed: int) -> void:
	if p >= fly:
		return
	var q := p / maxf(0.001, fly)
	var fs := roundi(STREAK_FONT * Settings.text_scale)
	for k in n:
		var ang := TAU * (k + _h(seed, k)) / maxf(1.0, float(n))
		var d := Vector2(cos(ang), sin(ang))
		var pos := at + d * reach * q
		ci.draw_set_transform(pos, ang, Vector2.ONE)
		ci.draw_string_outline(Palette.mono(), Vector2.ZERO, STREAK_TEXT, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, 4, Color(Palette.NIGHT_SKY, 0.9))
		ci.draw_string(Palette.mono(), Vector2.ZERO, STREAK_TEXT, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col.lerp(Palette.PAPER, 0.3))
	ci.draw_set_transform(Vector2.ZERO)


## A shockwave ring from `c` (§3.20 enemy defeated: the hub shockwave).
static func shockwave(ci: CanvasItem, c: Vector2, r0: float, r1: float, p: float, col: Color) -> void:
	var r := lerpf(r0, r1, p)
	ci.draw_arc(c, r, 0.0, TAU, SEGMENTS * 2, Color(col, (1.0 - p) * 0.9), lerpf(10.0, 1.0, p), true)
	ci.draw_arc(c, r * 0.92, 0.0, TAU, SEGMENTS * 2, Color(Palette.PAPER, (1.0 - p) * 0.6), 2.0, true)


## A 3-frame pixel tear at a hit (§3.20): `bands` offset strips round `at`.
static func pixel_tear(ci: CanvasItem, at: Vector2, size: float, col: Color, frame: int, seed: int) -> void:
	for k in 3:
		var y := at.y + (_h(seed, k, frame) - 0.5) * size
		var x := (_h(seed, k + 5, frame) - 0.5) * size * 0.6
		ci.draw_rect(Rect2(Vector2(at.x - size * 0.5 + x, y), Vector2(size, 3.0)), Color(col, 0.8))
