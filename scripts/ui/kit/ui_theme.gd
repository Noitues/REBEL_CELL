class_name UiTheme
extends RefCounted
## Builds the shared Theme (STYLE_GUIDE 3-4): Share Tech Mono for system text, Anton for
## display, Permanent Marker for the Cell's voice, scaled by Settings.text_scale.
## Controls look like neon terminal panels laid over the night city: deep navy glass,
## thin cyan edges, hover lifts and glows, FOCUS corner brackets (ART_BIBLE §6: always visible for pads).
## Type variations: "MenuItem" (a "> ITEM" line in a terminal menu), "TerminalPanel"
## (a PanelContainer framed like a terminal window), "GlassPanel" (the screen's content
## area: lighter glass so the city shows through), "HudLabel" (the status strip),
## "LogText" (the system log strip), "HeaderLabel" (a screen title).

const BASE_SIZE := 15

# --- ART_BIBLE §4.2 type scale ---------------------------------------------------------------
# Reference pixels at the 1280x720 base viewport, before Settings.text_scale. Every size a
# view uses comes from a step through font_px() (§4.3 rule 1: a literal size is a bug).
## Legend rows, keybind hints, tertiary meta. The floor: nothing the player reads is smaller.
const CAPTION := 12
## Default glass text, list rows, card rules text.
const BODY := BASE_SIZE
## Emphasised rows, chip text, button labels, forecast lines.
const LABEL := 18
## Panel titles, section headings.
const TITLE := 22
## Screen titles, stamp words, HP numbers.
const HEADING := 30
## Big numbers (Heat on the poster), verdict banners.
const DISPLAY := 44
## Verb graffiti (SEND IT), VICTORY, FLATLINED, campaign verdicts (the hero range runs to
## HERO_MAX).
const HERO := 64
const HERO_MAX := 96
## Every step, smallest first.
const STEPS: Array[int] = [CAPTION, BODY, LABEL, TITLE, HEADING, DISPLAY, HERO]
## Line height per step, as a multiple of the font size (§4.2).
const LINE_HEIGHT := {CAPTION: 1.3, BODY: 1.4, LABEL: 1.25, TITLE: 1.2, HEADING: 1.1, DISPLAY: 1.0, HERO: 1.0}
## Tracking (§4.2), as a fraction of the font size: Anton +2%, Share Tech Mono CAPS labels
## +8%, everything else default (0).
const TRACKING_DISPLAY := 0.02
const TRACKING_MONO_CAPS := 0.08
const TRACKING_DEFAULT := 0.0

# --- ART_BIBLE §5.1 spacing ------------------------------------------------------------------
# An 8 px grid with a 4 px half-step; reference pixels at 1280x720 (they scale with the
# viewport through the stretch mode, not with text_scale).
const SP_XS := 4
const SP_S := 8
const SP_M := 16
const SP_L := 24
const SP_XL := 32
const SP_XXL := 48
## The screen safe margin at 1280x720 (TV-safe mode is 5% of the viewport, W9).
const SAFE_MARGIN := 24
## Panel content padding, horizontal and vertical.
const PANEL_PAD_H := 16
const PANEL_PAD_V := 12
## The gutter between panels.
const GUTTER := 16
## Every spacing token, smallest first.
const SPACING: Array[int] = [SP_XS, SP_S, SP_M, SP_L, SP_XL, SP_XXL]


## The pixel size of type step `step` (e.g. UiTheme.TITLE) at the player's text scale.
static func font_px(step: int) -> int:
	return font_px_at(step, Settings.text_scale)


## The pixel size of type step `step` at text scale `scale` (pure; any scale up to 2.0).
static func font_px_at(step: int, scale: float) -> int:
	return roundi(step * scale)


## The line height multiple for type step `step` (§4.2); 1.0 for a size off the scale.
static func line_height(step: int) -> float:
	return LINE_HEIGHT.get(step, 1.0)


