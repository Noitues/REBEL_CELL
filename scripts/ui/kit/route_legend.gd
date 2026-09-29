class_name RouteLegend
extends TerminalWindow
## The netrun route's key (H23 S7: the route showed the campaign map's key, claimed /
## seized / threat route / CORE, which is not on a route): one row for each node kind the
## route actually has, its icon drawn by the map's own painter (CityMapOverlay.draw_icon)
## and what the node does, in a fixed order. Follows Settings.map_legend and the text
## size, like MapLegend. View only.
##
## Art pass W8b (ART_BIBLE §6.10, §11 Route; W10 lint: it shrank to 9.8 px): every size is a
## §4.2 step x the text scale, and from MapLegend.FOLD_SCALE up the key folds to its ROUTE
## KEY line like the Grid's MAP KEY (pointing at it, pressing it or the pad's key button
## opens the rows; they fold again when the pointer leaves or on a second press), so it is
## never scaled below `caption` to fit its room (LegendSpot places a foldable key at 1:1).

## H24 K1 twin: the key was folded or opened.
signal fold_changed

## What each route node kind is and does (the legend's rows and the nodes' tooltips).
const MEANINGS := {CityMapOverlay.KIND_FIGHT: "Fight: win it for Cycles and loot", # TR
	CityMapOverlay.KIND_ELITE: "Elite fight: harder, better loot", # TR
	CityMapOverlay.KIND_EVENT: "Event: a choice, and its price", # TR
	CityMapOverlay.KIND_SHOP: "Shop: spend Cycles (Modem)", # TR
	CityMapOverlay.KIND_RACK: "Rack: fight, then bank Schematics and assets"} # TR
## H24 S12: what the route's node colours mean (the key said nothing of blue vs green):
## [colour key, words]; the colours are route_graph's.
const COLOR_KEYS: Array[String] = ["here", "next", "later", "visited", "corp"]
const COLOR_WORDS: Array[String] = ["you are here", "next: pick one (numbered)", "further along the route", "already visited", # TR
	"elite or the Rack (the corporation's colour)"] # TR
## The folded key's words (the Grid's MAP KEY twin).
const FOLD_WORDS := "ROUTE KEY" # TR
## The colour swatch's ring width at scale 1.0 (px).
const RING_WIDTH := 2.5
## Row order (the kinds a route can have).
const ORDER: Array[String] = [CityMapOverlay.KIND_FIGHT, CityMapOverlay.KIND_ELITE, CityMapOverlay.KIND_EVENT,
	CityMapOverlay.KIND_SHOP, CityMapOverlay.KIND_RACK]
## Row lettering and the title as type steps (§4.2), the icon swatch at text scale 1.0,
## the icon's share of it and the gap after it (px).
const FONT := UiTheme.CAPTION
const TITLE_FONT := UiTheme.BODY
const SWATCH := 22.0
const ICON_SHARE := 0.36
const GAP := 8.0

## The kinds shown, in ORDER.
var kinds: Array[String] = []
var _built_scale: float = -1.0
## The corporation's colour (elite and Rack nodes).
var corp_color: Color = Palette.CORP_SOLACE
## The rows (folded away behind `fold_button` at big text) and whether they are open.
var rows_box: VBoxContainer = null
var fold_button: Button = null
var opened: bool = false
var _hover_opened: bool = false
## Folded for want of room (see force_fold).
var _forced: bool = false


## A key for the node kinds in `p_kinds` (any order; unknown kinds are left out).
func _init(p_kinds: Array = [], p_corp_color: Color = Palette.CORP_SOLACE) -> void:
	super(TranslationServer.translate("ROUTE KEY"))
	name = "RouteLegend"
	corp_color = p_corp_color
	# H24 S3/S4: the key's words are translated here and shown as given.
	TextDb.shown_as_given(self)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	for k in ORDER:
		if p_kinds.has(k):
			kinds.append(k)
	_build()
	visible = Settings.map_legend
	Settings.changed.connect(_on_settings_changed)


## The route kinds of every node in `graph_nodes` (route_graph's "kind"), in ORDER.
static func kinds_of(graph_nodes: Array) -> Array[String]:
	var out: Array[String] = []
	for k in ORDER:
		for n in graph_nodes:
			if String(n.get("kind", "")) == k:
				out.append(k)
				break
	return out


## True when the key folds to its ROUTE KEY line: at big text, or when its room is too short
## for it at full size (`force_fold`: it is never scaled below its text size instead).
func foldable() -> bool:
	return _forced or Settings.text_scale >= MapLegend.FOLD_SCALE - 0.001


## Folds the key to its line because its room is too short for it (LegendSpot calls it
## instead of scaling it down); a text size change measures again.
func force_fold() -> void:
	if _forced:
		return
	_forced = true
	_build()


## True when the rows are hidden behind the ROUTE KEY line.
func is_folded() -> bool:
	return foldable() and not opened


