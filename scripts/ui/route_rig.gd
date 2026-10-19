class_name RouteRig
extends Control
## NA-23a: the street netrun's 3D rig. The game's own city (`CityView3D`, the full model) seen through the netrun camera
## (`NetrunFrustum.apply`, a derive pose), the route's rooms (`StreetRoomKit` interiors lit behind windows cut from the route
## buildings' walls by the `city_building` shader), the 7.1 occlusion (`OcclusionHelper` states written per building as
## `NetrunInstancePack` words, eased over `occlusion.ease_s`), the street section and the fog. View only: it reads the derive and
## never changes game state; the overlay and the screen build on the projections it gives.
## Headless and under reduce effects every move and ease lands at once (the end state).

## The model, its chunks and the rooms are in place.
signal prepared
## The displayed pose changed (the overlay redraws).
signal pose_changed

const NEAR := 0.5
const FAR := 3000.0
## NA-25: the far plane is at least this many camera distances (the dive's start is beyond FAR).
const FAR_PAD := 1.5
## The Environment tonemap and the look this rig holds on the city (the netrun look in full).
const LOOK_BLEND := 1.0
const ROOM_MAX := 32

var data: StreetRouteData = null
var view: CityView3D = null
## The displayed pose (the camera's).
var pose: NetrunPose = null

var _tex: TextureRect = null
var _grade: ShaderMaterial = null
var _rooms: Dictionary = {}  # node id -> MeshInstance3D
var _room_mats: Dictionary = {}  # node id -> ShaderMaterial
var _prism_geom: Dictionary = {}  # bid -> Array of [prism index, y0, h]
var _route_bids: Dictionary = {}
var _built := false
var _extras: Array[Node3D] = []
var _clock_mats: Array = []
## The street dressing (NA-24): signs, lamps, lanes, beams, plumes by reveal tier.
var dressing: StreetDressing = null
var _anim_t := 0.0
# The camera move.
var _from: NetrunPose = null
var _to: NetrunPose = null
var _move_t := 1.0
var _move_dur := 0.0
# The occlusion ease: bid -> [cut, opacity] now / from / target.
var _occ_cur: Dictionary = {}
var _occ_from: Dictionary = {}
var _occ_tgt: Dictionary = {}
var _occ_t := 1.0
var _bid_cut_full: Dictionary = {}  # bid -> top


## Builds the rig for `p_data` on `model` (the game's full city). Call once, after adding to the tree.
func setup(p_data: StreetRouteData, model: CityModel) -> void:
	data = p_data
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	view = CityView3D.new()
	view.size = render_px()
	add_child(view)
	_tex = TextureRect.new()
	_tex.name = "CityTexture"
	_tex.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_tex.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_tex.stretch_mode = TextureRect.STRETCH_SCALE
	_tex.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_tex.texture = view.get_texture()
	_grade = ShaderMaterial.new()
	_grade.shader = load("res://shaders/city/route_grade.gdshader")
	_tex.material = _grade
	add_child(_tex)
	view.use_model(model)
	view.set_look_blend(LOOK_BLEND)
	_index_buildings(model)
	_mount_rooms()
	_mount_route_buildings()
	_apply_section()
	_build_atmosphere()
	_build_dressing()
	pose = data.overview_state()["pose"]
	_apply_pose()
	view.model_ready.connect(_on_model_ready, CONNECT_ONE_SHOT)
	if not CityView3D.can_render():
		_on_model_ready.call_deferred()
	set_process(true)


## Camera move seconds (config `rig`): a step to the next decision, the OVERVIEW <-> DECISION zoom, a hover in and out.
func t_step_seconds() -> float:
	return float(_rig_cfg()["t_step"])


func t_zoom_seconds() -> float:
	return float(_rig_cfg()["t_zoom"])


func t_hover_in_seconds() -> float:
	return float(_rig_cfg()["t_hover_in"])


func t_hover_out_seconds() -> float:
	return float(_rig_cfg()["t_hover_out"])


## The 2D grade material over the city texture (the hover power cut's uniforms: `mask`, `k`, `cut_level`, ...).
func grade() -> ShaderMaterial:
	return _grade


## True once the city's chunks are drawn.
func is_prepared() -> bool:
	return _built


