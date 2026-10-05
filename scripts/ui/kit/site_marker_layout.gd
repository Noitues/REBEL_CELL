class_name SiteMarkerLayout
extends RefCounted
## ART-5 5d: where the City Grid's Site markers and their labels go on screen, from the
## anchors a GridMarkerProjection gives (pure, headless-testable; the map overlay follows
## the same rules on today's city):
## - each disc floats SiteMarker.PAD_DROP over its pad; markers are placed front to back
##   (nearest anchor first, ties by Site id) and one that would touch a marker already
##   placed moves to the first free spot beside it, then a step higher: no two overlap;
## - labels (bible §4.1: label avoidance is required at the Grid zoom) by priority, ties by
##   Site id, at the first free spot round their marker (below, above, right, left, the
##   corners), inside the view, clear of every marker, label and blocked area; a label with
##   no room is left out (its Site keeps its tooltip);
## - picking: the nearest marker whose hit radius holds the point.

## Spots tried beside a marker before a step up (columns: here, right, left).
const FAN: Array[int] = [0, 1, -1]
const STACK_MAX := 6
## Gap kept between markers and between a label and anything (px x k).
const GAP := 3.0


## Disc centres (id -> px) for `anchors` (id -> px) of markers `specs` (id -> spec) at k.
static func place_discs(anchors: Dictionary, specs: Dictionary, k: float = 1.0) -> Dictionary:
	var ids: Array = anchors.keys().filter(func(id: Variant) -> bool: return specs.has(id) and (anchors[id] as Vector2).x != INF)
	ids.sort_custom(func(a: StringName, b: StringName) -> bool:
		var ya: float = (anchors[a] as Vector2).y
		var yb: float = (anchors[b] as Vector2).y
		if not is_equal_approx(ya, yb):
			return ya > yb
		return String(a) < String(b))
	var out := {}
	var placed: Array[Rect2] = []
	for id in ids:
		var spec: Dictionary = specs[id]
		var base: Vector2 = (anchors[id] as Vector2) - Vector2(0, SiteMarker.PAD_DROP * k)
		var own := SiteMarker.box(spec, base, k).size + Vector2(GAP, GAP) * k
		var at := base
		var found := false
		for level in STACK_MAX:
			for col in FAN:
				at = base + Vector2(col * own.x, -level * own.y)
				if _free(SiteMarker.box(spec, at, k), placed, GAP * k):
					found = true
					break
			if found:
				break
		placed.append(SiteMarker.box(spec, at, k))
		out[id] = at
	return out


## Label rects (id -> Rect2) for labels of `sizes` (id -> Vector2 px) round `discs`, by
## `prio` (id -> int, lower first), inside `area`, clear of every marker, label and
## `blocked` rect. Labels with no room are left out.
static func place_labels(discs: Dictionary, specs: Dictionary, sizes: Dictionary, prio: Dictionary, area: Rect2,
		blocked: Array[Rect2] = [], k: float = 1.0) -> Dictionary:
	var marks: Array[Rect2] = []
	var keys := discs.keys()
	keys.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	for id in keys:
		marks.append(SiteMarker.box(specs[id], discs[id], k))
	var order: Array = sizes.keys().filter(func(id: Variant) -> bool: return discs.has(id))
	order.sort_custom(func(a: StringName, b: StringName) -> bool:
		var pa := int(prio.get(a, 99))
		var pb := int(prio.get(b, 99))
		if pa != pb:
			return pa < pb
		return String(a) < String(b))
	var out := {}
	var taken: Array[Rect2] = []
	var g := GAP * k
	for id in order:
		var box: Vector2 = sizes[id]
		var body := SiteMarker.box(specs[id], discs[id], k)
		var c: Vector2 = discs[id]
		var spots: Array[Vector2] = [Vector2(c.x - box.x * 0.5, body.end.y + g), Vector2(c.x - box.x * 0.5, body.position.y - g - box.y),
			Vector2(body.end.x + g, c.y - box.y * 0.5), Vector2(body.position.x - g - box.x, c.y - box.y * 0.5),
			Vector2(body.end.x + g, body.end.y + g), Vector2(body.position.x - g - box.x, body.end.y + g),
			Vector2(body.end.x + g, body.position.y - g - box.y), Vector2(body.position.x - g - box.x, body.position.y - g - box.y)]
		for s in spots:
			var r := Rect2(s, box)
			if area.encloses(r) and _free(r, marks, g) and _free(r, taken, g) and _free(r, blocked, 0.0):
				out[id] = r
				taken.append(r)
				break
	return out


## The marker under `p` (nearest disc centre within its hit radius), or &"".
static func pick(discs: Dictionary, specs: Dictionary, p: Vector2, k: float = 1.0) -> StringName:
	var best: StringName = &""
	var best_d := INF
	var keys := discs.keys()
	keys.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	for id in keys:
		var d := p.distance_to(discs[id])
		if d <= SiteMarker.hit_radius(specs[id], k) and d < best_d:
			best_d = d
			best = id
	return best


static func _free(r: Rect2, others: Array[Rect2], gap: float) -> bool:
	var grown := r.grow(gap * 0.5)
	for o in others:
		if grown.intersects(o.grow(gap * 0.5)):
			return false
	return true
