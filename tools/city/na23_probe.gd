extends RefCounted
## LOOK-TOOLBOX slab probe, lab only (na23_lab --probe=x,y[;x,y...]): what the camera ray through a screen pixel hits first. Lists the
## nearest city buildings whose box the ray enters (merged lot records, plan BU -> world (x, z, -y)) and the nearest visual nodes whose
## global AABB it enters (MultiMesh nodes report their whole box, so the building list is the one to trust for city mass).


## Report lines for pixel `px` of `cam` over the city `city` and the node tree under `root`.
static func probe(cam: Camera3D, px: Vector2, city: Dictionary, route: Array, near_r2: Dictionary, root: Node) -> Array:
	var o := cam.project_ray_origin(px)
	var d := cam.project_ray_normal(px)
	var out: Array = ["probe %s: cam %s dir %s" % [px, o, d]]
	var hits: Array = []
	for b: Dictionary in StreetR2Adapter.buildings(city):
		var lo := Vector3(float(b["x0"]), float(b["z0"]), -float(b["y1"]))
		var hi := Vector3(float(b["x1"]), float(b["z0"]) + float(b["h"]), -float(b["y0"]))
		var t := _ray_box(o, d, lo, hi)
		if t >= 0.0:
			hits.append([t, String(b["uid"]), float(b["h"]), float(b["z0"]), lo, hi])
	hits.sort_custom(func(a: Array, c: Array) -> bool: return a[0] < c[0] or (a[0] == c[0] and String(a[1]) < String(c[1])))
	for h: Array in hits.slice(0, 4):
		out.append("  building %s at %.1f BU: h %.1f z0 %.1f box %s..%s route %s r2-frontage %s" % [h[1], h[0], h[2], h[3], h[4], h[5],
			route.has(h[1]), near_r2.has(h[1])])
	var nodes: Array = []
	_walk(root, o, d, nodes)
	nodes.sort_custom(func(a: Array, c: Array) -> bool: return a[0] < c[0] or (a[0] == c[0] and String(a[1]) < String(c[1])))
	for n: Array in nodes.slice(0, 8):
		out.append("  node %s at %.1f BU (aabb %s)" % [n[1], n[0], n[2]])
	return out


static func _walk(n: Node, o: Vector3, d: Vector3, acc: Array) -> void:
	if n is VisualInstance3D and (n as Node3D).is_visible_in_tree():
		var vi := n as VisualInstance3D
		var bx := vi.global_transform * vi.get_aabb()
		var t := _ray_box(o, d, bx.position, bx.end)
		if t >= 0.0 and bx.size.length() < 2000.0:
			acc.append([t, String(n.get_path()).right(90) + " [" + n.get_class() + "]", bx.size])
	for c in n.get_children():
		_walk(c, o, d, acc)


## Entry distance of ray o + t d into the box lo..hi (0 when inside), -1 when it misses.
static func _ray_box(o: Vector3, d: Vector3, lo: Vector3, hi: Vector3) -> float:
	var t0 := -INF
	var t1 := INF
	for i in 3:
		if absf(d[i]) < 1e-9:
			if o[i] < lo[i] or o[i] > hi[i]:
				return -1.0
			continue
		var a := (lo[i] - o[i]) / d[i]
		var b := (hi[i] - o[i]) / d[i]
		t0 = maxf(t0, minf(a, b))
		t1 = minf(t1, maxf(a, b))
	if t1 < maxf(t0, 0.0):
		return -1.0
	return maxf(t0, 0.0)
