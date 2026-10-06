class_name HqRunView
extends Control
## ART-8 8w: the HQ run's page on the city (bible 4.6 / 4.7, wave 2b): its own CityView3D
## framed on the corporation's compound (HqCompoundStage: the manifest's camera; DISPATCH's
## run in the round 43 Tokyo canyon), with the run drawn over it in the route's ink: the
## entry and "you are here", the links (walked a solid lime line, the live ones a crawling
## orange dash, the rest a white dash), the nodes as the route's vinyl stickers with their
## state rings, and the Central Server: the rack sticker, the red grease-pencil TARGET circle
## and the yellow `CENTRAL SERVER // <name>` chip clear of the pencil.
## Headless (no renderer) it draws the marks only, projected by the same camera, so the
## page's maths are testable. A view: it emits `node_pressed` and never changes game state.
## Parity S-HQRUN (round 43 HQ run concepts, designer group ruling 2026-10-05): the page's
## yellow title sticker per corporation, the `> HQ MECHANIC` terminal at the foot presenting
## the HQ run's rules that exist (the breach: the gate's Exploits; GDD 4.2 / 11.7) with a
## STEP chip, the state key strip (walked / selectable / not yet / cut off), name tabs and
## choice numbers on the selectable nodes, cut-off nodes on a pale backing so they read on a
## dark compound, the entry as the concept's lime diamond; the chip and the page's chrome
## step aside while the Central Server's gate is open over the page (`set_gate_open`, called
## by the gate through GROUP). The per-corporation mechanics' words (CLIMB THE HELIX, the
## crane and train, the eye, the missile loop, SYNC STRIKE) are G12: listed, not built.

## A selectable node was clicked (or pressed by its number).
signal node_pressed(id: StringName)

## The group every HQ-run page joins (the gate tells the page it is open over it).
const GROUP := &"hq_run_view"
const CHIP_WORDS := "CENTRAL SERVER // %s" # TR
## The page's title sticker: "<CORPORATION>: HQ RUN" (the concept's mechanic names wait for G12).
const TITLE_WORDS := "%s: HQ RUN" # TR
## The foot terminal's header, its STEP chip and its words (the rules the run has today).
const MECHANIC_TITLE := "HQ MECHANIC" # TR
const STEP_WORDS := "STEP %d/%d" # TR
const BREACH_RULE := "Today's HQ run is the breach: one node, the Central Server. Its gate takes %d Exploits; each extra one weakens the boss further." # TR
const MAP_RULE := "Walk the compound layer by layer to the Central Server (%d layers). Its gate takes %d Exploits." # TR
## The key strip's states (RouteOverlay.STATE_*) and their words, in the concept's order.
const KEY_STATES: Array[String] = [RouteOverlay.STATE_WALKED, RouteOverlay.STATE_NEXT, RouteOverlay.STATE_LATER, RouteOverlay.STATE_CUT]
const KEY_WORDS: Array[String] = ["walked", "selectable", "not yet", "cut off"] # TR
## Title sticker: lettering (px at text scale 1.0), tilt (degrees), inset from the page's
## top-left corner under the run's HUD band (`top_inset`).
const TITLE_PX := 26.0
const TITLE_TILT := -2.0
const EDGE := 16.0
## The foot: the gap between the terminal (the width the key leaves) and the key; the key's
## ring swatch (px) and its ring share.
const FOOT_GAP := 24.0
const KEY_SWATCH := 18.0
const KEY_RING_SHARE := 0.36
## Name tabs under a selectable node: gap under the sticker, padding, lettering, border.
const TAB_GAP := 3.0
const TAB_PAD := Vector2(4.0, 1.0)
const TAB_FONT := 12
const TAB_BORDER := 1.0
const TAB_GLASS_ALPHA := 0.88
## A cut-off node's pale backing (so its grey sticker reads on a dark compound).
const CUT_BACKING_ALPHA := 0.5
const CUT_BACKING_GROW := 4.0
## The entry's lime diamond: half-width and squash (the ground's iso foreshortening).
const ENTRY_DIAMOND := 9.0
const ENTRY_SQUASH := 0.5
## The chip: gap above the pencil circle, padding, lettering (screen px at text scale 1.0)
## and its glass alpha.
const CHIP_GAP := 8.0
const CHIP_PAD := 6.0
const CHIP_FONT := 15
const CHIP_GLASS_ALPHA := 0.9
## The entry's size for the operative pin when no node is current.
const ENTRY_RADIUS := 7.0
## A click reaches a node within its sticker plus this (screen px).
const PICK_SLACK := 6.0
## The page keeps every node and the entry this far inside its edges (screen px), widening
## the compound's reference framing up to FIT_MAX_SHARE times when it must.
const FIT_MARGIN_PX := 64.0
const FIT_MAX_SHARE := 2.0
## The foot's terminal and key strip take this much of the page's height (px at text scale 1.0).
const FOOT_RESERVE := 104.0
## Room over the topmost node under the HUD band: the TARGET circle and the CENTRAL SERVER chip
## above it (px at text scale 1.0).
const TOP_ROOM := 80.0

