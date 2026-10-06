class_name RaidSocket
extends RefCounted
## ART-6 3A: a Cell node on the raid map as its circuit socket (ART_BIBLE v2 §4.8 "Network on
## the street = circuit inlay", round 22 `node_status_key`, round 21 `node_health`): the
## approved concept art itself, rendered unchanged by the concept's street-decal code on
## art-concepts-r43 (round23_raid_ui `netdecal19.Net.pad` + health v2 `netdecal21.Net.health_pad`)
## and baked by `tools/art_pipeline/raid/bake_sockets.py` into `assets/raid/sockets/`
## (manifest.json names the source). No tag: the type is the glyph; the status is the frame:
## - HOLDS: green frame, pins lit (CORE pink hex); health v2: the inner lit fill drains north
##   to south (baked at 100 / 75 / 50 / 25 %), repair raises it again.
## - DOWN (DECISIONS 2026-10-05 ruling 11): the concept's disabled socket greyed, with the Site
##   markers' white lightning bolt drawn over it (the bolt is the ruling's addition: no
##   concept image of it in a socket, so it is drawn).
## - TAKEN: the burnt socket with embers.
## - Forecast: the dashed outer ring in the projected outcome's colour.
## - Dock (drag): the white frame where a defence can go; red frame + X where it can't.
## The game only picks the image. View only.

const STATE_HOLDS := "holds"
const STATE_DOWN := "down"
const STATE_TAKEN := "taken"
const DRAG_VALID := "valid"
const DRAG_INVALID := "invalid"

## Node types (content/nodes ids) and the socket each takes (§4.8: Relay all-targets arrows,
## Firewall, Vault safe door, Proxy fingerprint, Safehouse key, Compiler Rack chip, CORE hex).
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

const DIR := "res://assets/raid/sockets/"
## The baked image's size and the socket's half width in it, pins included (px; manifest.json).
const ART_PX := 134.0
const ART_HALF_PX := 47.0
## The socket's half width and half height on the map (x the map icon radius).
const HALF := Vector2(1.5, 1.5)
## The baked health steps (%), highest first.
const HP_STEPS: Array[int] = [100, 75, 50, 25]
## DOWN: the bolt's size (x radius) and keyline width (x its size).
const BOLT := 1.25
const BOLT_W := 0.16

static var _cache: Dictionary = {}


## The glyph id of node type `node_type` ("relay" when unknown).
static func glyph_of(node_type: StringName) -> String:
	return GLYPH_OF.get(node_type, GLYPH_RELAY)


## The colour a socket's frame takes for its node (the concept's: CORE pink, every other
## owned node the "holds" green). Marks beside the socket take it.
static func frame_color(glyph: String) -> Color:
	return Palette.CELL_PINK if glyph == GLYPH_CORE else Palette.GAIN


## The baked health step for `health` (0..1): the nearest, never full while damaged.
static func hp_step(health: float) -> int:
	var best := HP_STEPS[0]
	for s in HP_STEPS:
		if absf(s / 100.0 - health) < absf(best / 100.0 - health):
			best = s
	if best == HP_STEPS[0] and health < 1.0:
		best = HP_STEPS[1]
	return best


## The baked image's file stem for `spec` (see draw).
static func image_of(spec: Dictionary) -> String:
	var glyph := String(spec.get("glyph", GLYPH_RELAY))
	var state := String(spec.get("state", STATE_HOLDS))
	var dock := String(spec.get("dock", ""))
	var forecast := String(spec.get("forecast", ""))
	var look := "hp%03d" % hp_step(clampf(float(spec.get("health", 1.0)), 0.0, 1.0))
	if state == STATE_TAKEN:
		look = "taken"
	elif state == STATE_DOWN:
		look = "down"
	elif dock == DRAG_VALID:
		look = "hover"
	elif dock == DRAG_INVALID:
		look = "invalid"
	elif forecast == STATE_DOWN:
		look = "fc_down"
	elif forecast == STATE_TAKEN:
		look = "fc_taken"
	return "%s_%s" % [glyph, look]


## The baked texture for `spec` (null when missing).
static func texture(spec: Dictionary) -> Texture2D:
	var p := DIR + image_of(spec) + ".png"
	if not _cache.has(p):
		_cache[p] = load(p) if ResourceLoader.exists(p) else null
	return _cache[p]


## The box a socket at `c`, radius `r` covers (the whole baked image: pins and forecast ring).
static func rect(c: Vector2, r: float) -> Rect2:
	var half := ART_PX * 0.5 * HALF.x * r / ART_HALF_PX
	return Rect2(c - Vector2(half, half), Vector2(half, half) * 2.0)


## Draws a socket at `c` (radius `r`, the map icon's) on `ci`. `spec`: glyph (GLYPH_*),
## state (STATE_*), health (0..1), forecast ("" / STATE_DOWN / STATE_TAKEN), dock (""
## / DRAG_*), alpha.
static func draw(ci: CanvasItem, c: Vector2, r: float, spec: Dictionary) -> void:
	var alpha := float(spec.get("alpha", 1.0))
	var tex := texture(spec)
	if tex != null:
		ci.draw_texture_rect(tex, rect(c, r), false, Color(Palette.NO_TINT, alpha))
	if String(spec.get("state", STATE_HOLDS)) == STATE_DOWN:
		bolt(ci, c, r * BOLT, alpha)


## The Site markers' DOWN mark (§4.5, ruling 11): a white lightning bolt across the marker on
## a dark keyline.
static func bolt(ci: CanvasItem, c: Vector2, size: float, alpha: float = 1.0) -> void:
	var pts := PackedVector2Array([
		c + Vector2(0.18, -0.62) * size, c + Vector2(-0.22, 0.04) * size, c + Vector2(0.04, 0.04) * size,
		c + Vector2(-0.16, 0.62) * size, c + Vector2(0.26, -0.08) * size, c + Vector2(0.0, -0.08) * size,
	])
	ci.draw_colored_polygon(pts, Color(Palette.TEXT_HI, alpha))
	var ring := pts.duplicate()
	ring.append(pts[0])
	ci.draw_polyline(ring, Color(Palette.NIGHT_SKY, 0.9 * alpha), maxf(1.0, size * BOLT_W * 0.5), true)
