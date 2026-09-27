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
	for e in errors:
		printerr("  - ", e)
	print("Content: %d resources, %d ids, config %s, motion %s." % [
		registry.resource_count(), registry.all_ids().size(),
		"loaded" if registry.config != null else "MISSING",
		("%d entries" % registry.motion.entries.size()) if registry.motion != null else "MISSING"])
	print("CONTENT VALIDATION: ", "PASS" if errors.is_empty() else "FAIL (%d)" % errors.size())
	registry.free()
	quit(0 if errors.is_empty() else 1)


## The UI motion table must exist at its path (H24-anim A1) and carry every animation id
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
