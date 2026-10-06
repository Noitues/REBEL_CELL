class_name HeatGauge
extends HeatPoster
## HQ-B (M14, designer ruling Q1 2026-10-05; the HQ redesign's `heat_indicator.jpg`): the
## one Heat indicator of the whole game, in the top bar's first slot on every screen at the
## same pixels. A terminal tag: the "HEAT" caption, the number in bare Anton in its band's
## colour, the band word printed (never colour alone: COOL / NOTICED / FLAGGED / HUNTED /
## PURGE), "/max", and the five-band strip with its threshold ticks and a marker at the Heat.
## With `interactive` (the HQ; read-only in a run, Q2) it is a button with a caret: a click,
## A on focus, or the pad's View (`HeatGauge.OPEN_ACTIONS`, the scene's call) opens the Heat
## terminal (`HeatTerminal`). The WANTED poster's motion moves onto it unchanged (Q1: every
## entry kept): it IS a HeatPoster (`poster` false), so the number's roll, a crossing's pop,
## shake, band stamp, banner and consequence note, the Heat memory and MotionSkip are the
## poster's own; only the drawing and the banner's room are the gauge's. View only.

signal pressed

## The look every screen shares (sizes, lettering, strip).
const LOOK := preload("res://content/config/heat_gauge_look.tres")
## The action that opens the terminal from anywhere on a screen with an interactive gauge
## (Settings.RUNTIME_ACTIONS: H); the HQ also takes the pad's View (the run's `rewind`
## button). The scene listens (Signal Up): the gauge never opens anything itself.
const OPEN_ACTION := &"open_heat"
## The caption's word (a translation key, translated where drawn).
const CAPTION := "HEAT" # TR

## True when the tag opens the Heat terminal (a caret shows, it takes focus and presses).
var interactive: bool = false:
	set(v):
		interactive = v
		focus_mode = Control.FOCUS_ALL if v else Control.FOCUS_NONE
		mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND if v else Control.CURSOR_ARROW
		queue_redraw()
var look: HeatGaugeLook = LOOK
var _hot: bool = false


func _init() -> void:
	super(false)
	name = "HeatGauge"
	custom_minimum_size = gauge_size()
	mouse_entered.connect(_set_hot.bind(true))
	mouse_exited.connect(_set_hot.bind(false))
	focus_entered.connect(queue_redraw)
	focus_exited.connect(queue_redraw)


func _ready() -> void:
	Settings.changed.connect(_refit)


func _exit_tree() -> void:
	if Settings.changed.is_connected(_refit):
		Settings.changed.disconnect(_refit)


## The drawn object's growth with the text size (STYLE 5.6: capped at the look's x1.3).
func grow() -> float:
	return clampf(Settings.text_scale, 1.0, look.scale_max)


## The gauge's size now (px).
func gauge_size() -> Vector2:
	return (look.size * grow()).ceil()


func _refit() -> void:
	custom_minimum_size = gauge_size()
	_layout_key = ""
	queue_redraw()


func _set_hot(on: bool) -> void:
	_hot = on
	queue_redraw()


func _gui_input(event: InputEvent) -> void:
	if not interactive:
		return
	var click := event is InputEventMouseButton and (event as InputEventMouseButton).pressed \
		and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT
	if click or (has_focus() and event.is_action_pressed(&"ui_accept") and not event.is_echo()):
		pressed.emit()
		accept_event()


## The band word's box (local px): where it is printed and stamps.
func band_label_rect() -> Rect2:
	var g := grow()
	var f := Palette.display()
	var px := roundi(look.band_px * g)
	var x := _strip_rect().position.x
	var base := look.pad.y * g + f.get_ascent(px)
	return Rect2(x, base - f.get_ascent(px), f.get_string_size(band_word(), HORIZONTAL_ALIGNMENT_LEFT, -1, px).x, f.get_height(px))


## The band word the number shows now (upper case, translated).
func band_word() -> String:
	return tr(BAND_WORDS[mini(shown_band(), BAND_WORDS.size() - 1)]).to_upper()


## The crossing's banner covers the tag (its own room: the top bar has none under it).
func banner_room() -> Rect2:
	var s := size if size.x > 0.0 else custom_minimum_size
	return Rect2(Vector2(BANNER_MARGIN, BANNER_MARGIN), s - Vector2(BANNER_MARGIN, BANNER_MARGIN) * 2.0)


func banner_room_wide() -> Rect2:
	return banner_room()


## The gauge's colour for the band shown (the bright band colours: it sits on a terminal).
func band_color() -> Color:
	return Palette.HEAT_BAND_COLORS[mini(shown_band(), Palette.HEAT_BAND_COLORS.size() - 1)]


## The five-band strip's box (local px).
func _strip_rect() -> Rect2:
	var g := grow()
	var s := size if size.x > 0.0 else custom_minimum_size
	var left := look.pad.x * g + s.x * look.number_share
	var right := s.x - look.pad.x * g - look.caret_px * g * 1.5
	var y := s.y - look.pad.y * g - look.strip_height * g - look.tick_overhang * g * 0.5
	return Rect2(left, y, maxf(1.0, right - left), look.strip_height * g)


## The strip's x for Heat `value` (local px).
func strip_x(value: float) -> float:
	var r := _strip_rect()
	return r.position.x + r.size.x * clampf(value / maxf(1.0, heat_max), 0.0, 1.0)


