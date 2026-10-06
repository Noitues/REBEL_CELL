extends Node
## Review-pack harness (ART-0 D, ported from art-pass W10 / W9F; ART_BIBLE §13 "Automated
## visual checks"). Dev tool, never exported (tools/* is excluded) and never in game code.
## Drives every reachable screen of main's game from a clean state through the scenes'
## public methods, their dev hooks and `DemoSetup` (the same way tools/playtest/storyboard.gd,
## the motion lab and the integration tests do), captures a picture of each and exports the
## visible text Controls for the runtime lint (`<screen>.lint.json`). Needs a renderer: run it
## only through `tools/visual_qa/capture_pack.py` (which goes through tools/run_windowed.py and
## gives the run its own user:// folder), never headless (only `--list` runs headless).
##
##   res://tools/visual_qa/review_pack.tscn -- --out=<abs dir> [--screens=a,b] [--scale=1.6]
##       [--pad] [--reduce-effects] [--filter=none|grey|deutan] [--scramble]
##       [--high-contrast] [--reduce-motion] [--colorblind=<mode>] [--save-size=800x450]
##       [--screen-timeout=90] [--list=<file.json>] [--skins=v2,cobalt]
## --skins (ART-12 12s) walks the screens once per palette skin, into <out>/<skin>/.
## --scales=1.0,1.6,2.0 (parity NEWC) walks them once per text scale, into <out>/s<scale>/
## (one launch for a fit check at every scale; it overrides --scale).
##
## Per screen it writes <screen>.png, <screen>.lint.json and <screen>.status.json
## ({status: ok|failed|timeout|unavailable, error, errors[], warnings[], seconds});
## `_current.txt` names the screen in progress, so the driver can tell which one a crash took
## down. `--scale` writes Settings.text_scale directly, past the clamp of set_text_scale (main
## clamps at 1.6 until ART-0 C raises it to 2.0). The accessibility axes (high contrast,
## reduce motion, colour-blind mode) are switched only when this build's Settings has them
## (`settings_axes()`; ART-0 C ports them): `--list` reports which exist and the driver skips
## the others. Nothing is saved to the player's files.

const TITLE := preload("res://scenes/menu/title_scene.tscn")
const HQ := preload("res://scenes/hq/hq_scene.tscn")
const COMBAT := preload("res://scenes/combat/combat_scene.tscn")
const NETRUN := preload("res://scenes/netrun_map/netrun_scene.tscn")
const FILTER_SHADER := preload("res://tools/visual_qa/cvd_filter.gdshader")
const ErrorLog := preload("res://tools/visual_qa/review_pack_log.gd")

const SLOT := "gut_review_pack"
const SAVE_DIR := "user://saves/review_pack"
const SETTINGS_FILE := "user://review_pack_settings.json"
## The layout size: every screen is laid out and linted at this size.
const CAPTURE_SIZE := Vector2i(1280, 720)
## Frames a screen gets to settle before its picture.
const SETTLE_FRAMES := 12
## Most frames the harness waits for a map camera, a fight to open or a motion to end.
const WAIT_FRAMES := 900
## Most seconds (real time: bakes run on worker threads, and frames run as fast as they can
## under --fixed-fps) the harness waits for every visible city to show its baked current look;
## a city still not there is captured anyway, with a warning naming it.
const CITY_WAIT_S := 20.0
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
## Seeds tried for a Mainframe that stocks Firmware (the socket picker needs one).
const SOCKET_SEEDS := 12
## Boss HP shares for the phase screens (content phases are at 66% and 33%).
const BOSS_P2_SHARE := 0.6
const BOSS_P3_SHARE := 0.25
## Frames into a SEND IT replay / raid playout for the "mid" pictures.
const MID_REPLAY_FRAMES := 24
const MID_PLAYOUT_STEP := 2
## Frames into a scripted drag (the HQ's ANIM-4 drag demo: layout, pick-up, then the pointer
## path) at which the item is carried mid-way.
const MID_DRAG_FRAMES := 10
## The Heat poster's band crossing (the HQ's heat_pulse demo values) and the frames into the
## crossing the picture is taken (its banner and note are up for their reading hold).
const HEAT_FROM := 20
const HEAT_TO := 30
const HEAT_BAND_FRAMES := 20
## Schematics a raid or claim screen gets to spend (the HQ demos' budget).
const DEMO_SCHEMATICS := 100
## The accessibility settings the axes switch (ART-0 C ports them; absent on older builds).
const AXIS_SETTINGS: Array[StringName] = [&"high_contrast", &"reduce_motion", &"colorblind_mode"]

