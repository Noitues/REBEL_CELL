extends Node
## Phase 3 / 3b: windowed stills of the Solace Infected Tide raid screen, one per beat (DECAY, DRAW, PLAN, FORECAST, SEALED A, RESPONSE, the
## playout beams, AFTERMATH, HQ step). A seeded Solace campaign opens its raid in the real HQ scene. Prints CAPTURE lines. Run:
##   python tools/run_windowed.py --log <f> -- --resolution 1280x720 res://tools/raid_tide/tide_ui_capture.tscn -- --out=<abs dir> [--seed=7] [--scenario=decay|lost]
## Scenarios: default = the campaign's first raid (HOME damaged, a district DOWN, Heat 80, so the HQ step offers every action);
## decay = the second raid with two districts DOWN (DECAY takes them: the INFECTED tally); lost = the second raid with INFECTED one card short of
## the line (the PLAN warning "1 more = CITY LOST", then an unguarded raid that ends the city).

const HQ := preload("res://scenes/hq/hq_scene.tscn")
const SIZE := Vector2i(1280, 720)
const MODEL_WAIT_FRAMES := 2400
const SETTLE_FRAMES := 30
const PLAYOUT_WAIT_FRAMES := 1500
const START_HEAT := 80
const SEED := 7

var _out := ""
var _seed := SEED
var _scn := ""


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
		elif a.begins_with("--scenario="):
			_scn = a.trim_prefix("--scenario=")
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
	# The default scenario is the campaign's FIRST raid (no DECAY yet); "decay" and "lost" are its second.
	c.raids_won = 0 if _scn == "" else 1
	# One district is DOWN (it waits for a repair at the HQ step, or DECAY takes it) and HOME took damage.
	c.grid.site(ring[0])["condition"] = GridState.Condition.DOWN
	c.grid.home_integrity -= 6
	c.grid.site(c.grid.home_site_id)["integrity"] = c.grid.home_integrity
	if _scn == "decay":
		c.grid.site(ring[1])["condition"] = GridState.Condition.DOWN
	if _scn == "lost":
		# DECAY takes the DOWN district (+1 INFECTED), then INFECTED equals healthy: one more card ends the city.
		var st := SolaceTideCampaign.load_state(c, corp, cfg)
		var healthy := st.deck.size() - st.wound_count()
		var ids: Array = []
		for i in healthy - st.wound_count() - 1:
			ids.append(ring[1 + i % 3])
		SolaceTideRules.add_infected(c.corp_theme.solace.tide, ids, false)
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
	var p := "r1" if _scn == "" else ("r2_" + _scn)
	print("CAPTURE scenario=%s raid=%d decay=%s infected=%d healthy=%d" % [_scn, flow.raid_number(), flow.decay_tally, flow.hud()["infected"], flow.hud()["healthy"]])
	await _shot(p + "_decay")
	screen.cont()
	await _settle()
	if flow.phase == TideRaidFlow.Phase.DRAW:
		await _shot(p + "_draw")
		screen.cont()
		await _settle()
	if flow.phase == TideRaidFlow.Phase.PLAN:
		await _shot(p + "_plan_empty")
		if _scn != "lost":
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
			# Point at the first sealed route: the other routes dim.
			screen._set_hover("cand0")
			await _settle()
			await _shot(p + "_plan_focus")
			screen._set_hover("")
			await _settle()
			await _shot(p + "_plan_placed")
		screen.to_forecast()
		await _settle()
		await _shot(p + "_forecast")
		screen.launch()
		if flow.phase == TideRaidFlow.Phase.FORECAST:
			await _shot(p + "_launch_confirm")
			screen.launch()
		await _settle()
		await _shot(p + "_reveal_a")
		for i in PLAYOUT_WAIT_FRAMES:
			if flow.phase != TideRaidFlow.Phase.REVEAL:
				break
			await get_tree().process_frame
		if flow.phase == TideRaidFlow.Phase.RESPONSE:
			await _settle()
			await _shot(p + "_response")
			screen.select_group(0)
			await _settle()
			await _shot(p + "_response_picked")
			screen.commit()
			if flow.phase == TideRaidFlow.Phase.RESPONSE:
				await _shot(p + "_hold_confirm")
				screen.commit()
		var last := -2
		var last_stage := 0
		for i in PLAYOUT_WAIT_FRAMES:
			if flow.phase != TideRaidFlow.Phase.PLAYOUT:
				break
			if screen._beam_n != last or screen._hunter_stage != last_stage:
				last = screen._beam_n
				last_stage = screen._hunter_stage
				await _settle(12)
				await _shot("%s_playout_beam%d_stage%d" % [p, last, last_stage])
			await get_tree().process_frame
	await _settle()
	await _shot(p + "_aftermath")
	print("CAPTURE aftermath tier=%s phase=%d tally=%s" % [flow.aftermath()["tier"], flow.phase, flow.aftermath()["tally"]])
	screen.cont()
	await _settle()
	if flow.phase == TideRaidFlow.Phase.HQ_STEP:
		await _shot(p + "_hq_step")
		# Pick a repair and a build: the picked rows, the total and the greyed rows with their reasons.
		var acts := flow.hq_actions([&"", "", false])
		for a in acts:
			if a["kind"] == "repair" and bool(a["enabled"]):
				screen._hq_pick(a)
				break
		await _settle()
		await _shot(p + "_hq_step_picked")
	hq.queue_free()


func _settle(n: int = SETTLE_FRAMES) -> void:
	for i in n:
		await get_tree().process_frame


func _shot(name_: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png(_out.path_join(name_ + ".png"))
	print("CAPTURE shot %s" % name_)
