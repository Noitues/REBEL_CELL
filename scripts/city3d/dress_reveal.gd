class_name DressReveal
extends RefCounted
## NA-24: the `visibility_range` of a dressing group, from config only (PIPELINE_SPEC 5.2b). A group names a reveal asset and a tier
## (`DressingConfigData.groups`); the tier's distances are the rows of `NetrunArtConfigData.reveal` (`[tier, far, near]`, "N1
## calibration pending"). A group whose asset is "" or lists no such tier is the big layer: range 0 = always drawn.
## A tier node is drawn below `far` and cross-fades over `share * (far - near)` (never under `fade.min_share` of the interval).


## The `[tier, far, near]` row of `asset` / `tier`, or an empty array.
static func row_of(asset: String, tier: int) -> Array:
	var rv: Dictionary = NetrunArtConfigData.shipped().reveal
	if asset == "" or not rv.has(asset):
		return []
	for row: Array in rv[asset]:
		if int(row[0]) == tier:
			return row
	return []


## `{end, near, margin}` of `group` (BU): `end` 0 = always drawn.
static func range_of(group: String) -> Dictionary:
	var cfg := DressingConfigData.shipped()
	var g: Dictionary = cfg.groups[group]
	var row: Array = row_of(String(g["asset"]), int(g["tier"]))
	if row.is_empty():
		return {"end": 0.0, "near": 0.0, "margin": 0.0}
	var far: float = float(row[1])
	var near: float = float(row[2])
	var share: float = maxf(float(cfg.fade["share"]), float(cfg.fade["min_share"]))
	return {"end": far, "near": near, "margin": minf(far * 0.99, (far - near) * share)}


## True when `group` is drawn (at any opacity) at camera distance `d`.
static func is_drawn(group: String, d: float) -> bool:
	var r: Dictionary = range_of(group)
	return float(r["end"]) <= 0.0 or d < float(r["end"])


## Opacity 0..1 of `group` at camera distance `d` (1 inside `near`, smoothstep up to `end`).
static func weight(group: String, d: float) -> float:
	var r: Dictionary = range_of(group)
	if float(r["end"]) <= 0.0:
		return 1.0
	var span: float = maxf(float(r["end"]) - float(r["near"]), 0.001)
	var t: float = clampf((float(r["end"]) - d) / span, 0.0, 1.0)
	return t * t * (3.0 - 2.0 * t)


## Sets `visibility_range_end`, its margin and the self fade on `node` from the config of `group`.
static func apply(node: GeometryInstance3D, group: String) -> void:
	var r: Dictionary = range_of(group)
	node.visibility_range_begin = 0.0
	node.visibility_range_end = float(r["end"])
	node.visibility_range_end_margin = float(r["margin"])
	node.visibility_range_fade_mode = GeometryInstance3D.VISIBILITY_RANGE_FADE_SELF if float(r["end"]) > 0.0 else GeometryInstance3D.VISIBILITY_RANGE_FADE_DISABLED
