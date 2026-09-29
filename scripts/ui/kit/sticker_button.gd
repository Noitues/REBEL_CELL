class_name StickerButton
extends Button
## A taped paper sticker that presses like a button (combat actions around the spinner:
## NUDGE, RESPIN, UNDO and the toggles). Marker text on note paper, a tilt, tape; hover or
## focus lifts it with an acid glow. The scene decides what a press means.
## Art pass W2 (ART_BIBLE §6): all six states from KitState: hover lifts 2 px and glows,
## focus adds the FOCUS brackets, pressed drops 1 px, disabled keeps its paper and ink (the
## words at full contrast) with a DISABLED edge and a lock, refused flashes HARM with the
## no-entry mark (`refuse`).

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
## The hover / focus glow round the sticker (px, alpha x the §6 glow), its paper shadow
## offset and its edge's ink alpha.
const HOT_GROW := 3.0
const HOT_ALPHA := 0.5
const SHADOW_OFFSET := Vector2(3, 4)
const EDGE_ALPHA := 0.45


func _init(p_text: String = "", p_paper: Color = Palette.NOTE_YELLOW, p_tilt: float = 0.0) -> void:
	text = p_text
	paper = p_paper
	tilt = p_tilt
	flat = true
	clip_text = true  # the sticker measures and draws its own lettering (_fit)
	focus_mode = Control.FOCUS_ALL
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	for key in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color", "font_hover_pressed_color", "font_disabled_color"]:
		add_theme_color_override(key, Color.TRANSPARENT)  # the sticker draws its own text
	mouse_entered.connect(func() -> void: _hot = true; queue_redraw())
	mouse_exited.connect(func() -> void: _hot = false; queue_redraw())
	focus_entered.connect(func() -> void: _hot = true; queue_redraw())
	focus_exited.connect(func() -> void: _hot = false; queue_redraw())
	KitState.track(self)
	_fit()


## Shows the §6 refused state (HARM flash, no-entry mark) on the sticker.
func refuse() -> void:
	KitState.refuse(self)


## The state drawn now (KitState).
func state() -> StringName:
	return KitState.of(self)


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
			draw_arc(c, r, -PI * 0.8, PI * 0.9, 14, col, 2.0)
			var a := PI * 0.9
			var tip := c + Vector2(cos(a), sin(a)) * r
			var tg := Vector2(-sin(a), cos(a))
			draw_colored_polygon(PackedVector2Array([tip + tg * 5.0, tip + tg.orthogonal() * 4.0, tip - tg.orthogonal() * 4.0]), col)
		"undo":
			draw_arc(c + Vector2(1, 1), r * 0.8, -PI * 0.5, PI * 0.5, 10, col, 2.0)
			draw_line(c + Vector2(1, -r * 0.8 + 1), c + Vector2(-r, -r * 0.8 + 1), col, 2.0)
			var tip := c + Vector2(-r - 2, -r * 0.8 + 1)
			draw_colored_polygon(PackedVector2Array([tip, tip + Vector2(5, -4), tip + Vector2(5, 4)]), col)


func set_label(t: String) -> void:
	if t != text:
		text = t
		_fit()
		queue_redraw()


func _draw() -> void:
	var st := state()
	var r := Rect2(Vector2.ZERO, size)
	draw_set_transform(size * 0.5 + Vector2(0, KitState.lift(st)), deg_to_rad(tilt), Vector2.ONE)
	var rr := Rect2(-size * 0.5, size)
	if st == KitState.HOVER or st == KitState.FOCUS or st == KitState.PRESSED:
		draw_rect(rr.grow(HOT_GROW), Color(Palette.CELL_ACID, HOT_ALPHA * KitState.glow(st)))
	draw_rect(Rect2(rr.position + SHADOW_OFFSET, rr.size), Palette.SHADOW)
	draw_rect(rr, paper)
	draw_rect(rr, Palette.DISABLED if st == KitState.DISABLED else Color(Palette.INK, EDGE_ALPHA), false, 1.0)
	draw_rect(Rect2(Vector2(-12, rr.position.y - 5), Vector2(24, 9)), Palette.NOTE_TAPE)
	var fs := font_px()
	var baseline := rr.position.y + (rr.size.y + Palette.marker().get_ascent(fs) - Palette.marker().get_descent(fs)) * 0.5
	var ink := Palette.INK
	var text_x := rr.position.x
	var text_w := rr.size.x
	if drawn_icon != "":
		var s := Settings.text_scale
		var ic := Vector2(rr.position.x + ICON_ROOM * 0.5 * s + 4.0, rr.position.y + rr.size.y * 0.5)
		_draw_icon(ic, 7.0 * s, ink)
		text_x += ICON_ROOM * s
		text_w -= ICON_ROOM * s
	draw_string(Palette.marker(), Vector2(text_x, baseline), shown_text(), HORIZONTAL_ALIGNMENT_CENTER, text_w, fs, ink)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	KitState.draw_frame(self, r.grow(-1.0), st)
