class_name MenuChip
extends Button
## ART-10 4C: a terminal button with a plain label and a line under it (ART_BIBLE v2 §4.13
## "terminal buttons (`>` caret on hover, no colour-only cue)"; round 33 `title_screen.jpg`
## CONTINUE / TUTORIAL / NEW CAMPAIGN, `ui_kit.jpg` RESPIN chips): navy glass with a cut
## corner, the label in terminal CAPS and the line in the caption step. Hover: a `>` caret
## and a brighter edge; pressed: a cyan fill with ink words; disabled: a grey hatch;
## focus: the theme's lime brackets (§2.10). `text` is the label (tests and screen readers
## read it); `line` the second line. View only.

## Padding (px at 1280x720): sides, top, between the lines, bottom.
const PAD := Vector4(14, 8, 3, 8)
## The caret's room before the label on hover (in label-size shares).
const CARET_SHARE := 1.2
## Hatch spacing on a disabled chip (px).
const HATCH := 7.0

var line: String = ""
var accent: Color = Palette.NET_CYAN
var label_step: int = UiTheme.LABEL
var line_step: int = UiTheme.CAPTION
## The label is already translated (it is shown as given).
var pre_translated := false
## Selected (a tile's chosen value, a tab's open section): a cyan fill and ink words, like a
## press held (§2.10: ON / selected are cyan fills plus a word; lime is only focus).
var selected := false:
	set(v):
		selected = v
		queue_redraw()


func _init(p_text: String = "", p_line: String = "", p_accent: Color = Palette.NET_CYAN) -> void:
	text = p_text
	line = p_line
	accent = p_accent
	focus_mode = Control.FOCUS_ALL
	clip_text = true
	alignment = HORIZONTAL_ALIGNMENT_LEFT
	for box in [&"normal", &"hover", &"pressed", &"hover_pressed", &"disabled"]:
		add_theme_stylebox_override(box, StyleBoxEmpty.new())
	for key in [&"font_color", &"font_hover_color", &"font_pressed_color", &"font_focus_color", &"font_hover_pressed_color", &"font_disabled_color"]:
		add_theme_color_override(key, Palette.AUTO)
	KitState.track(self)
	refit()
	mouse_entered.connect(queue_redraw)
	mouse_exited.connect(queue_redraw)
	focus_exited.connect(queue_redraw)
	button_down.connect(queue_redraw)
	button_up.connect(queue_redraw)


func _ready() -> void:
	Settings.changed.connect(refit)
	refit()


func _exit_tree() -> void:
	if Settings.changed.is_connected(refit):
		Settings.changed.disconnect(refit)


func shown_text() -> String:
	return (text if pre_translated else tr(text)).to_upper()


## The second line as shown (translated where it is set).
func set_line(t: String) -> void:
	line = t
	refit()
	queue_redraw()


## The least width the chip keeps (px), whatever its words.
var min_width: float = 0.0


## Sizes the chip to its words (a Button's own minimum ignores a script's
## _get_minimum_size): custom_minimum_size = its measure, at least `min_width` wide.
func refit() -> void:
	var m := measure()
	custom_minimum_size = Vector2(maxf(min_width, m.x), m.y)


## The size the label, the caret's room and the line need (px).
func measure() -> Vector2:
	var lf := Chrome.caps_font(label_step)
	var lp := Chrome.px(label_step)
	var w := lf.get_string_size(shown_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, lp).x + lp * CARET_SHARE
	var h := lf.get_height(lp)
	if line != "":
		var sp := Chrome.px(line_step)
		w = maxf(w, Palette.mono().get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, sp).x)
		h += PAD.z + Palette.mono().get_height(sp)
	return Vector2(ceilf(w + PAD.x * 2.0), ceilf(h + PAD.y + PAD.w))


