class_name HighContrast
extends RefCounted
## High-contrast mode (ART_BIBLE §12, art pass W9; ART-0 C, ported from art-pass ec07661):
## turns a built UiTheme into its high-contrast variant in place. `UiTheme.build()` calls
## `apply` as its last step while `Settings.high_contrast` is on, so the theme rebuilds
## through the usual Settings.changed path. Rules:
## - every box with a fill becomes opaque #000 (no glass, blur or scrim transparency);
##   a box that marked its state with a tint (hover, pressed, a highlight) keeps that tint
##   as an opaque edge instead, so the state still reads;
## - fills that ARE the information (scroll grabbers, the slider's filled part) stay their
##   colour, made opaque;
## - buttons get a solid HC_BUTTON_BORDER px edge and focus a solid HC_FOCUS_BORDER px
##   FOCUS edge; no soft shadows;
## - every font colour becomes TEXT (focus: FOCUS, disabled: DISABLED_TEXT), reaching 7:1
##   on #000 (HC_MIN_CONTRAST; disabled labels keep more than §3.7's 4.5:1).
## Views that override colours on their own nodes (paper components, custom _draw) are
## outside the theme: they read `Settings.high_contrast` themselves (each ART-n batch
## restyles its views with it).
##
## ART-0 C: the three colours are area E's semantic tokens (TEXT_HI, TEXT_MID, FOCUS).

## The panel colour behind high-contrast text (§12: "TEXT_HI on #000").
const BG := Palette.HC_BG
## High-contrast text.
const TEXT := Palette.TEXT_HI
## High-contrast focus.
const FOCUS := Palette.FOCUS
## High-contrast disabled words (far above §3.7's 4.5:1 on BG).
const DISABLED_TEXT := Palette.TEXT_MID
## §12: the minimum contrast of theme text in high-contrast mode.
const HC_MIN_CONTRAST := 7.0
## Edge width of buttons (every state) in high-contrast mode, px.
const HC_BUTTON_BORDER := 3
## Edge width of the focus box in high-contrast mode, px (§6: visible from 3 m).
const HC_FOCUS_BORDER := 4
## Edge width given to a box whose state was only a tint, px.
const HC_TINT_BORDER := 2
## M14 12Q-ACCESS (L78): the least edge any edged box keeps in high contrast, px ("thick edges").
const HC_EDGE_MIN := 2
## M14 12Q-ACCESS: an edge a view draws itself is this much wider in high contrast.
const HC_EDGE_SCALE := 2.0
## M14 12Q-ACCESS: the BG outline that backs light words over the city and the art in high
## contrast (outline_size, as a share of the font px, and its least px): the words reach
## HC_MIN_CONTRAST against it whatever is behind.
const HC_OUTLINE_SHARE := 0.25
const HC_OUTLINE_MIN := 4
## Words with less contrast than this on BG are ink: they sit on paper or a sticker.
const INK_MAX_CONTRAST := 2.5
## Words given less alpha than this are hidden (a layout stand-in, a reveal not begun).
const HIDDEN_ALPHA := 0.05
## The steps of the search for the least change that lifts a colour to HC_MIN_CONTRAST.
const LIFT_STEPS := 14
## Theme types whose boxes are buttons (their variations are found by base type).
const BUTTON_TYPES: Array[StringName] = [&"Button", &"OptionButton", &"CheckButton", &"CheckBox", &"MenuButton"]
## Stylebox names whose fill is the information (kept, made opaque).
const FILL_BOXES: Array[StringName] = [&"grabber", &"grabber_highlight", &"grabber_pressed",
	&"grabber_area", &"grabber_area_highlight", &"fill"]
## Stylebox names drawn only as a focus ring.
const FOCUS_BOXES: Array[StringName] = [&"focus", &"tab_focus"]
## Font colour names that show focus.
const FOCUS_COLORS: Array[StringName] = [&"font_focus_color"]
## Font colour names of unavailable controls.
const DISABLED_COLORS: Array[StringName] = [&"font_disabled_color", &"font_placeholder_color", &"font_readonly_color"]
## Font colour names that are outlines or shadows (made solid black, not text colour).
const DARK_COLORS: Array[StringName] = [&"font_outline_color", &"font_shadow_color"]