## Extra line spacing (px) that brings `font` at `px` to the step's line height, for
## Label/RichTextLabel `line_spacing` (negative when the face's own height is taller).
static func line_spacing_px(font: Font, step: int, px: int) -> int:
	return roundi(px * line_height(step) - font.get_height(px))


## Tracking in pixels for a tracking fraction (TRACKING_*) at `px`, for
## FontVariation.spacing_glyph.
static func tracking_px(tracking: float, px: int) -> int:
	return roundi(px * tracking)


static func build(text_scale: float = 1.0) -> Theme:
	var t := Theme.new()
	var size := roundi(BASE_SIZE * text_scale)
	t.default_font = Palette.mono()
	t.default_font_size = size
	for kind in ["Button", "Label", "RichTextLabel", "OptionButton", "SpinBox", "LineEdit", "CheckButton", "CheckBox", "HSlider", "TabBar", "PopupMenu", "TooltipLabel"]:
		t.set_font_size("font_size", kind, size)
		t.set_font("font", kind, Palette.mono())
	for kind in ["normal_font_size", "bold_font_size", "italics_font_size", "mono_font_size"]:
		t.set_font_size(kind, "RichTextLabel", size)
	t.set_color("font_color", "Label", Palette.TERMINAL_TEXT)
	t.set_color("default_color", "RichTextLabel", Palette.TERMINAL_TEXT)
	t.set_color("font_shadow_color", "Label", Color(Palette.NET_BG_OUTER, 0.6))
	t.set_constant("shadow_offset_x", "Label", 1)
	t.set_constant("shadow_offset_y", "Label", 1)
	_buttons(t, text_scale)
	_menu_item(t, text_scale)
	_fields(t)
	_panels(t)
	_bars(t)
	var header := "HeaderLabel"
	t.set_type_variation(header, "Label")
	t.set_font(&"font", header, Palette.mono())
	t.set_font_size(&"font_size", header, font_px_at(TITLE, text_scale))
	t.set_color(&"font_color", header, Palette.PAPER)
	_body_text(t, text_scale)
	if Settings.high_contrast: HighContrast.apply(t)  # W9 hook (ART_BIBLE §12)
	return t


## The theme type variation for body text (ART_BIBLE §4.1/§4.2): set
## `theme_type_variation = UiTheme.BODY_TEXT` on a Label or a RichTextLabel.
const BODY_TEXT := &"BodyText"


## "BodyText": Plex Sans Condensed at font_px(BODY) with the body line height (1.4), TEXT_HI
## on dark. One variation serves Label (font, font_size, font_color, line_spacing) and
## RichTextLabel (normal/bold fonts and sizes, default_color, line_separation); its own
## empty "normal" box keeps either from inheriting the other's.
static func _body_text(t: Theme, text_scale: float) -> void:
	var v := BODY_TEXT
	t.set_type_variation(v, &"Label")
	var px := font_px_at(BODY, text_scale)
	var spacing := line_spacing_px(Palette.body(), BODY, px)
	t.set_stylebox(&"normal", v, StyleBoxEmpty.new())
	t.set_font(&"font", v, Palette.body())
	t.set_font_size(&"font_size", v, px)
	t.set_color(&"font_color", v, Palette.TEXT_HI)
	t.set_constant(&"line_spacing", v, spacing)
	t.set_font(&"normal_font", v, Palette.body())
	t.set_font(&"bold_font", v, Palette.body_medium())
	for key in [&"normal_font_size", &"bold_font_size", &"italics_font_size", &"bold_italics_font_size"]:
		t.set_font_size(key, v, px)
	t.set_color(&"default_color", v, Palette.TEXT_HI)
	t.set_constant(&"line_separation", v, spacing)