## Opens (or folds) a foldable key's rows.
func set_opened(value: bool, by_hover: bool = false) -> void:
	_hover_opened = value and by_hover
	mouse_filter = Control.MOUSE_FILTER_PASS if _hover_opened else Control.MOUSE_FILTER_IGNORE
	if value == opened:
		return
	opened = value
	if rows_box != null:
		rows_box.visible = opened or not foldable()
	if fold_button != null:
		IconMark.attach(fold_button, StatIcon.MORE if not opened else StatIcon.CODEX)
	update_minimum_size()
	fold_changed.emit()


## The size its room is fitted around: the folded line for a foldable key, else the key.
func fit_size() -> Vector2:
	if not foldable() or rows_box == null or not rows_box.visible:
		return get_combined_minimum_size()
	rows_box.visible = false
	var folded := get_combined_minimum_size()
	rows_box.visible = true
	return folded


func _notification(what: int) -> void:
	if what == NOTIFICATION_MOUSE_EXIT and _hover_opened:
		set_opened(false)


func _build() -> void:
	_built_scale = Settings.text_scale
	var s := Settings.text_scale
	var head := find_child("TerminalTitle", true, false) as Label
	if head != null:
		head.add_theme_font_size_override("font_size", UiTheme.font_px(TITLE_FONT))
		# Folded, the ROUTE KEY line is the title (no second one over it), as MapLegend's strip.
		var bar := head.get_parent() as Control
		bar.visible = not foldable()
		var outer := bar.get_parent()
		if outer.get_child_count() > 1 and outer.get_child(1) is ColorRect:
			(outer.get_child(1) as ColorRect).visible = not foldable()
	for child in body.get_children():
		body.remove_child(child)
		child.free()
	fold_button = null
	if foldable():
		fold_button = Button.new()
		fold_button.name = "KeyToggle"
		fold_button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		fold_button.text = TranslationServer.translate(FOLD_WORDS)
		fold_button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		fold_button.add_theme_font_size_override("font_size", UiTheme.font_px(FONT))
		fold_button.tooltip_text = UiTip.fold(CityMapOverlay.tr_word("The map key: what the icons, colours and lines mean. Point at it or press it to open it; the pad's key button too."))
		fold_button.pressed.connect(func() -> void: set_opened(not opened))
		fold_button.mouse_entered.connect(func() -> void:
			if not opened:
				set_opened(true, true))
		IconMark.attach(fold_button, StatIcon.MORE if not opened else StatIcon.CODEX)
		body.add_child(fold_button)
	rows_box = VBoxContainer.new()
	rows_box.name = "Rows"
	rows_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rows_box.visible = opened or not foldable()
	body.add_child(rows_box)
	for k in kinds:
		rows_box.add_child(_row(k, s))
	for i in COLOR_KEYS.size():
		rows_box.add_child(_color_row(COLOR_KEYS[i], COLOR_WORDS[i], s))
	update_minimum_size()


## The colour a route node of colour key `key` is drawn in (route_graph's colours).
func color_of(key: String) -> Color:
	match key:
		"here":
			return Palette.CELL_PINK
		"next":
			return Palette.CELL_ACID
		"visited":
			return Color(Palette.NET_CYAN, 0.5)
		"corp":
			return corp_color
	return Palette.NET_CYAN


func _color_row(key: String, words: String, s: float) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.name = "Color_%s" % key
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override("separation", roundi(GAP * s))
	var side := SWATCH * s
	var swatch := Control.new()
	swatch.name = "Swatch"
	swatch.custom_minimum_size = Vector2(side, side)
	swatch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var col := color_of(key)
	swatch.draw.connect(func() -> void:
		swatch.draw_arc(swatch.size * 0.5, side * ICON_SHARE, 0.0, TAU, 20, col, RING_WIDTH * s, true))
	row.add_child(swatch)
	row.add_child(_words(words))
	return row


func _row(kind: String, s: float) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.name = "Kind_%s" % kind
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override("separation", roundi(GAP * s))
	var side := SWATCH * s
	var swatch := Control.new()
	swatch.name = "Swatch"
	swatch.custom_minimum_size = Vector2(side, side)
	swatch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	swatch.draw.connect(func() -> void:
		CityMapOverlay.draw_icon(swatch, kind, swatch.size * 0.5, side * ICON_SHARE, Palette.PAPER))
	row.add_child(swatch)
	row.add_child(_words(String(MEANINGS.get(kind, kind))))
	return row


## A row's words at the FONT step, translated here.
func _words(text: String) -> Label:
	var l := Label.new()
	l.text = TranslationServer.translate(text)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_font_size_override("font_size", UiTheme.font_px(FONT))
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	return l


func _on_settings_changed() -> void:
	visible = Settings.map_legend
	if not is_equal_approx(_built_scale, Settings.text_scale):
		_forced = false
		if not foldable():
			opened = false
			_hover_opened = false
		_build()
