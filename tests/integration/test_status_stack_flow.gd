extends GutTest
## Plan 2 N8 flow (view glue): the combat screen shows ×N stacks — the badge tag says "×N"
## only from 2 stacks, the slot's tooltip names the stacks through TextDb words, the disc
## wears the parasite look for OUTPUT_DOWN, a cleanse takes the tag away, the Codex line
## says statuses stack, and a fight with stacks saved and continued keeps them.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)

var _settings: Dictionary = {}


func before_all() -> void:
	_settings = Settings.snapshot()


func after_all() -> void:
	Settings.restore(_settings)
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_n8_stacks"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.use_config(null)
	Motion.force_live = false
	Settings.restore(_settings)
	Fx.apply_settings()


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _combat() -> Control:
	Settings.set_text_scale(1.0)
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"collections_agent", 5)
	await _frames()
	return scene


func test_badge_hidden_at_one_stack_shown_at_two() -> void:
	assert_eq(WheelView.stack_badge(0), "")
	assert_eq(WheelView.stack_badge(1), "", "one stack: no count")
	assert_eq(WheelView.stack_badge(2), "×2")
	assert_eq(WheelView.stack_badge(5), "×5")
	var scene := await _combat()
	var v: WheelView = scene._player_view
	var st: CombatState = scene.engine.state()
	st.player.wheel.set_status(1, RC.Status.OUTPUT_DOWN, 1)
	scene._refresh(st)
	assert_false(v._status_tag(RC.Status.OUTPUT_DOWN, 1).contains("×"), "x1 shows no count")
	assert_eq(v._status_tag(RC.Status.OUTPUT_DOWN, 1), "x0.75")
	st.player.wheel.set_status(1, RC.Status.OUTPUT_DOWN, 2)
	scene._refresh(st)
	assert_eq(v._status_tag(RC.Status.OUTPUT_DOWN, 2), "×2 x0.5", "the count, then the output it leaves")
	assert_eq(v._status_tag(RC.Status.OVERCLOCKED, 3), "×3 x1.5", "OVERCLOCKED stays x1.5 at any count")
	v._sync_disc(v._center(), v._radius(), v.shown_rotation())
	var stats: PackedInt32Array = v.disc.mat.get_shader_parameter(&"stat")
	assert_eq(stats[1], RC.Status.PARASITE, "OUTPUT_DOWN wears the parasite's look on the disc")
	var tip: String = v._slice_label(1)
	assert_string_contains(tip, "×2: 2 stacks of OUTPUT DOWN on this slice.")
	scene.skip_motion()


func test_badge_updates_on_cleanse() -> void:
	var scene := await _combat()
	var v: WheelView = scene._player_view
	var st: CombatState = scene.engine.state()
	st.player.wheel.set_status(1, RC.Status.OUTPUT_DOWN, 3)
	scene._refresh(st)
	assert_eq(v.combatant.wheel.stacks_of(1, RC.Status.OUTPUT_DOWN), 3)
	var events: Array[Dictionary] = []
	scene.engine.session.resolver.fx.cleanse(st.player, 1, events, RC.CleanseMode.ONE_STACK)
	scene._refresh(st)
	assert_eq(v._status_tag(v.combatant.wheel.status_at(1), v.combatant.wheel.stacks_of(1, RC.Status.OUTPUT_DOWN)), "×2 x0.5")
	scene.engine.session.resolver.fx.cleanse(st.player, 1, events)
	scene._refresh(st)
	assert_eq(v.combatant.wheel.status_at(1), RC.Status.NONE, "cleansed: no badge")
	assert_false(v._slice_label(1).contains("stacks"))
	scene.skip_motion()


func test_quit_mid_fight_and_continue_keeps_stacks() -> void:
	var s := StatusSaveFixture.start()
	s.state.player.wheel.set_status(1, RC.Status.OUTPUT_DOWN, 3)
	s.state.get_combatant(&"enemy_0").wheel.set_status(2, RC.Status.CORRUPTED, 2)
	var path := SaveService.save_dir.path_join("n8_flow_%d.json" % OS.get_process_id())
	assert_eq(SaveService.save_dict(path, {"run": {"combat": s.to_dict()}}), OK)
	var loaded: Dictionary = SaveService.load_dict(path)
	assert_eq(int(loaded["version"]), SaveService.SAVE_VERSION)
	var back := CombatSession.from_dict(StatusSaveFixture.resolver(), StatusSaveFixture.session_dict(loaded))
	assert_eq(back.state_hash(), s.state_hash(), "continue: the same fight, stacks and all")
	var a := s.apply(CombatAction.end_turn())
	var b := back.apply(CombatAction.end_turn())
	assert_eq(b.resolved_state.state_hash(), a.resolved_state.state_hash(), "and it resolves the same")
	SaveService.delete_save(path)


func test_codex_status_entry_mentions_stacks() -> void:
	var def := String(Codex.STATUS_TEXT[RC.Status.OUTPUT_DOWN])
	assert_string_contains(def, "per stack")
	assert_string_contains(def, "Stacks add up")
	assert_false(Codex.STATUS_TEXT.has(RC.Status.PARASITE), "PARASITE is retired from the Codex (R8)")
	var entries := Codex.entries(ContentLookup.new().add_registry(ContentRegistry))
	var titles := []
	for e in entries["Statuses & precision"]:
		titles.append(String(e["title"]))
	assert_has(titles, "OUTPUT DOWN")
	assert_eq(Codex.status_text(RC.Status.OUTPUT_DOWN, 1), def, "one stack: the definition alone")
	assert_string_contains(Codex.status_text(RC.Status.OUTPUT_DOWN, 4), "×4: 4 stacks of OUTPUT DOWN")
