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
## ANIM-R1 M2: a painter's geometry is built on a worker thread (the frame keeps drawing
## the old image meanwhile); off builds it in the painter's first draw, as before.
static var threaded: bool = true
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


## ANIM-R1 M2: the viewport's picture copied on the GPU into a texture of its own (no
## readback to the CPU and upload back, ~60 ms for a big bake); null when the renderer
## has no RenderingDevice (the Compatibility renderer) or the copy fails.
static func _gpu_copy(vp: SubViewport) -> Texture2D:
	if not gpu_copy:
		return null
	var rd := RenderingServer.get_rendering_device()
	if rd == null:
		return null
	var src := RenderingServer.texture_get_rd_texture(vp.get_texture().get_rid())
	if not src.is_valid():
		return null
	var src_fmt := rd.texture_get_format(src)
	var fmt := RDTextureFormat.new()
	fmt.width = src_fmt.width
	fmt.height = src_fmt.height
	fmt.format = src_fmt.format
	fmt.usage_bits = RenderingDevice.TEXTURE_USAGE_SAMPLING_BIT | RenderingDevice.TEXTURE_USAGE_CAN_COPY_TO_BIT | RenderingDevice.TEXTURE_USAGE_CAN_COPY_FROM_BIT
	var dst := rd.texture_create(fmt, RDTextureView.new())
	if not dst.is_valid():
		return null
	if rd.texture_copy(src, dst, Vector3.ZERO, Vector3.ZERO, Vector3(fmt.width, fmt.height, 1), 0, 0, 0, 0) != OK:
		rd.free_rid(dst)
		return null
	var tex := BakedTexture.new()
	tex.texture_rd_rid = dst
	return tex


## Off switch for the GPU copy (tests and a renderer that shows it wrong).
static var gpu_copy: bool = true


static func _holder() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	var holder := tree.root.get_node_or_null(HOLDER_NAME)
	if holder == null:
		holder = Node.new()
		holder.name = HOLDER_NAME
		tree.root.add_child(holder)
	return holder


static func _bake(key: String, look: String, painter: NeonCity) -> void:
	if threaded:
		# ANIM-R1 M2: the seconds of GDScript that build the geometry run off the main
		# thread; the frames go on (the old image, or a stand-in, shows until this lands).
		var tree := Engine.get_main_loop() as SceneTree
		var task := WorkerThreadPool.add_task(painter.prebuild, true, "city bake")
		while not WorkerThreadPool.is_task_completed(task):
			await tree.process_frame
		WorkerThreadPool.wait_for_task_completion(task)
	var vp := SubViewport.new()
	vp.size = Vector2i(ceili(painter.size.x * painter.scale.x), ceili(painter.size.y * painter.scale.y))
	vp.transparent_bg = false
	vp.disable_3d = true
	# ANIM-R1 M2: a threaded bake renders once, after its chunks are all in.
	vp.render_target_update_mode = SubViewport.UPDATE_DISABLED if threaded else SubViewport.UPDATE_ALWAYS
	vp.add_child(painter)
	_holder().add_child(vp)
	# The painter builds its geometry in its first draw (threaded: before it, and it is
	# submitted a chunk a frame); let the viewport render it (READBACK_FRAMES frames, so the
	# render has surely landed), then take the picture and drop the viewport and geometry.
	await painter.rebuilt
	if threaded:
		var at := 0
		while at >= 0:
			at = painter.submit_chunk(at)
			if at >= 0:
				await (Engine.get_main_loop() as SceneTree).process_frame
		vp.render_target_update_mode = SubViewport.UPDATE_ONCE
	for f in READBACK_FRAMES:
		await RenderingServer.frame_post_draw
	var e := {"look": look, "region": painter.painter_region, "scale": painter.scale.x}
	var tex: Texture2D = _gpu_copy(vp) if is_instance_valid(vp) else null
	if tex == null and is_instance_valid(vp):
		var img: Image = vp.get_texture().get_image()
		if img != null and not img.is_empty():
			tex = ImageTexture.create_from_image(img)
	if tex == null:
		e["failed"] = true
	else:
		e["texture"] = tex
		e.merge(painter.overlay_data())
	painter.free_chunks()
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
