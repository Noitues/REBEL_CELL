extends Node
## W10 review-pack harness (ART_BIBLE §13 "Automated visual checks", §11 screen list).
## Dev tool, never exported (tools/* is excluded) and never in game code. Drives every
## reachable screen from a clean state through the scenes' public methods and the run and
## campaign state (the same way tools/playtest/storyboard.gd and the integration tests do),
## captures a 1280x720 PNG of each and exports the visible text Controls for the runtime
## lint (`<screen>.lint.json`). Needs a renderer: run it only through
## `tools/visual_qa/capture_pack.py` (which goes through tools/run_windowed.py and gives the
## run its own user:// folder), never headless.
##
##   res://tools/visual_qa/review_pack.tscn -- --out=<abs dir> [--screens=a,b] [--scale=1.6]
##       [--pad] [--reduce-effects] [--filter=none|grey|deutan] [--scramble]
##       [--screen-timeout=90] [--list=<file.json>]
##
## Per screen it writes <screen>.png, <screen>.lint.json and <screen>.status.json
## ({status: ok|failed|timeout, error, errors[], warnings[], seconds}); `_current.txt` names
## the screen in progress, so the driver can tell which one a crash took down.
## `--scale` writes Settings.text_scale directly, past the 1.6 clamp of set_text_scale (as
## the storyboard does): W9 raises the range. Nothing is saved to the player's files.

const TITLE := preload("res://scenes/menu/title_scene.tscn")
const HQ := preload("res://scenes/hq/hq_scene.tscn")
const NETRUN := preload("res://scenes/netrun_map/netrun_scene.tscn")
const FILTER_SHADER := preload("res://tools/visual_qa/cvd_filter.gdshader")
const ErrorLog := preload("res://tools/visual_qa/review_pack_log.gd")

const SLOT := "gut_review_pack"
const SAVE_DIR := "user://saves/review_pack"
const SETTINGS_FILE := "user://review_pack_settings.json"
const CAPTURE_SIZE := Vector2i(1280, 720)
## Frames a screen gets to settle before its picture.
const SETTLE_FRAMES := 12
## Most frames the harness waits for a map camera, a fight to open or a motion to end.
const WAIT_FRAMES := 900
## Frames a screen may keep running after a script error before it counts as failed.
const ERROR_GRACE_FRAMES := 120
const DEFAULT_TIMEOUT_S := 90.0
## Filter modes of cvd_filter.gdshader.
const FILTER_MODES := {"none": 0, "grey": 1, "deutan": 2}
## Layer of the post filter: above everything the game draws.
const FILTER_LAYER := 128
## Text Control classes the lint walks.
const TEXT_CLASSES: Array[String] = ["Label", "Button", "RichTextLabel", "LineEdit", "TextEdit"]
## Longest text kept per Control in the lint export.
const LINT_TEXT_MAX := 120
## Seeds tried for a Modem that stocks Firmware (the socket picker needs one).
const SOCKET_SEEDS := 12
## Boss HP shares for the phase screens (content phases are at 66% and 33%).
const BOSS_P2_SHARE := 0.6
const BOSS_P3_SHARE := 0.25
## Frames into a SEND IT replay / raid playout for the "mid" pictures.
const MID_REPLAY_FRAMES := 24
const MID_PLAYOUT_STEP := 2

