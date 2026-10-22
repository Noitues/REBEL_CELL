class_name M10Data
extends RefCounted
## Loads data/m10_golden.json (written by tools/raid_concepts/m10_golden.py) into typed cases for the rules.

const GOLDEN_PATH := "res://tools/raid_lab_m10/data/m10_golden.json"


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


## A golden case as {seed, assets (cell -> value), b1, cands (Array of lines), own3, plans (raw golden dict)}.
static func make_case(raw: Dictionary) -> Dictionary:
	var assets := {}
	for a in raw["assets"]:
		assets[Vector2i(int(a[0]), int(a[1]))] = int(a[2])
	var cands: Array = []
	for ln in raw["cands"]:
		cands.append(cells(ln))
	return {"seed": int(raw["seed"]), "assets": assets, "b1": cells(raw["b1"]), "cands": cands,
		"own3": cells(raw["own3"]), "plans": raw["plans"]}


static func load_cases() -> Array:
	var g := load_json(GOLDEN_PATH)
	var out: Array = []
	for raw in g.get("cases", []):
		out.append(make_case(raw))
	return out


static func case_by_seed(cases: Array, seed_id: int) -> Dictionary:
	for c in cases:
		if int(c["seed"]) == seed_id:
			return c
	return {}


## A golden plan as the rules' plan dictionary.
static func plan_of(raw_plan: Dictionary) -> Dictionary:
	return {"ghost": cells(raw_plan["ghost"]), "dark": cells(raw_plan["dark"]), "decoys": cells(raw_plan["decoys"])}
