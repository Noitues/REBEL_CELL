class_name RaidSocket
extends RefCounted
## ART-6 3A: a Cell node on the raid map as a circuit socket (ART_BIBLE v2 §4.8 "Network on
## the street = circuit inlay", round 22 `node_status_key`, round 21 `node_health`): a chip
## frame with pins and a pin-1 notch, the node's glyph, an inner lit fill. No tag: the type
## is the glyph; the status is the frame's colour and pattern:
## - HOLDS: a solid green frame, pins lit, the fill full (CORE: pink).
## - Health v2: the outline and the glyph stay lit; only the inner lit fill drains from the
##   north point to the south point, with a faint hatch over the drained part and a bright
##   drain line; repair raises it again (south to north).
## - DOWN (DECISIONS 2026-10-05 ruling 11): the Site markers' white lightning bolt across a
##   greyed socket, at every zoom (no amber dashed socket).
## - TAKEN: a burnt socket with embers (the node is gone; reclaim and reinstall).
## - Forecast: a dashed outer ring in the projected outcome's colour (DOWN amber, TAKEN red).
## - Drag: a white frame while a defence can go there; red frame + X where it can't.
## Static drawing on any CanvasItem; view only.

const STATE_HOLDS := "holds"
const STATE_DOWN := "down"
const STATE_TAKEN := "taken"
const DRAG_VALID := "valid"
const DRAG_INVALID := "invalid"

## Node types (content/nodes ids) and the glyph each draws (§4.8: Relay all-targets arrows,
## Firewall, Vault safe door, Proxy fingerprint, Safehouse key, CORE pink hex).
const GLYPH_RELAY := "relay"
const GLYPH_FIREWALL := "firewall"
const GLYPH_VAULT := "vault"
const GLYPH_PROXY := "proxy"
const GLYPH_SAFEHOUSE := "safehouse"
const GLYPH_COMPILER := "compiler"
const GLYPH_CORE := "core"
const GLYPH_OF := {
	&"relay": GLYPH_RELAY, &"firewall_relay": GLYPH_FIREWALL, &"vault_terminal": GLYPH_VAULT,
	&"proxy_relay": GLYPH_PROXY, &"safehouse": GLYPH_SAFEHOUSE, &"compiler_rack": GLYPH_COMPILER,
	&"home_server": GLYPH_CORE,
}

## The socket's half width and half height (x the map icon radius: an isometric chip).
const HALF := Vector2(1.9, 1.1)
## The inner track's share of the frame, the frame and track widths (x radius).
const INNER := 0.72
const FRAME_W := 0.16
const TRACK_W := 0.09
## Pins per edge, their length and width (x radius).
const PINS := 5
const PIN_LEN := 0.22
const PIN_W := 0.07
## The lit fill's alpha, the drained hatch's alpha and spacing (x radius), the drain line's lift.
const FILL_ALPHA := 0.34
const HATCH_ALPHA := 0.22
const HATCH_STEP := 0.22
const DRAIN_LIFT := 0.6
## The glyph's size (x radius) and its lift toward white.
const GLYPH_SIZE := 0.62
const GLYPH_LIFT := 0.25
## A dark keyline under the frame (x radius) and its alpha.
const KEYLINE := 0.14
## The frame's soft glow (x radius) and its alpha (light spill, §1.2).
const GLOW_W := 0.55
const GLOW_ALPHA := 0.22
## DOWN: the grey it fades to and the bolt's size (x radius) and width.
const DOWN_GREY := 0.7
const BOLT := 1.25
const BOLT_W := 0.16
## TAKEN: embers (count, size x radius).
const EMBERS := 9
const EMBER := 0.07
## Forecast ring: its size (x the frame), dash count and width (x radius).
const FORECAST_OUT := 1.32
const FORECAST_DASHES := 16
const FORECAST_W := 0.12
## Health below this share reads red on its track (round 22 key: "track turns red under 1/3").
const CRITICAL := 1.0 / 3.0


## The glyph id of node type `node_type` ("relay" when unknown).
static func glyph_of(node_type: StringName) -> String:
	return GLYPH_OF.get(node_type, GLYPH_RELAY)


## The colour a socket's frame takes for its node: CORE pink, every other owned node the
## "holds" green (§4.8: owned sockets shift from map lime to holds green).
static func frame_color(glyph: String) -> Color:
	return Palette.CELL_PINK if glyph == GLYPH_CORE else Palette.GAIN


## The socket's outline points round `c` at radius `r` (scale `s` of the frame).
static func diamond(c: Vector2, r: float, s: float = 1.0) -> PackedVector2Array:
	var h := HALF * r * s
	return PackedVector2Array([c + Vector2(0, -h.y), c + Vector2(h.x, 0), c + Vector2(0, h.y), c + Vector2(-h.x, 0)])