var corp: StringName = &""
## The Central Server's name, translated and upper case (the Site's display name).
var server_label: String = ""
var graph: MapGraph = null
var current_id: StringName = &""
var visited: Array[StringName] = []
var available: Array[StringName] = []
## The city (null headless or before mount).
var city: CityView3D = null
## The camera the marks are projected with (the city's own when there is one).
var iso: CityIsoCamera = null
var anim_t: float = 0.0
## How far down the page's title sits: the run's HUD band covers the page's top.
var top_inset: float = HudBar.BAND_HEIGHT
## The Exploits the breach's gate takes (the campaign config's minimum).
var min_exploits: int = 3
## True while the Central Server's gate is open over the page (its chip and chrome step aside).
var gate_open: bool = false
## The page's chrome (built on show_run): the title sticker, the foot terminal and its rule
## label, the key strip.
var title_sticker: VerbSticker = null
var mechanic: CrtWindow = null
var mechanic_text: Label = null
var key_strip: CrtWindow = null
var _chrome: MarginContainer = null
var _foot: Control = null
var _foot_top: float = -1.0
var _built_scale: float = 1.0

var _layout: HqCompoundLayoutData = null
var _manifest: Dictionary = {}
var _at: Transform3D = Transform3D()
var _points: Dictionary = {}
var _entry: Vector3 = Vector3.ZERO
var _city_rect: TextureRect = null
var _marks: Control = null


func _init() -> void:
	name = "HqRunView"
	mouse_filter = Control.MOUSE_FILTER_STOP
	_city_rect = TextureRect.new()
	_city_rect.name = "City"
	_city_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_city_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_city_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_city_rect.stretch_mode = TextureRect.STRETCH_SCALE
	add_child(_city_rect)
	_marks = Control.new()
	_marks.name = "Marks"
	_marks.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_marks.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_marks.draw.connect(_draw_marks)
	add_child(_marks)
	# B1b: the TARGET's grease pencil is the kit's wax, over the marks.
	_pencil = PencilSet.under(self)
	resized.connect(_on_resized)
	add_to_group(GROUP)


## Shows run `graph` on `p_corp`'s compound: the walked, current and selectable nodes, and
## the Central Server named `p_server_label`.
func show_run(p_corp: StringName, p_graph: MapGraph, p_current: StringName, p_visited: Array[StringName],
		p_available: Array[StringName], p_server_label: String) -> void:
	corp = p_corp
	graph = p_graph
	current_id = p_current
	visited = p_visited.duplicate()
	available = p_available.duplicate()
	server_label = p_server_label
	_manifest = HqCompoundStage.manifest(corp)
	_layout = HqCompoundStage.layout(corp)
	_at = HqCompoundStage.place(CityView3D.CONFIG, corp, _manifest)
	_points = HqCompoundStage.node_points(_layout, graph, _at)
	_entry = HqCompoundStage.entry_point(_layout, _at)
	var cfg := RunManager.config()
	if cfg != null:
		min_exploits = cfg.min_exploits_for_breach
	_frame()
	if CityView3D.can_render() and city == null:
		_mount_city()
	_build_chrome()
	_marks.queue_redraw()


