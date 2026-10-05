class_name LandmarkAssetChecks
extends RefCounted
## ART-5 5b: the landmark asset check for tools/validate_content.gd. Every corporation has a landmark folder
## (assets/city/landmarks/<corporation id>/) whose manifest.json (schema rebel_cell.art_export/1, written by
## tools/art_pipeline/city/build_landmarks_v1.py) names its source scripts, commit and pipeline hash; every file it
## lists exists with the listed size and sha256; every landmark entry points at a listed file and carries its origin
## and footprint; the pipeline has not changed since the export (scripts_sha256).

const ROOT := "res://assets/city/landmarks"
const SCHEMA := "rebel_cell.art_export/1"
const REQUIRED_KEYS: Array[String] = ["schema", "corp", "source", "settings", "origin", "footprint", "materials", "landmarks", "files"]


## The errors for the corporations `corp_ids` (empty when every landmark is in place).
static func errors(corp_ids: Array[StringName]) -> PackedStringArray:
	var out := PackedStringArray()
	for cid in corp_ids:
		out.append_array(corp_errors(cid))
	return out


## The errors for one corporation's landmark folder.
static func corp_errors(cid: StringName) -> PackedStringArray:
	var out := PackedStringArray()
	var dir := "%s/%s" % [ROOT, cid]
	var mp := dir + "/manifest.json"
	if not FileAccess.file_exists(mp):
		out.append("Landmark %s: no manifest at %s." % [cid, mp])
		return out
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(mp))
	if not parsed is Dictionary:
		out.append("Landmark %s: %s is not a JSON object." % [cid, mp])
		return out
	var m: Dictionary = parsed
	for k in REQUIRED_KEYS:
		if not m.has(k):
			out.append("Landmark %s: manifest has no '%s'." % [cid, k])
	if not out.is_empty():
		return out
	if String(m["schema"]) != SCHEMA:
		out.append("Landmark %s: schema '%s', expected %s." % [cid, m["schema"], SCHEMA])
	if String(m["corp"]) != String(cid):
		out.append("Landmark %s: manifest is for '%s'." % [cid, m["corp"]])
	var src: Dictionary = m["source"]
	var scripts: Array = src.get("scripts", [])
	for s: String in scripts:
		if not FileAccess.file_exists("res://" + s):
			out.append("Landmark %s: source script %s is missing." % [cid, s])
	if out.is_empty() and pipeline_sha256(scripts) != String(src.get("scripts_sha256", "")):
		out.append("Landmark %s: the pipeline changed since the export (scripts_sha256); rebuild and re-assemble." % cid)
	var listed := {}
	for f: Dictionary in m["files"]:
		var p := dir + "/" + String(f["path"])
		listed[String(f["path"])] = true
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
		var file := String(e.get("file", ""))
		if not listed.has(file):
			out.append("Landmark %s: entry %s names an unlisted file '%s'." % [cid, e.get("job", "?"), file])
		if file.ends_with(".glb"):
			glbs += 1
			if not e.has("origin") or not e.has("footprint"):
				out.append("Landmark %s: entry %s has no origin or footprint." % [cid, e.get("job", "?")])
	if glbs == 0:
		out.append("Landmark %s: no glTF landmark." % cid)
	return out


## The pipeline hash of build_landmarks_v1.scripts_sha256: SHA-256 over each script's path relative to
## tools/art_pipeline/city/ and its content with CRLF read as LF, in the listed order.
static func pipeline_sha256(scripts: Array) -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	for s: String in scripts:
		ctx.update(s.trim_prefix("tools/art_pipeline/city/").to_utf8_buffer())
		ctx.update(_lf(FileAccess.get_file_as_bytes("res://" + s)))
	return ctx.finish().hex_encode()


## `b` with every CR LF pair read as LF (bytes, so a BOM or any encoding hashes as Python reads it).
static func _lf(b: PackedByteArray) -> PackedByteArray:
	if b.find(13) < 0:
		return b
	var out := PackedByteArray()
	out.resize(b.size())
	var n := 0
	for i in b.size():
		if b[i] == 13 and i + 1 < b.size() and b[i + 1] == 10:
			continue
		out[n] = b[i]
		n += 1
	out.resize(n)
	return out
