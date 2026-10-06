class_name UiTheme
extends RefCounted
## Builds the shared Theme (STYLE_GUIDE 3-4): Share Tech Mono for system text, Anton for
## display, Permanent Marker for the Cell's voice, scaled by Settings.text_scale.
## Controls look like neon terminal panels laid over the night city: deep navy glass,
## thin cyan edges, hot-pink hover glow, acid focus ring (always visible for pads).
## Type variations: "MenuItem" (a "> ITEM" line in a terminal menu), "TerminalPanel"
## (a PanelContainer framed like a terminal window), "GlassPanel" (the screen's content
## area: lighter glass so the city shows through), "HudLabel" (the status strip),
## "LogText" (the system log strip), "HeaderLabel" (a screen title).

const BASE_SIZE := 15

# --- Type scale (ART_BIBLE §2.9 / v1 §4.2; art pass W1 + WF, ported in ART-0 E) -----------
# Reference pixels at the 1280x720 base viewport, before Settings.text_scale. Views move
# their literal sizes onto these steps in ART-1..12 (a literal size is a bug).
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
## Verb graffiti (SEND IT), VICTORY, campaign verdicts (the hero range runs to HERO_MAX).
const HERO := 64
const HERO_MAX := 96
## Every step, smallest first.
const STEPS: Array[int] = [CAPTION, BODY, LABEL, TITLE, HEADING, DISPLAY, HERO]
## Line height per step, as a multiple of the font size.
const LINE_HEIGHT := {CAPTION: 1.3, BODY: 1.4, LABEL: 1.25, TITLE: 1.2, HEADING: 1.1, DISPLAY: 1.0, HERO: 1.0}
## Tracking as a fraction of the font size: Anton +2%, Share Tech Mono CAPS labels +8%,
## everything else default (0). Below `heading` these round to 0 px: TRACKING_PX is the
## per-step table the views use.
const TRACKING_DISPLAY := 0.02
const TRACKING_MONO_CAPS := 0.08
const TRACKING_DEFAULT := 0.0
## Tracking in px per type step at text scale 1.0. Faces: TRACK_DISPLAY (Anton) and
## TRACK_MONO_CAPS (Share Tech Mono labels in CAPS); any other face, or a step not listed,
## tracks 0.
const TRACK_DISPLAY := &"display"
const TRACK_MONO_CAPS := &"mono_caps"
const TRACKING_PX := {
	TRACK_DISPLAY: {CAPTION: 1, BODY: 1, LABEL: 1, TITLE: 1, HEADING: 2, DISPLAY: 2, HERO: 3},
	TRACK_MONO_CAPS: {CAPTION: 1, BODY: 1, LABEL: 1, TITLE: 2, HEADING: 2, DISPLAY: 3, HERO: 4},
}

# --- Spacing (ART_BIBLE v1 §5.1, kept by v2) -------------------------------------------------
# An 8 px grid with a 4 px half-step; reference pixels at 1280x720 (they scale with the
# viewport through the stretch mode, not with text_scale).
const SP_XS := 4
const SP_S := 8
const SP_M := 16
const SP_L := 24
const SP_XL := 32
const SP_XXL := 48
## The screen safe margin at 1280x720.
const SAFE_MARGIN := 24
## Panel content padding, horizontal and vertical.
const PANEL_PAD_H := 16
const PANEL_PAD_V := 12
## The gutter between panels.
const GUTTER := 16
## Every spacing token, smallest first.
const SPACING: Array[int] = [SP_XS, SP_S, SP_M, SP_L, SP_XL, SP_XXL]
# --- Component states (ART_BIBLE v1 §6, kept by v2; ART-0 F, ported from art-pass W2) -------
## §6 Hover: lift (px) and glow share; Pressed: drop (px) and glow share (KitState reads
## them for the kit components that draw themselves; the theme's button boxes lift and drop
## by the same px).
const HOVER_LIFT := 2
const PRESS_DROP := 1
const GLOW_HOVER := 1.2
const GLOW_PRESSED := 0.8
## A drawn glow at rest (px, alpha; KitState.draw_box).
const GLOW_PX := 6
const GLOW_ALPHA := 0.3
## Share of the fill that the glow lightens on hover / darkens on press (§6: glow +/-20%).
const FILL_SHIFT := 0.1
## The theme types whose "focus" box is the focus brackets (StyleBoxBrackets).
const BRACKET_FOCUS_TYPES: Array[StringName] = [&"Button", &"OptionButton", &"CheckButton", &"CheckBox",
	&"NoteButton", &"MenuItem", &"LineEdit", &"LogText", TERMINAL_BUTTON]