## Screen name -> [method, what the picture shows]. Order is the capture order.
const SCREENS := [
	["title", "_s_title", "Title / main menu with a campaign to continue."],
	["slots", "_s_slots", "Campaign slots with one saved campaign."],
	["new_campaign", "_s_new_campaign", "New campaign page (all corporations unlocked)."],
	["new_campaign_picker", "_s_new_campaign_picker", "New campaign with the target picker open."],
	["hq", "_s_hq", "HQ after starting a new campaign."],
	["hq_black_market", "_s_hq_black_market", "HQ scrolled to the Black Market."],
	["hq_crew", "_s_hq_crew", "HQ crew / dossiers with four classes."],
	["hq_loadout_deck", "_s_hq_loadout_deck", "Loadout modal, DECK tab."],
	["hq_loadout_spinner", "_s_hq_loadout_spinner", "Loadout modal, SPINNER tab, rank-3 operative."],
	["hq_pause", "_s_hq_pause", "Pause menu over the HQ."],
	["grid", "_s_grid", "City Grid, nothing selected."],
	["grid_site_selected", "_s_grid_site_selected", "City Grid with an Exploit site selected."],
	["grid_raid_pending", "_s_grid_raid_pending", "City Grid with a raid pending (RAID SETUP)."],
	["grid_meridian", "_s_grid_meridian", "City Grid against Meridian."],
	["grid_halcyon", "_s_grid_halcyon", "City Grid against Halcyon."],
	["grid_orbital", "_s_grid_orbital", "City Grid against Orbital."],
	["grid_rebel_cell", "_s_grid_rebel_cell", "City Grid against REBEL_CELL."],
	["raid_setup", "_s_raid_setup", "Raid setup with one asset deployed."],
	["raid_playout", "_s_raid_playout", "Raid playout, mid-way."],
	["raid_result", "_s_raid_result", "Raid playout at its end (RESULT)."],
	["raid_report", "_s_raid_report", "Raid report page after the playout."],
	["raid_interlude", "_s_raid_interlude", "Raid interlude inside a netrun."],
	["route", "_s_route", "Netrun route: choosing where to go."],
	["combat_start", "_s_combat_start", "A fight starts."],
	["combat_hover", "_s_combat_hover", "The pointer over the first card."],
	["combat_aiming", "_s_combat_aiming", "A card selected, waiting to be aimed."],
	["combat_resolving", "_s_combat_resolving", "SEND IT pressed, the turn mid-replay."],
	["combat_after", "_s_combat_after", "The turn after it has played out."],
	["combat_refused", "_s_combat_refused", "A respin refused for lack of RAM."],
	["combat_boss_p2", "_s_combat_boss_p2", "Boss fight in phase 2."],
	["combat_boss_p3", "_s_combat_boss_p3", "Boss fight in phase 3."],
	["combat_victory", "_s_combat_victory", "The killing turn: VICTORY."],
	["combat_defeat", "_s_combat_defeat", "The losing turn: DEFEAT."],
	["loot", "_s_loot", "Picking a card reward."],
	["modem", "_s_modem", "The Modem shop."],
	["modem_socket", "_s_modem_socket", "The Modem with the socket choice open."],
	["event", "_s_event", "A story event with choices."],
	["codex", "_s_codex", "Codex from the title menu."],
	["options", "_s_options", "Options from the title menu."],
	["stats", "_s_stats", "Stats and achievements with some history."],
	["run_end", "_s_run_end", "Run end: FLATLINED."],
	["campaign_won", "_s_campaign_won", "Campaign end: WON."],
	["campaign_lost", "_s_campaign_lost", "Campaign end: LOST."],
]

var out_dir := ""
var text_scale := 1.0
var pad := false
var reduce_effects := false
var filter := "none"
var scramble := false
var screen_timeout := DEFAULT_TIMEOUT_S
var _keep: Array[Node] = []
var _log: RefCounted = null
var _warnings: Array[String] = []
var _done := false
var _filter_layer: CanvasLayer = null
var _custom_draw: Array = []
var _draw_cache := {}


func _ready() -> void:
	var only: PackedStringArray = []
	var list_file := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out_dir = a.trim_prefix("--out=")
		elif a.begins_with("--screens="):
			only = a.trim_prefix("--screens=").split(",", false)
		elif a.begins_with("--scale="):
			text_scale = float(a.trim_prefix("--scale="))
		elif a == "--pad":
			pad = true
		elif a == "--reduce-effects":
			reduce_effects = true
		elif a.begins_with("--filter="):
			filter = a.trim_prefix("--filter=")
		elif a == "--scramble":
			scramble = true
		elif a.begins_with("--screen-timeout="):
			screen_timeout = float(a.trim_prefix("--screen-timeout="))
		elif a.begins_with("--list="):
			list_file = a.trim_prefix("--list=")
	if list_file != "":
		_write_json(list_file, {"screens": SCREENS.map(func(s: Array) -> Dictionary: return {"screen": s[0], "what": s[2]})})
		get_tree().quit()
		return
	if out_dir == "":
		push_error("review_pack: --out=<dir> is required")
		get_tree().quit(2)
		return
	DirAccess.make_dir_recursive_absolute(out_dir)
	_log = ErrorLog.new()
	OS.add_logger(_log)
	_setup_settings()
	for n in get_tree().root.get_children():
		_keep.append(n)
	await get_tree().process_frame
	var todo: Array = []
	for s in SCREENS:
		if only.is_empty() or only.has(s[0]):
			todo.append(s)
	for s in todo:
		await _capture(s[0], s[1], s[2])
	_teardown()
	print("REVIEW PACK DONE %d screens in %s" % [todo.size(), out_dir])
	get_tree().quit()


# --- Axes ------------------------------------------------------------------------------

func _setup_settings() -> void:
	# Nothing reaches the player's files: settings, slot and saves are private (as the
	# storyboard, H24), on top of the private user:// folder the driver gives the run.
	Settings.path = SETTINGS_FILE
	SaveService.save_dir = SAVE_DIR
	Settings.tutorial_done = true
	if scramble:
		ProjectSettings.set_setting("internationalization/pseudolocalization/replace_with_accents", true)
		ProjectSettings.set_setting("internationalization/pseudolocalization/double_vowels", true)
		ProjectSettings.set_setting("internationalization/pseudolocalization/fake_bidi", true)
		ProjectSettings.set_setting("internationalization/pseudolocalization/override", true)
		TranslationServer.pseudolocalization_enabled = true
		TranslationServer.reload_pseudolocalization()
	Settings.text_scale = text_scale  # past the clamp on purpose (W9 raises it)
	Settings.reduce_effects = reduce_effects
	Settings.changed.emit()
	Settings.pad_active = pad
	Settings.hints_changed.emit()
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	if FILTER_MODES.get(filter, 0) != 0:
		_filter_layer = CanvasLayer.new()
		_filter_layer.layer = FILTER_LAYER
		var rect := ColorRect.new()
		rect.set_anchors_preset(Control.PRESET_FULL_RECT)
		rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var mat := ShaderMaterial.new()
		mat.shader = FILTER_SHADER
		mat.set_shader_parameter("mode", FILTER_MODES[filter])
		rect.material = mat
		_filter_layer.add_child(rect)
		add_child(_filter_layer)


