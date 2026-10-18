class_name Toast
extends PanelContainer
## A short-lived terminal strip that says why an action was refused ("Not enough RAM")
## right where the player is looking (H20: refusals used to go to a hidden log).
## ART-2 2D (ART_BIBLE v2 §4.13): plain cyan terminal for a note; a refusal has a HARM edge
## and the no-entry mark. View only. Instant and static under headless or reduce effects.

## Seconds on screen (delay) and the fade at the end (duration): the `toast` motion entry.
const MOTION := &"toast"
const FONT_SIZE := 15
## A drawn no-entry mark leads the message (readable without the words): radius and the
## room it takes on the left (px at text scale 1.0).
const MARK_RADIUS := 8.0
const MARK_ROOM := 28.0

var label: Label
var _tween: Tween = null
## A refusal leads with the no-entry mark; a note (what an action just did) doesn't.
var refusal := true
var _panel: StyleBoxFlat


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = false
	var sb := StyleBoxFlat.new()
	_panel = sb
	sb.bg_color = PaletteSkins.chrome(HudSkin.TERMINAL_BG)
	sb.border_color = PaletteSkins.chrome(HudSkin.TERMINAL_EDGE)
	sb.set_border_width_all(2)
	sb.set_content_margin_all(8)
	sb.content_margin_left = MARK_ROOM
	add_theme_stylebox_override("panel", sb)
	label = Label.new()
	# Callers pass translated text (H24: the respin note was translated twice).
	label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	label.add_theme_color_override("font_color", HudSkin.TERMINAL_TEXT)
	label.add_theme_font_override("font", HudSkin.mono())
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(label)


## Shows `text` centred on `anchor` (global, the toast's bottom centre), wrapped to
## `max_width` px when given.
func show_text(text: String, anchor: Vector2, max_width: float = 0.0) -> void:
	_beside = {}
	_show(text, anchor, true, max_width)


## W0 ARTFIX: a refusal beside the thing it is about: to the right of the ring at `center` / `radius`
## (global), to its left when there is no room inside `bounds`, `BESIDE_GAP` px clear of it and
## centred on it vertically (a refusal that said it at the screen's foot read as unrelated).
func show_beside(text: String, center: Vector2, radius: float, bounds: Rect2, max_width: float = 0.0) -> void:
	_beside = {"center": center, "radius": radius, "bounds": bounds}
	_show(text, center, true, max_width)


## Where a toast of size `sz` stands beside a ring (`center`, `radius`, global): right of it with
## `gap` px clear, else left of it, held inside `bounds` vertically. Never overlaps the ring.
static func beside_position(sz: Vector2, center: Vector2, radius: float, bounds: Rect2, gap: float) -> Vector2:
	var x := center.x + radius + gap
	if x + sz.x > bounds.end.x:
		x = center.x - radius - gap - sz.x
	var y := clampf(center.y - sz.y * 0.5, bounds.position.y, maxf(bounds.position.y, bounds.end.y - sz.y))
	return Vector2(x, y).floor()


## The gap between a toast shown beside a ring and that ring (px at text scale 1.0).
const BESIDE_GAP := 12.0
var _beside: Dictionary = {}


## Shows what an action just did (no no-entry mark), e.g. where a respin landed (H23: a
## respin that landed on the same slice looked like RAM spent for nothing).
func show_note(text: String, anchor: Vector2, max_width: float = 0.0) -> void:
	_show(text, anchor, false, max_width)


