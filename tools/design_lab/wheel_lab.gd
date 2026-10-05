extends Control
## Wheel lab (dev tool, not exported; ART-2 2A): the wheel stack on the real views, for windowed
## captures next to the references (`docs/art_reference/hud/round41_wheel_stack/combat_*_v4.jpg`,
## `wheel/round17_corp_wheels/*`, `wheel/round18_corp_wheels/*`).
##
## Run:      python tools/run_windowed.py --log <f> -- res://tools/design_lab/wheel_lab.tscn
##             --resolution 1600x900 --write-movie <dir>/f.png --fixed-fps 30 --quit-after 40 -- --case=typical
## Cases (`--case=`):
##   typical  the combat scene vs THE MANIFEST (Breaker), one status, one firmware chip.
##   worst    the same with a status (and ×N stacks) on every slice of both wheels.
##   kits     a gallery: the player wheel and one wheel per corp kit (elite, boss) side by side.
##   hubs     the hub states: player, Mk2, enemy hub, lockdown, defeat drain.
##   states   one wheel per state overlay.
##   landing  a PERFECT / GOOD / WEAK landing on the player wheel (`--tier=perfect|good|weak`).
## Several cases in one window: `--cases=typical,worst:solace,kits,landing:weak --hold=30` (frames each;
## a case's `:x` is its tier for landing, its corp for typical / worst).
## Options: `--text-scale=1.6`, `--reduce-effects`, `--corp=<id>` (typical: the enemy's corp boss).
## Lab only: it sets fixture states on the views' own combatants; the game never does this.

const BOSSES := {&"meridian": &"the_manifest", &"solace": &"renewal_engine", &"halcyon": &"civic_core",
	&"orbital": &"commons_array", &"rebel_cell": &"dispatch_core"}
const ELITES := {&"meridian": &"port_authority", &"solace": &"recall_unit", &"halcyon": &"riot_control",
	&"orbital": &"station_commander", &"rebel_cell": &"the_handler"}
const CORPS: Array[StringName] = [&"meridian", &"solace", &"halcyon", &"orbital", &"rebel_cell"]
const SEED := 7
## Frames the scene lays out before a fixture is applied.
const SETTLE := 3

var case_name: String = "typical"
var corp: StringName = &"meridian"
var tier: String = "perfect"
var _scene: Node = null
var _engines: Array[CombatEngine] = []


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--case="):
			case_name = a.trim_prefix("--case=")
		elif a.begins_with("--corp="):
			corp = StringName(a.trim_prefix("--corp="))
		elif a.begins_with("--tier="):
			tier = a.trim_prefix("--tier=")
		elif a.begins_with("--text-scale="):
			Settings.set_text_scale(float(a.trim_prefix("--text-scale=")))
		elif a == "--reduce-effects":
			Settings.reduce_effects = true
	Settings.tutorial_done = true  # lab only (its own APPDATA): no tutorial over the captures
	UiTheme.apply(self)
	var cases := PackedStringArray([case_name])
	var hold := 30
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--cases="):
			cases = a.trim_prefix("--cases=").split(",")
		elif a.begins_with("--hold="):
			hold = int(a.trim_prefix("--hold="))
	# One window, several cases one after another (`--cases=typical,kits,landing:weak --hold=30`).
	for c in cases:
		for ch in get_children():
			ch.queue_free()
		_engines.clear()
		_scene = null
		case_name = c.get_slice(":", 0)
		if c.contains(":"):
			tier = c.get_slice(":", 1)
			corp = StringName(c.get_slice(":", 1)) if case_name in ["typical", "worst"] else corp
		await get_tree().process_frame
		print("wheel_lab: case %s from frame %d" % [c, Engine.get_frames_drawn()])
		_build()
		for k in hold:
			await get_tree().process_frame


func _build() -> void:
	match case_name:
		"typical", "worst", "landing":
			_combat()
		"kits":
			_gallery(_kit_rows())
		"hubs":
			_gallery(_hub_rows())
		"states":
			_gallery(_state_rows())


func _exit_tree() -> void:
	for e in _engines:
		e.queue_free()


# --- the combat scene ------------------------------------------------------------------------

