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
## The street's real coloured local lights (AAA-2, `StreetLightRig`).
var lights: StreetLightRig = null
var _anim_t := 0.0
var _anim_frozen := false
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
# The building shader's room windows: slot of each room, its window volume, and the arrays as written (a closed room's slot is empty).
var _room_slot: Dictionary = {}  # node id -> slot
var _room_vol: Dictionary = {}  # node id -> {"box": Vector4, "z": Vector2}
var _win_boxes := PackedVector4Array()
var _win_zs := PackedVector2Array()
var _win_open := PackedFloat32Array()
var _haze_cur := -1.0
## Tools: a fixed post exposure (the exposure solve); 0 = the framing's solved value.
var exposure_override := 0.0
var _grit_skip: Dictionary = {}
var _depth_quad: MeshInstance3D = null


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
	view.grit_filter = _grit_near
	view.use_model(model)
	view.set_look_blend(LOOK_BLEND)
	_index_buildings(model)
	_mount_rooms()
	_mount_route_buildings()
	_apply_street_look()
	_apply_section()
	_build_atmosphere()
	_build_dressing()
	pose = data.overview_state()["pose"]
	_apply_pose()
	view.model_ready.connect(_on_model_ready, CONNECT_ONE_SHOT)
	if not CityView3D.can_render():
		_on_model_ready.call_deferred()
	set_process(true)


## AAA-2 facet grit (`CityView3D.grit_filter`): the buildings within `aaa.grit.reach` BU of the street segment draw with their own fgrid mesh.
func _grit_near(pr: Dictionary, n: int) -> bool:
	if _grit_skip.is_empty():
		for bid: String in data.route_bids():
			for k: int in data.bid_prisms[bid]:
				_grit_skip[k] = true
	if _grit_skip.has(n):
		return false  # a route building keeps its plane: the room windows are cut from a thin box of it
	var reach: float = float(CityShaderConfigData.shipped().aaa["grit"]["reach"])
	var poly: PackedVector2Array = pr["poly"]
	var c := Vector2.ZERO
	for p: Vector2 in poly:
		c += p
	c /= float(poly.size())
	var st: Dictionary = data.derive["street"]
	var a := Vector2(float(st["a"][0]), float(st["a"][1]))
	var b := Vector2(float(st["c"][0]), float(st["c"][1]))
	var plan := Vector2(c.x, -c.y)
	return Geometry2D.get_closest_point_to_segment(plan, a, b).distance_to(plan) <= reach


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
	_win_open.resize(ROOM_MAX)
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
			_room_slot[id] = n_win
			_room_vol[id] = vol
			_win_open[n_win] = 1.0
			n_win += 1
	_win_boxes = boxes
	_win_zs = zs
	var bm := view.building_material()
	bm.set_shader_parameter(&"room_n", n_win)
	bm.set_shader_parameter(&"room_box", boxes)
	bm.set_shader_parameter(&"room_z", zs)
	bm.set_shader_parameter(&"room_open", _win_open)


## The route buildings carry the `route` bit: the shader cuts the room windows out of their walls.
func _mount_route_buildings() -> void:
	for bid: String in _route_bids:
		for g: Array in _prism_geom.get(bid, []):
			view.set_prism_w(int(g[0]), NetrunInstancePack.pack(float(g[2]), float(g[2]), 1.0, 0.0, 0.0, false, true))


## The street's own look on the city (`StreetRouteConfigData.look`): the building uniforms of the route street (wash, floor bands)
## and the quiet lane lines (`route_lane`: desaturated, dimmed). Only this view sets them; the page and the other netrun views keep
## the shared NA-22 numbers.
func _apply_street_look() -> void:
	var lk: Dictionary = StreetRouteConfigData.shipped().look
	var bm := view.building_material()
	var over: Dictionary = lk["building"]
	for k: String in over:
		bm.set_shader_parameter(StringName(k), float(over[k]))
	var lane := view.lane_material()
	if lane != null:
		var ln: Dictionary = lk["lane"]
		lane.shader = load("res://shaders/city/route_lane.gdshader")
		lane.set_shader_parameter(&"street_gain", float(ln["gain"]))
		lane.set_shader_parameter(&"lane_sat", float(ln["sat"]))


## Opens or closes room `id` at once (`set_room_dissolve` at 1 or 0): closed, the building keeps its facade over the room (no window
## cut into the wall, the room mesh hidden), so an unrevealed room never reads as a black box.
func set_room_open(id: String, open: bool) -> void:
	set_room_dissolve(id, 1.0 if open else 0.0)


## NA-25b: the facade of room `id` dissolved into its cutaway room by `k` (0 = the closed facade, 1 = the window cut and the room
## whole). The REVEAL drives `k` by its timeline (`EntryBeats.up_k`, `entry_reveal_dissolve` seconds), so scrubbing, the jack-out reverse
## and a skip all land on the same end state; under reduce effects the view passes 0 or 1 only. A share of the window's pixels is cut
## by a Bayer order (`city_building` `room_open`).
func set_room_dissolve(id: String, k: float) -> void:
	k = clampf(k, 0.0, 1.0)
	var m: MeshInstance3D = _rooms.get(id)
	if m != null:
		m.visible = k > 0.0
	if not _room_slot.has(id):
		return
	var slot: int = _room_slot[id]
	var vol: Dictionary = _room_vol[id]
	var open: bool = k > 0.0
	var want_box: Vector4 = vol["box"] if open else Vector4()
	var want_z: Vector2 = vol["z"] if open else Vector2()
	if _win_boxes[slot] == want_box and _win_zs[slot] == want_z and is_equal_approx(_win_open[slot], k):
		return
	_win_boxes[slot] = want_box
	_win_zs[slot] = want_z
	_win_open[slot] = k
	var bm := view.building_material()
	bm.set_shader_parameter(&"room_box", _win_boxes)
	bm.set_shader_parameter(&"room_z", _win_zs)
	bm.set_shader_parameter(&"room_open", _win_open)


