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
##
## ANIM-R2 R1 / R10 / R11: bakes queue for one build slot (MAX_BUILDING: a build holds its
## whole geometry until it is submitted, so memory stays bounded to one region's worth),
## the view's own bakes ahead of prebakes; a build runs on the worker pool in slices at
## once (NeonCity.BUILD_SLICES), joined in order; `find_pending` lets a view wait on a
## running bake that will cover it; `shutdown()` (the game quitting) stops and joins every
## running build and frees its painter, viewport and textures.
## ANIM-R3 B10: a bake whose every waiter is gone (the scene that asked for it was left:
## the HQ's Grid and playout prebakes when the jack takes the player into a run) is stale:
## it is dropped from the queue, or stopped if it is building, whenever a bake is asked for
## or the slot frees (`drop_stale`), so it never keeps the one build slot from the scene on
## screen. A bake's coroutine checks its own record (never just the key: after `shutdown`
## a new request for the same key has a record of its own).

## Entries kept, and their texture memory budget (least recently used dropped first).
const CAPACITY := 8
const BUDGET_BYTES := 160 * 1024 * 1024
## Largest texture a bake may produce (pixels); the bake scale shrinks to fit.
const MAX_PIXELS := 12_000_000
## Name of the persistent holder node under the tree root (the bake viewports live there).
const HOLDER_NAME := "CityBakeHolder"
## Frames rendered after the painter's draw before the pixels are read back.
const READBACK_FRAMES := 2
## ANIM-R2 R11: bakes building (geometry held in memory) at once; the rest queue.
const MAX_BUILDING := 1
## ANIM-R2 R1: the main-thread time a frame may spend handing a bake's chunks to the renderer
## (microseconds; a chunk takes a few ms, so one or two a frame).
const SUBMIT_BUDGET_USEC := 6000

## Off switch (design tools that want the old per-frame procedural city).
static var enabled: bool = true
## ANIM-R1 M2: a painter's geometry is built on the worker pool (the frame keeps drawing
## the old image meanwhile); off builds it in the painter's first draw, as before.
static var threaded: bool = true
## Test runs only (ANIM-R2 R1): a headless run pretends it can bake (the cities take the
## baked path: placement, the sky, bakes asked for) but nothing is built; a test lands a
## bake with `store`. Never on in the game.
static var simulate: bool = false
## key -> {"texture": Texture2D, "region": Rect2, "scale": float, "roofs", "beacons",
## "lights", "trails", "signs"} or {"failed": true}.
static var _entries: Dictionary = {}
static var _lru: Array[String] = []
## key -> {"waiters": Array[int] (instance ids redrawn when it lands), "look", "region"}.
static var _pending: Dictionary = {}
## Bakes waiting for the build slot: {"key", "look", "painter"}, the next first.
static var _queue: Array[Dictionary] = []
## Bakes running: key -> {"painter", "vp", "task", "group"} (what `shutdown` must stop).
static var _live: Dictionary = {}
static var _building: int = 0
## Bakes finished (tests and the probe read it).
static var bakes_done: int = 0


## True when this renderer can bake (never headless, but for a test's `simulate`).
static func can_bake() -> bool:
	return enabled and (DisplayServer.get_name() != "headless" or simulate)


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


## ANIM-R2 R1: the most recent finished bake of `look` covering at least `share` (0..1) of
## `view`; "" when none does.
static func find_covering(look: String, view: Rect2, share: float) -> String:
	var area := view.get_area()
	if area <= 0.0:
		return ""
	for k in range(_lru.size() - 1, -1, -1):
		var key := _lru[k]
		var e: Dictionary = _entries[key]
		if e.get("look", "") != look or e.has("failed") or not e.has("texture"):
			continue
		var r: Rect2 = e.get("region", Rect2())
		if r.intersects(view) and r.intersection(view).get_area() >= area * share:
			return key
	return ""


## ANIM-R2 R1: a running (or queued) bake of `look` whose region will cover `view`; "".
static func find_pending(look: String, view: Rect2) -> String:
	for key: String in _pending:
		var p: Dictionary = _pending[key]
		if p.get("look", "") == look and (p.get("region", Rect2()) as Rect2).encloses(view):
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


## Drops every finished bake (their textures, GPU ones included, are freed with the last
## reference).
static func clear() -> void:
	_entries.clear()
	_lru.clear()
	_keep.clear()