# --- v2 chrome (ART-1 1A; ART_BIBLE v2 §1.2, §2.10, §6.4, ui_kit.jpg) ---------------------
## Theme type variations added by ART-1: a standalone terminal chip, decrypted corp intel and
## an intercepted corp document (TerminalPanel, GlassPanel, MenuItem etc. are the base set).
const TERMINAL_BUTTON := &"TerminalButton"
const HOLO_PANEL := &"HoloPanel"
const PAPER_PANEL := &"PaperPanel"
## A standalone button's padding (label + 2 x SP_M) and a list row's (the plain Button).
const BUTTON_PAD_H := SP_M
const BUTTON_PAD_V := SP_XS
const LIST_PAD_H := 10
## The standalone terminal chip's edge (px; the list rows keep 1 px).
const TERMINAL_EDGE_PX := 2
## The terminal panel's cut top-right corner (px; the bottom-left takes half).
const TERMINAL_CHAMFER_PX := 12
## The cyan edge glow round terminal panels and holo plates (px, alpha).
const EDGE_GLOW_PX := 8
const EDGE_GLOW_ALPHA := 0.22
## The hover wash on flat rows (alpha of NET_CYAN).
const TINT_HOVER := 0.14
## Vinyl sticker stand-in (HotButton): die-cut border, corner radius, ink extrude, padding,
## the hover glow and the focused sticker's lime die-cut halo (px).
const STICKER_BORDER_PX := 3
const STICKER_RADIUS_PX := 10
const STICKER_EXTRUDE_PX := 4
const STICKER_PAD_H := 18
const STICKER_PAD_V := 8
const STICKER_GLOW_PX := 12
const STICKER_HALO_PX := 3
## Decrypted holo (§1.2): the corp tint share of the plate and the plate's alpha.
const HOLO_TINT := 0.22
const HOLO_PLATE_ALPHA := 0.88
## Live numbers (§6.4): the dark rim (px at 1.0, before the text scale) and the glow.
const LIVE_RIM_PX := 2
const LIVE_GLOW_PX := 10
const LIVE_GLOW_ALPHA := 0.5
## The theme type variation for body text: set `theme_type_variation = UiTheme.BODY_TEXT` on
## a Label or a RichTextLabel.
const BODY_TEXT := &"BodyText"
## The header label's type step (a screen title).
const HEADER_STEP := TITLE


## The pixel size of type step `step` (e.g. UiTheme.TITLE) at the player's text scale.
static func font_px(step: int) -> int:
	return font_px_at(step, Settings.text_scale)


## The pixel size of type step `step` at text scale `scale` (pure; any scale).
static func font_px_at(step: int, scale: float) -> int:
	return roundi(step * scale)


## The line height multiple for type step `step`; 1.0 for a size off the scale.
static func line_height(step: int) -> float:
	return LINE_HEIGHT.get(step, 1.0)


## Extra line spacing (px) that brings `font` at `px` to the step's line height, for
## Label/RichTextLabel `line_spacing` (negative when the face's own height is taller).
static func line_spacing_px(font: Font, step: int, px: int) -> int:
	return roundi(px * line_height(step) - font.get_height(px))


## The height one laid-out line of `font` at `px` takes in a RichTextLabel (px): the
## ascent and descent each rounded up, as the text server lays lines. With MSDF faces
## (ART-1 1A) `Font.get_height` is fractional (Share Tech Mono 30 px: 34.375, laid out at 35),
## so code that pages or sizes text by lines measures with this, never get_height.
static func line_px(font: Font, px: int) -> float:
	return ceilf(font.get_ascent(px)) + ceilf(font.get_descent(px))


## Tracking in pixels for a tracking fraction (TRACKING_*) at `px`, for
## FontVariation.spacing_glyph.
static func tracking_px(tracking: float, px: int) -> int:
	return roundi(px * tracking)


## The tracking (px) of `face` (TRACK_DISPLAY / TRACK_MONO_CAPS) at type step `step`, at the
## player's text scale (or `scale` when given): TRACKING_PX's value times the scale,
## rounded, never under the 1.0 value.
static func tracking_step_px(face: StringName, step: int, scale: float = -1.0) -> int:
	var base: int = (TRACKING_PX.get(face, {}) as Dictionary).get(step, 0)
	var s := Settings.text_scale if scale < 0.0 else scale
	return maxi(base, roundi(base * s)) if s >= 1.0 else roundi(base * s)


