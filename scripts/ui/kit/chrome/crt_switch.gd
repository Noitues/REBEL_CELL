class_name CrtSwitch
extends CheckButton
## ART-10 4C: an Options row with an ON / OFF switch (ART_BIBLE v2 §4.13 "Settings"; round 31
## `settings_menu.jpg`, round 33 `ui_kit.jpg` TOGGLES): the setting's name in terminal CAPS,
## what it does under it in Plex, the switch at the right (ON = a cyan pill with its word
## and the knob right; OFF = an outlined pill, knob left; never colour alone). Focus: the
## lime brackets round the row (the theme) and a `>` caret before the name; the row never
## grows with the pad focus scale (UiFocus.META_NO_SCALE, ART-0 carry-over). `text` keeps
## the whole setting line ("Name (what it does)"): the name is the part before " (", the
## line the part inside. An optional `note` callable returns a warn chip shown under the
## line ("LIMITED: ..."; "" = none). Still a CheckButton: `button_pressed` and `toggled`
## work as before. View only.

## Layout (px at 1280x720): side pads, top / bottom pads, gap name -> line, the switch.
const PAD := Vector2(12, 7)
const LINE_GAP := 2.0
const PILL := Vector2(48, 22)
const KNOB_INSET := 3.0
## The OFF track's fill: this share of the cyan over the glass.
const OFF_TRACK := 0.22
## The caret's room before the name (shares of the name's size).
const CARET_SHARE := 1.1
const NAME_STEP := UiTheme.LABEL
const LINE_STEP := UiTheme.BODY
const NOTE_STEP := UiTheme.CAPTION

## The baked art this view draws, held while it lives (a texture loaded only inside _draw
## was freed before the frame drew it: a white box).
var _held: Dictionary = {}
var note: Callable = Callable()


func _init(p_text: String = "") -> void:
	text = p_text
	clip_text = true
	set_meta(UiFocus.META_NO_SCALE, true)
	for box in [&"normal", &"hover", &"pressed", &"hover_pressed", &"disabled"]:
		add_theme_stylebox_override(box, StyleBoxEmpty.new())
	for key in [&"font_color", &"font_hover_color", &"font_pressed_color", &"font_focus_color", &"font_hover_pressed_color", &"font_disabled_color"]:
		add_theme_color_override(key, Palette.AUTO)
	var none := ImageTexture.new()
	for icon in [&"checked", &"unchecked", &"checked_disabled", &"unchecked_disabled", &"checked_mirrored", &"unchecked_mirrored"]:
		add_theme_icon_override(icon, none)
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	KitState.track(self)
	for s in [mouse_entered, mouse_exited, focus_exited]:
		(s as Signal).connect(queue_redraw)
	toggled.connect(func(_on: bool) -> void: queue_redraw())
	resized.connect(_rewrap)
	refit()


func _ready() -> void:
	Settings.changed.connect(_settings_changed)
	refit()


func _exit_tree() -> void:
	if Settings.changed.is_connected(_settings_changed):
		Settings.changed.disconnect(_settings_changed)


func _settings_changed() -> void:
	refit()
	queue_redraw()


## The setting's name (CAPS) and what it does, from `text` ("Name (what it does)").
func parts() -> PackedStringArray:
	var t := tr(text) if can_auto_translate() else text
	var at := t.find(" (")
	if at < 0:
		return PackedStringArray([t.to_upper(), ""])
	var rest := t.substr(at + 2)
	var close := rest.rfind(")")
	if close >= 0:
		rest = rest.substr(0, close) + rest.substr(close + 1)
	return PackedStringArray([(t.substr(0, at) + (t.substr(t.length() - 1) if t.ends_with("»") else "")).to_upper(), rest.left(1).to_upper() + rest.substr(1)])


func _note_text() -> String:
	return String(note.call()) if note.is_valid() else ""


## The width changed: the line rewraps, the row takes its new height (only the height:
## the width never follows its own size, so layout cannot loop).
func _rewrap() -> void:
	var h := measure(size.x).y
	if not is_equal_approx(custom_minimum_size.y, h):
		custom_minimum_size.y = h
		queue_redraw()


## Sizes the row to its words (a Button's own minimum ignores a script's
## _get_minimum_size); called on build, on a Settings change and when its note may change.
func refit() -> void:
	custom_minimum_size = measure(size.x)
	queue_redraw()


