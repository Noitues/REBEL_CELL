extends GutTest
## Playtest tooling rules (tooling slice T1): gate profiles list the right testers, screen testers
## do not escalate on combat turn starts by default, the batch cost is counted once, parity pairs
## turns by replay. The checks live in tools/playtest/test_playtest_tools.py (no API, no game).


func test_playtest_tools_unit_tests_pass() -> void:
	var out: Array = []
	var code := OS.execute("python", [ProjectSettings.globalize_path("res://tools/playtest/test_playtest_tools.py")], out, true)
	if code == -1:
		pending("python is not on PATH here: run tools/playtest/test_playtest_tools.py by hand")
		return
	var text := "\n".join(out)
	assert_eq(code, 0, "tools/playtest/test_playtest_tools.py passes:\n%s" % text)
	assert_true(text.contains("OK"), "unittest says OK")