## A terminal box: deep glass, thin edge, square corners.
static func box(bg: Color, edge: Color, border: int = 1, margin_h: float = 10, margin_v: float = 4) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = bg
	s.border_color = edge
	s.set_border_width_all(border)
	s.set_corner_radius_all(0)
	s.content_margin_left = margin_h
	s.content_margin_right = margin_h
	s.content_margin_top = margin_v
	s.content_margin_bottom = margin_v
	s.anti_aliasing = false
	return s


# --- ART_BIBLE §6 / §6.4 buttons (art pass W2) -----------------------------------------------
## The §6.4 button variants, as theme type variations of Button. "HotButton" is the Primary
## (kept under its old name so every screen that uses it picks the new look up).
const PRIMARY := &"HotButton"
const SECONDARY := &"SecondaryButton"
const TERTIARY := &"TertiaryButton"
const DANGER := &"DangerButton"
## Every §6.4 variant (the plain "Button" type is the Secondary look too).
const BUTTON_VARIANTS: Array[StringName] = [PRIMARY, SECONDARY, TERTIARY, DANGER]
## §6 Hover: lift (px) and glow share; Pressed: drop (px) and glow share.
const HOVER_LIFT := 2
const PRESS_DROP := 1
const GLOW_HOVER := 1.2
const GLOW_PRESSED := 0.8
## The glow at rest: a soft shadow in the variant's own colour (px, alpha).
const GLOW_PX := 6
const GLOW_ALPHA := 0.3
## §6.4: a standalone action button is its label plus 32 px (SP_M each side).
const BUTTON_PAD_H := SP_M
## A plain Button (list rows, grids, the native pickers) keeps the old row padding.
const LIST_PAD_H := 10
const BUTTON_PAD_V := SP_XS
## The Primary sits a half-step taller (its label is `title` sized, in Anton).
const PRIMARY_PAD_V := SP_S
## A tertiary button (text plus icon, no box) keeps a small hit margin.
const TERTIARY_PAD_H := SP_S
## Terminal menu lines and list rows (full-width bars) keep the list's own padding.
const ROW_PAD_H := 12
const ROW_PAD_V := 5
## The terminal menu line's left rule (px) when hot.
const ROW_RULE := 3
## The shadow round glass panels (px) and its offset, and the fields' small padding.
const PANEL_SHADOW_PX := 18
const GLASS_SHADOW_PX := 14
const PANEL_SHADOW_OFFSET := Vector2(3, 4)
const FIELD_PAD_H := SP_S
const FIELD_PAD_V := 3
## Share of the fill that the glow lightens on hover / darkens on press (§6: glow +/-20%).
const FILL_SHIFT := 0.1


## A StyleBoxFlat lifted up by `dy` px (negative) or pressed down by `dy` (positive): the box
## moves, the label moves with it (content margins shift), the minimum size never changes.
static func shifted(sb: StyleBoxFlat, dy: float) -> StyleBoxFlat:
	sb.expand_margin_top -= dy
	sb.expand_margin_bottom += dy
	sb.content_margin_top += dy
	sb.content_margin_bottom -= dy
	return sb


## The §6 idle / hover / pressed boxes of one button look: `fill`, a `border`-px `edge`, and
## a glow in `glow`; hover lifts and glows +20%, pressed drops and glows -20%.
static func button_boxes(fill: Color, edge: Color, border: int, glow: Color, pad_h: float, pad_v: float) -> Dictionary:
	var out := {}
	for state in [&"normal", &"hover", &"pressed"]:
		var k := 1.0
		var f := fill
		var sb := box(f, edge, border, pad_h, pad_v)
		if state == &"hover":
			k = GLOW_HOVER
			sb.bg_color = f.lightened(FILL_SHIFT) if f.a > 0.0 else f
			shifted(sb, -HOVER_LIFT)
		elif state == &"pressed":
			k = GLOW_PRESSED
			sb.bg_color = f.darkened(FILL_SHIFT) if f.a > 0.0 else f
			shifted(sb, PRESS_DROP)
		if glow.a > 0.0:
			sb.shadow_color = Color(glow, clampf(GLOW_ALPHA * k, 0.0, 1.0))
			sb.shadow_size = roundi(GLOW_PX * k)
		out[state] = sb
	return out