## Makes `theme` high contrast in place (see the class notes). Safe to call twice.
static func apply(theme: Theme) -> void:
	if theme == null:
		return
	var done := {}
	for type in theme.get_type_list():
		var is_button := _is_button(theme, type)
		for box_name in theme.get_stylebox_list(type):
			var sb := theme.get_stylebox(box_name, type)
			if done.has(sb):
				continue
			if sb is StyleBoxFlat:
				done[sb] = true
				_box(sb as StyleBoxFlat, box_name, is_button)
			elif sb is StyleBoxBrackets:
				# ART-0 F (ported from art-pass W2 / W9): the focus brackets, solid FOCUS and
				# thickened for 3 m (HC_FOCUS_BORDER).
				done[sb] = true
				var br := sb as StyleBoxBrackets
				br.color = FOCUS
				br.thickness = float(HC_FOCUS_BORDER)
		for color_name in theme.get_color_list(type):
			var c := _color(color_name, theme.get_color(color_name, type))
			theme.set_color(color_name, type, c)


## The colour text `color_name` takes in high contrast (`current` when it isn't text).
static func text_color(color_name: StringName, current: Color) -> Color:
	return _color(color_name, current)


## The fill a high-contrast box shows behind its text: opaque #000 unless it is one of
## FILL_BOXES (tests measure text against this).
static func is_text_box(box_name: StringName) -> bool:
	return not FILL_BOXES.has(box_name)


## M14 12Q-ACCESS (L78): restyles box `sb` (named `box_name`; `is_button` for a button's states)
## as `apply` restyles the theme's: see-through fills opaque BG, a tint kept as an edge, edges
## thicker. The walk (HighContrastWalk) calls it on a copy of a view's own box.
static func restyle_box(sb: StyleBoxFlat, box_name: StringName, is_button: bool) -> void:
	_box(sb, box_name, is_button)


## True while high contrast is on (the view helpers below read it).
static func on() -> bool:
	return Settings.high_contrast


## M14 12Q-ACCESS (L78): `c` changed as little as it must to reach HC_MIN_CONTRAST on `bg`
## (towards TEXT on a dark backing, towards INK on a light one); opaque. Pure; `lift(lift(c))`
## is `lift(c)`.
static func lift(c: Color, bg: Color = BG) -> Color:
	var out := Color(c, 1.0)
	if Palette.contrast(out, bg) >= HC_MIN_CONTRAST:
		return out
	var to := TEXT if Palette.contrast(TEXT, bg) >= Palette.contrast(Palette.INK, bg) else Palette.INK
	var lo := 0.0
	var hi := 1.0
	for _i in LIFT_STEPS:
		var mid := (lo + hi) * 0.5
		if Palette.contrast(out.lerp(to, mid), bg) >= HC_MIN_CONTRAST:
			hi = mid
		else:
			lo = mid
	return Color(out.lerp(to, hi), 1.0)


## Words a view draws in colour `c`: lifted to 7:1 on BG and opaque under high contrast (a
## fade is the caller's, multiplied on after), `c` otherwise.
static func ink(c: Color) -> Color:
	return lift(c) if on() else c


## The fill of a see-through plate or panel a view draws: opaque BG under high contrast.
static func plate(c: Color) -> Color:
	return BG if on() else c


## An edge `w` px wide a view draws: HC_EDGE_SCALE x wider (at least HC_EDGE_MIN) under high contrast.
static func edge(w: float) -> float:
	return maxf(w * HC_EDGE_SCALE, float(HC_EDGE_MIN)) if on() else w


## The BG outline (px, outline_size) that backs light words of `font_px` under high contrast.
static func outline_px(font_px: int) -> int:
	return maxi(HC_OUTLINE_MIN, roundi(font_px * HC_OUTLINE_SHARE))


## M14 12Q-ACCESS (L78): draws `text` on `ci` as draw_string does, in `col`, over its own
## `outline` px outline in `outline_col` (none when 0). Under high contrast the words are
## lifted to 7:1 and backed by an opaque BG outline at least outline_px wide, whatever they
## sit on; `fade` (0..1, a reveal) multiplies the alpha either way.
## M14 12Q-ACCESS follow-up: ink (words under INK_MAX_CONTRAST on BG: a sticker's or a paper's
## lettering) is darkened to 7:1 on PAPER and gets no outline; every other colour of words is
## lifted to 7:1 on BG over a BG outline. Hidden words (alpha under HIDDEN_ALPHA) stay hidden.
static func draw_text(ci: CanvasItem, font: Font, pos: Vector2, text: String, align: HorizontalAlignment, width: float,
		fs: int, col: Color, outline: int = 0, outline_col: Color = Palette.CLEAR, fade: float = 1.0) -> void:
	if on() and col.a * fade >= HIDDEN_ALPHA:
		var a := fade if col.a >= HIDDEN_ALPHA else col.a * fade
		if is_ink(col):
			var dark := Color(lift(col, Palette.PAPER), a)
			_note(text, fs, dark, 0, Palette.CLEAR)
			ci.draw_string(font, pos, text, align, width, fs, dark)
			return
		var o := maxi(outline, outline_px(fs))
		var lit := Color(lift(col), a)
		_note(text, fs, lit, o, BG)
		ci.draw_string_outline(font, pos, text, align, width, fs, o, Color(BG, a))
		ci.draw_string(font, pos, text, align, width, fs, lit)
		return
	if outline > 0 and outline_col.a > 0.0:
		ci.draw_string_outline(font, pos, text, align, width, fs, outline, Color(outline_col, outline_col.a * fade))
	ci.draw_string(font, pos, text, align, width, fs, Color(col, col.a * fade))