## The part of convex polygon `poly` at or below `y` (screen y grows down).
static func below(poly: PackedVector2Array, y: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	var n := poly.size()
	for i in n:
		var a := poly[i]
		var b := poly[(i + 1) % n]
		var a_in := a.y >= y
		var b_in := b.y >= y
		if a_in:
			out.append(a)
		if a_in != b_in and absf(b.y - a.y) > 0.0001:
			out.append(a.lerp(b, (y - a.y) / (b.y - a.y)))
	return out


## The box a socket at `c`, radius `r` covers (its pins and forecast ring included).
static func rect(c: Vector2, r: float) -> Rect2:
	var h := HALF * r * FORECAST_OUT
	return Rect2(c - h, h * 2.0)


## Draws a socket at `c` (radius `r`, the map icon's) on `ci`. `spec`: glyph (GLYPH_*),
## state (STATE_*), health (0..1), forecast ("" / STATE_DOWN / STATE_TAKEN), dock (""
## / DRAG_*), alpha, seed (embers).
static func draw(ci: CanvasItem, c: Vector2, r: float, spec: Dictionary) -> void:
	var glyph := String(spec.get("glyph", GLYPH_RELAY))
	var state := String(spec.get("state", STATE_HOLDS))
	var health := clampf(float(spec.get("health", 1.0)), 0.0, 1.0)
	var alpha := float(spec.get("alpha", 1.0))
	var drag := String(spec.get("dock", ""))
	var col := frame_color(glyph)
	if state == STATE_DOWN:
		col = col.lerp(Palette.DISABLED, DOWN_GREY)
	elif state == STATE_TAKEN:
		col = Palette.DISABLED.darkened(0.35)
	if drag == DRAG_VALID:
		col = Palette.TEXT_HI
	elif drag == DRAG_INVALID:
		col = Palette.HARM
	col = Color(col, col.a * alpha)
	var outer := diamond(c, r)
	var inner := diamond(c, r, INNER)
	var ink := Color(Palette.NIGHT_SKY, 0.9 * alpha)
	# Dark plate and keyline: readable over any street.
	ci.draw_colored_polygon(outer, Color(Palette.NIGHT_SKY, 0.82 * alpha))
	if state == STATE_TAKEN:
		_burnt(ci, c, r, alpha, int(spec.get("seed", 1)))
	else:
		_fill(ci, c, r, inner, col, health, alpha)
	_pins(ci, outer, c, r, col, ink)
	ci.draw_polyline(_closed(outer), Color(col, col.a * GLOW_ALPHA), r * GLOW_W, true)
	ci.draw_polyline(_closed(outer), ink, r * (FRAME_W + KEYLINE), true)
	ci.draw_polyline(_closed(outer), col, r * FRAME_W, true)
	var track := col
	if state == STATE_HOLDS and health < CRITICAL and drag == "":
		track = Color(Palette.HARM, alpha)
	ci.draw_polyline(_closed(inner), track, r * TRACK_W, true)
	# The pin-1 notch at the south point (lit).
	var s := outer[2]
	ci.draw_colored_polygon(PackedVector2Array([s + Vector2(-r * 0.32, -r * 0.05), s + Vector2(r * 0.32, -r * 0.05), s + Vector2(0, r * 0.22)]), col)
	if state != STATE_TAKEN:
		draw_glyph(ci, glyph, c, r * GLYPH_SIZE, Color(col.lerp(Palette.TEXT_HI, GLYPH_LIFT), alpha))
	if state == STATE_DOWN:
		bolt(ci, c, r * BOLT, alpha)
	var forecast := String(spec.get("forecast", ""))
	if forecast != "" and forecast != STATE_HOLDS and drag == "":
		forecast_ring(ci, c, r, Palette.WARN if forecast == STATE_DOWN else Palette.HARM, alpha)
	if drag == DRAG_INVALID:
		var arm := r * 0.9
		for d: Vector2 in [Vector2(1, 0.55), Vector2(1, -0.55)]:
			ci.draw_line(c - d * arm, c + d * arm, ink, r * 0.26)
			ci.draw_line(c - d * arm, c + d * arm, col, r * 0.14)


static func _closed(poly: PackedVector2Array) -> PackedVector2Array:
	var out := poly.duplicate()
	out.append(poly[0])
	return out


## The inner lit fill at `health`: lit south of the drain line, hatched north of it.
static func _fill(ci: CanvasItem, c: Vector2, r: float, inner: PackedVector2Array, col: Color, health: float, alpha: float) -> void:
	var top := inner[0].y
	var bottom := inner[2].y
	var cut := lerpf(bottom, top, health)
	var lit := below(inner, cut)
	if lit.size() >= 3:
		ci.draw_colored_polygon(lit, Color(col, FILL_ALPHA * alpha))
	if health >= 1.0:
		return
	# The drained part: a faint hatch in the active colour.
	var step := r * HATCH_STEP
	var hw := HALF.x * r * INNER
	var x := -hw * 2.0
	while x < hw * 2.0:
		var a := Vector2(c.x + x, top)
		var b := Vector2(c.x + x + (cut - top), cut)
		var seg := _clip_to(inner, a, b)
		if seg.size() == 2:
			ci.draw_line(seg[0], seg[1], Color(col, HATCH_ALPHA * alpha), maxf(1.0, r * 0.04))
		x += step
	if health > 0.0:
		var line := _clip_to(inner, Vector2(c.x - hw * 1.2, cut), Vector2(c.x + hw * 1.2, cut))
		if line.size() == 2:
			ci.draw_line(line[0], line[1], Color(col.lerp(Palette.TEXT_HI, DRAIN_LIFT), alpha), maxf(1.0, r * 0.07))


## Segment a-b clipped to convex polygon `poly` ([] when outside).
static func _clip_to(poly: PackedVector2Array, a: Vector2, b: Vector2) -> PackedVector2Array:
	var t0 := 0.0
	var t1 := 1.0
	var n := poly.size()
	var centre := Vector2.ZERO
	for p in poly:
		centre += p
	centre /= n
	for i in n:
		var p := poly[i]
		var q := poly[(i + 1) % n]
		var normal := (q - p).orthogonal()
		if normal.dot(centre - p) < 0.0:
			normal = -normal
		var denom := normal.dot(b - a)
		var num := normal.dot(p - a)
		if absf(denom) < 0.00001:
			if num > 0.0:
				return PackedVector2Array()
			continue
		var t := num / denom
		if denom > 0.0:
			t0 = maxf(t0, t)
		else:
			t1 = minf(t1, t)
		if t0 > t1:
			return PackedVector2Array()
	return PackedVector2Array([a.lerp(b, t0), a.lerp(b, t1)])


static func _pins(ci: CanvasItem, outer: PackedVector2Array, c: Vector2, r: float, col: Color, ink: Color) -> void:
	for e in 4:
		var a := outer[e]
		var b := outer[(e + 1) % 4]
		var mid := (a + b) * 0.5
		var out := (mid - c).normalized()
		for k in PINS:
			var u := (k + 1.0) / (PINS + 1.0)
			var p := a.lerp(b, u)
			ci.draw_line(p, p + out * r * PIN_LEN, ink, r * (PIN_W + 0.06))
			ci.draw_line(p, p + out * r * PIN_LEN, col, r * PIN_W)


## A TAKEN socket's burnt plate: charred, with embers (positions from `seed`).
static func _burnt(ci: CanvasItem, c: Vector2, r: float, alpha: float, seed: int) -> void:
	ci.draw_colored_polygon(diamond(c, r, 0.95), Color(Palette.INK, 0.95 * alpha))
	for i in EMBERS:
		var p := c + Vector2(RaidPencil.noise(seed, i) * HALF.x, RaidPencil.noise(seed + 5, i) * HALF.y) * r * 0.75
		var col := Palette.CRT_AMBER.lerp(Palette.HEAT_FLAGGED, absf(RaidPencil.noise(seed + 9, i)))
		ci.draw_circle(p, r * EMBER * (1.0 + absf(RaidPencil.noise(seed + 2, i))), Color(col, alpha))


## The Site markers' DOWN mark (§4.5, ruling 11): a white lightning bolt across the marker on
## a dark keyline.
static func bolt(ci: CanvasItem, c: Vector2, size: float, alpha: float = 1.0) -> void:
	var pts := PackedVector2Array([
		c + Vector2(0.18, -0.62) * size, c + Vector2(-0.22, 0.04) * size, c + Vector2(0.04, 0.04) * size,
		c + Vector2(-0.16, 0.62) * size, c + Vector2(0.26, -0.08) * size, c + Vector2(0.0, -0.08) * size,
	])
	ci.draw_colored_polygon(pts, Color(Palette.TEXT_HI, alpha))
	ci.draw_polyline(_closed(pts), Color(Palette.NIGHT_SKY, 0.9 * alpha), maxf(1.0, size * BOLT_W * 0.5), true)


## A dashed outer ring round the socket in the projected outcome's colour (forecast).
static func forecast_ring(ci: CanvasItem, c: Vector2, r: float, col: Color, alpha: float = 1.0) -> void:
	var ring := diamond(c, r, FORECAST_OUT)
	var pts := _closed(ring)
	var total := RaidPencil.length_of(pts)
	var dash := total / (FORECAST_DASHES * 2.0)
	for k in FORECAST_DASHES:
		var seg := RaidPencil.trimmed(pts, (k * 2.0 * dash) / total, ((k * 2.0 + 1.0) * dash) / total)
		if seg.size() >= 2:
			ci.draw_polyline(seg, Color(Palette.NIGHT_SKY, 0.85 * alpha), r * (FORECAST_W + 0.08))
			ci.draw_polyline(seg, Color(col, alpha), r * FORECAST_W)


## A node glyph `glyph` at `c` (half size `s`) in `col`.
static func draw_glyph(ci: CanvasItem, glyph: String, c: Vector2, s: float, col: Color) -> void:
	var w := maxf(1.2, s * 0.16)
	match glyph:
		GLYPH_RELAY:
			# All-targets: three arrows out of one stem.
			var base := c + Vector2(0, s * 0.75)
			for tip: Vector2 in [c + Vector2(0, -s * 0.85), c + Vector2(-s * 0.8, -s * 0.35), c + Vector2(s * 0.8, -s * 0.35)]:
				ci.draw_line(base, tip, col, w)
				var d := (tip - base).normalized()
				for sgn: float in [-1.0, 1.0]:
					ci.draw_line(tip, tip - d.rotated(sgn * 0.6) * s * 0.35, col, w)
		GLYPH_FIREWALL:
			# A brick wall with a flame on it.
			var top := c.y - s * 0.05
			var rows := 2
			var bh := s * 0.4
			for row in rows:
				var y := top + row * bh
				ci.draw_rect(Rect2(c.x - s * 0.9, y, s * 1.8, bh), col, false, w)
				var off := 0.0 if row % 2 == 0 else s * 0.45
				var x := c.x - s * 0.9 + s * 0.6 + off
				while x < c.x + s * 0.9:
					ci.draw_line(Vector2(x, y), Vector2(x, y + bh), col, w)
					x += s * 0.9
			var flame := PackedVector2Array([c + Vector2(-s * 0.45, -s * 0.05), c + Vector2(-s * 0.2, -s * 0.55), c + Vector2(0, -s * 0.3),
				c + Vector2(s * 0.15, -s * 0.9), c + Vector2(s * 0.45, -s * 0.05)])
			ci.draw_colored_polygon(flame, col)
		GLYPH_VAULT:
			# A safe door: a box, a dial, a handle.
			ci.draw_rect(Rect2(c - Vector2(s * 0.9, s * 0.7), Vector2(s * 1.8, s * 1.4)), col, false, w)
			ci.draw_arc(c + Vector2(-s * 0.1, 0), s * 0.42, 0, TAU, 20, col, w)
			ci.draw_circle(c + Vector2(-s * 0.1, 0), s * 0.12, col)
			ci.draw_line(c + Vector2(s * 0.62, -s * 0.3), c + Vector2(s * 0.62, s * 0.3), col, w)
		GLYPH_PROXY:
			# A fingerprint: nested arcs.
			for k in 4:
				var rr := s * (0.25 + k * 0.22)
				ci.draw_arc(c + Vector2(0, s * 0.1), rr, PI * (1.05 + k * 0.03), TAU * (0.98 - k * 0.02), 16, col, w * 0.8)
			ci.draw_line(c + Vector2(0, -s * 0.05), c + Vector2(0, s * 0.55), col, w * 0.8)
		GLYPH_SAFEHOUSE:
			# A key.
			ci.draw_arc(c + Vector2(-s * 0.5, 0), s * 0.36, 0, TAU, 18, col, w)
			ci.draw_line(c + Vector2(-s * 0.14, 0), c + Vector2(s * 0.95, 0), col, w)
			ci.draw_line(c + Vector2(s * 0.55, 0), c + Vector2(s * 0.55, s * 0.32), col, w)
			ci.draw_line(c + Vector2(s * 0.85, 0), c + Vector2(s * 0.85, s * 0.26), col, w)
		GLYPH_COMPILER:
			# A rack chip: a box with three slots.
			ci.draw_rect(Rect2(c - Vector2(s * 0.8, s * 0.65), Vector2(s * 1.6, s * 1.3)), col, false, w)
			for k in 3:
				var y := c.y - s * 0.35 + k * s * 0.35
				ci.draw_line(Vector2(c.x - s * 0.5, y), Vector2(c.x + s * 0.3, y), col, w)
				ci.draw_circle(Vector2(c.x + s * 0.55, y), w * 0.6, col)
		GLYPH_CORE:
			# The CORE's pink hexagon.
			var hex := PackedVector2Array()
			for k in 7:
				var a := TAU * k / 6.0 + PI / 6.0
				hex.append(c + Vector2(cos(a), sin(a) * 0.9) * s * 0.85)
			ci.draw_polyline(hex, col, w * 1.6, true)
		_:
			ci.draw_circle(c, s * 0.3, col)
