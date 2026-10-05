class_name LandmarkAssetChecks
extends RefCounted
## ART-5 5b: the landmark asset check for tools/validate_content.gd. Every corporation has a landmark folder
## (assets/city/landmarks/<corporation id>/) whose manifest.json (written by
## tools/art_pipeline/city/build_landmarks_v1.py) names its source scripts and commit, and every file it lists exists
## with the listed size and sha256; every landmark entry points at a listed file.

const ROOT := "res://assets/city/landmarks"
const REQUIRED_KEYS: Array[String] = ["corp", "version", "source_commit", "source_scripts", "coordinates", "landmarks", "files"]


## The errors for the corporations `corp_ids` (empty when every landmark is in place).
static func errors(corp_ids: Array[StringName]) -> PackedStringArray:
	var out := PackedStringArray()
	for cid in corp_ids:
		out.append_array(corp_errors(cid))
	return out


## The errors for one corporation's landmark folder.
static func corp_errors(cid: StringName) -> PackedStringArray:
	var out := PackedStringArray()
	var mp := "%s/%s/manifest.json" % [ROOT, cid]
	if not FileAccess.file_exists(mp):
		out.append("Landmark %s: no manifest at %s." % [cid, mp])
		return out
	var man: Variant = JSON.parse_string(FileAccess.get_file_as_string(mp))
	if not man is Dictionary:
		out.append("Landmark %s: %s is not a JSON object." % [cid, mp])
		return out
	var m: Dictionary = man
	for k in REQUIRED_KEYS:
		if not m.has(k):
			out.append("Landmark %s: manifest has no '%s'." % [cid, k])
	if not out.is_empty():
		return out
	if String(m["corp"]) != String(cid):
		out.append("Landmark %s: manifest is for '%s'." % [cid, m["corp"]])
	for s: String in m["source_scripts"]:
		if not FileAccess.file_exists("res://" + s):
			out.append("Landmark %s: source script %s is missing." % [cid, s])
	var listed := {}
	for f: Dictionary in m["files"]:
		var p := "res://" + String(f["path"])
		listed[String(f["path"]).get_file()] = true
		if not FileAccess.file_exists(p):
			out.append("Landmark %s: file %s is missing." % [cid, p])
			continue
		var fa := FileAccess.open(p, FileAccess.READ)
		var size := fa.get_length()
		fa.close()
		if size != int(f["bytes"]):
			out.append("Landmark %s: %s is %d bytes, the manifest says %d." % [cid, p, size, int(f["bytes"])])
		elif FileAccess.get_sha256(p) != String(f["sha256"]):
			out.append("Landmark %s: %s does not match its sha256 (rebuild and re-assemble)." % [cid, p])
	var glbs := 0
	for e: Dictionary in m["landmarks"]:
		if not listed.has(String(e.get("file", ""))):
			out.append("Landmark %s: entry %s names an unlisted file '%s'." % [cid, e.get("job", "?"), e.get("file", "")])
		if String(e.get("file", "")).ends_with(".glb"):
			glbs += 1
	if glbs == 0:
		out.append("Landmark %s: no glTF landmark." % cid)
	return out
