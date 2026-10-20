class_name RouteLegend
extends TerminalWindow
## The netrun route's key (H23 S7: one entry for each node kind the route actually has, in a
## fixed order). ART-7 3B (ART_BIBLE v2 §4.6, round 37 / 38 references): one CRT terminal
## strip along the foot of the map: each kind's sticker as the map draws it
## (RouteOverlay.draw_sticker) with its word, the two state rings the map draws (walked,
## next; B3: hidden nodes are fully hidden and cut-off ones never drawn, round 44
## `route_page.png`), then the cue "HOVER: SHOW ALL LINKS": hovering the strip shows every run
## link as a hairline (`show_links_hovered`; the scene tells the map; designer Q4), and reads
## "SHOWING ALL LINKS" while it holds. Each entry's tooltip says what the kind does (MEANINGS). Follows
## Settings.map_legend and the text size, like MapLegend. View only.

## Emitted when the pointer enters (true) or leaves (false) the strip (B3, Q4: every link).
signal show_links_hovered(on: bool)
## F14: the pointer is over the row of node kind `kind` ("" = no row).
signal kind_hovered(kind: String)

## What each route node kind is and does (the entries' and the nodes' tooltips).
const MEANINGS := {CityMapOverlay.KIND_FIGHT: "Fight: win it for Cycles and loot", # TR
	CityMapOverlay.KIND_ELITE: "Elite fight: harder, better loot", # TR
	CityMapOverlay.KIND_EVENT: "Event: a choice, and its price", # TR
	CityMapOverlay.KIND_SHOP: "Shop: spend Cycles (Mainframe)", # TR
	CityMapOverlay.KIND_RACK: "Rack: fight, then bank Schematics and assets", # TR
	CityMapOverlay.KIND_REST: "Rest: placeholder text", # TR
	CityMapOverlay.KIND_WORKSHOP: "Workshop: placeholder text", # TR
	CityMapOverlay.KIND_CACHE: "Cache: placeholder text"} # TR
## The strip's word for each kind (round 44 `route_page.png`: FIGHT, ELITE, EVENT, SHOP, RACK).
const SHORT := {CityMapOverlay.KIND_FIGHT: "FIGHT", CityMapOverlay.KIND_ELITE: "ELITE", # TR
	CityMapOverlay.KIND_EVENT: "EVENT", CityMapOverlay.KIND_SHOP: "SHOP", CityMapOverlay.KIND_RACK: "RACK", # TR
	CityMapOverlay.KIND_REST: "REST", CityMapOverlay.KIND_WORKSHOP: "WORKSHOP", CityMapOverlay.KIND_CACHE: "CACHE"} # TR
## ART-7 3B: the state rings the key names (option A), and their words. B3 (round 44): only the
## rings the map draws by default (walked, next).
const COLOR_KEYS: Array[String] = ["walked", "next"]
## Round 44's words ("next" reads alone on the strip; the full words are its tooltip).
const COLOR_WORDS: Array[String] = ["walked", "next: pick one (numbered)"] # TR
## The cue (mouse, shown through UiTip.for_input with PAD_WORDS when pad_active), its pad
## words (UiTip.for_input(HOVER_WORDS, PAD_WORDS)), the words while the hover shows every link,
## and the words while Options shows every node.
const HOVER_WORDS := "HOVER: SHOW ALL LINKS" # TR
const PAD_WORDS := "HOVER: SHOW ALL LINKS" # TR
const LINKS_WORDS := "SHOWING ALL LINKS" # TR
## Entry order (the kinds a route can have).
const ORDER: Array[String] = [CityMapOverlay.KIND_FIGHT, CityMapOverlay.KIND_ELITE, CityMapOverlay.KIND_EVENT,
	CityMapOverlay.KIND_SHOP, CityMapOverlay.KIND_RACK,
	CityMapOverlay.KIND_REST, CityMapOverlay.KIND_WORKSHOP, CityMapOverlay.KIND_CACHE]
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
var _built_pad: bool = false
## The corporation's colour (kept for callers; option A's stickers keep their kind colours).
var corp_color: Color = Palette.CORP_SOLACE
## The strip's rows (every entry is in it). M14 12Q-WORDS (L54): a flow, so at big text it wraps
## to a second row at the room it is given instead of being scaled down under the text size.
var strip: HFlowContainer
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
	mouse_entered.connect(func() -> void: show_links_hovered.emit(true))
	mouse_exited.connect(func() -> void:
		_set_hovered_kind("")
		show_links_hovered.emit(false))
	for k in ORDER:
		if p_kinds.has(k):
			kinds.append(k)
	_build()
	visible = Settings.map_legend
	Settings.changed.connect(_on_settings_changed)


