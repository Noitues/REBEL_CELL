class_name ZinePanel
extends Control
## Zine paper panel (STYLE_GUIDE 1, 4; ART_BIBLE §2 PAPER): halftone paper, ink border, tape
## strips, a hard shadow, a slight tilt. Put content in `content` (a MarginContainer).
## `terminal` panels (options, pause, confirm) are GLASS instead: navy glass with a SCRIM
## behind it (`GlassScrim`; opaque under high contrast), a mono title over a `CELL_PINK`
## rule and corner brackets, never paper, tape or tilt (§2: materials never mix).
##
## Type and spacing come from the scale (§4.2, §5.1): the title at `label` times the text
## scale (the paper title in marker, the glass title in mono), the content inset by the
## panel padding. The panel is at least as big as its content (it sizes to it inside a
## container, and never draws its content outside itself); `scroll_content(max)` caps the
## content's height, past which it scrolls inside with a MORE BELOW hint (§5.3).

const PAPER_SHADER := preload("res://shaders/zine_paper.gdshader")

@export var tilt_degrees: float = 0.0
@export var tape: bool = true
@export var title: String = ""
## System dialogs (options, pause, confirm) render as terminal glass instead of paper:
## DISPATCH-style system surfaces stay clean (STYLE_GUIDE 3).
var terminal: bool = false

var content: MarginContainer
var _paper: ColorRect
## The blur-and-dim behind a glass panel (null on paper).
var scrim: GlassScrim = null
## The scrolling view once `scroll_content` capped the content (null until then).
var fit: FitScroll = null

## The title's type step (§4.2) and its size at text scale 1.0 (px; kept for callers).
const TITLE_STEP := UiTheme.LABEL
const TITLE_SIZE := TITLE_STEP
## The title's size in use (px): the step times the text scale.
var title_size: int = TITLE_SIZE
## Tape strips overhang the panel's top edge by this much (px), and their sizes.
const TAPE_OVERHANG := 6.0
const TAPE_TOP := Vector2(60, 14)
const TAPE_SIDE := Vector2(16, 40)
## The hard shadow's offset (paper) and the glass shadow's (px).
const PAPER_SHADOW := 5.0
const GLASS_SHADOW := 6.0
## The glass title rule's thickness, the gap under it, and the corner brackets' arm (px).
const RULE_H := 2.0
const RULE_GAP := float(UiTheme.SP_S)
const BRACKET := 14.0
const BRACKET_W := 2.0
## The glass fill's opacity (the scrim shows the blurred city through the rest).
const GLASS_ALPHA := 0.97


func _init(p_title: String = "", p_tilt: float = 0.0, p_terminal: bool = false) -> void:
	title = p_title
	tilt_degrees = p_tilt
	terminal = p_terminal
	tape = not p_terminal
	if terminal:
		scrim = GlassScrim.new()
		scrim.show_behind_parent = true
		scrim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		add_child(scrim)
	_paper = ColorRect.new()
	_paper.name = "Paper"
	if terminal:
		_paper.color = Color(Palette.TERMINAL_BG, GLASS_ALPHA)
		_paper.material = UiTheme.crt_material()
	else:
		_paper.material = ShaderMaterial.new()
		_paper.material.shader = PAPER_SHADER
	# Behind the panel's own drawing, so the border and title stay on top of the paper.
	_paper.show_behind_parent = true
	_paper.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_paper.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_paper)
	content = MarginContainer.new()
	content.name = "Content"
	content.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(content)
	content.minimum_size_changed.connect(update_minimum_size)
	scale_title(Settings.text_scale)


func _ready() -> void:
	rotation_degrees = tilt_degrees
	pivot_offset = size / 2.0
	if not Settings.changed.is_connected(_on_settings):
		Settings.changed.connect(_on_settings)


func _on_settings() -> void:
	scale_title(Settings.text_scale)
	_sync_contrast()


## The paper title follows text scale `s` (H23 S10: the event's title stayed small and
## squeezed at 1.6); the content moves down to keep clear of it, and the side and bottom
## padding follow the panel padding (§5.1). Returns the panel.
func scale_title(s: float) -> ZinePanel:
	title_size = UiTheme.font_px_at(TITLE_STEP, s)
	content.add_theme_constant_override("margin_left", UiTheme.PANEL_PAD_H)
	content.add_theme_constant_override("margin_right", UiTheme.PANEL_PAD_H)
	content.add_theme_constant_override("margin_bottom", UiTheme.PANEL_PAD_V)
	content.add_theme_constant_override("margin_top", roundi(_head_height()))
	_sync_contrast()
	queue_redraw()
	return self


## The band the title takes at the top (px): the padding, the title's line, and for glass
## its rule and the gap under it. Without a title, the padding alone.
func _head_height() -> float:
	if title == "":
		return float(UiTheme.PANEL_PAD_V)
	var h := UiTheme.PANEL_PAD_V + _title_font().get_height(title_size)
	if terminal:
		h += RULE_H + RULE_GAP
	return ceilf(h)