## The gate over the page opened (`on`) or closed: the chip (the gate names the server) and
## the page's chrome step aside under it (GATE-02).
func set_gate_open(on: bool) -> void:
	gate_open = on
	for c: Control in [title_sticker, mechanic, key_strip]:
		if c != null:
			c.visible = not on
	_marks.queue_redraw()


## The title sticker's words: "<CORPORATION>: HQ RUN" (the corporation's first name word).
func title_text() -> String:
	return tr(TITLE_WORDS) % corp_word(corp)


## The corporation's short name in capitals: the first word of its display name
## ("Solace Biosystems" -> SOLACE; REBEL_CELL stays REBEL_CELL).
static func corp_word(p_corp: StringName) -> String:
	var cd := ContentRegistry.get_content(p_corp) as CorporationData
	var name_text := TextDb.t(cd, "display_name") if cd != null else String(p_corp)
	return name_text.get_slice(" ", 0).to_upper()


## The foot terminal's rule: the breach (one node) or a full run map's layers, with the
## gate's Exploits.
func mechanic_rule() -> String:
	var layers := graph.layer_count() if graph != null else 0
	if layers <= 1:
		return tr(BREACH_RULE) % min_exploits
	return tr(MAP_RULE) % [layers, min_exploits]


## The foot terminal's chip: the step the run is on (walked nodes) of its layers.
func step_text() -> String:
	return tr(STEP_WORDS) % [visited.size(), graph.layer_count() if graph != null else 0]


## The page's chrome in one full-page frame: the title row at the top left (under the HUD
## band, `top_inset`), the terminal and the key along the foot (the terminal takes the width
## the key leaves).
func _build_chrome() -> void:
	if _chrome != null:
		_chrome.free()
	_foot_top = -1.0
	var k := Settings.text_scale
	_built_scale = k
	var edge := roundi(EDGE * k)
	_chrome = MarginContainer.new()
	_chrome.name = "Chrome"
	_chrome.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_chrome.add_theme_constant_override("margin_left", edge)
	_chrome.add_theme_constant_override("margin_right", edge)
	_chrome.add_theme_constant_override("margin_bottom", edge)
	_chrome.add_theme_constant_override("margin_top", roundi(top_inset) + edge)
	add_child(_chrome)
	var col := VBoxContainer.new()
	col.name = "Column"
	_chrome.add_child(col)
	var top := HBoxContainer.new()
	top.name = "TitleRow"
	col.add_child(top)
	title_sticker = VerbSticker.new(title_text(), VerbSticker.Fill.YELLOW, TITLE_PX, TITLE_TILT)
	title_sticker.name = "TitleSticker"
	title_sticker.pre_translated = true
	top.add_child(title_sticker)
	var fill := Control.new()
	fill.name = "Middle"
	fill.size_flags_vertical = Control.SIZE_EXPAND_FILL
	col.add_child(fill)
	var foot := HBoxContainer.new()
	foot.name = "Foot"
	foot.add_theme_constant_override("separation", roundi(FOOT_GAP * k))
	col.add_child(foot)
	_foot = foot
	foot.resized.connect(_on_foot_laid_out)
	mechanic = CrtWindow.new(tr(MECHANIC_TITLE))
	mechanic.name = "HqMechanic"
	mechanic.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	mechanic.size_flags_vertical = Control.SIZE_SHRINK_END
	mechanic.tag_label.text = step_text()
	mechanic_text = Chrome.body_label(mechanic_rule(), UiTheme.CAPTION, Palette.TEXT_MID)
	mechanic_text.add_theme_font_override(&"font", Palette.mono())
	mechanic_text.name = "Rule"
	mechanic.body.add_child(mechanic_text)
	foot.add_child(mechanic)
	key_strip = CrtWindow.new("")
	key_strip.name = "StateKey"
	key_strip.size_flags_vertical = Control.SIZE_SHRINK_END
	var row := HBoxContainer.new()
	row.name = "Keys"
	row.add_theme_constant_override("separation", roundi(UiTheme.SP_M * k))
	key_strip.body.add_child(row)
	for i in KEY_STATES.size():
		row.add_child(_key_row(KEY_STATES[i], KEY_WORDS[i], k))
	foot.add_child(key_strip)
	_ignore_mouse(_chrome)
	move_child(_chrome, _marks.get_index() + 1)
	set_gate_open(gate_open)


