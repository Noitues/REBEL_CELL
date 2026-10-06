class_name RouteLegend
extends TerminalWindow
## The netrun route's key (H23 S7: one entry for each node kind the route actually has, in a
## fixed order). ART-7 3B (ART_BIBLE v2 §4.6, round 37 / 38 references): one CRT terminal
## strip along the foot of the map: each kind's sticker as the map draws it
## (RouteOverlay.draw_sticker) with its word, the state rings (walked, next, not yet, cut
## off), then the D13 cue "HOVER HERE: SHOW ALL NODES": hovering the strip shows every node
## (`show_all_hovered`; the scene tells the map). With Options "Always show all nodes" on it
## reads "SHOWING ALL NODES". Each entry's tooltip says what the kind does (MEANINGS). Follows
## Settings.map_legend and the text size, like MapLegend. View only.

## Emitted when the pointer enters (true) or leaves (false) the strip (D13 legend hover).
signal show_all_hovered(on: bool)

## What each route node kind is and does (the entries' and the nodes' tooltips).
const MEANINGS := {CityMapOverlay.KIND_FIGHT: "Fight: win it for Cycles and loot", # TR
	CityMapOverlay.KIND_ELITE: "Elite fight: harder, better loot", # TR
	CityMapOverlay.KIND_EVENT: "Event: a choice, and its price", # TR
	CityMapOverlay.KIND_SHOP: "Shop: spend Cycles (Mainframe)", # TR
	CityMapOverlay.KIND_RACK: "Rack: fight, then bank Schematics and assets"} # TR
## The strip's word for each kind (§4.6 legend: COMBAT, ELITE, EVENT, SHOP, RACK).
const SHORT := {CityMapOverlay.KIND_FIGHT: "COMBAT", CityMapOverlay.KIND_ELITE: "ELITE", # TR
	CityMapOverlay.KIND_EVENT: "EVENT", CityMapOverlay.KIND_SHOP: "SHOP", CityMapOverlay.KIND_RACK: "RACK"} # TR
## ART-7 3B: the state rings the key names (option A), and their words.
const COLOR_KEYS: Array[String] = ["walked", "next", "later", "cut"]
## Parity ROUTE-05: round 37's words where the route has the same state (selectable, not yet
## (hidden)); walked is the route's own (the walked cable).
const COLOR_WORDS: Array[String] = ["walked", "selectable: pick one (numbered)", "not yet (hidden)", "cut off"] # TR
## The D13 cue (mouse, shown through UiTip.for_input with PAD_WORDS when pad_active), its pad
## words (UiTip.for_input(HOVER_WORDS, PAD_WORDS)), and the words while every node shows.
const HOVER_WORDS := "HOVER HERE: SHOW ALL NODES" # TR
const PAD_WORDS := "OPTIONS > DISPLAY: SHOW ALL NODES" # TR
const SHOWING_WORDS := "SHOWING ALL NODES" # TR
## Entry order (the kinds a route can have).
const ORDER: Array[String] = [CityMapOverlay.KIND_FIGHT, CityMapOverlay.KIND_ELITE, CityMapOverlay.KIND_EVENT,
	CityMapOverlay.KIND_SHOP, CityMapOverlay.KIND_RACK]
## Lettering and swatch at text scale 1.0 (px), the swatch's sticker share, the gaps.
const FONT := 12
const TITLE_FONT := 15
const SWATCH := 22.0
const ICON_SHARE := 0.5
const GAP := 8.0
const GROUP_GAP := 18.0

## The kinds shown, in ORDER.
var kinds: Array[String] = []
var _built_scale: float = -1.0
var _built_all: bool = false
var _built_pad: bool = false
## The corporation's colour (kept for callers; option A's stickers keep their kind colours).
var corp_color: Color = Palette.CORP_SOLACE
## The strip's row (every entry is in it).
var strip: HBoxContainer
## The D13 cue's label.
var cue: Label


