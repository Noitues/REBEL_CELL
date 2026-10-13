extends GutTest
## ART-2 acceptance (MILESTONES "The worst-case clutter fixture renders legibly at 1.0 and 1.6";
## DECISIONS 2026-10-11 "M14 ART-2/ART-5 acceptance"): each corporation's boss fight dressed as
## arena_lab's worst fixture (ClutterFixture: a drone or satellite on every slot of both wheels,
## Firmware in every slot, every lab Daemon, every dock bloomed, a card hovered; the review pack's
## `combat_clutter` screen). At text sizes 1.0 and 1.6 the wheels' words (HP number, NEXT / LAST
## TURN plates, tag), the bloomed drones, the result chips, the Daemon rack and the hand's text stay
## on screen and inside their own rects, and none sits on another. The hand's own fan (D15: each
## card under its right neighbour by HAND_OVERLAP) is the approved look, not checked here.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const ClutterFixture := preload("res://tools/visual_qa/clutter_fixture.gd")
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6]
## The corporations' bosses (arena_lab's BOSSES, in id order).
const BOSSES: Array[StringName] = [&"civic_core", &"the_manifest", &"commons_array", &"dispatch_core", &"renewal_engine"]
## Rects closer than this (px) count as touching, not overlapping (anti-aliased edges).
const EDGE := 0.5

var _settings: Dictionary = {}


func before_all() -> void:
	_settings = Settings.snapshot()


func after_all() -> void:
	Settings.restore(_settings)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_art2_clutter"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	Settings.restore(_settings)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 4) -> void:
	for i in n:
		await get_tree().process_frame


## `boss`'s fight at text scale `scale`, dressed as the worst fixture and settled.
func _clutter(scale: float, boss: StringName) -> Control:
	Settings.set_text_scale(scale)
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(boss, 7)
	await _frames()
	ClutterFixture.dress(scene)
	await _frames()
	return scene


func _close(scene: Control) -> void:
	if is_instance_valid(scene):
		scene.skip_motion()
		scene.get_parent().queue_free()
	await _frames(2)


## Every word block on screen: [owner, what, global rect]. Owner is the wheel's combatant id, or
## "hud" / "hand".
func _words(scene: Control) -> Array:
	var out: Array = []
	for v: WheelView in scene._views():
		if v.combatant == null:
			continue
		var who := String(v.combatant.id)
		for r: Rect2 in v._hp_block_rects():
			out.append([who, "HP block", Rect2(v.global_position + r.position, r.size)])
		if v.intent_rect().has_area():
			out.append([who, "tag", v.intent_rect()])
		var banner := v.banner_rect()
		if banner.has_area():
			out.append([who, "boss banner", Rect2(v.global_position + banner.position, banner.size)])
		for hint in v.arrow_hint_rects():
			out.append([who, "nudge key hint", hint])
		var row: HudResultChips = scene.hud_layer.row_for(v)
		if row != null and row.is_visible_in_tree():
			for r: Rect2 in row.standing_rects() + row.chip_rects():
				out.append([who, "result chip", Rect2(row.global_position + r.position, r.size)])
	for b in scene.hud_layer.buttons():
		var r := float(b["radius"])
		out.append([String((b["view"] as WheelView).combatant.id), "nudge button", _disc_box(b["center"], r)])
	var rack := scene._player_view.get_node_or_null("DaemonRack") as Control
	if rack != null and rack.is_visible_in_tree():
		out.append(["hud", "Daemon rack", rack.get_global_rect()])
	for c: Control in [scene._end_turn_button, scene._respin_button, scene._rewind_button, scene.ram_note, scene._banner]:
		if c != null and c.is_visible_in_tree():
			out.append(["hud", String(c.name), c.get_global_rect()])
	for c in scene._hand_box.get_children():
		if c is ZineCard:
			out.append(["hand", (c as ZineCard).card_title, (c as ZineCard).get_global_rect()])
	return out


