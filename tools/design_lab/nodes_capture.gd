extends Node
## Nodes round 2 capture (dev tool, windowed only through tools/run_windowed.py; never headless): the route with every node kind, the REST and
## WORKSHOP pages and the CACHE loot header, frozen (`Settings.reduce_effects`). Runs on BOTH trees (then = main 63364307, now = art/look-nodes):
## it reaches the page and the scene only through names both trees have.
##
##   python tools/run_windowed.py --log <file> -- res://tools/design_lab/nodes_capture.tscn -- --out=<abs dir> [--shots=map,rest,workshop,cache]

const NETRUN := preload("res://scenes/netrun_map/netrun_scene.tscn")
const SLOT := "nodes_capture"
## Seconds a settled picture waits for the city bake (real time), and the frames after it.
const BAKE_WAIT_S := 14.0
const SETTLE_FRAMES := 30
## The wheel slots and offer picked on the pages, and the HP the REST page shows (a share of max).
const REST_PICKS: Array[int] = [0, 2]
const WORKSHOP_PICKS: Array[int] = [1, 2]
const HP_SHARE := 0.68
const CYCLES := 160

var out := ""
var shots: PackedStringArray = ["map", "rest", "workshop", "cache"]
var net: Node = null


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.substr(6)
		elif a.begins_with("--shots="):
			shots = a.substr(8).split(",")
	DirAccess.make_dir_recursive_absolute(out)
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	Settings.reduce_effects = true
	Settings.tutorial_done = true
	for s in shots:
		await _one(s)
	RunManager.delete_save()
	get_tree().quit()


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout


func _shot(shot_name: String) -> void:
	await _frames(SETTLE_FRAMES)
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [out, shot_name])


func _fresh() -> void:
	if net != null and is_instance_valid(net):
		net.queue_free()
		await _frames(4)
	RunManager.reset()
	RunManager.new_campaign(7)
	net = NETRUN.instantiate()
	get_tree().root.add_child(net)
	await _frames(2)
	net.start_run(1)
	await _until(func() -> bool: return net.arrival_ready(), 900)
	await _wait(BAKE_WAIT_S)


func _until(cond: Callable, limit: int) -> void:
	for i in limit:
		if cond.call():
			return
		await get_tree().process_frame


## Every kind on the route: the nodes in map order get the kinds in turn (the first choices are REST, WORKSHOP, CACHE), a few elites.
func _all_kinds() -> void:
	var cycle: Array = [RC.InfilNodeType.REST, RC.InfilNodeType.WORKSHOP, RC.InfilNodeType.CACHE, RC.InfilNodeType.MAINFRAME,
			RC.InfilNodeType.TERMINAL, RC.InfilNodeType.ROUTER, RC.InfilNodeType.SERVER_RACK, RC.InfilNodeType.ROUTER]
	var i := 0
	for n in RunManager.netrun.run.map.all_nodes():
		n["type"] = cycle[i % cycle.size()]
		n["elite"] = i % cycle.size() == cycle.size() - 1
		i += 1


func _page() -> Node:
	for n in net.find_children("*", "VBoxContainer", true, false):
		if n.get_class() != "" and n.has_method("setup") and n.has_signal("patch_pressed") and not n.is_queued_for_deletion():
			return n
	return null


func _enter(node_type: int) -> void:
	await _fresh()
	var s: NetrunSession = RunManager.netrun
	var first: StringName = s.available_nodes()[0]
	s.run.map.get_node(first)["type"] = node_type
	s.run.operative.hp = maxi(1, roundi(s.run.operative.max_hp * HP_SHARE))
	s.run.cycles = CYCLES
	net.enter_node(first)
	await _wait(2.0)


func _one(shot_name: String) -> void:
	match shot_name:
		"map":
			await _fresh()
			_all_kinds()
			net._show_current()
			await _until(func() -> bool: return net.arrival_ready(), 900)
			await _wait(BAKE_WAIT_S)
			await _shot("map")
		"rest":
			await _enter(RC.InfilNodeType.REST)
			var p := _page()
			if p != null:
				for i in REST_PICKS:
					p._pick_slot(i)
					await _frames(2)
			await _wait(1.0)
			await _shot("rest")
		"workshop":
			await _enter(RC.InfilNodeType.WORKSHOP)
			var p := _page()
			if p != null:
				p._pick_offer(WORKSHOP_PICKS[0])
				await _frames(2)
				p._pick_target(WORKSHOP_PICKS[1])
			await _wait(1.0)
			await _shot("workshop")
		"cache":
			await _enter(RC.InfilNodeType.CACHE)
			await _wait(2.0)
			await _shot("cache")
