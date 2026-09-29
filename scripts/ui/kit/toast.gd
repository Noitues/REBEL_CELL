class_name Toast
extends PanelContainer
## ART_BIBLE §6.7: the game's **one** toast. A `NOTE_YELLOW` sticky with a strip of tape, a
## drawn glyph (the no-entry mark for a refusal, an info "i" otherwise) and the words in the
## `label` step (Permanent Marker, INK). It sits near what it refers to (an anchor Control),
## or at the bottom centre of its host when global, and never covers a usable control or
## the pad prompt bar (DECISIONS H20 "a toast can sit over a bottom control for 3.5 s" is
## closed by `spot`). Timing (§10): `toast_in` 0.18 s, held `hold_seconds` (at least
## `toast_hold` 2.5 s, longer words to the stamp reading rule), `toast_out` 0.2 s.
## Ignores the mouse and focus. View only.
##
## Two ways in: `pop_on(host, text, refusal, anchor)` puts a fresh toast on a screen
## (replacing the one there; ToastNote.show_on is this with the old signature), and a
## screen that keeps its own Toast (combat) calls `show_text` / `show_note` with the spot
## (bottom centre) it has room for.

const NODE_NAME := "Toast"
const IN_MOTION := &"toast_in"
const HOLD_MOTION := &"toast_hold"
const OUT_MOTION := &"toast_out"
## The glyph's radius and the room it takes on the left (px at text scale 1.0).
const GLYPH_R := 9.0
const GLYPH_ROOM := 30.0
## Padding round the words (px at 1.0), and the widest a toast gets (px at 1.0; also never
## wider than its host less SIDE_GAP each side).
const PAD_H := 12.0
const PAD_V := 8.0
const MAX_WIDTH := 520.0
## Gaps: to the host's bottom and sides, to the anchor, and the step a bottom toast climbs
## by while it would cover a control (px).
const BOTTOM_GAP := 18.0
const SIDE_GAP := 24.0
const ANCHOR_GAP := 8.0
const CLIMB_STEP := 12.0
## The tape strip across the top (px at 1.0) and its tilt (degrees: paper is never square).
const TAPE_SIZE := Vector2(46, 12)
const TAPE_TILT := -4.0
## The hard paper shadow's offset (px).
const SHADOW_OFFSET := Vector2(3, 4)

var label: Label
## A refusal leads with the no-entry mark; a note (what an action just did) with "i".
var refusal := true
## Freed after it fades (pop_on toasts); a screen's own toast only hides.
var free_after := false
var _panel: StyleBoxFlat
var _tween: Tween = null
var _anchor := Vector2.ZERO
var _anchor_ctl: WeakRef = null
var _max_width := 0.0


func _init() -> void:
	name = NODE_NAME
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	visible = false
	_panel = note_style()
	add_theme_stylebox_override(&"panel", _panel)
	label = Label.new()
	# Callers pass translated text (H24: the respin note was translated twice).
	label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	label.add_theme_color_override(&"font_color", Palette.INK)
	label.add_theme_color_override(&"font_shadow_color", Color.TRANSPARENT)
	label.add_theme_font_override(&"font", Palette.marker())
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(label)


## The sticky's paper box (the SAVED stamp borrows it): NOTE_YELLOW, a faint ink edge and
## a hard offset shadow.
static func note_style() -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = Palette.NOTE_YELLOW
	sb.border_color = Color(Palette.INK, 0.35)
	sb.set_border_width_all(1)
	sb.shadow_color = Palette.SHADOW
	sb.shadow_size = 1
	sb.shadow_offset = SHADOW_OFFSET
	return sb


## How long a toast with `text` holds (s): `toast_hold` at least, longer words to the
## stamp reading rule (ZineStamp.hold_seconds). Read raw: reading time is never sped up.
static func hold_seconds(text: String) -> float:
	var e := Motion.entry(HOLD_MOTION)
	return maxf(e.duration if e != null else 0.0, ZineStamp.hold_seconds(text))


## The screen a control sits on (its top-most Control ancestor): where a toast about it goes.
static func host_of(c: Control) -> Control:
	var host: Control = c
	var p := c.get_parent()
	while p != null:
		if p is Control:
			host = p as Control
		elif p is Viewport or p is CanvasLayer:
			break
		p = p.get_parent()
	return host


