class_name UiScrimPools
extends Control
## B1a (M14 integration review D1, section d "World darkening under the UI"; ART_BIBLE v2 §3.1,
## §4.1): the one layer between the world (the 3D city, a backdrop still, the 2D city) and the UI
## that darkens the world under the UI. The concepts drop the city round the wheels, the hand and
## the panels and lay darker bands under the bars; this layer does it for every screen over the
## city: pools round the registered wheels (`wheel_pool_multiply` held out to `wheel_pool_reach` x
## the disc radius, fading over `wheel_pool_fade` x it) and panels (`panel_pool_multiply`, held over
## `panel_pool_hold` of `panel_pool_margin_px` past the edge, then fading), desaturated toward their
## luma by `pool_saturation` (D1: 0.6), and bands under the registered bars (`band_multiply`, held
## over `band_hold` of `band_reach_top_px` / `band_reach_bottom_px`). Numbers: `content/config/
## ui_scrim_look.tres` (UiScrimLook). Its child `spill` (UiSpillShadows) draws the panels' drop
## shadows and the emissive elements' light spill on the same world, above the pools.
##
## The network stays at full strength (bible §4.1; designer ruling on B1a's Q1, 2026-10-06):
## - Anything of the world in LIFT_GROUP (a map's CityMapOverlay: markers, icons, labels, the
##   flow, the pencil and TARGET; the HQ run's marks and chrome) is drawn over this layer: the
##   world siblings before the layer sink to WORLD_Z, the layer to SCRIM_Z and the lifted item
##   draws at its host's own z (still under every UI sibling after the layer, by tree order).
## - A map on the 3D city draws its links and node discs as the city's ground decal: the shader
##   keeps them out of the pools and bands (`keep_network`, NETWORK_GROUP: the same segments and
##   nodes, mapped from this layer's px to the ground plane of the ortho map camera).
##
## How a screen uses it (the API other screens use; DECISIONS "B1a"):
##   var scrim := UiScrimPools.attach_after(background)   # right after the world node
##   scrim.add_wheels(_views)                              # combat: () -> Array of WheelViews
##   UiScrimPools.mark_panel(site_card)                    # pool + drop shadow under a panel
##   UiScrimPools.mark_panel(sheet, false)                 # drop shadow only (no pool)
##   UiScrimPools.mark_band(hud, SIDE_TOP)                 # a dark band under a bar
##   UiSpillShadows.mark_spill(jack_in, Palette.CELL_PINK) # an emissive element lights the city
##   node.add_to_group(UiScrimPools.LIFT_GROUP)            # a world item drawn over the scrim
## Marks live on the Control (groups + metas), so a page marks its parts where it builds them,
## without holding the layer; a mark is taken by the nearest layer whose host (its parent) holds
## the Control and that draws before it (a fight inside a netrun page belongs to the fight's own
## layer, not the run's). Each frame the layer reads the rects of the visible marked Controls
## (bounding boxes in its own space, any CanvasLayer), so pages that move, scroll, slide in or hide
## need nothing more; a freed Control simply drops out.
##
## Cost: one full-screen quad that reads the world drawn so far (a BackBufferCopy just before it,
## so an earlier screen reader's stale copy is never read; the pixels outside every shape are
## discarded), its uniforms set only when a rect moves; hidden while nothing is registered. A
## second BackBufferCopy after the layer hands every later screen reader (glass blur, the heat
## glitch) the pooled world. Static: nothing animates, so reduce effects and
## MotionSkip have nothing to stop (its end state is its only state); VfxTier T0 (backdrop
## coverage, no flash). City quality tier 0 keeps the pools (they carry the UI's contrast) and drops
## the spill and the shadows (UiScrimLook tier flags). View only: it never changes a Control it
## reads, nor any state (it sets only draw order: z_index of the world items it lifts).

