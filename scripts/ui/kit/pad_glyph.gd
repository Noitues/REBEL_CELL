class_name PadGlyph
extends Control
## ART_BIBLE §12: a pad button drawn as its glyph, for the four glyph sets (Xbox,
## PlayStation, Switch, Steam Deck). Every glyph is procedural and original (discs, tabs,
## shapes and letters drawn with CanvasItem calls; no third-party glyph art): the face
## buttons (Xbox coloured A/B/X/Y; PlayStation's cross, circle, square and triangle drawn as
## shapes; Switch's B/A/Y/X by position; the Deck's A/B/X/Y), shoulders and triggers,
## the D-pad (each direction and whole), both sticks (and their clicks), and Menu / View as
## icons, never the words. The set follows `Settings.pad_glyph_set` (auto / xbox /
## playstation / switch / deck); auto reads the first pad's name (`detect_set`).
## Buttons are Godot's JoyButton ids (the Xbox layout Godot maps every pad onto), plus the
## TRIGGER_*, STICK_* and DPAD ids below for axes. Draw-only; PadPrompts pairs a glyph
## with its verb.

const SET_AUTO := &"auto"
const SET_XBOX := &"xbox"
const SET_PLAYSTATION := &"playstation"
const SET_SWITCH := &"switch"
const SET_DECK := &"deck"
## The glyph sets drawn (auto resolves to one of them).
const SETS: Array[StringName] = [SET_XBOX, SET_PLAYSTATION, SET_SWITCH, SET_DECK]
## The Settings key that picks the set (W9s adds it; read defensively).
const SETTING := &"pad_glyph_set"

## Face buttons by position (Godot's JoyButton: A is the bottom face button).
const FACE_SOUTH := JOY_BUTTON_A
const FACE_EAST := JOY_BUTTON_B
const FACE_WEST := JOY_BUTTON_X
const FACE_NORTH := JOY_BUTTON_Y
const SHOULDER_L := JOY_BUTTON_LEFT_SHOULDER
const SHOULDER_R := JOY_BUTTON_RIGHT_SHOULDER
const DPAD_UP := JOY_BUTTON_DPAD_UP
const DPAD_DOWN := JOY_BUTTON_DPAD_DOWN
const DPAD_LEFT := JOY_BUTTON_DPAD_LEFT
const DPAD_RIGHT := JOY_BUTTON_DPAD_RIGHT
const STICK_L_CLICK := JOY_BUTTON_LEFT_STICK
const STICK_R_CLICK := JOY_BUTTON_RIGHT_STICK
const MENU := JOY_BUTTON_START
const VIEW := JOY_BUTTON_BACK
## Axes and groups have ids of their own (past Godot's JoyButton range).
const AXIS_BASE := 1000
const TRIGGER_L := AXIS_BASE + JOY_AXIS_TRIGGER_LEFT
const TRIGGER_R := AXIS_BASE + JOY_AXIS_TRIGGER_RIGHT
const STICK_L := AXIS_BASE + 100
const STICK_R := AXIS_BASE + 101
const DPAD := AXIS_BASE + 102
## Every button each set draws (tests check each set has each).
const BUTTONS: Array[int] = [FACE_SOUTH, FACE_EAST, FACE_WEST, FACE_NORTH, SHOULDER_L, SHOULDER_R, TRIGGER_L, TRIGGER_R,
	DPAD, DPAD_UP, DPAD_DOWN, DPAD_LEFT, DPAD_RIGHT, STICK_L, STICK_R, STICK_L_CLICK, STICK_R_CLICK, MENU, VIEW]