## A key for the node kinds in `p_kinds` (any order; unknown kinds are left out).
func _init(p_kinds: Array = [], p_corp_color: Color = Palette.CORP_SOLACE) -> void:
	super("", Palette.CELL_ACID)
	name = "RouteLegend"
	corp_color = p_corp_color
	# H24 S3/S4: the key's words are translated here and shown as given.
	TextDb.shown_as_given(self)
	# D13: the strip takes the pointer (its hover shows every node); its entries do not.
	mouse_filter = Control.MOUSE_FILTER_STOP
	mouse_entered.connect(func() -> void: show_all_hovered.emit(true))
	mouse_exited.connect(func() -> void: show_all_hovered.emit(false))
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
	_built_all = Settings.always_show_all_nodes
	_built_pad = Settings.pad_active
	var s := Settings.text_scale
	for child in body.get_children():
		body.remove_child(child)
		child.free()
	strip = HBoxContainer.new()
	strip.name = "Strip"
	strip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	strip.add_theme_constant_override("separation", roundi(GAP * s))
	body.add_child(strip)
	for k in kinds:
		strip.add_child(_row(k, s))
	strip.add_child(_gap(s))
	for i in COLOR_KEYS.size():
		strip.add_child(_color_row(COLOR_KEYS[i], COLOR_WORDS[i], s))
	strip.add_child(_gap(s))
	cue = Label.new()
	cue.name = "ShowAllCue"
	cue.mouse_filter = Control.MOUSE_FILTER_IGNORE
	cue.add_theme_font_size_override("font_size", roundi(FONT * s))
	cue.add_theme_color_override("font_color", Palette.CELL_ACID)
	cue.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	strip.add_child(cue)
	_set_cue()
	update_minimum_size()


func _set_cue() -> void:
	if cue == null:
		return
	if Settings.always_show_all_nodes:
		cue.text = TranslationServer.translate(SHOWING_WORDS)
	else:
		cue.text = UiTip.for_input(TranslationServer.translate(HOVER_WORDS), TranslationServer.translate(PAD_WORDS))


## Shows "SHOWING ALL NODES" while the map shows every node (`on`), else the cue.
func set_showing_all(on: bool) -> void:
	if cue == null:
		return
	if on:
		cue.text = TranslationServer.translate(SHOWING_WORDS)
	else:
		_set_cue()


func _gap(s: float) -> Control:
	var g := ColorRect.new()
	g.color = Color(Palette.CELL_ACID, 0.5)
	g.custom_minimum_size = Vector2(maxf(1.0, s), SWATCH * s * 0.8)
	g.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	g.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var box := MarginContainer.new()
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_theme_constant_override("margin_left", roundi(GROUP_GAP * s * 0.5))
	box.add_theme_constant_override("margin_right", roundi(GROUP_GAP * s * 0.5))
	box.add_child(g)
	return box


## The ring colour of state key `key` (RouteInk: walked lime, next orange, not yet white, cut
## grey).
func color_of(key: String) -> Color:
	return RouteInk.ring_of(key)


func _color_row(key: String, words: String, s: float) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.name = "Color_%s" % key
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override("separation", roundi(GAP * s * 0.5))
	var side := SWATCH * s
	var swatch := Control.new()
	swatch.name = "Swatch"
	swatch.custom_minimum_size = Vector2(side, side)
	swatch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# ART-7 3B: the ring as the map draws it, colour and style (never colour alone).
	swatch.set_meta(&"ring_style", String(RouteOverlay.RING_STYLES.get(key, "")))
	# Parity ROUTE-05: "not yet (hidden)" is the small disc the map draws for a hidden node.
	swatch.set_meta(&"ghost", key == RouteOverlay.STATE_LATER)
	swatch.draw.connect(func() -> void:
		if key == RouteOverlay.STATE_LATER:
			RouteOverlay.draw_ghost(swatch, swatch.size * 0.5, side * 0.4, key, s * 0.8 / RouteOverlay.GHOST_SHARE)
		else:
			RouteOverlay.draw_state_ring(swatch, swatch.size * 0.5, side * 0.36, key, s * 0.8))
	row.add_child(swatch)
	var l := Label.new()
	# "selectable: pick one (numbered)" reads "selectable" on the strip; the full words are its tooltip.
	l.text = TranslationServer.translate(words).get_slice(":", 0)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_font_size_override("font_size", roundi(FONT * s))
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.tooltip_text = TranslationServer.translate(words)
	row.add_child(l)
	return row


func _row(kind: String, s: float) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.name = "Kind_%s" % kind
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override("separation", roundi(GAP * s * 0.5))
	row.tooltip_text = TranslationServer.translate(String(MEANINGS.get(kind, kind)))
	var side := SWATCH * s
	var swatch := Control.new()
	swatch.name = "Swatch"
	swatch.custom_minimum_size = Vector2(side, side)
	swatch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	swatch.draw.connect(func() -> void:
		RouteOverlay.draw_sticker(swatch, kind, swatch.size * 0.5, side * ICON_SHARE, RouteOverlay.STATE_LATER, s * ICON_SHARE))
	row.add_child(swatch)
	var l := Label.new()
	l.text = TranslationServer.translate(String(SHORT.get(kind, kind)))
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_font_size_override("font_size", roundi(FONT * s))
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(l)
	return row


func _on_settings_changed() -> void:
	visible = Settings.map_legend
	if not is_equal_approx(_built_scale, Settings.text_scale) or _built_all != Settings.always_show_all_nodes or _built_pad != Settings.pad_active:
		_build()