## The §6 Disabled box: opaque glass, a 1 px DISABLED outline and a lock badge.
static func disabled_box(pad_h: float, pad_v: float, fill: Color = Palette.TERMINAL_BG) -> StyleBoxLocked:
	var sb := StyleBoxLocked.new()
	sb.fill = fill
	sb.content_margin_left = pad_h
	sb.content_margin_right = pad_h
	sb.content_margin_top = pad_v
	sb.content_margin_bottom = pad_v
	return sb


## The §6 Focus box: FOCUS 4-corner brackets outside the control.
static func focus_box() -> StyleBoxBrackets:
	return StyleBoxBrackets.new()


## Applies one look to button type `kind`: boxes from button_boxes, the label colours, the
## §6 disabled and focus treatments.
static func _button_look(t: Theme, kind: StringName, boxes: Dictionary, label: Color, label_hot: Color, pad_h: float, pad_v: float) -> void:
	t.set_stylebox(&"normal", kind, boxes[&"normal"])
	t.set_stylebox(&"hover", kind, boxes[&"hover"])
	t.set_stylebox(&"pressed", kind, boxes[&"pressed"])
	t.set_stylebox(&"hover_pressed", kind, boxes[&"pressed"])
	t.set_stylebox(&"disabled", kind, disabled_box(pad_h, pad_v))
	t.set_stylebox(&"focus", kind, focus_box())
	t.set_color(&"font_color", kind, label)
	t.set_color(&"font_hover_color", kind, label_hot)
	t.set_color(&"font_focus_color", kind, label_hot)
	t.set_color(&"font_pressed_color", kind, label)
	t.set_color(&"font_hover_pressed_color", kind, label)
	# §3.7: a disabled label still reads at 4.5:1 (TEXT_MID on glass), never a faded colour.
	t.set_color(&"font_disabled_color", kind, Palette.TEXT_MID)
	t.set_color(&"icon_disabled_color", kind, Palette.TEXT_MID)


