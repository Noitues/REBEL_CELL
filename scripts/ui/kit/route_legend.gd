class_name RouteLegend
extends TerminalWindow
## The netrun route's key (H23 S7: the route showed the campaign map's key, claimed /
## taken / threat route / CORE, which is not on a route): one row for each node kind the
## route actually has, its icon drawn by the map's own painter (CityMapOverlay.draw_icon)
## and what the node does, in a fixed order. Follows Settings.map_legend and the text
## size, like MapLegend. View only.

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
## The colour swatch's ring width at scale 1.0 (px).
const RING_WIDTH := 2.5
## Row order (the kinds a route can have).
const ORDER: Array[String] = [CityMapOverlay.KIND_FIGHT, CityMapOverlay.KIND_ELITE, CityMapOverlay.KIND_EVENT,
	CityMapOverlay.KIND_SHOP, CityMapOverlay.KIND_RACK]
## Row lettering and icon swatch at text scale 1.0 (px), and the icon's share of it.
const FONT := 12
const TITLE_FONT := 15
const SWATCH := 22.0
const ICON_SHARE := 0.36
const GAP := 8.0

## The kinds shown, in ORDER.
var kinds: Array[String] = []
var _built_scale: float = -1.0
## The corporation's colour (elite and Rack nodes).
var corp_color: Color = Palette.CORP_SOLACE


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


func _build() -> void:
	_built_scale = Settings.text_scale
	var s := Settings.text_scale
	var head := find_child("TerminalTitle", true, false) as Label
	if head != null:
		head.add_theme_font_size_override("font_size", roundi(TITLE_FONT * s))
	for child in body.get_children():
		body.remove_child(child)
		child.free()
	for k in kinds:
		body.add_child(_row(k, s))
	for i in COLOR_KEYS.size():
		body.add_child(_color_row(COLOR_KEYS[i], COLOR_WORDS[i], s))
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
	var l := Label.new()
	l.text = TranslationServer.translate(words)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_font_size_override("font_size", roundi(FONT * s))
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(l)
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
	var l := Label.new()
	l.text = TranslationServer.translate(String(MEANINGS.get(kind, kind)))
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_font_size_override("font_size", roundi(FONT * s))
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(l)
	return row


func _on_settings_changed() -> void:
	visible = Settings.map_legend
	if not is_equal_approx(_built_scale, Settings.text_scale):
		_build()
