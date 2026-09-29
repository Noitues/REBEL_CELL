extends Control
## Art pass W3 review strips: plays one combat motion in the real combat scene and saves a
## frame every `--step` seconds (game time) to `--out` (a folder), for
## the review strips in docs/art_review/W3 (real-time steps). Run windowed through run_windowed.py:
##   python tools/run_windowed.py --log s.log -- res://tools/design_lab/w3_strips.tscn -- --mode=resolve --speed=x2 --out=C:/tmp/f
## Modes: resolve (SEND IT at --speed x1 / x2 / instant), boss_intro (a boss fight opens),
## phase (a boss phase: its stamp, burst and new needle drawing on), hp_drain (the two-stage
## HP drain). Nothing here changes a rule: it drives the scene's own public calls.

const SCENE := "res://scenes/combat/combat_scene.tscn"
const BOSS := &"civic_core"
const SETTLE_FRAMES := 20

var _out := ""
var _step := 0.1
var _frames := 12
var _crop := Rect2i()


func _ready() -> void:
	var mode := "resolve"
	var speed := &"x1"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--mode="):
			mode = a.trim_prefix("--mode=")
		elif a.begins_with("--speed="):
			speed = StringName(a.trim_prefix("--speed="))
		elif a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
		elif a.begins_with("--step="):
			_step = float(a.trim_prefix("--step="))
		elif a.begins_with("--frames="):
			_frames = int(a.trim_prefix("--frames="))
	Settings.resolve_speed = speed
	DirAccess.make_dir_recursive_absolute(_out)
	RunManager.scene_switching_enabled = false
	RunManager.reset()
	RunManager.new_campaign(1)
	var scene: Control = load(SCENE).instantiate()
	scene.auto_start = false
	add_child(scene)
	scene.size = Vector2(1280, 720)
	var enemy := BOSS if mode in ["boss_intro", "phase"] else &"collections_agent"
	if mode != "boss_intro":
		scene.start_fight(enemy, 1)
		for i in SETTLE_FRAMES:
			await get_tree().process_frame
		scene.skip_motion()
		await get_tree().process_frame
	match mode:
		"resolve":
			scene.end_turn()
		"boss_intro":
			for i in 2:
				await get_tree().process_frame
			scene.start_fight(enemy, 1)
		"phase":
			var ev: WheelView = scene._enemy_views.values()[0]
			var st: CombatState = scene.engine.state()
			scene._phase_beat({"target": st.enemies[0].id, "phase_index": 1, "behavior": RC.PointerBehavior.MULTIPLY,
				"ticks": [0, 10, 20], "spawned": []}, st)
			ev.queue_redraw()
		"hp_drain":
			var pv: WheelView = scene._player_view
			pv.play_hp(float(pv.combatant.hp) * 0.2)
			pv.play_hit()
	# Frames at even steps of real time (a 2x replay shows twice the progress per frame).
	var start := Time.get_ticks_msec()
	var next := 0.0
	var k := 0
	while k < _frames:
		await RenderingServer.frame_post_draw
		var elapsed := (Time.get_ticks_msec() - start) / 1000.0
		if elapsed + 0.0001 >= next:
			var img := get_viewport().get_texture().get_image()
			img.save_png("%s/f%03d.png" % [_out, k])
			k += 1
			next += _step
	print("w3_strips: saved %d frames to %s" % [k, _out])
	Settings.resolve_speed = &"x1"
	get_tree().quit(0)
