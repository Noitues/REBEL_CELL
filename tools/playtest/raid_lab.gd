extends Node
## Raid lab (raid review 2026-10-21): builds a campaign in code at the edge of a Heat raid and
## walks the whole raid flow through the HQ scene's public methods, saving a screenshot at each
## moment: Heat below the threshold, the crossing (the raid is queued by the real Heat rule),
## the HQ arrival with its warning, the Grid, the raid setup (bare and defended), the playout at
## several steps, its end, the report, and the HQ and Grid afterwards. Dev tool: not exported
## (tools/* is excluded), needs a renderer, run only through tools/run_windowed.py. Uses a private
## save slot (never the player's) unless --save-default is given for a blackbox session's own
## private APPDATA.
##
##   python tools/run_windowed.py --log <f> -- --resolution 1280x720 res://tools/playtest/raid_lab.tscn \
##       -- --out=<abs dir> [--variant=hold|lose|breach] [--scramble] [--save-default]
##
## hold:   Heat 22 -> 26 (raid_heat_25), a small network, one turret placed, one operative stationed.
## lose:   Heat 72 -> 76 (raid_heat_75, +25 % strength), a wider network, nothing placed.
## breach: as lose, with the home server at a few integrity points.
## --save-default: stop after the crossing and save the campaign into the default slot (a
## blackbox session then plays it from the title's Continue). No shots after that point.

const HQ := preload("res://scenes/hq/hq_scene.tscn")
const SLOT := "gut_raid_lab"
const LAB_SETTINGS := "user://raid_lab_settings.json"
const SETTLE_FRAMES := 45
const WAIT_FRAMES := 1200
const PLAYOUT_FRAME_LIMIT := 7200
const PLAYOUT_MAX_SNAPS := 9
const PLAYOUT_BEAT_FRAMES := 100

var out_dir := "user://raid_lab"
var variant := "hold"
var save_default := false
## --size=N: the network's node count (default 2 for hold, 5 otherwise). 9 gives a lose raid with a node DOWN, one
## TAKEN and home hit.
var size_override := 0
var _step := 0
var _shots: PackedStringArray = []


func _ready() -> void:
	var scramble := false
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out_dir = a.trim_prefix("--out=")
		elif a.begins_with("--variant="):
			variant = a.trim_prefix("--variant=")
		elif a == "--scramble":
			scramble = true
		elif a == "--save-default":
			save_default = true
		elif a.begins_with("--size="):
			size_override = int(a.trim_prefix("--size="))
	DirAccess.make_dir_recursive_absolute(out_dir)
	if scramble:
		ProjectSettings.set_setting("internationalization/pseudolocalization/replace_with_accents", true)
		ProjectSettings.set_setting("internationalization/pseudolocalization/double_vowels", true)
		ProjectSettings.set_setting("internationalization/pseudolocalization/fake_bidi", true)
		ProjectSettings.set_setting("internationalization/pseudolocalization/override", true)
		TranslationServer.pseudolocalization_enabled = true
		TranslationServer.reload_pseudolocalization()
	Settings.path = LAB_SETTINGS
	RunManager.save_slot = RunManager.DEFAULT_SLOT if save_default else SLOT
	RunManager.scene_switching_enabled = false
	if not save_default:
		RunManager.delete_save()
	RunManager.reset()
	await _run()
	if not save_default:
		RunManager.delete_save()
		RunManager.save_slot = RunManager.DEFAULT_SLOT
	var f := FileAccess.open(out_dir.path_join("index.txt"), FileAccess.WRITE)
	if f != null:
		f.store_string("\n".join(_shots))
		f.close()
	print("RAID LAB DONE %d shots in %s" % [_shots.size(), ProjectSettings.globalize_path(out_dir)])
	get_tree().quit()


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _until(cond: Callable, limit: int = WAIT_FRAMES) -> bool:
	for i in limit:
		if cond.call():
			return true
		await get_tree().process_frame
	return false


func _shot(label: String, what: String, settle: int = SETTLE_FRAMES) -> void:
	await _frames(settle)
	_step += 1
	var name := "%02d_%s.png" % [_step, label]
	var img := get_viewport().get_texture().get_image()
	if img != null:
		img.save_png(out_dir.path_join(name))
	_shots.append("%s\t%s" % [name, what])