static func _buttons(t: Theme, text_scale: float) -> void:
	# Secondary (§6.4): 1 px TERMINAL_EDGE on glass, TEXT_HI label. The plain Button and the
	# native pickers share its look at the list rows' padding (they are mostly row and grid
	# buttons; W8 gives standalone actions a §6.4 variation, label + 32 px).
	var row := button_boxes(Palette.TERMINAL_BG, Palette.TERMINAL_EDGE, 1, Palette.NET_CYAN, LIST_PAD_H, BUTTON_PAD_V)
	var sec := button_boxes(Palette.TERMINAL_BG, Palette.TERMINAL_EDGE, 1, Palette.NET_CYAN, BUTTON_PAD_H, BUTTON_PAD_V)
	for kind in [&"Button", &"OptionButton", &"CheckButton", &"CheckBox", SECONDARY]:
		var pad := BUTTON_PAD_H if kind == SECONDARY else LIST_PAD_H
		_button_look(t, kind, sec if kind == SECONDARY else row, Palette.TEXT_HI, Palette.TEXT_HI, pad, BUTTON_PAD_V)
		t.set_color(&"icon_normal_color", kind, Palette.NET_CYAN)
		t.set_color(&"icon_hover_color", kind, Palette.CELL_PINK)
		t.set_color(&"icon_focus_color", kind, Palette.FOCUS)
		# §6 Focus: a full-width row's brackets sit far apart, so its words take FOCUS too.
		t.set_color(&"font_focus_color", kind, Palette.FOCUS)
	t.set_type_variation(SECONDARY, &"Button")
	# Primary (§6.4, "HotButton"): filled CELL_PINK, INK label in Anton, icon left.
	var hv := PRIMARY
	t.set_type_variation(hv, &"Button")
	_button_look(t, hv, button_boxes(Palette.CELL_PINK, Palette.CELL_PINK, 0, Palette.CELL_PINK, BUTTON_PAD_H, PRIMARY_PAD_V),
		Palette.INK, Palette.INK, BUTTON_PAD_H, PRIMARY_PAD_V)
	for key in [&"icon_normal_color", &"icon_hover_color", &"icon_pressed_color", &"icon_focus_color"]:
		t.set_color(key, hv, Palette.INK)
	t.set_font(&"font", hv, Palette.display())
	# §4.3.1: the Primary's title size scales with the text like every other size.
	t.set_font_size(&"font_size", hv, font_px_at(TITLE, text_scale))
	# Tertiary (§6.4): text plus icon, no box; the glow is the label brightening.
	var tv := TERTIARY
	t.set_type_variation(tv, &"Button")
	var ter := button_boxes(Color.TRANSPARENT, Color.TRANSPARENT, 0, Color.TRANSPARENT, TERTIARY_PAD_H, BUTTON_PAD_V)
	_button_look(t, tv, ter, Palette.TEXT_MID, Palette.TEXT_HI, TERTIARY_PAD_H, BUTTON_PAD_V)
	t.set_stylebox(&"disabled", tv, disabled_box(TERTIARY_PAD_H, BUTTON_PAD_V, Color.TRANSPARENT))
	# Danger (§6.4): 1 px HARM outline and an X glyph (never the power glyph); a confirm
	# dialog follows the press (the screen's job).
	var dv := DANGER
	t.set_type_variation(dv, &"Button")
	_button_look(t, dv, button_boxes(Palette.TERMINAL_BG, Palette.HARM, 1, Palette.HARM, BUTTON_PAD_H, BUTTON_PAD_V),
		Palette.TEXT_HI, Palette.TEXT_HI, BUTTON_PAD_H, BUTTON_PAD_V)
	t.set_icon(&"icon", dv, cross())
	for key in [&"icon_normal_color", &"icon_hover_color", &"icon_pressed_color", &"icon_focus_color"]:
		t.set_color(key, dv, Palette.HARM)
	# "NoteButton": a choice on a taped paper note (Terminal event options): PAPER, INK.
	var nv := &"NoteButton"
	t.set_type_variation(nv, &"Button")
	var note := button_boxes(Palette.NOTE_PAPER, Color(Palette.INK, 0.4), 1, Palette.INK, SP_M, PANEL_PAD_V)
	var note_hot := button_boxes(Palette.NOTE_PINK, Palette.CELL_PINK, 2, Palette.CELL_PINK, SP_M, PANEL_PAD_V)
	for sb: StyleBoxFlat in [note[&"normal"]]:
		sb.shadow_color = Palette.SHADOW
		sb.shadow_offset = PANEL_SHADOW_OFFSET
	t.set_stylebox(&"normal", nv, note[&"normal"])
	t.set_stylebox(&"hover", nv, note_hot[&"hover"])
	t.set_stylebox(&"pressed", nv, note_hot[&"pressed"])
	t.set_stylebox(&"hover_pressed", nv, note_hot[&"pressed"])
	t.set_stylebox(&"disabled", nv, disabled_box(SP_M, PANEL_PAD_V, Palette.NOTE_PAPER))
	t.set_stylebox(&"focus", nv, focus_box())
	for key in [&"font_color", &"font_hover_color", &"font_focus_color", &"font_pressed_color", &"font_hover_pressed_color", &"font_disabled_color"]:
		t.set_color(key, nv, Palette.INK)
	# Toggles sit flat in lists (no box of their own); hover glows faintly, focus brackets.
	var flat := box(Color.TRANSPARENT, Color.TRANSPARENT, 0, SP_XS, 2)
	for kind in [&"CheckButton", &"CheckBox"]:
		t.set_stylebox(&"normal", kind, flat)
		t.set_stylebox(&"pressed", kind, flat)
		t.set_stylebox(&"disabled", kind, disabled_box(SP_XS, 2, Color.TRANSPARENT))
		var hot := shifted(box(Color(Palette.CELL_PINK, 0.12), Color.TRANSPARENT, 0, SP_XS, 2), -HOVER_LIFT)
		t.set_stylebox(&"hover", kind, hot)
		t.set_stylebox(&"hover_pressed", kind, hot)


