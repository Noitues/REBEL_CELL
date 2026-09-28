extends Node
## Playtest storyboard (H20, for the naive-player reviews): plays a fixed path through the
## game and saves a screenshot at every step, so a reviewer who has never seen the game
## can say what they understand and what they would click. Dev tool: not exported
## (tools/* is excluded), runs with a renderer (not headless), uses a private test save
## slot so the designer's profile is never touched.
##
##   godot --path . --resolution 1280x720 res://tools/playtest/storyboard.tscn -- --out=<dir> [--scramble] [--pad] [--scale=1.6]
##
## --scramble turns on Godot's pseudolocalisation (accented, stretched, mirrored text) for
## everything drawn by Controls, for the "cannot read English" review. --pad shows pad hints.

const SLOT := "gut_storyboard"
const TITLE := preload("res://scenes/menu/title_scene.tscn")
const HQ := preload("res://scenes/hq/hq_scene.tscn")
const NETRUN := preload("res://scenes/netrun_map/netrun_scene.tscn")
## Frames to let a screen settle before its picture.
const SETTLE_FRAMES := 12

var out_dir: String = "user://storyboard"
var _step: int = 0
var _scale_before: float = 1.0
## Frames the storyboard waits for a fight to open after the route move.
const FIGHT_WAIT_FRAMES := 600
## The storyboard's own settings file.
const STORYBOARD_SETTINGS := "user://storyboard_settings.json"
var _shots: PackedStringArray = []


func _ready() -> void:
	var scramble := false
	var pad := false
	var scale := 1.0
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out_dir = a.trim_prefix("--out=")
		elif a == "--scramble":
			scramble = true
		elif a == "--pad":
			pad = true
		elif a.begins_with("--scale="):
			scale = float(a.trim_prefix("--scale="))
	DirAccess.make_dir_recursive_absolute(out_dir)
	if scramble:
		ProjectSettings.set_setting("internationalization/pseudolocalization/replace_with_accents", true)
		ProjectSettings.set_setting("internationalization/pseudolocalization/double_vowels", true)
		ProjectSettings.set_setting("internationalization/pseudolocalization/fake_bidi", true)
		ProjectSettings.set_setting("internationalization/pseudolocalization/override", true)
		TranslationServer.pseudolocalization_enabled = true
		TranslationServer.reload_pseudolocalization()
	# Anything saved during the run goes to a file of its own, never the player's (H24).
	Settings.path = STORYBOARD_SETTINGS
	_scale_before = Settings.text_scale
	if not is_equal_approx(scale, _scale_before):
		Settings.text_scale = scale  # this run only: not saved
		Settings.changed.emit()
	Settings.pad_active = pad
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	await _run()
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	Settings.text_scale = _scale_before
	var f := FileAccess.open(out_dir.path_join("index.txt"), FileAccess.WRITE)
	if f != null:
		f.store_string("\n".join(_shots))
		f.close()
	print("STORYBOARD DONE %d shots in %s" % [_shots.size(), ProjectSettings.globalize_path(out_dir)])
	get_tree().quit()


func _settle(frames: int = SETTLE_FRAMES) -> void:
	for i in frames:
		await get_tree().process_frame


func _shot(label: String, what: String) -> void:
	await _settle()
	_step += 1
	var name := "%02d_%s.png" % [_step, label]
	var img := get_viewport().get_texture().get_image()
	if img != null:
		img.save_png(out_dir.path_join(name))
	_shots.append("%s\t%s" % [name, what])


func _open(scene: PackedScene) -> Node:
	var n := scene.instantiate()
	get_tree().root.add_child(n)
	return n


func _close(n: Node) -> void:
	if is_instance_valid(n):
		n.queue_free()
	await _settle(2)


func _run() -> void:
	await _settle(1)  # the root is still adding its children during _ready
	# 1. Title. H24 S13: its Continue line shows this storyboard's own campaign (private
	# slot), the one its HQ shots show, not the designer's newest slot (Heat 14 vs 0).
	RunManager.new_campaign(7)
	RunManager.autosave()
	var title: Node = TITLE.instantiate()
	title.continue_slot = SLOT
	get_tree().root.add_child(title)
	await _shot("title", "The game's first screen.")
	await _close(title)
	# 2. HQ with a new campaign, then the city Grid.
	var hq: Node = _open(HQ)
	await _settle(2)
	hq.new_campaign(7)
	await _shot("hq", "Home base after starting a new campaign.")
	hq.show_grid()
	await _shot("grid", "The city map (the Grid).")
	# 3. A raid on the home network.
	var c := RunManager.campaign
	var grid_data := RunManager.corporation.city_grid
	var first: StringName = grid_data.get_site(grid_data.home_site_id).links[0]
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	c.armory = [&"turret", &"ice_lock", &"decoy"]
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	hq.show_raid()
	await _shot("raid_setup", "Defending against a raid: placing defences.")
	c.pending_raids.clear()
	await _close(hq)
	Dialogue.clear()
	# 4. A netrun: the route, a fight and its moments.
	var net: Node = _open(NETRUN)
	await _settle(2)
	net.start_run(1)
	await _shot("route", "A run: choosing where to go next.")
	net.enter_node(RunManager.netrun.available_nodes()[0])
	# The route move plays first (Animation pass ANIM-5), then the fight opens: wait for it.
	for i in FIGHT_WAIT_FRAMES:
		if net.combat_scene != null:
			break
		await get_tree().process_frame
	await _settle(4)
	var combat: Control = net.combat_scene
	if combat == null:
		push_error("storyboard: the fight never opened")
	if combat != null:
		await _shot("fight", "A fight starts.")
		combat._preview_card(0)
		await _shot("fight_card_hover", "The mouse is over the first card in the hand.")
		for i in combat.engine.state().hand.size():
			if CardTargeting.options(combat.engine.resolver, combat.engine.state(), i).size() > 1:
				combat.select_card(i)
				await _shot("fight_aiming", "A card was clicked and is waiting to be aimed.")
				combat.cancel_selection()
				break
		combat.nudge_wheel(&"player", 1)
		await _shot("fight_after_nudge", "The player clicked the right arrow above their wheel once.")
		combat.end_turn()
		await _shot("fight_resolving", "The player pressed SEND IT once; the turn is still playing out.")
		for i in FIGHT_WAIT_FRAMES:
			if not combat.motion_busy():
				break
			await get_tree().process_frame
		await _shot("fight_after_send_it", "The same turn after it has finished playing out.")
		# Spend RAM the honest way (respins) until the next one is refused.
		for i in 8:
			if combat.engine.state().ram < combat.engine.resolver.config.respin_ram_cost:
				break
			combat.respin()
		combat.respin()
		await _shot("fight_refused", "The player tried to respin with no RAM.")
	# 5. The shop, an event and a reward.
	RunManager.netrun.run.cycles = 120
	RunManager.netrun._open_shop()
	net._show_current()
	await _shot("modem", "A shop node.")
	var run := RunManager.netrun.run
	run.event_id = &"ev_leash_on_the_floor"
	run.phase = RunState.Phase.EVENT
	net._show_current()
	await _shot("event", "A story event with choices.")
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.phase = RunState.Phase.REWARD
	net._show_current()
	await _shot("loot", "Picking a reward.")
	await _close(net)
	Dialogue.clear()
