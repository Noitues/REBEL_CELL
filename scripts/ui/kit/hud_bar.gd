class_name HudBar
extends PanelContainer
## The top strip of a screen: a slim terminal band with the screen number in pink and its
## title (neon gauge cluster style, "01 / CYBERDECK HQ"), the campaign's numbers as
## ransom-note paper tags hanging off the band, and VIEW LOADOUT (the deck and spinner of
## the current operative). `label` keeps the full status as text (tooltip, screen readers
## and tests); the tags are what the player sees.
##
## Art pass W8b (ART_BIBLE §5.2, §6.9): the band is one row at a height set by the text
## scale alone and never wraps. Every size is a §4.2 step x the text scale: the number at
## `label`, the title at `body` stepping down to `caption`; a title still wider than its
## room folds (the number stays, the title goes to the band's tooltip; with no number it
## wraps to two lines at `caption`). From HudStats.FOLD_SCALE up VIEW LOADOUT shows its
## icon only (its words in the tooltip), as the Grid's step buttons do. `watch_drops`
## puts FOCUS brackets on the tags and the DAEMONS icon that take the item being carried.

signal loadout_pressed
signal daemons_pressed

## The band's least height at text scale 1.0 (a fight keeps the tags to it: netrun_scene).
const BAND_HEIGHT := 56.0
## The title's room at text scale 1.0, and the most that room grows with the text (px).
const TITLE_PAD := 8.0
const TITLE_MIN_WIDTH := 24.0
const TITLE_MAX_WIDTH := 250.0
const TITLE_GROW_MAX := 1.3
## The title's type steps, largest first (it steps down to fit its room).
const TITLE_STEPS: Array[int] = [UiTheme.BODY, UiTheme.CAPTION]
## The number's type step and the lines a folded, number-less title may take.
const NUMBER_STEP := UiTheme.LABEL
const TITLE_LINES_MAX := 2
## Band padding and the gap between its parts (px at scale 1.0).
const BAND_PAD := 10
const ROW_GAP := UiTheme.SP_S + UiTheme.SP_XS
const BORDER := 2
## The DAEMONS icon: its button's size at scale 1.0, the sigil radius, the second sigil's
## offset and radius, the count badge's radius and offset (px at scale 1.0).
const DAEMON_SIZE := Vector2(52, 44)
const SIGIL_R := 16.0
const SIGIL_BACK_R := 14.0
const SIGIL_BACK_AT := Vector2(6, -3)
const SIGIL_NUDGE := Vector2(-4, 0)
const BADGE_R := 9.0
const BADGE_AT := Vector2(17, 12)
const EMPTY_RING_R := 15.0
const EMPTY_ALPHA := 0.7

var label: Label
var title_box: Control
var stats: HudStats
var loadout_button: Button
## One DAEMONS icon (stacked sigils + count) that opens the Daemon tray.
var daemon_button: Button
var daemon_ids: Array[StringName] = []
var _number: String = ""
var _title: String = ""
## The title as laid out: its lines and their size (px), and the number's size.
var _title_lines: PackedStringArray = PackedStringArray()
var _title_px: int = UiTheme.BODY
var _number_px: int = NUMBER_STEP
## True while the daemon icon takes the carried item (brackets on it).
var _daemons_hot: bool = false
## The drop layer watched for carries (see watch_drops).
var _watched: DropLayer = null
var _row: HBoxContainer


func _init() -> void:
	name = "HudBar"
	var band := StyleBoxFlat.new()
	band.bg_color = Palette.TERMINAL_BG
	band.border_color = Palette.NET_CYAN
	band.border_width_bottom = BORDER
	band.content_margin_left = BAND_PAD
	band.content_margin_right = BAND_PAD
	add_theme_stylebox_override("panel", band)
	material = UiTheme.crt_material()
	custom_minimum_size.y = BAND_HEIGHT
	_row = HBoxContainer.new()
	add_child(_row)
	title_box = Control.new()
	title_box.name = "TitleBox"
	title_box.mouse_filter = Control.MOUSE_FILTER_PASS
	title_box.draw.connect(_draw_title)
	_row.add_child(title_box)
	stats = HudStats.new()
	stats.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_row.add_child(stats)
	# H24 S4: the bar shows its words as given, translated once here.
	TextDb.shown_as_given(self)
	loadout_button = Button.new()
	loadout_button.name = "ViewLoadout"
	loadout_button.text = tr("VIEW LOADOUT")
	loadout_button.set_meta(&"full_text", loadout_button.text)
	loadout_button.tooltip_text = UiTip.fold(tr("The operative's deck and spinner (hub core and inner ring included)."))
	loadout_button.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	loadout_button.pressed.connect(func() -> void: loadout_pressed.emit())
	loadout_button.visible = false
	IconMark.attach(loadout_button, StatIcon.CARDS)
	_row.add_child(loadout_button)
	daemon_button = Button.new()
	daemon_button.name = "Daemons"
	daemon_button.flat = true
	daemon_button.tooltip_text = UiTip.fold(tr("The installed Daemons. Opens the tray: each sigil shows what its Daemon does."))
	daemon_button.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	daemon_button.draw.connect(_draw_daemon_icon)
	daemon_button.pressed.connect(func() -> void: daemons_pressed.emit())
	daemon_button.mouse_entered.connect(daemon_button.queue_redraw)
	daemon_button.mouse_exited.connect(daemon_button.queue_redraw)
	daemon_button.visible = false
	_row.add_child(daemon_button)
	label = Label.new()
	label.visible = false
	_row.add_child(label)
	_fit()


