extends Node
## ART-11 4D capture lab (dev tool, not exported): walks the campaign's end states in ONE
## windowed launch and writes a picture of each, to read next to the references in
## `docs/art_reference/campaign_end/`. For each corporation: the campaign lost lock (the tear,
## the wipe with its padlocks, the notice with the curling stickers, the end state), the cut to
## the audit dossier (the cover opening, the open file); then a won dossier; then the run ends
## (FLATLINED, JACKED OUT, HOME FELL). A demo campaign in the lab's own slot; never headless.
##
##   python tools/run_windowed.py --log <file> -- res://tools/design_lab/campaign_end_lab.tscn
##       -- --out=<abs dir> [--corps=halcyon,meridian] [--what=lost,won,abandoned,run] [--scales=1.0,2.0]
##       [--reduce-effects]

const HQ := preload("res://scenes/hq/hq_scene.tscn")
const NETRUN := preload("res://scenes/netrun_map/netrun_scene.tscn")
const SLOT := "lab_4d"
const CORPS: Array[StringName] = [&"halcyon", &"meridian", &"solace", &"orbital", &"rebel_cell"]
## Lock moments to picture (s into the lock) and the dossier's (s into its motion).
const LOCK_AT: Array[float] = [0.25, 1.1, 2.6, 4.2]
const DOSSIER_AT: Array[float] = [0.45]
## A won file's CORP DOWN beat (s into the dossier's motion): the poster in, the pencil X, the
## sticker's slap, at rest.
const WON_AT: Array[float] = [1.2, 1.5, 1.75, 2.0, 2.3]
## The demo campaign's story: Sites claimed, its Heat and thresholds, runs, raids.
const CLAIMS := 3
const DEMO_HEAT := 82
const DEMO_MARKS: Array[int] = [25, 50, 75]
const DEMO_SCHEMATICS := 2000
const DEMO_SCHEMATICS_LEFT := 37
const MAX_WAIT_FRAMES := 1200
const SETTLE_FRAMES := 20

var out_dir := ""
var _shots := 0


func _ready() -> void:
	var corps := CORPS.duplicate()
	var what := ["lost", "won", "run"]
	var scales: Array[float] = [1.0]
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out_dir = a.trim_prefix("--out=")
		elif a.begins_with("--corps="):
			corps.clear()
			for c in a.trim_prefix("--corps=").split(","):
				corps.append(StringName(c))
		elif a.begins_with("--what="):
			what = Array(a.trim_prefix("--what=").split(","))
		elif a.begins_with("--scales="):
			scales.clear()
			for v in a.trim_prefix("--scales=").split(","):
				scales.append(float(v))
		elif a == "--reduce-effects":
			Settings.set_reduce_effects(true)
			Fx.apply_settings()
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	_unlock_all()
	_run_scales.call_deferred(corps, what, scales)


## Every end state at each text size in turn (one launch), then quits.
func _run_scales(corps: Array, what: Array, scales: Array[float]) -> void:
	var was := Settings.text_scale
	for sc in scales:
		Settings.text_scale = sc
		Settings.changed.emit()
		_tag = "s%.1f_" % sc
		await _run(corps, what)
	Settings.text_scale = was
	print("lab4d: done, %d pictures" % _shots)
	RunManager.delete_save()
	get_tree().quit()


var _tag := ""


func _run(corps: Array, what: Array) -> void:
	await _frames(5)
	if "lost" in what:
		for corp in corps:
			await _lost(corp)
	if "won" in what:
		for corp in corps.slice(0, 2):
			await _won(corp)
	if "abandoned" in what:
		for corp in corps.slice(0, 1):
			await _abandoned(corp)
	if "run" in what:
		for kind in ["died", "completed", "aborted"]:
			await _run_end(kind)


func _unlock_all() -> void:
	var lookup := RunManager.lookup()
	for id in lookup.ids_of_class(&"CorporationData"):
		var u := CampaignRules.unlock_for(lookup, lookup.get_content(id))
		if u != null:
			RunManager.profile.add_unlock(u.id)


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


## The longest of the next `n` frames (ms, wall clock between frames drawn).
func _longest_frame(n: int) -> float:
	var worst := 0.0
	var t := Time.get_ticks_usec()
	for i in n:
		await RenderingServer.frame_post_draw
		var now := Time.get_ticks_usec()
		worst = maxf(worst, (now - t) / 1000.0)
		t = now
	return worst


## Frames measured after the lock's cut (the switch lands in the first of them).
const SWITCH_FRAMES := 12
var _hold_ms := 0.0


