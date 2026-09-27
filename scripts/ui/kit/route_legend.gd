class_name RouteLegend
extends TerminalWindow
## The netrun route's key (H23 S7: the route showed the campaign map's key, claimed /
## seized / threat route / CORE, which is not on a route): one row for each node kind the
## route actually has, its icon drawn by the map's own painter (CityMapOverlay.draw_icon)
## and what the node does, in a fixed order. Follows Settings.map_legend and the text
## size, like MapLegend. View only.

## What each route node kind is and does (the legend's rows and the nodes' tooltips).
const MEANINGS := {CityMapOverlay.KIND_FIGHT: "Fight: win it for Cycles and loot",
	CityMapOverlay.KIND_ELITE: "Elite fight: harder, better loot",
	CityMapOverlay.KIND_EVENT: "Event: a choice, and its price",
	CityMapOverlay.KIND_SHOP: "Shop: spend Cycles (Modem)",
	CityMapOverlay.KIND_RACK: "Rack: fight, then bank Schematics and assets"}
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


## A key for the node kinds in `p_kinds` (any order; unknown kinds are left out).
func _init(p_kinds: Array = []) -> void:
	super("ROUTE KEY")
	name = "RouteLegend"
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
	update_minimum_size()


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
	l.text = String(MEANINGS.get(kind, kind))
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_font_size_override("font_size", roundi(FONT * s))
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(l)
	return row


func _on_settings_changed() -> void:
	visible = Settings.map_legend
	if not is_equal_approx(_built_scale, Settings.text_scale):
		_build()