## Screen name -> [method, what the picture shows]. Order is the capture order. Re-pointed at
## main's screens (ART-0 D): main's ANIM states the art pass never saw are marked "main".
const SCREENS := [
	["title", "_s_title", "Title / main menu with a campaign to continue."],
	["title_confirm", "_s_title_confirm", "ART-10 4C: the title's delete-slot confirm (the abandon dialog look)."],
	["slots", "_s_slots", "Campaign slots with one saved campaign."],
	["new_campaign", "_s_new_campaign", "New campaign page (all corporations unlocked)."],
	["new_campaign_picker", "_s_new_campaign_picker", "New campaign with the target picker open."],
	["new_campaign_locked", "_s_new_campaign_locked", "Parity NEWC: a fresh profile's new campaign (corporations, homes and classes locked, one class and one home bought)."],
	["new_campaign_crew", "_s_new_campaign_crew", "Parity NEWC: the same page scrolled to the crew tiles and the city seed."],
	["new_campaign_codes", "_s_new_campaign_codes", "Parity NEWC: the same page scrolled to today's run and the share codes, the code row open."],
	["hq", "_s_hq", "HQ after starting a new campaign."],
	["hq_black_market", "_s_hq_black_market", "HQ scrolled to the Black Market."],
	["hq_crew", "_s_hq_crew", "HQ crew / dossiers with four classes."],
	["hq_loadout_deck", "_s_hq_loadout_deck", "Loadout modal, DECK tab."],
	["hq_loadout_spinner", "_s_hq_loadout_spinner", "Loadout modal, SPINNER tab, rank-3 operative."],
	["hq_pause", "_s_hq_pause", "Pause menu over the HQ."],
	["hq_heat_band", "_s_hq_heat_band", "main: the HQ's Heat poster crossing a band (banner and note held)."],
	["grid", "_s_grid", "City Grid, nothing selected."],
	["grid_site_selected", "_s_grid_site_selected", "City Grid with an Exploit site selected."],
	["grid_raid_pending", "_s_grid_raid_pending", "City Grid with a raid pending (RAID SETUP)."],
	["grid_influence", "_s_grid_influence", "main: City Grid after a second claim, its territory tint landed."],
	["grid_drag_crew", "_s_grid_drag_crew", "main: an operative carried from the Grid's crew chips to JACK IN."],
	["grid_meridian", "_s_grid_meridian", "City Grid against Meridian."],
	["grid_halcyon", "_s_grid_halcyon", "City Grid against Halcyon."],
	["grid_orbital", "_s_grid_orbital", "City Grid against Orbital."],
	["grid_rebel_cell", "_s_grid_rebel_cell", "City Grid against REBEL_CELL."],
	["raid_setup", "_s_raid_setup", "Raid setup with one asset deployed."],
	["raid_drag_asset", "_s_raid_drag_asset", "main: an asset carried from the Armory onto the raid map."],
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
	["mainframe", "_s_mainframe", "The Mainframe shop."],
	["mainframe_socket", "_s_mainframe_socket", "The Mainframe with the socket choice open."],
	["mainframe_remove", "_s_mainframe_remove", "The Mainframe's REMOVE A CARD viewer."],
	["mainframe_overwrite", "_s_mainframe_overwrite", "The Mainframe's UPGRADE A SLICE viewer, a slot picked."],
	["event", "_s_event", "A story event with choices."],
	["event_dispatch", "_s_event_dispatch", "A DISPATCH (terminal) event."],
	["codex", "_s_codex", "Codex from the title menu."],
	["options", "_s_options", "Options from the title menu."],
	["stats", "_s_stats", "Stats and achievements with some history."],
	["run_end", "_s_run_end", "Run end: FLATLINED."],
	["run_end_clean", "_s_run_end_clean", "main: run end after a clean exit (the verdict stamp)."],
	["campaign_won", "_s_campaign_won", "Campaign end: WON."],
	["campaign_lost", "_s_campaign_lost", "Campaign end: LOST."],
	["deck_view", "_s_deck_view", "VIEW LOADOUT in a netrun: the deck viewer."],
	["card_detail", "_s_card_detail", "A card's detail over the deck viewer."],
	["daemon_tray", "_s_daemon_tray", "The Daemon tray with an installed Daemon."],
	["tutorial", "_s_tutorial", "The tutorial's first step over its fight."],
	["jack_in", "_s_jack_in", "The jack-in transition, its cover up."],
	["pause_netrun", "_s_pause_netrun", "The pause menu over a netrun's route."],
	["pause_fight", "_s_pause_fight", "The pause menu over a fight."],
	["pause_fight_quit", "_s_pause_fight_quit", "ART-2 2D: the quit confirm (the dialog kit) over a fight's pause menu."],
]

var out_dir := ""
var text_scale := 1.0
var pad := false
var reduce_effects := false
var filter := "none"
var scramble := false
## The accessibility axes (each switched only when Settings has it).
var high_contrast := false
var reduce_motion := false
var colorblind := ""
## ART-12 12s: palette skins to walk (empty: the one Settings has).
var skins: PackedStringArray = []
## Parity NEWC: text scales to walk (empty: the one --scale gives).
var scales: PackedStringArray = []
## The PNG's size (the layout stays CAPTURE_SIZE; the picture is scaled down to keep packs small).
var save_size := CAPTURE_SIZE
var screen_timeout := DEFAULT_TIMEOUT_S
var _keep: Array[Node] = []
var _log: RefCounted = null
var _warnings: Array[String] = []
var _done := false
var _filter_layer: CanvasLayer = null
var _custom_draw: Array = []
var _draw_cache := {}
## Run once the picture is taken (the jack's switch lets its cover lift).
var _after_capture: Callable = Callable()
## Axes asked for that this build's Settings lacks: every screen reports "unavailable".
var _missing_axes: Array[String] = []
## The screen being reached: a screen given up on (timeout or script error) leaves its
## coroutine waiting inside a helper; when the helper wakes on a later screen it parks on
## `_never` instead of driving a freed scene (it never resumes).
var _gen := 0
signal _never


