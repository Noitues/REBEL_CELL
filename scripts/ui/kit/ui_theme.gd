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
	t.set_color("font_shadow_color", "Label", Color(0, 0, 0, 0.6))
	t.set_constant("shadow_offset_x", "Label", 1)
	t.set_constant("shadow_offset_y", "Label", 1)
	_buttons(t)
	_menu_item(t, size)
	_fields(t)
	_panels(t)
	_bars(t)
	var header := "HeaderLabel"
	t.set_type_variation(header, "Label")
	t.set_font(&"font", header, Palette.mono())
	t.set_font_size(&"font_size", header, font_px_at(HEADER_STEP, text_scale))
	t.set_color(&"font_color", header, Palette.PAPER)
	_body_text(t, text_scale)
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


static func _buttons(t: Theme) -> void:
	var normal := box(Palette.TERMINAL_BG, Palette.TERMINAL_EDGE)
	var hover := box(Palette.TERMINAL_BG_HOT, Palette.CELL_PINK)
	hover.shadow_color = Color(Palette.CELL_PINK, 0.35)
	hover.shadow_size = 6
	var pressed := box(Color(Palette.CELL_PINK, 0.55), Palette.CELL_PINK)
	var disabled := box(Color(Palette.TERMINAL_BG, 0.55), Color(Palette.TERMINAL_EDGE, 0.25))
	# Focus draws over the normal box: an acid ring outside the edge, readable on pads.
	var focus := box(Color(0, 0, 0, 0), Palette.CELL_ACID, 2)
	focus.draw_center = false
	focus.set_expand_margin_all(2)
	focus.shadow_color = Color(Palette.CELL_ACID, 0.25)
	focus.shadow_size = 5
	for kind in ["Button", "OptionButton", "CheckButton", "CheckBox"]:
		t.set_stylebox("normal", kind, normal)
		t.set_stylebox("hover", kind, hover)
		t.set_stylebox("pressed", kind, pressed)
		t.set_stylebox("hover_pressed", kind, pressed)
		t.set_stylebox("disabled", kind, disabled)
		t.set_stylebox("focus", kind, focus)
		t.set_color("font_color", kind, Palette.TERMINAL_TEXT)
		t.set_color("font_hover_color", kind, Palette.PAPER)
		t.set_color("font_focus_color", kind, Palette.CELL_ACID)
		t.set_color("font_pressed_color", kind, Palette.PAPER)
		t.set_color("font_hover_pressed_color", kind, Palette.PAPER)
		t.set_color("font_disabled_color", kind, Color(Palette.TERMINAL_TEXT, 0.35))
		t.set_color("icon_normal_color", kind, Palette.NET_CYAN)
		t.set_color("icon_hover_color", kind, Palette.CELL_PINK)
		t.set_color("icon_focus_color", kind, Palette.CELL_ACID)
	# "HotButton": the one big action on a screen (RUN THE RAID, INITIATE BREACH).
	var hv := "HotButton"
	t.set_type_variation(hv, "Button")
	var hot_n := box(Palette.CELL_PINK, Palette.PAPER, 2, 18, 8)
	hot_n.shadow_color = Color(Palette.CELL_PINK, 0.35)
	hot_n.shadow_size = 8
	var hot_h := box(Palette.CELL_PINK.lightened(0.15), Palette.CELL_ACID, 2, 18, 8)
	hot_h.shadow_color = Color(Palette.CELL_PINK, 0.6)
	hot_h.shadow_size = 12
	t.set_stylebox("normal", hv, hot_n)
	t.set_stylebox("hover", hv, hot_h)
	t.set_stylebox("pressed", hv, box(Palette.CELL_PINK.darkened(0.2), Palette.PAPER, 2, 18, 8))
	t.set_stylebox("disabled", hv, box(Color(Palette.CELL_PINK, 0.18), Color(Palette.CELL_PINK, 0.4), 1, 18, 8))
	t.set_color("font_disabled_color", hv, Color(Palette.CELL_PINK, 0.5))
	t.set_color("font_color", hv, Palette.INK)
	t.set_color("font_hover_color", hv, Palette.INK)
	t.set_color("font_focus_color", hv, Palette.INK)
	t.set_color("font_pressed_color", hv, Palette.INK)
	t.set_font("font", hv, Palette.display())
	t.set_font_size("font_size", hv, 22)
	# "NoteButton": a choice on a taped paper note (Terminal event options).
	var nv := "NoteButton"
	t.set_type_variation(nv, "Button")
	var note_n := box(Palette.NOTE_PAPER, Color(Palette.INK, 0.4), 1, 16, 12)
	note_n.shadow_color = Palette.SHADOW
	note_n.shadow_size = 6
	note_n.shadow_offset = Vector2(3, 4)
	var note_h := box(Palette.NOTE_PINK, Palette.CELL_PINK, 2, 16, 12)
	note_h.shadow_color = Color(Palette.CELL_PINK, 0.4)
	note_h.shadow_size = 10
	var note_d := box(Color(Palette.NOTE_PAPER, 0.45), Color(Palette.INK, 0.3), 1, 16, 12)
	t.set_stylebox("normal", nv, note_n)
	t.set_stylebox("hover", nv, note_h)
	t.set_stylebox("pressed", nv, note_h)
	t.set_stylebox("disabled", nv, note_d)
	for key in ["font_color", "font_hover_color", "font_focus_color", "font_pressed_color", "font_hover_pressed_color"]:
		t.set_color(key, nv, Palette.INK)
	t.set_color("font_disabled_color", nv, Color(Palette.INK, 0.45))
	# Toggles sit flat in lists (no box of their own).
	var flat := box(Color(0, 0, 0, 0), Color(0, 0, 0, 0), 0, 4, 2)
	for kind in ["CheckButton", "CheckBox"]:
		t.set_stylebox("normal", kind, flat)
		t.set_stylebox("pressed", kind, flat)
		t.set_stylebox("disabled", kind, flat)
		var hot := box(Color(Palette.CELL_PINK, 0.12), Color(0, 0, 0, 0), 0, 4, 2)
		t.set_stylebox("hover", kind, hot)
		t.set_stylebox("hover_pressed", kind, hot)


