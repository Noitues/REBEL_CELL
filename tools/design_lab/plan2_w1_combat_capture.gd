extends Node
## Plan 2 W1 CAP-W1 combat review capture (dev tool, windowed only through tools/run_windowed.py, 1920x1080, text 1.0).
## `--out=<abs dir>`: one PNG per state, driven from fixtures / state setup (never by playing turns):
##   1_N8_STACKS.png    the x2 stack badge on a player slice, its tooltip plate open
##   2_N6_LISTENER.png  the enemy listener chip ("REACTS: N DMG") from a hovered nudge's preview
##   3_N7_LOCKS.png     NUDGE LOCKED / RESPIN LOCKED chips on the player wheel and the refusal toast
##   4_N12_DISC.png     the combat disc with uneven slice spans (9 3 6 0 4 8 ticks: one empty arc)
##   5_N12_LOADOUT.png  the loadout SPINNER tab with the sub-tick map under the uneven wheel
## tools/design_lab/plan2_w1_combat_sheet.py stitches them.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const L = preload("res://tests/helpers/listener_fixture.gd")
const LK = preload("res://tests/helpers/lock_fixture.gd")

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


func _shot(name: String, wait: int = 14) -> void:
	await _frames(wait)
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [_out, name])
	print("shot ", name)


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.substr(6)
	DirAccess.make_dir_recursive_absolute(_out)
	# The quiet window ignores --resolution: size it here.
	DisplayServer.window_set_size(Vector2i(1920, 1080))
	await _frames(6)
	RunManager.save_slot = "plan2_w1_cap"
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	RunManager.new_campaign(1)
	await _stacks()
	await _listener()
	await _locks()
	var uneven := _uneven_class()
	await _disc(uneven)
	await _loadout(uneven)
	RunManager.delete_save()
	get_tree().quit()


func _stacks() -> void:
	var scene := await _scene(&"collections_agent")
	var v: WheelView = scene._player_view
	var st: CombatState = scene.engine.state()
	st.player.wheel.set_status(1, RC.Status.OUTPUT_DOWN, 2)
	scene._refresh(st)
	await _frames(10)
	# Native tooltips never open in the quiet off-screen window: the capture draws the view's own tooltip text
	# (WheelView._slice_label) on a plate beside the slice, as hover would show it.
	var plate := PanelContainer.new()
	var label := Label.new()
	# The live tooltip: what hovering the slice asks the view for (WheelView._get_tooltip at the slice's badge).
	var live := v._get_tooltip(v.badge_spot(1) - v.global_position)
	print("TIP_MATCH ", live == v._slice_label(1), " live_len ", live.length())
	label.text = live
	label.custom_minimum_size.x = 460
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	plate.add_child(label)
	_holder.add_child(plate)
	plate.position = v.global_center() + Vector2(150, -120)
	await _shot("1_N8_STACKS")


func _listener() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_NUDGE, [L.hit(4), L.block(1)])], {"factor": 1.3})
	L.stage(s)
	var scene := await _scene(&"", s)
	scene._sync_listener_chips(s.preview(CombatAction.nudge(&"player", 1)).events)
	await _shot("2_N6_LISTENER")


func _locks() -> void:
	var s := LK.session()
	var scene := await _scene(&"", s)
	s.state.player.wheel.add_lock(WheelState.LOCK_NUDGE, &"lk_enemy", 1)
	s.state.player.wheel.add_lock(WheelState.LOCK_RESPIN, &"lk_enemy", 1)
	scene._refresh(s.state)
	await _frames(6)
	scene.nudge_wheel(&"player", 1)
	await _shot("3_N7_LOCKS", 4)


func _uneven_class() -> ClassData:
	var types := [RC.SliceType.SHIM, RC.SliceType.DEFRAG, RC.SliceType.SANDBOX, RC.SliceType.NULL, RC.SliceType.DETOUR, RC.SliceType.SHIM]
	var slices := []
	for i in types.size():
		slices.append(CombatFixture.slice(StringName("cw1_%d" % i), types[i], 6 + i, RC.TargetRule.SELF if types[i] != RC.SliceType.SHIM else RC.TargetRule.POINTER))
	var w := WheelFixtures.make_layout([9, 3, 6, 0, 4, 8], slices, [], [], [3, 13, 23])
	w.hub = CombatFixture.hub(&"cw1_hub")
	var noop: Array[CardData] = [CombatFixture.card(&"cw1_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	return CombatFixture.operative_class(&"cw1_class", 60, w, noop)


func _disc(cls: ClassData) -> void:
	var foe := EnrageFixture.enemy(&"cw1_foe", RC.EnemyClass.NORMAL, 9, 80, null, [2, 12])
	foe.display_name = "Collector"
	var s := CombatSession.start(CombatFixture.resolver([cls, foe]), cls.id, [foe.id], 77)
	var scene := await _scene(&"", s)
	await _shot("4_N12_DISC")


func _loadout(cls: ClassData) -> void:
	if _holder != null:
		_holder.queue_free()
		await _frames(3)
	_holder = Control.new()
	_holder.size = get_viewport().get_visible_rect().size
	add_child(_holder)
	var lookup := ContentLookup.new().add_registry(ContentRegistry)
	lookup.add(cls)
	for slot in cls.starting_wheel.slots:
		lookup.add(slot.slice)
	var op := OperativeState.from_class(cls, &"op_1", "Vex")
	var view := LoadoutView.new(op, lookup)
	_holder.add_child(view)
	await _frames(20)
	view.show_spinner()
	await _frames(30)
	await _shot("5_N12_LOADOUT")
