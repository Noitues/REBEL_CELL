extends RefCounted
## ART-2 acceptance "the worst-case clutter fixture renders legibly at 1.0 and 1.6": arena_lab's
## worst fixture (`tools/design_lab/arena_lab.gd --fixture=worst --hover=spin --bloom`, next to
## `docs/art_reference/hud/round41_wheel_stack/combat_worst_case_v4`) as one shared dressing for
## the review pack's `combat_clutter` screen, the perf pack's `combat_worst` screens and
## `test_art2_clutter_fixture`. Dev tool, never game code: it dresses a running fight's state
## directly (drones on every player slot, a satellite on every enemy slot, Firmware in every
## slot of both wheels, every lab Daemon, the docks bloomed, a card hovered).

const ARENA_LAB := preload("res://tools/design_lab/arena_lab.gd")


## Dresses `combat` (a combat scene with its fight started; its first enemy is the host of the
## satellites) as the worst fixture and refreshes it. Returns the dressed state.
static func dress(combat: Control) -> CombatState:
	var engine = combat.engine
	var st: CombatState = engine.state()
	var lookup: ContentLookup = engine.resolver.lookup
	var foe := st.enemies[0]
	for i in st.player.wheel.slice_count:
		if st.satellite_at(st.player.id, i) == null:
			dock(st, st.player, lookup.get_content(ARENA_LAB.DRONE) as EnemyData, i)
	for i in foe.wheel.slice_count:
		if st.satellite_at(foe.id, i) == null:
			dock(st, foe, lookup.get_content(ARENA_LAB.SAT_TEMPLATES[i % ARENA_LAB.SAT_TEMPLATES.size()]) as EnemyData, i)
	for i in st.player.wheel.slice_count:
		st.player.wheel.slot_firmware_ids[i] = ARENA_LAB.FIRMWARE[i % ARENA_LAB.FIRMWARE.size()]
	for i in foe.wheel.slice_count:
		foe.wheel.slot_firmware_ids[i] = ARENA_LAB.FIRMWARE[(i + 2) % ARENA_LAB.FIRMWARE.size()]
	st.daemon_ids.clear()
	for d in ARENA_LAB.DAEMONS:
		st.daemon_ids.append(d)
	st.hand[0] = ARENA_LAB.SPIN_CARD
	combat._refresh(st)
	for v in combat._views():
		v.attachments.dock.force_bloom = true
	combat._preview_card(0)
	return st


## arena_lab's `_dock`: a satellite of `data` docked on `owner`'s slot `slot`.
static func dock(st: CombatState, owner: CombatantState, data: EnemyData, slot: int) -> void:
	if data == null:
		return
	var d := EffectInterpreter.make_combatant(data, StringName("%s_lab_%d" % [owner.id, slot]), true)
	d.is_player = owner.is_player
	d.host_id = owner.id
	d.dock_slot = slot
	d.hp = maxi(1, d.max_hp - slot % 3)
	if d.wheel != null:
		d.wheel.rotation = (slot * 7) % RC.TICKS
	if owner.is_player:
		st.drones.append(d)
	else:
		st.enemies.append(d)