## Which accessibility settings this build's Settings has ({name: bool}).
static func settings_axes() -> Dictionary:
	var out := {}
	for s in AXIS_SETTINGS:
		out[String(s)] = s in Settings
	return out


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
		elif a == "--high-contrast":
			high_contrast = true
		elif a == "--reduce-motion":
			reduce_motion = true
		elif a.begins_with("--colorblind="):
			colorblind = a.trim_prefix("--colorblind=")
		elif a.begins_with("--save-size="):
			var wh := a.trim_prefix("--save-size=").split("x")
			if wh.size() == 2 and int(wh[0]) > 0 and int(wh[1]) > 0:
				save_size = Vector2i(int(wh[0]), int(wh[1]))
		elif a.begins_with("--screen-timeout="):
			screen_timeout = float(a.trim_prefix("--screen-timeout="))
		elif a.begins_with("--skins="):
			skins = a.trim_prefix("--skins=").split(",", false)
		elif a.begins_with("--scales="):
			scales = a.trim_prefix("--scales=").split(",", false)
		elif a.begins_with("--list="):
			list_file = a.trim_prefix("--list=")
	if list_file != "":
		_write_json(list_file, {
			"screens": SCREENS.map(func(s: Array) -> Dictionary: return {"screen": s[0], "what": s[2]}),
			"settings_axes": settings_axes(),
			"text_scale_max": Settings.TEXT_SCALE_MAX,
		})
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
	var base := out_dir
	for skin in (skins if not skins.is_empty() else PackedStringArray([""])):
		var skin_dir := base
		if skin != "":
			Settings.palette_skin = StringName(skin)
			Settings.changed.emit()
			skin_dir = base.path_join(skin)
		for sc in (scales if not scales.is_empty() else PackedStringArray([""])):
			out_dir = skin_dir
			if sc != "":
				text_scale = float(sc)
				Settings.text_scale = text_scale  # past the clamp on purpose, as --scale
				Settings.changed.emit()
				out_dir = skin_dir.path_join("s" + sc)
			DirAccess.make_dir_recursive_absolute(out_dir)
			for s in todo:
				if _missing_axes.is_empty():
					await _capture(s[0], s[1], s[2])
				else:
					_unavailable(s[0], s[2])
	out_dir = base
	_teardown()
	print("REVIEW PACK DONE %d screens in %s" % [todo.size(), out_dir])
	get_tree().quit()


# --- Axes ------------------------------------------------------------------------------

func _setup_settings() -> void:
	# Nothing reaches the player's files: settings, slot and saves are private (as the
	# storyboard), on top of the private user:// folder the driver gives the run.
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
	Settings.text_scale = text_scale  # past the clamp on purpose (the harness checks big text)
	Settings.reduce_effects = reduce_effects
	if high_contrast:
		_set_axis(&"high_contrast", true)
	if reduce_motion:
		_set_axis(&"reduce_motion", true)
	if colorblind != "":
		_set_axis(&"colorblind_mode", StringName(colorblind))
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


## Switches accessibility setting `name` when this build has it; otherwise the axis is
## recorded as missing (its screens report "unavailable", never a picture without it).
func _set_axis(name: StringName, value: Variant) -> void:
	if name in Settings:
		Settings.set(name, value)
	else:
		_missing_axes.append(String(name))


func _unavailable(screen: String, what: String) -> void:
	var why := "Settings has no %s on this build (ART-0 C ports it)" % ", ".join(_missing_axes)
	_write_json(out_dir.path_join(screen + ".status.json"), {
		"screen": screen, "what": what, "status": "unavailable", "error": why,
		"errors": [], "warnings": [], "seconds": 0.0, "frames": 0,
	})


func _teardown() -> void:
	_clear_scenes()
	RunManager.delete_save()
	for slot in ["1", "demo", SLOT]:
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
	_gen += 1
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
			# The lint reads the layout at CAPTURE_SIZE; the PNG may be smaller (lint_report.py
			# scales it back up to measure contrast).
			var lint := _lint_export(screen, img.get_size())
			if save_size != CAPTURE_SIZE:
				img.resize(save_size.x, save_size.y, Image.INTERPOLATE_LANCZOS)
			lint["png_size"] = [save_size.x, save_size.y]
			img.save_png(png)
			_write_json(out_dir.path_join(screen + ".lint.json"), lint)
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
	if _after_capture.is_valid():
		var after := _after_capture
		_after_capture = Callable()
		await after.call()
		await _frames(SETTLE_FRAMES)