func _shot(name: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png(out_dir.path_join("%02d_%s%s.png" % [_shots, _tag, name]))
	_shots += 1
	print("lab4d: shot %s" % name)


## A demo campaign against `corp` with a network, a crew (one lost), an Armory, Heat and runs.
func _campaign(hq: Node, corp: StringName, outcome: int) -> void:
	hq.new_campaign(4, 0, RunManager.DEFAULT_HOME, RunManager.DEFAULT_CLASS, corp)
	var c := RunManager.campaign
	if c.corporation_id != corp:
		# REBEL_CELL is generated from a profile the lab has not played: its house style is
		# previewed on the campaign that came up (lab only; the screens read the id's style).
		print("lab4d: %s not available, got %s; previewing %s's style on it" % [corp, c.corporation_id, corp])
		c.corporation_id = corp
	var cfg := RunManager.config()
	var lookup := RunManager.lookup()
	DemoSetup.set_schematics(c, DEMO_SCHEMATICS)
	for i in CLAIMS:
		var sites := RunManager.launchable_sites()
		for sd in sites:
			if not c.grid.is_claimed(sd.id):
				CampaignRules.on_run_completed(c, RunManager.corporation, cfg, hq._demo_run(sd.id))
				var err := CampaignRules.claim_error(c, RunManager.corporation, cfg, lookup, sd.id, &"firewall_relay")
				if err != "":
					print("lab4d: claim %s: %s" % [sd.id, err])
				CampaignRules.claim(c, RunManager.corporation, cfg, lookup, sd.id, &"firewall_relay")
				break
	DemoSetup.set_schematics(c, DEMO_SCHEMATICS_LEFT)
	for cls in [&"ghost", &"rigger"]:
		var cd := lookup.get_content(cls) as ClassData
		if cd != null:
			c.recruit(cd)
	if c.roster.size() > 1:
		c.roster[1].alive = false
		c.roster[0].runs_completed = 5
		c.roster[0].rank = 2
	DemoSetup.set_armory(c, [&"turret", &"ice_lock", &"decoy", &"flak_array"] as Array[StringName])
	c.heat = DEMO_HEAT
	c.thresholds_fired.assign(DEMO_MARKS)
	c.runs_started = 8
	c.runs_completed = 6
	c.deaths = 1
	c.raids_won = 3
	c.raids_lost = 1
	c.story_beats_revealed = 2
	DemoSetup.end_campaign(c, outcome)


func _lost(corp: StringName) -> void:
	RunManager.campaign = null  # a fresh HQ, never the last demo's campaign end
	RunManager.delete_save()
	var hq: Node = HQ.instantiate()
	add_child(hq)
	await _frames(3)
	await _campaign(hq, corp, CampaignState.Outcome.LOST)
	hq.show_end()
	var lock: RansomLock = hq.end_lock
	if lock == null:
		print("lab4d: no lock for %s" % corp)
	else:
		var waited := 0
		while not lock.started and waited < MAX_WAIT_FRAMES:
			await get_tree().process_frame
			waited += 1
		for t in LOCK_AT:
			while is_instance_valid(lock) and lock.elapsed < t and not lock.done:
				await get_tree().process_frame
			await _shot("%s_lock_%.1f" % [corp, t])
		if is_instance_valid(lock):
			lock.complete_motion()
			_hold_ms = await _longest_frame(2)
			await _shot("%s_lock_end" % corp)
			lock.cut()
		# 12p: the cut's switch to the dossier (built in the hold): the longest frame round it.
		var worst := 0.0
		var t := Time.get_ticks_usec()
		while is_instance_valid(hq.end_lock):
			await RenderingServer.frame_post_draw
			var now := Time.get_ticks_usec()
			worst = maxf(worst, (now - t) / 1000.0)
			t = now
		worst = maxf(worst, await _longest_frame(SWITCH_FRAMES))
		print("lab4d: switch %s longest_frame_ms=%.1f (hold build frame %.1f ms)" % [corp, worst, _hold_ms])
	var d := hq._panel as AuditDossier
	if d != null:
		for t in DOSSIER_AT:
			while is_instance_valid(d) and d.elapsed < t and d.motion_running():
				await get_tree().process_frame
			await _shot("%s_dossier_%.2f" % [corp, t])
		while is_instance_valid(d) and d.motion_running():
			await get_tree().process_frame
		await _frames(SETTLE_FRAMES)
		await _shot("%s_dossier" % corp)
	hq.queue_free()
	await _frames(3)


func _won(corp: StringName) -> void:
	await _ended(corp, CampaignState.Outcome.WON, "won")


## M14 parity END: a campaign the Cell abandoned (a loss in its own words; no lock).
func _abandoned(corp: StringName) -> void:
	await _ended(corp, CampaignState.Outcome.ABANDONED, "abandoned")


## A won or abandoned end: the dossier (a won file: a frame strip of its CORP DOWN beat,
## WON_AT s into its motion), then at rest.
func _ended(corp: StringName, outcome: int, tag: String) -> void:
	RunManager.campaign = null  # a fresh HQ, never the last demo's campaign end
	RunManager.delete_save()
	var hq: Node = HQ.instantiate()
	add_child(hq)
	await _frames(3)
	await _campaign(hq, corp, outcome)
	hq.show_end()
	var d := hq._panel as AuditDossier
	if outcome == CampaignState.Outcome.WON:
		for t in WON_AT:
			while d != null and is_instance_valid(d) and d.elapsed < t and d.motion_running():
				await get_tree().process_frame
			await _shot("%s_won_%.2f" % [corp, t])
	while d != null and is_instance_valid(d) and d.motion_running():
		await get_tree().process_frame
	await _frames(SETTLE_FRAMES)
	await _shot("%s_%s" % [corp, tag])
	hq.queue_free()
	await _frames(3)


func _run_end(kind: String) -> void:
	RunManager.new_campaign(7)
	var net: Node = NETRUN.instantiate()
	add_child(net)
	await _frames(3)
	net.start_run(1)
	await _frames(SETTLE_FRAMES)
	if kind == "aborted":
		RunManager.netrun.run.outcome = RunState.Outcome.ABORTED
		RunManager.netrun.run.phase = RunState.Phase.ENDED
		net._show_end()
	else:
		DemoSetup.end_run(RunManager.netrun, kind)
		net._report(RunManager.netrun.last_events)
		net._show_current()
	await _frames(SETTLE_FRAMES * 3)
	await _shot("run_%s" % kind)
	net.queue_free()
	await _frames(3)