static func _menu_item(t: Theme, text_scale: float) -> void:
	var v := &"MenuItem"
	t.set_type_variation(v, &"Button")
	var clear := box(Color.TRANSPARENT, Color.TRANSPARENT, 0, ROW_PAD_H, ROW_PAD_V)
	var hot := shifted(box(Color(Palette.CELL_PINK, 0.16), Palette.CELL_PINK, 0, ROW_PAD_H, ROW_PAD_V), -HOVER_LIFT)
	hot.border_width_left = ROW_RULE
	var pressed := shifted(box(Color(Palette.CELL_PINK, 0.4), Palette.CELL_PINK, 0, ROW_PAD_H, ROW_PAD_V), PRESS_DROP)
	pressed.border_width_left = ROW_RULE
	t.set_stylebox(&"normal", v, clear)
	t.set_stylebox(&"hover", v, hot)
	t.set_stylebox(&"pressed", v, pressed)
	t.set_stylebox(&"hover_pressed", v, pressed)
	t.set_stylebox(&"disabled", v, disabled_box(ROW_PAD_H, ROW_PAD_V, Color.TRANSPARENT))
	t.set_stylebox(&"focus", v, focus_box())
	t.set_constant(&"h_separation", v, SP_S)
	t.set_icon(&"icon", v, chevron())
	# §4.2: a menu line is on the type scale (was body + 2 px, off the scale). `body`, not
	# `label`: a label-sized menu widens the HQ's menu column past the crew's two columns at
	# 1.6 (W8 can step it up when it reflows those pages).
	t.set_font_size(&"font_size", v, font_px_at(BODY, text_scale))
	t.set_color(&"font_color", v, Palette.TERMINAL_TEXT)
	t.set_color(&"font_focus_color", v, Palette.FOCUS)
	t.set_color(&"font_disabled_color", v, Palette.TEXT_MID)


static func _fields(t: Theme) -> void:
	var field := box(Palette.TERMINAL_BG, Color(Palette.TERMINAL_EDGE, 0.5), 1, FIELD_PAD_H, FIELD_PAD_V)
	t.set_stylebox(&"normal", &"LineEdit", field)
	t.set_stylebox(&"focus", &"LineEdit", focus_box())
	t.set_stylebox(&"read_only", &"LineEdit", field)
	t.set_color(&"font_color", &"LineEdit", Palette.TEXT_HI)
	t.set_color(&"font_placeholder_color", &"LineEdit", Palette.TEXT_LO)
	t.set_color(&"caret_color", &"LineEdit", Palette.FOCUS)
	t.set_color(&"selection_color", &"LineEdit", Color(Palette.CELL_PINK, 0.4))
	var popup := box(Color(Palette.TERMINAL_BG, 0.98), Palette.TERMINAL_EDGE, 1, 6, 6)
	t.set_stylebox(&"panel", &"PopupMenu", popup)
	t.set_stylebox(&"hover", &"PopupMenu", box(Color(Palette.CELL_PINK, 0.3), Color.TRANSPARENT, 0))
	t.set_color(&"font_color", &"PopupMenu", Palette.TERMINAL_TEXT)
	t.set_color(&"font_hover_color", &"PopupMenu", Palette.TEXT_HI)
	# §6.8: tooltips are GLASS: navy glass edged in the Cell's pink rule (2 px on top, the
	# title rule); mono TEXT_HI lettering (UiTip folds it to 26-36 columns).
	var tip := box(Palette.TERMINAL_BG, Palette.CELL_PINK, 1, FIELD_PAD_H, 5)
	tip.border_width_top = 2
	tip.shadow_color = Palette.SHADOW
	tip.shadow_size = GLOW_PX
	t.set_stylebox(&"panel", &"TooltipPanel", tip)
	t.set_color(&"font_color", &"TooltipLabel", Palette.TEXT_HI)


