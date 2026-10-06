extends SceneTree
## Content validation. Loads every resource under res://content (and the resources
## nested inside them), then prints every validate() error and duplicate id.
##   godot --headless --path . -s tools/validate_content.gd
## Exits with code 0 when there are no errors.

const RegistryScript := preload("res://scripts/autoload/content_registry.gd")


func _init() -> void:
	var registry: Node = RegistryScript.new()
	var errors: PackedStringArray = registry.scan_directory(registry.CONTENT_ROOT)
	errors.append_array(registry.validate())
	errors.append_array(_motion_errors(registry.motion))
	errors.append_array(_hq_compound_errors(registry))
	errors.append_array(LandmarkAssetChecks.errors(_corporation_ids(registry)))
	errors.append_array(RoofPropAssetChecks.errors())  # ART-5 5e
	for e in errors:
		printerr("  - ", e)
	print("Content: %d resources, %d ids, config %s, motion %s." % [
		registry.resource_count(), registry.all_ids().size(),
		"loaded" if registry.config != null else "MISSING",
		("%d entries" % registry.motion.entries.size()) if registry.motion != null else "MISSING"])
	print("CONTENT VALIDATION: ", "PASS" if errors.is_empty() else "FAIL (%d)" % errors.size())
	registry.free()
	quit(0 if errors.is_empty() else 1)


## ART-5 5b: the corporation ids (each owns a landmark under assets/city/landmarks/), sorted.
func _corporation_ids(registry: Node) -> Array[StringName]:
	var out: Array[StringName] = []
	for id: StringName in registry.all_ids():
		var r: Resource = registry.get_content(id)
		if r is CorporationData:
			out.append(id)
	out.sort()
	return out


## The UI motion table must exist at its path (Animation pass ANIM-1) and carry every animation id
## the kit and the roadmap name (ANIMATION_HANDOFF 4).
func _motion_errors(motion: UiMotionData) -> PackedStringArray:
	var errors := PackedStringArray()
	if motion == null:
		errors.append("No UiMotionData found (expected %s)." % RegistryScript.MOTION_PATH)
		return errors
	if motion.resource_path != RegistryScript.MOTION_PATH:
		errors.append("UiMotionData at %s, expected %s." % [motion.resource_path, RegistryScript.MOTION_PATH])
	for id in UiMotionData.REQUIRED_IDS:
		if motion.find(id) == null:
			errors.append("UiMotionData has no entry '%s'." % id)
	return errors


## ART-8 8p validator hook: every corporation has its HQ compound layout, each layout fits the
## run map (a row per layer before the final one, a slot per possible node) and its model
## folder holds a manifest for that corporation whose listed files all exist.
## tools/art_pipeline/city/validate_hq_compounds.py checks the exports in depth.
func _hq_compound_errors(registry: Node) -> PackedStringArray:
	var errors := PackedStringArray()
	var cfg: CampaignConfigData = registry.config
	for id in registry.all_ids():
		var res: Resource = registry.get_content(id)
		if res is CorporationData and not registry.has_content(HqCompoundLayoutData.id_for(id)):
			errors.append("Corporation %s has no HQ compound layout (%s)." % [id, HqCompoundLayoutData.id_for(id)])
		if not res is HqCompoundLayoutData:
			continue
		var l := res as HqCompoundLayoutData
		if cfg != null and (l.layer_rows() != cfg.map_layers - 1 or l.slots_per_layer != cfg.map_nodes_max):
			errors.append("%s: %d rows of %d, expected %d of %d." % [id, l.layer_rows(), l.slots_per_layer, cfg.map_layers - 1, cfg.map_nodes_max])
		var f := FileAccess.open(l.asset_dir + "/manifest.json", FileAccess.READ)
		if f == null:
			errors.append("%s: no manifest.json in %s." % [id, l.asset_dir])
			continue
		var m: Variant = JSON.parse_string(f.get_as_text())
		if not m is Dictionary or String(m.get("corp", "")) != String(l.corporation_id):
			errors.append("%s: manifest.json does not describe %s." % [id, l.corporation_id])
			continue
		for entry in m.get("files", []):
			if not FileAccess.file_exists(l.asset_dir + "/" + String(entry.get("path", ""))):
				errors.append("%s: manifest file %s is missing." % [id, entry.get("path", "")])
	return errors