static var _tracked: Dictionary = {}


## `font` with the tracking of `face` at `step` (a cached FontVariation whose spacing_glyph
## is tracking_step_px), for a Label's font override or draw_string. The loaded font is
## never changed.
static func tracked(font: Font, face: StringName, step: int, scale: float = -1.0) -> Font:
	var px := tracking_step_px(face, step, scale)
	if px == 0 or font == null:
		return font
	var key := "%d|%d" % [font.get_instance_id(), px]
	if not _tracked.has(key):
		var v := FontVariation.new()
		v.base_font = font
		v.spacing_glyph = px
		_tracked[key] = v
	return _tracked[key]


## The type step a size (px, at the player's text scale or `scale`) belongs to: the largest
## step whose size is at most `px` (caption when smaller).
static func step_of(px: int, scale: float = -1.0) -> int:
	var s := Settings.text_scale if scale < 0.0 else scale
	var out := CAPTION
	for st in STEPS:
		if font_px_at(st, s) <= px:
			out = st
	return out


## Gives a Label or RichTextLabel its tracking: Anton by its step, Share Tech Mono by its
## step when its words are in CAPS; any other face or mixed-case mono is left alone (an
## earlier tracking is taken off). Call after its font, size and words are set (again if
## they change). No screen calls it yet (ART-1..12 do, with their restyle).
static func track_label(c: Control) -> void:
	if c == null:
		return
	var rich := c is RichTextLabel
	var font_name := &"normal_font" if rich else &"font"
	var size_name := &"normal_font_size" if rich else &"font_size"
	var f := c.get_theme_font(font_name)
	var base: Font = f
	if f is FontVariation and (f as FontVariation).base_font != null and _tracked.values().has(f):
		base = (f as FontVariation).base_font
	var text := (c as RichTextLabel).get_parsed_text() if rich else String(c.get(&"text"))
	var face := &""
	if base == Palette.display():
		face = TRACK_DISPLAY
	elif base == Palette.mono() and text == text.to_upper() and text != text.to_lower():
		face = TRACK_MONO_CAPS
	if face == &"":
		if base != f:
			c.add_theme_font_override(font_name, base)
		return
	var want := tracked(base, face, step_of(c.get_theme_font_size(size_name)))
	if want != f:
		c.add_theme_font_override(font_name, want)


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
	_menu_item(t, size)
	_fields(t, text_scale)
	_panels(t)
	_bars(t)
	# ART-1 1A: a screen title is terminal CAPS (Share Tech Mono, tracked +8 %) in the Cell's
	# cyan-white; the yellow title sticker is the screens' own (ART-9..11).
	var header := "HeaderLabel"
	t.set_type_variation(header, "Label")
	t.set_font(&"font", header, tracked(Palette.mono(), TRACK_MONO_CAPS, HEADER_STEP, text_scale))
	t.set_font_size(&"font_size", header, font_px_at(HEADER_STEP, text_scale))
	t.set_color(&"font_color", header, Palette.TEXT_HI)
	_body_text(t, text_scale)
	PaletteSkins.apply(t, PaletteSkins.active())  # ART-12 12s: the skin's chrome values (v2: none)
	if Settings.high_contrast:
		HighContrast.apply(t)  # ART-0 C (art pass W9, ART_BIBLE §12): the high-contrast hook
	return t


## "BodyText": Plex Sans Condensed at the BODY step with the body line height (1.4), TEXT_HI
## on dark. One variation serves Label (font, font_size, font_color, line_spacing) and
## RichTextLabel (normal/bold fonts and sizes, default_color, line_separation); its own
## empty "normal" box keeps either from inheriting the other's. No screen uses it yet.
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


## A StyleBoxFlat lifted up by `dy` px (negative) or pressed down by `dy` (positive): the box
## moves, the label moves with it (content margins shift), the minimum size never changes
## (§6 Hover / Pressed; ART-0 F, ported from art-pass W2).
static func shifted(sb: StyleBoxFlat, dy: float) -> StyleBoxFlat:
	sb.expand_margin_top -= dy
	sb.expand_margin_bottom += dy
	sb.content_margin_top += dy
	sb.content_margin_bottom -= dy
	return sb


## The §6 / v2 §2.10 focus box: FOCUS 4-corner brackets, 3 px at 7 px outside the control
## (a new box per type, so high contrast can thicken each).
static func focus_box() -> StyleBoxBrackets:
	return StyleBoxBrackets.new()


