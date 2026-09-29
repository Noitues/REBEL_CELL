extends SceneTree
## W10: writes or prints the static visual lint (tools/visual_qa/visual_lint_static.gd).
## Run through `python tools/visual_qa/update_lint_baseline.py` (it redirects the output
## and adds a timeout), or directly:
##
##   godot --headless --path . -s res://tools/visual_qa/lint_static_cli.gd -- [--write=lower|reset] [--report=<file.json>]
##
## --write=lower  lowers each file-rule count in lint_baseline.json to today's count (never
##                raises one; the default for the update script).
## --write=reset  writes today's counts as they are (raises too: only on the designer's say).
## --report=<f>   writes every finding with its lines to <f> (JSON).

const Lint := preload("res://tools/visual_qa/visual_lint_static.gd")


func _init() -> void:
	var mode := ""
	var report := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--write="):
			mode = a.trim_prefix("--write=")
		elif a.begins_with("--report="):
			report = a.trim_prefix("--report=")
	var findings := Lint.scan_all()
	var now := Lint.counts(findings)
	var base := Lint.load_baseline()
	var cmp := Lint.compare(findings, base)
	for l in cmp["up"]:
		print("UP   ", l)
	for l in cmp["down"]:
		print("DOWN ", l)
	if report != "":
		var f := FileAccess.open(report, FileAccess.WRITE)
		if f != null:
			f.store_string(JSON.stringify({"files": findings, "counts": now}, "\t", true))
			f.close()
	if mode == "lower" or mode == "reset":
		var out := {}
		var paths := {}
		for p in now:
			paths[p] = true
		if mode == "lower":
			for p in base:
				paths[p] = true
		var keys := paths.keys()
		keys.sort()
		for p in keys:
			var per := {}
			for r in Lint.RULES:
				var n := int((now.get(p, {}) as Dictionary).get(r, 0))
				if mode == "lower" and not base.is_empty():
					n = mini(n, int((base.get(p, {}) as Dictionary).get(r, 0)))
				if n > 0:
					per[r] = n
			if not per.is_empty():
				out[p] = per
		var doc := {
			"about": "W10 static visual lint baseline (tests/unit/test_visual_lint_static.gd): per file under scripts/ui, the count of lines per rule (literal colours, literal font sizes). A count may only go down. Lower it with python tools/visual_qa/update_lint_baseline.py after migrating a file.",
			"rules": Lint.RULES,
			"files": out,
		}
		var f := FileAccess.open(Lint.BASELINE, FileAccess.WRITE)
		f.store_string(JSON.stringify(doc, "\t", false) + "\n")
		f.close()
		print("LINT BASELINE WRITTEN (%s) %d files" % [mode, out.size()])
	var total := 0
	for p in now:
		for r in now[p]:
			total += int(now[p][r])
	print("LINT STATIC DONE %d findings in %d files, %d up, %d down" % [total, now.size(), (cmp["up"] as Array).size(), (cmp["down"] as Array).size()])
	quit(1 if not (cmp["up"] as Array).is_empty() and mode == "" else 0)
