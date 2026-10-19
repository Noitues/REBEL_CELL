extends GutTest
## Array.sort() on StringNames orders by interned address, not text (PT-004 SORTSWEEP). Every
## sort of an id array goes through IdSort; this scans scripts/ and tools/ for a bare .sort()
## and fails on any array not proven to hold ints, floats, Vector2i or Strings.

const ROOTS: Array[String] = ["res://scripts", "res://tools"]

## "file name:variable" pairs proven to hold ints, floats, Vector2i, paths or Strings only.
const ALLOWED: Array[String] = [
	"na22_lab.gd:keys", "netrun_art_layout.gd:members", "netrun_hq_orbit.gd:faces", "netrun_street_deriver.gd:keys", "netrun_street_deriver.gd:fb",  # NA-21 / NA-23b: int part / face / layer indices
	"content_registry.gd:paths", "save_service.gd:out", "city_mesh_kit.gd:keys",
	"city_motion_site.gd:keys", "city_layout_ruler.gd:keys", "city_view_3d.gd:keys", "campaign_rules.gd:crosses",
	"heat_rules.gd:out", "map_graph.gd:targets", "netrun_session.gd:ids",
	"raid_resolver.gd:steps", "campaign_config_data.gd:out", "netrun_art_export.gd:bids",
	"netrun_art_export.gd:corps", "netrun_art_export.gd:sorted_keys", "dossier_facts.gd:heat_marks",
	"bit_path.gd:out", "flash_limiter.gd:sorted", "hq_scene.gd:from", "city_layout.gd:key",
	"combat_fx_layer.gd:out", "mainframe_sign.gd:names", "bits_path.gd:out", "motion.gd:out",
	"text_db.gd:out", "netrun_scene.gd:kids", "city_perf_probe.gd:sorted", "na25_e2e_lab.gd:sorted", "profile_frames.gd:_times",
	"schema_check.gd:keys", "lint_static_cli.gd:keys", "perf_pack.gd:sorted", "perf_pack.gd:names",
	"visual_lint_static.gd:out", "visual_lint_static.gd:sorted",
	"wheel_state.gd:status_ints", "result_chip_model.gd:seen_statuses",
]


func _gd_files(dir: String, out: Array[String]) -> void:
	for sub in DirAccess.get_directories_at(dir):
		_gd_files(dir.path_join(sub), out)
	for f in DirAccess.get_files_at(dir):
		if f.ends_with(".gd"):
			out.append(dir.path_join(f))


func test_no_bare_sort_on_id_arrays() -> void:
	var re := RegEx.create_from_string("([A-Za-z_][A-Za-z0-9_.]*)\\.sort\\(\\)")
	var files: Array[String] = []
	for r in ROOTS:
		_gd_files(r, files)
	assert_gt(files.size(), 100, "the scan found the sources")
	var bad: Array[String] = []
	for path in files:
		for line in FileAccess.get_file_as_string(path).split("\n"):
			var m := re.search(line)
			if m == null or line.strip_edges().begins_with("#"):
				continue
			var key := "%s:%s" % [path.get_file(), m.get_string(1).get_slice(".", m.get_string(1).count(".")) ]
			if not ALLOWED.has(key):
				bad.append("%s  %s" % [path, line.strip_edges()])
	assert_eq(bad, [] as Array[String], "bare .sort() on a possible id array: use IdSort.sort_ids")


func test_sort_ids_is_text_order_whatever_was_interned_first() -> void:
	# intern in reverse text order so address order disagrees with text order
	var z := StringName("zz_ptsort_c")
	var y := StringName("zz_ptsort_b")
	var x := StringName("zz_ptsort_a")
	var ids: Array[StringName] = [z, x, y]
	IdSort.sort_ids(ids)
	assert_eq(ids, [x, y, z] as Array[StringName], "text order")
	var mixed: Array = [&"b", "a", &"c"]
	IdSort.sort_ids(mixed)
	assert_eq(mixed.map(func(v: Variant) -> String: return String(v)), ["a", "b", "c"], "String and StringName mix by text")
	var nums: Array = [10, 9, 100]
	IdSort.sort_ids(nums)
	assert_eq(nums, [9, 10, 100], "ints keep numeric order")
	assert_true(IdSort.less(&"a", &"b") and not IdSort.less(&"b", &"a"))