## Names per set (tests, screen readers, PadPrompts.texts). Menu / View are drawn as icons.
const NAMES := {
	SET_XBOX: {FACE_SOUTH: "A", FACE_EAST: "B", FACE_WEST: "X", FACE_NORTH: "Y", SHOULDER_L: "LB", SHOULDER_R: "RB",
		TRIGGER_L: "LT", TRIGGER_R: "RT", DPAD: "D-pad", DPAD_UP: "D-pad up", DPAD_DOWN: "D-pad down", DPAD_LEFT: "D-pad left",
		DPAD_RIGHT: "D-pad right", STICK_L: "L stick", STICK_R: "R stick", STICK_L_CLICK: "L3", STICK_R_CLICK: "R3",
		MENU: "Menu", VIEW: "View"},
	SET_PLAYSTATION: {FACE_SOUTH: "Cross", FACE_EAST: "Circle", FACE_WEST: "Square", FACE_NORTH: "Triangle", SHOULDER_L: "L1",
		SHOULDER_R: "R1", TRIGGER_L: "L2", TRIGGER_R: "R2", DPAD: "D-pad", DPAD_UP: "D-pad up", DPAD_DOWN: "D-pad down",
		DPAD_LEFT: "D-pad left", DPAD_RIGHT: "D-pad right", STICK_L: "L stick", STICK_R: "R stick", STICK_L_CLICK: "L3",
		STICK_R_CLICK: "R3", MENU: "Options", VIEW: "Create"},
	SET_SWITCH: {FACE_SOUTH: "B", FACE_EAST: "A", FACE_WEST: "Y", FACE_NORTH: "X", SHOULDER_L: "L", SHOULDER_R: "R",
		TRIGGER_L: "ZL", TRIGGER_R: "ZR", DPAD: "D-pad", DPAD_UP: "D-pad up", DPAD_DOWN: "D-pad down", DPAD_LEFT: "D-pad left",
		DPAD_RIGHT: "D-pad right", STICK_L: "L stick", STICK_R: "R stick", STICK_L_CLICK: "L stick press",
		STICK_R_CLICK: "R stick press", MENU: "Plus", VIEW: "Minus"},
	SET_DECK: {FACE_SOUTH: "A", FACE_EAST: "B", FACE_WEST: "X", FACE_NORTH: "Y", SHOULDER_L: "L1", SHOULDER_R: "R1",
		TRIGGER_L: "L2", TRIGGER_R: "R2", DPAD: "D-pad", DPAD_UP: "D-pad up", DPAD_DOWN: "D-pad down", DPAD_LEFT: "D-pad left",
		DPAD_RIGHT: "D-pad right", STICK_L: "L stick", STICK_R: "R stick", STICK_L_CLICK: "L3", STICK_R_CLICK: "R3",
		MENU: "Menu", VIEW: "View"},
}
## Letters on the face buttons (sets that letter them; PlayStation draws shapes).
const FACE_BUTTONS: Array[int] = [FACE_SOUTH, FACE_EAST, FACE_WEST, FACE_NORTH]
## Pad-name words that pick a set in auto (lower case, first match wins; else Xbox).
const DETECT := [["steam deck", SET_DECK], ["steam", SET_DECK], ["dualsense", SET_PLAYSTATION], ["dualshock", SET_PLAYSTATION],
	["playstation", SET_PLAYSTATION], ["ps5", SET_PLAYSTATION], ["ps4", SET_PLAYSTATION], ["ps3", SET_PLAYSTATION],
	["sony", SET_PLAYSTATION], ["nintendo", SET_SWITCH], ["switch", SET_SWITCH], ["joy-con", SET_SWITCH],
	["pro controller", SET_SWITCH]]

## Glyph height relative to the label step's size, and the width of the wide glyphs
## (shoulders, triggers, sticks' labels) as a multiple of the height.
const HEIGHT_FACTOR := 1.35
const WIDE := 1.6
## Stroke width (share of the height) and the letter size (share of the height; never under
## the caption step).
const STROKE := 0.09
const LETTER := 0.58

## The button drawn (a BUTTONS id).
var button: int = FACE_SOUTH:
	set(value):
		button = value
		_fit()
## The set drawn (&"" = the player's set, `current_set`).
var glyph_set: StringName = &"":
	set(value):
		glyph_set = value
		queue_redraw()


func _init(p_button: int = FACE_SOUTH, p_set: StringName = &"") -> void:
	name = "PadGlyph"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	glyph_set = p_set
	button = p_button


func _fit() -> void:
	custom_minimum_size = glyph_size(button)
	queue_redraw()


func _notification(what: int) -> void:
	if what == NOTIFICATION_THEME_CHANGED:
		_fit()


## The glyph's height at the player's text scale (px).
static func glyph_height() -> float:
	return roundf(UiTheme.font_px(UiTheme.LABEL) * HEIGHT_FACTOR)