func _run() -> void:
	await _frames(1)
	var hq: Node = HQ.instantiate()
	get_tree().root.add_child(hq)
	await _frames(2)
	hq.new_campaign(7)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	var lookup := RunManager.lookup()
	var classes: Array[ClassData] = []
	for id in [&"breaker", &"ghost", &"rigger"]:
		var cls := lookup.get_content(id) as ClassData
		if cls != null:
			classes.append(cls)
	if not classes.is_empty():
		DemoSetup.roster_of(c, classes)
	DemoSetup.set_schematics(c, 60)
	var size := size_override if size_override > 0 else (2 if variant == "hold" else 5)
	var types: Array[StringName] = [&"safehouse", &"firewall_relay", &"vault_terminal", &"relay", &"proxy_relay"]
	for i in size:
		var open := CampaignRules.launchable_sites(c, corp, cfg)
		if open.is_empty():
			break
		CampaignRules.on_run_completed(c, corp, cfg, hq._demo_run(open[0].id))
		CampaignRules.claim(c, corp, cfg, lookup, open[0].id, types[i % types.size()])
	c.pending_raids.clear()
	var from_heat := 22 if variant == "hold" else 72
	DemoSetup.set_heat(c, from_heat)
	if variant == "breach":
		c.grid.home_integrity = 6
	DemoSetup.set_armory(c, [&"turret", &"ice_lock", &"decoy"] as Array[StringName])
	hq.show_hq()
	await _until(func() -> bool: return hq.arrival_ready())
	await _shot("hq_before", "HQ, Heat %d, just under the threshold." % from_heat)
	hq.toggle_heat_terminal()
	await _shot("heat_terminal", "The Heat terminal opened from the HUD (Heat %d)." % from_heat)
	hq.close_heat_terminal()
	# The crossing: the real Heat rule queues the raid.
	HeatRules.add_heat(c, 4, cfg, "Server Rack")
	if save_default:
		RunManager.autosave()
		print("RAID LAB saved Heat %d, %d raid(s) pending, into the default slot" % [c.heat, c.pending_raids.size()])
		return
	hq.show_hq()
	await _until(func() -> bool: return hq.arrival_ready())
	await _shot("hq_raid_pending_toast", "HQ after the run that crossed the threshold: the arrival, warning toast.", 20)
	await _shot("hq_raid_pending", "HQ a few seconds later.", 150)
	hq.show_grid()
	await _until(func() -> bool: return hq.arrival_ready())
	await _shot("grid_raid_pending", "The city Grid with a raid pending.")
	hq.show_raid()
	await _until(func() -> bool: return hq.arrival_ready())
	await _shot("setup_bare", "Raid setup, nothing placed.", 90)
	if variant == "hold":
		var claimed := c.grid.claimed_ids()
		for id in claimed:
			if id != c.grid.home_site_id and c.grid.node_type_of(id) == &"safehouse" and not c.roster.is_empty():
				CampaignRules.station(c, lookup, c.roster[0].id, id)
		CampaignRules.deploy_asset(c, cfg, lookup, 0, claimed[claimed.size() - 1])
		hq.show_raid()
		await _until(func() -> bool: return hq.arrival_ready())
		await _shot("setup_defended", "Raid setup after a turret is placed and an operative stationed.", 90)
	# RAID-FIX B3: a target picked and the first defense card pointed at: its effect in words.
	for id in c.grid.claimed_ids():
		if id != c.grid.home_site_id and c.grid.is_active_node(id):
			hq.select_target(id)
			break
	await _until(func() -> bool: return hq.arrival_ready())
	await _frames(30)
	hq.point_card(0)
	await _shot("setup_card_effect", "Raid setup: a target picked, the first defense card pointed at (effect words).", 30)
	hq.show_if_placed(0)
	await _shot("setup_if_placed", "Raid setup: the what-if for the first defense card.", 30)
	hq.request_start_defense()
	await _frames(20)
	if hq.playout == null:
		await _shot("start_confirm", "After pressing START DEFENSE (a confirm?).", 10)
		var d: Node = hq.get("_defense_confirm")
		if d != null and is_instance_valid(d):
			d.yes_button.pressed.emit()
		await _frames(10)
	# RAID-VIS F1: the playout at 1x, timed from START DEFENSE to the end; a frame at each step that hurts (a node
	# DOWN or TAKEN, home hit) once its beats have landed, and the first steps.
	var flat: Array = []
	if hq.playout != null and is_instance_valid(hq.playout):
		for g in hq.playout._steps:
			flat.append_array(g)
	var planned := RaidBeats.playout_seconds(flat)
	var started_ms := Time.get_ticks_msec()
	var seen := 0
	var snaps := 0
	for i in PLAYOUT_FRAME_LIMIT:
		if hq.playout == null or not is_instance_valid(hq.playout) or hq.playout.is_done() or snaps >= PLAYOUT_MAX_SNAPS:
			break
		await get_tree().process_frame
		var cur: int = hq.playout.current_step()
		if cur <= seen:
			continue
		seen = cur
		var key := false
		for e in hq.playout._steps[cur - 1]:
			if String(e.get("type", "")) in ["down", "taken", "home_hit"]:
				key = true
		if key or cur == 2 or cur == 3:
			await _frames(PLAYOUT_BEAT_FRAMES if key else 30)
			if hq.playout == null or not is_instance_valid(hq.playout):
				break
			await _shot("playout_step%02d" % cur, "Playout at step %d of %d%s." % [hq.playout.current_step(), hq.playout.steps_total(), " (a loss lands)" if key else ""], 1)
			snaps += 1
	if hq.playout != null and is_instance_valid(hq.playout):
		await _until(func() -> bool: return not is_instance_valid(hq.playout) or hq.playout.is_done(), 3600)
		var measured := float(Time.get_ticks_msec() - started_ms) / 1000.0
		print("RAID LAB playout %s: planned %.1f s, measured %.1f s at 1x (%d steps)" % [variant, planned, measured, seen])
		_shots.append("playout_length\t%s planned %.1f s measured %.1f s at 1x" % [variant, planned, measured])
		await _shot("playout_end", "Playout at its end.", 30)
		await _shot("playout_end_later", "Playout end, 4 s later.", 240)
	if c.is_over():
		await _shot("campaign_end", "The campaign is over.", 120)
		return
	hq.show_raid_summary()
	await _shot("report", "The raid report.", 90)
	hq._leave_raid_report()
	await _until(func() -> bool: return hq.arrival_ready())
	await _shot("hq_after", "HQ after the raid.", 90)
	hq.show_grid()
	await _until(func() -> bool: return hq.arrival_ready())
	await _shot("grid_after", "The Grid after the raid.", 90)