func _teardown() -> void:
	_clear_scenes()
	RunManager.delete_save()
	for slot in ["1", SLOT]:
		RunManager.save_slot = slot
		RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT


# --- One screen ------------------------------------------------------------------------

func _capture(screen: String, method: String, what: String) -> void:
	_write_text(out_dir.path_join("_current.txt"), screen)
	await _reset()
	_warnings.clear()
	_log.call(&"begin")
	_done = false
	var started := Time.get_ticks_msec()
	Callable(self, &"_run_screen").call(method)
	var frames := 0
	var status := "ok"
	var error_since := -1
	while not _done:
		await get_tree().process_frame
		frames += 1
		if (Time.get_ticks_msec() - started) / 1000.0 > screen_timeout:
			status = "timeout"
			break
		if error_since < 0 and _log.call(&"has_script_error"):
			error_since = frames
		if error_since >= 0 and frames - error_since > ERROR_GRACE_FRAMES:
			status = "failed"
			break
	var errors: Array = _log.call(&"take")
	var png := out_dir.path_join(screen + ".png")
	if status == "ok":
		await get_tree().process_frame
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		if img == null:
			status = "failed"
			errors.append("no viewport image")
		else:
			if img.get_size() != CAPTURE_SIZE:
				_warnings.append("viewport was %s, resized to %s" % [img.get_size(), CAPTURE_SIZE])
				img.resize(CAPTURE_SIZE.x, CAPTURE_SIZE.y, Image.INTERPOLATE_LANCZOS)
			img.save_png(png)
			_write_json(out_dir.path_join(screen + ".lint.json"), _lint_export(screen, img.get_size()))
	var err_text := ""
	if status == "timeout":
		err_text = "no picture within %.0f s" % screen_timeout
	elif status == "failed":
		err_text = "script error while reaching the screen" if errors.is_empty() else str(errors[0])
	_write_json(out_dir.path_join(screen + ".status.json"), {
		"screen": screen, "what": what, "status": status, "error": err_text,
		"errors": errors, "warnings": _warnings.duplicate(),
		"seconds": (Time.get_ticks_msec() - started) / 1000.0, "frames": frames,
	})
	print("review_pack: %s %s (%d frames)" % [screen, status, frames])


func _run_screen(method: String) -> void:
	await call(method)
	_done = true


func _reset() -> void:
	_clear_scenes()
	for i in 3:
		await get_tree().process_frame
	get_tree().paused = false
	Dialogue.clear()
	Engine.time_scale = 1.0
	RunManager.save_slot = SLOT
	RunManager.delete_save()
	RunManager.reset()


func _clear_scenes() -> void:
	for n in get_tree().root.get_children():
		if not _keep.has(n):
			n.queue_free()


func _open(scene: PackedScene) -> Node:
	var n := scene.instantiate()
	get_tree().root.add_child(n)
	return n


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


## Waits until `cond` holds (at most WAIT_FRAMES); false (with a warning) if it never did.
func _until(cond: Callable, why: String, limit: int = WAIT_FRAMES) -> bool:
	for i in limit:
		if cond.call():
			return true
		await get_tree().process_frame
	_warnings.append("waited %d frames for %s" % [limit, why])
	return false


## Lets the screen settle: page entrances and deals end, subtitles finish typing.
func _settle(root: Node, frames: int = SETTLE_FRAMES) -> void:
	await _frames(frames)
	# The city's bake lands before the picture (a stand-in city is not the screen).
	await _until(func() -> bool: return CityBakeCache.busy() == 0, "the city bake")
	if is_instance_valid(root):
		PageTransition.settle(root)
	if Dialogue.has_method(&"finish_typing"):
		Dialogue.finish_typing()
	await _frames(4)


# --- Setup helpers ---------------------------------------------------------------------

func _hq_with_campaign(seed: int = 7) -> Node:
	var hq: Node = _open(HQ)
	await _frames(2)
	hq.new_campaign(seed)
	return hq


func _unlock_all_corps() -> void:
	var p := RunManager.profile
	for u in [&"unlock_meridian", &"unlock_halcyon", &"unlock_orbital"]:
		if not p.unlocks.has(u):
			p.unlocks.append(u)
	for id in ["solace", "meridian", "halcyon", "orbital"]:
		p.best_ice_by_corp[id] = 10


func _first_link() -> StringName:
	var g := RunManager.corporation.city_grid
	return g.get_site(g.home_site_id).links[0]