func _run_screen(method: String) -> void:
	var gen := _gen
	await call(method)
	if gen == _gen:
		_done = true


func _reset() -> void:
	# Bakes still building or queued land first (at most CITY_WAIT_S): a scene freed under a
	# build that is submitting its chunks raised script errors in the cache's coroutine.
	var since := Time.get_ticks_msec()
	while CityBakeCache._building > 0 or not CityBakeCache._queue.is_empty():
		if (Time.get_ticks_msec() - since) / 1000.0 > CITY_WAIT_S:
			break
		await get_tree().process_frame
	# ...and their picture is read back (a build done on the GPU still reads its picture for
	# READBACK_FRAMES drawn frames; its painter must outlive that).
	for i in CityBakeCache.READBACK_FRAMES + 1:
		await RenderingServer.frame_post_draw
	_clear_scenes()
	for i in 3:
		await get_tree().process_frame
	# Every screen starts from a cold city cache, as a fresh launch does: bakes of the scenes
	# just freed (mid-build, or held by their views) never block the next screen's bake.
	CityBakeCache.shutdown()
	get_tree().paused = false
	Dialogue.clear()
	Engine.time_scale = 1.0
	RunManager.save_slot = SLOT
	RunManager.delete_save()
	RunManager.reset()
	RunManager.scene_switching_enabled = false


func _clear_scenes() -> void:
	for n in get_tree().root.get_children():
		if not _keep.has(n):
			n.queue_free()


func _open(scene: PackedScene) -> Node:
	var n := scene.instantiate()
	get_tree().root.add_child(n)
	return n


func _frames(n: int) -> void:
	var gen := _gen
	for i in n:
		await get_tree().process_frame
		if gen != _gen:
			await _never


## Waits until `cond` holds (at most WAIT_FRAMES); false (with a warning) if it never did.
func _until(cond: Callable, why: String, limit: int = WAIT_FRAMES) -> bool:
	var gen := _gen
	for i in limit:
		if cond.call():
			return true
		await get_tree().process_frame
		if gen != _gen:
			await _never
	_warnings.append("waited %d frames for %s" % [limit, why])
	return false


## Lets the screen settle: page entrances and deals end, subtitles finish typing.
func _settle(root: Node, frames: int = SETTLE_FRAMES) -> void:
	await _frames(frames)
	# The city's bake lands before the picture (a stand-in city is not the screen). Main's
	# views hold the bake they draw (ANIM-R6), so "no bake running" is not the test: every
	# visible city shows its current look from a finished bake, faded in.
	var gen := _gen
	var since := Time.get_ticks_msec()
	while not _cities_ready():
		if (Time.get_ticks_msec() - since) / 1000.0 > CITY_WAIT_S:
			_warnings.append("waited %.0f s for the city bake; not ready: %s" % [CITY_WAIT_S, _city_wait_reason()])
			break
		await get_tree().process_frame
		if gen != _gen:
			await _never
	if is_instance_valid(root):
		PageTransition.settle(root)
	Dialogue.finish_typing()
	Typing.finish_all(get_tree())
	await _frames(4)


## True when every visible city draws its current look, its view covered by a finished
## bake and faded in (or it draws procedurally).
func _cities_ready() -> bool:
	return _city_wait_reason() == ""


## Why a visible city is not ready yet ("" when every one is).
func _city_wait_reason() -> String:
	for n in get_tree().root.find_children("*", "", true, false):
		var city := n as NeonCity
		if city == null or not city.is_visible_in_tree() or city.hold_landing:
			# A held city (a fight's, ANIM-R6 A14) lands its bake between turns by design.
			continue
		var why := PackedStringArray()
		if not city.showing_current_look():
			why.append("old look")
		if not city.view_covered():
			why.append("view not covered")
		if city.bake_fade < 1.0:
			why.append("fading in")
		if not why.is_empty():
			return "%s (%s)" % [city.get_path(), ", ".join(why)]
	return ""


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
	DemoSetup.set_schematics(c, DEMO_SCHEMATICS)
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	var armory: Array[StringName] = [&"turret", &"ice_lock", &"decoy"]
	DemoSetup.set_armory(c, armory)
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
	await _until(func() -> bool: return not is_instance_valid(net) or net.combat_scene != null, "the fight to open")
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


func _s_title_confirm() -> void:
	RunManager.save_slot = "1"  # the confirm shows slot 1's costs
	RunManager.new_campaign(7)
	DemoSetup.set_heat(RunManager.campaign, 33)
	RunManager.autosave()
	var title: Node = TITLE.instantiate()
	title.continue_slot = SLOT
	get_tree().root.add_child(title)
	await _frames(2)
	title.confirm_delete("1")
	await _settle(title)


func _s_slots() -> void:
	RunManager.save_slot = "1"
	RunManager.new_campaign(4)
	DemoSetup.set_heat(RunManager.campaign, 33)
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


