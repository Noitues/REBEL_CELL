extends GutTest
## Animation pass ANIM-R5 R4 (DECISIONS "Animation pass — ANIM-R5 motion rules and tests"):
## every entry's motion lab demo exercises that entry. The lab plays each id while the
## Motion kit notes which script reads which entry (Motion.recording). A demo on a real
## piece (a combat scene, a screen, the wheel, Fx, the city map, the raid) passes when a
## script other than the lab reads the id; a stand-in demo (the lab's own Motion helper on
## a lab piece) passes only when the game plays that id with the same helper, so a share,
## a drawn motion or a stamp is never shown as a generic pop, lift or fade (a lift of 0.33
## px for a fade share, an alpha loop for a road pulse, a panel fade for a stamp).

const LAB := "res://tools/design_lab/motion_lab.tscn"
const LAB_SCRIPT := "res://tools/design_lab/motion_lab.gd"
const GAME_ROOT := "res://scripts"
## The Motion kit helper each stand-in kind plays (the game must play the id with it).
const STAND_IN_HELPERS := {
	"pop": "pop", "pulse_scale": "pop", "lift": "run", "drop": "slide_in", "drop_away": "run",
	"slide_x": "slide_in", "fly": "run", "shake": "shake", "blink": "blink", "pulse": "loop_pulse",
	"pulse_pointer": "loop_pulse", "fade_out": "fade", "fade_to": "fade", "fade_in": "fade",
	"tilt": "run", "spin": "run", "roll": "number_roll",
}
## Demos whose real piece skips its motion under the headless display itself (not through
## Motion.animating, which force_live opens) or needs the GPU's bake: the test checks they
## play on a real piece, a windowed run checks the read (motion_lab --demo-check=<frames>;
## DECISIONS "Animation pass — ANIM-R5 motion rules and tests").
const WINDOWED_ONLY := {
	&"toast": "Toast stays up headless for tests to read",
	&"resolve_pass": "the combat log is instant headless",
	&"hand_reflow": "the hand's gap closes when the pointer leaves the hand (no pointer headless)",
	&"influence_spread": "spreads once the new look's bake shows (GPU)",
	&"influence_crossfade": "spreads once the new look's bake shows (GPU)",
	&"influence_tint": "spreads once the new look's bake shows (GPU)",
	&"influence_mark": "marks once the new look's bake shows (GPU)",
	&"city_bake_fade": "fades the city's bake in (GPU)",
}
## Game time a demo gets to read its entry (at SPEED), s.
const DEMO_LIMIT := 12.0
## Demos play at this speed (the lab's own speed control).
const SPEED := Motion.SPEED_MAX

var _reduce: bool = false
var _typing: bool = true


func before_all() -> void:
	_reduce = Settings.reduce_effects
	_typing = Settings.subtitle_typing


func after_all() -> void:
	Motion.recording = false
	Motion.force_live = false
	Motion.set_speed(1.0)
	Motion.use_config(null)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()
	if Settings.subtitle_typing != _typing:
		Settings.set_subtitle_typing(_typing)
	Dialogue.clear()
	Fx._jacking = false


## {script path: {const name: id}} for the game's scripts, and their sources.
func _game_sources() -> Dictionary:
	var out := {}
	var stack: Array[String] = [GAME_ROOT]
	while not stack.is_empty():
		var dir: String = stack.pop_back()
		for f in DirAccess.get_files_at(dir):
			if f.ends_with(".gd"):
				out[dir.path_join(f)] = FileAccess.get_file_as_string(dir.path_join(f))
		for d in DirAccess.get_directories_at(dir):
			stack.append(dir.path_join(d))
	return out


## True when some game script plays `id` with Motion.<helper>( (the id written in the call,
## or a constant of that script naming it).
func _game_plays_with(sources: Dictionary, id: StringName, helper: String) -> bool:
	var call := "Motion.%s(" % helper
	var lit := "&\"%s\"" % id
	var const_re := RegEx.create_from_string("const\\s+([A-Z_][A-Z0-9_]*)\\s*:?=\\s*&\"%s\"" % id)
	for p in sources:
		var src: String = sources[p]
		if not src.contains(call):
			continue
		var names: Array[String] = [lit]
		for m in const_re.search_all(src):
			names.append(m.get_string(1))
		for line in src.split("\n"):
			if not line.contains(call):
				continue
			for n in names:
				if line.contains(n):
					return true
	return false


