class_name MenuMotion
extends Control
## Terminal menu motion (Animation pass ANIM-6, ANIMATION_HANDOFF 4.18, STYLE_GUIDE 5.3): on a
## list of menu lines (the title's main menu, the HQ deck menu, the pause menu) the focus
## highlight slides from the old line to the new one (`menu_highlight`), the new line
## types in (`menu_type`: seconds per character, at most its amplitude for a line) and a
## block caret blinks at the end of the focused line's words (`menu_cursor_blink`, the
## terminal's `> ITEM_` cursor).
##
## The caret and the sliding box are drawn by this control, a child of the focused line
## (it moves with focus; no container lays it out). The line's own focus box is hidden only
## while the box slides. Typing shows the line's words a character at a time with the
## line's size held, so nothing around it moves; a key press completes it. The first focus
## after `attach` (a page opening or refreshing) shows at once: the page's own entrance is
## the motion then. Under reduce effects and headless nothing types or slides and the caret
## holds steady. View only.

const NODE_NAME := "MenuCursor"
## Caret size relative to the line's font size, and its gap after the words.
const CARET_W := 0.5
const CARET_H := 0.8
const CARET_GAP := 3.0
## Share of the blink period the caret shows.
const CARET_ON_SHARE := 0.5

## The menu this motion serves (its Button children are the lines).
var menu: Control = null
var _line: Button = null
var _from: Rect2 = Rect2()
var _slide: float = 1.0
var _slide_tween: Tween = null
var _hidden_focus: StyleBox = null
var _had_focus_override: bool = false
var _full_text: String = ""
var _typed: int = -1
var _type_tween: Tween = null
var _held_min: Vector2 = Vector2.ZERO
var _had_min: Vector2 = Vector2.ZERO
var _blink_t: float = 0.0
var _quiet: bool = true
## The last line that had focus (the highlight slides from it).
var _prev_rect: Rect2 = Rect2()


## Gives the Button lines of `p_menu` the menu motion; returns the motion (or the one they
## already have).
static func attach(p_menu: Control) -> MenuMotion:
	var old := of(p_menu)
	if old != null:
		return old
	var m := MenuMotion.new()
	m.menu = p_menu
	p_menu.set_meta(&"menu_motion", m)
	for b in p_menu.get_children():
		if b is Button:
			(b as Button).focus_entered.connect(m._on_focus.bind(b))
			(b as Button).focus_exited.connect(m._on_blur.bind(b))
			if m.get_parent() == null:
				# Lives on the first line until a line takes focus (freed with the menu).
				b.add_child(m)
	if m.get_parent() == null:
		m.free()
		p_menu.remove_meta(&"menu_motion")
		return null
	return m


## The motion on `p_menu`, or null.
static func of(p_menu: Control) -> MenuMotion:
	if p_menu == null or not p_menu.has_meta(&"menu_motion"):
		return null
	var m: Variant = p_menu.get_meta(&"menu_motion")
	return m as MenuMotion if m != null and is_instance_valid(m) else null


func _init() -> void:
	name = NODE_NAME
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE


## The line with focus now (null when focus is elsewhere).
func line() -> Button:
	return _line


## True while the focused line is still typing in.
func typing() -> bool:
	return _typed >= 0


## True while the highlight slides.
func sliding() -> bool:
	return _slide < 1.0


## Ends the typing and the slide at once (the line's words whole, its box in place).
func finish() -> void:
	_end_typing()
	_end_slide()


func _on_focus(b: Button) -> void:
	var from := _prev_rect if _prev_rect.has_area() and _prev_rect != b.get_global_rect() else Rect2()
	finish()
	_line = b
	if get_parent() != b:
		if get_parent() != null:
			get_parent().remove_child(self)
		b.add_child(self)
	position = Vector2.ZERO
	size = b.size
	_blink_t = 0.0
	var quiet := _quiet
	_quiet = false
	if quiet:
		queue_redraw()
		return
	if from.has_area():
		_start_slide(from)
	_start_typing()
	queue_redraw()


func _on_blur(b: Button) -> void:
	if b != _line:
		return
	finish()
	_prev_rect = b.get_global_rect()
	_line = null
	queue_redraw()


func _start_slide(from: Rect2) -> void:
	if not Motion.live(&"menu_highlight"):
		return
	_from = from
	_had_focus_override = _line.has_theme_stylebox_override(&"focus")
	_hidden_focus = _line.get_theme_stylebox(&"focus")
	_line.add_theme_stylebox_override(&"focus", StyleBoxEmpty.new())
	_slide = 0.0
	var e := Motion.entry(&"menu_highlight")
	_slide_tween = create_tween()
	_slide_tween.tween_method(_set_slide, 0.0, 1.0, Motion.seconds(&"menu_highlight")).set_ease(e.ease).set_trans(e.trans)
	_slide_tween.tween_callback(_end_slide)