const LOOK: UiScrimLook = preload("res://content/config/ui_scrim_look.tres")
const SHADER := preload("res://shaders/kit/ui_scrim_pools.gdshader")
## Shapes the shader takes (its MAX_SHAPES).
const MAX_SHAPES := 32
const NODE_NAME := "UiScrimPools"
## Marks (groups on the marked Controls) and their metas.
const PANEL_GROUP := &"ui_scrim_panel"
const BAND_GROUP := &"ui_scrim_band"
const META_POOL := &"ui_scrim_pool"
const META_SHADOW := &"ui_scrim_shadow"
const META_SIDE := &"ui_scrim_side"
## World items drawn over the layer, and the maps whose ground decal network it keeps.
const LIFT_GROUP := &"ui_scrim_lift"
const NETWORK_GROUP := &"ui_scrim_network"
## The meta on a layer's host naming its layer (instance id), and on a lifted item.
const HOST_META := &"ui_scrim_host"
const LIFT_META := &"ui_scrim_lifted"
## Draw order while something is lifted (relative to the host): the world under the layer.
const WORLD_Z := -2
const SCRIM_Z := -1
## Rec. 709 luma weights (the shader's desaturation; the luma probes').
const LUMA := Vector3(0.2126, 0.7152, 0.0722)

## Shape kinds (the shader's params.x).
enum Kind { DISC, RECT, BAND }

## The light spill and panel shadows over the pools.
var spill: UiSpillShadows
## The shapes this frame, in this layer's own px: [{kind, centre, half, hold, end, removal}]
## (`hold`: the distance the shape holds full darkness to, from a disc's centre or past a rect's
## edge; `end`: where it has faded out).
var shapes: Array[Dictionary] = []
## The network kept out of the pools this frame ({} = none; see keep_from).
var keep: Dictionary = {}
## The world items this layer lifted (tests).
var lifted: Array[CanvasItem] = []
## Dev probes only (tools/visual_qa/perf_pack.gd scrim_luma): keep this frame's shapes while the
## probe hides the UI to measure the world under it.
var hold_shapes: bool = false
## Dev probes only (perf_pack scrim_probe_*): the network keep's cost is measured by turning it off.
var keep_enabled: bool = true

## B4 (review D7, round 44 `hq_idle`): the map dim this frame, in this layer's px ({} = off):
## {rect: Rect2 (the network's fit rect, grown by the look's margin), focus: Vector2 (the
## selected Site's centre; INF = none), plus the look's numbers in px: feather, hold, end}.
var map_dim: Dictionary = {}
## B4: the page's map dim source: () -> {rect: Rect2, focus: Vector2} in global canvas px, or {}
## (off). Set by a page that shows a map at rest (the HQ idle); cleared by `set_map_dim_source`
## with an empty Callable.
var _dim_source: Callable = Callable()

var _quad: ColorRect
var _mat: ShaderMaterial
var _copy: BackBufferCopy
var _before: BackBufferCopy
var _wheel_sources: Array[Callable] = []
var _sig: int = 0
var _keep_net: CityNetworkData = null
var _keep_sig: int = 0


func _init() -> void:
	name = NODE_NAME
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_mat = ShaderMaterial.new()
	_mat.shader = SHADER
	_mat.set_shader_parameter(&"pool_saturation", LOOK.pool_saturation)
	# The world as drawn up to here (an earlier screen reader, a light spill in the backdrop's Heat
	# lights, may have taken the screen before the world was whole).
	_before = BackBufferCopy.new()
	_before.name = "BeforeScrim"
	_before.copy_mode = BackBufferCopy.COPY_MODE_VIEWPORT
	add_child(_before)
	_quad = ColorRect.new()
	_quad.name = "Pools"
	_quad.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_quad.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_quad.material = _mat
	_quad.visible = false
	add_child(_quad)
	spill = UiSpillShadows.new()
	add_child(spill)
	_copy = BackBufferCopy.new()
	_copy.name = "AfterScrim"
	_copy.copy_mode = BackBufferCopy.COPY_MODE_VIEWPORT
	add_child(_copy)


func _enter_tree() -> void:
	get_parent().set_meta(HOST_META, get_instance_id())


