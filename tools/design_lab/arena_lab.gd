extends Control
## Design lab (dev tool, not exported): the combat screen with ART-2 2B's wheel attachments and arena
## (ART_BIBLE v2 §3.9, §3.11, §3.13, §3.14, §3.17, §3.21), on a fixture, captured to a PNG for review
## next to `docs/art_reference/hud/round41_wheel_stack/combat_typical_v4` / `combat_worst_case_v4`.
## It sets up a real fight through the combat scene and then dresses the fight's state directly
## (drones, satellites, firmware, Daemons): a lab, never game code.
##
## Run (windowed only, through tools/run_windowed.py):
##   res://tools/design_lab/arena_lab.tscn -- --corp=meridian --boss --day --fixture=typical|worst|none
##       --hover=spin --bloom --won --scale=1.6 --shot=<abs png> --frames=40
##       --phase=2 (FIX-REDS: the boss in that phase: its HP under the threshold, its needles)
##       --scales=1.0,1.6,2.0 (one shot per text scale in one launch: <shot>_<scale>.png)

const COMBAT := preload("res://scenes/combat/combat_scene.tscn")
const BOSSES := {&"meridian": &"the_manifest", &"solace": &"renewal_engine", &"halcyon": &"civic_core",
	&"orbital": &"commons_array", &"rebel_cell": &"dispatch_core"}
const REGULARS := {&"meridian": &"cargo_hauler", &"solace": &"account_manager", &"halcyon": &"parking_warden",
	&"orbital": &"ground_control", &"rebel_cell": &"cell_informant"}
const DRONE := &"botnet_drone"
const SAT_TEMPLATES: Array[StringName] = [&"care_drone", &"civic_drone", &"courier_drone", &"echo_drone"]
const FIRMWARE: Array[StringName] = [&"leech", &"overvolt", &"hardened", &"mirror", &"burner", &"power_cell"]
const DAEMONS: Array[StringName] = [&"clean_signal", &"cascade", &"botnet_seed", &"twin_pointer", &"zero_day", &"kernel_sync", &"scrubber"]
const SPIN_CARD := &"heavy_spin"

var _args := {}
var _scene: Control = null
var _frames := 0
var _scales: PackedStringArray = []


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		_args[kv[0]] = kv[1] if kv.size() > 1 else "1"
	if _args.has("scales"):
		_scales = String(_args["scales"]).split(",", false)
		_args["scale"] = _scales[0]
	_start()


func _start() -> void:
	if _args.has("scale"):
		Settings.text_scale = float(_args["scale"])
	var corp := StringName(_args.get("corp", "meridian"))
	var camp := CampaignState.new()
	camp.corporation_id = corp
	camp.runs_started = 1 if _args.has("day") else 0
	RunManager.campaign = camp
	Settings.tutorial_done = true  # the lab's own user:// (run_windowed): no tutorial over the fight
	_scene = COMBAT.instantiate()
	_scene.auto_start = false
	add_child(_scene)
	var enemy: StringName = BOSSES[corp] if _args.has("boss") else REGULARS[corp]
	_scene.start_fight(enemy, 7)
	_dress.call_deferred()


func _dress() -> void:
	var engine = _scene.engine
	var st: CombatState = engine.state()
	var lookup: ContentLookup = engine.resolver.lookup
	var fixture := String(_args.get("fixture", "typical"))
	if fixture != "none":
		var boss := st.enemies[0]
		var n_player := st.player.wheel.slice_count if fixture == "worst" else 2
		var n_enemy := boss.wheel.slice_count if fixture == "worst" else 1
		for i in n_player:
			if st.satellite_at(st.player.id, i) == null:
				_dock(st, st.player, lookup.get_content(DRONE) as EnemyData, i)
		for i in n_enemy:
			if st.satellite_at(boss.id, i) == null:
				_dock(st, boss, lookup.get_content(SAT_TEMPLATES[i % SAT_TEMPLATES.size()]) as EnemyData, i)
		var n_fw := st.player.wheel.slice_count if fixture == "worst" else 2
		for i in n_fw:
			st.player.wheel.slot_firmware_ids[i] = FIRMWARE[i % FIRMWARE.size()]
		if fixture == "worst":
			for i in boss.wheel.slice_count:
				boss.wheel.slot_firmware_ids[i] = FIRMWARE[(i + 2) % FIRMWARE.size()]
		st.daemon_ids.clear()
		for k in (DAEMONS.size() if fixture == "worst" else 4):
			st.daemon_ids.append(DAEMONS[k])
	if _args.has("phase"):
		var foe := st.enemies[0]
		var data := lookup.get_content(foe.source_id) as EnemyData
		var n := int(_args["phase"])
		if data != null and n >= 2 and n - 2 < data.phases.size():
			var ph := data.phases[n - 2]
			foe.phase_index = n - 1
			foe.hp = roundi(foe.max_hp * (ph.hp_threshold_pct - 0.05))
			if not ph.pointer_ticks.is_empty():
				foe.wheel.pointer_ticks = ph.pointer_ticks.duplicate()
	if _args.has("hover"):
		st.hand[0] = SPIN_CARD
	_scene._refresh(st)
	if _args.has("bloom"):
		for v in _scene._views():
			v.attachments.dock.force_bloom = true
	if _args.has("hover"):
		_scene._preview_card(0)
	if _args.has("won"):
		for e in st.enemies:
			e.hp = 0
		_scene._refresh(st)
		_scene.arena_backdrop.play_won(true)


func _dock(st: CombatState, owner: CombatantState, data: EnemyData, slot: int) -> void:
	if data == null:
		return
	var d := EffectInterpreter.make_combatant(data, StringName("%s_lab_%d" % [owner.id, slot]), true)
	d.is_player = owner.is_player
	d.host_id = owner.id
	d.dock_slot = slot
	d.hp = maxi(1, d.max_hp - slot % 3)
	if d.wheel != null:
		d.wheel.rotation = (slot * 7) % RC.TICKS
	if owner.is_player:
		st.drones.append(d)
	else:
		st.enemies.append(d)


func _process(_delta: float) -> void:
	_frames += 1
	if _frames == int(_args.get("frames", "40")) and _args.has("shot"):
		var img := get_viewport().get_texture().get_image()
		var path := String(_args["shot"])
		if not _scales.is_empty():
			path = "%s_%s.png" % [path.get_basename(), String(_args["scale"])]
		DirAccess.make_dir_recursive_absolute(path.get_base_dir())
		img.save_png(path)
		print("arena_lab: saved ", path)
		var at := _scales.find(String(_args["scale"]))
		if at >= 0 and at + 1 < _scales.size():
			_args["scale"] = _scales[at + 1]
			_scene.queue_free()
			_frames = 0
			_start.call_deferred()
			return
		get_tree().quit()
