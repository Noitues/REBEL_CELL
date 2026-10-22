class_name RcLookSlots
extends RefCounted
## LOOK-TOOLBOX module 17: what a Blender export's glTF material slot means for the look. Reads the slot map
## (RcLookSlotsConfig, addons/rc_look/config/look_slots.tres) and walks an imported scene's surfaces. Pure lookup: it never
## assigns a material (the views do, by role); the post-import script (addons/rc_look/import/rc_look_post_import.gd) stamps
## each mesh with its slots and reports the unlisted ones at import.

const DEFAULT_PATH := "res://addons/rc_look/config/look_slots.tres"
## Families.
const LANDMARK := &"landmark"
const HQ := &"hq"
const SOLACE := &"solace"
const STREET := &"street_kit"
const NONE := &""
## Meta on a MeshInstance3D: Array of "family:role" per surface (the post-import stamp).
const META := &"rcl_slots"

static var _cfg: RcLookSlotsConfig = null


## The shipped slot map, loaded once.
static func config() -> RcLookSlotsConfig:
	if _cfg == null:
		_cfg = load(DEFAULT_PATH) as RcLookSlotsConfig
	return _cfg


## What slot `slot_name` means: {family, role, listed}. Landmark and HQ roles are landmark_toon roles (int; -1 the light
## cone); street roles are StreetR2Materials surface ids (String); a Solace slot keeps its own name (its table is fenced).
## `listed` is false for a name no family carries (a street slot then reports the fallback surface it would get).
static func of(slot_name: String, cfg: RcLookSlotsConfig = null) -> Dictionary:
	var c := cfg if cfg != null else config()
	if slot_name == c.landmark_beam:
		return {"family": LANDMARK, "role": -1, "listed": true}
	if c.landmark_roles.has(slot_name):
		return {"family": LANDMARK, "role": int(c.landmark_roles[slot_name]), "listed": true}
	if slot_name.begins_with(c.solace_prefix):
		return {"family": SOLACE, "role": slot_name.trim_prefix(c.solace_prefix), "listed": true}
	if c.hq_alias.has(slot_name):
		var lm := String(c.hq_alias[slot_name])
		return {"family": HQ, "role": -1 if lm == c.landmark_beam else int(c.landmark_roles[lm]), "listed": true}
	if c.street_exact.has(slot_name):
		return {"family": STREET, "role": String(c.street_exact[slot_name]), "listed": true}
	var prefixes: Array = c.street_prefix.keys()
	prefixes.sort()
	for p: String in prefixes:
		if slot_name.begins_with(p):
			return {"family": STREET, "role": String(c.street_prefix[p]), "listed": true}
	return {"family": NONE, "role": c.street_fallback, "listed": false}


## Every surface under `root`: [{node (path from root), surface, slot, family, role, listed}], in tree order. A surface with
## no material reports slot "" (the vehicles carry none: their parts go by node name).
static func surfaces(root: Node, cfg: RcLookSlotsConfig = null) -> Array:
	var out: Array = []
	for n: Node in [root] + root.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		if mi == null or mi.mesh == null:
			continue
		for s in mi.mesh.get_surface_count():
			var m := mi.mesh.surface_get_material(s)
			var nm := String(m.resource_name) if m != null else ""
			var r := of(nm, cfg) if nm != "" else {"family": NONE, "role": "", "listed": true}
			out.append({"node": String(root.get_path_to(mi)), "surface": s, "slot": nm, "family": r["family"], "role": r["role"],
				"listed": r["listed"]})
	return out


## The slot names under `root` that no family lists (sorted, once each).
static func unlisted(root: Node, cfg: RcLookSlotsConfig = null) -> PackedStringArray:
	var seen := {}
	for e: Dictionary in surfaces(root, cfg):
		if not bool(e["listed"]):
			seen[e["slot"]] = true
	var out := PackedStringArray(seen.keys())
	out.sort()
	return out


## Stamps every MeshInstance3D under `root` with META (one "family:role" per surface); returns the unlisted slot names.
static func stamp(root: Node, cfg: RcLookSlotsConfig = null) -> PackedStringArray:
	var per: Dictionary = {}
	for e: Dictionary in surfaces(root, cfg):
		var key := String(e["node"])
		if not per.has(key):
			per[key] = []
		(per[key] as Array).append("%s:%s" % [e["family"], e["role"]])
	for key: String in per:
		var mi := root.get_node(NodePath(key)) if key != "." else root
		mi.set_meta(META, PackedStringArray(per[key]))
	return unlisted(root, cfg)
