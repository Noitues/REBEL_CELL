class_name StickerButton
extends Button
## A taped paper sticker that presses like a button (combat actions around the spinner:
## NUDGE, RESPIN, UNDO and the toggles). Marker text on note paper, a tilt, tape; hover or
## focus lifts it with an acid glow. The scene decides what a press means.

var paper: Color = Palette.NOTE_YELLOW
var tilt: float = 0.0
var _hot: bool = false
## A drawn mark before the lettering ("respin": a circular arrow, "undo": a hooked arrow),
## so the sticker reads without words (H22). "" = none.
var drawn_icon: String = ""
const ICON_ROOM := 22.0

## Marker lettering size and sticker height at text scale 1.0 (px).
const FONT_SIZE := 14
const HEIGHT := 30.0
const MIN_WIDTH := 64.0
const PADDING := 22.0
## Alpha of the acid glow behind a hot sticker.
const GLOW_ALPHA: float = 0.5
## How far the glow grows past the sticker rect (px).
const GLOW_GROW_PX: float = 3.0
## Drop shadow offset (px).
const SHADOW_OFFSET: Vector2 = Vector2(3, 4)
## Alpha of the paper outline.
const OUTLINE_ALPHA: float = 0.45
## Alpha of the disabled ink.
const DISABLED_INK_ALPHA: float = 0.5
## Darkening of the paper when disabled.
const DISABLED_DARKEN: float = 0.45
## Tape strip: left offset x (px).
const TAPE_OFFSET_X: float = -12.0
## Tape strip: rise above the sticker top (px).
const TAPE_RISE_PX: float = 5.0
## Tape strip size (px).
const TAPE_SIZE: Vector2 = Vector2(24, 9)
## Stroke width of drawn icons (px).
const ICON_LINE_PX: float = 2.0
## Point count of icon arcs.
const ARC_POINTS_RESPIN: int = 14
const ARC_POINTS_UNDO: int = 10
## Arrowhead half-sizes for the respin icon (px).
const RESPIN_HEAD_TANGENT_PX: float = 5.0
const RESPIN_HEAD_NORMAL_PX: float = 4.0
## Undo icon geometry.
const UNDO_CENTER_SHIFT: Vector2 = Vector2(1, 1)
const UNDO_ARC_RATIO: float = 0.8
const UNDO_TIP_EXTRA_PX: float = 2.0
const UNDO_HEAD_LEN_PX: float = 5.0
const UNDO_HEAD_HALF_PX: float = 4.0
## Fraction of PI for the respin arc start and end angle.
const RESPIN_ARC_START: float = 0.8
const RESPIN_ARC_END: float = 0.9


func _init(p_text: String = "", p_paper: Color = Palette.NOTE_YELLOW, p_tilt: float = 0.0) -> void:
	text = p_text
	paper = p_paper
	tilt = p_tilt
	flat = true
	clip_text = true  # the sticker measures and draws its own lettering (_fit)
	focus_mode = Control.FOCUS_ALL
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	for key in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color", "font_hover_pressed_color", "font_disabled_color"]:
		add_theme_color_override(key, Color(0, 0, 0, 0))  # the sticker draws its own text
	mouse_entered.connect(func() -> void: _hot = true; queue_redraw())
	mouse_exited.connect(func() -> void: _hot = false; queue_redraw())
	focus_entered.connect(func() -> void: _hot = true; queue_redraw())
	focus_exited.connect(func() -> void: _hot = false; queue_redraw())
	KitState.track(self)  # ART-0 F (art pass W2, §6): the six states
	_fit()


## ART-0 F (§6): the state drawn now (KitState).
func state() -> StringName:
	return KitState.of(self)


## ART-0 F (§6 Error / refused): flashes the refused state (HARM outline, no-entry mark).
func refuse() -> void:
	KitState.refuse(self)


## The lettering size: Settings.text_scale reaches the stickers too (GDD 9.6).
static func font_px() -> int:
	return roundi(FONT_SIZE * Settings.text_scale)


## The lettering as drawn and measured: translated (H23 S16: drawn words never were).
func shown_text() -> String:
	return text if pre_translated else tr(text)  # H24 S4: tr, so a page shown as given still translates the key


## The label is already translated (its caller builds it from translated parts with a
## number or key hint in it, which no translation key matches).
var pre_translated := false