## The room the line wraps in at row width `width` (px).
func _line_room(width: float) -> float:
	var np := Chrome.px(NAME_STEP)
	return maxf(1.0, width - (PAD.x + np * CARET_SHARE) - PAD.x * 2.0 - PILL.x * Settings.text_scale)


## The size the name, the line (wrapped at `width`, whole words; 0 = unwrapped), the note
## chip and the switch need (px). The least width is the name or the line's longest word.
func measure(width: float = 0.0) -> Vector2:
	var p := parts()
	var nf := Chrome.caps_font(NAME_STEP)
	var np := Chrome.px(NAME_STEP)
	# The name wraps at its words too (a narrow host at big text: the pause menu at 2.0).
	var w := _longest_word(nf, p[0], np) + np * CARET_SHARE
	var name_full := nf.get_string_size(p[0], HORIZONTAL_ALIGNMENT_LEFT, -1, np).x
	var h := nf.get_multiline_string_size(p[0], HORIZONTAL_ALIGNMENT_LEFT, _line_room(width) if width > 0.0 else name_full, np, -1, WRAP).y
	if p[1] != "":
		var lp := Chrome.px(LINE_STEP)
		var bf := Chrome.body_font()
		w = maxf(w, _longest_word(bf, p[1], lp) + np * CARET_SHARE)
		var full := bf.get_string_size(p[1], HORIZONTAL_ALIGNMENT_LEFT, -1, lp).x
		var room := _line_room(width) if width > 0.0 else full
		h += LINE_GAP + bf.get_multiline_string_size(p[1], HORIZONTAL_ALIGNMENT_LEFT, room, lp, -1, TextServer.BREAK_MANDATORY | TextServer.BREAK_WORD_BOUND).y
	var n := _note_text()
	if n != "":
		var cp := Chrome.px(NOTE_STEP)
		h += LINE_GAP * 2.0 + Palette.mono().get_height(cp) + 4.0
	var s := Settings.text_scale
	return Vector2(ceilf(w + PAD.x * 3.0 + PILL.x * s), ceilf(h + PAD.y * 2.0))


## Whole-word line breaks for the name and the line.
const WRAP := TextServer.BREAK_MANDATORY | TextServer.BREAK_WORD_BOUND


static func _longest_word(f: Font, t: String, px: int) -> float:
	var longest := 0.0
	for word in t.split(" ", false):
		longest = maxf(longest, f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x)
	return longest


func _draw() -> void:
	var st := KitState.of(self)
	var hot := st == KitState.HOVER or st == KitState.FOCUS or st == KitState.PRESSED
	var r := Rect2(Vector2.ZERO, size)
	if hot:
		draw_rect(r, Color(Palette.NET_CYAN, 0.08))
	draw_line(Vector2(PAD.x, r.end.y - 0.5), Vector2(r.end.x - PAD.x, r.end.y - 0.5), Color(Palette.NET_CYAN, 0.15), 1.0)
	var p := parts()
	var nf := Chrome.caps_font(NAME_STEP)
	var np := Chrome.px(NAME_STEP)
	var x := PAD.x + np * CARET_SHARE
	var y := PAD.y + nf.get_ascent(np)
	var dim := disabled
	if hot and not dim:
		draw_string(nf, Vector2(PAD.x, y), ">", HORIZONTAL_ALIGNMENT_LEFT, -1, np, Palette.FOCUS if st == KitState.FOCUS else Palette.NET_CYAN)
	var name_h := nf.get_multiline_string_size(p[0], HORIZONTAL_ALIGNMENT_LEFT, _line_room(size.x), np, -1, WRAP).y
	draw_multiline_string(nf, Vector2(x, y), p[0], HORIZONTAL_ALIGNMENT_LEFT, _line_room(size.x), np, -1, Palette.TEXT_LO if dim else Palette.TEXT_HI, WRAP)
	var s := Settings.text_scale
	var pill := Rect2(Vector2(r.end.x - PAD.x - PILL.x * s, PAD.y + (nf.get_height(np) - PILL.y * s) * 0.5), PILL * s)
	var line_y := y + name_h - nf.get_ascent(np)
	if p[1] != "":
		var lp := Chrome.px(LINE_STEP)
		line_y += LINE_GAP + Chrome.body_font().get_ascent(lp)
		var bf := Chrome.body_font()
		var room := _line_room(size.x)
		draw_multiline_string(bf, Vector2(x, line_y), p[1], HORIZONTAL_ALIGNMENT_LEFT, room, lp, -1, Palette.TEXT_LO if dim else Palette.TEXT_MID,
			TextServer.BREAK_MANDATORY | TextServer.BREAK_WORD_BOUND)
		line_y += bf.get_multiline_string_size(p[1], HORIZONTAL_ALIGNMENT_LEFT, room, lp, -1, TextServer.BREAK_MANDATORY | TextServer.BREAK_WORD_BOUND).y - bf.get_ascent(lp)
	var n := _note_text()
	if n != "":
		var cp := Chrome.px(NOTE_STEP)
		var cf := Palette.mono()
		var tw := cf.get_string_size(n, HORIZONTAL_ALIGNMENT_LEFT, -1, cp).x
		var chip := Rect2(Vector2(r.end.x - PAD.x - tw - 10.0, line_y + LINE_GAP * 2.0), Vector2(tw + 8.0, cf.get_height(cp) + 2.0))
		draw_rect(chip, Color(Palette.WARN, 0.12))
		draw_rect(chip, Palette.WARN, false, 1.0)
		draw_string(cf, Vector2(chip.position.x + 4.0, chip.position.y + 1.0 + cf.get_ascent(cp)), n, HORIZONTAL_ALIGNMENT_LEFT, -1, cp, Palette.WARN)
	_draw_pill(pill, button_pressed, dim)
	KitState.draw_frame(self, r, st, false)