## The size glyph `b` takes.
static func glyph_size(b: int) -> Vector2:
	var h := glyph_height()
	return Vector2(h * WIDE if is_wide(b) else h, h)


## True for the glyphs drawn wider than tall (shoulders and triggers).
static func is_wide(b: int) -> bool:
	return b in [SHOULDER_L, SHOULDER_R, TRIGGER_L, TRIGGER_R]


## The set to draw: `Settings.pad_glyph_set` (null or auto: `detect_set` of the first pad).
static func current_set() -> StringName:
	var s: Variant = Settings.get(SETTING)
	var want := StringName(s) if s != null else SET_AUTO
	if SETS.has(want):
		return want
	var pads := Input.get_connected_joypads()
	return detect_set(Input.get_joy_name(pads[0]) if not pads.is_empty() else "")


## The glyph set for a pad called `joy_name` (Input.get_joy_name): PlayStation, Switch or
## Steam Deck by name, else Xbox (Godot's own layout).
static func detect_set(joy_name: String) -> StringName:
	var n := joy_name.to_lower()
	for pair in DETECT:
		if n.contains(String(pair[0])):
			return pair[1]
	return SET_XBOX


## The pad button bound to `action` (a BUTTONS id), or -1 when it has none.
static func button_for_action(action: StringName) -> int:
	if not InputMap.has_action(action):
		return -1
	for ev in InputMap.action_get_events(action):
		if ev is InputEventJoypadButton:
			return (ev as InputEventJoypadButton).button_index
		if ev is InputEventJoypadMotion:
			var axis := (ev as InputEventJoypadMotion).axis
			if axis == JOY_AXIS_TRIGGER_LEFT or axis == JOY_AXIS_TRIGGER_RIGHT:
				return AXIS_BASE + axis
			return STICK_L if axis == JOY_AXIS_LEFT_X or axis == JOY_AXIS_LEFT_Y else STICK_R
	return -1


## The name of button `b` in set `set` ("A", "Cross", "ZL"...; "" when unknown).
static func name_of(b: int, gset: StringName = &"") -> String:
	var s := gset if SETS.has(gset) else current_set()
	return String((NAMES[s] as Dictionary).get(b, ""))


## True when set `set` draws button `b`.
static func has_glyph(gset: StringName, b: int) -> bool:
	return NAMES.has(gset) and (NAMES[gset] as Dictionary).has(b)


## The name shown (tests, accessibility).
func glyph_name() -> String:
	return name_of(button, glyph_set)


func _draw() -> void:
	draw_glyph(self, Rect2(Vector2.ZERO, size), button, glyph_set if SETS.has(glyph_set) else current_set())


## Draws button `b` of set `set` filling `rect` (local to `ci`).
static func draw_glyph(ci: CanvasItem, rect: Rect2, b: int, gset: StringName) -> void:
	var h := minf(rect.size.y, rect.size.x if not is_wide(b) else rect.size.y)
	var c := rect.get_center()
	var w := maxf(1.5, h * STROKE)
	var r := h * 0.5 - w * 0.5
	if FACE_BUTTONS.has(b):
		_face(ci, c, r, w, b, gset)
	elif is_wide(b):
		_tab(ci, rect, w, name_of(b, gset), b == TRIGGER_L or b == TRIGGER_R)
	elif b == DPAD or b == DPAD_UP or b == DPAD_DOWN or b == DPAD_LEFT or b == DPAD_RIGHT:
		_dpad(ci, c, r, w, b)
	elif b == STICK_L or b == STICK_R or b == STICK_L_CLICK or b == STICK_R_CLICK:
		_stick(ci, c, r, w, "L" if b == STICK_L or b == STICK_L_CLICK else "R", b == STICK_L_CLICK or b == STICK_R_CLICK)
	elif b == MENU or b == VIEW:
		_system(ci, c, r, w, b, gset)
	else:
		ci.draw_arc(c, r, 0, TAU, 20, Palette.TEXT_MID, w)