## ANIM-R2 R10: the game is quitting (or a test resets): every running build is told to stop
## and joined (its slices end within a few lots), its painter, slices and viewport freed;
## queued bakes are dropped; then `clear()`. Safe to call twice.
static func shutdown() -> void:
	for key: String in _live.keys():
		_stop(_live[key])
	_live.clear()
	for job in _queue:
		var p: NeonCity = job.get("painter")
		if p != null and is_instance_valid(p):
			p.free()
	_queue.clear()
	_pending.clear()
	_building = 0
	clear()


## Stops a running build's record `rec`: tells its painter and slices to stop, joins its
## worker tasks, frees its painter, slices and viewport. The caller drops it from `_live`.
static func _stop(rec: Dictionary) -> void:
	var painter: NeonCity = rec.get("painter")
	if painter != null and is_instance_valid(painter):
		painter.cancelled = true
		for t in painter._slices:
			if is_instance_valid(t):
				t.cancelled = true
	if rec.has("task"):
		WorkerThreadPool.wait_for_task_completion(int(rec["task"]))
		rec.erase("task")
	if rec.has("group"):
		WorkerThreadPool.wait_for_group_task_completion(int(rec["group"]))
		rec.erase("group")
	if painter != null and is_instance_valid(painter):
		painter.free_chunks()
		painter.free_slices()
		if not painter.is_inside_tree():
			painter.free()
	var vp: SubViewport = rec.get("vp")
	if vp != null and is_instance_valid(vp):
		vp.free()


## True when some waiter of the bake for `key` is still alive (a bake nobody waits for is
## stale).
static func _wanted(key: String) -> bool:
	for id in _pending.get(key, {}).get("waiters", []):
		var w := instance_from_id(id)
		if w != null and is_instance_valid(w) and not (w as Node).is_queued_for_deletion():
			return true
	return false


## ANIM-R3 B10: drops the bakes whose every waiter is gone (the scene that asked for them was
## left): queued ones leave the queue, a building one is stopped and gives the slot back.
## Returns how many were dropped. Called on every request and when the slot frees.
static func drop_stale() -> int:
	var dropped := 0
	for i in range(_queue.size() - 1, -1, -1):
		var job: Dictionary = _queue[i]
		if not _wanted(job["key"]):
			var p: NeonCity = job.get("painter")
			if p != null and is_instance_valid(p):
				p.free()
			_pending.erase(job["key"])
			_queue.remove_at(i)
			dropped += 1
	for key: String in _live.keys():
		if _wanted(key):
			continue
		var rec: Dictionary = _live[key]
		_live.erase(key)
		_pending.erase(key)
		if bool(rec.get("holding", false)):
			_building = maxi(0, _building - 1)
		_stop(rec)
		dropped += 1
	stale_dropped += dropped
	return dropped


## Stale bakes dropped so far (tests).
static var stale_dropped: int = 0


## Bakes running or queued (tests).
static func busy() -> int:
	return _live.size() + _queue.size()


## Bake scale for a region: `wanted`, shrunk so the texture stays under MAX_PIXELS.
static func fit_scale(region: Rect2, wanted: float) -> float:
	var area := maxf(1.0, region.size.x * region.size.y)
	return minf(wanted, sqrt(MAX_PIXELS / area))


## Starts a bake of `painter` (a NeonCity set up by `NeonCity.make_painter`) for `key`
## (a region of `look`), unless one is running; `waiter` is redrawn when it lands.
## ANIM-R2 R1: `urgent` (a view waiting on it) goes ahead of queued prebakes.
## ANIM-R5 P2: `outlive` bakes for the next scene (the HQ warmed from a run's end, a raid
## interlude's framing from the jack): the cache's own holder waits on it too, so it is never
## stale when the scene that asked for it goes.
static func request(key: String, look: String, painter: NeonCity, waiter: Node, urgent: bool = false, outlive: bool = false) -> void:
	drop_stale()
	if _pending.has(key):
		wait(key, waiter)
		if outlive:
			wait(key, _holder())
		painter.free()
		return
	_pending[key] = {"waiters": [waiter.get_instance_id()], "look": look, "region": painter.painter_region}
	if outlive:
		(_pending[key]["waiters"] as Array).append(_holder().get_instance_id())
	if simulate:
		painter.free()
		return
	var job := {"key": key, "look": look, "painter": painter}
	if urgent:
		_queue.push_front(job)
	else:
		_queue.append(job)
	_pump()