func _exit_tree() -> void:
	var host := get_parent()
	if host != null and host.has_meta(HOST_META) and int(host.get_meta(HOST_META)) == get_instance_id():
		host.remove_meta(HOST_META)


## Makes a layer and puts it right after `world` (same parent: drawn over the world, under every
## UI sibling after it). Returns it.
static func attach_after(world: Node) -> UiScrimPools:
	var s := UiScrimPools.new()
	var host := world.get_parent()
	host.add_child(s)
	host.move_child(s, world.get_index() + 1)
	return s


## Registers the wheels `source` returns (() -> Array of WheelViews, or anything with
## `global_center()` and `disc_radius()` in its canvas' global px); each visible one with a
## combatant gets a pool.
func add_wheels(source: Callable) -> void:
	if source.is_valid() and not _wheel_sources.has(source):
		_wheel_sources.append(source)


## Marks `c` as a panel over the world: a pool under it (`pool`) and a drop shadow (`shadow`).
static func mark_panel(c: Control, pool: bool = true, shadow: bool = true) -> void:
	c.set_meta(META_POOL, pool)
	c.set_meta(META_SHADOW, shadow)
	c.add_to_group(PANEL_GROUP)


## Marks `c` as a bar with a dark band under it, reaching to the screen's `side` edge
## (SIDE_TOP or SIDE_BOTTOM).
static func mark_band(c: Control, side: Side) -> void:
	c.set_meta(META_SIDE, side)
	c.add_to_group(BAND_GROUP)


## Marks every Control under `root` (itself included) that is one of `classes` (class names) as a
## panel (see mark_panel), the outermost only: a window inside a marked window is not marked
## again. For a page built of shared windows: one line marks them all.
static func mark_panels_in(root: Node, classes: Array[String], pool: bool = true, shadow: bool = true) -> void:
	var found: Array[Node] = []
	for cls in classes:
		if root is Control and _is_class(root, cls):
			found.append(root)
		found.append_array(root.find_children("*", cls, true, false))
	for n in found:
		var nested := false
		for m in found:
			if m != n and m.is_ancestor_of(n):
				nested = true
				break
		if not nested and n is Control:
			mark_panel(n as Control, pool, shadow)


static func _is_class(n: Node, cls: String) -> bool:
	if n.is_class(cls):
		return true
	var s := n.get_script() as Script
	while s != null:
		if s.get_global_name() == StringName(cls):
			return true
		s = s.get_base_script()
	return false


## Takes every mark off `c`.
static func unmark(c: Control) -> void:
	for g in [PANEL_GROUP, BAND_GROUP, UiSpillShadows.SPILL_GROUP]:
		if c.is_in_group(g):
			c.remove_from_group(g)


## The layer whose host is the nearest layer host above `n` (null: none).
static func layer_of(n: Node) -> UiScrimPools:
	var p := n.get_parent()
	while p != null:
		if p.has_meta(HOST_META):
			return instance_from_id(int(p.get_meta(HOST_META))) as UiScrimPools
		p = p.get_parent()
	return null


## True when this layer takes `n`'s mark: `n` is shown, draws after this layer (later in the tree,
## or a world item it lifted), and this layer's host is the nearest layer host above it.
func owns(n: Node) -> bool:
	if not is_inside_tree() or not n.is_inside_tree() or n == self:
		return false
	if n is CanvasItem and not (n as CanvasItem).is_visible_in_tree():
		return false
	if not n.is_greater_than(self) and not is_lifted(n):
		return false
	return layer_of(n) == self


## True when `n` or an ancestor of it is a world item this layer lifted.
func is_lifted(n: Node) -> bool:
	var p := n
	while p != null:
		if p.has_meta(LIFT_META) and int(p.get_meta(LIFT_META)) == get_instance_id():
			return true
		p = p.get_parent()
	return false