## Xbox's letter colours (§3.3 tokens: green, red, blue, yellow) and PlayStation's shapes'.
static func face_color(b: int, gset: StringName) -> Color:
	if gset == SET_XBOX:
		return XBOX_COLORS.get(b, Palette.TEXT_HI)
	if gset == SET_PLAYSTATION:
		return PLAYSTATION_COLORS.get(b, Palette.TEXT_HI)
	return Palette.TEXT_HI


const XBOX_COLORS := {FACE_SOUTH: Palette.GAIN, FACE_EAST: Palette.HARM, FACE_WEST: Palette.NET_CYAN, FACE_NORTH: Palette.RESIST_GOLD}
const PLAYSTATION_COLORS := {FACE_SOUTH: Palette.NET_CYAN, FACE_EAST: Palette.HARM, FACE_WEST: Palette.STICKER_PINK, FACE_NORTH: Palette.GAIN}


static func _disc(ci: CanvasItem, c: Vector2, r: float, w: float, rim: Color) -> void:
	ci.draw_circle(c, r + w * 0.5, Palette.DESK_DARK)
	ci.draw_arc(c, r, 0, TAU, 28, rim, w, true)


static func _letter(ci: CanvasItem, c: Vector2, h: float, text: String, col: Color) -> void:
	var f := Palette.display()
	var px := maxi(UiTheme.font_px_at(UiTheme.CAPTION, 1.0), roundi(h * LETTER))
	var sz := f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, px)
	ci.draw_string(f, Vector2(c.x - sz.x * 0.5, c.y + (f.get_ascent(px) - f.get_descent(px)) * 0.5), text, HORIZONTAL_ALIGNMENT_LEFT, -1, px, col)


static func _face(ci: CanvasItem, c: Vector2, r: float, w: float, b: int, gset: StringName) -> void:
	var col := face_color(b, gset)
	_disc(ci, c, r, w, col if gset == SET_XBOX else Palette.TEXT_MID)
	if gset == SET_PLAYSTATION:
		var s := r * 0.5
		match b:
			FACE_SOUTH:
				ci.draw_line(c + Vector2(-s, -s), c + Vector2(s, s), col, w * 1.2, true)
				ci.draw_line(c + Vector2(s, -s), c + Vector2(-s, s), col, w * 1.2, true)
			FACE_EAST:
				ci.draw_arc(c, s * 1.05, 0, TAU, 20, col, w * 1.2, true)
			FACE_WEST:
				ci.draw_rect(Rect2(c - Vector2(s, s) * 0.9, Vector2(s, s) * 1.8), col, false, w * 1.2)
			FACE_NORTH:
				var pts := PackedVector2Array([c + Vector2(0, -s * 1.05), c + Vector2(s * 1.05, s * 0.75), c + Vector2(-s * 1.05, s * 0.75), c + Vector2(0, -s * 1.05)])
				ci.draw_polyline(pts, col, w * 1.2, true)
		return
	_letter(ci, c, r * 2.0, name_of(b, gset), col)


static func _tab(ci: CanvasItem, rect: Rect2, w: float, text: String, trigger: bool) -> void:
	var box := rect.grow(-w * 0.5)
	var pts := PackedVector2Array()
	var rad := box.size.y * (0.5 if trigger else 0.3)
	# A trigger is rounded on top (its curved face), a shoulder is a flat bar with soft ends.
	var steps := 6
	for k in steps + 1:
		var a := PI + PI * 0.5 * k / steps
		pts.append(Vector2(box.position.x + rad, box.position.y + rad) + Vector2(cos(a), sin(a)) * rad)
	for k in steps + 1:
		var a := PI * 1.5 + PI * 0.5 * k / steps
		pts.append(Vector2(box.end.x - rad, box.position.y + rad) + Vector2(cos(a), sin(a)) * rad)
	pts.append(Vector2(box.end.x, box.end.y))
	pts.append(Vector2(box.position.x, box.end.y))
	ci.draw_colored_polygon(pts, Palette.DESK_DARK)
	pts.append(pts[0])
	ci.draw_polyline(pts, Palette.TEXT_MID, w, true)
	_letter(ci, box.get_center() + Vector2(0, w * 0.5), box.size.y * 0.95, text, Palette.TEXT_HI)


