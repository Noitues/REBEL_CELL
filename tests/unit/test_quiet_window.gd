extends GutTest
## Quiet windowed runs (tools/run_windowed.py, docs/TEST_SUITE.md "Windowed checks"): the
## switch reads the environment or a user arg, is off otherwise, and the off-screen spot is
## off every screen.


func test_quiet_window_is_off_by_default() -> void:
	assert_false(Settings.quiet_window_from(PackedStringArray(), ""), "no arg, no environment: a normal window")
	assert_false(Settings.quiet_window_from(PackedStringArray(["--demo-run"]), "0"), "other args and 0 leave it off")


func test_quiet_window_from_environment_or_arg() -> void:
	assert_true(Settings.quiet_window_from(PackedStringArray(), "1"), "the environment flag run_windowed.py sets")
	assert_true(Settings.quiet_window_from(PackedStringArray(["--demo-run", Settings.QUIET_WINDOW_ARG]), ""), "the user arg")


func test_this_test_run_is_not_quiet() -> void:
	# The suite runs headless; a quiet flag leaking into it would mute AudioDirector tests.
	assert_false(Settings.quiet_window_from(OS.get_cmdline_user_args(), ""), "GUT gets no quiet arg")


func test_quiet_position_is_off_every_screen() -> void:
	var spot := Rect2i(Settings.QUIET_WINDOW_POSITION, Vector2i(3840, 2160))
	for i in DisplayServer.get_screen_count():
		assert_false(spot.intersects(Rect2i(DisplayServer.screen_get_position(i), DisplayServer.screen_get_size(i))), "screen %d" % i)
	assert_lt(Settings.QUIET_WINDOW_POSITION.x + 3840, 0, "left of any screen at the origin")