func _fit() -> void:
	var scale := Settings.text_scale
	var w := Palette.marker().get_string_size(shown_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, font_px()).x + PADDING * scale + (ICON_ROOM * scale if drawn_icon != "" else 0.0)
	custom_minimum_size = Vector2(maxf(MIN_WIDTH * scale, w), HEIGHT * scale)
	size = get_combined_minimum_size()


## Re-measures after a text-scale change.
func refit() -> void:
	_fit()
	queue_redraw()


func _draw_icon(c: Vector2, r: float, col: Color) -> void:
	match drawn_icon:
		"respin":
			draw_arc(c, r, -PI * RESPIN_ARC_START, PI * RESPIN_ARC_END, ARC_POINTS_RESPIN, col, ICON_LINE_PX)
			var a := PI * RESPIN_ARC_END
			var tip := c + Vector2(cos(a), sin(a)) * r
			var tg := Vector2(-sin(a), cos(a))
			draw_colored_polygon(PackedVector2Array([tip + tg * RESPIN_HEAD_TANGENT_PX, tip + tg.orthogonal() * RESPIN_HEAD_NORMAL_PX, tip - tg.orthogonal() * RESPIN_HEAD_NORMAL_PX]), col)
		"undo":
			draw_arc(c + UNDO_CENTER_SHIFT, r * UNDO_ARC_RATIO, -PI * 0.5, PI * 0.5, ARC_POINTS_UNDO, col, ICON_LINE_PX)
			draw_line(c + Vector2(1, -r * UNDO_ARC_RATIO + 1), c + Vector2(-r, -r * UNDO_ARC_RATIO + 1), col, ICON_LINE_PX)
			var tip := c + Vector2(-r - UNDO_TIP_EXTRA_PX, -r * UNDO_ARC_RATIO + 1)
			draw_colored_polygon(PackedVector2Array([tip, tip + Vector2(UNDO_HEAD_LEN_PX, -UNDO_HEAD_HALF_PX), tip + Vector2(UNDO_HEAD_LEN_PX, UNDO_HEAD_HALF_PX)]), col)


func set_label(t: String) -> void:
	if t != text:
		text = t
		_fit()
		queue_redraw()


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	var st := state()
	# ART-0 F (§6): hover lifts the sticker, a press drops it.
	draw_set_transform(size * 0.5 + Vector2(0, KitState.lift(st)), deg_to_rad(tilt), Vector2.ONE)
	var rr := Rect2(-size * 0.5, size)
	if _hot and not disabled:
		draw_rect(rr.grow(GLOW_GROW_PX), Color(Palette.CELL_ACID, GLOW_ALPHA))
	draw_rect(Rect2(rr.position + SHADOW_OFFSET, rr.size), Palette.SHADOW)
	draw_rect(rr, paper if not disabled else paper.darkened(DISABLED_DARKEN))
	draw_rect(rr, Color(Palette.INK, OUTLINE_ALPHA), false, 1.0)
	draw_rect(Rect2(Vector2(TAPE_OFFSET_X, rr.position.y - TAPE_RISE_PX), TAPE_SIZE), Palette.NOTE_TAPE)
	var fs := font_px()
	var baseline := rr.position.y + (rr.size.y + Palette.marker().get_ascent(fs) - Palette.marker().get_descent(fs)) * 0.5
	var ink := Palette.INK if not disabled else Color(Palette.INK, DISABLED_INK_ALPHA)
	var text_x := rr.position.x
	var text_w := rr.size.x
	if drawn_icon != "":
		var s := Settings.text_scale
		var ic := Vector2(rr.position.x + ICON_ROOM * 0.5 * s + 4.0, rr.position.y + rr.size.y * 0.5)
		_draw_icon(ic, 7.0 * s, ink)
		text_x += ICON_ROOM * s
		text_w -= ICON_ROOM * s
	HighContrast.draw_text(self, Palette.marker(), Vector2(text_x, baseline), shown_text(), HORIZONTAL_ALIGNMENT_CENTER, text_w, fs, ink)
	# ART-0 F (§6): the disabled lock and the refused mark on the sticker's face; its focus is
	# the lime halo above (a sticker's focus, v2 §2.10), never brackets.
	KitState.draw_frame(self, rr, st, false)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	r = r