## True when `n` is part of this layer's world: under a sibling drawn before it, this layer the
## nearest.
func in_world(n: Node) -> bool:
	return is_inside_tree() and n.is_inside_tree() and get_parent().is_ancestor_of(n) and not n.is_greater_than(self) \
		and layer_of(n) == self


## The marked Controls this layer takes in `group`, in tree order.
func owned(group: StringName) -> Array[Control]:
	var out: Array[Control] = []
	if not is_inside_tree():
		return out
	for n in get_tree().get_nodes_in_group(group):
		if n is Control and owns(n):
			out.append(n as Control)
	return out


## `c`'s rect in this layer's own px (its bounding box: a tilted sticker's whole reach).
func local_rect(c: Control) -> Rect2:
	var xf := get_global_transform_with_canvas().affine_inverse() * c.get_global_transform_with_canvas()
	return xf * Rect2(Vector2.ZERO, c.size)


## px at the look's reference height -> this layer's px.
func px(length: float) -> float:
	return length * size.y / maxf(LOOK.reference_height, 1.0)


func _process(_delta: float) -> void:
	refresh()


## Reads the registered rects now and updates the shader (each frame; tests call it directly).
func refresh() -> void:
	_lift_world()
	if not hold_shapes:
		shapes = shapes_for(sources())
	_sync_keep()
	_sync_dim()
	var on := not shapes.is_empty() or not map_dim.is_empty()
	var sig := hash([shapes, map_dim])
	if sig == _sig and _quad.visible == on:
		return
	_sig = sig
	_quad.visible = on
	# No pools: no screen copies either (a later reader takes its own, as without the layer).
	_before.visible = _quad.visible
	_copy.visible = _quad.visible
	var rects := PackedVector4Array()
	var params := PackedVector4Array()
	rects.resize(MAX_SHAPES)
	params.resize(MAX_SHAPES)
	for i in shapes.size():
		var s: Dictionary = shapes[i]
		var c: Vector2 = s["centre"]
		var h: Vector2 = s["half"]
		rects[i] = Vector4(c.x, c.y, h.x, h.y)
		params[i] = Vector4(float(s["kind"]), float(s["hold"]), float(s["end"]), float(s["removal"]))
	_mat.set_shader_parameter(&"count", shapes.size())
	_mat.set_shader_parameter(&"shape_rect", rects)
	_mat.set_shader_parameter(&"shape_params", params)
	_mat.set_shader_parameter(&"dim_on", not map_dim.is_empty())
	if not map_dim.is_empty():
		var r: Rect2 = map_dim["rect"]
		var f: Vector2 = map_dim["focus"]
		_mat.set_shader_parameter(&"dim_rect", Vector4(r.get_center().x, r.get_center().y, r.size.x * 0.5, r.size.y * 0.5))
		_mat.set_shader_parameter(&"dim_in", 1.0 - LOOK.map_dim_inside)
		_mat.set_shader_parameter(&"dim_out", 1.0 - LOOK.map_dim_outside)
		_mat.set_shader_parameter(&"dim_sat", LOOK.map_dim_saturation)
		_mat.set_shader_parameter(&"dim_feather", float(map_dim["feather"]))
		_mat.set_shader_parameter(&"dim_focus", Vector4(f.x, f.y, float(map_dim["hold"]), float(map_dim["end"])) if f.is_finite() \
			else Vector4(0.0, 0.0, -1.0, 0.0))


## B4 (review D7): the page's map dim (see `map_dim`): `source` () -> {rect, focus} in global
## canvas px, or {} while the page shows no map at rest. An empty Callable turns it off.
func set_map_dim_source(source: Callable) -> void:
	_dim_source = source


## B4: reads the map dim source into this layer's px (the look's lengths scaled to its height).
func _sync_dim() -> void:
	map_dim = {}
	if not _dim_source.is_valid() or not is_inside_tree():
		return
	var src: Dictionary = _dim_source.call()
	if src.is_empty() or not (src.get("rect", Rect2()) as Rect2).has_area():
		return
	var inv := get_global_transform_with_canvas().affine_inverse()
	var r: Rect2 = inv * (src["rect"] as Rect2)
	var f: Vector2 = src.get("focus", Vector2.INF)
	map_dim = {"rect": r.grow(px(LOOK.map_dim_margin_px)), "focus": inv * f if f.is_finite() else Vector2.INF,
		"feather": px(LOOK.map_dim_feather_px), "hold": px(LOOK.map_focus_hold_px), "end": px(LOOK.map_focus_end_px)}