func _prepare_raid(deploy: bool) -> void:
	var c := RunManager.campaign
	var first := _first_link()
	c.schematics = 100
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	c.armory = [&"turret", &"ice_lock", &"decoy"]
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	if deploy:
		CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)


func _grid(hq: Node) -> void:
	hq.show_grid()
	await _until(func() -> bool: return hq.arrival_ready(), "the Grid camera")
	await _settle(hq)


func _grid_of(corp_id: StringName) -> void:
	_unlock_all_corps()
	var hq: Node = _open(HQ)
	await _frames(2)
	var corp := RunManager.lookup().get_content(corp_id) as CorporationData
	if corp == null:
		push_error("review_pack: no corporation %s" % corp_id)
		return
	hq.new_campaign(1, 0, RunManager.DEFAULT_HOME, RunManager.DEFAULT_CLASS, corp_id)
	await _grid(hq)


func _netrun(seed: int = 7) -> Node:
	RunManager.new_campaign(seed)
	var net: Node = _open(NETRUN)
	await _frames(2)
	net.start_run(1)
	return net


## A netrun with its first fight open and settled; null (with an error) when none opened.
func _fight(seed: int = 7) -> Control:
	var net: Node = await _netrun(seed)
	await _until(func() -> bool: return net.arrival_ready(), "the route camera")
	net.enter_node(RunManager.netrun.available_nodes()[0])
	await _until(func() -> bool: return net.combat_scene != null, "the fight to open")
	var combat: Control = net.combat_scene
	if combat == null:
		push_error("review_pack: the fight never opened")
		return null
	await _until(func() -> bool: return not PageTransition.running(net), "the fight page to enter")
	await _settle(net)
	return combat


## A boss fight inside a netrun (the Breach), past the launch checks (screens only).
func _boss_fight() -> Control:
	RunManager.new_campaign(5)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var boss_site: SiteData = null
	for sd in corp.city_grid.sites:
		if CampaignRules.run_kind_for(c, sd) == "boss":
			boss_site = sd
			break
	if boss_site == null:
		push_error("review_pack: no boss site")
		return null
	RunManager._ensure_resolver()
	var op_id: StringName = c.living_operatives()[0].id
	RunManager.netrun = NetrunSession.start_special(RunManager.resolver, c, op_id, "boss", boss_site.id, boss_site.tier,
		c.campaign_seed, corp.final_boss.id, CampaignRules.boss_overrides(c, corp), corp)
	RunManager.run_changed.emit(RunManager.netrun)
	var net: Node = _open(NETRUN)
	await _frames(2)
	await _until(func() -> bool: return net.arrival_ready(), "the route camera")
	net.enter_node(RunManager.netrun.available_nodes()[0])
	await _until(func() -> bool: return net.combat_scene != null, "the boss fight to open")
	var combat: Control = net.combat_scene
	if combat == null:
		push_error("review_pack: the boss fight never opened")
		return null
	await _until(func() -> bool: return not PageTransition.running(net), "the fight page to enter")
	await _settle(net)
	return combat


func _boss_phase(share: float) -> void:
	var combat := await _boss_fight()
	if combat == null:
		return
	var st: CombatState = combat.engine.state()
	st.player.hp = st.player.max_hp
	st.enemies[0].hp = int(st.enemies[0].max_hp * share)
	combat.end_turn()
	await _frames(2)
	combat.skip_motion()
	await _until(func() -> bool: return not combat.motion_busy(), "the phase turn to play out")
	await _settle(combat.get_parent())


# --- Screens ---------------------------------------------------------------------------

func _s_title() -> void:
	RunManager.new_campaign(7)
	RunManager.autosave()
	var title: Node = TITLE.instantiate()
	title.continue_slot = SLOT
	get_tree().root.add_child(title)
	await _settle(title)


func _s_slots() -> void:
	RunManager.save_slot = "1"
	RunManager.new_campaign(4)
	RunManager.campaign.heat = 33
	RunManager.autosave()
	RunManager.save_slot = SLOT
	var title: Node = TITLE.instantiate()
	title.continue_slot = "1"
	get_tree().root.add_child(title)
	await _frames(2)
	title.show_slots()
	await _settle(title)


func _new_campaign_page() -> Node:
	_unlock_all_corps()
	RunManager.campaign = null
	var hq: Node = _open(HQ)
	await _frames(2)
	if hq.panel_name != "start":
		hq.show_start()
	await _settle(hq)
	return hq


func _s_new_campaign() -> void:
	await _new_campaign_page()


func _s_new_campaign_picker() -> void:
	var hq: Node = await _new_campaign_page()
	var pick := hq.find_child("CorporationPicker", true, false) as Control
	if pick == null:
		push_error("review_pack: no CorporationPicker")
		return
	# Art pass W8b: the target is a row of dossier tiles (no popup): the drawer of seed and
	# codes open, then the picker focused on its second tile.
	if pick.has_method("show_popup"):
		pick.call("show_popup")
	else:
		if hq.has_method("set_codes_open"):
			hq.call("set_codes_open", true)
		await _frames(2)
		pick.grab_focus()
		pick.set("cursor", 1)
		pick.queue_redraw()
	await _frames(SETTLE_FRAMES)


