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
## RAID-FIX D5: the countdown chip hanging under the bar at the raid threshold's tick (a translation key: at, Heat
## still to gain) and the compact "(24)" after "/max" on the top row.
const RAID_NEXT := "RAID AT %d \u00b7 %d AWAY" # TR
const RAID_AWAY_COMPACT := "(%d)"
## The chip's room round its words (px at 1.0), the gap under the gauge's box, the pointer's base and its edge width.
const CHIP_PAD := Vector2(5.0, 2.0)
const CHIP_GAP := 2.0
const CHIP_POINTER_W := 8.0
const CHIP_EDGE_W := 1.5
## The room kept under the chip for the threshold banner (px at 1.0), and the gap between them.
const BANNER_BELOW_GAP := 4.0
const BANNER_BELOW_H := 40.0
## The Heat of the next raid threshold and the Heat to gain ({"at", "away"}, HeatRules.next_raid; {} = none): the
## countdown words and a tick on the strip. Set by the HQ (a view: it reads the rule).
var raid_next: Dictionary = {}:
	set(v):
		raid_next = v
		queue_redraw()

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
	if not raid_next.is_empty():
		# RAID-FIX D5: with the countdown chip on the bar, the banner stands outside the box, under the chip (it
		# never covers the bar or the chip).
		var top := s.y + chip_height() + (CHIP_GAP + BANNER_BELOW_GAP) * grow()
		return Rect2(BANNER_MARGIN, top, s.x - BANNER_MARGIN * 2.0, BANNER_BELOW_H * grow())
	return Rect2(Vector2(BANNER_MARGIN, BANNER_MARGIN), s - Vector2(BANNER_MARGIN, BANNER_MARGIN) * 2.0)


func banner_room_wide() -> Rect2:
	return banner_room()


## RAID-FIX D5: the countdown chip's words ("RAID AT 100 · 24 AWAY"; "" with no raid ahead).
func chip_words() -> String:
	if raid_next.is_empty():
		return ""
	return tr(RAID_NEXT) % [int(raid_next["at"]), int(raid_next["away"])]


## The chip's lettering (px: the "/max" size).
func chip_px() -> int:
	return roundi(look.max_px * grow())


## The chip's height (px; 0 with no raid ahead).
func chip_height() -> float:
	if raid_next.is_empty() or chip_px() <= 0:
		return 0.0
	return ceilf(HudSkin.mono().get_height(chip_px()) + CHIP_PAD.y * 2.0 * grow())


## The x of the raid threshold's tick on the strip (local px; the chip's pointer stands on it).
func raid_tick_x() -> float:
	return strip_x(float(raid_next["at"])) if not raid_next.is_empty() else -1.0


## The chip's box (local px): under the gauge's box, kept in the gauge's width, over the tick.
func chip_rect() -> Rect2:
	if raid_next.is_empty() or chip_px() <= 0:
		return Rect2()
	var g := grow()
	var s := size if size.x > 0.0 else custom_minimum_size
	var w := HudSkin.mono().get_string_size(chip_words(), HORIZONTAL_ALIGNMENT_LEFT, -1, chip_px()).x + CHIP_PAD.x * 2.0 * g
	var x := clampf(raid_tick_x() - w * 0.5, 0.0, maxf(0.0, s.x - w))
	return Rect2(x, s.y + CHIP_GAP * g, w, chip_height())


## The chip's pointer (its apex on the tick, the tick's foot, its base on the chip's top; local px).
func chip_pointer() -> PackedVector2Array:
	var c := chip_rect()
	var g := grow()
	var strip := _strip_rect()
	var apex := Vector2(raid_tick_x(), strip.end.y + look.tick_overhang * g)
	var half := CHIP_POINTER_W * g * 0.5
	return PackedVector2Array([apex, Vector2(apex.x + half, c.position.y), Vector2(apex.x - half, c.position.y)])