## B4: the map dim's [removal, desaturation share] at `p` (this layer's px) for `dim` (`map_dim`),
## as the shader computes it ([0, 0] when off).
static func dim_at(dim: Dictionary, p: Vector2) -> Vector2:
	if dim.is_empty():
		return Vector2.ZERO
	var r: Rect2 = dim["rect"]
	var outside := smoothstep(0.0, maxf(float(dim["feather"]), 0.001), maxf(sd_box(p - r.get_center(), r.size * 0.5, 0.0), 0.0))
	var f: Vector2 = dim["focus"]
	var lit := 0.0
	if f.is_finite():
		lit = 1.0 - smoothstep(float(dim["hold"]), maxf(float(dim["end"]), float(dim["hold"]) + 0.001), p.distance_to(f))
	return Vector2(lerpf(1.0 - LOOK.map_dim_inside, 1.0 - LOOK.map_dim_outside, outside) * (1.0 - lit), outside * (1.0 - lit))


## What the registered parts are this frame, in this layer's own px: {size, scale (px per px at
## the look's reference height), wheels: [{centre, radius}], panels: [Rect2] (pooled ones),
## bands: [{rect, top}]}. The probes and the fixture tests rebuild the shapes from it.
func sources() -> Dictionary:
	var wheels: Array[Dictionary] = []
	var panels: Array[Rect2] = []
	var bands: Array[Dictionary] = []
	var out := {"size": size, "scale": size.y / maxf(LOOK.reference_height, 1.0), "wheels": wheels, "panels": panels, "bands": bands}
	if not is_inside_tree():
		return out
	var inv := get_global_transform_with_canvas().affine_inverse()
	for source in _wheel_sources:
		if not source.is_valid():
			continue
		for v in source.call():
			if not (v is CanvasItem) or not is_instance_valid(v) or not (v as CanvasItem).is_visible_in_tree():
				continue
			if "combatant" in v and v.combatant == null:
				continue
			var xf := inv * (v as CanvasItem).get_canvas_transform()
			wheels.append({"centre": xf * (v.global_center() as Vector2), "radius": float(v.disc_radius()) * xf.get_scale().x})
	for c in owned(PANEL_GROUP):
		if bool(c.get_meta(META_POOL, true)):
			panels.append(local_rect(c))
	for c in owned(BAND_GROUP):
		bands.append({"rect": local_rect(c), "top": int(c.get_meta(META_SIDE, SIDE_TOP)) == SIDE_TOP})
	return out


## The shapes for `src` (see `sources`) with the look's numbers (at most MAX_SHAPES).
static func shapes_for(src: Dictionary) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var sz: Vector2 = src.get("size", Vector2.ZERO)
	var k := float(src.get("scale", 1.0))
	for w: Dictionary in src.get("wheels", []):
		var r := float(w["radius"])
		var hold := r * LOOK.wheel_pool_reach
		out.append(_shape(Kind.DISC, w["centre"], Vector2.ZERO, hold, hold + r * LOOK.wheel_pool_fade, 1.0 - LOOK.wheel_pool_multiply))
	for r: Rect2 in src.get("panels", []):
		var m := LOOK.panel_pool_margin_px * k
		out.append(_shape(Kind.RECT, r.get_center(), r.size * 0.5, m * LOOK.panel_pool_hold, m, 1.0 - LOOK.panel_pool_multiply))
	for b: Dictionary in src.get("bands", []):
		var r: Rect2 = b["rect"]
		var top := bool(b["top"])
		var y0 := minf(0.0, r.position.y) if top else r.position.y
		var y1 := r.end.y if top else maxf(sz.y, r.end.y)
		var reach := (LOOK.band_reach_top_px if top else LOOK.band_reach_bottom_px) * k
		# Full width and past the sides, so only its inner edge fades.
		out.append(_shape(Kind.BAND, Vector2(sz.x * 0.5, (y0 + y1) * 0.5), Vector2(sz.x * 0.5 + reach * 2.0, (y1 - y0) * 0.5),
			reach * LOOK.band_hold, reach, 1.0 - LOOK.band_multiply))
	if out.size() > MAX_SHAPES:
		out.resize(MAX_SHAPES)
	return out