func _on_model_ready() -> void:
	if _built:
		return
	_built = true
	prepared.emit()


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED and view != null:
		_resize_view()


## `CityView3D.set_view_size` re-applies the iso camera, so the netrun pose goes back on after it.
func _resize_view() -> void:
	view.set_view_size(render_px())
	if pose != null:
		_apply_pose()


## The city's render size: this control's logical size times the window's stretch scale (the game's stretch mode is canvas_items,
## so a 1080p window draws the 3D at 1920 x 1080, not 1280 x 720 scaled up).
func render_px() -> Vector2i:
	var st := get_viewport().get_final_transform().get_scale().x if is_inside_tree() else 1.0
	return Vector2i((size * maxf(st, 1.0)).round()).max(Vector2i(2, 2))


func _instant() -> bool:
	return DisplayServer.get_name() == "headless" or Settings.reduce_effects


func _rig_cfg() -> Dictionary:
	return NetrunArtConfigData.shipped().rig


# --- Scene ------------------------------------------------------------------------------------

func _index_buildings(model: CityModel) -> void:
	for bid: String in data.bid_prisms:
		var geo: Array = []
		var top := 0.0
		for n: int in data.bid_prisms[bid]:
			var pr: Dictionary = model.prisms[n]
			geo.append([n, float(pr["y0"]), float(pr["h"])])
			top = maxf(top, float(pr["y0"]) + float(pr["h"]))
		_prism_geom[bid] = geo
		_bid_cut_full[bid] = top
	for bid: String in data.route_bids():
		_route_bids[bid] = true


## The room meshes (one per route node) and the windows the building shader cuts.
func _mount_rooms() -> void:
	var cfg := StreetRouteConfigData.shipped()
	var rooms: Dictionary = data.rooms()
	var ids: Array = rooms.keys()
	IdSort.sort_ids(ids)
	var elite: Dictionary = {}
	for n: Dictionary in data.run_graph["nodes"]:
		elite[String(n["id"])] = bool(n["elite"])
	var boxes := PackedVector4Array()
	var zs := PackedVector2Array()
	boxes.resize(ROOM_MAX)
	zs.resize(ROOM_MAX)
	var n_win := 0
	for id: String in ids:
		var room: Dictionary = rooms[id]
		var kind := String(room["kind"])
		var is_elite: bool = bool(elite.get(id, false))
		var rgb: Array = cfg.rooms["elite"] if is_elite and kind == "router" else cfg.rooms["colors"][kind]
		var mesh := StreetRoomKit.build_mesh(room, kind, is_elite, Color(float(rgb[0]), float(rgb[1]), float(rgb[2])), cfg.rooms)
		if mesh == null:
			push_error("RouteRig: room %s of kind '%s' cannot be drawn" % [id, kind])
			continue
		var mi := MeshInstance3D.new()
		mi.name = "Room_%s" % id
		mi.mesh = mesh
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		var mat := ShaderMaterial.new()
		mat.shader = load("res://shaders/city/route_room.gdshader")
		mat.set_shader_parameter(&"energy", float(cfg.rooms["energy_idle"]))
		var layer_i := int(room["layer"])
		# G is the node's 1-based place in the run graph's order (layer, index): one value per room, so a check can box a room
		# by G alone (the layer is in B).
		var idx: int = data.node_ids.find(id) + 1
		mat.set_shader_parameter(&"id_color", Vector3(5.0, float(idx), float(layer_i)) / 255.0)
		mi.material_override = mat
		view.add_to_layer(&"props", mi)
		_rooms[id] = mi
		_room_mats[id] = mat
		var vol := StreetRoomKit.volume(room, float(cfg.rooms["glass_pad_bu"]))
		if not vol.is_empty() and n_win < ROOM_MAX:
			boxes[n_win] = vol["box"]
			zs[n_win] = vol["z"]
			n_win += 1
	var bm := view.building_material()
	bm.set_shader_parameter(&"room_n", n_win)
	bm.set_shader_parameter(&"room_box", boxes)
	bm.set_shader_parameter(&"room_z", zs)


