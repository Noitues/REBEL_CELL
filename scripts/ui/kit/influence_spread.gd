class_name InfluenceSpread
extends RefCounted
## Territory colour change as motion (Animation pass ANIM-5, the designer's ask): when a
## Site changes owner (cleared or claimed by the Cell, TAKEN in a raid, taken back) the
## city's territory tint does not jump; the new tint spreads out from the Site(s) that
## changed, block by block along the street grid, and whatever changed beyond the
## spread's reach (a raid's sway over the whole territory) cross-fades in behind it.
##
## Pure view math, shared by NeonCity (which draws the new baked image under the old one
## and masks the old one away with `shaders/influence_reveal.gdshader`, the same formula)
## and the tests. Distances are in grid lots, Manhattan along the streets (the grid's
## axes are its streets), plus a per-block jitter from a hash of the lot so whole blocks
## turn at once (decoration only: no RNG). Reads CityInfluence dictionaries, never
## campaign state.

## At most this many origins drive the mask (the shader's array size).
const MAX_ORIGINS := 4
## Weights closer than this count as unchanged (CityInfluence.SIGNATURE_STEP's step).
const WEIGHT_EPSILON := 0.005


## Where the spread starts (grid lots): the Sites whose pull changed between `old_inf`
## and `new_inf`, in Site id order (at most MAX_ORIGINS); when only the raid sway changed,
## the corporation's HQ (its power reaches out from there). Empty when nothing changed.
static func origins(old_inf: Dictionary, new_inf: Dictionary) -> PackedVector2Array:
	var out := PackedVector2Array()
	if new_inf.is_empty() and old_inf.is_empty():
		return out
	for id in changed_sites(old_inf, new_inf):
		if out.size() >= MAX_ORIGINS:
			break
		out.append(_site_point(new_inf, id) if _has_source(new_inf, id) else _site_point(old_inf, id))
	if out.is_empty() and CityInfluence.signature(old_inf) != CityInfluence.signature(new_inf):
		var corp: StringName = new_inf.get("corp", old_inf.get("corp", &""))
		out.append(NeonCity.hq_of(corp) + Vector2(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS) * 0.5)
	return out


## Ids of the Sites whose pull changed (a source added, removed or re-weighted), sorted.
static func changed_sites(old_inf: Dictionary, new_inf: Dictionary) -> Array[StringName]:
	var before := _weights(old_inf)
	var after := _weights(new_inf)
	var ids: Array[StringName] = []
	for id in before:
		if not ids.has(id):
			ids.append(id)
	for id in after:
		if not ids.has(id):
			ids.append(id)
	var out: Array[StringName] = []
	for id in ids:
		if absf(float(before.get(id, 0.0)) - float(after.get(id, 0.0))) > WEIGHT_EPSILON:
			out.append(id)
	out.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	return out


## The colour of the spreading front: the Cell's pink when the first changed Site (id
## order) swung toward the Cell, the corporation's colour when it swung away; for a
## sway-only change, the side the sway moved toward.
static func front_color(old_inf: Dictionary, new_inf: Dictionary) -> Color:
	var corp: StringName = new_inf.get("corp", old_inf.get("corp", &""))
	var before := _weights(old_inf)
	var after := _weights(new_inf)
	var sites := changed_sites(old_inf, new_inf)
	var delta := 0.0
	if not sites.is_empty():
		delta = float(after.get(sites[0], 0.0)) - float(before.get(sites[0], 0.0))
	else:
		delta = float(new_inf.get("sway", 0.0)) - float(old_inf.get("sway", 0.0))
	return Palette.CELL_TURF if delta >= 0.0 else Palette.corp_color(corp)


