extends GutTest
## ART-12 12p (perf): the combat screen's per-frame redraws found by the windowed profile
## (tools/visual_qa/perf_pack.gd, docs/art_review/ART-12/perf.md). The telemetry ring turns
## without redrawing; the card-play preview's chevron chase redraws the preview alone, never
## the firmware sockets or the drone dock; the preview's ghost drones are the dock's layout at
## the ghost's rotation, re-laid whenever the ghost or the dock changes. The campaign end's
## paper art (the dossier's manila and print stock, the post-its) is loaded once and held.

const SCENE := "res://scenes/combat/combat_scene.tscn"

var _draws: Dictionary = {}


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_test_art12_perf"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	_draws.clear()


func after_each() -> void:
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 4) -> void:
	for i in n:
		await get_tree().process_frame


func _count(key: String) -> void:
	_draws[key] = int(_draws.get(key, 0)) + 1


func _watch(ci: CanvasItem, key: String) -> void:
	ci.draw.connect(_count.bind(key))


func _combat(enemy: StringName = &"the_manifest") -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(SCENE).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(enemy, 5)
	await _frames()
	return scene


func test_the_telemetry_ring_turns_without_redrawing() -> void:
	var ring := WheelTelemetry.new()
	add_child_autofree(ring)
	ring.setup(Vector2(200, 200), 0.5, "HP 10/10 // ", Palette.CELL_PINK)
	await _frames(2)
	_watch(ring, "ring")
	for i in 5:
		ring.rotation += 0.1
		await get_tree().process_frame
	assert_eq(int(_draws.get("ring", 0)), 0, "turning the ring (its scroll) never redraws its text")
	ring.setup(Vector2(200, 200), 0.5, "HP 9/10 // ", Palette.CELL_PINK)
	await _frames(2)
	assert_gt(int(_draws.get("ring", 0)), 0, "new words redraw it")


func test_the_preview_chase_redraws_the_preview_alone() -> void:
	var scene := await _combat()
	var v: WheelView = scene._player_view
	var at: WheelAttachments = v.attachments
	at._process(0.0)
	await _frames(2)
	_watch(at.sockets, "sockets")
	_watch(at.dock, "dock")
	_watch(at.preview, "preview")
	# Only the preview's own state moves (the chase headless holds at 1.0, so set it by hand).
	at.preview.chase = 0.25
	at._process(0.0)
	await get_tree().process_frame
	assert_gt(int(_draws.get("preview", 0)), 0, "the chase redraws the preview")
	assert_eq(int(_draws.get("dock", 0)), 0, "the dock does not redraw for the chase")
	assert_eq(int(_draws.get("sockets", 0)), 0, "the sockets do not redraw for the chase")
	# What the dock draws from changes: every layer redraws.
	v.set_ghost(posmod(v.combatant.wheel.rotation + 4, RC.TICKS))
	at._process(0.0)
	await get_tree().process_frame
	assert_gt(int(_draws.get("dock", 0)), 0, "a change the dock reads redraws it")
	assert_gt(int(_draws.get("sockets", 0)), 0, "and the sockets")


func test_the_ghost_drones_follow_the_ghost_and_the_dock() -> void:
	var scene := await _combat()
	var st: CombatState = scene.engine.state()
	var boss := st.enemies[0]
	var lookup: ContentLookup = scene.engine.resolver.lookup
	for slot in [0, 2]:
		var d := EffectInterpreter.make_combatant(lookup.get_content(&"care_drone") as EnemyData, StringName("gut_sat_%d" % slot), true)
		d.host_id = boss.id
		d.dock_slot = slot
		st.enemies.append(d)
	scene._refresh(st)
	var v: WheelView = null
	for w in scene._views():
		if w.combatant == boss:
			v = w
	assert_not_null(v, "the boss wheel")
	var at: WheelAttachments = v.attachments
	for step in [3, 7]:
		v.set_ghost(posmod(boss.wheel.rotation + step, RC.TICKS))
		at.preview._process(0.0)
		at._process(0.0)
		var cached := at.preview._ghost_entries()
		var fresh := at.dock.entries(float(int(at.preview.ghost["rot"])))
		assert_eq(cached.size(), fresh.size(), "a ghost drone per docked drone (ghost +%d)" % step)
		for i in fresh.size():
			assert_eq(cached[i]["tile"], fresh[i]["tile"], "drone %d ends where the dock lays it (ghost +%d)" % [i, step])
			assert_eq(cached[i]["mini"], fresh[i]["mini"], "its mini-wheel too (ghost +%d)" % step)


# --- Campaign end: paper art loaded once (an unheld load() decodes the file at every draw) ---

func test_the_dossier_holds_its_manila_and_print_stock_across_redraws() -> void:
	var c := RunManager.campaign
	c.outcome = CampaignState.Outcome.LOST
	var facts := DossierFacts.build(c, RunManager.corporation, RunManager.profile, RunManager.config(), func(id: StringName) -> String: return String(id),
		func(id: StringName) -> String: return String(id), [] as Array[Dictionary], 3)
	var d: AuditDossier = add_child_autofree(AuditDossier.new(facts))
	d.size = Vector2(1280, 720)
	await _frames(3)
	assert_not_null(d._manila_tex, "the folder drew its manila")
	var manila := d._manila_tex
	d.folder.queue_redraw()
	d.cover.queue_redraw()
	await _frames(2)
	assert_true(is_same(manila, d._manila_tex), "a redraw draws the held manila (no new load)")


func test_a_post_it_holds_its_paper_and_reloads_only_for_another_stock() -> void:
	var note: PostIt = add_child_autofree(PostIt.new("flag ICE 4.", Palette.END_NOTE_YELLOW))
	await _frames(2)
	assert_not_null(note._art, "the yellow stock is the concept's paper")
	var yellow := note._art
	note.queue_redraw()
	await _frames(2)
	assert_true(is_same(yellow, note._art), "a redraw draws the held paper")
	note.paper = Palette.END_NOTE_PINK
	note.queue_redraw()
	await _frames(2)
	assert_false(is_same(yellow, note._art), "another stock, its own paper")
	assert_not_null(note._art, "the pink stock is the concept's paper too")
