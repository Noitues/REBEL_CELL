extends Node
## ART-9 4A capture lab (dev tool, never exported): walks the MAINFRAME, loot and event states
## in one windowed launch and saves a picture of each (1280x720 PNG) for side-by-side review
## with docs/art_reference/shop_events/. Run only through tools/run_windowed.py:
##
##   python tools/run_windowed.py --log <log> -- res://tools/design_lab/art9_4a_lab.tscn -- --out=<abs dir> [--only=a,b]
##
## States: shop_<night|rain|day>, shop_takeover_<frame>, shop_x<scale>, shop_poor, deck_remove,
## loot_card, loot_firmware, event_street, event_corp, event_dispatch, event_chosen.

const NETRUN := preload("res://scenes/netrun_map/netrun_scene.tscn")
const SETTLE := 20
const TAKEOVER_FRAMES: Array[int] = [4, 14, 25, 40, 52, 75]

var _out := ""
var _only: PackedStringArray = []


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
		elif a.begins_with("--only="):
			_only = a.trim_prefix("--only=").split(",")
	DirAccess.make_dir_recursive_absolute(_out)
	RunManager.scene_switching_enabled = false
	RunManager.save_slot = "gut_art9_4a_lab"
	await _run()
	RunManager.delete_save()
	get_tree().quit()


func _want(name: String) -> bool:
	return _only.is_empty() or _only.has(name) or _only.has(name.get_slice("_", 0))


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _snap(name: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png(_out.path_join(name + ".png"))
	print("LAB saved ", name)


func _netrun(seed: int = 7) -> Node:
	RunManager.new_campaign(seed)
	var net: Node = NETRUN.instantiate()
	add_child(net)
	await _frames(2)
	net.start_run(1)
	await _frames(2)
	return net


func _settle(net: Node) -> void:
	await _frames(SETTLE)
	PageTransition.settle(net)
	Dialogue.finish_typing()
	Typing.finish_all(get_tree())
	if net.has_method("complete_motion"):
		net.complete_motion()
	for w in net.find_children("*", "SliceStockWheel", true, false):
		(w as SliceStockWheel).land()
	await _frames(6)


func _close(net: Node) -> void:
	net.queue_free()
	await _frames(3)
	RunManager.reset()


func _shop(net: Node, cycles: int = 400) -> void:
	DemoSetup.open_shop(RunManager.netrun, cycles)
	net._show_current()
	await _settle(net)


func _run() -> void:
	if _want("shop"):
		for state in [&"night", &"rain", &"day"]:
			var net := await _netrun()
			await _shop(net)
			if state != &"night":
				var old: MainframeFacade = net._shop_facade
				var f := MainframeFacade.new(state)
				f.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
				net.add_child(f)
				net.move_child(f, old.get_index())
				old.queue_free()
				net._shop_facade = f
				net._layout_shop(net._panel)
				await _frames(4)
			await _snap("shop_%s" % state)
			if state == &"night":
				var sign: MainframeSign = net._shop_facade.sign
				for seq in 3:
					sign.sequence_index = seq
					for i in TAKEOVER_FRAMES:
						sign.show_frame(i)
						await _frames(2)
						await _snap("shop_takeover_%d_%02d" % [seq, i])
				sign.settle()
				net.open_remove()
				await _settle(net)
				await _snap("deck_remove")
			await _close(net)
		for sc in [1.6, 2.0]:
			Settings.set_text_scale(sc)
			var net := await _netrun()
			await _shop(net)
			await _snap("shop_x%s" % str(sc))
			await _close(net)
		Settings.set_text_scale(1.0)
		var poor := await _netrun()
		await _shop(poor, 60)
		await _snap("shop_poor")
		await _close(poor)
	if _want("loot"):
		for kind in ["card", "firmware"]:
			var net := await _netrun()
			var opts: Array = ["twist", "jam", "cache"] if kind == "card" else ["barbed_wire", "overvolt", "skimmer"]
			DemoSetup.offer_loot(RunManager.netrun, opts, kind)
			net._show_current()
			await _settle(net)
			await _snap("loot_%s" % kind)
			await _close(net)
		Settings.set_text_scale(2.0)
		var big := await _netrun()
		DemoSetup.offer_loot(RunManager.netrun, ["twist", "jam", "cache"], "card")
		big._show_current()
		await _settle(big)
		await _snap("loot_card_x2.0")
		await _close(big)
		Settings.set_text_scale(1.0)
	if _want("event"):
		for pair in [["street", &"ev_leash_on_the_floor"], ["corp", &"ev_continuum_memo"], ["dispatch", &"ev_dispatch_early_reply"]]:
			var net := await _netrun()
			DemoSetup.open_event(RunManager.netrun, pair[1])
			net._show_current()
			await _settle(net)
			await _snap("event_%s" % pair[0])
			await _close(net)