## M14 12Q-ACCESS follow-up: draw_multiline_string through the same rules as draw_text.
static func draw_lines(ci: CanvasItem, font: Font, pos: Vector2, text: String, align: HorizontalAlignment, width: float,
		fs: int, max_lines: int, col: Color, brk: int = TextServer.BREAK_MANDATORY | TextServer.BREAK_WORD_BOUND) -> void:
	if on() and col.a >= HIDDEN_ALPHA:
		if is_ink(col):
			var dark := lift(col, Palette.PAPER)
			_note(text, fs, dark, 0, Palette.CLEAR)
			ci.draw_multiline_string(font, pos, text, align, width, fs, max_lines, dark, brk)
			return
		var o := outline_px(fs)
		_note(text, fs, lift(col), o, BG)
		ci.draw_multiline_string_outline(font, pos, text, align, width, fs, max_lines, o, BG, brk)
		ci.draw_multiline_string(font, pos, text, align, width, fs, max_lines, lift(col), brk)
		return
	ci.draw_multiline_string(font, pos, text, align, width, fs, max_lines, col, brk)


## True when `c` is ink: words for a light ground (under INK_MAX_CONTRAST on BG).
static func is_ink(c: Color) -> bool:
	return Palette.contrast(Color(c, 1.0), BG) < INK_MAX_CONTRAST


## Tests: while not null, every word draw_text / draw_lines draws under high contrast is noted
## here as {text, fs, color, outline, outline_color}.
static var drawn: Variant = null


static func _note(text: String, fs: int, col: Color, outline: int, outline_col: Color) -> void:
	if drawn != null:
		(drawn as Array).append({"text": text, "fs": fs, "color": col, "outline": outline, "outline_color": outline_col})


static func _is_button(theme: Theme, type: StringName) -> bool:
	var t := type
	for _i in 8:
		if BUTTON_TYPES.has(t):
			return true
		var base := theme.get_type_variation_base(t)
		if base == &"":
			return false
		t = base
	return false


static func _box(sb: StyleBoxFlat, box_name: StringName, is_button: bool) -> void:
	sb.shadow_size = 0
	sb.shadow_color = Color(BG, 0.0)
	var border := maxi(maxi(sb.border_width_left, sb.border_width_right), maxi(sb.border_width_top, sb.border_width_bottom))
	var has_edge := border > 0 and sb.border_color.a > 0.0
	if FOCUS_BOXES.has(box_name):
		sb.border_color = FOCUS
		sb.set_border_width_all(HC_FOCUS_BORDER)
		sb.draw_center = false
		return
	if FILL_BOXES.has(box_name):
		sb.bg_color = Color(sb.bg_color, 1.0)
		return
	var filled := sb.draw_center and sb.bg_color.a > 0.0
	if not filled and not has_edge:
		if is_button and not [&"normal", &"disabled"].has(box_name):
			# A flat toggle row's hover: no fill to tint, so an edge shows the state.
			sb.draw_center = false
			sb.border_color = FOCUS
			sb.set_border_width_all(HC_TINT_BORDER)
		return  # a clear box stays clear: it has no panel to make opaque
	if filled and not has_edge:
		# The tint was the state (hover, pressed, a highlight): keep it as an edge.
		sb.border_color = Color(sb.bg_color, 1.0)
		sb.set_border_width_all(HC_TINT_BORDER)
	else:
		sb.border_color = Color(sb.border_color, 1.0)
	if filled:
		sb.bg_color = BG
	# M14 12Q-ACCESS (L78): "thick edges": every edge at least HC_EDGE_MIN.
	for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]:
		if sb.get_border_width(side) > 0:
			sb.set_border_width(side, maxi(sb.get_border_width(side), HC_EDGE_MIN))
	if is_button:
		for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]:
			sb.set_border_width(side, maxi(sb.get_border_width(side), HC_BUTTON_BORDER))


static func _color(color_name: StringName, current: Color) -> Color:
	var n := String(color_name)
	if DARK_COLORS.has(color_name):
		return BG
	if not (n.begins_with("font_") or n == "default_color"):
		return Color(current, 1.0) if n.begins_with("icon_") else current
	if FOCUS_COLORS.has(color_name):
		return FOCUS
	if DISABLED_COLORS.has(color_name):
		return DISABLED_TEXT
	return TEXT
