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
## Art pass WF: the width the share is taken of (px); 0 = the page's (viewport's) width.
var container_width: float = 0.0
## Art pass WF: the growth cap in use, a share of `container_width` (MAX_SHARE is the one to
## use); 0 = no cap, the sticker grows with the text scale as before. Opt-in: combat sizes
## its hand from the room the stickers leave, so it switches this on together with a
## ceiling on the hand's scale (the wheels keep 70%, §12).
var max_share: float = 0.0:
	set(v):
		max_share = maxf(0.0, v)
		_fit()
## The lettering size and the sticker's own scale (lettering / FONT_SIZE) chosen by _fit.
var _px: int = FONT_SIZE
var _k: float = 1.0
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
## Art pass WF: the recommended cap (see `max_share`): the most of its container's width a
## sticker takes (the page's width when no `container_width` is given). Past it the lettering yields a type step (to caption at the
## text scale), then stops growing with the text scale (never under caption at 1.0), and
## the whole sticker (height, padding, icon) follows the lettering.
const MAX_SHARE := 0.2
## The width the share is taken of when the sticker isn't on a page yet (the reference
## viewport, px).
const REFERENCE_WIDTH := 1280.0
## The text scale is walked down by this step while the sticker is still too wide.
const YIELD_STEP := 0.1
## The drawn icon's radius and its inset from the sticker's left edge (px at 1.0).
const ICON_R := 7.0
const ICON_INSET := 4.0
## The tape strip across the top (px at 1.0).
const TAPE_SIZE := Vector2(24, 9)


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


## Art pass WF: the lettering size in use (px): font_px() while the sticker keeps under
## MAX_SHARE of its container, else a step smaller (see MAX_SHARE).
func lettering_px() -> int:
	return _px


## The sticker's own scale (the lettering over FONT_SIZE): its height, padding and icon.
func sticker_scale() -> float:
	return _k


## The width MAX_SHARE is taken of (px).
func share_of() -> float:
	if container_width > 0.0:
		return container_width
	if is_inside_tree():
		return get_viewport_rect().size.x
	return REFERENCE_WIDTH


## The sticker's width with lettering `px` at sticker scale `k` (px).
func width_at(px: int, k: float) -> float:
	var w := Palette.marker().get_string_size(shown_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, px).x + PADDING * k + (ICON_ROOM * k if drawn_icon != "" else 0.0)
	return maxf(MIN_WIDTH * k, w)


func _fit() -> void:
	var cap := share_of() * max_share if max_share > 0.0 else INF
	_px = yield_px(cap)
	_k = _scale_for(_px)
	custom_minimum_size = Vector2(width_at(_px, _k), HEIGHT * _k)
	size = get_combined_minimum_size()


## The lettering size that keeps the sticker under `cap` px wide: font_px() (the text
## scale's), else one type step down (caption at the scale), else caption with the scale
## walked down by YIELD_STEP, the 1.0 lettering and last caption at 1.0 (the floor).
func yield_px(cap: float) -> int:
	var scale := Settings.text_scale
	var tries: Array[int] = [font_px(), FONT_SIZE]
	var k := scale
	while k > 1.0 - 0.001:
		tries.append(UiTheme.font_px_at(UiTheme.CAPTION, k))
		k -= YIELD_STEP
	tries.append(UiTheme.font_px_at(UiTheme.CAPTION, 1.0))
	tries.sort()
	tries.reverse()
	for px in tries:
		if width_at(px, _scale_for(px)) <= cap:
			return px
	return tries[tries.size() - 1]


## The sticker scale that goes with lettering `px` (never under 1.0's sticker unless the text
## scale is under 1.0).
func _scale_for(px: int) -> float:
	return minf(Settings.text_scale, maxf(float(px) / FONT_SIZE, minf(1.0, Settings.text_scale)))


## Art pass WF: where the lettering is drawn inside the (untilted) sticker, local: the paper
## less the icon's room, the words centred in it at lettering_px().
func lettering_rect() -> Rect2:
	var f := Palette.marker()
	var w := f.get_string_size(shown_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, _px).x
	var x0 := ICON_ROOM * _k if drawn_icon != "" else 0.0
	var room := size.x - x0
	var h := f.get_ascent(_px) + f.get_descent(_px)
	return Rect2(Vector2(x0 + (room - w) * 0.5, (size.y - h) * 0.5), Vector2(w, h))


func _notification(what: int) -> void:
	if what == NOTIFICATION_ENTER_TREE:
		_fit()  # the page's width is known now (MAX_SHARE)


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
	draw_rect(Rect2(Vector2(-TAPE_SIZE.x * 0.5, rr.position.y - TAPE_SIZE.y * 0.55), TAPE_SIZE), Palette.NOTE_TAPE)
	var ink := Palette.INK
	if drawn_icon != "":
		var ic := Vector2(rr.position.x + ICON_ROOM * 0.5 * _k + ICON_INSET, rr.position.y + rr.size.y * 0.5)
		_draw_icon(ic, ICON_R * _k, ink)
	var lr := lettering_rect()
	draw_string(Palette.marker(), rr.position + Vector2(lr.position.x, lr.position.y + Palette.marker().get_ascent(_px)), shown_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, _px, ink)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	KitState.draw_frame(self, r.grow(-1.0), st)
