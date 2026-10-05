extends Node
## ART-7 3B capture walk (dev tool, never exported): ONE windowed launch that steps the netrun
## route through its states and writes a PNG per state, for reading next to the references
## (docs/art_reference/netrun/). Run only through tools/run_windowed.py:
##   res://tools/design_lab/netrun_states.tscn -- --out=<abs dir> [--states=a,b] [--size=1280x720]
## States: start, underway, show_all, heat, meridian_16, halcyon_20, orbital, jack.
## Sets the run up the way the motion lab and DemoSetup do (a dev tool may write a demo
## campaign; the screens never do). Saves to its own slot; restores the text size.

const NETRUN := preload("res://scenes/netrun_map/netrun_scene.tscn")
const HQ := preload("res://scenes/hq/hq_scene.tscn")
const SLOT := "gut_netrun_states"
const SETTLE := 20
const BAKE_FRAMES := 600
const ALL_STATES := ["start", "underway", "show_all", "heat", "meridian_16", "halcyon_20", "orbital", "jack"]
## Seconds into the jack-in at which frames are written.
const JACK_TIMES: Array[float] = [0.6, 1.4, 2.2, 3.0, 3.6, 4.2, 4.8, 5.6, 6.6, 8.0]

var _out := ""
var _scene: Node = null


func _ready() -> void:
	var states: Array = ALL_STATES.duplicate()
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
		elif a.begins_with("--states="):
			states = a.trim_prefix("--states=").split(",", false)
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	_run.call_deferred(states)


func _run(states: Array) -> void:
	var scale0 := Settings.text_scale
	for st in states:
		print("netrun_states: ", st)
		await _state(String(st))
	Settings.text_scale = scale0
	Settings.changed.emit()
	RunManager.delete_save()
	print("netrun_states: done")
	get_tree().quit()


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _open_netrun(corp: StringName, scale: float, heat: int = 0) -> Node:
	if _scene != null and is_instance_valid(_scene):
		_scene.queue_free()
		await _frames(2)
	Settings.text_scale = scale
	Settings.changed.emit()
	RunManager.reset()
	_unlock_all_corps()
	RunManager.new_campaign(1, corp)
	RunManager.campaign.heat = heat
	_scene = NETRUN.instantiate()
	add_child(_scene)
	_scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(2)
	_scene.start_run(1)
	return _scene


## As the review pack: every corporation playable in this run's own profile.
func _unlock_all_corps() -> void:
	var p := RunManager.profile
	for u in [&"unlock_meridian", &"unlock_halcyon", &"unlock_orbital"]:
		if not p.unlocks.has(u):
			p.unlocks.append(u)
	for id in ["solace", "meridian", "halcyon", "orbital"]:
		p.best_ice_by_corp[id] = 10


func _settle(net: Node) -> void:
	for f in BAKE_FRAMES:
		var city: NeonCity = net.background.city
		if net.arrival_ready() and city.showing_current_look() and city.camera_settled() and city.bake_fade >= 1.0:
			break
		await get_tree().process_frame
	await _frames(SETTLE)


func _underway(net: Node) -> void:
	var s := RunManager.netrun
	var first: StringName = s.available_nodes()[0]
	s.run.current_node_id = first
	s.run.visited.append(first)
	net._show_map()


func _shot(name_: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png(_out.path_join(name_ + ".png"))


func _state(st: String) -> void:
	match st:
		"start":
			var net := await _open_netrun(&"solace", 1.0)
			await _settle(net)
			await _shot(st)
		"underway", "show_all":
			var net := await _open_netrun(&"solace", 1.0)
			await _settle(net)
			_underway(net)
			# A second step: the walked path shows as a lime line.
			var s := RunManager.netrun
			var nxt: StringName = s.run.current_node()["next"][0]
			s.run.current_node_id = nxt
			s.run.visited.append(nxt)
			net._show_map()
			await _settle(net)
			if st == "show_all":
				(net.city_overlay as RouteOverlay).show_all = true
				await _frames(SETTLE)
			await _shot(st)
		"heat":
			var net := await _open_netrun(&"meridian", 1.0, 60)
			await _settle(net)
			_underway(net)
			await _settle(net)
			await _shot(st)
		"meridian_16":
			var net := await _open_netrun(&"meridian", 1.6)
			await _settle(net)
			_underway(net)
			await _settle(net)
			await _shot(st)
		"halcyon_20":
			var net := await _open_netrun(&"halcyon", 2.0)
			await _settle(net)
			await _shot(st)
		"orbital":
			var net := await _open_netrun(&"orbital", 1.0)
			await _settle(net)
			await _shot(st)
		"jack":
			await _jack()


## The jack-in from the HQ's City Grid onto the route, frames at JACK_TIMES.
func _jack() -> void:
	if _scene != null and is_instance_valid(_scene):
		_scene.queue_free()
		await _frames(2)
	Settings.text_scale = 1.0
	Settings.changed.emit()
	RunManager.reset()
	RunManager.scene_switching_enabled = true
	# The HQ as the current scene beside this walker (a scene change frees only the HQ).
	var hq := HQ.instantiate()
	get_tree().root.add_child(hq)
	get_tree().current_scene = hq
	await _frames(4)
	hq.new_campaign(1)
	await _frames(4)
	hq.show_grid()
	for f in BAKE_FRAMES:
		var city: NeonCity = hq.wireframe.city if not hq.background.visible else hq.background.city
		if city.showing_current_look() and city.camera_settled() and city.bake_fade >= 1.0:
			break
		await get_tree().process_frame
	await _frames(SETTLE)
	var site: StringName = RunManager.launchable_sites()[0].id
	hq.select_site(site)
	await _frames(SETTLE)
	var op := RunManager.campaign.living_operatives()[0]
	var t0 := Time.get_ticks_msec()
	hq.launch(site, op.id)
	for t in JACK_TIMES:
		while (Time.get_ticks_msec() - t0) / 1000.0 < t:
			await get_tree().process_frame
		await _shot("jack_%04d" % roundi(t * 1000.0))
