extends GutTest
## Change plan 1, W1-TAG: the enemy's precision tag is the pointer's projection after the hovered play,
## so what the tag says is exactly where the pointer reads once that play is really made (preview = result).
## V1 saw "NULL . good aim" on the tag while the pointer showed OVERFLOW: the tag is the AFTER, the pointer the NOW.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SCREEN := Vector2(1280, 720)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.scene_switching_enabled = false
	RunManager.reset()


func after_each() -> void:
	AudioDirector.muted = false
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _combat(combat_seed: int) -> Control:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"collections_agent", combat_seed)
	await _frames()
	return scene


## The first hand card that can be played now and is not a random one (random previews show odds, not a slice).
func _pick(scene: Control, skip: int = -1) -> int:
	var st: CombatState = scene.engine.state()
	for i in st.hand.size():
		var card := scene.engine.content(st.hand[i]) as CardData
		var opts := CardTargeting.options(scene.engine.resolver, st, i)
		if card == null or opts.is_empty() or CardTargeting.is_random(card) or i == skip:
			continue
		if scene.engine.validate(opts[0]) == "" and card.ram_cost <= st.ram:
			return i
	return -1


func _enemy_tag(scene: Control) -> String:
	var st: CombatState = scene.engine.state()
	return String(scene._landing_title(st, st.enemies[0])["text"])


func _agree(combat_seed: int, played: int) -> int:
	var scene: Control = await _combat(combat_seed)
	for k in played:
		var p := _pick(scene)
		if p < 0:
			scene.get_parent().queue_free()
			return 0
		scene.play_card(p)
		scene.skip_motion()
		await _frames(2)
	var checked := 0
	var st: CombatState = scene.engine.state()
	for i in st.hand.size():
		if _pick(scene) != i:
			# only the playable non-random ones; _pick returns the first, so test each index directly
			var card := scene.engine.content(st.hand[i]) as CardData
			var opts := CardTargeting.options(scene.engine.resolver, st, i)
			if card == null or opts.is_empty() or CardTargeting.is_random(card) or scene.engine.validate(opts[0]) != "" or card.ram_cost > st.ram:
				continue
		scene._preview_card(i)
		await _frames(2)
		var shown: String = String(scene._enemy_views[st.enemies[0].id].intent.get("text", ""))
		# Make the play for real and read the pointer the way the tag does.
		var action: CombatAction = scene._card_action(i)
		for a in CardTargeting.options(scene.engine.resolver, st, i):
			if a.wheel_id == st.target_id and a.direction == 1:
				action = a
				break
		if scene.engine.validate(action) != "":
			action = CardTargeting.options(scene.engine.resolver, st, i)[0]
		var after: CombatResult = scene.engine.preview(action)
		assert_true(after != null and after.ok(), "preview ok")
		var real_state: CombatState = after.state
		var real: String = String(scene._landing_title(real_state, real_state.get_combatant(st.enemies[0].id))["text"])
		assert_eq(shown, real, "seed %d after %d played, card %s: the tag reads the pointer after the play" % [combat_seed, played, st.hand[i]])
		checked += 1
	scene.get_parent().queue_free()
	await _frames(2)
	return checked


func test_tag_equals_pointer_after_the_hovered_play_chain() -> void:
	var total := 0
	for combat_seed in [5, 7, 11]:
		for played in [0, 1, 2]:
			total += await _agree(combat_seed, played)
	assert_gt(total, 0, "some hovers were checked")


## After the first play, hover the second: the tag already says where the pointer WILL be, so while it differs from
## the pointer now, playing it for real makes the pointer read what the tag said.
func test_real_play_moves_the_pointer_to_the_tag() -> void:
	var checked := 0
	for combat_seed in [5, 7, 11, 13]:
		var scene: Control = await _combat(combat_seed)
		var first := _pick(scene)
		if first >= 0:
			scene.play_card(first)
			scene.skip_motion()
			await _frames(2)
		var j := _pick(scene)
		if j < 0:
			scene.get_parent().queue_free()
			continue
		scene._preview_card(j)
		await _frames(2)
		var st: CombatState = scene.engine.state()
		var shown: String = String(scene._enemy_views[st.enemies[0].id].intent.get("text", ""))
		var opts := CardTargeting.options(scene.engine.resolver, st, j)
		var action: CombatAction = opts[0]
		for a in opts:
			if a.wheel_id == st.target_id and a.direction == 1:
				action = a
				break
		if scene.engine.validate(action) != "":
			action = opts[0]
		scene.engine.submit(action)
		scene.skip_motion()
		await _frames(2)
		assert_eq(shown, _enemy_tag(scene), "seed %d: after the second play the pointer reads what the tag said" % combat_seed)
		checked += 1
		scene.get_parent().queue_free()
		await _frames(2)
	assert_gt(checked, 0, "some chains were checked")
