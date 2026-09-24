extends GutTest
## Placeholder audio (GDD 10): generated streams exist, the ratchet maps to actions,
## precision feedback maps to tiers, music switches by context with Heat layers.


func before_each() -> void:
	AudioDirector.muted = true
	AudioDirector.played.clear()


func after_each() -> void:
	AudioDirector.muted = false
	AudioDirector.stop_music()


func test_every_placeholder_sound_is_generated() -> void:
	for name in ["tick", "click", "clack", "latch", "stutter", "static", "stamp", "jack_in", "alarm"]:
		assert_true(AudioDirector._sfx.has(name), name)
		var wav: AudioStreamWAV = AudioDirector._sfx[name]
		assert_true(wav.data.size() > 100, "%s has samples" % name)


func test_precision_feedback_maps_to_the_gdd_sounds() -> void:
	AudioDirector.play_precision(RC.PrecisionTier.PERFECT, false)
	AudioDirector.play_precision(RC.PrecisionTier.GOOD, false)
	AudioDirector.play_precision(RC.PrecisionTier.PARTIAL, false)
	AudioDirector.play_precision(RC.PrecisionTier.PERFECT, true)
	assert_eq(AudioDirector.played, ["latch", "click", "stutter", "static"])


func test_spin_is_a_run_of_clicks_and_music_follows_context() -> void:
	AudioDirector.play_spin(7)
	assert_eq(AudioDirector.played, ["spin:7"])
	AudioDirector.play_music("combat")
	AudioDirector.play_music("combat")
	AudioDirector.play_music("boss")
	assert_eq(AudioDirector.played.slice(1), ["music:combat", "music:boss"], "no restart on the same context")
	AudioDirector.set_heat_layers(5)
	assert_eq(AudioDirector.heat_layers, 3, "clamped to three layers")
	for ctx in AudioDirector.CONTEXTS:
		var wav: AudioStreamWAV = AudioDirector._make_music(ctx)
		assert_eq(wav.loop_mode, AudioStreamWAV.LOOP_FORWARD, "%s loops" % ctx)