static func _buttons(t: Theme, text_scale: float) -> void:
	# v2 terminal chip (ui_kit.jpg "secondary = terminal chip"): navy glass with a cyan edge;
	# hover lights the edge with a cyan glow; pressed fills cyan with navy words; disabled is a
	# DISABLED edge with legible TEXT_LO words; focus is F's lime brackets.
	var boxes := terminal_button_boxes(1, LIST_PAD_H, BUTTON_PAD_V)
	var focus := focus_box()
	for kind in ["Button", "OptionButton", "CheckButton", "CheckBox"]:
		_terminal_look(t, kind, boxes, focus)
	# "TerminalButton" (§6.4): a standalone terminal chip (RESPIN, VIEW LOADOUT): the same look
	# with the v2 2 px edge and the standalone padding.
	t.set_type_variation(TERMINAL_BUTTON, &"Button")
	_terminal_look(t, TERMINAL_BUTTON, terminal_button_boxes(TERMINAL_EDGE_PX, BUTTON_PAD_H, BUTTON_PAD_V), focus_box())
	# "HotButton": the one committing verb on a screen (RUN THE RAID, INITIATE BREACH) as a
	# pink vinyl sticker: CELL_PINK, a white die-cut border, an ink extrude under it, Anton in
	# INK. A sticker gets no brackets (§2.10: a lime die-cut halo when focused).
	var hv := "HotButton"
	t.set_type_variation(hv, "Button")
	var hot_n := sticker_box(Palette.STICKER_COMMIT)
	var hot_h := shifted(sticker_box(Palette.STICKER_COMMIT.lightened(FILL_SHIFT)), -HOVER_LIFT)
	hot_h.shadow_size = STICKER_GLOW_PX
	hot_h.shadow_color = Color(Palette.STICKER_COMMIT, GLOW_ALPHA * GLOW_HOVER)
	hot_h.shadow_offset = Vector2.ZERO
	var hot_p := shifted(sticker_box(Palette.STICKER_COMMIT.darkened(FILL_SHIFT)), PRESS_DROP)
	hot_p.shadow_offset = Vector2(0, STICKER_EXTRUDE_PX - PRESS_DROP)
	var hot_f := sticker_box(Palette.CLEAR)
	hot_f.draw_center = false
	hot_f.border_color = Palette.FOCUS
	hot_f.set_border_width_all(STICKER_HALO_PX)
	hot_f.set_expand_margin_all(STICKER_HALO_PX)
	hot_f.shadow_size = 0
	hot_f.shadow_offset = Vector2.ZERO
	var hot_d := sticker_box(Palette.DISABLED)
	t.set_stylebox("normal", hv, hot_n)
	t.set_stylebox("hover", hv, hot_h)
	t.set_stylebox("pressed", hv, hot_p)
	t.set_stylebox("hover_pressed", hv, hot_p)
	t.set_stylebox("focus", hv, hot_f)
	t.set_stylebox("disabled", hv, hot_d)
	t.set_color("font_disabled_color", hv, Palette.INK)
	for key in ["font_color", "font_hover_color", "font_focus_color", "font_pressed_color", "font_hover_pressed_color"]:
		t.set_color(key, hv, Palette.INK)
	t.set_font("font", hv, tracked(Palette.display(), TRACK_DISPLAY, TITLE, text_scale))
	t.set_font_size("font_size", hv, font_px_at(TITLE, text_scale))
	# "NoteButton": a choice on a taped paper note (Terminal event options): paper stays paper.
	var nv := "NoteButton"
	t.set_type_variation(nv, "Button")
	var note_n := box(Palette.NOTE_PAPER, Color(Palette.INK, 0.4), 1, 16, 12)
	note_n.shadow_color = Palette.SHADOW
	note_n.shadow_size = 6
	note_n.shadow_offset = Vector2(3, 4)
	var note_h := shifted(box(Palette.PAPER, Palette.NET_CYAN, 2, 16, 12), -HOVER_LIFT)
	note_h.shadow_color = Color(Palette.NET_CYAN, GLOW_ALPHA * GLOW_HOVER)
	note_h.shadow_size = GLOW_PX
	var note_p := shifted(note_h.duplicate() as StyleBoxFlat, HOVER_LIFT + PRESS_DROP)
	var note_d := box(Color(Palette.NOTE_PAPER, 0.45), Color(Palette.INK, 0.3), 1, 16, 12)
	t.set_stylebox("normal", nv, note_n)
	t.set_stylebox("hover", nv, note_h)
	t.set_stylebox("pressed", nv, note_p)
	t.set_stylebox("focus", nv, focus_box())
	t.set_stylebox("disabled", nv, note_d)
	for key in ["font_color", "font_hover_color", "font_focus_color", "font_pressed_color", "font_hover_pressed_color"]:
		t.set_color(key, nv, Palette.INK)
	t.set_color("font_disabled_color", nv, Color(Palette.INK, 0.45))
	# Toggles sit flat in lists (no box of their own); hover is a faint cyan wash.
	var flat := box(Color(0, 0, 0, 0), Color(0, 0, 0, 0), 0, 4, 2)
	for kind in ["CheckButton", "CheckBox"]:
		t.set_stylebox("normal", kind, flat)
		t.set_stylebox("pressed", kind, flat)
		t.set_stylebox("disabled", kind, flat)
		var hot := box(Color(Palette.NET_CYAN, TINT_HOVER), Color(0, 0, 0, 0), 0, 4, 2)
		t.set_stylebox("hover", kind, hot)
		t.set_stylebox("hover_pressed", kind, hot)
		t.set_color("font_pressed_color", kind, Palette.TEXT_HI)
		t.set_color("font_hover_pressed_color", kind, Palette.TEXT_HI)