func _ready() -> void:
	Settings.changed.connect(_fit)


## Sizes follow the text scale (§4.3.1): the gaps, the DAEMONS icon, VIEW LOADOUT's words
## (folded to its icon at big text) and the title.
func _fit() -> void:
	var s := Settings.text_scale
	_row.add_theme_constant_override("separation", roundi(ROW_GAP * s))
	daemon_button.custom_minimum_size = DAEMON_SIZE * s
	var full := String(loadout_button.get_meta(&"full_text", loadout_button.text))
	loadout_button.text = "" if s >= HudStats.FOLD_SCALE - 0.001 else full
	_layout_title()
	daemon_button.queue_redraw()


## Names the current screen ("01", "CYBERDECK HQ"; the title translated by the caller); an
## empty title leaves the band blank. The title takes only the width it needs (H21: the
## stat tags get the rest).
func set_screen(number: String, title: String) -> void:
	_number = number
	_title = title
	_layout_title()


## §5.2: the title's lines and sizes for the room it may take; a title that doesn't fit
## folds (see the class notes). Its full words are the band's tooltip then.
func _layout_title() -> void:
	var s := Settings.text_scale
	var mono := Palette.mono()
	var cap := TITLE_MAX_WIDTH * minf(s, TITLE_GROW_MAX)
	_number_px = UiTheme.font_px_at(NUMBER_STEP, s)
	_title_lines = PackedStringArray()
	_title_px = UiTheme.font_px_at(TITLE_STEPS[TITLE_STEPS.size() - 1], s)
	var width := mono.get_string_size(_number, HORIZONTAL_ALIGNMENT_LEFT, -1, _number_px).x if _number != "" else 0.0
	var folded := false
	if _title != "":
		var placed := false
		for step in TITLE_STEPS:
			var px := UiTheme.font_px_at(step, s)
			var w := mono.get_string_size(_title, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
			if w <= cap:
				_title_px = px
				_title_lines = PackedStringArray([_title])
				width = maxf(width, w)
				placed = true
				break
		if not placed:
			folded = true
			if _number == "":
				# No number to stand for it: the words on two lines at the least step.
				_title_lines = _wrap_title(_title, cap, mono, _title_px)
				for line in _title_lines:
					width = maxf(width, mono.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, _title_px).x)
	title_box.custom_minimum_size.x = clampf(ceilf(width) + TITLE_PAD * s, TITLE_MIN_WIDTH, cap + TITLE_PAD * s) if (_number != "" or _title != "") else TITLE_MIN_WIDTH
	title_box.tooltip_text = UiTip.fold(_title) if folded or (_number != "" and _title != "") else ""
	title_box.queue_redraw()