static func _shape(kind: Kind, centre: Vector2, half: Vector2, hold: float, end: float, removal: float) -> Dictionary:
	return {"kind": kind, "centre": centre, "half": half, "hold": maxf(hold, 0.0), "end": maxf(end, hold + 0.001),
		"removal": clampf(removal, 0.0, 1.0)}


## The masks at `p` (px) for `list` (shapes): x = the pools' removal, y = the bands', z = the
## pools' desaturation share (0..1), as the shader computes them.
static func masks_at(list: Array[Dictionary], p: Vector2) -> Vector3:
	var pool := 0.0
	var band := 0.0
	var sat := 0.0
	for s in list:
		var d: float
		if int(s["kind"]) == Kind.DISC:
			d = (p - (s["centre"] as Vector2)).length()
		else:
			d = maxf(sd_box(p - (s["centre"] as Vector2), s["half"], 0.0), 0.0)
		var m := 1.0 - smoothstep(float(s["hold"]), float(s["end"]), d)
		if int(s["kind"]) == Kind.BAND:
			band = maxf(band, float(s["removal"]) * m)
		else:
			pool = maxf(pool, float(s["removal"]) * m)
			sat = maxf(sat, m)
	return Vector3(pool, band, sat)


## World colour `c` (encoded, as the screen holds it) at `p` once `list`'s pools and bands lie
## over it (the shader's maths; `keep_share` 0..1 of it kept as a network pixel).
static func apply_shapes(list: Array[Dictionary], p: Vector2, c: Color, keep_share: float = 0.0) -> Color:
	var m := masks_at(list, p) * (1.0 - keep_share)
	var l := Vector3(c.r, c.g, c.b).dot(LUMA)
	var s := lerpf(1.0, LOOK.pool_saturation, m.z)
	var f := (1.0 - m.x) * (1.0 - m.y)
	return Color((l + (c.r - l) * s) * f, (l + (c.g - l) * s) * f, (l + (c.b - l) * s) * f, c.a)


## World colour `c` at `p` (this layer's px) once the layer lies over it (with its network kept).
func apply_at(p: Vector2, c: Color) -> Color:
	var k := keep_at(p, keep)
	var d := dim_at(map_dim, p)  # B4: the dim lies over the network too (the shader's perf rule)
	if d == Vector2.ZERO:
		return apply_shapes(shapes, p, c, k)
	# B4: the map dim as the shader does it: one saturation (the pools' times the dim's), then
	# every multiply.
	var m := masks_at(shapes, p) * (1.0 - k)
	var l := Vector3(c.r, c.g, c.b).dot(LUMA)
	var s := lerpf(1.0, LOOK.pool_saturation, m.z) * lerpf(1.0, LOOK.map_dim_saturation, d.y)
	var f := (1.0 - m.x) * (1.0 - m.y) * (1.0 - d.x)
	return Color((l + (c.r - l) * s) * f, (l + (c.g - l) * s) * f, (l + (c.b - l) * s) * f, c.a)


## What the layer leaves of the world's brightness at `p` (pools and bands, no desaturation;
## 1.0 where nothing is registered).
func factor_at(p: Vector2) -> float:
	var k := keep_at(p, keep)
	var m := masks_at(shapes, p) * (1.0 - k)
	return (1.0 - m.x) * (1.0 - m.y) * (1.0 - dim_at(map_dim, p).x)


