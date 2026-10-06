class_name MapLegend
extends TerminalWindow
## The map key for the city map views (Settings.map_legend): what the highlight colours,
## marks, line styles and badge glyphs mean. Every status row has its own glyph, so the
## key never relies on colour alone (GDD 9.6): claimed Sites carry a spray ring, TAKEN
## ones a cross. Follows the setting live, and can resize a linked control with it (the
## HQ Grid's Site list takes the legend's room back when it is off).
##
## H22: every row's text, glyph and icon follow Settings.text_scale (rebuilt live when it
## changes); rows are plain Labels so the legend reports its full minimum size at once
## (a legend pinned over a map grows upward from its corner and never runs off it); the
## tier row shows the map's difficulty pips.
##
## H23 #3: a strip variant (`pin_to(area, corp, true)`, the Grid) runs along the foot of
## a map in as many columns as `set_strip_width` allows, in fewer words (STRIP_ROWS).
##
## H24 K1: at big text (FOLD_SCALE and up) the strip folds to one line, its MAP KEY
## button: hovering it, pressing it, or the pad's key button (hq_scene) opens the rows
## over the map, and they fold again when the pointer leaves or on a second press. The
## map is framed for the folded line (`fit_size`), so it keeps its room. K7: every row's
## words go through the TranslationServer once (the Labels do not translate them again).
## K5: each icon row names its icon (`icon_id` meta, CityMapOverlay.icon_id).

## H24 K1: the key was folded or opened.
signal fold_changed
## ART-5 5d: the key's SHOW ALL was pointed at (true) or left (false); an opened key shows
## all too (the pad's key button). The Grid reveals its hidden Sites while it holds.
signal show_all_changed(on: bool)

## ART-5 5d: the Grid's key as the v4 Site markers (`use_site_markers`): each row draws the
## map's own marker (SiteMarkerView) and names it in a word or two; pointing at a row tells
## what it means in the game, in plain words (SiteMarker.MEANINGS). [key, strip words].
const MARKER_ROWS := [["next", "next"], ["notyet", "not yet"], ["cleared", "cleared"], ["yours", "yours"], ["core", "CORE"], # TR
	["down", "DOWN"], ["taken", "TAKEN"], ["exploit", "exploit"], ["heat", "heat obj."], ["target", "TARGET"]] # TR
## The line rows of the v4 key: [key, strip words].
const MARKER_LINE_ROWS := [["locked", "locked link"], ["depowered", "no power"], ["threat", "threat route"]] # TR
## The cell that reveals the hidden Sites while pointed at.
## Its words by device (UiTip.for_input picks the pad's when pad_active).
const SHOW_ALL := "HOVER: SHOW ALL" # TR
const SHOW_ALL_PAD := "OPEN KEY: SHOW ALL" # TR
const SHOW_ALL_TIP := "Point here to show every Site; unselectable regular Sites are hidden to keep the map clear." # TR
const SHOW_ALL_TIP_PAD := "Open the key to show every Site; unselectable regular Sites are hidden to keep the map clear." # TR
## A marker swatch's scale (of the map's marker) and its cell (x the icon swatch), at text
## scale 1.0.
const MARKER_SWATCH_SCALE := 0.55
## The rows the strip (the Grid's foot) keeps (v4 key strip): the rest are in the full key.
const STRIP_MARKER_KEYS: Array[String] = ["next", "cleared", "yours", "down", "taken", "exploit", "heat"]
const MARKER_SWATCH_CELL := 1.3

const ROWS := [["○", "#D4FF00", "claimed (yours): spray ring"], ["◇", "#5CE1FF", "cleared"], ["■", "", "corporate"], ["✕", "#FFD24D", "taken: crossed out"],
	["━", "#D4FF00", "your network link"], ["- -", "", "threat route"]]
## The node icons (H21 #14), drawn by CityMapOverlay.draw_icon exactly as on the map:
## [kind, text shown in the icon, meaning].
const ICON_ROWS := [[CityMapOverlay.KIND_EXPLOIT, "", "exploit"], [CityMapOverlay.KIND_HEAT, "", "heat reduction"],
	[CityMapOverlay.KIND_CENTRAL_SERVER, "", "central server"], [CityMapOverlay.KIND_HOME, "", "CORE (your home)"], [CityMapOverlay.KIND_TIER, "T2", "Site tier: more lit pips, harder"]]