func _draw() -> void:
	var g := grow()
	var r := Rect2(Vector2.ZERO, size)
	var col := band_color()
	HudSkin.draw_terminal_panel(self, r, col, HudSkin.TERMINAL_BG)
	if interactive and (_hot or has_focus()):
		draw_rect(r.grow(-2.0), Color(col, look.hover_alpha))
	var mono := HudSkin.mono()
	var disp := Palette.display()
	# The caption and the number (it rolls, grows and flashes on a crossing: the poster's).
	var cap_px := roundi(look.caption_px * g)
	if cap_px > 0:  # B2: the fight's corner chip (Q1 c) has no caption
		draw_string(mono, Vector2(look.pad.x * g, look.pad.y * g + mono.get_ascent(cap_px)), tr(CAPTION), HORIZONTAL_ALIGNMENT_LEFT, -1, cap_px, HudSkin.TERMINAL_TEXT)
	var num_col := col
	if number_scale > 1.0:
		num_col = num_col.lerp(Palette.PAPER, clampf((number_scale - 1.0) / maxf(0.001, Motion.amplitude(&"heat_number_pop") - 1.0), 0.0, 1.0))
	var npx := roundi(look.number_px * g)
	var num_at := Vector2(look.pad.x * g, size.y - look.pad.y * g)
	draw_set_transform(num_at + Vector2(0, -npx * 0.35), 0.0, Vector2.ONE * number_scale)
	draw_string(disp, Vector2(0, npx * 0.35), "%d" % roundi(shown_heat), HORIZONTAL_ALIGNMENT_LEFT, -1, npx, num_col)
	draw_set_transform(Vector2.ZERO)
	# The band word, printed (never colour alone); it stamps on when the band changes.
	var word_r := band_label_rect()
	var bpx := roundi(look.band_px * g)
	var word_at := Vector2(word_r.position.x, word_r.position.y + disp.get_ascent(bpx))
	if stamp_scale > 1.0:
		var c := word_r.get_center()
		draw_set_transform(c, 0.0, Vector2.ONE * stamp_scale)
		draw_rect(Rect2(word_r.position - c, word_r.size).grow(STAMP_BOX_PAD), Color(col, clampf((stamp_scale - 1.0) * 4.0, 0.0, 1.0)), false, 2.0)
		_draw_spaced(disp, word_at - c, band_word(), bpx, col)
		draw_set_transform(Vector2.ZERO)
	else:
		_draw_spaced(disp, word_at, band_word(), bpx, col)
	# "/max" at the strip's right end, over it.
	var strip := _strip_rect()
	var mpx := roundi(look.max_px * g)
	var max_text := "/%d" % heat_max
	if mpx > 0:  # B2: the fight's corner chip has no "/max"
		var mw := mono.get_string_size(max_text, HORIZONTAL_ALIGNMENT_LEFT, -1, mpx).x
		draw_string(mono, Vector2(strip.end.x - mw, look.pad.y * g + mono.get_ascent(mpx)), max_text, HORIZONTAL_ALIGNMENT_LEFT, -1, mpx, HudSkin.TERMINAL_TEXT)
	_draw_strip(strip, g)
	if interactive:
		var cp := look.caret_px * g
		var tip := Vector2(size.x - look.pad.x * g * 0.5 - cp * 0.5, size.y - look.pad.y * g)
		draw_colored_polygon(PackedVector2Array([tip + Vector2(-cp * 0.6, -cp * 0.7), tip + Vector2(cp * 0.6, -cp * 0.7), tip]), col)
	if banner_alpha > 0.0:
		_draw_banner(0.0)


## `text` with the look's letter spacing (the band word reads as a printed label).
func _draw_spaced(f: Font, at: Vector2, text: String, px: int, col: Color) -> void:
	var x := at.x
	for ch in text:
		draw_string(f, Vector2(x, at.y), ch, HORIZONTAL_ALIGNMENT_LEFT, -1, px, col)
		x += f.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x + look.band_spacing * grow()


## The five-band strip: each band's stretch in its colour, lit up to the Heat and dim above
## it, the threshold ticks, and the marker over the Heat.
func _draw_strip(strip: Rect2, g: float) -> void:
	var edges: Array[float] = [0.0]
	for t in marks:
		if t > 0 and t < heat_max:
			edges.append(float(t))
	edges.append(float(heat_max))
	var at := clampf(shown_heat, 0.0, float(heat_max))
	for i in edges.size() - 1:
		var a := strip_x(edges[i])
		var b := strip_x(edges[i + 1])
		var bc: Color = Palette.HEAT_BAND_COLORS[mini(i, Palette.HEAT_BAND_COLORS.size() - 1)]
		draw_rect(Rect2(a, strip.position.y, b - a, strip.size.y), Color(bc, look.unlit_alpha))
		var lit := minf(b, strip_x(at))
		if lit > a:
			draw_rect(Rect2(a, strip.position.y, lit - a, strip.size.y), bc)
	for i in range(1, edges.size() - 1):
		var x := strip_x(edges[i])
		draw_line(Vector2(x, strip.position.y - look.tick_overhang * g * 0.5), Vector2(x, strip.end.y + look.tick_overhang * g * 0.5), Palette.PAPER, 1.5)
	var m := look.marker_px * g
	var mx := strip_x(at)
	var top := strip.position.y - m * 0.15
	draw_colored_polygon(PackedVector2Array([Vector2(mx - m * 0.6, top - m), Vector2(mx + m * 0.6, top - m), Vector2(mx, top)]), Palette.PAPER)
