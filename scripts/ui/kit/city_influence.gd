class_name CityInfluence
extends RefCounted
## Territory colour influence on the city (view-only, H20): the campaign's Grid state
## pulls the city's ink toward the Cell or the corporation around each Site. A claimed
## Site tints its blocks toward the Cell's pink, a cleared one a little; a TAKEN or
## disabled Site pulls them back toward the corporation. Raid results sway the whole
## corporate territory and the blocks round every one of its Sites, wherever they stand
## (won raids toward the Cell, lost ones toward the corporation).
## Pure and deterministic: reads CampaignState, never writes it; Sites are taken in id
## order so equal states always give equal influence (and the same bake key).

## Weight per Site status (+ = the Cell, - = the corporation).
const WEIGHT_CLAIMED := 1.0
const WEIGHT_CLEARED := 0.45
const WEIGHT_TAKEN := -1.0
## A claimed Site knocked out in a raid (condition DOWN) pulls this far back.
const WEIGHT_DOWN := -0.6
## How far a Site's pull reaches (lots) and its falloff exponent.
const RADIUS := 7.5
const FALLOFF := 2.0
## Raid sway over the whole corporate territory, per net raid won (or lost), capped.
const RAID_SWAY_STEP := 0.08
const RAID_SWAY_MAX := 0.32
## H21 #22: the sway also follows the corporation's own Sites wherever they stand (some
## corporations' Grids reach past their district): full within SWAY_REACH lots of a
## Site, fading to nothing over SWAY_FEATHER more.
const SWAY_REACH := 4.5
const SWAY_FEATHER := 1.5
## Quantisation of weights in the signature (so float noise never re-bakes the city).
const SIGNATURE_STEP := 100.0


## The influence of a campaign on the city: {"corp": StringName, "sway": float,
## "sources": [{"id", "at": Vector2 (grid lots), "w": float}], "sites": PackedVector2Array
## (every Site, id order)} with sources sorted by Site id. An empty Dictionary (no
## campaign) means no influence. The Site points are part of the signature (a generated
## Grid stands elsewhere, so its sway lands elsewhere).
static func of(c: CampaignState, corp: CorporationData) -> Dictionary:
	if c == null or corp == null or corp.city_grid == null:
		return {}
	var points := CityLayout.site_points(corp)
	var ids: Array[StringName] = []
	for id in points:
		ids.append(id)
	ids.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	var sources: Array[Dictionary] = []
	var sites := PackedVector2Array()
	for id in ids:
		sites.append(points[id])
		var w := weight_of(c.grid, id)
		if not is_zero_approx(w):
			sources.append({"id": id, "at": points[id], "w": w})
	var sway := clampf((c.raids_won - c.raids_lost) * RAID_SWAY_STEP, -RAID_SWAY_MAX, RAID_SWAY_MAX)
	return {"corp": corp.id, "sway": sway, "sources": sources, "sites": sites}


## A Site's pull from its status and condition.
static func weight_of(grid: GridState, site_id: StringName) -> float:
	var w := 0.0
	match grid.status_of(site_id):
		GridState.SiteStatus.CLAIMED:
			w = WEIGHT_CLAIMED
			if int(grid.site(site_id).get("condition", GridState.Condition.OK)) == GridState.Condition.DOWN:
				w += WEIGHT_DOWN
		GridState.SiteStatus.CLEARED:
			w = WEIGHT_CLEARED
		GridState.SiteStatus.TAKEN:
			w = WEIGHT_TAKEN
	return w


## Influence at grid point `p` (lots) in territory `terr`: -1 (the corporation) .. +1
## (the Cell). Sum of the Sites' pulls with a smooth falloff, plus the raid sway inside
## the corporation's own territory and around its own Sites (`sway_share`).
static func value_at(inf: Dictionary, p: Vector2, terr: StringName = &"") -> float:
	if inf.is_empty():
		return 0.0
	var v := 0.0
	for s: Dictionary in inf["sources"]:
		var d := p.distance_to(s["at"]) / RADIUS
		if d < 1.0:
			v += float(s["w"]) * pow(1.0 - d, FALLOFF)
	var sway := float(inf["sway"])
	if not is_zero_approx(sway):
		v += sway * sway_share(inf, p, terr)
	return clampf(v, -1.0, 1.0)


## How much of the raid sway reaches grid point `p` in territory `terr`: all of it inside
## the corporation's territory or within SWAY_REACH of one of its Sites, fading to 0 over
## SWAY_FEATHER beyond that.
static func sway_share(inf: Dictionary, p: Vector2, terr: StringName = &"") -> float:
	if inf.is_empty():
		return 0.0
	if terr != &"" and terr == inf["corp"]:
		return 1.0
	var nearest := INF
	for q: Vector2 in inf.get("sites", PackedVector2Array()):
		nearest = minf(nearest, p.distance_squared_to(q))
	return clampf((SWAY_REACH + SWAY_FEATHER - sqrt(nearest)) / SWAY_FEATHER, 0.0, 1.0)


## The colour the influence leans toward: the Cell's territory colour (v > 0; ANIM-R3 B6:
## Palette.CELL_TURF, not the damage pink) or the corporation's.
static func color_for(inf: Dictionary, v: float) -> Color:
	if v >= 0.0 or inf.is_empty():
		return Palette.CELL_TURF
	return Palette.corp_color(inf["corp"])


## Stable text signature (part of the city bake key): changes only when the influence
## does.
static func signature(inf: Dictionary) -> String:
	if inf.is_empty():
		return "-"
	var parts := PackedStringArray([String(inf["corp"]), str(roundi(float(inf["sway"]) * SIGNATURE_STEP))])
	# Where the Sites stand (generated Grids differ per campaign): it moves the sway.
	parts.append(str(hash(inf.get("sites", PackedVector2Array()))))
	for s: Dictionary in inf["sources"]:
		parts.append("%s:%d" % [s["id"], roundi(float(s["w"]) * SIGNATURE_STEP)])
	return "|".join(parts)
