class_name StreetR2Materials
extends RefCounted
## Street r2 renderer, material half: one `street_r2_surface` ShaderMaterial per accumulator id (numbers of `StreetR2RenderConfigData.materials`,
## MATERIAL_SPEC section 4) and the slot-name rule for the street kit glb (`neon_emit*` neon, `lit_emit` window, `lamp_emit` lamp head).

const SURFACE := preload("res://shaders/street_r2/street_r2_surface.gdshader")
const SIGN := preload("res://shaders/street_r2/street_r2_sign.gdshader")

var _by_id: Dictionary = {}
var _tinted: Dictionary = {}


## The material of accumulator id `mat` (conc, glass, panel, solid, win, neon); one instance per builder.
func surface(mat: String) -> ShaderMaterial:
	if not _by_id.has(mat):
		_by_id[mat] = _make(mat, 0.0, -1.0)
	return _by_id[mat]


## The material for a glb surface slot `slot`. Emissive slots take the per-instance tint (MultiMesh custom data) and `emit_k`; the lamp head
## its own emission.
func for_slot(slot: String) -> ShaderMaterial:
	if slot == "lamp_emit":
		return _tint("lamp_emit", "neon", float(StreetR2RenderConfigData.shipped().lamps["head_emit"]))
	if slot.begins_with("neon_emit"):
		return _tint("neon", "neon", -1.0)
	if slot == "lit_emit":
		return _tint("win", "win", -1.0)
	match slot:
		"panel":
			return surface("panel")
		"conc":
			return surface("conc")
		"glass":
			return surface("glass")
	return surface("solid")


## A sign board material showing `tex` at emission `emit`.
func sign_board(tex: Texture2D, emit: float) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = SIGN
	m.set_shader_parameter(&"board", tex)
	m.set_shader_parameter(&"emit", emit)
	return m


func _tint(key: String, mat: String, emit_override: float) -> ShaderMaterial:
	if not _tinted.has(key):
		_tinted[key] = _make(mat, 1.0, emit_override)
	return _tinted[key]


func _make(mat: String, use_tint: float, emit_override: float) -> ShaderMaterial:
	var row: Dictionary = StreetR2RenderConfigData.shipped().materials[mat]
	var m := ShaderMaterial.new()
	m.shader = SURFACE
	m.set_shader_parameter(&"albedo_k", float(row["albedo"]))
	m.set_shader_parameter(&"rough", float(row["rough"]))
	m.set_shader_parameter(&"metal", float(row["metal"]))
	var e := float(row["emit"]) if emit_override < 0.0 else emit_override
	if use_tint > 0.0:
		e *= float(StreetR2RenderConfigData.shipped().props["emit_k"]) if emit_override < 0.0 else 1.0
	m.set_shader_parameter(&"emit", e)
	m.set_shader_parameter(&"use_tint", use_tint)
	if e <= 0.0:
		var b: Dictionary = CityShaderConfigData.shipped().building
		var fl := StreetR2OneCity.floor_bu()
		var wf: Array = b["wash_floors"]
		var wa: Array = b["wash_a"]
		var wb: Array = b["wash_b"]
		m.set_shader_parameter(&"wash_gain", float(b["wash_gain"]) * float(StreetR2RenderConfigData.shipped().facade["wash_k"]))
		m.set_shader_parameter(&"wash_h", Vector2(float(wf[0]) * fl, float(wf[1]) * fl))
		m.set_shader_parameter(&"wash_a", Vector3(float(wa[0]), float(wa[1]), float(wa[2])))
		m.set_shader_parameter(&"wash_b", Vector3(float(wb[0]), float(wb[1]), float(wb[2])))
	return m