## Parity NEWC: a fresh profile (only Solace open) with one class and one home server bought,
## so the page shows open and locked tiles in every picker, with their unlock costs.
func _s_new_campaign_locked() -> void:
	await _new_campaign_locked_page()


func _new_campaign_locked_page() -> Node:
	var p := RunManager.profile
	p.unlocks.clear()
	p.best_ice_by_corp.clear()
	for u in [&"unlock_ghost", &"unlock_home_bunker"]:
		p.unlocks.append(u)
	RunManager.campaign = null
	var hq: Node = _open(HQ)
	await _frames(2)
	if hq.panel_name != "start":
		hq.show_start()
	await _settle(hq)
	return hq


## Scrolls the page so `node_name` shows (its bottom on the screen).
func _scroll_to(hq: Node, node_name: String) -> void:
	var target: Control = hq._panel.find_child(node_name, true, false) if hq._panel != null else null
	var sc := hq._panel_host.get_parent() as ScrollContainer
	if target == null or sc == null:
		push_error("review_pack: no %s / scroll" % node_name)
		return
	sc.ensure_control_visible(target)
	await _frames(SETTLE_FRAMES)


func _s_new_campaign_crew() -> void:
	var hq: Node = await _new_campaign_locked_page()
	await _scroll_to(hq, "SeedRow")


func _s_new_campaign_codes() -> void:
	var hq: Node = await _new_campaign_locked_page()
	var toggle := hq._panel.find_child("CodesToggle", true, false) as Button
	if toggle != null:
		toggle.pressed.emit()
	await _frames(2)
	await _scroll_to(hq, "ShareCodes")


func _s_new_campaign_picker() -> void:
	var hq: Node = await _new_campaign_page()
	var pick := hq.find_child("CorporationPicker", true, false) as Control
	if pick == null:
		push_error("review_pack: no CorporationPicker")
		return
	# Main: an OptionButton (its list pops up). The art pass's dossier tiles (no popup) take
	# focus on their second tile instead.
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
	DemoSetup.set_schematics(RunManager.campaign, 500)
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
	var classes: Array[ClassData] = []
	for id in [&"ghost", &"rigger", &"botnet", &"wrecker"]:
		classes.append(RunManager.lookup().get_content(id) as ClassData)
	DemoSetup.roster_of(RunManager.campaign, classes)
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
	DemoSetup.set_rank(op, 3)
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


## Main (ANIM-R6): the wanted poster crosses a Heat band where it shows; the picture is taken
## during its reading hold (banner and consequence note up). Under reduce effects it is the
## end state at once.
func _s_hq_heat_band() -> void:
	var hq: Node = await _hq_with_campaign()
	DemoSetup.set_heat(RunManager.campaign, HEAT_FROM)
	hq.show_hq()
	await _settle(hq)
	DemoSetup.set_heat(RunManager.campaign, HEAT_TO)
	hq.show_hq()
	await _frames(HEAT_BAND_FRAMES)


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


## Main (ANIM-5 / R6): a second Site cleared and claimed on the Grid; the territory tint
## spreads from it once its new look has baked (the HQ's influence_spread demo).
func _s_grid_influence() -> void:
	var hq: Node = await _hq_with_campaign()
	await _grid(hq)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	DemoSetup.set_schematics(c, DEMO_SCHEMATICS)  # the claim's price (the HQ demos' budget)
	for sd in RunManager.launchable_sites():
		if not c.grid.is_claimed(sd.id):
			CampaignRules.on_run_completed(c, corp, RunManager.config(), hq._demo_run(sd.id))
			CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), sd.id, &"firewall_relay")
			break
	# Every visible city re-reads the influence; the picture waits for the new look to land
	# (its tint spreads in from the claim, or shows at once under reduce effects).
	for n in get_tree().root.find_children("*", "", true, false):
		if n is NeonCity and (n as NeonCity).is_visible_in_tree():
			(n as NeonCity).sync_influence()
	await _settle(hq)


## Main (ANIM-4): an operative carried from the Grid's crew chips towards JACK IN, mid-path
## (the HQ's drag_crew demo; scene switching stays off, so nothing launches).
func _s_grid_drag_crew() -> void:
	var hq: Node = await _hq_with_campaign()
	await _grid(hq)
	await _mid_drag(hq, "drag_crew")


func _s_grid_meridian() -> void:
	await _grid_of(&"meridian")


func _s_grid_halcyon() -> void:
	await _grid_of(&"halcyon")


func _s_grid_orbital() -> void:
	await _grid_of(&"orbital")


func _s_grid_rebel_cell() -> void:
	await _grid_of(&"rebel_cell")


func _raid_setup(deploy: bool = true) -> Node:
	var hq: Node = await _hq_with_campaign()
	_prepare_raid(deploy)
	hq.show_raid()
	await _until(func() -> bool: return hq.arrival_ready(), "the raid camera")
	await _settle(hq)
	return hq


func _s_raid_setup() -> void:
	await _raid_setup()


## Main (ANIM-4): an asset carried from the Armory onto the raid map, mid-path (the HQ's
## drag_asset demo).
func _s_raid_drag_asset() -> void:
	var hq: Node = await _raid_setup(false)
	await _mid_drag(hq, "drag_asset")