## What a wheel's pool leaves of the world `d` disc radii from its centre (the look's numbers;
## the combat contrast checks read it).
static func wheel_factor(d: float) -> float:
	var m := 1.0 - smoothstep(LOOK.wheel_pool_reach, LOOK.wheel_pool_reach + LOOK.wheel_pool_fade, d)
	return 1.0 - (1.0 - LOOK.wheel_pool_multiply) * m


## The signed distance from `p` to a rounded box of half size `b` and corner `r` (the shaders').
static func sd_box(p: Vector2, b: Vector2, r: float) -> float:
	var q := p.abs() - b + Vector2(r, r)
	return Vector2(maxf(q.x, 0.0), maxf(q.y, 0.0)).length() + minf(maxf(q.x, q.y), 0.0) - r


# --- The network over the layer --------------------------------------------------------------

## Lifts this layer's world items in LIFT_GROUP over it (once each) and sinks the world under it.
func _lift_world() -> void:
	if not is_inside_tree():
		return
	for i in range(lifted.size() - 1, -1, -1):
		if not is_instance_valid(lifted[i]):
			lifted.remove_at(i)
	for n in get_tree().get_nodes_in_group(LIFT_GROUP):
		var ci := n as CanvasItem
		if ci == null or lifted.has(ci) or not in_world(ci):
			continue
		_sink_world()
		ci.z_as_relative = false
		ci.z_index = _host_z()
		ci.set_meta(LIFT_META, get_instance_id())
		lifted.append(ci)


func _sink_world() -> void:
	if z_index == SCRIM_Z:
		return
	z_index = SCRIM_Z
	for sib in get_parent().get_children():
		if sib == self:
			break
		var ci := sib as CanvasItem
		if ci != null and ci.z_as_relative and ci.z_index == 0:
			ci.z_index = WORLD_Z


## The draw z of this layer's host (its own z and its ancestors' while relative).
func _host_z() -> int:
	var z := 0
	var p := get_parent() as CanvasItem
	while p != null:
		z += p.z_index
		if not p.z_as_relative:
			break
		p = p.get_parent() as CanvasItem
	return z


## Keeps the ground-decal network of this layer's map (NETWORK_GROUP: a CityMapOverlay on the 3D
## city, ortho) out of the pools and bands.
func _sync_keep() -> void:
	keep = {}
	var ov := _network_map() if keep_enabled else null
	if ov != null:
		var v3: CityView3D = ov.city.view3d
		var net: CityNetworkData = ov.fed_network()
		if net != null and v3.iso != null and not v3.iso.perspective():
			var cfg := CityView3D.CONFIG
			var to_world := func(p: Vector2) -> Vector2:
				var canvas := get_global_transform_with_canvas() * p
				var local: Vector2 = ov.city.get_global_transform_with_canvas().affine_inverse() * canvas
				var cover: Rect2 = ov.city.cover_rect()
				var view := (local - cover.position) / cover.size * v3.iso.viewport
				var w := v3.unproject(view, cfg.lane_stroke_bu)
				return Vector2(w.x, w.z)
			var span := maxf(size.x, 1.0)
			var o: Vector2 = to_world.call(Vector2.ZERO)
			var ax: Vector2 = (to_world.call(Vector2(span, 0.0)) - o) / span
			var ay: Vector2 = (to_world.call(Vector2(0.0, span)) - o) / span
			var mgmt := 1.0 - CityLod.city_share(cfg, CityView3D.view_lod(cfg, v3.iso.ortho, v3.band_lock))
			keep = keep_from(net, o, ax, ay, v3.iso.bu_per_px(), mgmt)
			if net != _keep_net:
				_keep_net = net
				_mat.set_shader_parameter(&"keep_nodes", ImageTexture.create_from_image(net.node_image(cfg.net_nodes_max)))
				_mat.set_shader_parameter(&"keep_segs", ImageTexture.create_from_image(net.segment_image(cfg.net_points_max)))
				_mat.set_shader_parameter(&"keep_node_count", mini(net.nodes.size(), cfg.net_nodes_max))
				_mat.set_shader_parameter(&"keep_seg_count", mini(net.segments.size(), cfg.net_points_max))
				_mat.set_shader_parameter(&"keep_trace_px", cfg.net_trace_px)
				_mat.set_shader_parameter(&"keep_node_px", cfg.net_node_px)
				_mat.set_shader_parameter(&"keep_bus_gap_px", cfg.net_bus_gap_px)
				_mat.set_shader_parameter(&"keep_edge_px", cfg.net_keep_edge_px)
	var sig := hash([keep.get("o"), keep.get("x"), keep.get("y"), keep.get("bu"), keep.get("mgmt")])
	if sig == _keep_sig:
		return
	_keep_sig = sig
	_mat.set_shader_parameter(&"keep_on", not keep.is_empty())
	if not keep.is_empty():
		_mat.set_shader_parameter(&"keep_o", keep["o"])
		_mat.set_shader_parameter(&"keep_x", keep["x"])
		_mat.set_shader_parameter(&"keep_y", keep["y"])
		_mat.set_shader_parameter(&"keep_bu_per_px", keep["bu"])
		_mat.set_shader_parameter(&"keep_mgmt", keep["mgmt"])


