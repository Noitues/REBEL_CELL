extends SceneTree
## Parse check with the autoloads registered (tools/precommit.sh's fallback): Godot's
## `--check-only -s <file>` compiles without the project's autoloads, so a script that loads a
## scene script naming one (a visual QA pack preloading the HQ, the review pack's Settings) fails
## there though it compiles in the game. This loads each script named after `--` the way the
## game does and exits 1 when one does not compile.
##
##   godot --headless --path . -s tools/parse_check.gd -- res://tools/visual_qa/perf_pack.gd


func _initialize() -> void:
	var bad := 0
	for a in OS.get_cmdline_user_args():
		var path := a if a.begins_with("res://") else "res://" + a
		var s := load(path) as Script
		if s == null or not s.can_instantiate():
			print("PARSE_CHECK FAIL %s" % path)
			bad += 1
		else:
			print("PARSE_CHECK OK %s" % path)
	quit(1 if bad > 0 else 0)
