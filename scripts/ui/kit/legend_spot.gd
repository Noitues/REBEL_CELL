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
## ANIM-R1 M15: the most spots tried along each axis (a bigger area is sampled evenly).
const SPOTS_MAX := 200
## Clearance round a node icon (share of its radius).
const ICON_CLEAR := 0.3
## The most one `fit_into` pass zooms out (a factor per pass; later passes settle it), and
## the least zoom-in worth a new frame when the nodes already fit.
const MIN_FIT_ZOOM := 0.4
const REFIT_SLACK := 0.05
## How far inside the free area a fit aims (px), and the share of a zoom-out it takes.
const FIT_INSET := 8.0
const FIT_OVERSHOOT := 0.9


## Screen rects of `overlay`'s node icons (with a little clearance), tier pips and, with
## `labels`, node labels. The legend is placed against icons and pips only: the screen
## registers it with `CityMapOverlay.avoid_controls`, so the labels make way for it.
## ANIM-R3 B8: `only` (node ids; empty: every node) limits the rects to those nodes.
static func node_rects(overlay: CityMapOverlay, labels: bool = true, only: Array = []) -> Array[Rect2]:
	var out: Array[Rect2] = []
	if overlay == null or not is_instance_valid(overlay) or not overlay.is_inside_tree():
		return out
	var xf := overlay.get_global_transform()
	var k := xf.get_scale().x
	for n in overlay.nodes:
		if not only.is_empty() and not only.has(n["id"]):
			continue
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
	# ANIM-R1 M15: measured geometry that is not finite (a frame mid-layout) never loops:
	# maxf / minf with NaN kept the old loops going for ever.
	if not (is_finite(max_x) and is_finite(max_y) and is_finite(lsize.x) and is_finite(lsize.y)):
		legend.position = Vector2(MARGIN, MARGIN)
		return INF
	var best := Vector2(MARGIN, max_y)
	var best_hits := INF
	# The spots tried: at most SPOTS_MAX per axis (a huge area is sampled, never walked).
	var cols := ceili((max_x - MARGIN) / STEP) + 1
	var rows := ceili((max_y - MARGIN) / STEP) + 1
	var step_x := STEP if cols <= SPOTS_MAX else (max_x - MARGIN) / (SPOTS_MAX - 1)
	var step_y := STEP if rows <= SPOTS_MAX else (max_y - MARGIN) / (SPOTS_MAX - 1)
	cols = mini(cols, SPOTS_MAX)
	rows = mini(rows, SPOTS_MAX)
	for ci in cols:
		var x := minf(max_x, MARGIN + step_x * ci)
		for ri in rows:
			var at := Vector2(x, maxf(MARGIN, max_y - step_y * ri))
			var hits := covered(Rect2(area.position + at, lsize), blocked)
			if hits < best_hits:
				best_hits = hits
				best = at
			if hits == 0.0:
				break
		if best_hits <= 0.0:
			break
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


## H23 #5: how to frame the map so every node (icon and tier pips) lies inside `free`
## (screen px), as large as `max_zoom` (a factor on the current zoom) allows: {"zoom":
## factor, "from": the icon centres' box centre, "to": where it should go}; {} when the
## nodes already fit and zooming in would gain less than REFIT_SLACK. Icons and pips keep
## their screen size as the city zooms, so only the spread between icon centres scales:
## the answer is exact but for icons floating up to clear each other. The zoom factor is
## never below `min_zoom` (a floor on how small the map may get; at the floor the nodes
## are centred in `free` as well as they go).
## ANIM-R3 B8: `only` (node ids; empty: every node) fits just those nodes, and `extra`
## (screen rects, e.g. the "you are here" marker off the nodes) is kept inside too.
static func fit_into(overlay: CityMapOverlay, free: Rect2, max_zoom: float = 1.0, min_zoom: float = MIN_FIT_ZOOM, only: Array = [], extra: Array[Rect2] = []) -> Dictionary:
	var rects := node_rects(overlay, false, only)
	rects.append_array(extra)
	if rects.is_empty() or free.size.x <= 0.0 or free.size.y <= 0.0:
		return {}
	var xf := overlay.get_global_transform()
	var centres := Rect2()
	var first := true
	for n in overlay.nodes:
		if not only.is_empty() and not only.has(n["id"]):
			continue
		var at := overlay.icon_pos(n)
		if at.x == INF:
			continue
		var p := xf * at
		centres = Rect2(p, Vector2.ZERO) if first else centres.expand(p)
		first = false
	for r in extra:
		centres = Rect2(r.get_center(), Vector2.ZERO) if first else centres.expand(r.get_center())
		first = false
	var box := rects[0]
	for r in rects:
		box = box.merge(r)
	# Aim a little inside `free` so a small drift (icons floating to clear each other)
	# never asks for another pass.
	var aim := free.grow(-FIT_INSET) if free.size.x > FIT_INSET * 4.0 and free.size.y > FIT_INSET * 4.0 else free
	var pad_lo := centres.position - box.position
	var pad_hi := box.end - centres.end
	var room := (aim.size - pad_lo - pad_hi).max(Vector2.ONE)
	var k := max_zoom
	if centres.size.x > 0.0:
		k = minf(k, room.x / centres.size.x)
	if centres.size.y > 0.0:
		k = minf(k, room.y / centres.size.y)
	if free.encloses(box) and k < 1.0 + REFIT_SLACK:
		return {}
	if k < 1.0:
		# Zoomed out, crowded icons float up to clear each other and the box grows a little
		# past the estimate: aim lower so one more pass settles it.
		k *= FIT_OVERSHOOT
	k = maxf(k, minf(1.0, min_zoom))
	return {"zoom": k, "from": centres.get_center(), "to": aim.position + pad_lo + room * 0.5}


## Node area (px²) `rect` covers.
static func covered(rect: Rect2, blocked: Array[Rect2]) -> float:
	var hits := 0.0
	for b in blocked:
		if rect.intersects(b):
			hits += rect.intersection(b).get_area()
	return hits