## Puts a fresh toast with `text` (translated) on `host`, replacing the one there: a
## refusal (no-entry) or a note ("i"), near `anchor` when given, else bottom centre.
static func pop_on(host: Control, text: String, is_refusal: bool = true, anchor: Control = null) -> Toast:
	var t := Toast.new()
	replace_on(host, t)
	t.present(text, is_refusal, anchor)
	return t


## Adds `t` to `host` in place of any toast there.
static func replace_on(host: Control, t: Toast) -> void:
	var old := host.get_node_or_null(NODE_NAME)
	if old != null:
		host.remove_child(old)
		old.queue_free()
	t.name = NODE_NAME
	t.free_after = true
	host.add_child(t)


## Shows `text` on its host (pop_on / ToastNote.show_on): placed by `spot` (after the words
## lay out), then in, held and out; freed after.
func present(text: String, is_refusal: bool, anchor: Control = null) -> void:
	_anchor_ctl = weakref(anchor) if anchor != null else null
	var host := get_parent() as Control
	var room := MAX_WIDTH * Settings.text_scale
	if host != null and host.size.x > 0.0:
		room = minf(room, host.size.x - SIDE_GAP * 2.0)
	_set_words(text, is_refusal, room)
	_place_on_host.call_deferred()
	# A wrapped label reports its height a frame late (ANIM-R2 E9): place it again then.
	_place_on_host.call_deferred()
	_appear()
	if DisplayServer.get_name() == "headless" and is_inside_tree():
		# Headless (tests) plays no tween: the toast goes after its hold on the clock.
		get_tree().create_timer(hold_seconds(text)).timeout.connect(queue_free)


## Shows `text` as a refusal centred on `anchor` (global, the toast's bottom centre),
## wrapped to `max_width` px when given (a screen's own toast: combat's column).
func show_text(text: String, anchor: Vector2, max_width: float = 0.0) -> void:
	_show(text, anchor, true, max_width)


## Shows what an action just did ("i", not the no-entry mark), e.g. where a respin landed
## (H23: a respin that landed on the same slice looked like RAM spent for nothing).
func show_note(text: String, anchor: Vector2, max_width: float = 0.0) -> void:
	_show(text, anchor, false, max_width)


func _show(text: String, anchor: Vector2, is_refusal: bool, max_width: float) -> void:
	_set_words(text, is_refusal, max_width if max_width > 0.0 else MAX_WIDTH * Settings.text_scale)
	_anchor = anchor
	_reanchor()
	_reanchor.call_deferred()
	_appear()


## Sets the words, the glyph room and the wrap width (`room`: the widest the toast may be).
func _set_words(text: String, is_refusal: bool, room: float) -> void:
	refusal = is_refusal
	var s := Settings.text_scale
	_panel.content_margin_left = GLYPH_ROOM * s
	_panel.content_margin_right = PAD_H * s
	_panel.content_margin_top = PAD_V * s
	_panel.content_margin_bottom = PAD_V * s
	label.text = text
	label.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.LABEL))
	label.autowrap_mode = TextServer.AUTOWRAP_OFF
	label.custom_minimum_size.x = 0.0
	_max_width = room
	var chrome := _panel.content_margin_left + _panel.content_margin_right
	var natural := Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.font_px(UiTheme.LABEL)).x
	if room > 0.0 and natural + chrome > room:
		label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		label.custom_minimum_size.x = maxf(1.0, room - chrome)
	queue_redraw()


## In (`toast_in`: fade up and a small drop), held, out (`toast_out`); at once under reduce
## effects (held, then gone) and headless (stays up for tests to read).
func _appear() -> void:
	modulate.a = 1.0
	visible = true
	if _tween != null and _tween.is_valid():
		_tween.kill()
	if DisplayServer.get_name() == "headless" and not Motion.force_live:
		return
	_tween = create_tween()
	if Motion.live(IN_MOTION):
		modulate.a = 0.0
		var e := Motion.entry(IN_MOTION)
		_tween.tween_property(self, "modulate:a", 1.0, Motion.seconds(IN_MOTION)).set_ease(e.ease).set_trans(e.trans)
	_tween.tween_interval(hold_seconds(label.text))
	if Motion.live(OUT_MOTION):
		var o := Motion.entry(OUT_MOTION)
		_tween.tween_property(self, "modulate:a", 0.0, Motion.seconds(OUT_MOTION)).set_ease(o.ease).set_trans(o.trans)
	_tween.tween_callback(queue_free if free_after else hide)