func test_every_lab_demo_exercises_its_own_entry() -> void:
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	Fx.apply_settings()
	if not Settings.subtitle_typing:
		Settings.set_subtitle_typing(true)
	Motion.force_live = true
	var lab: Control = load(LAB).instantiate()
	lab.set("_loop", false)
	add_child_autofree(lab)
	await get_tree().process_frame
	Motion.set_speed(SPEED)
	var sources := _game_sources()
	var demos: Dictionary = (load(LAB_SCRIPT) as GDScript).get_script_constant_map()["DEMOS"]
	var bad: Array[String] = []
	var cfg := Motion.config()
	for id in cfg.ids():
		var demo: Array = demos.get(id, ["pop", "sticker"])
		var kind := String(demo[0])
		var stand_in := STAND_IN_HELPERS.has(kind)
		if WINDOWED_ONLY.has(id):
			if stand_in:
				bad.append("%s (%s %s): windowed-only, and a stand-in" % [id, kind, demo[1]])
			continue
		# One jack at a time (a jack asked for during another does nothing).
		await BoundedWait.until(get_tree(), func() -> bool: return not Fx.transitioning(), DEMO_LIMIT)
		Motion.start_recording()
		lab.set("_id", id)
		lab.call("_play")
		var ok := await BoundedWait.until(get_tree(), func() -> bool: return _exercised(id, stand_in), DEMO_LIMIT)
		var readers := Motion.readers(id)
		Motion.stop_recording()
		if not ok:
			bad.append("%s (%s %s): read by %s" % [id, kind, demo[1], readers])
		elif stand_in and not _game_plays_with(sources, id, STAND_IN_HELPERS[kind]):
			bad.append("%s (%s %s): a stand-in, but the game doesn't play it with Motion.%s" % [id, kind, demo[1], STAND_IN_HELPERS[kind]])
	for b in bad:
		gut.p("demo misses its entry: %s" % b)
	assert_eq(bad.size(), 0, "every demo exercises its own entry on the real piece (the list: 'demo misses its entry' lines)")
	Motion.recording = false


## True when the demo now running has read `id`: from a real piece (a script other than the
## lab), or for a stand-in from the lab's Motion helper.
func _exercised(id: StringName, stand_in: bool) -> bool:
	for p in Motion.readers(id):
		if p != LAB_SCRIPT or stand_in:
			return true
	return false


## The check catches the demos ANIM-R4 shipped wrong: a 0 s lift of 0.33 px for the forecast
## change's fade share, an alpha loop on a sticker for the road pulse, a panel fade for the
## RAID INCOMING stamp. None of them is played by the game with that helper, and each demo
## now plays on the real piece.
func test_the_check_catches_the_stand_ins_that_misrepresented() -> void:
	var sources := _game_sources()
	assert_false(_game_plays_with(sources, &"forecast_change_fade", "run"), "the fade share is no lift")
	assert_false(_game_plays_with(sources, &"forecast_road_pulse", "loop_pulse"), "the road pulse is no alpha loop")
	assert_false(_game_plays_with(sources, &"raid_incoming_hold", "fade"), "the stamp's hold is no panel fade")
	assert_true(_game_plays_with(sources, &"card_pickup", "pop"), "a pickup is a pop in the game too (a fair stand-in)")
	var demos: Dictionary = (load(LAB_SCRIPT) as GDScript).get_script_constant_map()["DEMOS"]
	for id in [&"forecast_change_fade", &"forecast_road_pulse", &"raid_incoming_hold"]:
		assert_false(STAND_IN_HELPERS.has(String((demos[id] as Array)[0])), "%s plays on its real piece (%s)" % [id, demos[id]])
	for id in WINDOWED_ONLY:
		assert_true(Motion.has(id), "%s (windowed only) is a table id" % id)
