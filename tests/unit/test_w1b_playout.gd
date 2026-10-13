extends GutTest
## 1B-PLAYOUT (PT-002a F3): SEND IT, the tutorial win and START DEFENSE showed no playout in
## the real game. Cause: a windowed capture or lab run shared the player's user:// settings and
## saved reduce_effects = true into settings.json; every playout asks Motion.animating(), which
## is false under reduce effects. Guards: a fresh Settings has motion on at 1x; a quiet windowed
## run never touches the player's file; and with only the display faked (Motion.force_live, the
## stand-in for a real window) and Settings left as a new player has them, SEND IT replays.

const SCENE := "res://scenes/combat/combat_scene.tscn"
const SETTINGS := "res://scripts/autoload/settings.gd"


func after_each() -> void:
	Motion.force_live = false
	Fx.apply_settings()


func test_a_new_player_has_playouts_on_at_1x() -> void:
	var fresh: Node = load(SETTINGS).new()
	fresh.from_dict({})
	assert_false(fresh.reduce_effects, "reduce effects is off by default")
	assert_false(fresh.reduce_motion, "reduce motion is off by default")
	assert_eq(fresh.resolve_speed, &"x1", "the resolve plays at 1x by default")
	fresh.free()


func test_only_the_players_session_uses_the_players_settings_file() -> void:
	var S: GDScript = load(SETTINGS)
	assert_eq(S.path_for(false, false, 7), S.PATH, "a normal session")
	assert_ne(S.path_for(false, true, 7), S.PATH, "a quiet windowed run (captures, labs) is kept off it")
	assert_ne(S.path_for(true, false, 7), S.PATH, "and a test run")
	assert_ne(S.path_for(false, true, 7), S.path_for(true, false, 7))


func test_send_it_replays_with_settings_as_a_new_player_has_them() -> void:
	assert_false(Settings.reduce_effects, "the test run starts from defaults (no leaked reduce effects)")
	assert_eq(Settings.resolve_speed, &"x1")
	Motion.force_live = true
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(SCENE).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"collections_agent", 5)
	for i in 3:
		await get_tree().process_frame
	scene.end_turn()
	assert_not_null(scene._seq, "SEND IT plays its replay")
	assert_almost_eq(Motion.resolve_time_scale(), 1.0, 0.0001, "at 1x")