## `text` in at most TITLE_LINES_MAX lines no wider than `room` at `px`, broken at spaces
## (the last line takes the rest; §4.3.3: never mid-word).
static func _wrap_title(text: String, room: float, font: Font, px: int) -> PackedStringArray:
	var out := PackedStringArray()
	var cur := ""
	for word in text.split(" ", false):
		var trial := word if cur == "" else cur + " " + word
		if cur != "" and font.get_string_size(trial, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x > room and out.size() < TITLE_LINES_MAX - 1:
			out.append(cur)
			cur = word
		else:
			cur = trial
	if cur != "":
		out.append(cur)
	return out


## The title's lines as drawn now (tests).
func title_lines() -> PackedStringArray:
	return _title_lines.duplicate()


## The stat tags: each [name, value, suffix] ("HEAT", "12", "/100"), and the small
## captions over their groups (H24 S16: [[first tag index, words, tooltip], ...], the words
## translated by the caller: "CAMPAIGN", "THIS RUN").
func set_stats(items: Array, captions: Array = []) -> void:
	stats.captions = captions
	stats.items = items
	stats.queue_redraw()
	label.tooltip_text = label.text


## The Daemons installed on the current operative (the icon shows the first and a count).
func set_daemons(ids: Array[StringName]) -> void:
	daemon_ids = ids
	daemon_button.visible = true
	daemon_button.queue_redraw()


## §6.9: the tags (CARDS) and the DAEMONS icon show FOCUS brackets while `layer` carries an
## item they take: a target of the layer's is matched to a tag or the icon by where it
## sits. The screen calls it once per drop layer (netrun_scene: its `drops`).
func watch_drops(layer: DropLayer) -> void:
	if _watched != null and is_instance_valid(_watched) and _watched.carry_changed.is_connected(_on_carry):
		_watched.carry_changed.disconnect(_on_carry)
	_watched = layer
	if layer != null:
		layer.carry_changed.connect(_on_carry)


func _on_carry(carrying: bool) -> void:
	var hot: Array[StringName] = []
	_daemons_hot = false
	if carrying and _watched != null and is_instance_valid(_watched):
		var rects := stats.tag_rects()
		var xf := stats.get_global_transform()
		for t in _watched.targets:
			if not _watched.offered(String(t["id"])):
				continue
			var r := _watched.locate(t)
			if not r.has_area():
				continue
			for i in mini(stats.items.size(), rects.size()):
				var g := Rect2(xf * rects[i].position, rects[i].size * xf.get_scale())
				if g.intersects(r) and not hot.has(stats.icon_of(i)):
					hot.append(stats.icon_of(i))
			if daemon_button.is_visible_in_tree() and daemon_button.get_global_rect().intersects(r):
				_daemons_hot = true
	stats.hot_kinds = hot
	daemon_button.queue_redraw()


## True while the DAEMONS icon shows its drop brackets (tests).
func daemons_hot() -> bool:
	return _daemons_hot


func _draw_daemon_icon() -> void:
	var s := Settings.text_scale
	var c := daemon_button.size * 0.5 + SIGIL_NUDGE * s
	var hot := daemon_button.is_hovered() or daemon_button.has_focus()
	if daemon_ids.size() > 1:
		DaemonSigil.draw_sigil(daemon_button, c + SIGIL_BACK_AT * s, SIGIL_BACK_R * s, daemon_ids[1])
	if daemon_ids.is_empty():
		var fs := UiTheme.font_px_at(UiTheme.CAPTION, s)
		daemon_button.draw_arc(c, EMPTY_RING_R * s, 0, TAU, 24, Color(Palette.NEON_VIOLET, EMPTY_ALPHA), maxf(1.0, s))
		daemon_button.draw_string(Palette.mono(), c + Vector2(-EMPTY_RING_R * s, fs * HudStats.DIGIT_HALF), "D", HORIZONTAL_ALIGNMENT_CENTER, EMPTY_RING_R * 2.0 * s, fs, Palette.NEON_VIOLET)
	else:
		DaemonSigil.draw_sigil(daemon_button, c, SIGIL_R * s, daemon_ids[0])
	var badge := c + BADGE_AT * s
	daemon_button.draw_circle(badge, BADGE_R * s, Palette.FOCUS if hot else Palette.NEON_VIOLET)
	var bfs := UiTheme.font_px_at(UiTheme.CAPTION, s)
	daemon_button.draw_string(Palette.display(), badge + Vector2(-BADGE_R * s, bfs * HudStats.DIGIT_HALF), str(daemon_ids.size()), HORIZONTAL_ALIGNMENT_CENTER, BADGE_R * 2.0 * s, bfs, Palette.INK)
	if _daemons_hot:
		StyleBoxBrackets.draw_on(daemon_button, Rect2(Vector2.ZERO, daemon_button.size), Palette.FOCUS)


func _draw_title() -> void:
	var mono := Palette.mono()
	var y := 0.0
	var lines: Array = []
	if _number != "":
		lines.append([_number, _number_px, Palette.CELL_PINK])
	for line in _title_lines:
		lines.append([line, _title_px, Palette.PAPER])
	var total := 0.0
	for l in lines:
		total += mono.get_height(int(l[1]))
	y = maxf(0.0, (title_box.size.y - total) * 0.5)
	for l in lines:
		var px := int(l[1])
		title_box.draw_string(mono, Vector2(0, y + mono.get_ascent(px)), String(l[0]), HORIZONTAL_ALIGNMENT_LEFT, title_box.size.x, px, l[2])
		y += mono.get_height(px)