## The tier row's example tier (its icon text above is "T2").
const TIER_EXAMPLE := 2
## Legend width, glyph column width, the full and compact variants' font sizes (legends
## pinned over a map are compact), and the title's; all at text scale 1.0. The full
## variant sits in a screen's column: it keeps WIDTH and its text wraps (at least
## MIN_TEXT_WIDTH per line); the compact one grows with the text scale unwrapped.
const WIDTH := 230.0
const MIN_TEXT_WIDTH := 110.0
const GLYPH_WIDTH := 22.0
const FULL_FONT := 15
const COMPACT_FONT := 12
const TITLE_FONT := 15
## Icon swatch side (px) at text scale 1.0, and the icon's radius as a share of it.
const ICON_SWATCH := 22.0
const ICON_SHARE := 0.36
const ICON_SWATCH_GAP := 8
## Margin (px) of a legend pinned to a map area's bottom-left corner.
const PIN_MARGIN := 10.0
## H23 #3: the strip variant (the Grid's key along the foot of its map) says each row in
## fewer words, in as many columns as its width holds; gaps between them (px at text
## scale 1.0).
const STRIP_ROWS := ["claimed: spray ring", "cleared", "corporate", "taken: crossed out", "your network link", "threat route"]
const STRIP_ICON_ROWS := ["exploit", "heat reduction", "central server", "CORE (your home)", "tier: more pips, harder"]
const STRIP_H_GAP := 16
const STRIP_V_GAP := 2

## H24 K1: the strip folds to its MAP KEY line from this text scale up (at 1.3 the open
## strip took about a third of the map's height, at 1.6 over 40 %).
const FOLD_SCALE := 1.3

## H23 S4: each ROWS row's key (the ICON_ROWS rows are keyed by their kind).
const ROW_KEYS: Array[String] = ["claimed", "cleared", "corporate", "taken", "link", "threat"]

var compact: bool = false
## H23 S4: the rows shown, by key (ROW_KEYS, icon kinds); empty = every row. A map key
## lists what its map shows (the raid legend took a quarter of the screen).
var only: Array[String] = []
## H23 #3: rows laid out in columns across `strip_width` (see `strip`).
var strip: bool = false
var strip_width: float = 0.0
var _grid: GridContainer = null
## H24 K1: the strip's rows are shown (a folded key opened) and whether the pointer
## opened it (it folds again when the pointer leaves); the MAP KEY button of a foldable
## strip.
var opened: bool = false
var _hover_opened: bool = false
var fold_button: Button = null
var _corp_hex: String = ""
var _corp_id: StringName = &""
## ART-5 5d: rows are the v4 Site markers (the Grid's key).
var site_markers: bool = false
var marker_threat: bool = false
var show_all_cell: Label = null
var _built_scale: float = -1.0
var _linked: Control = null
var _size_on: Vector2 = Vector2.ZERO
var _size_off: Vector2 = Vector2.ZERO
## ANIM-5: the folding key's rows slide in (1 = in place) by `legend_fold`'s amplitude px
## and fade with it; their resting y from the last container sort.
const FOLD_MOTION := &"legend_fold"
var fold_slide: float = 1.0:
	set(v):
		fold_slide = v
		_apply_slide()
var _rows_rest_y: float = 0.0


func _init(corporation_id: StringName = &"", p_compact: bool = false, p_strip: bool = false) -> void:
	super("MAP LEGEND")
	name = "MapLegend"
	strip = p_strip
	compact = p_compact or p_strip
	_corp_hex = Palette.corp_color(corporation_id).to_html(false)
	_corp_id = corporation_id
	_build()
	visible = Settings.map_legend
	Settings.changed.connect(_on_settings_changed)
	body.sort_children.connect(_on_body_sorted)


## The rows' font size now (px): the variant's size at the current text scale.
func font_size() -> int:
	return roundi((COMPACT_FONT if compact else FULL_FONT) * Settings.text_scale)


