extends GutTest
## Animation pass ANIM-R5, motion rules and tests (DECISIONS "Animation pass — ANIM-R5
## motion rules and tests"): every helper asks the one press rule (MotionSkip.handle) and
## one press completes every running skippable motion (R1, R2); a switched-off table entry
## does what the table says for every kind of entry (R3); the motion lab's demos exercise
## their own entries on the real pieces (R4).

const SCREEN := Rect2(0, 0, 1280, 720)
## The helpers that end a motion on a press (the one rule, not hand-rolled).
const HELPERS: Array[String] = [
	"res://scripts/ui/kit/typing.gd",
	"res://scripts/autoload/dialogue.gd",
	"res://scripts/ui/kit/menu_motion.gd",
	"res://scripts/ui/kit/drop_layer.gd",
	"res://scripts/ui/kit/flight_fx.gd",
	"res://scripts/ui/kit/page_transition.gd",
	"res://scripts/ui/netrun_scene.gd",
	"res://scripts/ui/combat_scene.gd",
]

var _reduce: bool = false
var _typing: bool = true


class Counter extends Node:
	## Counts the presses that reach it (it sits before the helpers in the tree, so they see
	## each event first).
	var got: int = 0

	func _input(event: InputEvent) -> void:
		if MotionSkip.is_press(event):
			got += 1


class FakeHelper extends Node:
	## A registered helper with a motion that runs until completed, keeping `keep`.
	var runs: bool = true
	var keep: Array = []
	var completed: int = 0

	func _ready() -> void:
		MotionSkip.register(self)

	func _input(event: InputEvent) -> void:
		if runs:
			MotionSkip.handle(event, self)

	func motion_running() -> bool:
		return runs

	func complete_motion() -> void:
		runs = false
		completed += 1

	func motion_keeps() -> Array:
		return keep


func before_all() -> void:
	_reduce = Settings.reduce_effects
	_typing = Settings.subtitle_typing


func before_each() -> void:
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	Motion.set_speed(1.0)
	Motion.use_config(null)
	Engine.time_scale = 1.0
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()
	if Settings.subtitle_typing != _typing:
		Settings.set_subtitle_typing(_typing)
	Dialogue.clear()


func _frames(n: int = 1) -> void:
	for i in n:
		await get_tree().process_frame


func _live() -> void:
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	Fx.apply_settings()
	if not Settings.subtitle_typing:
		Settings.set_subtitle_typing(true)
	Motion.force_live = true


func _holder() -> Array:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var counter := Counter.new()
	holder.add_child(counter)
	return [holder, counter]


func _key(k: Key) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = k
	e.physical_keycode = k
	e.pressed = true
	return e


func _click(at: Vector2, button: MouseButton = MOUSE_BUTTON_LEFT) -> InputEventMouseButton:
	var e := InputEventMouseButton.new()
	e.button_index = button
	e.pressed = true
	e.position = at
	e.global_position = at
	return e


func _hover(at: Vector2) -> void:
	var m := InputEventMouseMotion.new()
	m.position = at
	m.global_position = at
	get_viewport().push_input(m)


## A flight, a drop stamp, a page entrance and a typing label on `holder`, all running.
func _four_motions(holder: Control) -> Dictionary:
	FlightFx.fly_node(holder, ColorRect.new(), Rect2(10, 10, 40, 40), Vector2(600, 300), &"buy_fly")
	var layer := DropLayer.new()
	holder.add_child(layer)
	layer._stamp(Vector2(100, 100), 10.0)
	var page := Panel.new()
	page.size = Vector2(300, 200)
	holder.add_child(page)
	var label := Label.new()
	label.text = "THE RACK IS TWO HOPS OUT"
	label.position = Vector2(400, 400)
	holder.add_child(label)
	await _frames(1)
	PageTransition.enter(page)
	Typing.type_in(label)
	return {"layer": layer, "page": page, "label": label}


func _all_running(holder: Control, m: Dictionary) -> bool:
	return FlightFx.active_count(holder) > 0 and (m["layer"] as DropLayer).busy() \
		and PageTransition.running(m["page"]) and Typing.typing(m["label"])


func _none_running(holder: Control, m: Dictionary) -> bool:
	return FlightFx.active_count(holder) == 0 and not (m["layer"] as DropLayer).busy() \
		and not PageTransition.running(m["page"]) and not Typing.typing(m["label"])


# --- R1: every helper asks the one rule ---------------------------------------------------------

func test_the_helpers_route_presses_through_the_one_rule() -> void:
	for p in HELPERS:
		var src := FileAccess.get_file_as_string(p)
		assert_true(src.contains("MotionSkip.handle(") or src.contains("MotionSkip.verdict("), "%s asks the one rule" % p)
		assert_false(src.contains("MotionSkip.is_press("), "%s doesn't hand-roll the press test" % p)
		assert_false(src.contains("if not MotionSkip.works_ui"), "%s doesn't hand-roll the verdict" % p)
		assert_true(src.contains("MotionSkip.register(self)"), "%s joins the helpers one press completes" % p)
		assert_true(src.contains("func motion_running()") and src.contains("func complete_motion()"), "%s answers the helpers' protocol" % p)


