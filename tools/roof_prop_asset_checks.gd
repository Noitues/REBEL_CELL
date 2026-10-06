class_name RoofPropAssetChecks
extends RefCounted
## ART-5 5e: the roof props' asset check for tools/validate_content.gd (as LandmarkAssetChecks):
## assets/city/roof_props/manifest.json (rebel_cell.art_export/1, written by
## tools/art_pipeline/city/build_roof_props_v1.py) names its source scripts and pipeline hash
## (unchanged since the export), every listed file has its size and sha256, and the glTF holds
## every prop CityRoofProps places (PROPS).

const DIR := "res://assets/city/roof_props"
## The props CityRoofProps places (CityRoofProps.names(); test_art5_city_integration checks they agree).
const PROPS: Array[String] = ["ac", "tank", "antenna", "billboard_0", "billboard_1", "billboard_2", "billboard_3"]


## The errors (empty when the roof props are in place).
static func errors() -> PackedStringArray:
	var out := PackedStringArray()
	var mp := DIR + "/manifest.json"
	if not FileAccess.file_exists(mp):
		out.append("Roof props: no manifest at %s." % mp)
		return out
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(mp))
	if not parsed is Dictionary:
		out.append("Roof props: %s is not a JSON object." % mp)
		return out
	var m: Dictionary = parsed
	for k in ["schema", "source", "settings", "origin", "materials", "props", "files"]:
		if not m.has(k):
			out.append("Roof props: manifest has no '%s'." % k)
	if not out.is_empty():
		return out
	if String(m["schema"]) != LandmarkAssetChecks.SCHEMA:
		out.append("Roof props: schema '%s', expected %s." % [m["schema"], LandmarkAssetChecks.SCHEMA])
	var scripts: Array = (m["source"] as Dictionary).get("scripts", [])
	for sc: String in scripts:
		if not FileAccess.file_exists("res://" + sc):
			out.append("Roof props: source script %s is missing." % sc)
	if out.is_empty() and LandmarkAssetChecks.pipeline_sha256(scripts) != String((m["source"] as Dictionary).get("scripts_sha256", "")):
		out.append("Roof props: the pipeline changed since the export (scripts_sha256); rebuild and re-assemble.")
	for f: Dictionary in m["files"]:
		var p := DIR + "/" + String(f["path"])
		if not FileAccess.file_exists(p):
			out.append("Roof props: file %s is missing." % p)
			continue
		var fa := FileAccess.open(p, FileAccess.READ)
		var size := fa.get_length()
		fa.close()
		if size != int(f["bytes"]):
			out.append("Roof props: %s is %d bytes, the manifest says %d." % [p, size, int(f["bytes"])])
		elif FileAccess.get_sha256(p) != String(f["sha256"]):
			out.append("Roof props: %s does not match its sha256 (rebuild and re-assemble)." % p)
	var props: Dictionary = m["props"]
	var glb := DIR + "/roof_props.glb"
	var scene := load(glb) as PackedScene if ResourceLoader.exists(glb) else null
	if scene == null:
		out.append("Roof props: %s does not load." % glb)
		return out
	var root := scene.instantiate()
	var meshes := {}
	for mi in root.find_children("*", "MeshInstance3D", true, false):
		meshes[String(mi.name)] = true
	root.free()
	for nm in PROPS:
		if not props.has(nm):
			out.append("Roof props: the manifest lists no '%s'." % nm)
		elif not meshes.has(nm):
			out.append("Roof props: %s has no mesh '%s'." % [glb, nm])
	return out