## (Re)builds every row at the current text scale.
func _build() -> void:
	_built_scale = Settings.text_scale
	var s := Settings.text_scale
	custom_minimum_size.x = WIDTH * s if compact else WIDTH
	var head := find_child("TerminalTitle", true, false) as Label
	if head != null:
		head.add_theme_font_size_override("font_size", roundi(TITLE_FONT * s))
	for child in body.get_children():
		body.remove_child(child)
		child.free()
	var fs := font_size()
	var into: Container = body
	_grid = null
	if strip:
		custom_minimum_size.x = 0.0
		_grid = GridContainer.new()
		_grid.name = "Rows"
		_grid.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_grid.add_theme_constant_override("h_separation", roundi(STRIP_H_GAP * s))
		_grid.add_theme_constant_override("v_separation", roundi(STRIP_V_GAP * s))
		body.add_child(_grid)
		into = _grid
		# The title takes the grid's first cell (the strip's rows fill whole lines, so it
		# costs no height), not a bar of its own over the rows.
		if head != null:
			var bar := head.get_parent() as Control
			bar.visible = false
			var outer := bar.get_parent()
			if outer.get_child_count() > 1 and outer.get_child(1) is ColorRect:
				(outer.get_child(1) as ColorRect).visible = false
			fold_button = null
			if foldable():
				# H24 K1: folded, the key is this one line; it opens over the map.
				fold_button = Button.new()
				fold_button.name = "KeyToggle"
				fold_button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
				fold_button.text = CityMapOverlay.tr_word("MAP KEY")
				fold_button.alignment = HORIZONTAL_ALIGNMENT_LEFT
				fold_button.add_theme_font_size_override("font_size", fs)
				fold_button.tooltip_text = UiTip.fold(CityMapOverlay.tr_word("The map key: what the icons, colours and lines mean. Point at it or press it to open it; the pad's key button too."))
				fold_button.pressed.connect(func() -> void: set_opened(not opened))
				fold_button.mouse_entered.connect(_on_hover_open)
				IconMark.attach(fold_button, StatIcon.MORE if not opened else StatIcon.CODEX)
				body.add_child(fold_button)
				body.move_child(fold_button, 0)
				_grid.visible = opened
			else:
				var cell := Label.new()
				cell.name = "StripTitle"
				cell.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
				cell.text = CityMapOverlay.tr_word(head.text)
				cell.mouse_filter = Control.MOUSE_FILTER_IGNORE
				cell.add_theme_color_override("font_color", head.get_theme_color("font_color"))
				cell.add_theme_font_size_override("font_size", fs)
				cell.size_flags_vertical = Control.SIZE_SHRINK_CENTER
				_grid.add_child(cell)
	if site_markers:
		_build_marker_rows(into, fs)
		if strip:
			_fit_columns()
		update_minimum_size()
		return
	for i in ROWS.size():
		var r: Array = ROWS[i]
		if not only.is_empty() and not only.has(ROW_KEYS[i]):
			continue
		var row := HBoxContainer.new()
		row.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_theme_constant_override("separation", roundi(ICON_SWATCH_GAP * s))
		var glyph := Label.new()
		glyph.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED  # a mark, not a word
		glyph.text = r[0]
		glyph.custom_minimum_size.x = GLYPH_WIDTH * s
		glyph.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		glyph.add_theme_color_override("font_color", Color.html(r[1] if r[1] != "" else _corp_hex))
		glyph.add_theme_font_size_override("font_size", fs)
		glyph.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(glyph)
		row.add_child(_text(STRIP_ROWS[i] if strip else r[2], fs))
		into.add_child(row)
	for i in ICON_ROWS.size():
		var r: Array = ICON_ROWS[i]
		if not only.is_empty() and not only.has(String(r[0])):
			continue
		into.add_child(_icon_row(r[0], r[1], STRIP_ICON_ROWS[i] if strip else r[2], fs))
	if strip:
		_fit_columns()
	update_minimum_size()


## H24 K1: true when this key folds to its MAP KEY line (a strip at big text).
func foldable() -> bool:
	return strip and (always_fold or Settings.text_scale >= FOLD_SCALE - 0.001)


## HQ-B (round 37 "the key is a one-line strip"): the strip folds to its MAP KEY line at every
## text size (the HQ's map has no room for the open rows; they open over it).
var always_fold: bool = false:
	set(v):
		if v != always_fold:
			always_fold = v
			_build()