## Starts the HQ's scripted drag `id` and waits until the item is carried part of its way.
func _mid_drag(hq: Node, id: String) -> void:
	hq._demo_drag(id)
	var layer: DropLayer = hq.drops
	if not await _until(func() -> bool: return layer.mode == DropLayer.Mode.CARRY, "the %s pick-up" % id):
		return
	await _frames(MID_DRAG_FRAMES)


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
	DemoSetup.queue_raid_interlude(RunManager.netrun, RunManager.config())
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
	# Main's combat end demo (ANIM-R6 B3) sets the fight one hit from its end and presses
	# SEND IT a few frames later, through one-shot frame connections.
	net._demo_combat_end(kind)
	await _until(func() -> bool: return not is_instance_valid(combat) or combat.engine.state().outcome != CombatState.Outcome.NONE, "the ending turn")
	# The replay is skipped to its end: the held outcome (DEFEATED stamp, status word, the
	# LOOT / JACK OUT verb) is the picture, not the wheel breaking mid-way.
	await _frames(2)
	if is_instance_valid(combat):
		combat.skip_motion()
	await _until(func() -> bool: return not is_instance_valid(combat) or combat.continue_shown(), "the outcome to land")
	await _frames(SETTLE_FRAMES)
	# The DISPATCH line the outcome brings is shown whole (not caught mid-typing).
	Typing.finish_all(get_tree())
	await _frames(2)


func _s_combat_victory() -> void:
	await _combat_end("win")


func _s_combat_defeat() -> void:
	await _combat_end("lose")


func _s_loot() -> void:
	var net: Node = await _netrun()
	DemoSetup.offer_loot(RunManager.netrun, ["twist", "jam", "cache"])
	net._show_current()
	await _settle(net)


func _mainframe(seed: int) -> Node:
	var net: Node = await _netrun(seed)
	DemoSetup.open_shop(RunManager.netrun)
	net._show_current()
	await _settle(net)
	return net


func _s_mainframe() -> void:
	await _mainframe(7)


func _s_mainframe_socket() -> void:
	for seed in range(7, 7 + SOCKET_SEEDS):
		var net: Node = await _mainframe(seed)
		# Main: the socket choice is an OptionButton (its list pops up); the art pass's slot
		# tiles take focus instead.
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
	push_error("review_pack: no shop with Firmware in %d seeds" % SOCKET_SEEDS)


func _s_mainframe_remove() -> void:
	var net: Node = await _mainframe(7)
	net.open_remove()
	await _settle(net)


func _s_mainframe_overwrite() -> void:
	for seed in range(7, 7 + SOCKET_SEEDS):
		var net: Node = await _mainframe(seed)
		if not (RunManager.netrun.run.shop.get("slices", []) as Array).is_empty():
			net.open_overwrite(0)
			await _frames(4)
			var view := net.get_node_or_null("SpinnerView") as SpinnerView
			if view != null:
				view.select(0)
			await _settle(net)
			return
		net.queue_free()
		await _frames(2)
		RunManager.reset()
	push_error("review_pack: no shop with slices in %d seeds" % SOCKET_SEEDS)


func _event(id: StringName) -> void:
	var net: Node = await _netrun()
	DemoSetup.open_event(RunManager.netrun, id)
	net._show_current()
	await _settle(net)


func _s_event() -> void:
	await _event(&"ev_leash_on_the_floor")


func _s_event_dispatch() -> void:
	await _event(&"ev_dispatch_early_reply")


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


## The run ends through the session's own ending (main's `DemoSetup.end_run`, as the
## netrun's `--demo-end=` flag does): "died" is the flatline, "completed" the clean exit.
func _run_end(kind: String) -> void:
	var net: Node = await _netrun()
	DemoSetup.end_run(RunManager.netrun, kind)
	net._report(RunManager.netrun.last_events)
	net._show_current()
	await _settle(net)


func _s_run_end() -> void:
	await _run_end("died")


func _s_run_end_clean() -> void:
	await _run_end("completed")


func _campaign_end(outcome: int) -> void:
	var hq: Node = await _hq_with_campaign()
	var c := RunManager.campaign
	c.story_beats_revealed = 99
	DemoSetup.end_campaign(c, outcome)
	hq.show_end()
	await _settle(hq)


func _s_campaign_won() -> void:
	await _campaign_end(CampaignState.Outcome.WON)


func _s_campaign_lost() -> void:
	await _campaign_end(CampaignState.Outcome.LOST)


func _route_page() -> Node:
	var net: Node = await _netrun()
	await _until(func() -> bool: return net.arrival_ready(), "the route camera")
	await _settle(net)
	return net


func _s_deck_view() -> void:
	var net: Node = await _route_page()
	net.open_loadout()
	await _settle(net)


func _s_card_detail() -> void:
	var net: Node = await _route_page()
	net.open_loadout()
	await _frames(4)
	var lv := net.get_node_or_null("LoadoutView")
	var deck: Variant = lv.get("_view") if lv != null else null
	if not (deck is DeckView):
		push_error("review_pack: no deck viewer")
		return
	(deck as DeckView).open_card(0)
	await _settle(net)