func _set_slide(v: float) -> void:
	_slide = v
	queue_redraw()


func _end_slide() -> void:
	if _slide_tween != null and _slide_tween.is_valid():
		_slide_tween.kill()
	_slide_tween = null
	if _slide < 1.0 and _line != null and is_instance_valid(_line):
		if _had_focus_override and _hidden_focus != null:
			_line.add_theme_stylebox_override(&"focus", _hidden_focus)
		else:
			_line.remove_theme_stylebox_override(&"focus")
	_slide = 1.0
	_hidden_focus = null
	queue_redraw()


func _start_typing() -> void:
	if not Motion.live(&"menu_type") or _line.text.length() < 2:
		return
	_full_text = _line.text
	_had_min = _line.custom_minimum_size
	_held_min = _line.get_combined_minimum_size()
	_line.custom_minimum_size = _held_min
	var n := _full_text.length()
	var d := minf(Motion.seconds(&"menu_type") * n, Motion.amplitude(&"menu_type") / maxf(Motion.speed, Motion.SPEED_MIN))
	_set_typed(0)
	var e := Motion.entry(&"menu_type")
	_type_tween = create_tween()
	_type_tween.tween_method(func(v: float) -> void: _set_typed(roundi(v)), 0.0, float(n), d).set_ease(e.ease).set_trans(e.trans)
	_type_tween.tween_callback(_end_typing)


func _set_typed(k: int) -> void:
	if _line == null or not is_instance_valid(_line):
		return
	if _typed >= 0 and _line.text != _full_text.substr(0, _typed):
		# Someone relabelled the line mid-typing (a key hint changed): it keeps their words.
		_full_text = _line.text
		_typed = -1
		_line.custom_minimum_size = _had_min
		return
	_typed = clampi(k, 0, _full_text.length())
	_line.text = _full_text.substr(0, _typed)
	queue_redraw()


func _end_typing() -> void:
	if _type_tween != null and _type_tween.is_valid():
		_type_tween.kill()
	_type_tween = null
	if _typed >= 0 and _line != null and is_instance_valid(_line):
		if _line.text == _full_text.substr(0, _typed):
			_line.text = _full_text
		_line.custom_minimum_size = _had_min
	_typed = -1
	queue_redraw()


func _input(event: InputEvent) -> void:
	if (event is InputEventKey and event.pressed) or (event is InputEventJoypadButton and event.pressed):
		if typing():
			_end_typing()


func _process(delta: float) -> void:
	if _line == null:
		return
	if size != _line.size:
		size = _line.size
	if Motion.live(&"menu_cursor_blink"):
		var was := _caret_on()
		_blink_t += delta
		if _caret_on() != was:
			queue_redraw()


## Whether the caret shows now (steady when the blink doesn't play).
func _caret_on() -> bool:
	if not Motion.live(&"menu_cursor_blink"):
		return true
	var period := maxf(0.01, Motion.entry(&"menu_cursor_blink").duration * 2.0)
	return fmod(_blink_t, period) < period * CARET_ON_SHARE


## Where the line's words start (local x): the box's left margin, the icon and its gap.
func _text_x() -> float:
	var sb := _line.get_theme_stylebox(&"normal")
	var x := sb.get_margin(SIDE_LEFT) if sb != null else 0.0
	# The line's own icon, else its theme's (a MenuItem's "> " chevron).
	var icon: Texture2D = _line.icon if _line.icon != null else (_line.get_theme_icon(&"icon") if _line.has_theme_icon(&"icon") else null)
	if icon != null:
		var iw := float(icon.get_width())
		var cap := _line.get_theme_constant(&"icon_max_width")
		if cap > 0:
			iw = minf(iw, float(cap))
		x += iw + _line.get_theme_constant(&"h_separation")
	return x


## The caret's rect (local to the line).
func caret_rect() -> Rect2:
	if _line == null:
		return Rect2()
	var font := _line.get_theme_font(&"font")
	var fs := _line.get_theme_font_size(&"font_size")
	var words := _line.text
	var w := font.get_string_size(words, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var x := minf(_text_x() + w + CARET_GAP, _line.size.x - fs * CARET_W)
	var h := fs * CARET_H
	return Rect2(Vector2(x, (_line.size.y - h) * 0.5), Vector2(fs * CARET_W, h))


func _draw() -> void:
	if _line == null or not is_instance_valid(_line):
		return
	if _slide < 1.0 and _hidden_focus != null:
		var to := _line.get_global_rect()
		var r := Rect2(_from.position.lerp(to.position, _slide), _from.size.lerp(to.size, _slide))
		draw_style_box(_hidden_focus, Rect2(r.position - to.position, r.size))
	if _line.has_focus() and _caret_on() and _line.text != "" and _line.alignment == HORIZONTAL_ALIGNMENT_LEFT:
		draw_rect(caret_rect(), Color(_line.get_theme_color(&"font_focus_color"), 0.85))