## Every bloomed drone or satellite as it is drawn: [owner, id, global centre, radius].
func _drones(scene: Control) -> Array:
	var out: Array = []
	for v: WheelView in scene._views():
		if v.combatant == null:
			continue
		var dock: DroneDock = v.attachments.dock
		for e in dock.entries():
			var b := float(dock.bloom.get(int(e["slot"]), 0.0))
			var at: Vector2 = (e["tile"] as Vector2).lerp(e["mini"], b)
			var r := float(e["mini_r"]) * lerpf(DroneDock.BLOOM_FROM, 1.0, b)
			out.append([String(v.combatant.id), String((e["sat"] as CombatantState).id), dock.global_position + at, r])
	return out


static func _disc_box(at: Vector2, r: float) -> Rect2:
	return Rect2(at - Vector2(r, r), Vector2(r, r) * 2.0)


static func _disc_meets(rect: Rect2, at: Vector2, r: float) -> bool:
	var q := Vector2(clampf(at.x, rect.position.x, rect.end.x), clampf(at.y, rect.position.y, rect.end.y))
	return q.distance_to(at) < r - EDGE


func test_the_fixture_is_dressed_worst_case() -> void:
	var scene := await _clutter(1.0, &"renewal_engine")
	var st: CombatState = scene.engine.state()
	assert_eq(st.drones.size(), st.player.wheel.slice_count, "a drone on every player slot")
	assert_eq(st.enemies.size() - 1, st.enemies[0].wheel.slice_count, "a satellite on every boss slot")
	assert_eq(st.daemon_ids.size(), ClutterFixture.ARENA_LAB.DAEMONS.size(), "every lab Daemon")
	for v: WheelView in scene._views():
		if v.combatant != null:
			assert_true(v.attachments.dock.force_bloom, "%s: its docks bloomed" % v.combatant.id)
	await _close(scene)


func test_the_clutter_fixture_keeps_every_word_on_screen_and_apart_at_1_0_and_1_6() -> void:
	for boss in BOSSES:
		for scale in TestScope.scales(SCALES):
			var scene := await _clutter(scale, boss)
			var bad: Array[String] = []
			for v in scene.layout_violations():
				bad.append("layout rule: %s" % v)
			var words := _words(scene)
			var drones := _drones(scene)
			for w in words:
				if not SCREEN.grow(EDGE).encloses(w[2]):
					bad.append("%s's %s %s leaves the screen" % [w[0], w[1], w[2]])
			# Words of different owners never overlap (a wheel's own HP block and chips sit together
			# by design; the hand's fan is D15's).
			for i in words.size():
				for j in range(i + 1, words.size()):
					var a: Array = words[i]
					var b: Array = words[j]
					if a[0] == b[0]:
						continue
					if (a[2] as Rect2).grow(-EDGE).intersects((b[2] as Rect2).grow(-EDGE)):
						bad.append("%s's %s %s overlaps %s's %s %s" % [a[0], a[1], a[2], b[0], b[1], b[2]])
			# A bloomed drone stays on screen, off every word block and off every other drone.
			for i in drones.size():
				var d: Array = drones[i]
				if not SCREEN.grow(EDGE).encloses(_disc_box(d[2], d[3])):
					bad.append("drone %s leaves the screen" % d[1])
				for w in words:
					if _disc_meets(w[2], d[2], d[3]):
						bad.append("drone %s (%s) at %s r %.0f sits on %s's %s %s" % [d[1], d[0], d[2], d[3], w[0], w[1], w[2]])
				for j in range(i + 1, drones.size()):
					var o: Array = drones[j]
					if (d[2] as Vector2).distance_to(o[2]) < float(d[3]) + float(o[3]) - EDGE:
						bad.append("drones %s and %s overlap" % [d[1], o[1]])
			# The hand's text: every body line inside its card, never under the rest floor.
			for c in scene._hand_box.get_children():
				var card := c as ZineCard
				if card == null:
					continue
				var parts := card.sticker_parts()
				for r: Rect2 in parts["body"]:
					if not Rect2(Vector2.ZERO, card.size).grow(EDGE).encloses(r):
						bad.append("%s: body line %s outside its card %s" % [card.card_title, r, card.size])
				if int(parts["fs"]) < ZineCard.HAND_REST_FLOOR:
					bad.append("%s: body at %d px, under the rest floor" % [card.card_title, int(parts["fs"])])
			assert_eq(bad, [] as Array[String], "x%.1f %s:\n%s" % [scale, boss, "\n".join(bad)])
			await _close(scene)
