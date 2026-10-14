extends GutTest
## Change plan 1, wave 1b, slice 1B-COMBAT (PT-002a F10, F12; docs/handoff/plan1/W1B.md).
## F10: one backdrop per fight. The close-up was swapped in over the still whenever the city
## finished building (the playtester saw it as the hover on the enemy wheel); now the backdrop
## holds on its night sky for the close-up and gives it up for the still past
## CityConfig.backdrop_city_wait_s, and hovering a wheel never touches the backdrop.
## F12: SKIP on the loot page skips the current reward only; the others stay (verified, kept as
## the regression guard). Headless: no close-up is built (CityView3D.can_render), so the hold is
## checked through its pure step and the hover through the real combat scene's signals.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)

var _reduce: bool
var _scale: float


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_plan1_1b_combat"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	Fx.apply_settings()
	Motion.force_live = false
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


# --- F10: one backdrop per fight -----------------------------------------------------------------

func test_the_hold_waits_then_shows_the_close_up_or_gives_up_for_the_still() -> void:
	var wait := CityView3D.CONFIG.backdrop_city_wait_s
	assert_gt(wait, 0.0, "the wait is config, above zero")
	var w := 0.0
	w = CombatBackdrop.hold_step(w, wait * 0.25, false, wait)
	assert_almost_eq(w, wait * 0.25, 0.0001, "still waiting: the seconds add up")
	assert_eq(CombatBackdrop.hold_step(w, 0.01, true, wait), CombatBackdrop.HOLD_DONE, "ready in time: the close-up is the fight's picture")
	assert_eq(CombatBackdrop.hold_step(w, wait, false, wait), CombatBackdrop.HOLD_GIVE_UP, "past the wait: the still, for the whole fight")
	# Once chosen, nothing (a late close-up, a hover, more time) chooses again.
	assert_eq(CombatBackdrop.hold_step(CombatBackdrop.HOLD_DONE, 10.0, false, wait), CombatBackdrop.HOLD_DONE)
	assert_eq(CombatBackdrop.hold_step(CombatBackdrop.HOLD_DONE, 10.0, true, wait), CombatBackdrop.HOLD_DONE)
	assert_eq(CombatBackdrop.hold_step(w, -1.0, false, wait), w, "a negative delta never moves the wait back")


func test_hovering_the_enemy_wheel_never_changes_the_backdrop() -> void:
	RunManager.new_campaign(1)
	RunManager.campaign.corporation_id = &"solace"
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"compliance_officer", 5)
	await _frames(4)
	var bd: CombatBackdrop = scene.arena_backdrop
	var place := bd.place.duplicate()
	var tex: Texture2D = bd.get(&"_tex")
	assert_false(place.is_empty(), "the fight has its place")
	assert_eq(StringName(place["corp"]), &"solace", "the Compliance Officer stands at a Solace place")
	assert_false(bd.holding(), "headless: no close-up to wait for")
	var enemy: WheelView = null
	for v in scene._views():
		if v.combatant != null and not v.combatant.is_player:
			enemy = v
	assert_not_null(enemy, "the enemy wheel")
	for ring in [RC.RingScope.OUTER, RC.RingScope.INNER]:
		for dir in [1, -1]:
			enemy.arrow_hovered.emit({"ring": ring, "direction": dir})
			await _frames(2)
			assert_eq(bd.place, place, "hover ring %d dir %d: the same place" % [ring, dir])
			assert_eq(bd.get(&"_tex"), tex, "hover ring %d dir %d: the same picture" % [ring, dir])
			assert_eq(bd.on_city(), false)
	enemy.arrow_hovered.emit({})
	await _frames(2)
	assert_eq(bd.place, place, "leaving the wheel: the same place")
	assert_eq(bd.get(&"_tex"), tex, "leaving the wheel: the same picture")


# --- F12: SKIP skips the current reward only --------------------------------------------------------

func test_skip_skips_only_the_current_reward_and_the_others_stay() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.new_campaign(1)
	scene.start_run(1)
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.pending_rewards.append({"kind": "firmware", "options": ["leech", "overvolt"]})
	run.phase = RunState.Phase.REWARD
	scene._show_current()
	await _frames(4)
	var deck := run.operative.deck.size()
	assert_true(scene.rewards_list_on(), "W4: two picks list as rows; the card row opens its page")
	scene.open_reward(0)
	await _frames(4)
	var skip := scene.find_child("Skip", true, false) as BaseButton
	assert_not_null(skip, "the card page's SKIP")
	skip.pressed.emit()
	await _frames(4)
	assert_eq(run.phase, RunState.Phase.REWARD, "the Firmware offer is still to come")
	assert_eq(run.pending_rewards.size(), 1, "one reward skipped, one left")
	assert_eq(String(RunManager.netrun.current_reward()["kind"]), "firmware", "the Firmware offer stays")
	assert_eq(run.operative.deck.size(), deck, "no card taken")
	scene.open_reward(0)
	await _frames(4)
	skip = scene.find_child("Skip", true, false) as BaseButton
	assert_not_null(skip, "the Firmware page shows, with its own SKIP")
	skip.pressed.emit()
	await _frames(4)
	assert_true(run.pending_rewards.is_empty(), "the last reward skipped")
	assert_ne(run.phase, RunState.Phase.REWARD, "the run goes on once every reward is resolved")
