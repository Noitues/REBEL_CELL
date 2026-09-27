class_name CityBakeCache
extends RefCounted
## The baked city (H20): NeonCity's procedural geometry (millions of vertices, seconds of
## GDScript to build) is rendered ONCE per look into a texture and every backdrop and map
## view then draws that texture. Shared by all scenes (static, lives as long as the
## program): switching scenes re-bakes only when the look changes (district, net look,
## palette, texture, Heat creep step, territory influence...) or the camera leaves every
## baked region of that look. Each entry also keeps the overlay data built with the
## image (roof outlines, beacons, window lights, traffic sparks, signs) in world space.
## Least recently used entries are dropped past CAPACITY or BUDGET_BYTES.
##
## Headless (tests) has a dummy renderer: `can_bake()` is false there and NeonCity keeps
## drawing procedurally, so nothing waits on a GPU readback. A bake whose readback comes
## back empty is marked failed and the city falls back the same way. View-only.

## Entries kept, and their texture memory budget (least recently used dropped first).
const CAPACITY := 8
const BUDGET_BYTES := 160 * 1024 * 1024
## Largest texture a bake may produce (pixels); the bake scale shrinks to fit.
const MAX_PIXELS := 12_000_000
## Name of the persistent holder node under the tree root (the bake viewports live there).
const HOLDER_NAME := "CityBakeHolder"
## Frames rendered after the painter's draw before the pixels are read back.
const READBACK_FRAMES := 2

## Off switch (design tools that want the old per-frame procedural city).
static var enabled: bool = true
## key -> {"texture": Texture2D, "region": Rect2, "scale": float, "roofs", "beacons",
## "lights", "trails", "signs"} or {"failed": true}.
static var _entries: Dictionary = {}
static var _lru: Array[String] = []
## key -> Array[int] of NeonCity instance ids waiting for it.
static var _pending: Dictionary = {}
## Bakes finished (tests and the probe read it).
static var bakes_done: int = 0


## True when this renderer can bake (never headless).
static func can_bake() -> bool:
	return enabled and DisplayServer.get_name() != "headless"


## The cache key for a look: every value that changes the image, in a fixed order.
static func key_of(parts: Array) -> String:
	var out := PackedStringArray()
	for p in parts:
		out.append(var_to_str(p))
	return "#".join(out)


## The finished entry for `key` ({} while baking or unknown). Marks it recently used.
static func entry(key: String) -> Dictionary:
	if not _entries.has(key):
		return {}
	_lru.erase(key)
	_lru.append(key)
	return _entries[key]


## The key of a finished bake of `look` whose region covers `view` (world px), most
## recently used first; "" when none does.
static func find(look: String, view: Rect2) -> String:
	for k in range(_lru.size() - 1, -1, -1):
		var key := _lru[k]
		var e: Dictionary = _entries[key]
		if e.get("look", "") == look and (e.get("region", Rect2()) as Rect2).encloses(view):
			return key
	return ""


## A stand-in while a bake runs: the most recent finished bake of `look` that overlaps
## `view` at all; "" when none does.
static func find_overlapping(look: String, view: Rect2) -> String:
	for k in range(_lru.size() - 1, -1, -1):
		var key := _lru[k]
		var e: Dictionary = _entries[key]
		if e.get("look", "") == look and not e.has("failed") and (e.get("region", Rect2()) as Rect2).intersects(view):
			return key
	return ""


static func has(key: String) -> bool:
	return _entries.has(key)


static func is_pending(key: String) -> bool:
	return _pending.has(key)


## Texture memory held by the cache (bytes, RGBA8).
static func memory_bytes() -> int:
	var total := 0
	for k in _entries:
		var tex: Texture2D = _entries[k].get("texture")
		if tex != null:
			total += tex.get_width() * tex.get_height() * 4
	return total


static func clear() -> void:
	_entries.clear()
	_lru.clear()


## Bake scale for a region: `wanted`, shrunk so the texture stays under MAX_PIXELS.
static func fit_scale(region: Rect2, wanted: float) -> float:
	var area := maxf(1.0, region.size.x * region.size.y)
	return minf(wanted, sqrt(MAX_PIXELS / area))


## Starts a bake of `painter` (a NeonCity set up by `NeonCity.make_painter`) for `key`
## (a region of `look`), unless one is running; `waiter` is redrawn when it lands.
static func request(key: String, look: String, painter: NeonCity, waiter: Node) -> void:
	if _pending.has(key):
		wait(key, waiter)
		painter.free()
		return
	_pending[key] = [waiter.get_instance_id()]
	_bake(key, look, painter)


## Stores a finished bake (the baker, and tests that stand in for the renderer).
static func store(key: String, e: Dictionary) -> void:
	_entries[key] = e
	_lru.erase(key)
	_lru.append(key)
	while _lru.size() > 1 and (_lru.size() > CAPACITY or memory_bytes() > BUDGET_BYTES):
		_entries.erase(_lru.pop_front())


## Redraws `waiter` when the running bake for `key` lands.
static func wait(key: String, waiter: Node) -> void:
	if _pending.has(key) and not (_pending[key] as Array).has(waiter.get_instance_id()):
		(_pending[key] as Array).append(waiter.get_instance_id())


static func _holder() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	var holder := tree.root.get_node_or_null(HOLDER_NAME)
	if holder == null:
		holder = Node.new()
		holder.name = HOLDER_NAME
		tree.root.add_child(holder)
	return holder


static func _bake(key: String, look: String, painter: NeonCity) -> void:
	var vp := SubViewport.new()
	vp.size = Vector2i(ceili(painter.size.x * painter.scale.x), ceili(painter.size.y * painter.scale.y))
	vp.transparent_bg = false
	vp.disable_3d = true
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	vp.add_child(painter)
	_holder().add_child(vp)
	# The painter builds its geometry in its first draw; let the viewport render it
	# (READBACK_FRAMES frames, so the render has surely landed), then read the pixels back
	# and drop the viewport and its geometry.
	await painter.rebuilt
	for f in READBACK_FRAMES:
		await RenderingServer.frame_post_draw
	var img: Image = vp.get_texture().get_image() if is_instance_valid(vp) else null
	var e := {"look": look, "region": painter.painter_region, "scale": painter.scale.x}
	if img == null or img.is_empty():
		e["failed"] = true
	else:
		e["texture"] = ImageTexture.create_from_image(img)
		e.merge(painter.overlay_data())
	if is_instance_valid(vp):
		vp.queue_free()
	store(key, e)
	bakes_done += 1
	var waiters: Array = _pending.get(key, [])
	_pending.erase(key)
	for id in waiters:
		var w := instance_from_id(id) as CanvasItem
		if w != null and is_instance_valid(w):
			w.queue_redraw()
