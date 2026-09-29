extends GutTest
## Every test script compiles (Animation pass review: GUT skipped a test file that failed
## to parse, silently, for two batches). ANIM-R5: split out of test_suite_integrity.gd:
## loading every test script loads (and compiles) the whole game behind it, most of a
## minute on its own, so it sits in the full tier with its measured time and the integrity
## rules stay fast. The parallel runner also reports any script that did not run.

## The folder every test script (and helper) lives under.
const TESTS_ROOT := "res://tests"
## Fewer scripts than this means the walk found the wrong folder.
const MIN_SCRIPTS := 50


func _scripts(dir: String, out: Array[String]) -> void:
	for f in DirAccess.get_files_at(dir):
		if f.ends_with(".gd"):
			out.append(dir.path_join(f))
	for d in DirAccess.get_directories_at(dir):
		_scripts(dir.path_join(d), out)


func test_every_test_script_compiles() -> void:
	var paths: Array[String] = []
	_scripts(TESTS_ROOT, paths)
	assert_gt(paths.size(), MIN_SCRIPTS, "the suite's scripts were found")
	for p in paths:
		var s := load(p) as GDScript
		assert_not_null(s, "%s loads" % p)
		if s != null:
			assert_true(s.can_instantiate(), "%s compiles" % p)