## H24 K1: true when the rows are hidden behind the MAP KEY line.
func is_folded() -> bool:
	return foldable() and not opened


## H24 K1: opens (or folds) a foldable key's rows over the map.
func set_opened(value: bool, by_hover: bool = false) -> void:
	_hover_opened = value and by_hover
	mouse_filter = Control.MOUSE_FILTER_PASS if _hover_opened else Control.MOUSE_FILTER_IGNORE
	if value == opened:
		return
	opened = value
	if _grid != null:
		var show := opened or not foldable()
		if show:
			_grid.visible = true
			_slide_rows(true)
		elif _grid.visible and Motion.live(FOLD_MOTION) and is_inside_tree():
			_slide_rows(false)  # the rows hide when they have slid out
		else:
			_grid.visible = false
	if fold_button != null:
		IconMark.attach(fold_button, StatIcon.MORE if not opened else StatIcon.CODEX)
	_fit_columns()
	update_minimum_size()
	fold_changed.emit()
	if site_markers:
		show_all_changed.emit(opened)  # ART-5 5d: the opened key (pad, pointer) shows every Site


func _on_hover_open() -> void:
	if not opened:
		set_opened(true, true)


func _notification(what: int) -> void:
	# Opened by the pointer: folds again once the pointer leaves the key (and its rows).
	if what == NOTIFICATION_MOUSE_EXIT and _hover_opened:
		set_opened(false)


## H24 K1: the size the map is framed around: the folded MAP KEY line for a foldable key
## (open, its rows sit over the map for a moment), else the whole key.
func fit_size() -> Vector2:
	if not foldable() or _grid == null or not _grid.visible:
		return get_combined_minimum_size()
	_grid.visible = false
	var folded := get_combined_minimum_size()
	_grid.visible = true
	return folded


## ANIM-5: the rows slide in (opening) or out (folding; hidden at the end). The end state
## at once when motion doesn't play.
func _slide_rows(opening: bool) -> void:
	if not Motion.live(FOLD_MOTION) or not is_inside_tree():
		fold_slide = 1.0
		return
	if opening:
		fold_slide = 0.0
		Motion.run(FOLD_MOTION, self, ^"fold_slide", 1.0)
		return
	var tw := Motion.run(FOLD_MOTION, self, ^"fold_slide", 0.0)
	if tw == null:
		_rows_folded()
	else:
		tw.finished.connect(_rows_folded)


## The fold's slide ended: the rows hide and the key takes its one-line size.
func _rows_folded() -> void:
	if _grid != null and not opened and foldable():
		_grid.visible = false
		fold_slide = 1.0
		_fit_columns()
		update_minimum_size()


func _on_body_sorted() -> void:
	if _grid != null and is_instance_valid(_grid):
		_rows_rest_y = _grid.position.y
		_apply_slide()


func _apply_slide() -> void:
	if _grid == null or not is_instance_valid(_grid):
		return
	_grid.position.y = _rows_rest_y + (1.0 - fold_slide) * Motion.amplitude(FOLD_MOTION)
	_grid.modulate.a = fold_slide


## H23 #3: a strip legend lays its rows out in as many columns as `width` (px) holds.
func set_strip_width(width: float) -> void:
	strip_width = width
	_fit_columns()


## The strip's column count: as many of its widest row as fit across `strip_width` (all
## in one column when it has no width yet).
func _fit_columns() -> void:
	if _grid == null or not _grid.visible:
		return
	var widest := 0.0
	for row in _grid.get_children():
		widest = maxf(widest, (row as Control).get_combined_minimum_size().x)
	var chrome := get_combined_minimum_size().x - _grid.get_combined_minimum_size().x
	var gap := float(_grid.get_theme_constant("h_separation"))
	var room := strip_width - chrome
	var cols := 1
	if widest > 0.0 and room > widest:
		cols = floori((room + gap) / (widest + gap))
	_grid.columns = clampi(cols, 1, _grid.get_child_count())
	update_minimum_size()


func _text(text: String, fs: int) -> Label:
	var l := Label.new()
	l.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED  # H24 K7: translated here, once
	l.text = CityMapOverlay.tr_word(text)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_font_size_override("font_size", fs)
	if not compact:
		UiWrap.whole_words(l)  # ART-0 F (art pass W9F §4.3.3): whole words, never mid-word
		l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		l.custom_minimum_size.x = MIN_TEXT_WIDTH
	return l


