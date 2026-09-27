class_name LegendSpot
extends RefCounted
## Where a map legend goes over a city map (H22 #9, #14): the first spot in its area that
## covers no node icon and no node label (the raid setup's legend pinned bottom left
## covered CORE at big text; the route view had none). Spots are tried along the area's
## columns left to right, each from the bottom up (the legend's old corner first), in a
## fixed order; when no spot is clear the one covering the least wins. A legend taller or
## wider than its area is scaled down to fit it (the last resort at big text). A screen
## that owns the camera can ask `fit_beside` how to frame the map so the nodes leave the
## legend's column free. View only.

## Step between the spots tried (px) and the margin kept from the area's edges (px).
const STEP := 16.0
const MARGIN := 10.0
## Clearance round a node icon (share of its radius).
const ICON_CLEAR := 0.3


## Screen rects of `overlay`'s node icons (with a little clearance), tier pips and, with
## `labels`, node labels. The legend is placed against icons and pips only: the screen
## registers it with `CityMapOverlay.avoid_controls`, so the labels make way for it.
static func node_rects(overlay: CityMapOverlay, labels: bool = true) -> Array[Rect2]:
	var out: Array[Rect2] = []
	if overlay == null or not is_instance_valid(overlay) or not overlay.is_inside_tree():
		return out
	var xf := overlay.get_global_transform()
	var k := xf.get_scale().x
	for n in overlay.nodes:
		var at := overlay.icon_pos(n)
		if at.x == INF:
			continue
		var r := overlay.icon_radius(n) * k
		var p := xf * at
		out.append(Rect2(p - Vector2(r, r), Vector2(r, r) * 2.0).grow(r * ICON_CLEAR))
		var pips := overlay.tier_pips_rect(n)
		if pips.has_area():
			out.append(Rect2(xf * pips.position, pips.size * xf.get_scale()))
	if labels:
		var rects := overlay.label_rects()
		for key in rects:
			var lr: Rect2 = rects[key]
			out.append(Rect2(xf * lr.position, lr.size * xf.get_scale()))
	return out


## Places `legend` (a child of the plain Control covering the map's open area) at the
## first spot clear of `overlay`'s nodes. Returns how much node area it still covers (px²).
static func place(legend: Control, overlay: CityMapOverlay) -> float:
	if legend == null or not is_instance_valid(legend) or not legend.is_inside_tree():
		return 0.0
	var area_ctl := legend.get_parent() as Control
	if area_ctl == null:
		return 0.0
	var area := area_ctl.get_global_rect()
	var own := legend.get_combined_minimum_size()
	legend.set_anchors_preset(Control.PRESET_TOP_LEFT)
	legend.grow_horizontal = Control.GROW_DIRECTION_END
	legend.grow_vertical = Control.GROW_DIRECTION_END
	legend.size = own
	var k := fit_scale(own, area.size)
	legend.scale = Vector2(k, k)
	var lsize := own * k
	var blocked := node_rects(overlay, false)
	var max_x := maxf(MARGIN, area.size.x - lsize.x - MARGIN)
	var max_y := maxf(MARGIN, area.size.y - lsize.y - MARGIN)
	var best := Vector2(MARGIN, max_y)
	var best_hits := INF
	var x := MARGIN
	while best_hits > 0.0:
		var y := max_y
		while true:
			var at := Vector2(x, y)
			var hits := covered(Rect2(area.position + at, lsize), blocked)
			if hits < best_hits:
				best_hits = hits
				best = at
			if hits == 0.0 or y <= MARGIN:
				break
			y = maxf(MARGIN, y - STEP)
		if x >= max_x:
			break
		x = minf(max_x, x + STEP)
	legend.position = best
	return best_hits


## The scale that fits a legend of `own` size in an area of `room` (1 when it fits).
static func fit_scale(own: Vector2, room: Vector2) -> float:
	var k := 1.0
	if own.x > 0.0:
		k = minf(k, (room.x - MARGIN * 2.0) / own.x)
	if own.y > 0.0:
		k = minf(k, (room.y - MARGIN * 2.0) / own.y)
	return maxf(0.1, k)


## How to frame the map so its nodes fit beside the legend's column at the area's left
## edge: {"zoom": factor (at most 1), "from": the nodes' box centre, "to": where that
## centre should go} (screen px); {} when the nodes already leave the column free.
static func fit_beside(legend: Control, overlay: CityMapOverlay) -> Dictionary:
	if legend == null or not is_instance_valid(legend) or not (legend.get_parent() is Control):
		return {}
	var area := (legend.get_parent() as Control).get_global_rect()
	var column := MARGIN + legend.get_combined_minimum_size().x * legend.scale.x + MARGIN
	var free := Rect2(area.position.x + column, area.position.y + MARGIN, area.size.x - column - MARGIN, area.size.y - MARGIN * 2.0)
	var rects := node_rects(overlay, false)
	if rects.is_empty() or free.size.x <= 0.0 or free.size.y <= 0.0:
		return {}
	var box := rects[0]
	for r in rects:
		box = box.merge(r)
	if free.encloses(box):
		return {}
	var k := minf(1.0, minf(free.size.x / maxf(1.0, box.size.x), free.size.y / maxf(1.0, box.size.y)))
	return {"zoom": k, "from": box.get_center(), "to": free.get_center()}


## Node area (px²) `rect` covers.
static func covered(rect: Rect2, blocked: Array[Rect2]) -> float:
	var hits := 0.0
	for b in blocked:
		if rect.intersects(b):
			hits += rect.intersection(b).get_area()
	return hits
