class_name RcLookSlotsConfig
extends Resource
## LOOK-TOOLBOX module 17: the glTF material-slot map of the Blender exports (addons/rc_look/config/look_slots.tres): which
## slot name means which look role, per naming family. One table for the names the exporters write
## (tools/art_pipeline/**: `lm_*`, `hq_*`, `hq_sx_*`; the art-pass street kit's plain names). The runtime tables
## (LandmarkMaterials.ROLES / BEAM, HqCompoundMaterials.LANDMARK_NAME, StreetR2Materials.for_slot) are pinned equal to it by
## test_rc_look_slots until they read it.

## `lm_*` slot -> landmark_toon.gdshader `role` (LandmarkMaterials.ROLES).
@export var landmark_roles: Dictionary = {}
## The light-cone slot (landmark_beam.gdshader; role -1).
@export var landmark_beam: String = "lm_beam"
## `hq_*` slot -> the landmark slot it stands for (HqCompoundMaterials.LANDMARK_NAME).
@export var hq_alias: Dictionary = {}
## The Solace AAA-2 compound's slot prefix (HqSolaceMaterials.ROLES; listed, not mapped here: that table is fenced).
@export var solace_prefix: String = "hq_sx_"
## Street kit slot -> StreetR2Materials surface (`for_slot`): every name the kit glbs carry, the fallback ones included, so no
## slot reaches the renderer unlisted.
@export var street_exact: Dictionary = {}
## Street kit slot prefix -> surface (`neon_emit`, `neon_emit_2`, ...).
@export var street_prefix: Dictionary = {}
## The surface an unlisted street slot falls back to (StreetR2Materials.for_slot's last line).
@export var street_fallback: String = "solid"


## Problems with the table (empty when valid).
func validate() -> PackedStringArray:
	var out := PackedStringArray()
	for k: Variant in landmark_roles:
		if not String(k).begins_with("lm_") or not (landmark_roles[k] is int):
			out.append("landmark_roles: %s" % k)
	for k: Variant in hq_alias:
		if not String(k).begins_with("hq_") or String(k).begins_with(solace_prefix):
			out.append("hq_alias key: %s" % k)
		var v := String(hq_alias[k])
		if v != landmark_beam and not landmark_roles.has(v):
			out.append("hq_alias %s -> %s is no landmark slot" % [k, v])
	if street_fallback == "":
		out.append("street_fallback empty")
	return out