## A key row with the map's own icon of `kind` (named "Icon_<kind>"); the tier row adds
## the map's difficulty pips under its icon.
func _icon_row(kind: String, text: String, meaning: String, fs: int) -> HBoxContainer:
	var s := Settings.text_scale
	var row := HBoxContainer.new()
	row.name = "Icon_%s" % kind
	row.set_meta(&"icon_id", CityMapOverlay.icon_id(kind))
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override("separation", roundi(ICON_SWATCH_GAP * s))
	var side := ICON_SWATCH * s
	var tier := kind == CityMapOverlay.KIND_TIER
	var pips := CityMapOverlay.tier_pips_size(s)
	var swatch := Control.new()
	swatch.name = "Swatch"
	swatch.custom_minimum_size = Vector2(maxf(side, pips.x), side + (pips.y + CityMapOverlay.TIER_PIP_GAP * s if tier else 0.0))
	swatch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	swatch.draw.connect(func() -> void:
		var c := Vector2(swatch.size.x * 0.5, side * 0.5)
		var r := side * ICON_SHARE
		CityMapOverlay.draw_icon(swatch, kind, c, r, Palette.PAPER, text)
		if tier:
			CityMapOverlay.draw_tier(swatch, Vector2(c.x, side + CityMapOverlay.TIER_PIP_GAP * s + pips.y * 0.5), TIER_EXAMPLE, Palette.PAPER, s))
	row.add_child(swatch)
	var l := _text(meaning, fs)
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(l)
	return row


## ART-5 5d: this key shows the v4 Site markers (the Grid's key), in plain words.
## `with_threat`: a raid is coming (the strip names its dashed route too).
func use_site_markers(with_threat: bool = false) -> MapLegend:
	site_markers = true
	marker_threat = with_threat
	_build()
	return self


## The marker a v4 key row `key` draws (SiteMarker spec, this key's corporation).
func marker_spec(key: String) -> Dictionary:
	var s := {"kind": SiteMarker.KIND_SITE, "status": SiteMarker.ST_CORPORATE, "avail": SiteMarker.AV_NEXT, "tier": 1,
		"exploit": int(RC.ExploitType.NONE), "corp": _corp_id, "pinned": true, "won": false}
	match key:
		"notyet":
			s["avail"] = SiteMarker.AV_NOT_YET
		"cleared":
			s["status"] = SiteMarker.ST_CLEARED
			s["avail"] = SiteMarker.AV_YOURS
		"yours":
			s["status"] = SiteMarker.ST_CLAIMED
			s["avail"] = SiteMarker.AV_YOURS
			s["tier"] = 0
		"core":
			s["kind"] = SiteMarker.KIND_CORE
			s["status"] = SiteMarker.ST_CLAIMED
			s["avail"] = SiteMarker.AV_YOURS
			s["tier"] = 0
		"down":
			s["status"] = SiteMarker.ST_DOWN
			s["avail"] = SiteMarker.AV_YOURS
			s["tier"] = 0
		"taken":
			s["status"] = SiteMarker.ST_TAKEN
		"exploit":
			s["kind"] = SiteMarker.KIND_EXPLOIT
			s["avail"] = SiteMarker.AV_NOT_YET
			s["tier"] = 2
			s["exploit"] = int(RC.ExploitType.INTEL)
		"heat":
			s["kind"] = SiteMarker.KIND_HEAT
			s["avail"] = SiteMarker.AV_NOT_YET
		"target":
			s["kind"] = SiteMarker.KIND_CENTRAL_SERVER
			s["tier"] = 0
	return s