static func _dpad(ci: CanvasItem, c: Vector2, r: float, w: float, b: int) -> void:
	var arm := r * 0.42
	var dirs := {DPAD_UP: Vector2.UP, DPAD_DOWN: Vector2.DOWN, DPAD_LEFT: Vector2.LEFT, DPAD_RIGHT: Vector2.RIGHT}
	ci.draw_rect(Rect2(c - Vector2(arm, r), Vector2(arm * 2.0, r * 2.0)), Palette.DESK_DARK)
	ci.draw_rect(Rect2(c - Vector2(r, arm), Vector2(r * 2.0, arm * 2.0)), Palette.DESK_DARK)
	for d: int in dirs:
		var v: Vector2 = dirs[d]
		var lit := b == d or b == DPAD
		var tip := c + v * r
		var base := c + v * r * 0.35
		var side := v.orthogonal() * arm * 0.7
		ci.draw_colored_polygon(PackedVector2Array([tip, base + side, base - side]), Palette.FOCUS if lit and b != DPAD else Palette.TEXT_MID)
	var outline := PackedVector2Array([c + Vector2(-arm, -r), c + Vector2(arm, -r), c + Vector2(arm, -arm), c + Vector2(r, -arm), c + Vector2(r, arm),
		c + Vector2(arm, arm), c + Vector2(arm, r), c + Vector2(-arm, r), c + Vector2(-arm, arm), c + Vector2(-r, arm), c + Vector2(-r, -arm),
		c + Vector2(-arm, -arm), c + Vector2(-arm, -r)])
	ci.draw_polyline(outline, Palette.TEXT_MID, w * 0.7, true)


static func _stick(ci: CanvasItem, c: Vector2, r: float, w: float, side: String, click: bool) -> void:
	_disc(ci, c, r, w, Palette.TEXT_MID)
	ci.draw_arc(c, r * 0.6, 0, TAU, 20, Palette.TEXT_MID, w * 0.7, true)
	_letter(ci, c, r * 1.6, side, Palette.TEXT_HI)
	if click:
		# A press: a small arrow down into the stick's top.
		var tip := c + Vector2(r * 0.95, -r * 0.35)
		ci.draw_colored_polygon(PackedVector2Array([tip, tip + Vector2(-r * 0.3, -r * 0.4), tip + Vector2(r * 0.3, -r * 0.4)]), Palette.FOCUS)


static func _system(ci: CanvasItem, c: Vector2, r: float, w: float, b: int, gset: StringName) -> void:
	_disc(ci, c, r, w, Palette.TEXT_MID)
	var col := Palette.TEXT_HI
	var s := r * 0.5
	if gset == SET_SWITCH:
		# Plus and Minus, drawn.
		ci.draw_line(c + Vector2(-s, 0), c + Vector2(s, 0), col, w * 1.3)
		if b == MENU:
			ci.draw_line(c + Vector2(0, -s), c + Vector2(0, s), col, w * 1.3)
		return
	if b == MENU:
		# Three lines (Xbox Menu, the Deck's menu, PlayStation Options).
		for k in 3:
			var y := (k - 1) * s * 0.7
			ci.draw_line(c + Vector2(-s, y), c + Vector2(s, y), col, w)
		return
	if gset == SET_PLAYSTATION:
		# Create: three short rays over a small bar.
		for k in 3:
			var a := -PI * 0.5 + (k - 1) * 0.6
			ci.draw_line(c + Vector2(cos(a), sin(a)) * s * 0.3, c + Vector2(cos(a), sin(a)) * s * 1.1, col, w)
		ci.draw_line(c + Vector2(-s * 0.7, s * 0.6), c + Vector2(s * 0.7, s * 0.6), col, w)
		return
	# View: two overlapping windows.
	ci.draw_rect(Rect2(c + Vector2(-s, -s * 0.8), Vector2(s * 1.3, s * 1.1)), col, false, w * 0.8)
	ci.draw_rect(Rect2(c + Vector2(-s * 0.3, -s * 0.3), Vector2(s * 1.3, s * 1.1)), Palette.DESK_DARK)
	ci.draw_rect(Rect2(c + Vector2(-s * 0.3, -s * 0.3), Vector2(s * 1.3, s * 1.1)), col, false, w * 0.8)
