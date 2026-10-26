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
## The "warn" scenario leaves INFECTED this many cards short of the line before the raid.
const WARN_SHORT := 2

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
	# The default scenario is the campaign's FIRST raid (no DECAY yet, raid number 1); "decay" and "lost" are its second (raid number 2). The
	# raids fought count both won and lost, and the claims above may have played a raid, so both are set.
	c.raids_won = 0 if (_scn == "" or _scn == "warn") else 1
	c.raids_lost = 0
	# One district is DOWN (it waits for a repair at the HQ step, or DECAY takes it) and HOME took damage.
	c.grid.site(ring[0])["condition"] = GridState.Condition.DOWN
	c.grid.home_integrity -= 6
	c.grid.site(c.grid.home_site_id)["integrity"] = c.grid.home_integrity
	if _scn == "decay":
		c.grid.site(ring[1])["condition"] = GridState.Condition.DOWN
	if _scn == "lost" or _scn == "forced":
		# lost: DECAY takes the DOWN district (+1 INFECTED), then INFECTED equals healthy: one more card ends the city.
		# forced: INFECTED equals healthy before DECAY, so DECAY alone puts it over the line (THE CITY FALLS).
		var st := SolaceTideCampaign.load_state(c, corp, cfg)
		var healthy := st.deck.size() - st.wound_count()
		var ids: Array = []
		for i in healthy - st.wound_count() - (1 if _scn == "lost" else 0):
			ids.append(ring[1 + i % 3])
		SolaceTideRules.add_infected(c.corp_theme.solace.tide, ids, false)
	if _scn == "warn":
		# The first raid, with INFECTED a few cards short of the line: the HQ step warns about the next DECAY (the DOWN districts left fall to it).
		var st2 := SolaceTideCampaign.load_state(c, corp, cfg)
		var healthy2 := st2.deck.size() - st2.wound_count()
		var ids2: Array = []
		for i in healthy2 - st2.wound_count() - WARN_SHORT:
			ids2.append(ring[1 + i % 3])
		SolaceTideRules.add_infected(c.corp_theme.solace.tide, ids2, false)
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
	var p := "r1" if (_scn == "" or _scn == "warn") else ("r2_" + _scn)
	if _scn == "warn":
		p = "r1_warn"
	print("CAPTURE scenario=%s raid=%d decay=%s infected=%d healthy=%d" % [_scn, flow.raid_number(), flow.decay_tally, flow.hud()["infected"], flow.hud()["healthy"]])
	await _shot(p + "_decay")
	if flow.forced():
		# THE CITY FALLS: no PLAN, no RESPONSE; the raid plays straight through to CITY LOST.
		screen.city_falls()
		await _playout_shots(p, screen)
	else:
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
			# A card that stops nothing: flagged as a ghost while it is picked, red once it stands on the Site.
			var flagged := false
			for h in flow.hand_cards():
				if flagged or not SolaceTideRules.PLACEABLE.has(h["verb"]):
					continue
				for s in flow.placeable_sites():
					var chk := SolaceTideTally.sentry_check(flow.raid.ctx, flow.raid.st, flow.raid.place, s, h["id"])
					if bool(chk["useless"]) and String(chk["why"]) == "type":
						screen.card_pressed(h["id"])
						await _settle()
						await _shot(p + "_plan_ghost_flags")
						screen.site_clicked(s)
						await _settle()
						await _shot(p + "_plan_mismatch")
						flagged = true
						break
			print("CAPTURE mismatch_flagged=%s" % flagged)
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
		# Point at the worst tier of the odds: the map draws the Sites that go DOWN and HOME's damage.
		var odds := flow.plan_odds()
		if not odds.is_empty():
			screen._set_fc_hover({"a": -1, "tier": String(odds[0]["tier"]), "inf": -1})
			await _settle()
			print("CAPTURE forecast_hover tier=%s marks=%s" % [odds[0]["tier"], screen.layer.fc_marks])
			await _shot(p + "_forecast_hover")
			screen._set_fc_hover({})
			await _settle()
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
			# The lost scenario picks a row that can end the run (the decision point the stills must show); the others pick the first row.
			var pick := 0
			if _scn == "lost":
				for gi in flow.groups.size():
					if bool(flow.groups[gi]["lethal_any"]):
						pick = gi
						break
			screen.select_group(pick)
			await _settle()
			await _shot(p + "_response_picked")
			screen.commit()
			if flow.phase == TideRaidFlow.Phase.RESPONSE:
				await _settle()
				await _shot(p + ("_lethal_confirm" if flow.lethal_armed else "_hold_confirm"))
				screen.commit()
		await _playout_shots(p, screen)
	await _settle()
	if screen.city_lost_showing():
		await _shot(p + "_city_lost")
		screen._dismiss_city_lost()
		await _settle()
	await _shot(p + "_aftermath")
	print("CAPTURE aftermath tier=%s banner=%s phase=%d tally=%s" % [flow.aftermath()["tier"], flow.aftermath()["banner"], flow.phase, flow.aftermath()["tally"]])
	screen.cont()
	await _settle()
	if flow.phase == TideRaidFlow.Phase.HQ_STEP:
		await _shot(p + "_hq_step")
		# Pick the first action the Cell can take (a repair, else a patch, a clean or a cool): the picked row and the total show.
		var acts := flow.hq_actions([&"", "", false])
		var picked := false
		for kind in ["repair", "patch", "clean", "cool"]:
			for a in acts:
				if a["kind"] == kind and bool(a["enabled"]) and not picked:
					screen._hq_pick(a)
					picked = true
		print("CAPTURE hq_pick picked=%s total=%d" % [picked, flow.hq_total([screen._hq_repair, screen._hq_build, screen._hq_patch])])
		await _settle()
		await _shot(p + "_hq_step_picked")
	hq.queue_free()


## One still per beat stage: the pulse travelling (stage 0), the impact landing (1), the beat settled (2); the hunter's two lit streets. A merged quiet
## sweep is one step (its stills carry the last beam's index and "sweep").
func _playout_shots(p: String, screen: TideRaidScreen) -> void:
	var flow := screen.flow
	var last_key := ""
	var n_steps := 0
	for i in PLAYOUT_WAIT_FRAMES:
		if flow.phase != TideRaidFlow.Phase.PLAYOUT:
			break
		var key := _beat_key(screen)
		if key != last_key:
			last_key = key
			var wait := 0.5 if screen._stage == 0 else (0.2 if screen._stage == 1 else 0.05)
			await get_tree().create_timer(wait).timeout
			if flow.phase != TideRaidFlow.Phase.PLAYOUT or _beat_key(screen) != key:
				continue
			var tag := "lit" if screen._hunter_stage == 1 else "stage%d" % screen._stage
			if screen._quiet_step:
				tag = "sweep_" + tag
			if screen._stage == 0:
				n_steps += 1
			await _shot("%s_playout_beam%d_%s" % [p, screen._beam_n, tag])
		await get_tree().process_frame
	print("CAPTURE playout steps=%d beats=%d" % [n_steps, flow.beats().size()])


## The beat the playout is at, as a key: beam, the hunter's reveal stage, the beat stage.
func _beat_key(screen: TideRaidScreen) -> String:
	return "%d_%d_%d" % [screen._beam_n, screen._hunter_stage, screen._stage]


func _settle(n: int = SETTLE_FRAMES) -> void:
	for i in n:
		await get_tree().process_frame


func _shot(name_: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png(_out.path_join(name_ + ".png"))
	print("CAPTURE shot %s" % name_)