static func _panels(t: Theme) -> void:
	t.set_stylebox(&"panel", &"PanelContainer", box(Color.TRANSPARENT, Color.TRANSPARENT, 0, 0, 0))
	var v := &"TerminalPanel"
	t.set_type_variation(v, &"PanelContainer")
	var p := box(Palette.TERMINAL_BG, Palette.TERMINAL_EDGE, 1, 14, 10)
	# A soft dark halo round each panel keeps it readable over the bright city.
	p.shadow_color = Color(Palette.NET_BG_OUTER, 0.6)
	p.shadow_size = PANEL_SHADOW_PX
	p.shadow_offset = PANEL_SHADOW_OFFSET
	t.set_stylebox(&"panel", v, p)
	var g := &"GlassPanel"
	t.set_type_variation(g, &"PanelContainer")
	var glass := box(Color(Palette.TERMINAL_BG, 0.9), Color(Palette.TERMINAL_EDGE, 0.35), 1, 12, 8)
	glass.shadow_color = Palette.SHADOW
	glass.shadow_size = GLASS_SHADOW_PX
	t.set_stylebox(&"panel", g, glass)
	var hud := &"HudLabel"
	t.set_type_variation(hud, &"Label")
	var strip := box(Color(Palette.NET_BG_OUTER, 0.82), Palette.CELL_PINK, 0, 10, 5)
	strip.border_width_bottom = 2
	t.set_stylebox(&"normal", hud, strip)
	t.set_color(&"font_color", hud, Palette.PAPER)
	var lg := &"LogText"
	t.set_type_variation(lg, &"RichTextLabel")
	var log_box := box(Color(Palette.TERMINAL_BG, 0.9), Color(Palette.TERMINAL_EDGE, 0.4), 1, 12, 6)
	log_box.border_width_left = ROW_RULE
	log_box.border_color = Color(Palette.NET_CYAN, 0.6)
	t.set_stylebox(&"normal", lg, log_box)
	t.set_stylebox(&"focus", lg, focus_box())
	t.set_color(&"default_color", lg, Color(Palette.TERMINAL_TEXT, 0.9))
	# Tabs (options, codex): terminal tabs with a pink active underline; focus brackets.
	var tab := box(Palette.TERMINAL_BG, Color(Palette.TERMINAL_EDGE, 0.4), 1, 10, 4)
	var tab_on := box(Palette.TERMINAL_BG_HOT, Palette.CELL_PINK, 0, 10, 4)
	tab_on.border_width_bottom = ROW_RULE
	t.set_stylebox(&"tab_unselected", &"TabBar", tab)
	t.set_stylebox(&"tab_hovered", &"TabBar", box(Palette.TERMINAL_BG_HOT, Palette.CELL_PINK, 1, 10, 4))
	t.set_stylebox(&"tab_selected", &"TabBar", tab_on)
	t.set_stylebox(&"tab_focus", &"TabBar", focus_box())
	t.set_color(&"font_selected_color", &"TabBar", Palette.TEXT_HI)
	t.set_color(&"font_unselected_color", &"TabBar", Palette.TERMINAL_TEXT)
	t.set_color(&"font_hovered_color", &"TabBar", Palette.TEXT_HI)