func _show(text: String, anchor: Vector2, is_refusal: bool, max_width: float = 0.0) -> void:
	refusal = is_refusal
	label.autowrap_mode = TextServer.AUTOWRAP_OFF
	label.custom_minimum_size.x = 0.0
	_panel.content_margin_left = MARK_ROOM if is_refusal else _panel.content_margin_right
	queue_redraw()
	label.text = text
	label.add_theme_font_size_override("font_size", roundi(FONT_SIZE * Settings.text_scale))
	# ART-2 2D: terminal words on dark glass (high contrast: the brightest text token); the
	# edge says what it is: HARM for a refusal, cyan for a note (read each time it shows).
	label.add_theme_color_override("font_color", HudSkin.TERMINAL_HI if Settings.high_contrast else HudSkin.TERMINAL_TEXT)
	_panel.border_color = edge_color()
	_panel.bg_color = PaletteSkins.chrome(HudSkin.TERMINAL_BG)  # ART-12 12s-b: re-valued per show (a skin may have changed)
	_panel.set_border_width_all(roundi(edge_width()))
	if max_width > 0.0:
		var chrome := _panel.content_margin_left + _panel.content_margin_right
		var natural := label.get_theme_font("font").get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, label.get_theme_font_size("font_size")).x
		if natural + chrome > max_width:
			UiWrap.whole_words(label)  # ART-0 F (art pass W9F §4.3.3): whole words, never mid-word
			label.custom_minimum_size.x = max_width - chrome
	_anchor = anchor
	_reanchor()
	# A wrapped label reports its height a frame late: place it again then.
	_reanchor.call_deferred()
	modulate.a = 1.0
	visible = true
	if _tween != null and _tween.is_valid():
		_tween.kill()
	if DisplayServer.get_name() == "headless":
		return  # stays up for tests to read; the next action replaces it
	_tween = create_tween()
	_tween.tween_interval(Motion.delay_of(MOTION))
	if Fx.effects_enabled():
		var e := Motion.entry(MOTION)
		_tween.tween_property(self, "modulate:a", 0.0, Motion.seconds(MOTION)).set_ease(e.ease).set_trans(e.trans)
	_tween.tween_callback(hide)


func _draw() -> void:
	if not refusal:
		return
	var r := MARK_RADIUS * Settings.text_scale
	var c := Vector2(MARK_ROOM * 0.5, size.y * 0.5)
	var mark := Palette.HARM
	draw_arc(c, r, 0, TAU, 20, mark, 3.0, true)
	var d := Vector2(r, -r) * 0.7
	draw_line(c - d, c + d, mark, 3.0, true)


## Bottom centre on the anchor at the toast's current size.
func _reanchor() -> void:
	reset_size()
	var sz := get_combined_minimum_size()
	if not _beside.is_empty():
		global_position = beside_position(sz, _beside["center"], float(_beside["radius"]), _beside["bounds"], BESIDE_GAP * Settings.text_scale)
		return
	global_position = (_anchor - Vector2(sz.x * 0.5, sz.y)).floor()
	if clear_root != null and is_instance_valid(clear_root):
		_lift_off_controls(sz)


var _anchor := Vector2.ZERO
## ART-R1 F7: the node whose visible buttons a toast must never cover (the combat scene); it
## stands higher, step by step, until it is clear of every one of them.
var clear_root: Node = null
const CLEAR_STEP := 8.0
const CLEAR_TRIES := 40


## ART-R1 F7: every visible button under `root` (global rects).
static func button_rects(root: Node) -> Array[Rect2]:
	var out: Array[Rect2] = []
	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is BaseButton and (n as Control).is_visible_in_tree() and (n as Control).size.x > 1.0:
			out.append((n as Control).get_global_rect())
		for c in n.get_children():
			stack.append(c)
	return out


## ART-R1 F7: moves the toast up until its rect meets no visible button (as it stands when
## none can be cleared within the tries).
func _lift_off_controls(sz: Vector2) -> void:
	var rects := button_rects(clear_root)
	var r := Rect2(global_position, sz)
	var tries := 0
	while tries < CLEAR_TRIES and _hits_any(r, rects):
		r.position.y -= CLEAR_STEP
		tries += 1
	if tries < CLEAR_TRIES:
		global_position = r.position


func _hits_any(r: Rect2, rects: Array[Rect2]) -> bool:
	for b in rects:
		if r.intersects(b):
			return true
	return false


func text() -> String:
	return label.text if visible else ""


# --- Edge (ART-0 F high contrast kept: the edge is opaque and at least PaperInk.EDGE_PX) ----
## The toast's edge width out of high contrast (px).
const EDGE_PX := 2.0


## The toast's edge: HARM on a refusal, the terminal cyan on a note (opaque in high contrast).
func edge_color() -> Color:
	var c := Palette.HARM if refusal else PaletteSkins.chrome(HudSkin.TERMINAL_EDGE)
	return Color(c, 1.0) if Settings.high_contrast else c


## The toast's edge width (px): EDGE_PX, at least PaperInk.EDGE_PX under high contrast.
func edge_width() -> float:
	return PaperInk.edge_width(EDGE_PX)