func _combat() -> void:
	_scene = load("res://scenes/combat/combat_scene.tscn").instantiate()
	_scene.auto_start = false
	add_child(_scene)
	_scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_scene.start_fight(BOSSES.get(corp, &"the_manifest"), SEED)
	_scene.skip_motion()
	for k in SETTLE:
		await get_tree().process_frame
	var st: CombatState = _scene.engine.state()
	var foe: CombatantState = st.enemies[0]
	match case_name:
		"typical":
			st.player.wheel.slice_statuses[2] = RC.Status.OVERCLOCKED
			st.player.block = 6
			st.player.evade_charges = 1
			foe.shield = 4
			foe.wheel.slice_statuses[4] = RC.Status.ENCRYPTED
		"worst":
			var kinds := [RC.Status.CORRUPTED, RC.Status.OVERCLOCKED, RC.Status.ENCRYPTED, RC.Status.PARASITE]
			for c: CombatantState in [st.player, foe]:
				for i in c.wheel.slice_count:
					c.wheel.slice_statuses[i] = kinds[i % kinds.size()]
	_scene._refresh(st)
	_scene.skip_motion()
	if case_name == "landing":
		await get_tree().process_frame
		var tiers := {"perfect": RC.PrecisionTier.PERFECT, "good": RC.PrecisionTier.GOOD, "weak": RC.PrecisionTier.WEAK}
		var v: WheelView = _scene._player_view
		v.play_precision(int(tiers.get(tier, RC.PrecisionTier.PERFECT)), v.active_slot())
	print("wheel_lab: %s ready, scene %s" % [case_name, _scene.size])


# --- galleries -------------------------------------------------------------------------------

## One row per entry: [caption, class or enemy id, fixture callable or null].
func _gallery(rows: Array) -> void:
	var bg := ColorRect.new()
	bg.color = Palette.NIGHT_SKY
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	var grid := GridContainer.new()
	grid.columns = 3
	grid.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(grid)
	for row in rows:
		var eng := CombatEngine.new()
		add_child(eng)
		_engines.append(eng)
		var enemy: StringName = row[1]
		var foes: Array[StringName] = [enemy if enemy != &"" else &"the_manifest"]
		eng.start_fight(&"breaker", foes, SEED, &"rank:1")
		var st := eng.state()
		var c: CombatantState = st.player if enemy == &"" else st.enemies[0]
		if row[2] is Callable:
			(row[2] as Callable).call(c, st)
		var v := WheelView.new()
		v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		v.size_flags_vertical = Control.SIZE_EXPAND_FILL
		v.show_arrows = false
		grid.add_child(v)
		var lookup := ContentLookup.new().add_registry(ContentRegistry)
		v.show_combatant(c, st.satellites_of(c.id), eng.readouts(c), lookup)
		var cap := Label.new()
		cap.text = String(row[0])
		cap.theme_type_variation = &"HudLabel"
		v.add_child(cap)
	print("wheel_lab: %s ready (%d wheels)" % [case_name, rows.size()])


func _kit_rows() -> Array:
	var rows: Array = [["PLAYER // BREAKER", &"", null]]
	for c in CORPS:
		rows.append([String(c).to_upper() + " // BOSS", BOSSES[c], null])
	return rows


func _hub_rows() -> Array:
	return [
		["PLAYER HUB", &"", null],
		["ENEMY HUB", &"the_manifest", null],
		["ELITE", ELITES[&"meridian"], null],
		["LOCKDOWN 2", &"the_manifest", func(c: CombatantState, _st: CombatState) -> void: c.hub_breached_turns = 2],
		["LOCKDOWN 1 (player)", &"", func(c: CombatantState, _st: CombatState) -> void: c.hub_breached_turns = 1],
		["DEFEATED", &"", func(c: CombatantState, _st: CombatState) -> void: c.hp = 0],
	]


func _state_rows() -> Array:
	var rows: Array = []
	for s in [RC.Status.CORRUPTED, RC.Status.OVERCLOCKED, RC.Status.ENCRYPTED, RC.Status.PARASITE]:
		var status: int = s
		rows.append([RC.Status.keys()[status], &"", func(c: CombatantState, _st: CombatState) -> void:
			for i in c.wheel.slice_count:
				c.wheel.slice_statuses[i] = status])
	rows.append(["MIXED (boss)", &"the_manifest", func(c: CombatantState, _st: CombatState) -> void:
		for i in c.wheel.slice_count:
			c.wheel.slice_statuses[i] = 1 + i % 4])
	return rows