func _key_row(state: String, words: String, k: float) -> HBoxContainer:
	var row := HBoxContainer.new()
	row.name = "Key_%s" % state
	row.add_theme_constant_override("separation", roundi(UiTheme.SP_XS * k))
	var side := KEY_SWATCH * k
	var swatch := Control.new()
	swatch.name = "Swatch"
	swatch.custom_minimum_size = Vector2(side, side)
	swatch.draw.connect(func() -> void:
		RouteOverlay.draw_state_ring(swatch, swatch.size * 0.5, side * KEY_RING_SHARE, state, k * 0.7))
	row.add_child(swatch)
	var l := Chrome.caps_label(tr(words), UiTheme.CAPTION, Palette.TEXT_MID)
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(l)
	return row


static func _ignore_mouse(n: Node) -> void:
	if n is Control:
		(n as Control).mouse_filter = Control.MOUSE_FILTER_IGNORE
		(n as Control).focus_mode = Control.FOCUS_NONE
	for c in n.get_children():
		_ignore_mouse(c)


## The page's chrome rects (local, after layout): title, terminal, key (tests: on the page,
## apart).
func chrome_rects() -> Array[Rect2]:
	var out: Array[Rect2] = []
	for c: Control in [title_sticker, mechanic, key_strip]:
		if c != null:
			out.append(Rect2(c.global_position - global_position, c.size))
	return out


## The world point of node `id` (Vector3.INF when it has no slot).
func world_of(id: StringName) -> Vector3:
	return _points.get(id, Vector3.INF)


## The screen point (local) of node `id` (Vector2.INF when it has none).
func screen_of(id: StringName) -> Vector2:
	var w := world_of(id)
	return iso.project(w) if iso != null and w != Vector3.INF else Vector2.INF


## The entry's screen point (local).
func entry_screen() -> Vector2:
	return iso.project(_entry) if iso != null else Vector2.INF


## The sticker radius of node `id` (the Central Server's is the big one).
func node_radius(id: StringName) -> float:
	var big := graph != null and int(graph.get_node(id).get("layer", 0)) == graph.layer_count()
	return (RouteOverlay.STICKER_RADIUS_BIG if big else RouteOverlay.STICKER_RADIUS) * Settings.text_scale


## The state ring node `id` shows (RouteOverlay.STATE_*).
func state_of(id: StringName) -> String:
	if visited.has(id):
		return RouteOverlay.STATE_WALKED
	if available.has(id):
		return RouteOverlay.STATE_NEXT
	if current_id != &"" and graph != null and int(graph.get_node(id).get("layer", 0)) <= int(graph.get_node(current_id).get("layer", 0)):
		return RouteOverlay.STATE_CUT
	return RouteOverlay.STATE_LATER


## The links drawn: [{from, to, state}] where from/to are node ids (&"" = the entry) and state
## is "walked", "live" or "later"; in node-id order.
func links() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if graph == null:
		return out
	for id: StringName in graph.first_layer_ids():
		out.append({"from": &"", "to": id, "state": _link_state(&"", id)})
	var ids: Array[StringName] = []
	for n in graph.all_nodes():
		ids.append(n["id"])
	ids.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	for id in ids:
		var nexts: Array = graph.get_node(id).get("next", [])
		for to: StringName in nexts:
			out.append({"from": id, "to": to, "state": _link_state(id, to)})
	return out