## Starts queued bakes while the build slot is free.
static func _pump() -> void:
	if _building >= MAX_BUILDING or not _queue.is_empty():
		drop_stale()
	while _building < MAX_BUILDING and not _queue.is_empty():
		var job: Dictionary = _queue.pop_front()
		_building += 1
		_bake(job["key"], job["look"], job["painter"])


## Stores a finished bake (the baker, and tests that stand in for the renderer).
## ANIM-R5 P2: the least recently used entry that no slot keeps (`keep`) goes first; kept
## ones go only when nothing else is left to drop.
static func store(key: String, e: Dictionary) -> void:
	_entries[key] = e
	_lru.erase(key)
	_lru.append(key)
	while _lru.size() > 1 and (_lru.size() > CAPACITY or memory_bytes() > BUDGET_BYTES):
		var drop := 0
		while drop < _lru.size() - 1 and _kept_keys().has(_lru[drop]):
			drop += 1
		_entries.erase(_lru[drop])
		_lru.remove_at(drop)
	# A simulated bake (tests) lands here: its waiters redraw as a real one's do.
	if _pending.has(key) and not _live.has(key):
		_land(key)


## ANIM-R5 P2: named slots, each keeping one entry in the cache past the LRU (the run's route
## while its pages come and go: the route after a fight, loot or an event came back to the
## silhouette when the pages' bakes had pushed it out).
static var _keep: Dictionary = {}


## Keeps `key` in slot `slot` (replacing what the slot kept); "" empties the slot.
static func keep(slot: StringName, key: String) -> void:
	if key == "":
		_keep.erase(slot)
	else:
		_keep[slot] = key


## The key slot `slot` keeps ("" when none).
static func kept_key(slot: StringName) -> String:
	return String(_keep.get(slot, ""))


static func _kept_keys() -> Array:
	return _keep.values()


## Redraws `waiter` when the running bake for `key` lands.
static func wait(key: String, waiter: Node) -> void:
	if not _pending.has(key):
		return
	var ids: Array = _pending[key]["waiters"]
	if not ids.has(waiter.get_instance_id()):
		ids.append(waiter.get_instance_id())


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
	return BakedTexture.of_rd(dst)


## Off switch for the GPU copy (tests and a renderer that shows it wrong).
static var gpu_copy: bool = true


## ANIM-R5 P1: the bake's picture is its viewport's own render target, the viewport kept
## (never updated again; its painter and geometry go) and drawn through its ViewportTexture
## (`BakedTexture.of_viewport`): no second texture is made or filled in the landing frame.
## (ANIM-R4 H10 wrapped the target in a Texture2DRD; Godot refuses one over a viewport's
## shared texture, so every kept bake drew nothing.) Null with the switch off.
static func _keep_viewport(vp: SubViewport) -> Texture2D:
	if not keep_viewports:
		return null
	vp.render_target_update_mode = SubViewport.UPDATE_DISABLED
	return BakedTexture.of_viewport(vp)


## Keep the bake viewports (ANIM-R5 P1; see DECISIONS "ANIM-R5 city" for the measurement);
## off runs the GPU copy (then the CPU readback) as before ANIM-R4.
static var keep_viewports: bool = true


## ANIM-R5 P1: a picture the views can draw: a texture with a valid RID and a non-empty size
## (a BakedTexture also checks its viewport or its copy). A bake whose picture fails this is
## marked `failed`, and the views show the city's silhouette instead of drawing nothing.
static func usable(tex: Texture2D) -> bool:
	if tex == null or tex.get_width() <= 0 or tex.get_height() <= 0:
		return false
	if tex is BakedTexture:
		return (tex as BakedTexture).valid()
	return tex.get_rid().is_valid()


static func _holder() -> Node:
	var tree := Engine.get_main_loop() as SceneTree
	var holder := tree.root.get_node_or_null(HOLDER_NAME)
	if holder == null:
		holder = Node.new()
		holder.name = HOLDER_NAME
		tree.root.add_child(holder)
	return holder