static func _menu_item(t: Theme, size: int) -> void:
	var v := "MenuItem"
	t.set_type_variation(v, "Button")
	var clear := box(Color(0, 0, 0, 0), Color(0, 0, 0, 0), 0, 12, 5)
	var hot := box(Color(Palette.CELL_PINK, 0.16), Palette.CELL_PINK, 0, 12, 5)
	hot.border_width_left = 3
	var pressed := box(Color(Palette.CELL_PINK, 0.4), Palette.CELL_PINK, 0, 12, 5)
	pressed.border_width_left = 3
	t.set_stylebox("normal", v, clear)
	t.set_stylebox("hover", v, hot)
	t.set_stylebox("pressed", v, pressed)
	t.set_stylebox("hover_pressed", v, pressed)
	t.set_stylebox("disabled", v, clear)
	var focus := box(Color(Palette.CELL_ACID, 0.08), Palette.CELL_ACID, 0, 12, 5)
	focus.border_width_left = 3
	t.set_stylebox("focus", v, focus)
	t.set_constant("h_separation", v, 8)
	t.set_icon("icon", v, chevron())
	t.set_font_size("font_size", v, size + 2)
	t.set_color("font_color", v, Palette.TERMINAL_TEXT)


static func _fields(t: Theme) -> void:
	var field := box(Color(0.0, 0.02, 0.06, 0.95), Color(Palette.TERMINAL_EDGE, 0.5), 1, 8, 3)
	var field_focus := box(Color(0.0, 0.02, 0.06, 0.95), Palette.CELL_ACID, 2, 8, 3)
	t.set_stylebox("normal", "LineEdit", field)
	t.set_stylebox("focus", "LineEdit", field_focus)
	t.set_stylebox("read_only", "LineEdit", field)
	t.set_color("font_color", "LineEdit", Palette.PAPER)
	t.set_color("font_placeholder_color", "LineEdit", Color(Palette.TERMINAL_TEXT, 0.35))
	t.set_color("caret_color", "LineEdit", Palette.CELL_ACID)
	t.set_color("selection_color", "LineEdit", Color(Palette.CELL_PINK, 0.4))
	var popup := box(Color(0.02, 0.04, 0.1, 0.98), Palette.TERMINAL_EDGE, 1, 6, 6)
	t.set_stylebox("panel", "PopupMenu", popup)
	t.set_stylebox("hover", "PopupMenu", box(Color(Palette.CELL_PINK, 0.3), Color(0, 0, 0, 0), 0))
	t.set_color("font_color", "PopupMenu", Palette.TERMINAL_TEXT)
	t.set_color("font_hover_color", "PopupMenu", Palette.PAPER)
	t.set_stylebox("panel", "TooltipPanel", box(Color(0.02, 0.03, 0.08, 0.97), Palette.CELL_PINK, 1, 8, 5))
	t.set_color("font_color", "TooltipLabel", Palette.PAPER)


