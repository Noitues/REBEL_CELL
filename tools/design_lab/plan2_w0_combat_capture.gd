extends Node
## Plan 2 W0 VIS combat review capture (dev tool, windowed only through tools/run_windowed.py, 1920x1080, text 1.0).
## `--out=<abs dir>`: one PNG per state, driven from fixtures / state setup (never by playing turns):
##   1_ENRAGE.png    the ENRAGE N badge on a boss at turn 10, its tooltip open
##   2_NEEDLES.png   two adjacent needles (gap 1) on both wheels, each with its leader tag
##   3_RESIST.png    the resistance "+N" grease-pen mark at a turn refresh
##   4_DEFENSE.png   BLOCK / SHIELD / SANDBOX words on slices, SANDBOX charges, a negated hit
##   5_PARKED.png    the PARKED -N chip at a phase threshold
##   6_SATELLITE.png the satellite refusal toast, the satellite's nudge arrows disabled
## tools/design_lab/plan2_w0_combat_sheet.py stitches them.

const COMBAT := "res://scenes/combat/combat_scene.tscn"

var _out := ""
var _holder: Control = null


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


## A fresh combat scene (the previous one is freed). `session` null = a real fight against `enemy`.
func _scene(enemy: StringName, session: CombatSession = null) -> Control:
	if _holder != null:
		_holder.queue_free()
		await _frames(3)
	_holder = Control.new()
	_holder.size = get_viewport().get_visible_rect().size
	add_child(_holder)
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	_holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	if session == null:
		scene.start_fight(enemy, 5)
	else:
		scene.engine.resolver = session.resolver
		scene.engine.session = session
		scene.engine.state_changed.emit(session.state, session.last_events)
	scene.skip_motion()
	await _frames(10)
	return scene


func _shot(name: String) -> void:
	await _frames(14)
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [_out, name])
	print("shot ", name)


## Shows the badge's own tooltip (the object the engine's tooltip popup would show: native tooltips never
## open in the quiet off-screen window) just under it.
func _open_tooltip(badge: Control) -> void:
	var tip := badge._make_custom_tooltip(badge.tooltip_text) as Control
	var back := ColorRect.new()  # the popup's own glass
	back.color = Color(Palette.NIGHT_SKY, 0.95)
	_holder.add_child(back)
	back.add_child(tip)
	tip.reset_size()
	back.size = tip.size + Vector2(12, 8)
	tip.position = Vector2(6, 4)
	back.global_position = badge.get_global_rect().position + Vector2(-back.size.x + badge.size.x, badge.size.y + 6.0)
	print("tooltip ", back.get_global_rect())
	await _frames(4)


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.substr(6)
	DirAccess.make_dir_recursive_absolute(_out)
	# The quiet window ignores --resolution: size it here.
	DisplayServer.window_set_size(Vector2i(1920, 1080))
	await _frames(6)
	RunManager.save_slot = "plan2_w0_vis"
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	RunManager.new_campaign(1)
	await _enrage()
	await _needles()
	await _resist()
	await _defense()
	await _parked()
	await _satellite()
	RunManager.delete_save()
	get_tree().quit()


func _enrage() -> void:
	var scene := await _scene(&"civic_core")
	var s: CombatSession = scene.engine.session
	EnrageFixture.to_turn(s, 10)
	scene._refresh(s.state)
	await _frames(10)
	var e: CombatantState = s.state.enemies[0]
	var badge := scene._enemy_views[e.id].get_node_or_null(EnrageBuff.NODE_NAME) as Control
	if badge == null:
		push_error("ERROR: no enrage badge")
		await _shot("1_ENRAGE")
		return
	print("badge ", badge.get_global_rect(), " ", badge.tooltip_text)
	await _open_tooltip(badge)
	await _shot("1_ENRAGE")


func _needles() -> void:
	var scene := await _scene(&"collections_agent")
	var st: CombatState = scene.engine.state()
	for c: CombatantState in [st.enemies[0], st.player]:
		c.wheel.pointer_ticks = PackedInt32Array([8, 9]) if c.is_player else PackedInt32Array([17, 18])
	scene._refresh(st)
	await _shot("2_NEEDLES")


func _resist() -> void:
	var scene := await _scene(&"collections_agent")
	var st: CombatState = scene.engine.state()
	var e: CombatantState = st.enemies[0]
	e.resistance = 4
	e.resistance_gain = 4
	scene._refresh(st)
	await _shot("3_RESIST")


func _defense() -> void:
	var def_ := CombatFixture.slice(&"cv_def", RC.SliceType.DEFRAG, 6, RC.TargetRule.SELF)
	var shl := CombatFixture.slice(&"cv_shl", RC.SliceType.SANDBOX, 5, RC.TargetRule.SELF)
	var sbx := CombatFixture.slice(&"cv_sbx", RC.SliceType.DETOUR, 1, RC.TargetRule.SELF)
	var hit := CombatFixture.slice(&"cv_hit", RC.SliceType.SHIM, 9)
	var wheel := CombatFixture.wheel([def_, hit, shl, hit, sbx, hit], null, [2, 12, 22])
	var noop: Array[CardData] = [CombatFixture.card(&"cv_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var cls := CombatFixture.operative_class(&"cv_op", 60, wheel, noop)
	var foe := EnrageFixture.enemy(&"cv_foe", RC.EnemyClass.NORMAL, 9, 80, null, [2, 12])
	foe.display_name = "Collector"
	var s := CombatSession.start(CombatFixture.resolver([cls, foe]), cls.id, [foe.id], 77)
	var scene := await _scene(&"", s)
	var st: CombatState = s.state
	st.player.block = 6
	st.player.shield = 5
	st.player.evade_charges = 2
	st.enemies[0].block = 4
	CombatFixture.land(st.player, 0)
	CombatFixture.land(st.enemies[0], 1)
	st.player.wheel.pointer_ticks = PackedInt32Array([2, 12, 22])
	st.enemies[0].wheel.pointer_ticks = PackedInt32Array([7, 17])
	scene._refresh(st)
	await _frames(10)
	# SEND IT: the two hits meet the two charges (negated whole); the LAST TURN lines say so.
	scene.end_turn()
	scene.skip_motion()
	await _frames(20)
	print("charges left ", s.state.player.evade_charges)
	# The needles back on BLOCK / SHIELD / SANDBOX: their words sit on the slices; LAST TURN keeps the negated hits.
	s.state.player.evade_charges = 2
	CombatFixture.land(s.state.player, 0)
	scene._refresh(s.state)
	await _frames(10)
	await _shot("4_DEFENSE")


func _parked() -> void:
	var data := PhaseFixture.enemy(&"pf_cap", 100, [0.68, 0.33], RC.EnemyClass.MINI_BOSS)
	data.display_name = "Warden"
	data.phases[0].phase_line = "Warden shifts to phase two."
	var s := PhaseFixture.session(data, 30)
	PhaseFixture.aim(s).hp = 80  # 30 hits it to 50: the 68 % floor parks 18 of it
	var scene := await _scene(&"", s)
	scene._refresh(s.state)
	await _shot("5_PARKED")


func _satellite() -> void:
	var s := SatelliteFixture.session([SatelliteFixture.move_card(&"sf_nudge", RC.EffectType.NUDGE)])
	var scene := await _scene(&"", s)
	s.state.target_id = SatelliteFixture.sat_of(s).id
	scene._refresh(s.state)
	scene._nudge_wheel_option.select(1)
	scene.nudge(1)
	await _shot("6_SATELLITE")
