extends SceneTree
## Schema smoke test. Run headless from the project root:
##   godot --headless --path . -s tools/schema_smoke_test.gd
## Exits with code 0 when every check passes. The checks are in
## tools/schema_smoke_checks.gd (a schema change adds its check there).
##
## ANIM-R5 P17: this file is a runner on purpose. When the checks were compiled as part of the
## `-s` script itself, their dozens of data classes were loaded as that script's dependencies
## before any content, and about one exit in ten crashed after PASS (exit 139: an access
## violation inside the engine's GDScript clean-up at shutdown, GDScript::clear on a script
## already freed; the order the class scripts were loaded in decides whether it happens).
## Loading the content first, the way the game and tools/validate_content.gd do, and only
## then the checks, gives the clean-up a load order that exits cleanly (DECISIONS "Animation
## pass - ANIM-R5 city, raid, HQ and bake", P17: the runs measured).

const RegistryScript := preload("res://scripts/autoload/content_registry.gd")
const CHECKS_PATH := "res://tools/schema_smoke_checks.gd"


func _init() -> void:
	var registry: Node = RegistryScript.new()
	registry.scan_directory(registry.CONTENT_ROOT)
	registry.free()
	var checks: RefCounted = (load(CHECKS_PATH) as GDScript).new()
	var fails: int = checks.call(&"run")
	checks = null
	print("SCHEMA SMOKE TEST: ", "PASS" if fails == 0 else "FAIL (%d)" % fails)
	quit(0 if fails == 0 else 1)