## The v2 terminal chip boxes ("normal", "hover", "pressed", "disabled") with a `border`-px
## edge and the given padding (§6.4 TerminalButton; the plain Button at the list padding).
static func terminal_button_boxes(border: int, pad_h: float, pad_v: float) -> Dictionary:
	var normal := box(Palette.TERMINAL_BG, Palette.TERMINAL_EDGE, border, pad_h, pad_v)
	var hover := shifted(box(Palette.TERMINAL_BG_HOT, Palette.NET_CYAN, border, pad_h, pad_v), -HOVER_LIFT)
	hover.shadow_color = Color(Palette.NET_CYAN, GLOW_ALPHA * GLOW_HOVER)
	hover.shadow_size = GLOW_PX
	var pressed := shifted(box(Palette.SELECTED, Palette.SELECTED, border, pad_h, pad_v), PRESS_DROP)
	pressed.shadow_color = Color(Palette.NET_CYAN, GLOW_ALPHA * GLOW_PRESSED)
	pressed.shadow_size = GLOW_PX
	var disabled := box(Color(Palette.TERMINAL_BG, 0.7), Palette.DISABLED, border, pad_h, pad_v)
	for sb in [normal, hover, pressed, disabled]:
		PaletteSkins.apply_box(sb)  # ART-12 12s: the active skin's chrome
	return {&"normal": normal, &"hover": hover, &"pressed": pressed, &"disabled": disabled}


static func _terminal_look(t: Theme, kind: StringName, boxes: Dictionary, focus: StyleBox) -> void:
	t.set_stylebox("normal", kind, boxes[&"normal"])
	t.set_stylebox("hover", kind, boxes[&"hover"])
	t.set_stylebox("pressed", kind, boxes[&"pressed"])
	t.set_stylebox("hover_pressed", kind, boxes[&"pressed"])
	t.set_stylebox("disabled", kind, boxes[&"disabled"])
	t.set_stylebox("focus", kind, focus)
	t.set_color("font_color", kind, Palette.TERMINAL_TEXT)
	t.set_color("font_hover_color", kind, Palette.TEXT_HI)
	t.set_color("font_focus_color", kind, Palette.FOCUS)
	t.set_color("font_pressed_color", kind, Palette.ON_SELECTED)
	t.set_color("font_hover_pressed_color", kind, Palette.ON_SELECTED)
	t.set_color("font_disabled_color", kind, Palette.TEXT_LO)
	t.set_color("icon_normal_color", kind, Palette.NET_CYAN)
	t.set_color("icon_hover_color", kind, Palette.TEXT_HI)
	t.set_color("icon_pressed_color", kind, Palette.ON_SELECTED)
	t.set_color("icon_hover_pressed_color", kind, Palette.ON_SELECTED)
	t.set_color("icon_focus_color", kind, Palette.FOCUS)
	t.set_color("icon_disabled_color", kind, Palette.TEXT_LO)


## A vinyl sticker plate in `fill` (§1.2): a white die-cut border, round corners and a hard ink
## extrude under it (a StyleBoxFlat stand-in until the baked sticker atlas, ART-4/10).
static func sticker_box(fill: Color) -> StyleBoxFlat:
	var s := box(fill, Palette.STICKER_DIE_CUT, STICKER_BORDER_PX, STICKER_PAD_H, STICKER_PAD_V)
	s.set_corner_radius_all(STICKER_RADIUS_PX)
	s.anti_aliasing = true
	s.shadow_color = Palette.INK
	s.shadow_size = 0
	s.shadow_offset = Vector2(0, STICKER_EXTRUDE_PX)
	return s


