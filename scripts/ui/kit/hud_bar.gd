class_name HudBar
extends PanelContainer
## The top strip of a screen: a slim terminal band with the screen number in pink and its
## title (neon gauge cluster style, "01 / CYBERDECK HQ"), the campaign's numbers as
## ransom-note paper tags hanging off the band, and VIEW LOADOUT (the deck and spinner of
## the current operative). `label` keeps the full status as text (tooltip, screen readers
## and tests); the tags are what the player sees.

signal loadout_pressed
signal daemons_pressed

const BAND_HEIGHT := 56.0

var label: Label
var title_box: Control
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
	band.bg_color = Color(0.02, 0.04, 0.1, 0.92)
	band.border_color = Palette.NET_CYAN
	band.border_width_bottom = 2
	band.content_margin_left = 10
	band.content_margin_right = 10
	add_theme_stylebox_override("panel", band)
	material = UiTheme.crt_material()
	custom_minimum_size.y = BAND_HEIGHT
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	add_child(row)
	title_box = Control.new()
	title_box.custom_minimum_size = Vector2(250, BAND_HEIGHT)
	title_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	title_box.draw.connect(_draw_title)
	row.add_child(title_box)
	stats = HudStats.new()
	stats.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(stats)
	loadout_button = Button.new()
	loadout_button.name = "ViewLoadout"
	loadout_button.text = "VIEW LOADOUT"
	loadout_button.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	loadout_button.pressed.connect(func() -> void: loadout_pressed.emit())
	loadout_button.visible = false
	row.add_child(loadout_button)
	daemon_button = Button.new()
	daemon_button.name = "Daemons"
	daemon_button.flat = true
	daemon_button.tooltip_text = "Daemons"
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


## Names the current screen ("01", "CYBERDECK HQ"); an empty title leaves the band blank.
func set_screen(number: String, title: String) -> void:
	_number = number
	_title = title
	title_box.queue_redraw()


## The stat tags: each [name, value, suffix] ("HEAT", "12", "/100").
func set_stats(items: Array) -> void:
	stats.items = items
	stats.queue_redraw()
	label.tooltip_text = label.text


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


func _draw_title() -> void:
	var y := 24.0
	if _number != "":
		title_box.draw_string(Palette.mono(), Vector2(0, y), _number, HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Palette.CELL_PINK)
		title_box.draw_string(Palette.mono(), Vector2(0, y + 20), _title, HORIZONTAL_ALIGNMENT_LEFT, 250, 15, Palette.PAPER)
	elif _title != "":
		title_box.draw_string(Palette.mono(), Vector2(0, 29), _title, HORIZONTAL_ALIGNMENT_LEFT, 250, 16, Palette.PAPER)
