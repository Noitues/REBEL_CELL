class_name LandmarkMaterials
extends RefCounted
## ART-5 5b: puts the landmark materials on an instanced landmark glTF (assets/city/landmarks/<corp>/<job>.glb).
## The glTF carries one material per ROLE (lm_toon, lm_lit, lm_neon, lm_win, ... see the corp's manifest.json);
## this maps each role to the landmark toon or light-cone shader with the LandmarkLook values for the corp and the
## time of day. View-side only: it never touches game state.

const TOON_SHADER := preload("res://assets/city/landmarks/landmark_toon.gdshader")
const BEAM_SHADER := preload("res://assets/city/landmarks/landmark_beam.gdshader")
const LOOK_PATH := "res://assets/city/landmarks/landmark_look.tres"
## glTF material name -> landmark_toon.gdshader `role` (lm_beam uses the light-cone shader).
const ROLES := {"lm_toon": 0, "lm_toon_lines": 1, "lm_lit": 2, "lm_neon": 3, "lm_win": 4, "lm_win_ring": 5,
	"lm_win_lines": 6, "lm_win_fist_home": 7, "lm_win_fist_dispatch": 7, "lm_sign": 8}
const BEAM := "lm_beam"


## The role of glTF material `material_name` (-1 for the light cones, -2 when unknown).
static func role_of(material_name: String) -> int:
	if material_name == BEAM:
		return -1
	return int(ROLES.get(material_name, -2))


## Replaces every landmark material under `root` with its shader material for corporation `corp` (by day when
## `day`); returns the materials by glTF material name so the caller can drive the reveal (set_reveal) or swap the
## DISPATCH fist in (show_dispatch).
static func apply(root: Node, look: LandmarkLook, corp: StringName, day: bool) -> Dictionary:
	var mats := {}
	for mi: MeshInstance3D in _meshes(root):
		for s in mi.mesh.get_surface_count():
			var src := mi.mesh.surface_get_material(s)
			var nm := src.resource_name if src != null else ""
			if not mats.has(nm):
				mats[nm] = make(nm, look, corp, day)
			if mats[nm] != null:
				mi.set_surface_override_material(s, mats[nm])
	return mats


## The shader material for glTF material `material_name`, or null when it is not a landmark role.
static func make(material_name: String, look: LandmarkLook, corp: StringName, day: bool) -> ShaderMaterial:
	var role := role_of(material_name)
	if role == -2:
		return null
	var m := ShaderMaterial.new()
	m.resource_name = material_name
	if role == -1:
		m.shader = BEAM_SHADER
		m.set_shader_parameter("beam_alpha", look.beam_alpha)
		return m
	m.shader = TOON_SHADER
	m.set_shader_parameter("role", role)
	var ramp: Array[Color] = look.ramp_day if day else look.ramp_night
	var tint: Color = look.corp_tint.get(corp, Color(1, 1, 1))
	m.set_shader_parameter("ramp_shadow", _tinted(ramp[0], tint))
	m.set_shader_parameter("ramp_mid", _tinted(ramp[1], tint))
	m.set_shader_parameter("ramp_lit", _tinted(ramp[2], tint))
	m.set_shader_parameter("ramp_edges", look.ramp_edges)
	m.set_shader_parameter("lit_emission", look.lit_emission)
	m.set_shader_parameter("neon_gain", look.neon_gain_day if day else look.neon_gain_night)
	m.set_shader_parameter("window_gain", look.window_gain_day if day else look.window_gain_night)
	var glass := look.window_glass_day
	m.set_shader_parameter("glass", Vector3(glass.r, glass.g, glass.b))
	m.set_shader_parameter("glass_mix", look.window_glass_mix_day if day else 0.0)
	m.set_shader_parameter("sign_gain", look.sign_gain)
	m.set_shader_parameter("flicker_band", look.flicker_band)
	m.set_shader_parameter("fist_gain", look.fist_gain)
	m.set_shader_parameter("lines_window_share", look.lines_window_share)
	m.set_shader_parameter("lines_dark", Vector3(look.lines_dark.r, look.lines_dark.g, look.lines_dark.b))
	m.set_shader_parameter("lines_dark_k", look.lines_dark_k)
	return m


## REBEL_CELL: sets the reveal (0 = the sector fully lit, 1 = the fist revealed) on every material of `mats`.
static func set_reveal(mats: Dictionary, q: float) -> void:
	for m: ShaderMaterial in mats.values():
		if m != null and m.shader == TOON_SHADER:
			m.set_shader_parameter("reveal_q", q)


## REBEL_CELL: shows the DISPATCH fist windows (true) or the home ones (false) under `root`.
static func show_dispatch(root: Node, dispatch: bool) -> void:
	for mi: MeshInstance3D in _meshes(root):
		var nm := String(mi.name)
		if nm.ends_with("win_fist_home"):
			mi.visible = not dispatch
		elif nm.ends_with("win_fist_dispatch"):
			mi.visible = dispatch


static func _tinted(c: Color, t: Color) -> Vector3:
	return Vector3(minf(1.0, c.r * t.r), minf(1.0, c.g * t.g), minf(1.0, c.b * t.b))


static func _meshes(root: Node) -> Array[MeshInstance3D]:
	var out: Array[MeshInstance3D] = []
	if root is MeshInstance3D:
		out.append(root)
	for c in root.get_children():
		out.append_array(_meshes(c))
	return out
