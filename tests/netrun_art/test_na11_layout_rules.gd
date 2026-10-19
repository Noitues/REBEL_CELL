extends GutTest
## NA-11: the layout rules (frontage minimum, border width, street r2 height passes) in GDScript against the Python oracle
## (`tools/netrun_art/layout.py`, fixtures `fixtures/layout/`): every part height and base polygon of the ruled city is
## within 1e-4 BU on 3 seeds; no frontage building is under 6 floors; the passes are pure and deterministic.

const TOL := 1.0e-4
const SEEDS: Array[String] = ["101", "102", "103"]


func _load(seed_name: String, file: String) -> Variant:
	return NaFixture.decode(JSON.parse_string(FileAccess.get_file_as_string(NaFixture.DIR + "layout/%s%s.json" % [seed_name, file])))


func _ruled(seed_name: String) -> Dictionary:
	var w: Dictionary = _load(seed_name, "")
	return NetrunArtLayoutRules.apply_rules(w["city"], w["net"], w["route_tops"], "all")


func test_heights_and_polys_equal_python() -> void:
	for s in SEEDS:
		var want: Dictionary = _load(s, "_rules")
		var got := _ruled(s)
		assert_eq((got["buildings"] as Array).size(), want.size(), "seed %s building count" % s)
		var worst := 0.0
		var bad := ""
		for b: Dictionary in got["buildings"]:
			var parts: Array = want[b["bid"]]
			for i in parts.size():
				var p: Dictionary = (b["parts"] as Array)[i]
				var q: Dictionary = parts[i]
				var d := maxf(absf(float(p["h"]) - float(q["h"])), absf(float(p["z0"]) - float(q["z0"])))
				for v in (p["poly"] as Array).size():
					for k in 2:
						d = maxf(d, absf(float(p["poly"][v][k]) - float(q["poly"][v][k])))
				if d > worst:
					worst = d
					bad = "%s part %d" % [b["bid"], i]
		assert_lte(worst, TOL, "seed %s: worst diff %s at %s" % [s, worst, bad])


func test_no_frontage_under_six_floors() -> void:
	var fl := NetrunArtUnits.floor_bu()
	for s in SEEDS:
		var w: Dictionary = _load(s, "")
		var got := _ruled(s)
		var bases: Array = NetrunArtLayout.merged_buildings(w["city"])
		var front := {}
		for link: Dictionary in NetrunArtLayoutRules.links_of(w["net"], "all"):
			var legs: Array = NetrunArtLayout.link_legs(w["city"], link["pts"])
			for i in range(legs.size() - 1):
				var rows := NetrunArtLayoutRules.frontage_rows(bases, legs[i], legs[i + 1])
				for side: int in [1, -1]:
					for bi: Dictionary in rows[side]:
						front[bi["bid"]] = true
		assert_gt(front.size(), 0, "seed %s has a frontage" % s)
		var heights := {}
		for bi: Dictionary in NetrunArtLayout.merged_buildings(got):
			heights[bi["bid"]] = bi["h"]
		var bad: Array = []
		for bid: String in front:
			if int(float(heights[bid]) / fl + 1.0e-9) < 6:
				bad.append(bid)
		assert_eq(bad, [], "seed %s: frontage buildings under 6 floors" % s)


func test_pure_and_deterministic_and_ids_unique() -> void:
	var w: Dictionary = _load("101", "")
	var before := JSON.stringify(w["city"])
	var one := NetrunArtLayoutRules.apply_rules(w["city"], w["net"], w["route_tops"], "all")
	var two := NetrunArtLayoutRules.apply_rules(w["city"], w["net"], w["route_tops"], "all")
	assert_eq(JSON.stringify(w["city"]), before, "the input city is not modified")
	assert_eq(JSON.stringify(one), JSON.stringify(two), "same inputs, same city")
	var seen := {}
	for b: Dictionary in one["buildings"]:
		assert_false(seen.has(b["bid"]), "bid %s is unique" % b["bid"])
		seen[b["bid"]] = true


func test_config_carries_the_rules() -> void:
	var r: Dictionary = NetrunArtConfigData.shipped().layout_rules
	assert_eq(int(r["frontage_min_floors"]), 6)
	assert_eq(float(r["border_street_width"]), 8.0)
	assert_eq(float(r["base_street_width"]), 6.0)
	assert_true(bool(r["hero_sign_rule"]["blade"]) and bool(r["hero_sign_rule"]["band"]))
