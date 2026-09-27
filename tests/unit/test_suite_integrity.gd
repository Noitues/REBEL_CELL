extends GutTest
## Every test script compiles (Animation pass review: GUT skipped a test file that failed
## to parse, silently, for two batches).


func _scripts(dir: String, out: Array[String]) -> void:
	for f in DirAccess.get_files_at(dir):
		if f.ends_with(".gd"):
			out.append(dir.path_join(f))
	for d in DirAccess.get_directories_at(dir):
		_scripts(dir.path_join(d), out)


func test_every_test_script_compiles() -> void:
	var paths: Array[String] = []
	_scripts("res://tests", paths)
	assert_gt(paths.size(), 50, "the suite's scripts were found")
	for p in paths:
		var s := load(p) as GDScript
		assert_not_null(s, "%s loads" % p)
		if s != null:
			assert_true(s.can_instantiate(), "%s compiles" % p)