## A CRT terminal panel box (§1.2 / §6.4 TerminalPanel): navy glass, cyan edge, the top-right
## corner cut (the chamfer), a soft cyan edge glow. `edge` tints it (a corp terminal).
static func terminal_box(edge: Color = Palette.TERMINAL_EDGE, pad_h: float = 14, pad_v: float = 10) -> StyleBoxFlat:
	var p := box(Palette.TERMINAL_BG, edge, 1, pad_h, pad_v)
	p.corner_radius_top_right = TERMINAL_CHAMFER_PX
	p.corner_radius_bottom_left = TERMINAL_CHAMFER_PX / 2
	p.corner_detail = 1
	p.anti_aliasing = true
	p.shadow_color = Color(edge, EDGE_GLOW_ALPHA)
	p.shadow_size = EDGE_GLOW_PX
	PaletteSkins.apply_box(p)  # ART-12 12s: the active skin's chrome (a corp edge stays)
	return p


static func _menu_item(t: Theme, size: int) -> void:
	# v2 terminal menu line (ui_kit.jpg FOCUS): hover lights a cyan rule and wash; the focused
	# line takes the lime brackets and its `>` caret (the chevron icon, tinted FOCUS).
	var v := "MenuItem"
	t.set_type_variation(v, "Button")
	var clear := box(Color(0, 0, 0, 0), Color(0, 0, 0, 0), 0, 12, 5)
	var hot := shifted(box(Color(Palette.NET_CYAN, TINT_HOVER), Palette.NET_CYAN, 0, 12, 5), -HOVER_LIFT)
	hot.border_width_left = 3
	var pressed := shifted(box(Palette.SELECTED, Palette.SELECTED, 0, 12, 5), PRESS_DROP)
	pressed.border_width_left = 3
	t.set_stylebox("normal", v, clear)
	t.set_stylebox("hover", v, hot)
	t.set_stylebox("pressed", v, pressed)
	t.set_stylebox("hover_pressed", v, pressed)
	t.set_stylebox("disabled", v, clear)
	t.set_stylebox("focus", v, focus_box())
	t.set_constant("h_separation", v, 8)
	t.set_icon("icon", v, chevron())
	t.set_font_size("font_size", v, size + 2)
	t.set_color("font_color", v, Palette.TERMINAL_TEXT)
	t.set_color("font_hover_color", v, Palette.TEXT_HI)
	t.set_color("font_focus_color", v, Palette.FOCUS)
	t.set_color("font_pressed_color", v, Palette.ON_SELECTED)
	t.set_color("font_hover_pressed_color", v, Palette.ON_SELECTED)
	t.set_color("icon_normal_color", v, Palette.NET_CYAN)
	t.set_color("icon_hover_color", v, Palette.TEXT_HI)
	t.set_color("icon_focus_color", v, Palette.FOCUS)
	t.set_color("icon_pressed_color", v, Palette.ON_SELECTED)


static func _fields(t: Theme, text_scale: float) -> void:
	var field := box(Palette.TERMINAL_BG, Color(Palette.TERMINAL_EDGE, 0.5), 1, 8, 3)
	t.set_stylebox("normal", "LineEdit", field)
	t.set_stylebox("focus", "LineEdit", focus_box())
	t.set_stylebox("read_only", "LineEdit", field)
	t.set_color("font_color", "LineEdit", Palette.TEXT_HI)
	t.set_color("font_placeholder_color", "LineEdit", Palette.TEXT_LO)
	t.set_color("caret_color", "LineEdit", Palette.FOCUS)
	t.set_color("selection_color", "LineEdit", Color(Palette.NET_CYAN, 0.4))
	var popup := terminal_box(Palette.TERMINAL_EDGE, 6, 6)
	popup.bg_color = Color(Palette.TERMINAL_BG, 0.98)
	t.set_stylebox("panel", "PopupMenu", popup)
	t.set_stylebox("hover", "PopupMenu", box(Color(Palette.NET_CYAN, 0.3), Color(0, 0, 0, 0), 0))
	t.set_color("font_color", "PopupMenu", Palette.TERMINAL_TEXT)
	t.set_color("font_hover_color", "PopupMenu", Palette.TEXT_HI)
	# Tooltips (ui_kit.jpg TOOLTIP): a terminal panel, cyan edge, Plex body lettering (§2.9).
	t.set_stylebox("panel", "TooltipPanel", terminal_box(Palette.NET_CYAN, 8, 5))
	t.set_color("font_color", "TooltipLabel", Palette.TEXT_HI)
	t.set_font("font", "TooltipLabel", Palette.body())
	t.set_font_size("font_size", "TooltipLabel", font_px_at(BODY, text_scale))


