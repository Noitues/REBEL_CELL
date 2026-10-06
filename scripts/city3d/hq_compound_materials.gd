class_name HqCompoundMaterials
extends RefCounted
## ART-8 8w: puts the city's landmark materials on an instanced HQ compound glTF (8p's
## assets/city/hq_compounds/<corp>/<corp>_compound.glb). The compound's role materials
## (hq_toon, hq_lit, hq_neon, hq_win, hq_sign, hq_beam) are the landmark roles under other
## names, so each maps onto its LandmarkMaterials role (0 / 2 / 3 / 4 / 8, the light cone)
## and LandmarkMaterials.make builds it with the corp's ramp tint (the same target_corps
## TINT the manifest carries). View-side only.

## Compound material -> landmark material (LandmarkMaterials.ROLES / BEAM).
const LANDMARK_NAME := {"hq_toon": "lm_toon", "hq_lit": "lm_lit", "hq_neon": "lm_neon", "hq_win": "lm_win",
	"hq_sign": "lm_sign", "hq_beam": "lm_beam"}


## The landmark material name of compound material `material_name` ("" when unknown).
static func landmark_name(material_name: String) -> String:
	return String(LANDMARK_NAME.get(material_name, ""))


## The LandmarkMaterials role of compound material `material_name` (-1 the light cone, -2 unknown).
static func role_of(material_name: String) -> int:
	var lm := landmark_name(material_name)
	return LandmarkMaterials.role_of(lm) if lm != "" else -2


## Replaces every compound material under `root` with its landmark shader material for
## corporation `corp` (by day when `day`); returns them by compound material name.
static func apply(root: Node, look: LandmarkLook, corp: StringName, day: bool) -> Dictionary:
	var mats := {}
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
				var lm := landmark_name(nm)
				var m: ShaderMaterial = LandmarkMaterials.make(lm, look, corp, day) if lm != "" else null
				if m != null:
					m.resource_name = nm
				mats[nm] = m
			if mats[nm] != null:
				mi.set_surface_override_material(s, mats[nm])
	return mats