## Waits (a frame at a time) for worker task `rec[field]` (a group task when `group`) and
## joins it; false when the bake was stopped meanwhile (`shutdown`).
static func _join(key: String, rec: Dictionary, field: String, group: bool) -> bool:
	var tree := Engine.get_main_loop() as SceneTree
	while rec.has(field) and not (WorkerThreadPool.is_group_task_completed(int(rec[field])) if group else WorkerThreadPool.is_task_completed(int(rec[field]))):
		await tree.process_frame
	if not rec.has(field) or not is_same(_live.get(key), rec):
		return false
	if group:
		WorkerThreadPool.wait_for_group_task_completion(int(rec[field]))
	else:
		WorkerThreadPool.wait_for_task_completion(int(rec[field]))
	rec.erase(field)
	var painter: NeonCity = rec.get("painter")
	return painter != null and is_instance_valid(painter) and not painter.cancelled


static func _bake(key: String, look: String, painter: NeonCity) -> void:
	# `holding`: this build has the slot (drop_stale gives it back if it stops the build).
	var rec := {"painter": painter, "holding": true}
	_live[key] = rec
	if threaded:
		# ANIM-R1 M2 / ANIM-R2 R1: the seconds of GDScript that build the geometry run off the
		# main thread, in slices at once; the frames go on (the old image, a stand-in or the
		# sky with the placement shows until this lands).
		painter.make_slices(NeonCity.BUILD_SLICES)
		rec["task"] = WorkerThreadPool.add_task(painter.prebuild_lots, true, "city bake: lots")
		if not await _join(key, rec, "task", false):
			return
		rec["group"] = WorkerThreadPool.add_group_task(painter.prebuild_slice, NeonCity.BUILD_SLICES + 1, -1, true, "city bake: slices")
		if not await _join(key, rec, "group", true):
			return
		rec["task"] = WorkerThreadPool.add_task(painter.prebuild_join, true, "city bake: join")
		if not await _join(key, rec, "task", false):
			return
		painter.free_slices()
	var vp := SubViewport.new()
	rec["vp"] = vp
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
	if not is_same(_live.get(key), rec):
		return
	if threaded:
		# ANIM-R2 R1: chunks go in while the frame's budget lasts (SUBMIT_BUDGET_USEC), then
		# the next frame goes on.
		var at := 0
		var t0 := Time.get_ticks_usec()
		while at >= 0:
			at = painter.submit_chunk(at)
			if at >= 0 and Time.get_ticks_usec() - t0 >= SUBMIT_BUDGET_USEC:
				await (Engine.get_main_loop() as SceneTree).process_frame
				if not is_same(_live.get(key), rec):
					return
				t0 = Time.get_ticks_usec()
		vp.render_target_update_mode = SubViewport.UPDATE_ONCE
	# The geometry is on the GPU now: the next bake may build.
	rec["holding"] = false
	_building = maxi(0, _building - 1)
	_pump()
	for f in READBACK_FRAMES:
		await RenderingServer.frame_post_draw
		if not is_same(_live.get(key), rec):
			return
	var e := {"look": look, "region": painter.painter_region, "scale": painter.scale.x}
	var tex: Texture2D = _keep_viewport(vp) if is_instance_valid(vp) else null
	var kept := usable(tex)
	if not kept:
		tex = _gpu_copy(vp) if is_instance_valid(vp) else null
	if not usable(tex) and is_instance_valid(vp):
		var img: Image = vp.get_texture().get_image()
		if img != null and not img.is_empty():
			tex = ImageTexture.create_from_image(img)
	if not usable(tex):
		e["failed"] = true
		kept = false
		tex = null
	else:
		e["texture"] = tex
		e.merge(painter.overlay_data())
	painter.free_chunks()
	if kept:
		# The viewport stays (its target is the picture; it goes with the texture), the
		# painter goes.
		rec.erase("vp")
		vp.remove_child(painter)
		painter.queue_free()
	elif is_instance_valid(vp):
		vp.queue_free()
	_live.erase(key)
	store(key, e)
	bakes_done += 1
	_land(key)


## The bake for `key` landed: its waiters redraw.
static func _land(key: String) -> void:
	var p: Dictionary = _pending.get(key, {})
	_pending.erase(key)
	for id in p.get("waiters", []):
		var w := instance_from_id(id) as CanvasItem
		if w != null and is_instance_valid(w):
			w.queue_redraw()