var _hovered_kind: String = ""


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		_set_hovered_kind(kind_at((event as InputEventMouseMotion).global_position))


## The node kind of the row under global point `p` ("" = none).
func kind_at(p: Vector2) -> String:
	if strip == null:
		return ""
	for k in kinds:
		var row := strip.get_node_or_null("Kind_%s" % k) as Control
		if row != null and row.get_global_rect().has_point(p):
			return k
	return ""


func _set_hovered_kind(k: String) -> void:
	if k == _hovered_kind:
		return
	_hovered_kind = k
	kind_hovered.emit(k)


## The route kinds of every node in `graph_nodes` (the nodes' "kind"), in ORDER.
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
	_built_pad = Settings.pad_active
	var s := Settings.text_scale
	for child in body.get_children():
		body.remove_child(child)
		child.free()
	strip = HFlowContainer.new()
	strip.name = "Strip"
	strip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	strip.alignment = FlowContainer.ALIGNMENT_CENTER
	strip.add_theme_constant_override("h_separation", roundi(GAP * s))
	strip.add_theme_constant_override("v_separation", roundi(GAP * s * 0.5))
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
	# F13: the cue keeps one width whichever words it shows, so hovering the key never resizes
	# the strip (a resize refits the map and snapped the player's zoom and pan back).
	var font := cue.get_theme_font("font")
	var fsize := roundi(FONT * s)
	var widest := 0.0
	for w in [HOVER_WORDS, PAD_WORDS, LINKS_WORDS]:
		widest = maxf(widest, font.get_string_size(TranslationServer.translate(w), HORIZONTAL_ALIGNMENT_LEFT, -1.0, fsize).x)
	cue.custom_minimum_size.x = ceilf(widest)
	_set_cue()
	update_minimum_size()


## The strip's width on one row (px, local, with the window's margins): the most room it takes.
func one_row_width() -> float:
	if strip == null:
		return get_combined_minimum_size().x
	var w := 0.0
	var n := 0
	for c in strip.get_children():
		if c is Control and (c as Control).visible:
			w += (c as Control).get_combined_minimum_size().x
			n += 1
	w += strip.get_theme_constant("h_separation") * maxi(0, n - 1)
	var sb := get_theme_stylebox("panel")
	if sb != null:
		w += sb.get_margin(SIDE_LEFT) + sb.get_margin(SIDE_RIGHT)
	return ceilf(w)


func _set_cue() -> void:
	if cue == null:
		return
	cue.text = UiTip.for_input(TranslationServer.translate(HOVER_WORDS), TranslationServer.translate(PAD_WORDS))


## B3 (Q4): "SHOWING ALL LINKS" while the strip's hover shows every link (`on`), else the cue.
func set_showing_links(on: bool) -> void:
	if cue == null:
		return
	if on:
		cue.text = TranslationServer.translate(LINKS_WORDS)
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
	swatch.draw.connect(func() -> void:
		RouteOverlay.draw_state_ring(swatch, swatch.size * 0.5, side * 0.36, key, s * 0.8))
	row.add_child(swatch)
	var l := Label.new()
	# "next: pick one (numbered)" reads "next" on the strip; the full words are its tooltip.
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
	if not is_equal_approx(_built_scale, Settings.text_scale) or _built_pad != Settings.pad_active:
		_build()