## How far room `id`'s facade has dissolved open (0 closed .. 1 whole).
func room_dissolve_of(id: String) -> float:
	return _win_open[_room_slot[id]] if _room_slot.has(id) else (1.0 if room_is_open(id) else 0.0)


## True when room `id` is open (drawn, its window cut).
func room_is_open(id: String) -> bool:
	var m: MeshInstance3D = _rooms.get(id)
	return m != null and m.visible


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
	view.set_aaa_exposure(float(atm["exposure"]))
	view.add_to_layer(&"props", fv)
	_extras.append(fv)
	_clock_mats.append(fm)
	# The fog-only lights (the 18 city-glow lights and the beam spots) are part of the street's light rig (`_build_dressing`).
	NetrunShaderKit.set_clock(_clock_mats, 0.0, 0.0)


## The street dressing of NA-24 (signs, lamps, glows, washes, beams, lanes, plumes): placed from the derive and the city only, one
## group per reveal tier. Held in `_extras`, so the id pass hides it; its materials join the netrun clock after the fog's.
func _build_dressing() -> void:
	dressing = StreetDressing.build(data.derive, data.city)
	view.add_to_layer(&"props", dressing.root)
	_extras.append(dressing.root)
	_clock_mats.append_array(dressing.clock_mats)
	NetrunShaderKit.set_clock(_clock_mats, 0.0, 0.0)
	# AAA-2: the street's real coloured local lights (A-022); the emissive ground / wall discs that stood in for them are hidden.
	lights = StreetLightRig.build(dressing.light_sources(data.derive))
	view.add_to_layer(&"props", lights.root)
	_extras.append(lights.root)
	if bool(CityShaderConfigData.shipped().aaa["lights"]["hide_discs"]):
		for g: String in ["lamp_spill", "glow", "wash"]:
			for n: Variant in dressing.nodes.get(g, []):
				(n as Node3D).visible = false


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
	view.set_puddles_sharp(RevealTiers.band(pose.dist, "puddles_sharp"))
	view.environment().volumetric_fog_length = NetrunShaderKit.fog_length_for(pose.dist)
	var atm: Dictionary = StreetRouteConfigData.shipped().atmosphere
	(_clock_mats[0] as ShaderMaterial).set_shader_parameter(&"density_mul", lerpf(float(atm["density_overview"]), float(atm["density_decision"]), zd))
	# The depth haze is calibrated on the far OVERVIEW; the near DECISION frame keeps its facades (`look.haze` = [OVERVIEW, DECISION]).
	var hz: Array = StreetRouteConfigData.shipped().look["haze"]
	var haze := lerpf(float(hz[0]), float(hz[1]), zd)
	if not is_equal_approx(haze, _haze_cur):
		_haze_cur = haze
		view.building_material().set_shader_parameter(&"haze_k", haze)
	# The value band holds on both framings: the exposure eases from the OVERVIEW solve to the DECISION solve (`look.exposure`).
	var fk: Array = StreetRouteConfigData.shipped().look["frame"]
	for rid: String in _room_mats:
		(_room_mats[rid] as ShaderMaterial).set_shader_parameter(&"frame_k", lerpf(float(fk[0]), float(fk[1]), zd))
	var ex: Array = StreetRouteConfigData.shipped().look["exposure"]
	var expo: float = exposure_override if exposure_override > 0.0 else lerpf(float(ex[0]), float(ex[1]), zd)
	view.set_aaa_exposure(expo)
	_scale_transparent_emitters(expo)


## AAA-2: the transparent emitters (beam shafts, plumes, sign flickers: drawn after the post's screen copy, so the chain does not
## see them) take the exposure themselves, as the Environment tonemap exposure used to scale them.
func _scale_transparent_emitters(expo: float) -> void:
	for m: Variant in _clock_mats:
		var sm := m as ShaderMaterial
		if sm == null or sm.shader == null:
			continue
		var path: String = sm.shader.resource_path
		if path.ends_with("dress_neon.gdshader") or path.ends_with("beam_shaft.gdshader"):
			sm.set_shader_parameter(&"emission_multiplier", expo)
		elif path.ends_with("dress_plume.gdshader"):
			sm.set_shader_parameter(&"emit", float(DressingConfigData.shipped().plume["emit"]) * expo)


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


## The depth pass of PIPELINE_SPEC 12.0 on or off: a full-screen quad writing the linear camera depth in BU x 100 as 16 bits (R =
## high byte, G = low byte). Use it between `set_id_pass(true)` and `set_id_pass(false)` (the id pass hides the fog and the dressing),
## a few frames before reading `view.get_texture()`; `tools/city/png16.gd` packs the result into `depth.png`.
func set_depth_pass(on: bool) -> void:
	if on == (_depth_quad != null):
		return
	if on:
		_depth_quad = IdCapture.make_depth_quad()
		view.camera.add_child(_depth_quad)
	else:
		_depth_quad.queue_free()
		_depth_quad = null


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

## The always-alive loops' clock (s).
func anim_t() -> float:
	return _anim_t


## NA-ID: holds the loops' clock at `t` (on) or lets it run on from `t` (off); the id capture freezes it around a frame.
func freeze_anim(on: bool, t: float) -> void:
	_anim_frozen = on
	_anim_t = t
	if not _clock_mats.is_empty():
		NetrunShaderKit.set_clock(_clock_mats, _anim_t, 0.0)


func _process(delta: float) -> void:
	if view == null:
		return
	if Vector2i(view.size) != render_px():
		_resize_view()
	if not _clock_mats.is_empty() and not _anim_frozen:
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