static func _bars(t: Theme) -> void:
	for kind in [&"VScrollBar", &"HScrollBar"]:
		var track := box(Color(Palette.NET_BG_OUTER, 0.35), Color.TRANSPARENT, 0, 3, 3)
		var grab := box(Color(Palette.NET_CYAN, 0.45), Color.TRANSPARENT, 0, 3, 3)
		var grab_hot := box(Color(Palette.CELL_PINK, 0.8), Color.TRANSPARENT, 0, 3, 3)
		t.set_stylebox(&"scroll", kind, track)
		t.set_stylebox(&"grabber", kind, grab)
		t.set_stylebox(&"grabber_highlight", kind, grab_hot)
		t.set_stylebox(&"grabber_pressed", kind, grab_hot)
	var slider := box(Color(Palette.NET_CYAN, 0.18), Color.TRANSPARENT, 0, 0, 3)
	var fill := box(Color(Palette.CELL_PINK, 0.85), Color.TRANSPARENT, 0, 0, 3)
	t.set_stylebox(&"slider", &"HSlider", slider)
	t.set_stylebox(&"grabber_area", &"HSlider", fill)
	t.set_stylebox(&"grabber_area_highlight", &"HSlider", fill)


static var _crt: ShaderMaterial = null


## The shared terminal-glass material (scanlines + flicker) for terminal panels, the HUD
## and log strips; zeroed under reduce-effects.
static func crt_material() -> ShaderMaterial:
	if _crt == null:
		_crt = ShaderMaterial.new()
		_crt.shader = load("res://shaders/crt_panel.gdshader")
		_sync_crt()
	return _crt


static func _sync_crt() -> void:
	if _crt == null:
		return
	_crt.set_shader_parameter("scan_strength", 0.0 if Settings.reduce_effects else 0.12)
	_crt.set_shader_parameter("flicker", 0.0 if Settings.reduce_effects else 0.01)


static var _chevron: ImageTexture = null


## The "> " marker in front of terminal menu items (white, tinted by the icon colours).
static func chevron() -> Texture2D:
	if _chevron != null:
		return _chevron
	var img := Image.create(10, 14, false, Image.FORMAT_RGBA8)
	img.fill(Color.TRANSPARENT)
	for y in 14:
		var x := y if y < 7 else 13 - y
		for w in 3:
			var px := x + w - 1
			if px >= 0 and px < 10:
				img.set_pixel(px, y, Color.WHITE)
	_chevron = ImageTexture.create_from_image(img)
	return _chevron


static var _cross: ImageTexture = null
## The Danger button's X glyph: side and stroke (px, white, tinted by the icon colours).
const CROSS_SIDE := 12
const CROSS_STROKE := 2


## ART_BIBLE §6.4: the Danger variant's X glyph (white, tinted HARM by the theme).
static func cross() -> Texture2D:
	if _cross != null:
		return _cross
	var img := Image.create(CROSS_SIDE, CROSS_SIDE, false, Image.FORMAT_RGBA8)
	img.fill(Color.TRANSPARENT)
	for i in CROSS_SIDE:
		for w in CROSS_STROKE:
			var j := clampi(i + w - CROSS_STROKE / 2, 0, CROSS_SIDE - 1)
			img.set_pixel(i, j, Color.WHITE)
			img.set_pixel(CROSS_SIDE - 1 - i, j, Color.WHITE)
	_cross = ImageTexture.create_from_image(img)
	return _cross


static var _roots: Array[WeakRef] = []
static var _listening: bool = false


## Applies the theme to `root` and re-applies it while `root` lives and Settings change.
## One static listener serves every root (bound callables are not distinct connections).
static func apply(root: Control) -> void:
	root.theme = build(Settings.text_scale)
	# ART_BIBLE §6 Focus: the 1.03 focus scale, one hook per viewport (UiFocus).
	UiFocus.install_on(root)
	crt_material()
	_roots.append(weakref(root))
	if not _listening:
		_listening = true
		Settings.changed.connect(UiTheme._reapply_all)


static func _reapply_all() -> void:
	_sync_crt()
	var alive: Array[WeakRef] = []
	var theme := build(Settings.text_scale)
	for ref in _roots:
		var root: Object = ref.get_ref()
		if root != null and is_instance_valid(root):
			root.theme = theme
			alive.append(ref)
	_roots = alive
