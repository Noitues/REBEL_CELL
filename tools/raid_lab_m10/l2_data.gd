class_name L2Data
extends RefCounted
## Loads data/l2_golden.json (tools/raid_concepts/l2_golden.py) and data/l2_extra.json (data/gen_l2_extra.py: the raids'
## second extra beam, EXTRA_AT, the naive line) into typed legs for the rules.

const GOLDEN_PATH := "res://tools/raid_lab_m10/data/l2_golden.json"
const EXTRA_PATH := "res://tools/raid_lab_m10/data/l2_extra.json"


static func load_json(path: String) -> Dictionary:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	return parsed if parsed is Dictionary else {}


## [x, y] -> Vector2i.
static func cell(a: Array) -> Vector2i:
	return Vector2i(int(a[0]), int(a[1]))


static func cells(arr: Array) -> Array:
	var out: Array = []
	for a in arr:
		out.append(cell(a))
	return out


## A leg: {seed, home, values (cell -> v), raids [{b1, extra, extra2, cands, own3}], planned, greedy, naive (raw golden
## step lists)}. Empty if the seed is not in the golden.
static func load_leg(seed_id: int) -> Dictionary:
	var g := load_json(GOLDEN_PATH)
	var ex := load_json(EXTRA_PATH)
	for raw in g.get("legs", []):
		if int(raw["seed"]) != seed_id:
			continue
		var extra: Dictionary = ex["legs"][str(seed_id)]
		var lg: Dictionary = raw["leg"]
		var values := {}
		for v in lg["values"]:
			values[Vector2i(int(v[0]), int(v[1]))] = int(v[2])
		var raids: Array = []
		for i in range(lg["raids"].size()):
			var r: Dictionary = lg["raids"][i]
			var cands: Array = []
			for ln in r["cands"]:
				cands.append(cells(ln))
			raids.append({"b1": cells(r["b1"]), "extra": cells(r["extra"]), "extra2": cells(extra["extra2"][i]),
				"cands": cands, "own3": cells(r["own3"])})
		return {"seed": seed_id, "home": cell(lg["home"]), "values": values, "raids": raids,
			"planned": raw["planned"], "greedy": raw["greedy"], "naive": extra["naive"]}
	return {}


## A golden allocation as the rules' alloc dictionary.
static func alloc_of(a: Dictionary) -> Dictionary:
	return {"ghost": cells(a["ghost"]), "dark": cells(a["dark"]), "decoys": cells(a["decoys"])}


## A golden spoof ([x, y] or null) as a cell; NONE when absent.
static func spoof_of(s: Variant) -> Vector2i:
	if s == null:
		return L2Rules.NONE
	return cell(s)