func _s_daemon_tray() -> void:
	var net: Node = await _netrun()
	var ids: Array = RunManager.lookup().ids_of_class(&"DaemonData")
	ids.sort()
	if not ids.is_empty():
		var first: Array[StringName] = [StringName(ids[0])]
		DemoSetup.add_daemons(RunManager.netrun, first)
	net._show_current()
	await _until(func() -> bool: return net.arrival_ready(), "the route camera")
	await _settle(net)
	net.open_daemons()
	await _settle(net)


func _s_tutorial() -> void:
	RunManager.new_campaign(7)
	Settings.tutorial_done = false
	RunManager.pending_tutorial = true
	var combat: Node = _open(COMBAT)
	await _frames(4)
	await _settle(combat)
	Settings.tutorial_done = true


func _s_jack_in() -> void:
	var hq: Node = await _hq_with_campaign()
	await _settle(hq)
	Fx.jack_in(func() -> void: pass, -1.0, "Solace Biosystems")
	await _until(func() -> bool: return Fx.connect_label.visible or not bool(Fx.get(&"_jacking")), "the jack's cover")
	await _frames(4)
	# The picture is taken with the cover up; the next screen waits for it to lift.
	_after_capture = func() -> void: await _until(func() -> bool: return not bool(Fx.get(&"_jacking")), "the jack to end")


func _s_pause_netrun() -> void:
	var net: Node = await _route_page()
	net.open_settings()
	await _settle(net)


func _s_pause_fight() -> void:
	var combat := await _fight()
	if combat == null:
		return
	combat.open_settings()
	await _settle(combat.get_parent())


## ART-2 2D: the pause menu's Quit to desktop opens its confirm (nothing is confirmed).
func _s_pause_fight_quit() -> void:
	var combat := await _fight()
	if combat == null:
		return
	combat.open_settings()
	await _settle(combat.get_parent())
	for b in get_tree().root.find_children("*", "Button", true, false):
		if (b as Button).text == tr("Quit to desktop"):
			(b as Button).pressed.emit()
			break
	await _settle(combat.get_parent())


# --- Runtime lint export -----------------------------------------------------------------

## Every visible text Control on screen with its screen rect, the rect its text covers,
## its effective font size, colour and the clipping facts the report needs. Overlap and
## contrast are judged in Python (tools/visual_qa/lint_report.py) against the PNG.
func _lint_export(screen: String, size: Vector2i) -> Dictionary:
	var out: Array = []
	_custom_draw = []
	var screen_rect := Rect2(Vector2.ZERO, Vector2(size))
	_modals = _open_modals()
	_walk(get_tree().root, out, screen_rect)
	# The type steps the size rule checks overrides against, when this build's UiTheme has
	# them (ART-0 E ports the step machinery; main before it has none: the rule is skipped).
	var theme_consts := (UiTheme as Script).get_script_constant_map()
	return {"screen": screen, "text_scale": text_scale, "viewport": [size.x, size.y],
		"floor_px": roundi(12 * text_scale), "controls": out, "custom_draw": _custom_draw,
		"type_steps": theme_consts.get("STEPS", []),
		"hero": [theme_consts.get("HERO", 0), theme_consts.get("HERO_MAX", 0)],
		# ART-1 1B: the grease pencil rule (no UI over a stroke, pencil above all UI).
		"pencil": PencilLint.violations(get_tree().root)}


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
## can't see that text.
func _draws_text(n: Node) -> bool:
	var s := n.get_script() as Script
	if s == null or not s.resource_path.begins_with("res://scripts/"):
		return false
	if not _draw_cache.has(s.resource_path):
		var src := FileAccess.get_file_as_string(s.resource_path)
		_draw_cache[s.resource_path] = src.contains("draw_string(") or src.contains("draw_multiline_string(")
	return _draw_cache[s.resource_path]


## The modals open now (main's pause menu, Options, the Daemon tray, inspect popups,
## confirm dialogs, the deck / spinner / loadout viewers and the card detail; the kit's
## modal group and full-screen scrims once ART-0 F ports them): text under one is behind
## its scrim, so the lint leaves its contrast and overlaps out (it isn't read there).
var _modals: Array[Control] = []
const MODAL_CLASSES: Array[String] = ["PauseMenu", "SettingsPanel", "DaemonTray", "InspectPopup", "ConfirmDialog", "DeckView", "SpinnerView", "LoadoutView"]
## Node names of modals that have no class of their own (main's card detail window).
const MODAL_NAMES: Array[StringName] = [&"CardDetail", &"CardDetailHolder"]
## Script class of a full-screen scrim (the art pass's kit; absent on main until ported).
const SCRIM_CLASS := "GlassScrim"
## A scrim this share of the screen (or more) is a modal's backdrop.
const MODAL_SCRIM_SHARE := 0.9