static func _panels(t: Theme) -> void:
	var clear := StyleBoxFlat.new()
	clear.bg_color = Color(0, 0, 0, 0)
	t.set_stylebox("panel", "PanelContainer", clear)
	# "TerminalPanel" (§6.4): the Cell's own systems.
	var v := "TerminalPanel"
	t.set_type_variation(v, "PanelContainer")
	t.set_stylebox("panel", v, terminal_box())
	# "GlassPanel": a screen's content area, lighter glass so the city shows through.
	var g := "GlassPanel"
	t.set_type_variation(g, "PanelContainer")
	var glass := terminal_box(Color(Palette.TERMINAL_EDGE, 0.45), 12, 8)
	glass.bg_color = Color(Palette.TERMINAL_BG, 0.9)
	t.set_stylebox("panel", g, glass)
	# "HoloPanel" (§1.2): decrypted corp intel; this box is the corp-tinted plate and edge (the
	# `holo_panel` shader of the material kit, 1B, draws the scanlines, bands and RGB split
	# over it). The neutral tint is Halcyon-free violet glass; views set their corp's hue
	# with `holo_box(corp_color)`.
	t.set_type_variation(HOLO_PANEL, "PanelContainer")
	t.set_stylebox("panel", HOLO_PANEL, holo_box(Palette.NEON_VIOLET))
	# "PaperPanel" (§1.2): an intercepted corp document: paper stock, ink keyline, a drop
	# shadow; Courier Prime lettering in INK.
	t.set_type_variation(PAPER_PANEL, "PanelContainer")
	var paper := box(Palette.PAPER, Color(Palette.INK, 0.35), 1, 16, 12)
	paper.shadow_color = Palette.SHADOW
	paper.shadow_size = 6
	paper.shadow_offset = Vector2(3, 4)
	t.set_stylebox("panel", PAPER_PANEL, paper)
	var hud := "HudLabel"
	t.set_type_variation(hud, "Label")
	var strip := box(Palette.TERMINAL_BG, Palette.TERMINAL_EDGE, 0, 10, 5)
	strip.border_width_bottom = 2
	t.set_stylebox("normal", hud, strip)
	t.set_color("font_color", hud, Palette.TEXT_HI)
	var lg := "LogText"
	t.set_type_variation(lg, "RichTextLabel")
	var log_box := box(Color(Palette.TERMINAL_BG, 0.9), Color(Palette.TERMINAL_EDGE, 0.4), 1, 12, 6)
	log_box.border_width_left = 3
	log_box.border_color = Color(Palette.NET_CYAN, 0.6)
	t.set_stylebox("normal", lg, log_box)
	t.set_stylebox("focus", lg, focus_box())
	t.set_color("default_color", lg, Color(Palette.TERMINAL_TEXT, 0.9))
	# Tabs (ui_kit.jpg TABS: active = filled cyan, hover = lit edge, the rest navy glass).
	var tab := box(Palette.TERMINAL_BG, Color(Palette.TERMINAL_EDGE, 0.5), 1, 10, 4)
	var tab_on := box(Palette.SELECTED, Palette.SELECTED, 1, 10, 4)
	t.set_stylebox("tab_unselected", "TabBar", tab)
	t.set_stylebox("tab_hovered", "TabBar", box(Palette.TERMINAL_BG_HOT, Palette.NET_CYAN, 1, 10, 4))
	t.set_stylebox("tab_selected", "TabBar", tab_on)
	t.set_stylebox("tab_focus", "TabBar", box(Color(0, 0, 0, 0), Palette.FOCUS, 2, 10, 4))
	t.set_color("font_selected_color", "TabBar", Palette.ON_SELECTED)
	t.set_color("font_unselected_color", "TabBar", Palette.TERMINAL_TEXT)
	t.set_color("font_hovered_color", "TabBar", Palette.TEXT_HI)