## ANIM-R1 M5: what a territory change leaves on the city once it has spread: one mark per
## Site whose pull changed (id order, at most MAX_ORIGINS): {"id", "at" (grid lots),
## "word" (untranslated: CLAIMED / CLEARED toward the Cell, TAKEN / DOWN away from
## it), "color" (the Cell's territory colour, or the corporation's)}. Empty for a sway-only change.
static func marks(old_inf: Dictionary, new_inf: Dictionary) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var corp: StringName = new_inf.get("corp", old_inf.get("corp", &""))
	var before := _weights(old_inf)
	var after := _weights(new_inf)
	for id in changed_sites(old_inf, new_inf):
		if out.size() >= MAX_ORIGINS:
			break
		var w0 := float(before.get(id, 0.0))
		var w1 := float(after.get(id, 0.0))
		var word := ""
		if w1 > w0:
			word = MARK_CLAIMED if w1 >= CityInfluence.WEIGHT_CLAIMED - WEIGHT_EPSILON else MARK_CLEARED
		else:
			word = MARK_TAKEN if w1 <= CityInfluence.WEIGHT_TAKEN + WEIGHT_EPSILON else MARK_DOWN
		var at := _site_point(new_inf, id) if _has_source(new_inf, id) else _site_point(old_inf, id)
		out.append({"id": id, "at": at, "word": word, "color": Palette.CELL_TURF if w1 > w0 else Palette.corp_color(corp)})
	return out


## The marks' words (translation keys).
const MARK_CLAIMED := "CLAIMED" # TR
const MARK_CLEARED := "CLEARED" # TR
const MARK_TAKEN := "TAKEN" # TR
const MARK_DOWN := "DOWN" # TR


## Deterministic 0-1 jitter of lot `lot` (whole blocks turn together). The shader uses
## the same formula.
static func lot_jitter(lot: Vector2) -> float:
	var v := sin(lot.x * 12.9898 + lot.y * 78.233) * 43758.5453
	return v - floorf(v)


## Street distance (lots) from grid point `p` to the nearest origin, plus its block's
## jitter x `feather`. INF with no origins.
static func distance_at(p: Vector2, from: PackedVector2Array, feather: float) -> float:
	var d := INF
	for o in from:
		d = minf(d, absf(p.x - o.x) + absf(p.y - o.y))
	if d == INF:
		return d
	return d + lot_jitter(p.floor()) * feather


## How far the new tint has taken grid point `p`: 0 = the old tint, 1 = the new. `t` is
## the spread's eased progress (0..1, the front at t x `reach` lots), `fade` the
## cross-fade's (0..1) for everything the front has not reached.
static func reveal_at(p: Vector2, from: PackedVector2Array, t: float, fade: float, reach: float, feather: float) -> float:
	var d := distance_at(p, from, feather)
	var r := clampf(t, 0.0, 1.0) * reach
	var spread := 0.0
	if d != INF and t > 0.0:
		spread = 1.0 - smoothstep(r - feather, r, d)
	return maxf(spread, clampf(fade, 0.0, 1.0))


## Influence value at grid point `p` (territory `terr`) mid-change: the old and the new
## CityInfluence values mixed by `reveal` (reveal_at).
static func value_at(old_inf: Dictionary, new_inf: Dictionary, p: Vector2, reveal: float, terr: StringName = &"") -> float:
	return lerpf(CityInfluence.value_at(old_inf, p, terr), CityInfluence.value_at(new_inf, p, terr), clampf(reveal, 0.0, 1.0))


## The tint grid point `p` shows mid-change (CityInfluence.color_for of the mixed value,
## weighted by how strongly it leans): at reveal 1 it is exactly CityInfluence's colour
## for the new influence.
static func tint_at(old_inf: Dictionary, new_inf: Dictionary, p: Vector2, reveal: float, terr: StringName = &"") -> Color:
	var v := value_at(old_inf, new_inf, p, reveal, terr)
	var inf := new_inf if reveal >= 0.5 or old_inf.is_empty() else old_inf
	return CityInfluence.color_for(inf, v)


static func _weights(inf: Dictionary) -> Dictionary:
	var out := {}
	for s: Dictionary in inf.get("sources", []):
		out[StringName(s["id"])] = float(s["w"])
	return out


static func _has_source(inf: Dictionary, id: StringName) -> bool:
	for s: Dictionary in inf.get("sources", []):
		if StringName(s["id"]) == id:
			return true
	return false


static func _site_point(inf: Dictionary, id: StringName) -> Vector2:
	for s: Dictionary in inf.get("sources", []):
		if StringName(s["id"]) == id:
			return s["at"]
	return Vector2.ZERO