## The concept's plates (tools/art/bake_menus_r33.py, wordless): `chip` = the title's terminal
## chip (title.py `static_ui` term_panel; hot / idle), `tab` = ui31.tabs (active / idle), `tile`
## = settings.py tiles (selected / idle). Each a nine-patch at two thirds (board -> game).
const PLATE_DIR := "res://assets/ui/menus/kit/"
const PLATES := {&"chip": ["chip_hot", "chip_idle", 20], &"tab": ["tab_active", "tab_idle", 10], &"tile": ["tile_selected", "tile_idle", 10]}
const PLATE_SCALE := 2.0 / 3.0
## Which concept plate this chip wears (&"" = drawn).
var plate: StringName = &"chip"
static var _plates: Dictionary = {}


static func _plate_box(file: String, margin: int) -> StyleBoxTexture:
	if not _plates.has(file):
		var sb := StyleBoxTexture.new()
		sb.texture = load(PLATE_DIR + file + ".png") as Texture2D
		sb.texture_margin_left = margin
		sb.texture_margin_right = margin
		sb.texture_margin_top = margin
		sb.texture_margin_bottom = margin
		_plates[file] = sb
	return _plates[file]


## Lets the cached plates go (exit).
static func release() -> void:
	_plates.clear()


func _draw() -> void:
	var st := KitState.of(self)
	var r := Rect2(Vector2(0, KitState.lift(st)), size)
	var hot := st == KitState.HOVER or st == KitState.FOCUS or st == KitState.PRESSED
	var pressed := st == KitState.PRESSED or (selected and not disabled)
	if PLATES.has(plate):
		var p: Array = PLATES[plate]
		# The chip's lit plate on hover / focus; a tab's or a tile's filled plate when selected.
		var lit := (hot or selected) if plate == &"chip" else (selected or st == KitState.PRESSED)
		var sb := _plate_box(String(p[0]) if lit else String(p[1]), int(p[2]))
		draw_set_transform(r.position, 0.0, Vector2.ONE * PLATE_SCALE)
		draw_style_box(sb, Rect2(Vector2.ZERO, r.size / PLATE_SCALE))
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
		if plate == &"chip":
			pressed = false  # the chip's plate stays navy: its words stay white
	else:
		var glass := Color(accent, 0.85) if pressed else (Palette.TERMINAL_BG if not hot else Palette.TERMINAL_BG.lerp(accent, 0.12))
		Chrome.draw_terminal(self, r, accent if not disabled else Palette.DISABLED, glass, Chrome.CHAMFER * 0.8)
	if disabled:
		var x := r.position.x
		while x < r.end.x + r.size.y:
			draw_line(Vector2(x, r.end.y), Vector2(x - r.size.y, r.position.y), Color(Palette.DISABLED, 0.35), 1.0)
			x += HATCH
	var lf := Chrome.caps_font(label_step)
	var lp := Chrome.px(label_step)
	var ink := Palette.GLYPH_INK if pressed else (Palette.TEXT_HI if not disabled else Palette.TEXT_LO)
	var x0 := r.position.x + PAD.x
	if plate != &"chip" and plate != &"":
		# Tabs and tiles centre their words (ui31.tabs, settings.py tiles).
		x0 = r.position.x + (r.size.x - lf.get_string_size(shown_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, lp).x) * 0.5
	var y := r.position.y + PAD.y + lf.get_ascent(lp)
	if hot and not disabled:
		var centred := plate != &"chip" and plate != &""
		draw_string(lf, Vector2(x0 - (lp * CARET_SHARE if centred else 0.0), y), ">", HORIZONTAL_ALIGNMENT_LEFT, -1, lp, ink if pressed else accent)
		if not centred:
			x0 += lp * CARET_SHARE
	draw_string(lf, Vector2(x0, y), shown_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, lp, ink)
	if line != "":
		var sp := Chrome.px(line_step)
		var ly := y + lf.get_descent(lp) + PAD.z + Palette.mono().get_ascent(sp)
		draw_string(Palette.mono(), Vector2(r.position.x + PAD.x, ly), line, HORIZONTAL_ALIGNMENT_CENTER if plate != &"chip" else HORIZONTAL_ALIGNMENT_LEFT, r.size.x - PAD.x * 2.0, sp,
			Palette.GLYPH_INK if pressed else (Palette.TEXT_MID if not disabled else Palette.TEXT_LO))
	KitState.draw_frame(self, r, st, false)