## The route buildings carry the `route` bit: the shader cuts the room windows out of their walls.
func _mount_route_buildings() -> void:
	for bid: String in _route_bids:
		for g: Array in _prism_geom.get(bid, []):
			view.set_prism_w(int(g[0]), NetrunInstancePack.pack(float(g[2]), float(g[2]), 1.0, 0.0, 0.0, false, true))


## The street section: the corridor along the street, cut to the zoom's height (zoom_dive 1 on every street view).
func _apply_section() -> void:
	var st: Dictionary = data.derive["street"]
	var a: Array = st["a"]
	var c: Array = st["c"]
	var nrm: Array = data.derive["nrm"]
	var zcut := NetrunSection.zcut(1.0)
	NetrunShaderKit.set_section(view.building_material(), Vector2(float(a[0]), float(a[1])), Vector2(float(c[0]), float(c[1])),
		Vector2(float(nrm[0]), float(nrm[1])), 0.0, zcut)


## The fog volume, its fog-only lights and the exposure (the NA-22 calibration frame).
func _build_atmosphere() -> void:
	var env := view.environment()
	NetrunShaderKit.configure_environment(env)
	var st: Dictionary = data.derive["street"]
	var a := Vector2(float(st["a"][0]), float(st["a"][1]))
	var c := Vector2(float(st["c"][0]), float(st["c"][1]))
	var nrm: Array = data.derive["nrm"]
	var mid := (a + c) * 0.5
	var centre := Vector3(mid.x, 0.0, -mid.y)
	var fv := NetrunShaderKit.fog_volume(centre)
	var fm := fv.material as ShaderMaterial
	fm.set_shader_parameter(&"look_blend", LOOK_BLEND)
	fm.set_shader_parameter(&"sec_a", a)
	fm.set_shader_parameter(&"sec_c", c)
	fm.set_shader_parameter(&"sec_nrm", Vector2(float(nrm[0]), float(nrm[1])))
	var atm: Dictionary = StreetRouteConfigData.shipped().atmosphere
	fm.set_shader_parameter(&"front_sym", float(atm["front_sym"]))
	# The street's value-band solve (12.1, both seeds' OVERVIEW) with the dressing on: the exposure of this view.
	env.tonemap_exposure = float(atm["exposure"])
	view.add_to_layer(&"props", fv)
	_extras.append(fv)
	_clock_mats.append(fm)
	# Fog-only lights along the street (energy 0, volumetric energy only): the city's glow in the haze.
	var glow_n := int(atm["glow_count"])
	for k in glow_n:
		var l := OmniLight3D.new()
		l.light_energy = 0.0
		l.light_volumetric_fog_energy = float(atm["glow_energy"])
		l.omni_range = float(atm["glow_range"])
		var tint: Array = CityShaderConfigData.shipped().fog["tint_a" if k % 2 == 0 else "tint_b"]
		l.light_color = Color(float(tint[0]), float(tint[1]), float(tint[2]))
		var u := (float(k) + 0.5) / float(glow_n)
		var p := a.lerp(c, u)
		var side := 1.0 if k % 2 == 0 else -1.0
		var off := float(atm["glow_side"])
		l.position = Vector3(p.x + float(nrm[0]) * side * off, float(atm["glow_height"]), -(p.y + float(nrm[1]) * side * off))
		view.add_to_layer(&"props", l)
		_extras.append(l)
	NetrunShaderKit.set_clock(_clock_mats, 0.0, 0.0)


## The street dressing of NA-24 (signs, lamps, glows, washes, beams, lanes, plumes): placed from the derive and the city only, one
## group per reveal tier. Held in `_extras`, so the id pass hides it; its materials join the netrun clock after the fog's.
func _build_dressing() -> void:
	dressing = StreetDressing.build(data.derive, data.city)
	view.add_to_layer(&"props", dressing.root)
	_extras.append(dressing.root)
	_clock_mats.append_array(dressing.clock_mats)
	NetrunShaderKit.set_clock(_clock_mats, 0.0, 0.0)


# --- Camera -----------------------------------------------------------------------------------

func _apply_pose() -> void:
	# NA-25: the dive starts on the HQ page pose, farther than FAR (3833 BU): the far plane follows the camera.
	NetrunFrustum.apply_render(view.camera, pose, NEAR, maxf(FAR, pose.dist * FAR_PAD))
	_apply_fog_density()
	pose_changed.emit()


