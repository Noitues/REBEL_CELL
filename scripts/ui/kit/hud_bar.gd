class_name HudBar
extends PanelContainer
## The top strip of a screen: a slim terminal band with the HEAT gauge in its first slot, the
## screen's title as a yellow title sticker (v2 page-title rule), the campaign's numbers as
## ransom-note paper tags hanging off the band, and VIEW LOADOUT (the deck and spinner of
## the current operative). `label` keeps the full status as text (tooltip, screen readers
## and tests); the tags are what the player sees.

signal loadout_pressed
signal daemons_pressed
## HQ-B (Q1 / Q2): the HEAT gauge was pressed (the screen opens the Heat terminal).
signal heat_pressed

const BAND_HEIGHT := 56.0
## The screen title slot's padding and least width (px).
const TITLE_PAD := 8.0
const TITLE_MIN_WIDTH := 24.0
## The widest the title sticker may be (px): a long title letters smaller rather than push the
## stat tags (H21: the tags get the rest of the bar).
const TITLE_MAX_WIDTH := 150.0
## Designer ruling Q1 (v2 page-title rule): the screen's title is a yellow title sticker, not
## paper lettering. Its lettering size (px at text scale 1.0) and tilt (degrees).
const TITLE_STICKER_PX := 16.0
const TITLE_STICKER_TILT := -2.0
## A long title shrinks its lettering to the cap in at most this many passes, never below TITLE_MIN_PX.
const TITLE_FIT_PASSES := 6
const TITLE_MIN_PX := 8.0
const TITLE_FIT_MARGIN := 0.97

var label: Label
## HQ-B (Q1): the one Heat indicator, the bar's first slot on every screen that shows Heat.
var heat_gauge: HeatGauge
var title_box: Control
## The yellow sticker that names the screen (null while the screen has no title).
var title_sticker: VerbSticker
var stats: HudStats
var loadout_button: Button
## One DAEMONS icon (stacked sigils + count) that opens the Daemon tray.
var daemon_button: Button
var daemon_ids: Array[StringName] = []
var _number: String = ""
var _title: String = ""


func _init() -> void:
	name = "HudBar"
	var band := StyleBoxFlat.new()
	band.bg_color = Color(0.02, 0.04, 0.1, 0.0)  # B5: the kit glass behind it is the band's fill
	band.border_color = Palette.NET_CYAN
	PaletteSkins.track_box(band)  # ART-12 12s-b: the band's rule follows the skin
	band.border_width_bottom = 2
	band.content_margin_left = 10
	band.content_margin_right = 10
	add_theme_stylebox_override("panel", band)
	# B5 (B1c follow-up 2): the kit's CRT glass (scanlines, the hex dump that fades under the counters' words), not
	# the shared crt_panel material.
	CrtTerminalPanel.behind(self)
	custom_minimum_size.y = BAND_HEIGHT
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	add_child(row)
	# HQ-B (Q1): the HEAT gauge takes the bar's first slot (hidden until a screen shows Heat).
	heat_gauge = HeatGauge.new()
	heat_gauge.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	heat_gauge.visible = false
	heat_gauge.pressed.connect(func() -> void: heat_pressed.emit())
	row.add_child(heat_gauge)
	title_box = Control.new()
	title_box.custom_minimum_size = Vector2(250, BAND_HEIGHT)
	title_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(title_box)
	stats = HudStats.new()
	stats.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(stats)
	# H24 S4: the bar shows its words as given, translated once here.
	TextDb.shown_as_given(self)
	loadout_button = Button.new()
	loadout_button.name = "ViewLoadout"
	loadout_button.text = tr("VIEW LOADOUT")
	loadout_button.tooltip_text = UiTip.fold(tr("The operative's deck and spinner (hub core and inner ring included)."))
	loadout_button.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	loadout_button.pressed.connect(func() -> void: loadout_pressed.emit())
	loadout_button.visible = false
	row.add_child(loadout_button)
	daemon_button = Button.new()
	daemon_button.name = "Daemons"
	daemon_button.flat = true
	daemon_button.tooltip_text = UiTip.fold(tr("The installed Daemons. Opens the tray: each sigil shows what its Daemon does."))
	daemon_button.custom_minimum_size = Vector2(52, 44)
	daemon_button.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	daemon_button.draw.connect(_draw_daemon_icon)
	daemon_button.pressed.connect(func() -> void: daemons_pressed.emit())
	daemon_button.mouse_entered.connect(daemon_button.queue_redraw)
	daemon_button.mouse_exited.connect(daemon_button.queue_redraw)
	daemon_button.visible = false
	row.add_child(daemon_button)
	label = Label.new()
	label.visible = false
	row.add_child(label)
	MotionSkip.register_passive(self)  # ANIM-R6 D7: a landing pop ends with any press that ends a motion


## MotionSkip (ANIM-R6 D7): DAEMONS or VIEW LOADOUT pops for a landing.
func motion_running() -> bool:
	for b in [daemon_button, loadout_button]:
		if b != null and Motion.held(b, ^"scale"):
			return true
	return false


## MotionSkip (ANIM-R6 D7): the pops at rest.
func complete_motion() -> void:
	for b in [daemon_button, loadout_button]:
		Motion.settle(b, ^"scale")


