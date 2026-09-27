class_name CityInfluence
extends RefCounted
## Territory colour influence on the city (view-only, H20): the campaign's Grid state
## pulls the city's ink toward the Cell or the corporation around each Site. A claimed
## Site tints its blocks toward the Cell's pink, a cleared one a little; a Seized or
## disabled Site pulls them back toward the corporation. Raid results sway the whole
## corporate territory (won raids toward the Cell, lost ones toward the corporation).
## Pure and deterministic: reads CampaignState, never writes it; Sites are taken in id
## order so equal states always give equal influence (and the same bake key).

## Weight per Site status (+ = the Cell, - = the corporation).
const WEIGHT_CLAIMED := 1.0
const WEIGHT_CLEARED := 0.45
const WEIGHT_SEIZED := -1.0
## A claimed Site knocked out in a raid (condition DISABLED) pulls this far back.
const WEIGHT_DISABLED := -0.6
## How far a Site's pull reaches (lots) and its falloff exponent.
const RADIUS := 7.5
const FALLOFF := 2.0
## Raid sway over the whole corporate territory, per net raid won (or lost), capped.
const RAID_SWAY_STEP := 0.08
const RAID_SWAY_MAX := 0.32
## Quantisation of weights in the signature (so float noise never re-bakes the city).
const SIGNATURE_STEP := 100.0


## The influence of a campaign on the city: {"corp": StringName, "sway": float,
## "sources": [{"id", "at": Vector2 (grid lots), "w": float}]} sorted by Site id. An
## empty Dictionary (no campaign) means no influence.
static func of(c: CampaignState, corp: CorporationData) -> Dictionary:
	if c == null or corp == null or corp.city_grid == null:
		return {}
	var points := CityLayout.site_points(corp)
	var ids: Array[StringName] = []
	for id in points:
		ids.append(id)
	ids.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	var sources: Array[Dictionary] = []
	for id in ids:
		var w := weight_of(c.grid, id)
		if not is_zero_approx(w):
			sources.append({"id": id, "at": points[id], "w": w})
	var sway := clampf((c.raids_won - c.raids_lost) * RAID_SWAY_STEP, -RAID_SWAY_MAX, RAID_SWAY_MAX)
	return {"corp": corp.id, "sway": sway, "sources": sources}


## A Site's pull from its status and condition.
static func weight_of(grid: GridState, site_id: StringName) -> float:
	var w := 0.0
	match grid.status_of(site_id):
		GridState.SiteStatus.CLAIMED:
			w = WEIGHT_CLAIMED
			if int(grid.site(site_id).get("condition", GridState.Condition.OK)) == GridState.Condition.DISABLED:
				w += WEIGHT_DISABLED
		GridState.SiteStatus.CLEARED:
			w = WEIGHT_CLEARED
		GridState.SiteStatus.SEIZED:
			w = WEIGHT_SEIZED
	return w


## Influence at grid point `p` (lots) in territory `terr`: -1 (the corporation) .. +1
## (the Cell). Sum of the Sites' pulls with a smooth falloff, plus the raid sway inside
## the corporation's own territory.
static func value_at(inf: Dictionary, p: Vector2, terr: StringName = &"") -> float:
	if inf.is_empty():
		return 0.0
	var v := 0.0
	for s: Dictionary in inf["sources"]:
		var d := p.distance_to(s["at"]) / RADIUS
		if d < 1.0:
			v += float(s["w"]) * pow(1.0 - d, FALLOFF)
	if terr != &"" and terr == inf["corp"]:
		v += float(inf["sway"])
	return clampf(v, -1.0, 1.0)


## The colour the influence leans toward: the Cell's pink (v > 0) or the corporation's.
static func color_for(inf: Dictionary, v: float) -> Color:
	if v >= 0.0 or inf.is_empty():
		return Palette.CELL_PINK
	return Palette.corp_color(inf["corp"])


## Stable text signature (part of the city bake key): changes only when the influence
## does.
static func signature(inf: Dictionary) -> String:
	if inf.is_empty():
		return "-"
	var parts := PackedStringArray([String(inf["corp"]), str(roundi(float(inf["sway"]) * SIGNATURE_STEP))])
	for s: Dictionary in inf["sources"]:
		parts.append("%s:%d" % [s["id"], roundi(float(s["w"]) * SIGNATURE_STEP)])
	return "|".join(parts)