func _s_hq() -> void:
	var hq: Node = await _hq_with_campaign()
	await _settle(hq)


func _s_hq_black_market() -> void:
	var hq: Node = await _hq_with_campaign()
	RunManager.campaign.schematics = 500
	hq.show_hq()
	await _settle(hq)
	var market: Control = hq._panel.find_child("BlackMarket", true, false) if hq._panel != null else null
	var sc := hq._panel_host.get_parent() as ScrollContainer
	if market == null or sc == null:
		push_error("review_pack: no BlackMarket / scroll")
		return
	sc.ensure_control_visible(market)
	await _frames(SETTLE_FRAMES)


func _s_hq_crew() -> void:
	var hq: Node = await _hq_with_campaign()
	RunManager.campaign.roster.clear()
	for id in [&"ghost", &"rigger", &"botnet", &"wrecker"]:
		RunManager.campaign.recruit(RunManager.lookup().get_content(id) as ClassData)
	hq.show_hq()
	await _settle(hq)
	var roster: Control = hq._panel.find_child("Roster", true, false) if hq._panel != null else null
	var sc := hq._panel_host.get_parent() as ScrollContainer
	if roster != null and sc != null:
		sc.ensure_control_visible(roster)
	else:
		_warnings.append("no Roster node to scroll to")
	await _frames(SETTLE_FRAMES)


func _s_hq_loadout_deck() -> void:
	var hq: Node = await _hq_with_campaign()
	await _settle(hq)
	hq.open_loadout()
	await _settle(hq)


func _s_hq_loadout_spinner() -> void:
	var hq: Node = await _hq_with_campaign()
	var op: OperativeState = RunManager.campaign.living_operatives()[0]
	op.rank = 3
	hq.swap_segment(op.id, 0, &"seg_echo")
	await _settle(hq)
	hq.open_loadout(op)
	await _frames(2)
	var view := hq.get_node_or_null("LoadoutView")
	if view == null:
		push_error("review_pack: no LoadoutView")
		return
	view.show_spinner()
	await _settle(hq)


func _s_hq_pause() -> void:
	var hq: Node = await _hq_with_campaign()
	await _settle(hq)
	hq.open_settings()
	await _settle(hq)


func _s_grid() -> void:
	var hq: Node = await _hq_with_campaign()
	await _grid(hq)


func _s_grid_site_selected() -> void:
	var hq: Node = await _hq_with_campaign()
	for sd in RunManager.corporation.city_grid.sites:
		if sd.objective == RC.SiteObjective.EXPLOIT:
			hq.selected_site = sd.id
			break
	await _grid(hq)


func _s_grid_raid_pending() -> void:
	var hq: Node = await _hq_with_campaign()
	_prepare_raid(false)
	hq.selected_site = _first_link()
	await _grid(hq)


func _s_grid_meridian() -> void:
	await _grid_of(&"meridian")


func _s_grid_halcyon() -> void:
	await _grid_of(&"halcyon")


func _s_grid_orbital() -> void:
	await _grid_of(&"orbital")


func _s_grid_rebel_cell() -> void:
	await _grid_of(&"rebel_cell")


func _raid_setup() -> Node:
	var hq: Node = await _hq_with_campaign()
	_prepare_raid(true)
	hq.show_raid()
	await _until(func() -> bool: return hq.arrival_ready(), "the raid camera")
	await _settle(hq)
	return hq


func _s_raid_setup() -> void:
	await _raid_setup()


func _s_raid_playout() -> void:
	var hq: Node = await _raid_setup()
	hq.fight_raid()
	if reduce_effects:
		_warnings.append("reduce effects: the playout is instant, this shows its end")
	await _frames(2)
	if hq.playout != null:
		await _until(func() -> bool: return not is_instance_valid(hq.playout) or hq.playout.current_step() >= MID_PLAYOUT_STEP, "playout step %d" % MID_PLAYOUT_STEP)


func _s_raid_result() -> void:
	var hq: Node = await _raid_setup()
	hq.fight_raid()
	await _frames(2)
	if hq.playout != null and is_instance_valid(hq.playout):
		hq.playout.skip_to_end()
	await _settle(hq)


func _s_raid_report() -> void:
	var hq: Node = await _raid_setup()
	hq.fight_raid()
	await _frames(2)
	hq.show_raid_summary()
	await _settle(hq)


func _s_raid_interlude() -> void:
	var net: Node = await _netrun()
	HeatRules.add_heat(RunManager.campaign, RunManager.config().major_heat_levels()[0] + 1, RunManager.config(), "review_pack")
	RunManager.netrun._maybe_raid_interlude()
	net._show_current()
	await _until(func() -> bool: return net.arrival_ready(), "the interlude camera")
	await _settle(net)


func _s_route() -> void:
	var net: Node = await _netrun()
	await _until(func() -> bool: return net.arrival_ready(), "the route camera")
	await _settle(net)


func _s_combat_start() -> void:
	await _fight()


