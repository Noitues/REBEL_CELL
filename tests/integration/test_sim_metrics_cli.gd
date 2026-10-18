extends GutTest
## N19 flow smoke: a real balance.py fight sweep emits the phase metrics, and `compare` renders the phase columns.
## CLI plumbing and markdown rendering get this smoke only.

const SCRIPT := "res://tools/balance/balance.py"


func _py(args: Array) -> int:
	var all := PackedStringArray([ProjectSettings.globalize_path(SCRIPT)])
	for a in args:
		all.append(String(a))
	var out: Array = []
	return OS.execute("python", all, out, true)


func test_sweep_emits_phase_metrics_and_compare_renders_columns() -> void:
	var dir := ProjectSettings.globalize_path("user://n19_cli")
	DirAccess.make_dir_recursive_absolute(dir)
	var rc := _py(["run", "fight", "--name", "n19a", "--enemy", "claims_adjuster", "--tiers", "1", "--seeds", "1000:1001", "-j", "1",
		"--out-dir", dir])
	if rc == -1:
		pending("python is not on PATH here")
		return
	assert_eq(rc, 0, "the sweep ran")
	var data = JSON.parse_string(FileAccess.get_file_as_string("user://n19_cli/n19a.json"))
	assert_not_null(data)
	assert_eq(data["records"].size(), 2)
	for r in data["records"]:
		assert_true(r.has("metrics"), "each fight record carries metrics")
		assert_gt(r["metrics"]["phases"].size(), 0)
	assert_true(FileAccess.get_file_as_string("user://n19_cli/n19a.md").contains("Phase metrics"))
	var cmp := ProjectSettings.globalize_path("user://n19_cli/cmp.md")
	assert_eq(_py(["compare", dir + "/n19a.json", dir + "/n19a.json", "--name", "n19", "--out", cmp]), 0)
	var text := FileAccess.get_file_as_string("user://n19_cli/cmp.md")
	assert_true(text.contains("Phase metrics (N19)"))
	assert_true(text.contains("| group |"))
	for f in DirAccess.get_files_at("user://n19_cli"):
		DirAccess.remove_absolute("user://n19_cli/" + f)
