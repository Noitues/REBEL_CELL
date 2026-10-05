class_name SiteMarkerLayer
extends Control
## ART-5 5d: the City Grid's Site markers v4 as UI over the unified 3D city (5a's
## CityView3D, drawn by a host control the same size as its viewport): one SiteMarkerView
## per shown Site placed through the GridMarkerProjection seam and SiteMarkerLayout (apart,
## front to back), their labels placed clear of every marker, and picking. Re-placed when
## the view's camera or zoom band changes. The hidden-nodes rule holds (`show_all`, the
## key's SHOW ALL). Emits `site_clicked` and `site_hovered`; it never changes game state.

signal site_clicked(id: StringName)
signal site_hovered(id: StringName)

## Label pill padding and gap (px at text scale 1.0); label priority for the selected Site.
const LABEL_PAD := 3.0
const PRIO_SELECTED := 0
const PRIO_PINNED := 1
const PRIO_REST := 2

var projection: GridMarkerProjection = null
## Site id -> SiteMarker spec.
var specs: Dictionary = {}
## Site id -> label text ("" = none).
var labels: Dictionary = {}
var selected_id: StringName = &"":
	set(v):
		selected_id = v
		replace()
var show_all: bool = false:
	set(v):
		if v != show_all:
			show_all = v
			replace()
## The last placement: Site id -> disc centre, and id -> label rect (px, this control).
var discs: Dictionary = {}
var label_rects: Dictionary = {}
var _views: Dictionary = {}
var _hover: StringName = &""


func _init() -> void:
	name = "SiteMarkerLayer"
	mouse_filter = Control.MOUSE_FILTER_PASS
	resized.connect(replace)
	Settings.changed.connect(replace)


## Shows markers `p_specs` (and `p_labels`) through `p_projection`; follows its view's
## camera and band when it has one.
func attach(p_projection: GridMarkerProjection, p_specs: Dictionary, p_labels: Dictionary = {}) -> void:
	projection = p_projection
	specs = p_specs.duplicate()
	labels = p_labels.duplicate()
	var v := projection.view if projection != null else null
	if v != null:
		if not v.camera_changed.is_connected(_on_camera):
			v.camera_changed.connect(_on_camera)
		if not v.band_changed.is_connected(_on_band):
			v.band_changed.connect(_on_band)
	replace()


func _on_camera(_cam: CityIsoCamera) -> void:
	replace()


func _on_band(_band: int) -> void:
	replace()


## True when Site `id` shows now (pinned, SHOW ALL, selected or pointed at).
func is_shown(id: StringName) -> bool:
	var s: Dictionary = specs.get(id, {})
	return not s.is_empty() and (show_all or bool(s.get("pinned", true)) or id == selected_id or id == _hover)


## Places the markers and labels for the camera now (pure layout, then the views follow).
func replace() -> void:
	if projection == null:
		return
	if projection.view != null:
		projection.camera = projection.view.iso
	var all := projection.anchors()
	var anchors := {}
	var shown := {}
	for id in all:
		if is_shown(id):
			anchors[id] = all[id]
			shown[id] = specs[id]
	discs = SiteMarkerLayout.place_discs(anchors, shown, 1.0)
	var sizes := {}
	var prio := {}
	var f := Palette.mono()
	var fs := UiTheme.font_px(UiTheme.CAPTION)
	for id in discs:
		var text := String(labels.get(id, ""))
		if text == "":
			continue
		sizes[id] = Vector2(f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x, f.get_height(fs)) + Vector2(LABEL_PAD, LABEL_PAD) * 2.0 * Settings.text_scale
		prio[id] = PRIO_SELECTED if id == selected_id else (PRIO_PINNED if bool(specs[id].get("pinned", true)) else PRIO_REST)
	# No label on grease pencil: the boss's TARGET circle is a blocked area.
	var blocked: Array[Rect2] = []
	for id in discs:
		if specs[id].get("kind") == SiteMarker.KIND_CENTRAL_SERVER:
			var t := Vector2(CityMapOverlay.TARGET_RADIUS, CityMapOverlay.TARGET_RADIUS * CityMapOverlay.TARGET_FLAT) + Vector2.ONE * CityMapOverlay.TARGET_WIDTH
			blocked.append(Rect2(discs[id] + Vector2(0, SiteMarker.PAD_DROP) - t, t * 2.0))
	label_rects = SiteMarkerLayout.place_labels(discs, shown, sizes, prio, Rect2(Vector2.ZERO, size), blocked)
	for id in discs:
		var v: SiteMarkerView = _views.get(id)
		if v == null or not is_instance_valid(v):
			v = SiteMarkerView.new(specs[id])
			v.name = "Marker_%s" % id
			add_child(v)
			_views[id] = v
		elif str(v.spec) != str(specs[id]):
			v.set_spec(specs[id])
		v.position = discs[id]
	for id in _views.keys():
		if not discs.has(id):
			(_views[id] as Node).queue_free()
			_views.erase(id)
	_place_target()
	queue_redraw()


## The boss's red pencil TARGET round its anchor (no UI on pencil: it is the last child).
func _place_target() -> void:
	var boss: StringName = &""
	for id in discs:
		if specs[id].get("kind") == SiteMarker.KIND_CENTRAL_SERVER:
			boss = id
	if boss == &"":
		if target != null:
			target.queue_free()
			target = null
		return
	if target == null:
		target = GreasePencilMark.new()
		target.name = "Target"
		target.ink = GreasePencilMark.Ink.THREAT
		target.width = CityMapOverlay.TARGET_WIDTH
		target.seed = CityMapOverlay.TARGET_SEED
		target.add_stroke(PencilShapes.hand_circle(Vector2.ZERO, Vector2(CityMapOverlay.TARGET_RADIUS, CityMapOverlay.TARGET_RADIUS * CityMapOverlay.TARGET_FLAT), CityMapOverlay.TARGET_SEED))
		add_child(target)
	move_child(target, get_child_count() - 1)
	target.position = discs[boss] + Vector2(0, SiteMarker.PAD_DROP)


## The boss's pencil TARGET (null without a boss on the map).
var target: GreasePencilMark = null


## The marker view of Site `id` (null when hidden).
func view_of(id: StringName) -> SiteMarkerView:
	var v: Variant = _views.get(id)
	return v if v != null and is_instance_valid(v) else null


func _draw() -> void:
	var f := Palette.mono()
	var fs := UiTheme.font_px(UiTheme.CAPTION)
	var pad := LABEL_PAD * Settings.text_scale
	for id in label_rects:
		var r: Rect2 = label_rects[id]
		draw_rect(r, Color(Palette.NIGHT_SKY, 0.86))
		draw_rect(Rect2(r.position, Vector2(maxf(1.0, pad * 0.6), r.size.y)), SiteMarker.ring_color(specs[id]))
		draw_string(f, r.position + Vector2(pad, pad + f.get_ascent(fs)), String(labels[id]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.TEXT_HI)


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		var id := SiteMarkerLayout.pick(discs, specs, (event as InputEventMouseMotion).position)
		if id != _hover:
			_hover = id
			site_hovered.emit(id)
	elif event is InputEventMouseButton and event.pressed and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
		var id := SiteMarkerLayout.pick(discs, specs, (event as InputEventMouseButton).position)
		if id != &"":
			site_clicked.emit(id)
			accept_event()