func _s_combat_hover() -> void:
	var combat := await _fight()
	if combat == null:
		return
	combat._preview_card(0)
	await _frames(SETTLE_FRAMES)


func _s_combat_aiming() -> void:
	var combat := await _fight()
	if combat == null:
		return
	for i in combat.engine.state().hand.size():
		if CardTargeting.options(combat.engine.resolver, combat.engine.state(), i).size() > 1:
			combat.select_card(i)
			await _frames(SETTLE_FRAMES)
			return
	_warnings.append("no card in the hand has more than one target; showing the first selected")
	combat.select_card(0)
	await _frames(SETTLE_FRAMES)


func _s_combat_resolving() -> void:
	var combat := await _fight()
	if combat == null:
		return
	combat.end_turn()
	if reduce_effects:
		_warnings.append("reduce effects: the replay may already be at its end")
	await _frames(MID_REPLAY_FRAMES)


func _s_combat_after() -> void:
	var combat := await _fight()
	if combat == null:
		return
	combat.end_turn()
	await _frames(2)
	combat.skip_motion()
	await _until(func() -> bool: return not combat.motion_busy(), "the replay to end")
	await _settle(combat.get_parent())


func _s_combat_refused() -> void:
	var combat := await _fight()
	if combat == null:
		return
	for i in 8:
		if combat.engine.state().ram < combat.engine.resolver.config.respin_ram_cost:
			break
		combat.respin()
	await _frames(4)
	combat.skip_motion()
	await _frames(4)
	combat.respin()
	await _frames(SETTLE_FRAMES)


func _s_combat_boss_p2() -> void:
	await _boss_phase(BOSS_P2_SHARE)


func _s_combat_boss_p3() -> void:
	await _boss_phase(BOSS_P3_SHARE)


func _combat_end(kind: String) -> void:
	var combat := await _fight()
	if combat == null:
		return
	var net := combat.get_parent()
	while net != null and not net.has_method(&"_demo_combat_end"):
		net = net.get_parent()
	if net == null:
		push_error("review_pack: no netrun scene above the fight")
		return
	await net._demo_combat_end(kind)
	# The replay is skipped to its end: the held outcome (DEFEATED stamp, status word, the
	# LOOT / JACK OUT verb) is the picture, not the wheel breaking mid-way.
	await _frames(2)
	combat.skip_motion()
	await _until(func() -> bool: return not is_instance_valid(combat) or combat.continue_shown(), "the outcome to land")
	await _frames(SETTLE_FRAMES)


func _s_combat_victory() -> void:
	await _combat_end("win")


func _s_combat_defeat() -> void:
	await _combat_end("lose")


func _s_loot() -> void:
	var net: Node = await _netrun()
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.phase = RunState.Phase.REWARD
	net._show_current()
	await _settle(net)


func _modem(seed: int) -> Node:
	var net: Node = await _netrun(seed)
	RunManager.netrun.run.cycles = 120
	RunManager.netrun._open_shop()
	net._show_current()
	await _settle(net)
	return net


func _s_modem() -> void:
	await _modem(7)


func _s_modem_socket() -> void:
	for seed in range(7, 7 + SOCKET_SEEDS):
		var net: Node = await _modem(seed)
		# Art pass W8c: the socket list became slot tiles (SlotPicker, a TilePicker): the shot
		# focuses them (an OptionButton still pops its list).
		var pick := net._panel.find_child("SocketPick", true, false) as Control if net._panel != null else null
		if pick != null and pick.is_visible_in_tree():
			if seed != 7:
				_warnings.append("campaign seed %d (the first with Firmware in stock)" % seed)
			if pick.has_method("show_popup"):
				pick.call("show_popup")
			else:
				pick.grab_focus()
			await _frames(SETTLE_FRAMES)
			return
		net.queue_free()
		await _frames(2)
		RunManager.reset()
	push_error("review_pack: no Modem with Firmware in %d seeds" % SOCKET_SEEDS)


func _s_event() -> void:
	var net: Node = await _netrun()
	var run := RunManager.netrun.run
	run.event_id = &"ev_leash_on_the_floor"
	run.phase = RunState.Phase.EVENT
	net._show_current()
	await _settle(net)


func _title_page(page: String) -> void:
	var title: Node = TITLE.instantiate()
	get_tree().root.add_child(title)
	await _frames(2)
	title.call(page)
	await _settle(title)


func _s_codex() -> void:
	for id in [&"renewal_engine", &"collections_agent"]:
		RunManager.record_seen(id)
	await _title_page("show_codex")


func _s_options() -> void:
	await _title_page("show_options")


func _s_stats() -> void:
	var p := RunManager.profile
	p.campaigns_started = 3
	p.campaigns_won = 1
	p.runs_completed = 14
	p.raids_won = 2
	p.stats["perfects"] = 9
	p.stats["cycles"] = 640
	if Achievements.DEFS.size() > 0:
		p.achievements.append(StringName(str(Achievements.DEFS[0]["id"])))
	p.run_history.append({"corporation": "solace", "tier": 1, "site": "t1_a", "outcome": "completed", "cycles": 40, "banked": 12})
	p.run_history.append({"corporation": "solace", "tier": 2, "site": "t2_intel", "outcome": "died", "cycles": 18, "banked": 0})
	p.best_ice_by_corp["solace"] = 2
	await _title_page("show_stats")