## Names the current screen ("01", "CYBERDECK HQ"; the title translated by the caller); an
## empty title leaves the band blank. The title takes only the width it needs (H21: the
## stat tags get the rest).
func set_screen(number: String, title: String) -> void:
	_number = number
	_title = title
	if title_sticker != null:
		title_box.remove_child(title_sticker)
		title_sticker.free()
		title_sticker = null
	var w := TITLE_MIN_WIDTH
	if title != "":
		var px := TITLE_STICKER_PX
		title_sticker = _sticker(title, px)
		for _i in TITLE_FIT_PASSES:
			var wide := title_sticker.get_combined_minimum_size().x
			if wide <= TITLE_MAX_WIDTH or px <= TITLE_MIN_PX:
				break
			# the sticker's width is its lettering plus a fixed rim: shrink the lettering, measure again
			px = maxf(px * (TITLE_MAX_WIDTH / wide) * TITLE_FIT_MARGIN, TITLE_MIN_PX)
			title_sticker.free()
			title_sticker = _sticker(title, px)
		title_box.add_child(title_sticker)
		var m := title_sticker.get_combined_minimum_size()
		title_sticker.position = Vector2(0.0, maxf((BAND_HEIGHT - m.y) * 0.5, 0.0))
		w = maxf(ceilf(m.x) + TITLE_PAD, TITLE_MIN_WIDTH)
	title_box.custom_minimum_size.x = w
	# HQ-B (Q1, Q6): a screen with no title (the HQ) gives the slot to the HEAT gauge.
	title_box.visible = title != "" or not heat_gauge.visible


func _sticker(title: String, px: float) -> VerbSticker:
	var st := VerbSticker.new(title, VerbSticker.Fill.YELLOW, px, TITLE_STICKER_TILT)
	st.pre_translated = true
	st.name = "TitleSticker"
	st.focus_mode = Control.FOCUS_NONE
	st.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return st


## HQ-B (Q1 / Q2): shows the HEAT gauge in the bar's first slot: `value` of `maximum`, the
## band levels `marks` (HeatRules.band_levels), and whether it opens the Heat terminal
## (`interactive`: the caret; read-only in a run is the screen's call).
func set_heat(value: int, maximum: int, marks: Array[int], interactive: bool, tip: String = "") -> void:
	heat_gauge.visible = true
	heat_gauge.interactive = interactive
	heat_gauge.tooltip_text = tip
	heat_gauge.set_heat(value, maximum, marks)
	title_box.visible = _title != ""


## HQ-B: hides the HEAT gauge (a screen without a campaign).
func hide_heat() -> void:
	heat_gauge.visible = false
	title_box.visible = true


## The stat tags: each [name, value, suffix] ("HEAT", "12", "/100"), and the small
## captions over their groups (H24 S16: [[first tag index, words, tooltip], ...], the words
## translated by the caller: "CAMPAIGN", "THIS RUN").
func set_stats(items: Array, captions: Array = []) -> void:
	stats.captions = captions
	stats.items = items
	stats.queue_redraw()
	label.tooltip_text = label.text


## ANIM-R5 B5 / ANIM-R6 B7: a bought or picked item of `kind` ("card", "daemon", else a chip
## or slice) has landed on the bar: where it went pulses (`flight_land_pulse`): the CARDS tag
## for a card, the DAEMONS icon for a Daemon, VIEW LOADOUT for the rest (a pop). Returns the
## control that pulses (null when none shows).
func land_pulse(kind: String) -> Control:
	match kind:
		"card":
			# B5 (review section f): a page whose bar does not show CARDS (the Mainframe) lands the card on VIEW
			# LOADOUT, where the deck is (below).
			if stats.land_pulse(StatIcon.CARDS):
				return stats
		"daemon":
			if daemon_button.is_visible_in_tree():
				Motion.pop(daemon_button, HudStats.LAND_PULSE)
				return daemon_button
			return null
	if loadout_button.is_visible_in_tree():
		Motion.pop(loadout_button, HudStats.LAND_PULSE)
		return loadout_button
	return null


## The Daemons installed on the current operative (the icon shows the first and a count).
func set_daemons(ids: Array[StringName]) -> void:
	daemon_ids = ids
	daemon_button.visible = true
	daemon_button.queue_redraw()


func _draw_daemon_icon() -> void:
	var c := daemon_button.size * 0.5 + Vector2(-4, 0)
	var hot := daemon_button.is_hovered() or daemon_button.has_focus()
	if daemon_ids.size() > 1:
		DaemonSigil.draw_sigil(daemon_button, c + Vector2(6, -3), 14, daemon_ids[1])
	if daemon_ids.is_empty():
		daemon_button.draw_arc(c, 15, 0, TAU, 24, Color(Palette.NEON_VIOLET, 0.6), 1.5)
		daemon_button.draw_string(Palette.mono(), c + Vector2(-12, 5), "D", HORIZONTAL_ALIGNMENT_CENTER, 24, 14, Color(Palette.NEON_VIOLET, 0.8))
	else:
		DaemonSigil.draw_sigil(daemon_button, c, 16, daemon_ids[0])
	var badge := c + Vector2(17, 12)
	daemon_button.draw_circle(badge, 9, Palette.CELL_ACID if hot else Palette.NEON_VIOLET)
	daemon_button.draw_string(Palette.display(), badge + Vector2(-9, 5), str(daemon_ids.size()), HORIZONTAL_ALIGNMENT_CENTER, 18, 13, Palette.INK)