## The raid threshold's band colour (the next band's: the chip's edge).
func chip_color() -> Color:
	var b := band_of(int(raid_next["at"]), marks)
	return Palette.HEAT_BAND_COLORS[mini(b, Palette.HEAT_BAND_COLORS.size() - 1)]


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
		HighContrast.draw_text(self, mono, Vector2(look.pad.x * g, look.pad.y * g + mono.get_ascent(cap_px)), tr(CAPTION), HORIZONTAL_ALIGNMENT_LEFT, -1, cap_px, HudSkin.TERMINAL_TEXT)
	var num_col := col
	if number_scale > 1.0:
		num_col = num_col.lerp(Palette.PAPER, clampf((number_scale - 1.0) / maxf(0.001, Motion.amplitude(&"heat_number_pop") - 1.0), 0.0, 1.0))
	var npx := roundi(look.number_px * g)
	var num_at := Vector2(look.pad.x * g, size.y - look.pad.y * g)
	draw_set_transform(num_at + Vector2(0, -npx * 0.35), 0.0, Vector2.ONE * number_scale)
	HighContrast.draw_text(self, disp, Vector2(0, npx * 0.35), "%d" % roundi(shown_heat), HORIZONTAL_ALIGNMENT_LEFT, -1, npx, num_col)
	draw_set_transform(Vector2.ZERO)
	# The band word, printed (never colour alone); it pops when the band changes. B4 (review D7:
	# "no stamp on the Heat gauge; the Heat change is the gauge's roll"): the band stamp's motion
	# is kept as the word's pop, with no stamp box round it.
	var word_r := band_label_rect()
	var bpx := roundi(look.band_px * g)
	var word_at := Vector2(word_r.position.x, word_r.position.y + disp.get_ascent(bpx))
	if stamp_scale > 1.0:
		var c := word_r.get_center()
		draw_set_transform(c, 0.0, Vector2.ONE * stamp_scale)
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
		HighContrast.draw_text(self, mono, Vector2(strip.end.x - mw, look.pad.y * g + mono.get_ascent(mpx)), max_text, HORIZONTAL_ALIGNMENT_LEFT, -1, mpx, HudSkin.TERMINAL_TEXT)
	_draw_strip(strip, g)
	if not raid_next.is_empty() and mpx > 0:
		# RAID-FIX D5: the top row carries only "(24)" after "/max"; the words hang under the bar at the tick.
		var compact := RAID_AWAY_COMPACT % int(raid_next["away"])
		var mw2 := mono.get_string_size(max_text, HORIZONTAL_ALIGNMENT_LEFT, -1, mpx).x
		var cw := mono.get_string_size(compact, HORIZONTAL_ALIGNMENT_LEFT, -1, mpx).x
		HighContrast.draw_text(self, mono, Vector2(strip.end.x - mw2 - cw - look.pad.x * g * 0.5, look.pad.y * g + mono.get_ascent(mpx)), compact, HORIZONTAL_ALIGNMENT_LEFT, -1, mpx, Palette.HARM)
		_draw_chip()
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
		HighContrast.draw_text(self, f, Vector2(x, at.y), ch, HORIZONTAL_ALIGNMENT_LEFT, -1, px, col)
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
	if not raid_next.is_empty():
		# RAID-FIX C4: the next raid's tick, taller than the band ticks, with a point under the strip.
		var rx := strip_x(float(raid_next["at"]))
		var oh := look.tick_overhang * g
		draw_line(Vector2(rx, strip.position.y - oh), Vector2(rx, strip.end.y + oh), Palette.HARM, 3.0)
	var m := look.marker_px * g
	var mx := strip_x(at)
	var top := strip.position.y - m * 0.15
	draw_colored_polygon(PackedVector2Array([Vector2(mx - m * 0.6, top - m), Vector2(mx + m * 0.6, top - m), Vector2(mx, top)]), Palette.PAPER)


## RAID-FIX D5: the countdown chip under the bar: the terminal plate, the next band's colour as its edge, its pointer on the
## raid tick, the words in the mono face at the "/max" size.
func _draw_chip() -> void:
	var c := chip_rect()
	if c.size.x <= 0.0:
		return
	var col := chip_color()
	var mono := HudSkin.mono()
	draw_rect(c, PaletteSkins.chrome(HudSkin.TERMINAL_BG))
	draw_rect(c, col, false, CHIP_EDGE_W)
	var ptr := chip_pointer()
	draw_colored_polygon(ptr, col)
	var g := grow()
	HighContrast.draw_text(self, mono, Vector2(c.position.x + CHIP_PAD.x * g, c.position.y + CHIP_PAD.y * g + mono.get_ascent(chip_px())), chip_words(), HORIZONTAL_ALIGNMENT_LEFT, -1, chip_px(), HudSkin.TERMINAL_TEXT)
