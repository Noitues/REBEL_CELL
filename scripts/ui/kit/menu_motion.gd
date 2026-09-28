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
## while the box slides. Typing is drawn (ANIM-R1): the line's own words stay whole (its
## `text` never changes, so screen readers and tests read it all and nothing re-lays out);
## its font colours go clear while this control draws the typed part on top, a character
## at a time. A press completes the motion; a press that works the menu passes on (ANIM-R2,
## MotionSkip): a focus move (arrows, D-pad, Tab), an accept (Enter, Space, A) and a click
## on one of the menu's lines, since a menu must never drop a fast tap (Down then Enter the
## next frame activates the new line). Other presses are consumed. The first focus
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
## The line's font colour overrides while its words are drawn here ({name: colour or null}).
var _saved_colors: Dictionary = {}
var _type_color: Color = Color.WHITE
var _type_outline: Color = Color(0, 0, 0, 0)
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
	var n := _shown_words().length()
	var d := minf(Motion.seconds(&"menu_type") * n, Motion.amplitude(&"menu_type") / maxf(Motion.speed, Motion.SPEED_MIN))
	_hide_words()
	_set_typed(0)
	var e := Motion.entry(&"menu_type")
	_type_tween = create_tween()
	_type_tween.tween_method(func(v: float) -> void: _set_typed(roundi(v)), 0.0, float(n), d).set_ease(e.ease).set_trans(e.trans)
	_type_tween.tween_callback(_end_typing)


## The line's words as it draws them (translated when it translates).
func _shown_words() -> String:
	return _line.atr(_line.text) if _line != null else ""


func _set_typed(k: int) -> void:
	if _line == null or not is_instance_valid(_line):
		return
	if _typed >= 0 and _line.text != _full_text:
		# Someone relabelled the line mid-typing (a key hint changed): its new words show.
		_end_typing()
		return
	_typed = clampi(k, 0, _shown_words().length())
	queue_redraw()


## Typed characters shown so far (-1 when the line isn't typing: its words are whole).
func typed_count() -> int:
	return _typed


## The line's own lettering goes clear (this control draws the typed part on top).
func _hide_words() -> void:
	_saved_colors.clear()
	_type_color = _line.get_theme_color(&"font_focus_color")
	_type_outline = _line.get_theme_color(&"font_outline_color")
	for c in FONT_COLORS:
		_saved_colors[c] = _line.get_theme_color(c) if _line.has_theme_color_override(c) else null
		_line.add_theme_color_override(c, Color(0, 0, 0, 0))


func _show_words() -> void:
	if _line == null or not is_instance_valid(_line):
		_saved_colors.clear()
		return
	for c in _saved_colors:
		if _saved_colors[c] == null:
			_line.remove_theme_color_override(c)
		else:
			_line.add_theme_color_override(c, _saved_colors[c])
	_saved_colors.clear()


## The Button font colours cleared while a line types in.
const FONT_COLORS: Array[StringName] = [&"font_color", &"font_focus_color", &"font_hover_color", &"font_pressed_color",
	&"font_hover_pressed_color", &"font_disabled_color", &"font_outline_color"]


func _end_typing() -> void:
	if _type_tween != null and _type_tween.is_valid():
		_type_tween.kill()
	_type_tween = null
	if not _saved_colors.is_empty():
		_show_words()
	_typed = -1
	queue_redraw()


func _input(event: InputEvent) -> void:
	# ANIM-R1 / R2 (MotionSkip): a press completes the typing and the slide; a press that
	# works the menu (a focus move, an accept, a click on a line) is let through, any other
	# is consumed.
	if not (typing() or sliding()) or not MotionSkip.is_press(event):
		return
	finish()
	if not works_menu(event):
		MotionSkip.consume(self)


## True when `event` works this menu (ANIM-R2): a focus move, an accept, or a click on one
## of its lines. Such a press completes the line's motion and passes on.
func works_menu(event: InputEvent) -> bool:
	if _is_focus_move(event) or event.is_action(&"ui_accept"):
		return true
	if event is InputEventMouseButton and menu != null and is_instance_valid(menu):
		var at := (event as InputEventMouseButton).global_position
		for b in menu.get_children():
			if b is Button and (b as Button).is_visible_in_tree() and (b as Button).get_global_rect().has_point(at):
				return true
	return false


static func _is_focus_move(event: InputEvent) -> bool:
	for a in [&"ui_up", &"ui_down", &"ui_left", &"ui_right", &"ui_focus_next", &"ui_focus_prev"]:
		if event.is_action(a):
			return true
	return false


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
	var words := _shown_words() if _typed < 0 else _shown_words().substr(0, _typed)
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
	if _typed >= 0:
		# The typed part, where the line draws its words (they are clear meanwhile).
		var font := _line.get_theme_font(&"font")
		var fs := _line.get_theme_font_size(&"font_size")
		var full := _shown_words()
		var x := _text_x()
		if _line.alignment == HORIZONTAL_ALIGNMENT_CENTER:
			x = (_line.size.x - font.get_string_size(full, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x) * 0.5
		elif _line.alignment == HORIZONTAL_ALIGNMENT_RIGHT:
			var sb := _line.get_theme_stylebox(&"normal")
			x = _line.size.x - (sb.get_margin(SIDE_RIGHT) if sb != null else 0.0) - font.get_string_size(full, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var base := Vector2(x, (_line.size.y - font.get_height(fs)) * 0.5 + font.get_ascent(fs))
		var part := full.substr(0, _typed)
		var outline := _line.get_theme_constant(&"outline_size")
		if outline > 0 and _type_outline.a > 0.0:
			draw_string_outline(font, base, part, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, outline, _type_outline)
		draw_string(font, base, part, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, _type_color)
	if _line.has_focus() and _caret_on() and _line.text != "" and _line.alignment == HORIZONTAL_ALIGNMENT_LEFT:
		draw_rect(caret_rect(), Color(_line.get_theme_color(&"font_focus_color"), 0.85))