## The switch: ON = cyan fill, ink "ON", knob right; OFF = outline, "OFF", knob left.
## The concept's pill switch (round 31 ui31.toggle, baked by tools/art/bake_menus_r33.py: on /
## off x idle / hover / disabled), at two thirds (board -> game) with the text scale.
const TOGGLE_DIR := "res://assets/ui/menus/kit/"
const TOGGLE_SCALE := 2.0 / 3.0


func _draw_pill(pill: Rect2, on: bool, dim: bool) -> void:
	var st := "disabled" if dim else ("hover" if KitState.of(self) in [KitState.HOVER, KitState.FOCUS] else "idle")
	var path := TOGGLE_DIR + "toggle_%s_%s.png" % ["on" if on else "off", st]
	if ResourceLoader.exists(path):
		var tex := Chrome.held(_held, path)
		var sz := tex.get_size() * TOGGLE_SCALE * Settings.text_scale
		draw_texture_rect(tex, Rect2(Vector2(pill.end.x - sz.x, pill.get_center().y - sz.y * 0.5), sz), false)
		return
	var cyan := Palette.DISABLED if dim else Palette.NET_CYAN
	var rad := pill.size.y * 0.5
	var shape := _capsule(pill, rad)
	# OFF keeps a visible track (audit P2: a lone knob read as a bullet): a dim cyan fill and
	# the full outline, the knob on the left and the word OFF.
	draw_colored_polygon(shape, cyan if on else Palette.TERMINAL_BG.lerp(cyan, OFF_TRACK))
	var edge := shape.duplicate()
	edge.append(shape[0])
	draw_polyline(edge, cyan, 1.5, true)
	var kr := rad - KNOB_INSET
	var kx := pill.end.x - rad if on else pill.position.x + rad
	draw_circle(Vector2(kx, pill.position.y + rad), kr, Palette.TEXT_HI)
	var f := Palette.mono()
	var cp := Chrome.px(UiTheme.CAPTION)
	var word := tr("ON") if on else tr("OFF")
	var tx := pill.position.x + rad * 0.5 if on else pill.position.x + rad * 2.0
	draw_string(f, Vector2(tx, pill.position.y + (pill.size.y + f.get_ascent(cp) - f.get_descent(cp)) * 0.5), word, HORIZONTAL_ALIGNMENT_LEFT, pill.size.x - rad * 2.2, cp,
		Palette.GLYPH_INK if on else cyan)


static func _capsule(r: Rect2, rad: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	var steps := 10
	for i in steps + 1:
		var a := PI * 0.5 + PI * float(i) / steps
		pts.append(Vector2(r.position.x + rad, r.position.y + rad) + Vector2(cos(a), sin(a)) * rad)
	for i in steps + 1:
		var a := -PI * 0.5 + PI * float(i) / steps
		pts.append(Vector2(r.end.x - rad, r.position.y + rad) + Vector2(cos(a), sin(a)) * rad)
	return pts
