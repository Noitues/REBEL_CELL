extends SceneTree
## Parse check for tools/precommit.sh: compiles every script given after "--" (any number: one process checks a whole change, D15) and exits 1 if one fails.
## `godot --check-only -s <file>` stops before the autoloads are registered as global names, so
## every script that names one (Dialogue, Settings, ...) failed there; loaded from here, they exist.
##
##   godot --headless --path . -s tools/parse_check.gd -- res://scripts/ui/netrun_scene.gd


func _initialize() -> void:
	var rc := 0
	for a in OS.get_cmdline_user_args():
		var path := a if a.begins_with("res://") else "res://" + a
		var script := load(path) as Script  # a fresh process per check: the cache holds the file as it is now
		if script == null or not script.can_instantiate():
			printerr("PARSE CHECK FAIL: %s" % path)
			rc = 1
	quit(rc)