## True while the toast is on screen (its words are readable).
func showing() -> bool:
	return visible and is_inside_tree()


func _draw() -> void:
	var s := Settings.text_scale
	# The tape across the top edge, tilted (paper is never square).
	draw_set_transform(Vector2(size.x * 0.5, 0.0), deg_to_rad(TAPE_TILT), Vector2.ONE)
	draw_rect(Rect2(-TAPE_SIZE * s * 0.5, TAPE_SIZE * s), Palette.NOTE_TAPE)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	var c := Vector2(GLYPH_ROOM * s * 0.5 + 2.0, size.y * 0.5)
	if refusal:
		StatIcon.draw(self, c, GLYPH_R * s, StatIcon.NO_ENTRY, Palette.HARM_INK, true)  # ink on the sticky (§3.3)
	else:
		StatIcon.draw(self, c, GLYPH_R * s, StatIcon.INFO, Palette.INK, true)


## Bottom centre on the anchor point at the toast's current size (a screen's own toast).
func _reanchor() -> void:
	reset_size()
	var sz := get_combined_minimum_size()
	global_position = (_anchor - Vector2(sz.x * 0.5, sz.y)).floor()


## Places a pop_on toast on its host by `spot`, keeping off every usable control.
func _place_on_host() -> void:
	var host := get_parent() as Control
	if host == null or not is_inside_tree():
		return
	size = Vector2.ZERO
	size = get_combined_minimum_size()
	var anchor := Rect2()
	var a: Control = _anchor_ctl.get_ref() as Control if _anchor_ctl != null else null
	if a != null and is_instance_valid(a) and a.is_inside_tree():
		anchor = a.get_global_rect()
	var avoid: Array[Rect2] = Fx.avoid_rects(get_tree().root)
	global_position = spot(host.get_global_rect(), size, anchor, avoid)


## Where a toast of `sz` goes on `host` (global rects): beside `anchor` (above, below,
## right, left) when it has one, else bottom centre climbing CLIMB_STEP at a time; always
## inside the host less its gaps; the first spot covering none of `avoid` (usable controls,
## the prompt bar), else the one covering least. Pure (tests).
static func spot(host: Rect2, sz: Vector2, anchor: Rect2, avoid: Array[Rect2]) -> Vector2:
	var tries: Array[Vector2] = []
	if anchor.has_area():
		var cx := anchor.get_center().x - sz.x * 0.5
		var cy := anchor.get_center().y - sz.y * 0.5
		tries.append(Vector2(cx, anchor.position.y - ANCHOR_GAP - sz.y))
		tries.append(Vector2(cx, anchor.end.y + ANCHOR_GAP))
		tries.append(Vector2(anchor.end.x + ANCHOR_GAP, cy))
		tries.append(Vector2(anchor.position.x - ANCHOR_GAP - sz.x, cy))
	var y := host.end.y - BOTTOM_GAP - sz.y
	while y >= host.position.y + SIDE_GAP:
		tries.append(Vector2(host.get_center().x - sz.x * 0.5, y))
		y -= CLIMB_STEP
	if anchor.has_area():
		tries.append(Vector2(host.get_center().x - sz.x * 0.5, host.end.y - BOTTOM_GAP - sz.y))
	var best := Vector2.ZERO
	var best_hits := INF
	for at in tries:
		var p := Vector2(clampf(at.x, host.position.x + SIDE_GAP, maxf(host.position.x + SIDE_GAP, host.end.x - SIDE_GAP - sz.x)),
			clampf(at.y, host.position.y, maxf(host.position.y, host.end.y - BOTTOM_GAP - sz.y)))
		var box := Rect2(p, sz)
		var hits := 0.0
		for r in avoid:
			if box.intersects(r):
				hits += box.intersection(r).get_area() + 1.0
		if anchor.has_area() and box.intersects(anchor):
			hits += box.intersection(anchor).get_area() + 1.0
		if hits < best_hits:
			best_hits = hits
			best = p
			if hits == 0.0:
				break
	return best.floor()


## The words on screen ("" while hidden).
func text() -> String:
	return label.text if visible else ""