func _link_state(from: StringName, to: StringName) -> String:
	var from_walked := from == &"" or visited.has(from)
	if from_walked and visited.has(to):
		return "walked"
	if from == current_id and available.has(to):
		return "live"
	return "later"


## The selectable node under local point `p` (&"" = none).
func node_at(p: Vector2) -> StringName:
	var best := &""
	var best_d := INF
	for id: StringName in available:
		var s := screen_of(id)
		if s == Vector2.INF:
			continue
		var d := s.distance_to(p)
		if d <= node_radius(id) + PICK_SLACK and d < best_d:
			best = id
			best_d = d
	return best


## The chip's rect (local) over the Central Server (Rect2() when there is none).
func chip_rect() -> Rect2:
	var id := _server_id()
	var at := screen_of(id) if id != &"" else Vector2.INF
	if at == Vector2.INF:
		return Rect2()
	var f := Palette.mono()
	var fs := maxi(1, roundi(CHIP_FONT * Settings.text_scale))
	var w := f.get_string_size(_chip_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var box := Vector2(w, f.get_height(fs)) + Vector2(CHIP_PAD, CHIP_PAD) * 2.0
	var rr := node_radius(id) * RouteOverlay.TARGET_SHARE
	var r := Rect2(Vector2(at.x - box.x * 0.5, at.y - rr * RouteOverlay.TARGET_SQUASH - CHIP_GAP - box.y), box)
	r.position.x = clampf(r.position.x, 0.0, maxf(0.0, size.x - box.x))
	if r.position.y < 0.0:
		# No room above (the server near the top edge): under the circle, still clear of it.
		r.position.y = at.y + rr * RouteOverlay.TARGET_SQUASH + CHIP_GAP
	return r


func _chip_text() -> String:
	return tr(CHIP_WORDS) % server_label


func _server_id() -> StringName:
	if graph == null or graph.layer_count() < 1:
		return &""
	var last: Array = graph.nodes_in_layer(graph.layer_count())
	return StringName(last[0]["id"]) if not last.is_empty() else &""


## The part of a page `sz` big the run's nodes and entry keep inside: FIT_MARGIN_PX in from
## the sides, TOP_ROOM under the HUD band, above the foot's terminal and key (as laid out;
## FOOT_RESERVE before the first layout).
func free_rect(sz: Vector2) -> Rect2:
	var top := top_inset + TOP_ROOM * Settings.text_scale
	var bottom := FOOT_RESERVE * Settings.text_scale + FIT_MARGIN_PX * 0.5
	if _foot_top > 0.0:
		bottom = sz.y - _foot_top + FIT_MARGIN_PX * 0.5
	return Rect2(FIT_MARGIN_PX, top, sz.x - FIT_MARGIN_PX * 2.0, maxf(sz.y - top - bottom, 1.0))


## The foot found its height (a text size, the page's size): the run is framed above it.
func _on_foot_laid_out() -> void:
	if _foot == null or not is_instance_valid(_foot) or _foot.size.y <= 0.0:
		return
	var top := _foot.global_position.y - global_position.y
	if absf(top - _foot_top) < 0.5:
		return
	_foot_top = top
	if not _manifest.is_empty():
		_frame()
	_marks.queue_redraw()


func _frame() -> void:
	var sz := size if size.x > 1.0 and size.y > 1.0 else Vector2(1920, 1080)
	var pts: Array[Vector3] = [_entry]
	for id: StringName in _points:
		pts.append(_points[id])
	iso = HqCompoundStage.run_camera(CityView3D.CONFIG, _manifest, _at, sz, pts, FIT_MARGIN_PX, FIT_MAX_SHARE, free_rect(sz))
	if city != null:
		city.set_view_size(Vector2i(sz))
		city.set_iso(iso)


func _mount_city() -> void:
	city = CityView3D.new()
	city.name = "HqCity"
	city.set_iso(iso)
	city.stage_compound(corp)
	add_child(city)
	city.set_view_size(Vector2i(size.max(Vector2(2, 2))))
	_city_rect.texture = city.get_texture()
	move_child(city, 0)


func _ready() -> void:
	Settings.changed.connect(_on_settings_changed)


## A new text size rebuilds the chrome at its scale.
func _on_settings_changed() -> void:
	if _chrome != null and not is_equal_approx(_built_scale, Settings.text_scale):
		_build_chrome()
		_frame()
		_marks.queue_redraw()


func _on_resized() -> void:
	if not _manifest.is_empty():
		_frame()
	_marks.queue_redraw()
	# The foot moves with the page's height without changing its own size.
	_on_foot_laid_out.call_deferred()


func _process(delta: float) -> void:
	if not is_visible_in_tree() or not Fx.effects_enabled():
		return
	anim_t += delta
	_marks.queue_redraw()


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and (event as InputEventMouseButton).pressed \
			and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
		var id := node_at((event as InputEventMouseButton).position)
		if id != &"":
			accept_event()
			node_pressed.emit(id)


func _get_tooltip(at_position: Vector2) -> String:
	var id := node_at(at_position)
	if id == &"":
		return ""
	return tr(CityMapOverlay.KIND_NAMES[CityMapOverlay.KIND_CENTRAL_SERVER]) if id == _server_id() else ""


# --- Drawing ----------------------------------------------------------------------------------

func _draw_marks() -> void:
	_target_spec = {}
	_lay_pencil.call_deferred()
	if iso == null or graph == null:
		return
	var k := Settings.text_scale
	var e := entry_screen()
	for l in links():
		var a := e if l["from"] == &"" else screen_of(l["from"])
		var b := screen_of(l["to"])
		if a == Vector2.INF or b == Vector2.INF:
			continue
		_link(a, b, String(l["state"]), k)
	if e != Vector2.INF:
		_entry_diamond(e, k)
	var server := _server_id()
	for n in graph.all_nodes():
		var id: StringName = n["id"]
		var at := screen_of(id)
		if at == Vector2.INF:
			continue
		var state := state_of(id)
		if state == RouteOverlay.STATE_CUT:
			_marks.draw_circle(at, node_radius(id) + CUT_BACKING_GROW * k, Color(Palette.PAPER, CUT_BACKING_ALPHA))
		RouteOverlay.draw_sticker(_marks, kind_of(id), at, node_radius(id), state, k)
	for id: StringName in available:
		if id != server and screen_of(id) != Vector2.INF:
			_tab(id, k)
	if server != &"" and screen_of(server) != Vector2.INF:
		_target(server, screen_of(server), node_radius(server), k)
		if not gate_open:
			_chip(k)
	var here := screen_of(current_id) if current_id != &"" else e
	if here != Vector2.INF:
		_here(here, node_radius(current_id) if current_id != &"" else ENTRY_RADIUS * 2.0 * k, k)


## The route kind node `id` shows (CityMapOverlay.KIND_*; the Central Server is the rack).
func kind_of(id: StringName) -> String:
	if id == _server_id():
		return CityMapOverlay.KIND_RACK
	var n := graph.get_node(id) if graph != null else {}
	if n.is_empty():
		return CityMapOverlay.KIND_FIGHT
	return CityMapOverlay.route_kind(int(n["type"]), bool(n["elite"]))


## The choice number of selectable node `id` (its place in `available`, as the ROUTE window's
## buttons number them; 0 = not numbered: not selectable, or the only choice).
func number_of(id: StringName) -> int:
	if available.size() < 2:
		return 0
	return available.find(id) + 1


## The name tab's words under selectable node `id`: its number (when there is a choice) and
## its kind (the route key's word).
func tab_text(id: StringName) -> String:
	var word := tr(String(RouteLegend.SHORT.get(kind_of(id), "")))
	var n := number_of(id)
	return "%d %s" % [n, word] if n > 0 else word


## The name tab's rect (local) under node `id`.
func tab_rect(id: StringName) -> Rect2:
	var at := screen_of(id)
	if at == Vector2.INF:
		return Rect2()
	var k := Settings.text_scale
	var f := Palette.mono()
	var fs := maxi(1, roundi(TAB_FONT * k))
	var box := Vector2(f.get_string_size(tab_text(id), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x, f.get_height(fs)) + TAB_PAD * 2.0 * k
	return Rect2(Vector2(at.x - box.x * 0.5, at.y + node_radius(id) + TAB_GAP * k), box)


## The concept's name tab (round 43: a small dark glass tab with a cyan edge, mono capitals).
func _tab(id: StringName, k: float) -> void:
	var r := tab_rect(id)
	var f := Palette.mono()
	var fs := maxi(1, roundi(TAB_FONT * k))
	_marks.draw_rect(r, Color(Palette.NIGHT_SKY, TAB_GLASS_ALPHA))
	_marks.draw_rect(r, PaletteSkins.chrome(Palette.NET_CYAN), false, TAB_BORDER * k)
	_marks.draw_string(f, r.position + Vector2(TAB_PAD.x * k, TAB_PAD.y * k + f.get_ascent(fs)), tab_text(id),
		HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.PAPER)


## The entry: the concept's lime diamond on the ground where the walked path starts.
func _entry_diamond(e: Vector2, k: float) -> void:
	var w := ENTRY_DIAMOND * k
	var h := w * ENTRY_SQUASH
	var pts := PackedVector2Array([e + Vector2(-w, 0), e + Vector2(0, -h), e + Vector2(w, 0), e + Vector2(0, h)])
	var ink := pts.duplicate()
	ink.append(pts[0])
	_marks.draw_polyline(ink, Color(RouteInk.KEYLINE, RouteInk.KEYLINE_ALPHA), RouteOverlay.KEYLINE_EXTRA * k * 2.0, true)
	_marks.draw_colored_polygon(pts, RouteInk.RING_WALKED)


func _link(a: Vector2, b: Vector2, state: String, k: float) -> void:
	match state:
		"walked":
			var w := RouteOverlay.CABLE_WALKED * k
			_marks.draw_line(a, b, Color(RouteInk.RING_WALKED, RouteOverlay.CABLE_GLOW_ALPHA), w * RouteOverlay.CABLE_GLOW_SHARE, true)
			_marks.draw_line(a, b, Color(RouteInk.KEYLINE, RouteInk.KEYLINE_ALPHA), w + RouteOverlay.KEYLINE_EXTRA * k, true)
			_marks.draw_line(a, b, RouteInk.RING_WALKED, w, true)
		"live":
			var speed := 0.0
			var me := Motion.entry(CityMapOverlay.CRAWL_MOTION)
			if me != null and Motion.live(CityMapOverlay.CRAWL_MOTION):
				speed = me.amplitude / maxf(me.duration, 0.001)
			_dashes(a, b, RouteInk.RING_AVAILABLE, RouteOverlay.CABLE_LIVE * k, 1.0, fmod(anim_t * speed, CityMapOverlay.DASH_PERIOD * k), true, k)
		_:
			_dashes(a, b, RouteInk.RING_UNAVAILABLE, RouteOverlay.CABLE_LATER * k, RouteOverlay.LATER_ALPHA, 0.0, false, k)


func _dashes(a: Vector2, b: Vector2, col: Color, width: float, alpha: float, phase: float, keyline: bool, k: float) -> void:
	var length := a.distance_to(b)
	if length <= 0.0:
		return
	var dir := (b - a) / length
	var on := CityMapOverlay.DASH_ON * k
	var period := CityMapOverlay.DASH_PERIOD * k
	var t := phase - period
	var n := 0
	while t < length and n < CityMapOverlay.DASHES_MAX:
		var t0 := maxf(t, 0.0)
		var t1 := minf(t + on, length)
		if t1 > t0:
			if keyline:
				_marks.draw_line(a + dir * t0, a + dir * t1, Color(RouteInk.KEYLINE, RouteInk.KEYLINE_ALPHA * alpha), width + RouteOverlay.KEYLINE_EXTRA * k)
			_marks.draw_line(a + dir * t0, a + dir * t1, Color(col, alpha), width)
		t += period
		n += 1


## The red grease-pencil TARGET circle and the word beside it, as the route's TARGET: the kit's
## wax (B1b, D3), noted while the marks draw and laid as marks after the draw (`_lay_pencil`).
func _target(id: StringName, at: Vector2, r: float, _k: float) -> void:
	var rr := r * RouteOverlay.TARGET_SHARE
	_target_spec = {"id": id, "at": at, "rr": rr, "seed": absi(hash(String(corp) + String(id)))}


## B1b: the TARGET noted in the last draw ({} for none) and the set that lays it.
var _target_spec: Dictionary = {}
var _pencil: PencilSet = null


## Lays the TARGET's loop and word in the kit's wax (they write on when they first show).
func _lay_pencil() -> void:
	if _pencil == null or not is_instance_valid(_pencil):
		return
	_pencil.begin()
	if not _target_spec.is_empty():
		var at: Vector2 = _target_spec["at"]
		var rr: float = _target_spec["rr"]
		var key := String(_target_spec["id"])
		_pencil.stroke("loop|" + key, RouteOverlay.target_loop(at, rr, int(_target_spec["seed"])), GreasePencilMark.Ink.THREAT,
			PencilSet.AUTO, 0.0, false, int(_target_spec["seed"]))
		var word := tr(RouteOverlay.TARGET_WORD)
		var wp := at + Vector2(rr * RouteOverlay.ROUTE_TARGET_WORD_AT.x, -rr * RouteOverlay.ROUTE_TARGET_WORD_AT.y * 0.2)
		var c := PencilSet.centre_of(wp, word, RouteOverlay.TARGET_FONT, 1.0, RouteOverlay.TARGET_WORD_TILT)
		_pencil.word("word|" + key, word, c, RouteOverlay.TARGET_FONT, GreasePencilMark.Ink.THREAT, 1.0, PencilSet.AUTO, 0.0,
			RouteOverlay.TARGET_WORD_TILT)
	_pencil.end()


## The TARGET's pencil (tests).
func target_pencil() -> PencilSet:
	return _pencil


func _chip(k: float) -> void:
	var r := chip_rect()
	if not r.has_area():
		return
	var f := Palette.mono()
	var fs := maxi(1, roundi(CHIP_FONT * k))
	_marks.draw_rect(r, Color(Palette.NIGHT_SKY, CHIP_GLASS_ALPHA))
	_marks.draw_rect(r, Palette.RESIST_GOLD, false, maxf(1.0, k))
	_marks.draw_string(f, r.position + Vector2(CHIP_PAD, CHIP_PAD + f.get_ascent(fs)), _chip_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.RESIST_GOLD)


## The operative pin over "you are here" (the route's pin).
func _here(at: Vector2, r: float, k: float) -> void:
	var side := r * RouteOverlay.PIN_SHARE
	var c := at + Vector2(r * RouteOverlay.PIN_OFFSET.x, r * RouteOverlay.PIN_OFFSET.y)
	_marks.draw_set_transform(c, RouteOverlay.PIN_TILT)
	# The concept's operative token (the route's, round 37 token_sd), die-cut as wide as the pin.
	var t := RouteOverlay.token_art()
	var w := side + (RouteOverlay.DIE_CUT_WIDTH * k + k) * 2.0
	var sz := Vector2(t.get_width(), t.get_height()) * (w / maxf(1.0, t.get_width()))
	_marks.draw_texture_rect(t, Rect2(-sz * 0.5, sz), false)
	_marks.draw_set_transform(Vector2.ZERO, 0.0)
	_marks.draw_line(c + Vector2(-side * 0.2, side * 0.45), at + Vector2(r * 0.35, -r * 0.7), Color(RouteInk.KEYLINE, RouteInk.KEYLINE_ALPHA), 2.0 * k)