## The §1.2 decrypted-holo plate tinted `corp` (~78 % behind the scrim, edge in the corp hue).
static func holo_box(corp: Color) -> StyleBoxFlat:
	var tint := Palette.over(Palette.NET_BG_OUTER, Color(corp, HOLO_TINT))
	var h := box(Color(tint, HOLO_PLATE_ALPHA), corp, TERMINAL_EDGE_PX, 14, 10)
	h.shadow_color = Color(corp, EDGE_GLOW_ALPHA)
	h.shadow_size = EDGE_GLOW_PX
	return h


static func _bars(t: Theme) -> void:
	for kind in ["VScrollBar", "HScrollBar"]:
		var track := box(Color(0, 0, 0, 0.35), Color(0, 0, 0, 0), 0, 3, 3)
		var grab := box(Color(Palette.NET_CYAN, 0.45), Color(0, 0, 0, 0), 0, 3, 3)
		var grab_hot := box(Color(Palette.NET_CYAN, 0.9), Color(0, 0, 0, 0), 0, 3, 3)
		t.set_stylebox("scroll", kind, track)
		t.set_stylebox("grabber", kind, grab)
		t.set_stylebox("grabber_highlight", kind, grab_hot)
		t.set_stylebox("grabber_pressed", kind, grab_hot)
	var slider := box(Color(Palette.NET_CYAN, 0.18), Color(0, 0, 0, 0), 0, 0, 3)
	var fill := box(Color(Palette.NET_CYAN, 0.85), Color(0, 0, 0, 0), 0, 0, 3)
	t.set_stylebox("slider", "HSlider", slider)
	t.set_stylebox("grabber_area", "HSlider", fill)
	t.set_stylebox("grabber_area_highlight", "HSlider", fill)


static var _live: Dictionary = {}


## §6.4 live numbers (HP, Heat value, damage numbers): bare Anton at `step`, LIVE_NUMBER_RIM
## outline (2 px x the text scale) and a glow in its own colour `color` at 50 %. A cached
## LabelSettings per (step, colour, scale); never changed after it is made.
static func live_number(step: int, color: Color, scale: float = -1.0) -> LabelSettings:
	var s := Settings.text_scale if scale < 0.0 else scale
	var key := "%d|%s|%.2f" % [step, color.to_html(), s]
	if not _live.has(key):
		var ls := LabelSettings.new()
		ls.font = tracked(Palette.display(), TRACK_DISPLAY, step, s)
		ls.font_size = font_px_at(step, s)
		ls.font_color = color
		ls.outline_size = maxi(LIVE_RIM_PX, roundi(LIVE_RIM_PX * s)) * 2
		ls.outline_color = Palette.LIVE_NUMBER_RIM
		ls.shadow_size = LIVE_GLOW_PX
		ls.shadow_color = Color(color, LIVE_GLOW_ALPHA)
		ls.shadow_offset = Vector2.ZERO
		_live[key] = ls
	return _live[key]


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
	# M14 B1c (review D23): the faint scrolling hex dump at 6 % on every terminal glass, in
	# the Cell's cyan as the active skin re-values it (the kit's CRT glass shares the uniforms).
	CrtTerminalPanel.sync_hex(_crt, PaletteSkins.chrome(Palette.NET_CYAN), true, CrtTerminalPanel.HEX_SEED)


static var _chevron: ImageTexture = null


## The "> " marker in front of terminal menu items (white, tinted by the icon colours).
static func chevron() -> Texture2D:
	if _chevron != null:
		return _chevron
	var img := Image.create(10, 14, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	for y in 14:
		var x := y if y < 7 else 13 - y
		for w in 3:
			var px := x + w - 1
			if px >= 0 and px < 10:
				img.set_pixel(px, y, Palette.NO_TINT)
	_chevron = ImageTexture.create_from_image(img)
	return _chevron


static var _roots: Array[WeakRef] = []
static var _listening: bool = false


## ANIM-R5 P17: lets the shared material and texture go (Fx at exit): resources held by a
## script's static variables are otherwise freed with the script, after the renderer has
## shut down (a crash at exit now and then).
static func release() -> void:
	_crt = null
	_chevron = null
	_roots.clear()
	# ART-0 E: the tracked font variations hold fonts too (the same exit crash).
	_tracked.clear()
	_live.clear()


## Applies the theme to `root` and re-applies it while `root` lives and Settings change.
## One static listener serves every root (bound callables are not distinct connections).
static func apply(root: Control) -> void:
	root.theme = build(Settings.text_scale)
	crt_material()
	UiFocus.install_on(root)  # ART-0 F (§6): the pad focus scale on this root's viewport
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
