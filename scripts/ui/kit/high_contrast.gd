class_name HighContrast
extends RefCounted
## High-contrast mode (ART_BIBLE §12, art pass W9): turns a built UiTheme into its
## high-contrast variant in place. `UiTheme.build()` calls `apply` as its last step while
## `Settings.high_contrast` is on, so the theme rebuilds through the usual Settings.changed
## path. Rules:
## - every box with a fill becomes opaque #000 (no glass, blur or scrim transparency);
##   a box that marked its state with a tint (hover, pressed, a highlight) keeps that tint
##   as an opaque edge instead, so the state still reads;
## - fills that ARE the information (scroll grabbers, the slider's filled part) stay their
##   colour, made opaque;
## - buttons get a solid HC_BUTTON_BORDER px edge and focus a solid HC_FOCUS_BORDER px
##   `FOCUS` edge; no soft shadows;
## - every font colour becomes TEXT_HI (focus: FOCUS, disabled: TEXT_MID), reaching 7:1 on
##   #000 (HC_MIN_CONTRAST; disabled labels keep far more than §3.7's 4.5:1).
## Views that override colours on their own nodes (paper components, custom _draw) are
## outside the theme: they read `Settings.high_contrast` themselves (W2 components).

## The panel colour behind high-contrast text (§12: "TEXT_HI on #000").
const BG := Color.BLACK
## §12: the minimum contrast of theme text in high-contrast mode.
const HC_MIN_CONTRAST := 7.0
## Edge width of buttons (every state) in high-contrast mode, px.
const HC_BUTTON_BORDER := 3
## Edge width of the focus box in high-contrast mode, px (§6: visible from 3 m).
const HC_FOCUS_BORDER := 4
## Edge width given to a box whose state was only a tint, px.
const HC_TINT_BORDER := 2
## Theme types whose boxes are buttons (their variations are found by base type).
const BUTTON_TYPES: Array[StringName] = [&"Button", &"OptionButton", &"CheckButton", &"CheckBox", &"MenuButton"]
## Stylebox names whose fill is the information (kept, made opaque).
const FILL_BOXES: Array[StringName] = [&"grabber", &"grabber_highlight", &"grabber_pressed",
	&"grabber_area", &"grabber_area_highlight"]
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
				# W2's focus brackets (ART_BIBLE §6): solid FOCUS, thickened for 3 m.
				done[sb] = true
				var br := sb as StyleBoxBrackets
				br.color = Palette.FOCUS
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
		sb.border_color = Palette.FOCUS
		sb.set_border_width_all(HC_FOCUS_BORDER)
		sb.draw_center = false
		return
	if FILL_BOXES.has(box_name):
		sb.bg_color = Color(sb.bg_color, 1.0)
		return
	var filled := sb.draw_center and sb.bg_color.a > 0.0
	if not filled and not has_edge:
		if is_button and box_name != &"normal" and box_name != &"disabled":
			# A flat toggle row's hover: no fill to tint, so an edge shows the state.
			sb.draw_center = false
			sb.border_color = Palette.FOCUS
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
		return Palette.FOCUS
	if DISABLED_COLORS.has(color_name):
		return Palette.TEXT_MID
	return Palette.TEXT_HI