## The fog density multiplier eased between the OVERVIEW and the DECISION values by `zoom_detail` (0 .. 1 over the camera
## distance), on the fog volume's material.
func _apply_fog_density() -> void:
	if _clock_mats.is_empty() or data == null:
		return
	var z: Dictionary = data.derive["decision"]
	var d_ov: float = NetrunPose.from_json(data.derive["overview"]).dist
	var d_dec: float = NetrunPose.from_json(z).dist
	var zd := RevealTiers.zoom_detail(pose.dist, d_ov, d_dec)
	var atm: Dictionary = StreetRouteConfigData.shipped().atmosphere
	(_clock_mats[0] as ShaderMaterial).set_shader_parameter(&"density_mul", lerpf(float(atm["density_overview"]), float(atm["density_decision"]), zd))


## Puts the camera on `p` at once (no move).
func set_pose(p: NetrunPose) -> void:
	pose = p
	_to = null
	_move_t = 1.0
	_apply_pose()


## Moves the camera to `p` over `seconds` (smoothstep, `dist` in log space: `NetrunPose.mix`). Instant when headless or under
## reduce effects.
func move_to(p: NetrunPose, seconds: float) -> void:
	if _instant() or seconds <= 0.0 or not _built:
		set_pose(p)
		return
	_from = pose
	_to = p
	_move_t = 0.0
	_move_dur = seconds


## True while the camera is moving.
func moving() -> bool:
	return _to != null


## Ends a move at its target (the MotionSkip rule).
func complete_move() -> void:
	if _to != null:
		set_pose(_to)


# --- Id pass ----------------------------------------------------------------------------------

## The id pass of PIPELINE_SPEC 12.0 on or off (`CityView3D.set_id_pass`, the rooms' flat class 5 / room / layer colours, no fog
## volume). A capture reads `view.get_texture()` between the two calls, a frame after `on`.
func set_id_pass(on: bool) -> void:
	view.set_id_pass(on)
	for id: String in _room_mats:
		(_room_mats[id] as ShaderMaterial).set_shader_parameter(&"id_mode", on)
	for n in _extras:
		if is_instance_valid(n):
			n.visible = not on
	_tex.material = null if on else _grade


# --- Occlusion --------------------------------------------------------------------------------

## Sets the 7.1 occlusion of a pose record (`rec["occlusion"]["buildings"]`: bid, cut_height, opacity): each listed building eases
## to its cut and ghost, every other one back to its full height over `occlusion.ease_s` (0 under reduce effects / headless).
func set_occlusion(rec: Dictionary) -> void:
	var rows: Array = (rec["occlusion"] as Dictionary)["buildings"]
	var tgt: Dictionary = {}
	for r: Dictionary in rows:
		var bid := String(r["bid"])
		if not _prism_geom.has(bid) or _route_bids.has(bid):
			continue
		tgt[bid] = [float(r["cut_height"]), float(r["opacity"])]
	_occ_from = {}
	for bid: String in _occ_cur:
		_occ_from[bid] = _occ_cur[bid]
	for bid: String in tgt:
		if not _occ_from.has(bid):
			_occ_from[bid] = [float(_bid_cut_full[bid]), 1.0]
	_occ_tgt = tgt
	_occ_t = 0.0
	if _instant() or float(NetrunArtConfigData.shipped().occlusion["ease_s"]) <= 0.0:
		_occ_t = 1.0
		_write_occlusion(1.0)


## The eased [cut, opacity] of building `bid` now (full height, opaque when untouched).
func occlusion_of(bid: String) -> Array:
	return _occ_cur.get(bid, [float(_bid_cut_full.get(bid, 0.0)), 1.0])