func _build_marker_rows(into: Container, fs: int) -> void:
	var s := Settings.text_scale
	for r: Array in MARKER_ROWS:
		var key := String(r[0])
		if strip and not STRIP_MARKER_KEYS.has(key):
			continue  # the strip says what the map shows most; its full key says all
		var swatch := _swatch(s)
		if key == "target":
			swatch.draw.connect(_draw_target_swatch.bind(swatch))
		else:
			var v := SiteMarkerView.new(marker_spec(key), true)
			v.scale = Vector2.ONE * MARKER_SWATCH_SCALE * s
			swatch.add_child(v)
			swatch.resized.connect(func() -> void: v.position = swatch.size * 0.5 - Vector2(0, SiteMarker.PAD_DROP * 0.5) * v.scale.y)
		into.add_child(_marker_row("Marker_%s" % key, key, swatch, String(r[1]), fs))
	for r: Array in MARKER_LINE_ROWS:
		var key := String(r[0])
		if strip and not (key == "locked" or (key == "threat" and marker_threat)):
			continue
		var swatch := _swatch(s)
		swatch.draw.connect(_draw_line_swatch.bind(swatch, key))
		if key == "locked":
			var lock := GlyphIcon.make(&"state_locked", MapLegend.ICON_SWATCH * s * 0.5)
			lock.name = "Padlock"
			lock.fill = Palette.TEXT_HI
			swatch.add_child(lock)
			swatch.resized.connect(func() -> void: lock.position = swatch.size * 0.5 - lock.custom_minimum_size * 0.5)
		into.add_child(_marker_row("Line_%s" % key, key, swatch, String(r[1]), fs))
	show_all_cell = Label.new()
	show_all_cell.name = "ShowAll"
	show_all_cell.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	show_all_cell.text = UiTip.for_input(CityMapOverlay.tr_word(SHOW_ALL), CityMapOverlay.tr_word(SHOW_ALL_PAD))
	show_all_cell.tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	show_all_cell.tooltip_text = UiTip.fold(UiTip.for_input(CityMapOverlay.tr_word(SHOW_ALL_TIP), CityMapOverlay.tr_word(SHOW_ALL_TIP_PAD)))
	show_all_cell.mouse_filter = Control.MOUSE_FILTER_STOP
	show_all_cell.add_theme_font_size_override("font_size", fs)
	show_all_cell.add_theme_color_override("font_color", PaletteSkins.chrome(Palette.NET_CYAN))
	show_all_cell.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	show_all_cell.mouse_entered.connect(func() -> void: show_all_changed.emit(true))
	show_all_cell.mouse_exited.connect(func() -> void: show_all_changed.emit(opened))
	into.add_child(show_all_cell)


func _swatch(s: float) -> Control:
	var swatch := Control.new()
	swatch.name = "Swatch"
	swatch.custom_minimum_size = Vector2.ONE * ICON_SWATCH * MARKER_SWATCH_CELL * s
	swatch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return swatch


## A v4 key row: its swatch and words; pointing at it tells the meaning in plain words.
func _marker_row(row_name: String, key: String, swatch: Control, words: String, fs: int) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.name = row_name
	row.set_meta(&"meaning", key)
	row.mouse_filter = Control.MOUSE_FILTER_PASS
	row.tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED  # translated here, once
	row.tooltip_text = UiTip.fold(SiteMarker.meaning(key) if SiteMarker.MEANINGS.has(key) else CityMapOverlay.tr_word("A raid's route toward your CORE."))
	row.add_theme_constant_override("separation", roundi(ICON_SWATCH_GAP * Settings.text_scale * 0.5))
	row.add_child(swatch)
	var l := _text(words, fs)
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(l)
	return row


func _draw_target_swatch(swatch: Control) -> void:
	var c := swatch.size * 0.5
	var r := swatch.size.x * 0.42
	# B1b: the key shows the TARGET in the kit's one wax material (the map's own mark).
	var pts := PencilShapes.hand_circle(c, Vector2(r, r * CityMapOverlay.TARGET_FLAT), CityMapOverlay.TARGET_SEED)
	PencilSet.show_on(swatch, [pts] as Array[PackedVector2Array], GreasePencilMark.Ink.THREAT, CityMapOverlay.TARGET_SEED)


