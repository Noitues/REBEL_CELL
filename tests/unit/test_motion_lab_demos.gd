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
## ANIM-R6 D3: entries whose time is a hold, a wait or a reading time (how long an end
## state or a word shows), not a motion: switched off, they keep their time (UiMotionData:
## an entry's time stays, the end state's hold), so no view asks whether they play.
## STYLE_GUIDE 5.5 lists them.
const HOLDS := {
	&"resolve_landing_hold": "the landed slices hold before anything resolves",
	&"resolve_result_hold": "the result shows this long before the screen goes back",
	&"combat_end_hold": "VICTORY holds before the loot",
	&"toast_note_hold": "a note stays up to be read",
	&"dialog_hold_confirm": "the hold on an abandon dialog's verb (an input time: the ring fills under reduce effects too)",
	&"jack_arrival_wait": "the jack's cover waits (bounded) for the arriving screen",
	&"asset_drop_wait": "the drop waits for the camera",
	&"raid_incoming_hold": "RAID INCOMING's reading time",
	&"jack_connect": "CONNECTING's reading time",
	&"resolve_sequence": "the replay's pacing between beats",
	&"resolve_beat": "the replay's pacing between beats",
	&"resolve_pass": "the log's pacing between passes",
}
## ANIM-R6 D3: the Motion calls that ask whether an entry plays (the helpers ask `live`
## for their caller).
const ASKING_HELPERS: Array[String] = ["live", "seconds_live", "switched_on", "run", "fade", "pop", "slide_in",
	"shake", "blink", "loop_pulse", "number_roll"]
## ANIM-R6 D3: views found ignoring an entry's switch that another fix agent of this round
## owns (DECISIONS "Animation pass — ANIM-R6 rules", D3). Each must still be caught: once
## its view asks, the test says to remove it here (the list only shrinks).
const AWAITING_FIX := {
	&"dead_wheel_fade": "wheel_view.play_break (fix agent A combat)",
	&"heal_number": "combat_scene (fix agent A combat)",
	&"hit_absorb": "combat_scene (fix agent A combat)",
	&"hp_lag": "wheel_view (fix agent A combat)",
	&"number_float": "combat_scene (fix agent A combat)",
	&"beacon_blink": "neon_city (fix agent C city/raid)",
	&"city_sign_pick": "neon_city (fix agent C city/raid)",
	&"raid_outcome_stagger": "raid_fx_layer (fix agent C city/raid)",
	&"route_target_pulse": "city_map_overlay (fix agent C city/raid)",
	&"select_ring_pulse": "city_map_overlay (fix agent C city/raid)",
}
## Game time a demo gets to read its entry (at SPEED), s.
const DEMO_LIMIT := 12.0
## ANIM-R6: frames a demo gets at least, beyond the lab's own context settle (a netrun or
## HQ demo waits CONTEXT_SETTLE + CONTEXT_BAKE_FRAMES frames before it acts, and the
## fight_won demo then plays a whole SEND IT): under a loaded shard those frames' game time
## ran past DEMO_LIMIT first (combat_end_hold's demo failed 2 runs in 3). The wait returns as
## soon as the entry is read, so only a demo that misses pays for them.
const DEMO_EXTRA_FRAMES := 240
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
	var lab_consts := (load(LAB_SCRIPT) as GDScript).get_script_constant_map()
	var demos: Dictionary = lab_consts["DEMOS"]
	var min_frames := int(lab_consts["CONTEXT_SETTLE"]) + int(lab_consts["CONTEXT_BAKE_FRAMES"]) + DEMO_EXTRA_FRAMES
	var bad: Array[String] = []
	var cfg := Motion.config()
	# ANIM-R6 D3: every entry read and every `live` asked across all the demos.
	# The asks accumulate over the whole loop (a view may ask as its motion ends, after the
	# demo has shown its read); each demo's reads start afresh.
	var all_reads := {}
	Motion.start_recording()
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
		_merge(all_reads, Motion.reads)
		Motion.reads.clear()
		lab.set("_id", id)
		lab.call("_play")
		var ok := await BoundedWait.until(get_tree(), func() -> bool: return _exercised(id, stand_in), DEMO_LIMIT, min_frames)
		var readers := Motion.readers(id)
		if not ok:
			bad.append("%s (%s %s): read by %s" % [id, kind, demo[1], readers])
		elif stand_in and not _game_plays_with(sources, id, STAND_IN_HELPERS[kind]):
			bad.append("%s (%s %s): a stand-in, but the game doesn't play it with Motion.%s" % [id, kind, demo[1], STAND_IN_HELPERS[kind]])
	for b in bad:
		gut.p("demo misses its entry: %s" % b)
	assert_eq(bad.size(), 0, "every demo exercises its own entry on the real piece (the list: 'demo misses its entry' lines)")
	# The last demo's motions end (a view may ask as they do).
	await BoundedWait.until(get_tree(), func() -> bool: return not Fx.transitioning(), DEMO_LIMIT)
	_merge(all_reads, Motion.reads)
	var all_asks := Motion.asks.duplicate(true)
	Motion.stop_recording()
	var deaf := unswitched(all_reads, all_asks, sources)
	var awaiting: Array[String] = []
	for d in deaf:
		var id := StringName(d.get_slice(":", 0))
		if AWAITING_FIX.has(id):
			awaiting.append(String(id))
		else:
			gut.p("switch ignored: %s" % d)
	assert_eq(deaf.size() - awaiting.size(), 0, "every view that plays an entry asks whether it is switched on (the list: 'switch ignored' lines)")
	for id: StringName in AWAITING_FIX:
		if not awaiting.has(String(id)):
			gut.p("switch now asked: %s (remove it from AWAITING_FIX)" % id)
		assert_true(awaiting.has(String(id)), "%s still ignores its switch (%s); fixed: remove it from AWAITING_FIX" % [id, AWAITING_FIX[id]])


