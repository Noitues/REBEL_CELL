extends Node
## Phase 3: windowed stills of the Solace Infected Tide raid screen, one per beat (DECAY, DRAW, PLAN, FORECAST, SEALED A, RESPONSE, the
## playout beams, AFTERMATH, HQ step). A seeded Solace campaign with a DOWN district (so DECAY has something to say), INFECTED cards and
## Heat 80 (extra cards and beams) opens its raid in the real HQ scene. Prints CAPTURE lines. Run:
##   python tools/run_windowed.py --log <f> -- --resolution 1280x720 res://tools/raid_tide/tide_ui_capture.tscn -- --out=<abs dir> [--seed=7]

const HQ := preload("res://scenes/hq/hq_scene.tscn")
const SIZE := Vector2i(1280, 720)
const MODEL_WAIT_FRAMES := 2400
const SETTLE_FRAMES := 30
const PLAYOUT_WAIT_FRAMES := 1500
const START_HEAT := 80
const SEED := 7

var _out := ""
var _seed := SEED


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
		elif a.begins_with("--seed="):
			_seed = int(a.trim_prefix("--seed="))
	DirAccess.make_dir_recursive_absolute(_out)
	Settings.path = "user://tide_ui_capture_settings.json"
	SaveService.save_dir = "user://saves/tide_ui_capture"
	RunManager.save_slot = "gut_tide_ui_capture"
	RunManager.scene_switching_enabled = false
	DisplayServer.window_set_size(SIZE)
	await get_tree().process_frame
	await _run()
	print("CAPTURE DONE")
	RunManager.delete_save()
	get_tree().quit(0)


func _setup() -> void:
	RunManager.new_campaign(_seed)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	c.schematics = 300
	var ring: Array[StringName] = []
	for l in corp.city_grid.get_site(corp.city_grid.home_site_id).links:
		ring.append(l)
	ring.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	for id in ring.slice(0, 4):
		var run := RunState.new()
		run.site_id = id
		CampaignRules.on_run_completed(c, corp, cfg, run)
		CampaignRules.claim(c, corp, cfg, RunManager.lookup(), id, &"relay")
	c.pending_raids.clear()
	c.heat = START_HEAT
	c.raids_won = 1
	# One district went DOWN since the last raid, one is already INFECTED.
	var down: StringName = ring[0]
	c.grid.site(down)["condition"] = GridState.Condition.DOWN
	c.pending_raids.append({"raid_id": "raid_claim", "source": RC.RaidTriggerSource.TERRITORY_CLAIM, "site_id": "", "corporation": "solace", "model": "tide"})


func _run() -> void:
	var hq: Control = HQ.instantiate()
	get_tree().root.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await get_tree().process_frame
	hq.new_campaign(_seed)
	_setup()
	hq.show_raid()
	var city: NeonCity = hq.wireframe.city
	for i in MODEL_WAIT_FRAMES:
		var view: CityView3D = city.view3d
		if view != null and view.model != null and view._pending.is_empty() and view.chunks_built() > 0:
			break
		await get_tree().process_frame
	await _settle(SETTLE_FRAMES * 2)
	var screen: TideRaidScreen = hq.tide_screen
	if screen == null:
		print("CAPTURE FAIL no tide screen")
		return
	var flow := screen.flow
	var hb := hq._panel_host.get_parent() as Control
	print("CAPTURE geometry host=%s %s screen=%s %s hq=%s" % [hb.get_global_rect(), hb.get_class(), screen.get_global_rect(), screen.size, hq.get_global_rect()])
	await _shot("r1_decay")
	screen.cont()
	await _settle()
	await _shot("r1_draw")
	screen.cont()
	await _settle()
	await _shot("r1_plan_empty")
	# Place two cards on the first free Sites and the ghost.
	var placed := 0
	for h in flow.hand_cards():
		if placed >= flow.cfg.solace_tide_max_placed:
			break
		var sites := flow.placeable_sites()
		if sites.is_empty() or not SolaceTideRules.PLACEABLE.has(h["verb"]):
			continue
		screen.card_pressed(h["id"])
		screen.site_clicked(sites[0])
		placed += 1
	if flow.raid.st.ghost > 0:
		screen.ghost()
	await _settle()
	await _shot("r1_plan_placed")
	screen.to_forecast()
	await _settle()
	await _shot("r1_forecast")
	screen.launch()
	if flow.phase == TideRaidFlow.Phase.FORECAST:
		await _shot("r1_launch_confirm")
		screen.launch()
	await _settle()
	await _shot("r1_reveal_a")
	for i in PLAYOUT_WAIT_FRAMES:
		if flow.phase != TideRaidFlow.Phase.REVEAL:
			break
		await get_tree().process_frame
	if flow.phase == TideRaidFlow.Phase.RESPONSE:
		await _settle()
		await _shot("r1_response")
		screen.select_group(0)
		await _settle()
		await _shot("r1_response_picked")
		screen.commit()
		if flow.phase == TideRaidFlow.Phase.RESPONSE:
			await _shot("r1_hold_confirm")
			screen.commit()
	var last := -2
	for i in PLAYOUT_WAIT_FRAMES:
		if flow.phase != TideRaidFlow.Phase.PLAYOUT:
			break
		if screen._beam_n != last:
			last = screen._beam_n
			await _settle(12)
			await _shot("r1_playout_beam%d" % last)
		await get_tree().process_frame
	await _settle()
	await _shot("r1_aftermath")
	print("CAPTURE aftermath tier=%s phase=%d" % [flow.aftermath()["tier"], flow.phase])
	screen.cont()
	await _settle()
	if flow.phase == TideRaidFlow.Phase.HQ_STEP:
		await _shot("r1_hq_step")
	hq.queue_free()


func _settle(n: int = SETTLE_FRAMES) -> void:
	for i in n:
		await get_tree().process_frame


func _shot(name_: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png(_out.path_join(name_ + ".png"))
	print("CAPTURE shot %s" % name_)
