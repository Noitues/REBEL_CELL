class_name HqSolaceMaterials
extends RefCounted
## LOOK Solace HQ: the AAA-2 "Realistic night" materials of the v5 compound (assets/city/hq_compounds/solace, manifest
## `settings.look == "aaa2"`). The glb's role materials hq_sx_* map to the PBR shader (hq_solace_pbr), the window interior-mapping
## shader (hq_solace_window) and the glass shader. Every number is the plate scene's material (art-pass hq_build / hq_preset
## `light`) times one view gain per kind. View-side only: art-owned look file, no game state.

const PBR := preload("res://shaders/city/hq_solace_pbr.gdshader")
const GLASS := preload("res://shaders/city/hq_solace_glass.gdshader")
const WINDOW := preload("res://shaders/city/hq_solace_window.gdshader")
const LOOK_KEY := "aaa2"

## Role -> shader parameters (hq_preset `light`: skin_k 0.012, rim_k 0.12 / pow 4, porcelain rough 0.16 / coat 0.8, office rough 0.6).
const ROLES := {
	"hq_sx_skin": {"roughness": 0.16, "clearcoat": 0.8, "clearcoat_roughness": 0.05, "glow_k": 0.012, "rim_k": 0.12, "rim_pow": 4.0,
		"back_k": 0.22},
	"hq_sx_porc": {"roughness": 0.16, "clearcoat": 0.8, "clearcoat_roughness": 0.05},
	"hq_sx_neon": {"albedo_k": 0.0, "emit_gain": 1.0},
	"hq_sx_office": {"roughness": 0.6, "emit_gain": 1.0},
	"hq_sx_metal": {"roughness": 0.35, "metallic": 0.6},
	"hq_sx_stone": {"roughness": 0.62},
	"hq_sx_ground": {"roughness": 0.85},
	"hq_sx_plain": {"roughness": 0.8},
	"hq_sx_water": {"roughness": 0.05, "specular": 0.9},
}


## True when `manifest` asks for the AAA-2 look.
static func wants(manifest: Dictionary) -> bool:
	return String((manifest.get("settings", {}) as Dictionary).get("look", "")) == LOOK_KEY


## The atlas texture next to the glb (null when the manifest has none or it does not load).
static func atlas(corp: StringName, manifest: Dictionary) -> Texture2D:
	var file := String((manifest.get("settings", {}) as Dictionary).get("interior_atlas", ""))
	var path := "%s/%s/%s" % [HqCompoundStage.ASSETS_DIR, corp, file]
	return load(path) as Texture2D if file != "" and ResourceLoader.exists(path) else null


## A material for compound role `name` ("" prefix `hq_sx_`), null when unknown.
static func make(name: String, atlas_tex: Texture2D) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.resource_name = name
	if name == "hq_sx_glass":
		m.shader = GLASS
		return m
	if name == "hq_sx_win":
		m.shader = WINDOW
		m.set_shader_parameter(&"atlas", atlas_tex)
		return m
	if not ROLES.has(name):
		return null
	m.shader = PBR
	var p: Dictionary = ROLES[name]
	for k: String in p:
		m.set_shader_parameter(StringName(k), p[k])
	return m


## Replaces every hq_sx_* material under `root`; returns them by name.
static func apply(root: Node, corp: StringName, manifest: Dictionary) -> Dictionary:
	var mats := {}
	var tex := atlas(corp, manifest)
	var meshes: Array[Node] = root.find_children("*", "MeshInstance3D", true, false)
	if root is MeshInstance3D:
		meshes.push_front(root)
	for node in meshes:
		var mi := node as MeshInstance3D
		if mi.mesh == null:
			continue
		for s in mi.mesh.get_surface_count():
			var src := mi.mesh.surface_get_material(s)
			var nm := src.resource_name if src != null else ""
			if not mats.has(nm):
				mats[nm] = make(nm, tex)
			if mats[nm] != null:
				mi.set_surface_override_material(s, mats[nm])
	return mats
