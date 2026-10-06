extends GutTest
## FIX-BAKE (M14): a city bake whose painter or viewport is freed under it (the holder goes
## with the tree at quit, a page change) must stop cleanly: after its next await the
## coroutine used to call `submit_chunk` / read `painter_region` on the freed painter
## ("previously freed instance"). `CityBakeCache._abandoned` is the check after every await:
## the record is dropped, the build slot given back, and no queued work is left.

const SCREEN := Rect2(0, 0, 1280, 720)
## Bound on a threaded test bake (game seconds, frame floor).
const BAKE_WAIT_LIMIT := 20.0
const BAKE_WAIT_FRAMES := 600
## Frames pumped after the free, for any queued work to run.
const PUMP_FRAMES := 5


func before_each() -> void:
	AudioDirector.muted = true
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.simulate = false
	CityBakeCache.shutdown()
	AudioDirector.muted = false


## A NeonCity with a bake of `key` started and run to its readback wait (viewport made).
func _start_bake(holder: Control, key: String) -> Dictionary:
	var city := NeonCity.new()
	city.net_mode = true
	holder.add_child(city)
	CityBakeCache.request(key, city.look_key(), city.make_painter(Rect2(0, 0, 256, 192), 1.0), city)
	var rec: Dictionary = CityBakeCache._live.get(key, {})
	assert_false(rec.is_empty(), "the bake runs")
	await BoundedWait.until(get_tree(), func() -> bool: return rec.has("vp") and CityBakeCache._building == 0, BAKE_WAIT_LIMIT, BAKE_WAIT_FRAMES)
	assert_true(rec.has("vp"), "the bake got as far as its viewport")
	return rec


func test_a_bake_whose_viewport_is_freed_mid_bake_stops_cleanly() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var rec := await _start_bake(holder, "freed_vp")
	var vp: Node = rec["vp"]
	var ref: WeakRef = weakref(rec["painter"])
	# The holder's viewport goes (with the painter inside it), the record stays in _live.
	vp.free()
	assert_null(ref.get_ref(), "the painter went with its viewport")
	assert_true(CityBakeCache._abandoned("freed_vp", rec), "the next await ends the bake")
	for i in PUMP_FRAMES:
		await get_tree().process_frame
	assert_eq(CityBakeCache.busy(), 0, "no work left behind")
	assert_eq(CityBakeCache._building, 0, "the build slot is free")
	assert_false(CityBakeCache._pending.has("freed_vp"), "nobody waits on it")
	assert_false(CityBakeCache.has("freed_vp"), "a stopped bake never lands")


func test_a_bake_whose_painter_is_freed_alone_stops_cleanly() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var rec := await _start_bake(holder, "freed_painter")
	(rec["painter"] as NeonCity).free()
	assert_true(CityBakeCache._abandoned("freed_painter", rec))
	for i in PUMP_FRAMES:
		await get_tree().process_frame
	assert_eq(CityBakeCache.busy(), 0, "no work left behind")
	assert_eq(CityBakeCache._building, 0, "the build slot is free")


func test_a_live_bake_is_not_abandoned() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var rec := await _start_bake(holder, "alive")
	assert_false(CityBakeCache._abandoned("alive", rec), "a healthy bake goes on")
	assert_eq(CityBakeCache.busy(), 1)
	CityBakeCache.shutdown()
	assert_true(CityBakeCache._abandoned("alive", rec), "a shut down bake is abandoned")
	assert_eq(CityBakeCache.busy(), 0)


func test_the_city_freed_mid_bake_leaves_nothing_running() -> void:
	var holder := Control.new()
	holder.size = SCREEN.size
	add_child(holder)
	var city := NeonCity.new()
	city.net_mode = true
	holder.add_child(city)
	CityBakeCache.request("city_gone", city.look_key(), city.make_painter(Rect2(-600, -400, 1200, 800), 1.0), city)
	assert_eq(CityBakeCache.busy(), 1)
	holder.free()
	for i in PUMP_FRAMES:
		await get_tree().process_frame
	# Nobody waits for it now: the next request drops it as stale.
	CityBakeCache.drop_stale()
	assert_eq(CityBakeCache.busy(), 0, "a bake nobody waits for is gone")
	assert_eq(CityBakeCache._building, 0)
