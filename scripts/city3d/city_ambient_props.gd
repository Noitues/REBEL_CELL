class_name CityAmbientProps
extends RefCounted
## ART-5 5c: where the city's always-on ambient props stand (ART_BIBLE §4.1 "the City Grid
## shows all city life", §4.2 layers 3: holo billboards and aviation lights). Aviation
## lights on the tallest roofs (ties by building key), each with its blink phase; holo
## billboards on roofs of at least `billboard_min_roof`, spread (no two within three lots),
## each with a palette colour, a panel offset and a phase. Draws from the seeded
## `city_ambient` stream (RngStreams.make_stream: never a campaign stream). Pure data.

const STREAM := &"city_ambient"
## Least lots between two billboards.
const BILLBOARD_SPACING_LOTS := 3.0

## {"pos": Vector3 (roof top), "phase": 0-1}.
var aviation: Array[Dictionary] = []
## {"pos": Vector3 (panel centre), "color": int (lane palette), "panel": int, "phase": 0-1}.
var billboards: Array[Dictionary] = []


static func build(cfg: CityMotionConfigData, site: CityMotionSite, seed: int) -> CityAmbientProps:
	var a := CityAmbientProps.new()
	var rng := RngStreams.make_stream(seed, STREAM)
	var tall := site.roofs.duplicate()
	tall.sort_custom(func(x: Dictionary, y: Dictionary) -> bool:
		if float(x["h"]) != float(y["h"]):
			return float(x["h"]) > float(y["h"])
		return int(x["key"]) < int(y["key"]))
	for k in mini(cfg.aviation_count, tall.size()):
		a.aviation.append({"pos": tall[k]["pos"], "phase": rng.randf()})
	# Billboards: candidates in key order, a seeded shuffle, then spaced picks.
	var cand: Array[Dictionary] = []
	for rf in site.roofs:
		if float(rf["h"]) >= cfg.billboard_min_roof:
			cand.append(rf)
	for i in range(cand.size() - 1, 0, -1):
		var j := rng.randi_range(0, i)
		var tmp := cand[i]
		cand[i] = cand[j]
		cand[j] = tmp
	var space := BILLBOARD_SPACING_LOTS * site.lot_bu
	for rf in cand:
		if a.billboards.size() >= cfg.billboard_count:
			break
		var p: Vector3 = rf["pos"]
		var far := true
		for b in a.billboards:
			var q: Vector3 = b["pos"]
			if Vector2(p.x - q.x, p.z - q.z).length() < space:
				far = false
				break
		if not far:
			continue
		a.billboards.append({"pos": p + Vector3(0.0, cfg.billboard_lift + cfg.billboard_size.y * 0.5, 0.0),
			"color": rng.randi_range(0, cfg.lane_colors.size() - 1), "panel": rng.randi_range(0, cfg.billboard_panels - 1),
			"phase": rng.randf()})
	return a
