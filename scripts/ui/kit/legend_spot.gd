class_name LegendSpot
extends RefCounted
## Where a map legend goes over a city map (H22 #9, #14): the first spot in its area that
## covers no node icon and no node label (the raid setup's legend pinned bottom left
## covered CORE at big text; the route view had none). Spots are tried along the area's
## columns left to right, each from the bottom up (the legend's old corner first), in a
## fixed order; when no spot is clear the one covering the least wins. View only.

## Step between the spots tried (px) and the margin kept from the area's edges (px).
const STEP := 16.0
const MARGIN := 10.0
## Clearance round a node icon (share of its radius).
const ICON_CLEAR := 0.3


## Screen rects of `overlay`'s node icons (with a little clearance) and node labels.
static func node_rects(overlay: CityMapOverlay) -> Array[Rect2]:
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
	var labels := overlay.label_rects()
	for key in labels:
		var lr: Rect2 = labels[key]
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
	var lsize := legend.get_combined_minimum_size()
	legend.set_anchors_preset(Control.PRESET_TOP_LEFT)
	legend.grow_horizontal = Control.GROW_DIRECTION_END
	legend.grow_vertical = Control.GROW_DIRECTION_END
	legend.size = lsize
	var blocked := node_rects(overlay)
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


## Node area (px²) `rect` covers.
static func covered(rect: Rect2, blocked: Array[Rect2]) -> float:
	var hits := 0.0
	for b in blocked:
		if rect.intersects(b):
			hits += rect.intersection(b).get_area()
	return hits