func _write_occlusion(k: float) -> void:
	var oc: Dictionary = NetrunArtConfigData.shipped().occlusion
	var edge := float(oc["edge"])
	var keys: Array = _occ_from.keys()
	for bid: String in _occ_tgt:
		if not keys.has(bid):
			keys.append(bid)
	var cur: Dictionary = {}
	for bid: String in keys:
		var top: float = _bid_cut_full[bid]
		var f: Array = _occ_from.get(bid, [top, 1.0])
		var t: Array = _occ_tgt.get(bid, [top, 1.0])
		var cut := lerpf(float(f[0]), float(t[0]), k)
		var op := lerpf(float(f[1]), float(t[1]), k)
		var untouched: bool = cut >= top - 0.0001 and op >= 0.9999
		for g: Array in _prism_geom[bid]:
			var h: float = g[2]
			var rel: float = cut - float(g[1])
			var w := 0.0 if untouched else NetrunInstancePack.pack(h, rel, op, edge if op < 0.9999 else 0.0, 0.0)
			view.set_prism_w(int(g[0]), w)
		if not untouched:
			cur[bid] = [cut, op]
	_occ_cur = cur
	if k >= 1.0:
		_occ_from = cur.duplicate()


# --- Rooms ------------------------------------------------------------------------------------

## Brightens (or dims) room `id`: `1` the idle look, the config `energy_lit` the options / the hovered branch.
func set_room_energy(id: String, energy: float) -> void:
	var m: ShaderMaterial = _room_mats.get(id)
	if m != null:
		m.set_shader_parameter(&"energy", energy)


## The room mesh of node `id` (null when it could not be drawn).
func room_mesh(id: String) -> MeshInstance3D:
	return _rooms.get(id)


## The node ids that have a drawn room.
func room_ids() -> Array:
	var out: Array = _rooms.keys()
	IdSort.sort_ids(out)
	return out


# --- Projection -------------------------------------------------------------------------------

## The screen px (in this control) of plan point `p` ([x, y, z], z above ground) under the displayed pose; `Vector2(INF, INF)` behind
## the camera. The pose's 1920 x 1080 reference frame scaled to the width (keep-width projection).
func to_screen(p: Array, at: NetrunPose = null) -> Vector2:
	var ps: NetrunPose = pose if at == null else at
	var q: Array = ps.proj(p)
	if q.is_empty():
		return Vector2(INF, INF)
	var rg := _rig_cfg()
	var k := size.x / float(rg["ref_w"])
	return Vector2(size.x * 0.5 + (float(q[0]) - float(rg["ref_w"]) * 0.5) * k, size.y * 0.5 + (float(q[1]) - float(rg["ref_h"]) * 0.5) * k)


## The four front corners of room `id` in screen px (empty when one is behind the camera).
func room_corners_px(id: String, at: NetrunPose = null) -> PackedVector2Array:
	var out := PackedVector2Array()
	var room: Dictionary = data.rooms().get(id, {})
	if room.is_empty():
		return out
	var gz := float(room.get("ground_z", 0.0))
	for q: Array in room["front"]:
		var s := to_screen([q[0], q[1], float(q[2]) + gz], at)
		if not s.is_finite():
			return PackedVector2Array()
		out.append(s)
	return out


## The bounding box of room `id`'s front in screen px (empty Rect2 when not in front of the camera).
func room_box_px(id: String, at: NetrunPose = null) -> Rect2:
	var pts := room_corners_px(id, at)
	if pts.is_empty():
		return Rect2()
	var r := Rect2(pts[0], Vector2.ZERO)
	for p in pts:
		r = r.expand(p)
	return r


# --- Frame loop -------------------------------------------------------------------------------

func _process(delta: float) -> void:
	if view == null:
		return
	if Vector2i(view.size) != render_px():
		_resize_view()
	if not _clock_mats.is_empty():
		# The always-alive loops (T = loop_s): the clock of the dressing, lanes, beams and fog.
		_anim_t = fposmod(_anim_t + delta, float(CityShaderConfigData.shipped().streak["loop_s"]))
		NetrunShaderKit.set_clock(_clock_mats, _anim_t, 0.0)
	if _to != null:
		_move_t = minf(1.0, _move_t + delta / maxf(_move_dur, 0.001))
		if _move_t >= 1.0:
			set_pose(_to)
		else:
			pose = _from.mix(_to, NetrunCameraRig.ease(_move_t))
			_apply_pose()
	if _occ_t < 1.0:
		var ease_s := float(NetrunArtConfigData.shipped().occlusion["ease_s"])
		_occ_t = minf(1.0, _occ_t + delta / maxf(ease_s, 0.001))
		_write_occlusion(NetrunCameraRig.ease(_occ_t) if _occ_t < 1.0 else 1.0)