## Adds `from`'s {id: {script: true}} into `into`.
static func _merge(into: Dictionary, from: Dictionary) -> void:
	for id in from:
		var d: Dictionary = into.get_or_add(id, {})
		d.merge(from[id])


## ANIM-R6 D3 (the view-level switch check): the entries with a motion of their own
## (UiMotionData: not a part, a tuning or a hold) that a game script read while the demos
## played (their time, delay, shape or size) but that no game script asks whether it
## plays: not while the demos ran (`Motion.asks`) and not in its source (a `Motion.live`,
## `seconds_live` or `switched_on` question, or a kit helper that asks for its caller:
## `run`, `fade`, `pop`, ...). Switching such an entry off leaves the view animating. As
## "id: read by <scripts>".
func unswitched(reads: Dictionary, asks: Dictionary, sources: Dictionary) -> Array[String]:
	var out: Array[String] = []
	var ids := reads.keys()
	ids.sort()
	for id: StringName in ids:
		if UiMotionData.OFF_PARTS.has(id) or UiMotionData.ALWAYS_ON.has(id) or HOLDS.has(id):
			continue
		var game_readers: Array[String] = []
		for p: String in reads[id]:
			if p.begins_with(GAME_ROOT):
				game_readers.append(p)
		if game_readers.is_empty():
			continue
		var asked := false
		for p: String in asks.get(id, {}):
			if p.begins_with(GAME_ROOT):
				asked = true
		for helper in ASKING_HELPERS:
			if not asked and _game_plays_with(sources, id, helper):
				asked = true
		if not asked and _asked_through(sources, id):
			asked = true
		if not asked:
			game_readers.sort()
			out.append("%s: read by %s" % [id, ", ".join(game_readers)])
	return out


## ANIM-R6 D3: true when a game script asks about `id` through a function of its own that
## asks for the id it is given (`func f(id: StringName, ...)` whose body asks one of
## ASKING_HELPERS about `id`, or calls another such function with it: the raid layer's
## `beat_u` -> `motion_len` -> `Motion.live(id)`), called with `id` written out or a const
## naming it. A demo does not always reach the moment the view asks (a threat withdrawing
## at the verdict, the result banner at the raid's end).
func _asked_through(sources: Dictionary, id: StringName) -> bool:
	var fn_re := RegEx.create_from_string("^(static )?func ([a-z_0-9]+)\\(id: StringName")
	var const_re := RegEx.create_from_string("const\\s+([A-Z_][A-Z0-9_]*)\\s*:?=\\s*&\"%s\"" % id)
	for p: String in sources:
		var src: String = sources[p]
		var names: Array[String] = ["&\"%s\"" % id]
		for m in const_re.search_all(src):
			names.append(m.get_string(1))
		# The functions of this script that take an id, and their bodies.
		var bodies := {}
		var current := ""
		for line in src.split("\n"):
			var m := fn_re.search(line)
			if m != null:
				current = m.get_string(2)
				bodies[current] = ""
			elif line.begins_with("func ") or line.begins_with("static func "):
				current = ""
			elif current != "":
				bodies[current] += line + "\n"
		var asking: Array[String] = []
		var grew := true
		while grew:
			grew = false
			for fn: String in bodies:
				if asking.has(fn):
					continue
				var body: String = bodies[fn]
				var asks := false
				for helper in ASKING_HELPERS:
					if body.contains("Motion.%s(id" % helper):
						asks = true
				for other in asking:
					if body.contains("%s(id" % other):
						asks = true
				if asks:
					asking.append(fn)
					grew = true
		for fn in asking:
			for n in names:
				if src.contains("%s(%s" % [fn, n]):
					return true
	return false


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


## ANIM-R6 D3: the switch check names a view that reads an entry and never asks, and lets
## a part, a tuning, a hold, a runtime ask or a source ask through.
func test_the_switch_check_names_a_view_that_never_asks() -> void:
	var view := "res://scripts/ui/kit/a_view.gd"
	var reads := {&"raid_move": {view: true}, &"hit_line_flight": {view: true}, &"send_it_drips_share": {view: true},
		&"combat_end_hold": {view: true}, &"card_hover": {view: true}, &"toast": {LAB_SCRIPT: true}}
	var sources := {view: "func f() -> void:\n\tMotion.pop(self, &\"card_hover\")\n"}
	assert_eq(unswitched(reads, {}, sources), ["raid_move: read by %s" % view] as Array[String], "only the view that never asks is named")
	assert_eq(unswitched(reads, {&"raid_move": {view: true}}, sources), [] as Array[String], "an ask while the demos ran counts")
	for id: StringName in HOLDS:
		assert_true(Motion.has(id), "%s (a hold) is a table id" % id)
	for id: StringName in AWAITING_FIX:
		assert_true(Motion.has(id), "%s (awaiting its fix) is a table id" % id)
	# A view that asks through a function of its own counts (the raid layer's beat_u).
	var through := {"res://scripts/ui/kit/a_layer.gd": "const MOVE := &\"raid_move\"\n\nfunc len_of(id: StringName, d: float) -> float:\n\treturn d if Motion.live(id) else 0.0\n\nfunc u_of(id: StringName, t: float) -> float:\n\treturn t / len_of(id, 1.0)\n\nfunc _draw() -> void:\n\tvar u := u_of(MOVE, 0.5)\n"}
	assert_true(_asked_through(through, &"raid_move"), "an ask through the layer's own functions counts")
	assert_false(_asked_through(through, &"raid_flip"), "an id it never passes does not")
	assert_true(_asked_through(_game_sources(), &"raid_threat_withdraw"), "the raid layer asks about a withdrawal through beat_u")