func _s_run_end() -> void:
	var net: Node = await _netrun()
	RunManager.netrun.run.outcome = RunState.Outcome.DIED
	RunManager.netrun.run.phase = RunState.Phase.ENDED
	net._show_current()
	await _settle(net)


func _campaign_end(outcome: int) -> void:
	var hq: Node = await _hq_with_campaign()
	var c := RunManager.campaign
	c.story_beats_revealed = 99
	c.outcome = outcome
	hq.show_end()
	await _settle(hq)


func _s_campaign_won() -> void:
	await _campaign_end(CampaignState.Outcome.WON)


func _s_campaign_lost() -> void:
	await _campaign_end(CampaignState.Outcome.LOST)


# --- Runtime lint export -----------------------------------------------------------------

## Every visible text Control on screen with its screen rect, the rect its text covers,
## its effective font size, colour and the clipping facts the report needs. Overlap and
## contrast are judged in Python (tools/visual_qa/lint_report.py) against the PNG.
func _lint_export(screen: String, size: Vector2i) -> Dictionary:
	var out: Array = []
	_custom_draw = []
	var screen_rect := Rect2(Vector2.ZERO, Vector2(size))
	_walk(get_tree().root, out, screen_rect)
	return {"screen": screen, "text_scale": text_scale, "viewport": [size.x, size.y],
		"floor_px": roundi(12 * text_scale), "controls": out, "custom_draw": _custom_draw}


func _walk(n: Node, out: Array, screen_rect: Rect2) -> void:
	if n == _filter_layer or n == self:
		return
	if n is CanvasItem and not (n as CanvasItem).visible:
		return
	if n is CanvasLayer and not (n as CanvasLayer).visible:
		return
	if n is Window and n != get_tree().root and not (n as Window).visible:
		return
	if n is Control:
		var c := n as Control
		if _is_text(c) and c.is_visible_in_tree():
			var rec := _text_record(c, screen_rect)
			if not rec.is_empty():
				out.append(rec)
	if n is CanvasItem and _draws_text(n):
		var ci := n as CanvasItem
		if ci.is_visible_in_tree():
			var r := _screen_rect_of(n as Control, Rect2(Vector2.ZERO, (n as Control).size)) if n is Control else Rect2()
			_custom_draw.append({"path": str(n.get_path()), "script": (n.get_script() as Script).resource_path,
				"rect": [r.position.x, r.position.y, r.size.x, r.size.y]})
	for k in n.get_children():
		_walk(k, out, screen_rect)


## Whether the node's script draws text itself (draw_string in its source): the tree walk
## can't see that text (ART_BIBLE §13 lint, W10 item 4e).
func _draws_text(n: Node) -> bool:
	var s := n.get_script() as Script
	if s == null or not s.resource_path.begins_with("res://scripts/"):
		return false
	if not _draw_cache.has(s.resource_path):
		var src := FileAccess.get_file_as_string(s.resource_path)
		_draw_cache[s.resource_path] = src.contains("draw_string(") or src.contains("draw_multiline_string(")
	return _draw_cache[s.resource_path]


func _is_text(c: Control) -> bool:
	for cls in TEXT_CLASSES:
		if c.is_class(cls):
			return true
	return false


func _text_of(c: Control) -> String:
	if c is RichTextLabel:
		return (c as RichTextLabel).get_parsed_text()
	if c is LineEdit:
		var le := c as LineEdit
		return le.text if le.text != "" else le.placeholder_text
	if c is TextEdit:
		return (c as TextEdit).text
	var t: Variant = c.get(&"text")
	return str(t) if t != null else ""


func _screen_rect_of(c: Control, local: Rect2) -> Rect2:
	var xf := c.get_global_transform_with_canvas()
	var a := xf * local.position
	var b := xf * local.end
	var r := Rect2(a, Vector2.ZERO).expand(b)
	# Controls in an embedded popup window draw at the window's offset.
	var w := c.get_window()
	if w != null and w != get_tree().root:
		r.position += Vector2(w.position)
	return r


## The nearest game script (self or an ancestor) that built this Control: the file a
## workstream fixes.
func _owner_script(c: Node) -> String:
	var n: Node = c
	while n != null:
		var s := n.get_script() as Script
		if s != null and s.resource_path.begins_with("res://scripts/"):
			return s.resource_path
		n = n.get_parent()
	return ""


func _alpha_of(c: CanvasItem) -> float:
	var a := c.self_modulate.a
	var n: Node = c
	while n != null:
		if n is CanvasItem:
			a *= (n as CanvasItem).modulate.a
		n = n.get_parent()
	return a