func test_a_menu_line_click_trusts_the_cover_and_the_button_mask() -> void:
	var h := _holder()
	var holder: Control = h[0]
	var box := VBoxContainer.new()
	box.position = Vector2(100, 100)
	box.size = Vector2(300, 120)
	holder.add_child(box)
	for w in ["CONTINUE", "OPTIONS"]:
		var b := Button.new()
		b.text = w
		b.custom_minimum_size = Vector2(300, 50)
		box.add_child(b)
	var cover := Panel.new()
	cover.mouse_filter = Control.MOUSE_FILTER_STOP
	holder.add_child(cover)
	await _frames(2)
	var m := MenuMotion.attach(box)
	var first := (box.get_child(0) as Button).get_global_rect().get_center()
	var second := (box.get_child(1) as Button).get_global_rect().get_center()
	cover.position = second - Vector2(20, 20)
	cover.size = Vector2(40, 40)
	_hover(first)
	await _frames(1)
	assert_true(m.works_menu(_click(first)), "a left-click on a line works the menu")
	assert_false(m.works_menu(_click(first, MOUSE_BUTTON_RIGHT)), "a right-click works no left-click line (its button_mask)")
	_hover(second)
	await _frames(1)
	assert_false(m.works_menu(_click(second)), "a line under a panel is not clicked (the hovered panel is trusted)")
	assert_true(m.works_menu(_key(KEY_DOWN)), "a focus move works the menu")
	assert_false(m.works_menu(_key(KEY_SEMICOLON)), "a key that works nothing doesn't")


func test_a_pause_menu_line_owns_its_presses() -> void:
	var h := _holder()
	var holder: Control = h[0]
	var menu := PauseMenu.new()
	holder.add_child(menu)
	var outside := FakeHelper.new()
	holder.add_child(outside)
	var inside := FakeHelper.new()
	menu.add_child(inside)
	await _frames(1)
	assert_true(MotionSkip.pause_open(outside), "a helper outside the open pause menu leaves it the presses")
	assert_false(MotionSkip.pause_open(inside), "a helper inside it owns them with it")
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_eq(inside.completed, 1, "the pause menu's own motion completes")
	assert_true(outside.runs, "the motion the pause menu covers plays on (the press completes nothing behind it)")
	menu.free()


# --- R2: one press completes every running motion -------------------------------------------------

func test_a_stray_key_completes_a_flight_and_a_drop_together() -> void:
	_live()
	var h := _holder()
	var holder: Control = h[0]
	var counter: Counter = h[1]
	FlightFx.fly_node(holder, ColorRect.new(), Rect2(10, 10, 40, 40), Vector2(600, 300), &"buy_fly")
	var layer := DropLayer.new()
	holder.add_child(layer)
	layer._stamp(Vector2(100, 100), 10.0)
	assert_true(FlightFx.active_count(holder) > 0 and layer.busy(), "both run")
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_eq(FlightFx.active_count(holder), 0, "one stray key lands the flight")
	assert_false(layer.busy(), "and completes the drop's stamp with it (the consumed press used to end only the first)")
	assert_eq(counter.got, 0, "and is consumed")


func test_a_stray_key_completes_a_page_entrance_and_a_flight_together() -> void:
	_live()
	var h := _holder()
	var holder: Control = h[0]
	var counter: Counter = h[1]
	var page := Panel.new()
	page.size = Vector2(300, 200)
	holder.add_child(page)
	await _frames(1)
	PageTransition.enter(page)
	FlightFx.fly_node(holder, ColorRect.new(), Rect2(10, 10, 40, 40), Vector2(600, 300), &"buy_fly")
	assert_true(PageTransition.running(page) and FlightFx.active_count(holder) > 0, "both run")
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_false(PageTransition.running(page), "one stray key completes the entrance")
	assert_eq(FlightFx.active_count(holder), 0, "and lands the flight")
	assert_eq(counter.got, 0, "and is consumed")


func test_one_press_completes_four_running_motions_consumed_or_passed() -> void:
	_live()
	var h := _holder()
	var holder: Control = h[0]
	var counter: Counter = h[1]
	var m: Dictionary = await _four_motions(holder)
	assert_true(_all_running(holder, m), "a flight, a stamp, an entrance and typing all run")
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_true(_none_running(holder, m), "one stray key (CONSUME) completes all four")
	assert_eq(counter.got, 0, "and is consumed")
	m = await _four_motions(holder)
	assert_true(_all_running(holder, m), "all four run again")
	get_viewport().push_input(_key(KEY_LEFT))
	assert_true(_none_running(holder, m), "one focus move (PASS) completes all four")
	assert_eq(counter.got, 1, "and passes on")


