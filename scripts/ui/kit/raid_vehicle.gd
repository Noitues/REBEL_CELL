class_name RaidVehicle
extends RefCounted
## ART-6 3A: a raid threat's map icon, vehicle icons v4 (ART_BIBLE v2 §4.8): the approved concept
## art itself, baked unchanged from art-concepts-r43 `round22_raid_world/scripts/icons22.py` by
## `tools/art_pipeline/raid/bake_vehicle_icons.py` into `assets/raid/icons/` (manifest.json names
## the source). SHAPE = type (FAST chevron badge, HEAVY block, SPECIAL hexagon with the corp's verb,
## FLYING diamond with rotors), FILL = the corp colour = health draining from the top (baked at
## 100 / 75 / 50 / 25 / 0 %), RING = the dashed corp circle with its status pip (slowed, frozen),
## UPGRADED = two chevrons and a double rim. The game only picks the image and, on hover, draws the
## yellow heading arrow riding the ring (it turns with the threat, so it is drawn). The type
## comes from what the threat does in the rules (ThreatData): FAST moves two links a step,
## SPECIAL freezes or alters links, the rest HEAVY; FLYING has no rule yet. View only.

const FAST := "fast"
const HEAVY := "heavy"
const SPECIAL := "special"
const FLYING := "flying"
## Statuses a threat can carry in the current rules (ICE Lock / a stationed Ghost's hold).
const STATUS_FROZEN := "frozen"
const STATUS_SLOWED := "slowed"

const DIR := "res://assets/raid/icons/"
## The baked icon's shape radius and image size (px; manifest.json: icons22 `size` 56).
const ART_SHAPE_R := 22.4
const ART_PX := 140.0
## The ring's radius (x the shape radius; icons22: R = 1.78 r), the heading arrow's reach past
## it and half width (x the shape radius).
const RING := 1.78
const HEADING_OUT := 0.5
const HEADING_SPREAD := 0.3
## The baked health steps (%), highest first.
const HP_STEPS: Array[int] = [100, 75, 50, 25, 0]

static var _cache: Dictionary = {}


## The icon type of threat `t` from its rules.
static func type_of(t: ThreatData) -> String:
	if t == null:
		return HEAVY
	if t.freezes_edges or t.alters_edges:
		return SPECIAL
	if t.edges_per_step >= 2:
		return FAST
	return HEAVY


## The baked step for health `hp` (0..1): the nearest of HP_STEPS, never 0 while it lives.
static func hp_step(hp: float) -> int:
	var best := HP_STEPS[0]
	for s in HP_STEPS:
		if absf(s / 100.0 - hp) < absf(best / 100.0 - hp):
			best = s
	if best == 0 and hp > 0.0:
		best = HP_STEPS[HP_STEPS.size() - 2]
	return best


## The concept icon's path for corp `corporation_id`, `type`, `status` ("" none) and health.
static func path_of(type: String, corporation_id: StringName, hp: float = 1.0, status: String = "", upgraded: bool = false) -> String:
	if upgraded:
		return DIR + "%s_%s_up_hp100.png" % [corporation_id, type]
	return DIR + "%s_%s_%s_hp%03d.png" % [corporation_id, type, status if status != "" else "none", hp_step(hp)]


## The concept icon's texture (null when it was not baked: an unknown corp falls back to Halcyon's).
static func texture(type: String, corporation_id: StringName, hp: float = 1.0, status: String = "", upgraded: bool = false) -> Texture2D:
	var p := path_of(type, corporation_id, hp, status, upgraded)
	if not _cache.has(p):
		var t: Texture2D = load(p) if ResourceLoader.exists(p) else null
		if t == null and corporation_id != &"halcyon":
			t = texture(type, &"halcyon", hp, status, upgraded)
		_cache[p] = t
	return _cache[p]


## The box the icon covers with its ring (local px).
static func rect(c: Vector2, r: float) -> Rect2:
	var half := ART_PX * 0.5 * r / ART_SHAPE_R
	return Rect2(c - Vector2(half, half), Vector2(half, half) * 2.0)


## Draws threat icon `type` of `corporation_id` at `c` with shape radius `r`: `hp` 0..1,
## `statuses` (the first shows on the ring), `heading` (radians, NAN for none: hover only),
## `alpha`.
static func draw(ci: CanvasItem, c: Vector2, r: float, type: String, corporation_id: StringName, hp: float = 1.0,
		statuses: Array = [], heading: float = NAN, _ring_phase: float = 0.0, alpha: float = 1.0) -> void:
	var status := String(statuses[0]) if not statuses.is_empty() else ""
	var tex := texture(type, corporation_id, hp, status)
	if tex != null:
		ci.draw_texture_rect(tex, rect(c, r), false, Color(Color.WHITE, alpha))
	if not is_nan(heading):
		var R := r * RING
		var tip := c + Vector2.from_angle(heading) * (R + r * HEADING_OUT)
		var l := c + Vector2.from_angle(heading + HEADING_SPREAD) * (R - r * 0.1)
		var rr := c + Vector2.from_angle(heading - HEADING_SPREAD) * (R - r * 0.1)
		var tri := PackedVector2Array([tip, l, rr])
		ci.draw_colored_polygon(tri, Color(RaidSkin.pencil_plan(), alpha))
		tri.append(tip)
		ci.draw_polyline(tri, Color(Palette.NIGHT_SKY, alpha), maxf(1.0, r * 0.08))