static func _panels(t: Theme) -> void:
	var clear := StyleBoxFlat.new()
	clear.bg_color = Color(0, 0, 0, 0)
	t.set_stylebox("panel", "PanelContainer", clear)
	var v := "TerminalPanel"
	t.set_type_variation(v, "PanelContainer")
	var p := box(Palette.TERMINAL_BG, Palette.TERMINAL_EDGE, 1, 14, 10)
	# A soft dark halo round each panel keeps it readable over the bright city.
	p.shadow_color = Color(0, 0, 0, 0.6)
	p.shadow_size = 18
	p.shadow_offset = Vector2(3, 4)
	t.set_stylebox("panel", v, p)
	var g := "GlassPanel"
	t.set_type_variation(g, "PanelContainer")
	var glass := box(Color(0.02, 0.04, 0.1, 0.9), Color(Palette.TERMINAL_EDGE, 0.35), 1, 12, 8)
	glass.shadow_color = Color(0, 0, 0, 0.45)
	glass.shadow_size = 14
	t.set_stylebox("panel", g, glass)
	var hud := "HudLabel"
	t.set_type_variation(hud, "Label")
	var strip := box(Color(0, 0, 0, 0.82), Palette.CELL_PINK, 0, 10, 5)
	strip.border_width_bottom = 2
	t.set_stylebox("normal", hud, strip)
	t.set_color("font_color", hud, Palette.PAPER)
	var lg := "LogText"
	t.set_type_variation(lg, "RichTextLabel")
	var log_box := box(Color(0.01, 0.03, 0.07, 0.9), Color(Palette.TERMINAL_EDGE, 0.4), 1, 12, 6)
	log_box.border_width_left = 3
	log_box.border_color = Color(Palette.NET_CYAN, 0.6)
	t.set_stylebox("normal", lg, log_box)
	t.set_stylebox("focus", lg, box(Color(0, 0, 0, 0), Palette.CELL_ACID, 2))
	t.set_color("default_color", lg, Color(Palette.TERMINAL_TEXT, 0.9))
	# Tabs (options, codex): terminal tabs with a pink active underline.
	var tab := box(Palette.TERMINAL_BG, Color(Palette.TERMINAL_EDGE, 0.4), 1, 10, 4)
	var tab_on := box(Palette.TERMINAL_BG_HOT, Palette.CELL_PINK, 0, 10, 4)
	tab_on.border_width_bottom = 3
	t.set_stylebox("tab_unselected", "TabBar", tab)
	t.set_stylebox("tab_hovered", "TabBar", box(Palette.TERMINAL_BG_HOT, Palette.CELL_PINK, 1, 10, 4))
	t.set_stylebox("tab_selected", "TabBar", tab_on)
	t.set_stylebox("tab_focus", "TabBar", box(Color(0, 0, 0, 0), Palette.CELL_ACID, 2, 10, 4))
	t.set_color("font_selected_color", "TabBar", Palette.PAPER)
	t.set_color("font_unselected_color", "TabBar", Palette.TERMINAL_TEXT)
	t.set_color("font_hovered_color", "TabBar", Palette.PAPER)


static func _bars(t: Theme) -> void:
	for kind in ["VScrollBar", "HScrollBar"]:
		var track := box(Color(0, 0, 0, 0.35), Color(0, 0, 0, 0), 0, 3, 3)
		var grab := box(Color(Palette.NET_CYAN, 0.45), Color(0, 0, 0, 0), 0, 3, 3)
		var grab_hot := box(Color(Palette.CELL_PINK, 0.8), Color(0, 0, 0, 0), 0, 3, 3)
		t.set_stylebox("scroll", kind, track)
		t.set_stylebox("grabber", kind, grab)
		t.set_stylebox("grabber_highlight", kind, grab_hot)
		t.set_stylebox("grabber_pressed", kind, grab_hot)
	var slider := box(Color(Palette.NET_CYAN, 0.18), Color(0, 0, 0, 0), 0, 0, 3)
	var fill := box(Color(Palette.CELL_PINK, 0.85), Color(0, 0, 0, 0), 0, 0, 3)
	t.set_stylebox("slider", "HSlider", slider)
	t.set_stylebox("grabber_area", "HSlider", fill)
	t.set_stylebox("grabber_area_highlight", "HSlider", fill)


static var _crt: ShaderMaterial = null


## The shared terminal-glass material (scanlines + flicker) for terminal panels, the HUD
## and log strips; zeroed under reduce-effects.
static func crt_material() -> ShaderMaterial:
	if _crt == null:
		_crt = ShaderMaterial.new()
		_crt.shader = load("res://shaders/crt_panel.gdshader")
		ShaderReduce.track(_crt)  # ART-0 E: rc_common's reduce_effects
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
	img.fill(Color(0, 0, 0, 0))
	for y in 14:
		var x := y if y < 7 else 13 - y
		for w in 3:
			var px := x + w - 1
			if px >= 0 and px < 10:
				img.set_pixel(px, y, Color.WHITE)
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


## Applies the theme to `root` and re-applies it while `root` lives and Settings change.
## One static listener serves every root (bound callables are not distinct connections).
static func apply(root: Control) -> void:
	root.theme = build(Settings.text_scale)
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