func test_every_running_helpers_keeps_count_whichever_sees_the_press() -> void:
	_live()
	var h := _holder()
	var holder: Control = h[0]
	var counter: Counter = h[1]
	var button := Button.new()
	button.text = "SEND IT"
	button.position = Vector2(100, 100)
	button.size = Vector2(200, 60)
	holder.add_child(button)
	var replay := FakeHelper.new()
	replay.keep = [button]
	holder.add_child(replay)
	await _frames(1)
	# The flight's layer sits after the replay: it sees the press first.
	FlightFx.fly_node(holder, ColorRect.new(), Rect2(10, 10, 40, 40), Vector2(600, 300), &"buy_fly")
	var at := button.get_global_rect().get_center()
	_hover(at)
	await _frames(1)
	assert_eq(MotionSkip.verdict(_click(at), FlightFx.existing(holder)), MotionSkip.Verdict.CONSUME, "the flight's verdict counts the replay's keeps")
	var got := counter.got
	get_viewport().push_input(_click(at))
	assert_eq(FlightFx.active_count(holder), 0, "the click lands the flight")
	assert_false(replay.runs, "and ends the replay")
	assert_eq(counter.got, got, "and is kept: it never reaches the button behind (the next turn is never played blind)")


# --- R3: a switched-off entry does what the table says, for every kind of entry -------------------------

## A duplicate of the table in use (the loaded one is never changed) with `id` switched off.
func _table_with_off(id: StringName) -> UiMotionData:
	var dup := (load(Motion.CONFIG_PATH) as UiMotionData).duplicate(true)
	dup.find(id).enabled = false
	Motion.use_config(dup)
	return dup


func test_every_entry_switched_off_does_what_its_kind_says() -> void:
	_live()
	var file := load(Motion.CONFIG_PATH) as UiMotionData
	for id in UiMotionData.OFF_PARTS:
		assert_true(UiMotionData.REQUIRED_IDS.has(id), "%s (a part) is a table id" % id)
	for id in UiMotionData.ALWAYS_ON:
		assert_true(UiMotionData.REQUIRED_IDS.has(id), "%s (a tuning) is a table id" % id)
		assert_false(UiMotionData.OFF_PARTS.has(id), "%s is one kind only" % id)
	var kinds := {"own": 0, "part": 0, "tuning": 0}
	for on in file.entries:
		var id: StringName = on.id
		var dup := _table_with_off(id)
		assert_false(Motion.live(id), "%s off: its own motion never plays" % id)
		if UiMotionData.OFF_PARTS.has(id):
			kinds["part"] += 1
			assert_eq(Motion.seconds(id), 0.0, "%s off: the part takes no time" % id)
			assert_eq(Motion.delay_of(id), 0.0, "%s off: and waits for nothing" % id)
			assert_eq(Motion.amplitude(id), float(UiMotionData.OFF_PARTS[id]), "%s off: the part shows no motion" % id)
		elif UiMotionData.ALWAYS_ON.has(id):
			kinds["tuning"] += 1
			assert_false(dup.validate().is_empty(), "%s off: refused (it tunes another entry)" % id)
		else:
			kinds["own"] += 1
			assert_eq(Motion.seconds(id), on.duration, "%s off: its time stays (a hold the end state shows for)" % id)
			assert_eq(Motion.amplitude(id), on.amplitude, "%s off: its size stays (the end state's)" % id)
		Motion.use_config(null)
	assert_gt(int(kinds["own"]), 0, "entries with a motion of their own were checked")
	assert_eq(int(kinds["part"]), UiMotionData.OFF_PARTS.size(), "every part was checked")
	assert_eq(int(kinds["tuning"]), UiMotionData.ALWAYS_ON.size(), "every tuning was checked")
	assert_true(file.validate().is_empty(), "the table as shipped is valid")


func test_switched_off_parts_reach_the_views_that_read_them() -> void:
	_table_with_off(&"hit_line_flight")
	assert_almost_eq(CombatFxLayer.line_share(), 0.05, 0.0001, "hit_line_flight off: the projectile lands at once (the view's floor)")
	_table_with_off(&"mainframe_sign_strike")
	assert_eq(MainframeSign.strike_share(), 0.0, "mainframe_sign_strike off: every tube strikes at once")
	_table_with_off(&"mainframe_sign_flicker")
	assert_eq(MainframeSign.flicker_share(), 0.0, "mainframe_sign_flicker off: no flicker")
	_table_with_off(&"forecast_change_fade")
	assert_almost_eq(CityMapOverlay.change_fade_share(), 0.01, 0.0001, "forecast_change_fade off: no fade (the view's floor)")
	var combat: GDScript = load("res://scripts/ui/combat_scene.gd")
	_table_with_off(&"resolve_side_gap")
	assert_eq(float(combat.beat_timing()["side_gap"]), 0.0, "resolve_side_gap off: no gap between the sides")
	_table_with_off(&"resolve_attacker_gap")
	assert_eq(float(combat.beat_timing()["attacker_gap"]), 0.0, "resolve_attacker_gap off: no gap between attackers")
	_table_with_off(&"ride_perfect")
	assert_eq(Motion.amplitude(&"ride_perfect"), 1.0, "ride_perfect off: a PERFECT rides at its own size")
	Motion.use_config(null)
	assert_gt(Motion.amplitude(&"ride_perfect"), 1.0, "on: it rides bigger")
