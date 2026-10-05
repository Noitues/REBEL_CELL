class_name CityNetworkData
extends RefCounted
## ART-5 5a: the network ground decal's buffers (bible §6.1 "Network = one ground decal
## shader": a node buffer and a link buffer the decal shader reads). Built read-only from a
## map's graph (the Grid's Sites and links as CityLayout / CityMapOverlay place them: each
## node on its building's lot, each link along the streets), in world space. Pure data:
## the buffers are images (one texel per field) so the shader and the tests read the same
## numbers. Views never change state: this only reads the graph it is given.
##
## Node texels (row 0: world x, world z, radius share (big 1.4, else 1), state; row 1:
## colour rgb, tier). Segment texels (row 0: a.x, a.z, b.x, b.z; row 1: colour rgb, flags;
## row 2: length along the link before a, link length, width share, 0).

## Node states the decal draws (a ring and disc per state).
enum NodeState { CORPORATE, CLEARED, CLAIMED, TAKEN, HOME }
## Link flags (bit field in the segment's flags texel).
const FLAG_DASHED := 1
const FLAG_FLOW := 2
const FLAG_THREAT := 4
## Width of a link of width `w` px on the 2D map as a share of the decal's trace.
const WIDTH_REF := 3.0

## {"id", "world": Vector3, "color": Color, "state": int, "tier": int, "big": bool}
var nodes: Array[Dictionary] = []
## {"a": Vector3, "b": Vector3, "color": Color, "flags": int, "u0": float, "len": float,
## "width": float}
var segments: Array[Dictionary] = []


## The decal data of a map graph: `p_nodes` / `p_edges` as CityLayout.grid_graph makes them,
## `lot_of` (id -> Vector2i, the node's building lot) and `route_of` (edge index -> the
## street route in lot points) as the overlay placed them. Ties: graph order (CityLayout
## sorts its own data).
static func from_graph(cfg: CityConfig, p_nodes: Array[Dictionary], p_edges: Array[Dictionary], lot_of: Callable,
		route_of: Callable) -> CityNetworkData:
	var d := CityNetworkData.new()
	for n in p_nodes:
		var lot: Vector2i = lot_of.call(n["id"])
		d.nodes.append({"id": n["id"], "world": CityIsoCamera.lot_to_world(cfg, Vector2(lot) + Vector2(0.5, 0.5)),
			"color": n.get("color", Palette.NET_CYAN), "state": state_of(n), "tier": int(n.get("tier", 0)),
			"big": bool(n.get("big", false))})
	for k in p_edges.size():
		var e := p_edges[k]
		var pts: PackedVector2Array = route_of.call(k)
		if pts.size() < 2:
			continue
		var flags := 0
		if e.get("dashed", false):
			flags |= FLAG_DASHED
		if e.get("flow", false):
			flags |= FLAG_FLOW
		if e.get("arrows", false):
			flags |= FLAG_THREAT
		var world := PackedVector3Array()
		var total := 0.0
		for q in pts:
			world.append(CityIsoCamera.lot_to_world(cfg, q))
		for q in world.size() - 1:
			total += world[q].distance_to(world[q + 1])
		var u := 0.0
		for q in world.size() - 1:
			var seg := world[q].distance_to(world[q + 1])
			d.segments.append({"a": world[q], "b": world[q + 1], "color": e.get("color", Palette.NET_CYAN), "flags": flags,
				"u0": u, "len": total, "width": float(e.get("width", WIDTH_REF)) / WIDTH_REF})
			u += seg
	return d


## The decal state of a graph node (its map kind and mark, as CityLayout sets them).
static func state_of(n: Dictionary) -> int:
	if String(n.get("kind", "")) == CityMapOverlay.KIND_HOME:
		return NodeState.HOME
	match String(n.get("mark", "")):
		CityMapOverlay.MARK_SPRAY:
			return NodeState.CLAIMED
		CityMapOverlay.MARK_CROSS:
			return NodeState.TAKEN
	if (n.get("color", Color.BLACK) as Color).is_equal_approx(Palette.NET_CYAN):
		return NodeState.CLEARED
	return NodeState.CORPORATE


## The node buffer (`cap` texels wide, 2 rows; nodes past `cap` are left out).
func node_image(cap: int) -> Image:
	var img := Image.create(maxi(1, cap), 2, false, Image.FORMAT_RGBAF)
	for k in mini(cap, nodes.size()):
		var n := nodes[k]
		var w: Vector3 = n["world"]
		var c: Color = n["color"]
		img.set_pixel(k, 0, Color(w.x, w.z, 1.4 if n["big"] else 1.0, float(n["state"])))
		img.set_pixel(k, 1, Color(c.r, c.g, c.b, float(n["tier"])))
	return img


## The segment buffer (`cap` texels wide, 3 rows; segments past `cap` are left out).
func segment_image(cap: int) -> Image:
	var img := Image.create(maxi(1, cap), 3, false, Image.FORMAT_RGBAF)
	for k in mini(cap, segments.size()):
		var s := segments[k]
		var a: Vector3 = s["a"]
		var b: Vector3 = s["b"]
		var c: Color = s["color"]
		img.set_pixel(k, 0, Color(a.x, a.z, b.x, b.z))
		img.set_pixel(k, 1, Color(c.r, c.g, c.b, float(s["flags"])))
		img.set_pixel(k, 2, Color(float(s["u0"]), float(s["len"]), float(s["width"]), 0.0))
	return img


## The world box of the network (X/Z; empty when there are no nodes).
func bounds() -> Rect2:
	var r := Rect2()
	var first := true
	for n in nodes:
		var w: Vector3 = n["world"]
		r = Rect2(Vector2(w.x, w.z), Vector2.ZERO) if first else r.expand(Vector2(w.x, w.z))
		first = false
	for s in segments:
		for w: Vector3 in [s["a"], s["b"]]:
			r = Rect2(Vector2(w.x, w.z), Vector2.ZERO) if first else r.expand(Vector2(w.x, w.z))
			first = false
	return r