func _title_font() -> Font:
	return Palette.mono() if terminal else Palette.marker()


func _sync_contrast() -> void:
	if terminal and _paper != null:
		# High contrast (§12): opaque black glass; otherwise the navy glass over its scrim.
		_paper.color = HighContrast.BG if Settings.high_contrast else Color(Palette.TERMINAL_BG, GLASS_ALPHA)


## At least as big as the content (the content never spills out of the panel).
func _get_minimum_size() -> Vector2:
	return content.get_combined_minimum_size() if content != null else Vector2.ZERO


## Caps the content's height at `max_height` px: taller content scrolls inside the panel
## with a scroll hint (§5.3). The content's children move into the scrolling view (in
## order). Returns the panel. Call again to change the cap.
func scroll_content(max_height: float) -> ZinePanel:
	if fit == null:
		var box := VBoxContainer.new()
		box.name = "Scrolled"
		for c in content.get_children():
			content.remove_child(c)
			box.add_child(c)
		fit = FitScroll.new(box, max_height)
		content.add_child(fit)
	else:
		fit.max_height = max_height
	return self


## The share of the panel's height that holds nothing (0 when it is as tall as its content;
## §5.3 allows at most 0.25).
func empty_share() -> float:
	if size.y <= 0.0:
		return 0.0
	return clampf(1.0 - get_combined_minimum_size().y / size.y, 0.0, 1.0)


## The title's baseline (local y).
func _title_baseline() -> float:
	return UiTheme.PANEL_PAD_V + _title_font().get_ascent(title_size)


## The paper title's rect (local px), for layout checks.
func title_rect() -> Rect2:
	if title == "":
		return Rect2()
	var f := _title_font()
	var x := float(UiTheme.PANEL_PAD_H)
	return Rect2(x, _title_baseline() - f.get_ascent(title_size), minf(size.x - x * 2.0, f.get_string_size(title, HORIZONTAL_ALIGNMENT_LEFT, -1, title_size).x), f.get_height(title_size))


func _draw() -> void:
	if terminal:
		_draw_terminal()
		return
	# The drop shadow only where it shows (right and bottom edges): the paper sits behind
	# this drawing, so a full shadow rect would darken the whole sheet.
	var sh := PAPER_SHADOW
	draw_rect(Rect2(Vector2(size.x, sh + 1.0), Vector2(sh, size.y)), Palette.SHADOW)
	draw_rect(Rect2(Vector2(sh, size.y), Vector2(size.x - sh, sh + 1.0)), Palette.SHADOW)
	draw_rect(Rect2(Vector2.ZERO, size), Palette.INK, false, 2.0)
	if title != "":
		draw_string(Palette.marker(), Vector2(UiTheme.PANEL_PAD_H, _title_baseline()), title, HORIZONTAL_ALIGNMENT_LEFT, size.x - UiTheme.PANEL_PAD_H * 2.0, title_size, Palette.INK)
	if tape:
		draw_rect(Rect2(Vector2(size.x * 0.35, -TAPE_OVERHANG), TAPE_TOP), Palette.TAPE)
		draw_rect(Rect2(Vector2(-TAPE_SIDE.x * 0.5, size.y * 0.4), TAPE_SIDE), Palette.TAPE)


func _draw_terminal() -> void:
	var r := Rect2(Vector2.ZERO, size)
	var sh := GLASS_SHADOW
	draw_rect(Rect2(Vector2(size.x, sh + 2.0), Vector2(sh, size.y)), Palette.SHADOW)
	draw_rect(Rect2(Vector2(sh, size.y), Vector2(size.x - sh, sh + 2.0)), Palette.SHADOW)
	draw_rect(r, Palette.TERMINAL_EDGE, false, 1.0)
	if title != "":
		var f := _title_font()
		var pad := float(UiTheme.PANEL_PAD_H)
		draw_string(f, Vector2(pad, _title_baseline()), title, HORIZONTAL_ALIGNMENT_LEFT, size.x - pad * 2.0, title_size, Palette.TEXT_HI)
		var rule_y := UiTheme.PANEL_PAD_V + f.get_height(title_size) + RULE_H * 0.5
		draw_rect(Rect2(pad, rule_y, size.x - pad * 2.0, RULE_H), Palette.CELL_PINK)
	for c in [r.position, Vector2(r.end.x, 0), r.end, Vector2(0, r.end.y)]:
		var sx := 1.0 if c.x <= 0.0 else -1.0
		var sy := 1.0 if c.y <= 0.0 else -1.0
		draw_line(c, c + Vector2(BRACKET * sx, 0), Palette.NET_CYAN, BRACKET_W)
		draw_line(c, c + Vector2(0, BRACKET * sy), Palette.NET_CYAN, BRACKET_W)