## The shown map in this layer's world whose network is the 3D city's ground decal (null: none).
func _network_map() -> CityMapOverlay:
	if not is_inside_tree():
		return null
	for n in get_tree().get_nodes_in_group(NETWORK_GROUP):
		var ov := n as CityMapOverlay
		if ov != null and ov.is_visible_in_tree() and in_world(ov) and ov.on_ground_decal() and ov.city.view3d != null:
			return ov
	return null


## The network kept out of the pools: CityNetworkData `net` seen through the ground mapping (ground
## XZ = o + px.x * x + px.y * y), `bu` BU per decal px, `mgmt` the decal's management share. {segs:
## [[a, b, half width px]], nodes: [[centre, radius px]], o, x, y, bu, mgmt}.
static func keep_from(net: CityNetworkData, o: Vector2, x: Vector2, y: Vector2, bu: float, mgmt: float) -> Dictionary:
	var cfg := CityView3D.CONFIG
	var segs: Array = []
	var nodes: Array = []
	for s in net.segments:
		var a: Vector3 = s["a"]
		var b: Vector3 = s["b"]
		segs.append([Vector2(a.x, a.z), Vector2(b.x, b.z),
			cfg.net_trace_px * maxf(float(s["width"]), 0.6) * 0.5 + cfg.net_keep_edge_px + mgmt * cfg.net_bus_gap_px])
	for n in net.nodes:
		var w: Vector3 = n["world"]
		nodes.append([Vector2(w.x, w.z), cfg.net_node_px * (1.4 if n["big"] else 1.0) * (1.0 + mgmt * 0.7) + cfg.net_keep_edge_px])
	return {"segs": segs, "nodes": nodes, "o": o, "x": x, "y": y, "bu": maxf(bu, 0.0001), "mgmt": mgmt}


## 1 on `k`'s network (keep_from) at `p` (px), 0 off it, as the shader computes it.
static func keep_at(p: Vector2, k: Dictionary) -> float:
	if k.is_empty():
		return 0.0
	var w: Vector2 = (k["o"] as Vector2) + p.x * (k["x"] as Vector2) + p.y * (k["y"] as Vector2)
	var bu := float(k["bu"])
	var out := 0.0
	for s: Array in k["segs"]:
		var d := w.distance_to(Geometry2D.get_closest_point_to_segment(w, s[0], s[1])) / bu
		out = maxf(out, 1.0 - smoothstep(float(s[2]) - 0.75, float(s[2]) + 0.75, d))
	for n: Array in k["nodes"]:
		var d := w.distance_to(n[0]) / bu
		out = maxf(out, 1.0 - smoothstep(float(n[1]) - 0.75, float(n[1]) + 0.75, d))
	return out