func _draw_line_swatch(swatch: Control, key: String) -> void:
	var a := Vector2(swatch.size.x * 0.05, swatch.size.y * 0.7)
	var b := Vector2(swatch.size.x * 0.95, swatch.size.y * 0.3)
	var k := Settings.text_scale * MARKER_SWATCH_SCALE
	match key:
		"locked":
			var d := 0.0
			var pts := PackedVector2Array([a, b])
			var total := a.distance_to(b)
			while d < total:
				swatch.draw_polyline(PencilShapes.trim(pts, d, minf(total, d + CityMapOverlay.DASH_ON * k)), Palette.TEXT_LO, maxf(1.0, 2.0 * k))
				d += CityMapOverlay.DASH_PERIOD * k
			SiteMarker.draw_lock_disc(swatch, swatch.size * 0.5, swatch.size.x * 0.24)
		"depowered":
			SiteMarker.draw_depowered(swatch, PackedVector2Array([a, b]), k)
		_:
			var col := Palette.corp_color(_corp_id)
			var d := 0.0
			var total := a.distance_to(b)
			var dir := (b - a) / maxf(total, 0.001)
			while d < total:
				swatch.draw_line(a + dir * d, a + dir * minf(total, d + CityMapOverlay.DASH_ON * k * 1.5), col, maxf(1.5, 3.0 * k))
				d += CityMapOverlay.DASH_PERIOD * k * 1.5


## A compact legend pinned to `area`'s bottom-left corner (the raid maps: the map is the
## city behind the panels, `area` the open part of the screen over it). It grows up and
## right from that corner with its minimum size (bigger text makes it taller).
static func pin_to(area: Control, corporation_id: StringName, p_strip: bool = false) -> MapLegend:
	var legend := MapLegend.new(corporation_id, true, p_strip)
	legend.mouse_filter = Control.MOUSE_FILTER_IGNORE
	area.add_child(legend)
	legend.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT, Control.PRESET_MODE_MINSIZE, int(PIN_MARGIN))
	legend.grow_vertical = Control.GROW_DIRECTION_BEGIN
	legend.minimum_size_changed.connect(legend._repin)
	return legend


## B3 (review section f, round 44 `raid_setup.png`'s MAP KEY strip): a raid page's key: the
## strip folded to its MAP KEY line at every text size, opening over the map on hover, a press
## or the pad's key button; never a big box over the map or the pencil.
static func pin_key_line(area: Control, corporation_id: StringName) -> MapLegend:
	var legend := pin_to(area, corporation_id, true)
	legend.always_fold = true
	legend._repin()
	return legend


## Shows only the rows keyed in `keys` (ROW_KEYS and icon kinds; [] = every row).
func show_only(keys: Array[String]) -> MapLegend:
	only = keys.duplicate()
	_build()
	return self


## The row keys a city map graph shows (H23 S4): marks, the Sites' statuses (from the
## campaign grid), link and threat route edges, and the node icon kinds.
static func keys_of(graph: Dictionary, grid: GridState) -> Array[String]:
	var out: Array[String] = []
	for n in graph.get("nodes", []):
		match String(n.get("mark", "")):
			CityMapOverlay.MARK_SPRAY:
				_add_key(out, "claimed")
			CityMapOverlay.MARK_CROSS:
				_add_key(out, "taken")
		if grid != null:
			match grid.status_of(n["id"]):
				GridState.SiteStatus.CLEARED:
					_add_key(out, "cleared")
				GridState.SiteStatus.CORPORATE:
					_add_key(out, "corporate")
		var kind := String(n.get("kind", ""))
		if kind != "":
			_add_key(out, kind)
	for e in graph.get("edges", []):
		if bool(e.get("dashed", false)):
			_add_key(out, "threat")
		elif bool(e.get("flow", false)):
			_add_key(out, "link")
	return out


static func _add_key(out: Array[String], key: String) -> void:
	if not out.has(key):
		out.append(key)


## Keeps a pinned legend's bottom-left corner in place when its minimum size changes.
func _repin() -> void:
	if get_parent() is Container:
		return
	var ms := get_combined_minimum_size()
	offset_right = offset_left + ms.x
	offset_top = offset_bottom - ms.y


## Keeps `control`'s minimum size at `with_legend` while the legend shows, `without`
## otherwise, live.
func link_size(control: Control, with_legend: Vector2, without: Vector2) -> void:
	_linked = control
	_size_on = with_legend
	_size_off = without
	_apply_link()


func _on_settings_changed() -> void:
	visible = Settings.map_legend
	if not is_equal_approx(_built_scale, Settings.text_scale):
		if not foldable():
			opened = false
			_hover_opened = false
		_build()
	_apply_link()


func _apply_link() -> void:
	if _linked != null and is_instance_valid(_linked):
		_linked.custom_minimum_size = _size_on if Settings.map_legend else _size_off