func _text_record(c: Control, screen_rect: Rect2) -> Dictionary:
	var text := _text_of(c).strip_edges()
	if text == "":
		return {}
	var rect := _screen_rect_of(c, Rect2(Vector2.ZERO, c.size))
	if not rect.intersects(screen_rect) or rect.size.x < 1.0 or rect.size.y < 1.0:
		return {}
	var size_name := &"normal_font_size" if c is RichTextLabel else &"font_size"
	var font_px := c.get_theme_font_size(size_name)
	var color_name := &"default_color" if c is RichTextLabel else &"font_color"
	var col := c.get_theme_color(color_name)
	var font := c.get_theme_font(&"normal_font" if c is RichTextLabel else &"font")
	var override := -1
	if c.has_theme_font_size_override(size_name):
		override = font_px
	var ink := rect
	var lines := 1
	var visible_lines := 1
	var overrun := 0
	var clip := false
	var fits := true
	var in_scroll := false
	var p := c.get_parent()
	while p != null:
		if p is ScrollContainer:
			in_scroll = true
			break
		p = p.get_parent()
	var scale := c.get_global_transform_with_canvas().get_scale()
	if c is Label:
		var l := c as Label
		lines = l.get_line_count()
		visible_lines = l.get_visible_line_count()
		overrun = l.text_overrun_behavior
		clip = l.clip_text
		var shown := l.text
		if font != null:
			var line_h := font.get_height(font_px) + l.get_theme_constant(&"line_spacing")
			var widest := 0.0
			for part in shown.split("\n"):
				widest = maxf(widest, font.get_string_size(part, HORIZONTAL_ALIGNMENT_LEFT, -1, font_px).x)
			if l.autowrap_mode == TextServer.AUTOWRAP_OFF:
				fits = widest <= l.size.x + 1.0
			var w := minf(widest, l.size.x)
			var h := minf(line_h * maxi(visible_lines, 1), l.size.y)
			var x := 0.0
			match l.horizontal_alignment:
				HORIZONTAL_ALIGNMENT_CENTER:
					x = (l.size.x - w) * 0.5
				HORIZONTAL_ALIGNMENT_RIGHT:
					x = l.size.x - w
			var y := 0.0
			match l.vertical_alignment:
				VERTICAL_ALIGNMENT_CENTER:
					y = (l.size.y - h) * 0.5
				VERTICAL_ALIGNMENT_BOTTOM:
					y = l.size.y - h
			ink = _screen_rect_of(c, Rect2(x, y, w, h))
	elif c is Button:
		var b := c as Button
		overrun = b.text_overrun_behavior
		clip = b.clip_text
		if font != null:
			var sw := font.get_string_size(b.text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_px).x
			var sb := b.get_theme_stylebox(&"normal")
			var room := b.size.x - (sb.get_minimum_size().x if sb != null else 0.0)
			if b.icon != null:
				room -= b.icon.get_width() + b.get_theme_constant(&"h_separation")
			fits = sw <= room + 1.0
			var w := minf(sw, b.size.x)
			var h := minf(font.get_height(font_px), b.size.y)
			var x := (b.size.x - w) * 0.5
			match b.alignment:
				HORIZONTAL_ALIGNMENT_LEFT:
					x = sb.get_margin(SIDE_LEFT) if sb != null else 0.0
				HORIZONTAL_ALIGNMENT_RIGHT:
					x = b.size.x - w - (sb.get_margin(SIDE_RIGHT) if sb != null else 0.0)
			ink = _screen_rect_of(c, Rect2(x, (b.size.y - h) * 0.5, w, h))
	elif c is RichTextLabel:
		var r := c as RichTextLabel
		lines = r.get_line_count()
		visible_lines = r.get_visible_line_count()
		var cw := minf(float(r.get_content_width()), r.size.x)
		var ch := minf(float(r.get_content_height()), r.size.y)
		if cw > 0.0 and ch > 0.0:
			ink = _screen_rect_of(c, Rect2(0, 0, cw, ch))
		fits = r.fit_content or r.scroll_active or float(r.get_content_height()) <= r.size.y + 1.0
	return {
		"path": str(c.get_path()),
		"class": c.get_class(),
		"owner_script": _owner_script(c),
		"self_draws": _draws_text(c),
		"text": text.substr(0, LINT_TEXT_MAX),
		"rect": [rect.position.x, rect.position.y, rect.size.x, rect.size.y],
		"ink": [ink.position.x, ink.position.y, ink.size.x, ink.size.y],
		"font_px": font_px,
		"screen_px": font_px * absf(scale.y),
		"override": override,
		"color": [col.r, col.g, col.b, col.a],
		"alpha": _alpha_of(c),
		"lines": lines,
		"visible_lines": visible_lines,
		"overrun": overrun,
		"clip": clip,
		"fits": fits,
		"in_scroll": in_scroll,
		"ellipsis": text.contains("…"),
	}


# --- Files -----------------------------------------------------------------------------

func _write_json(path: String, data: Variant) -> void:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(data, "\t"))
		f.close()


func _write_text(path: String, text: String) -> void:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f != null:
		f.store_string(text)
		f.close()