func _open_modals() -> Array[Control]:
	var out: Array[Control] = []
	var group: String = str((PageTransition as Script).get_script_constant_map().get("MODAL_GROUP", ""))
	if group != "":
		for n in get_tree().get_nodes_in_group(group):
			if n is Control and (n as Control).is_visible_in_tree():
				out.append(n as Control)
	# The jack's cover hides the whole game while it is up.
	if Fx.jack_cover != null and Fx.jack_cover.is_visible_in_tree():
		out.append(Fx.jack_cover)
	var view := Vector2(CAPTURE_SIZE)
	for n in get_tree().root.find_children("*", "Control", true, false):
		var c := n as Control
		if out.has(c) or not c.is_visible_in_tree():
			continue
		var s := c.get_script() as Script
		var cls: String = s.get_global_name() if s != null else ""
		if MODAL_CLASSES.has(cls) or MODAL_NAMES.has(c.name):
			out.append(c)
		elif cls == SCRIM_CLASS and c.get_global_rect().size.x * c.get_global_rect().size.y >= view.x * view.y * MODAL_SCRIM_SHARE:
			# A full-screen scrim is its parent's backdrop: the parent is the modal (a page
			# stage's own scrim sits behind the page's text, so only a scrim over others counts).
			var p := c.get_parent() as Control
			if p != null and not out.has(p) and _has_later_sibling_text(c):
				out.append(p)
	return out


func _has_later_sibling_text(scrim: Control) -> bool:
	return scrim.get_index() < scrim.get_parent().get_child_count() - 1


## The CanvasLayer order of `n` (0 when on the root canvas).
func _layer_of(n: Node) -> int:
	var p := n
	while p != null:
		if p is CanvasLayer:
			return (p as CanvasLayer).layer
		p = p.get_parent()
	return 0


## True when an open modal draws over `c` (it isn't part of one, and the modal is on a
## higher layer, or the same layer later in the tree).
func _under_modal(c: Control) -> bool:
	for m in _modals:
		if not is_instance_valid(m) or m == c or m.is_ancestor_of(c):
			continue
		var lm := _layer_of(m)
		var lc := _layer_of(c)
		if lm > lc or (lm == lc and m.is_greater_than(c)):
			return true
	return false


## The screen rect `c` is visible in: its rect cut by every ancestor that clips its children
## (a ScrollContainer's view, clip_contents panels). Empty when scrolled out.
func _visible_rect(c: Control, rect: Rect2) -> Rect2:
	var r := rect
	var p := c.get_parent()
	# A CanvasLayer or a Window starts its own drawing: nothing above it clips this text.
	while p != null and not (p is CanvasLayer) and not (p is Window):
		if p is Control and ((p as Control).clip_contents or p is ScrollContainer):
			var pr := _screen_rect_of(p as Control, Rect2(Vector2.ZERO, (p as Control).size))
			r = r.intersection(pr)
			if r.size.x <= 0.0 or r.size.y <= 0.0:
				return Rect2()
		p = p.get_parent()
	return r


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
	if w != null and w != c.get_tree().root:
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
	# The on-screen size is the font size times every ancestor's scale (a legend scaled down
	# to its room, the pad's focus scale).
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
			# The text sits inside the label's own box (a sticker's paper, SAVED): the ink is
			# measured inside its content margins, so the ring round it reads the box.
			var sb := l.get_theme_stylebox(&"normal")
			var ml := sb.get_margin(SIDE_LEFT) if sb != null else 0.0
			var mt := sb.get_margin(SIDE_TOP) if sb != null else 0.0
			var inner := l.size - (sb.get_minimum_size() if sb != null else Vector2.ZERO)
			var w := minf(widest, inner.x)
			var h := minf(line_h * maxi(visible_lines, 1), inner.y)
			var x := ml
			match l.horizontal_alignment:
				HORIZONTAL_ALIGNMENT_CENTER:
					x = ml + (inner.x - w) * 0.5
				HORIZONTAL_ALIGNMENT_RIGHT:
					x = ml + inner.x - w
			var y := mt
			match l.vertical_alignment:
				VERTICAL_ALIGNMENT_CENTER:
					y = mt + (inner.y - h) * 0.5
				VERTICAL_ALIGNMENT_BOTTOM:
					y = mt + inner.y - h
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
		"scale": absf(scale.y),
		"under_modal": _under_modal(c),
		"box_color": _box_color(c),
		"visible_rect": _vr(c, rect),
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


## The colour of the opaque box a Label draws behind its own words (a sticker's paper:
## SAVED), or [] when it has none: the text's real background.
func _box_color(c: Control) -> Array:
	if not (c is Label):
		return []
	var sb := c.get_theme_stylebox(&"normal") as StyleBoxFlat
	if sb == null or not sb.draw_center or sb.bg_color.a < 0.9:
		return []
	return [sb.bg_color.r, sb.bg_color.g, sb.bg_color.b]


func _vr(c: Control, rect: Rect2) -> Array:
	var v := _visible_rect(c, rect)
	return [v.position.x, v.position.y, v.size.x, v.size.y]


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
