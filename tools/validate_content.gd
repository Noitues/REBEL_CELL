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
	for e in errors:
		printerr("  - ", e)
	print("Content: %d resources, %d ids, config %s." % [
		registry.resource_count(), registry.all_ids().size(),
		"loaded" if registry.config != null else "MISSING"])
	print("CONTENT VALIDATION: ", "PASS" if errors.is_empty() else "FAIL (%d)" % errors.size())
	registry.free()
	quit(0 if errors.is_empty() else 1)
