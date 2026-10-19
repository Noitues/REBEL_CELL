class_name RiderFixture
extends RefCounted
## Plan 2 N20 test helper: rider slices and small fights around them. An enemy whose six
## slices are one rider slice attacks an operative whose six slices are a harmless,
## non-NULL pad (BLOCK 0), so CORRUPTED counts on the operative's wheel are easy to set.

const SEED := 7


## A SHIM (or `type`) slice of `base` with the N20 riders set.
static func rider(id: StringName, base: int, hits: int = 1, mult: float = 1.0, pierce: bool = false, status: int = RC.Status.NONE, per_slice: int = 0, type: int = RC.SliceType.SHIM, extra: Array[TriggeredEffectData] = []) -> SliceData:
	var s := CombatFixture.slice(id, type, base, RC.TargetRule.POINTER, extra)
	s.hits = hits
	s.perfect_multiplier = mult
	s.pierce = pierce
	s.hits_per_target_status = status as RC.Status
	s.hits_per_status_slice = per_slice
	return s


## The operative's harmless pad slice (BLOCK 0, never NULL).
static func pad(id: StringName) -> SliceData:
	return CombatFixture.slice(id, RC.SliceType.DEFRAG, 0, RC.TargetRule.SELF)


static func _deck(id: StringName) -> Array[CardData]:
	return [CombatFixture.card(StringName("%s_noop" % id), [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]


## A fight: the enemy's six slices are `foe_slice` (needles `foe_pointers`); the
## operative's six are `player_slices` (default: the pad) with needles `player_pointers`.
## Both wheels land on slot 0 at PERFECT; move them with CombatFixture.land.
static func session(tag: StringName, foe_slice: SliceData, player_pointers: Array = [0], foe_pointers: Array = [0], player_slices: Array = [], seed: int = SEED) -> CombatSession:
	var slices := player_slices
	if slices.is_empty():
		var p := pad(StringName("%s_pad" % tag))
		slices = [p, p, p, p, p, p]
	var cls := CombatFixture.operative_class(StringName("%s_op" % tag), 999, CombatFixture.wheel(slices, null, player_pointers), _deck(tag))
	var foe := CombatFixture.enemy(StringName("%s_foe" % tag), 999, CombatFixture.wheel([foe_slice, foe_slice, foe_slice, foe_slice, foe_slice, foe_slice], null, foe_pointers))
	var s := CombatSession.start(CombatFixture.resolver([cls, foe]), cls.id, [foe.id], seed)
	for i in s.state.player.wheel.pointer_ticks.size():
		CombatFixture.land(s.state.player, 0, 0, i)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 0)
	return s


## Ends the turn of `s`: {"preview_lost", "lost" (operative HP), "result", "preview"}.
static func end(s: CombatSession) -> Dictionary:
	var hp := s.state.player.hp
	var pv := s.preview_end_turn()
	var r := s.apply(CombatAction.end_turn())
	return {"preview_lost": hp - pv.resolved_state.player.hp, "lost": hp - r.resolved_state.player.hp, "result": r, "preview": pv}


## The hit outcomes of `events` in order ("damage" and SANDBOX "evaded"), optionally only
## those landing on `target`.
static func hits_of(events: Array[Dictionary], target: StringName = &"") -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for e in events:
		if String(e.get("type", "")) in ["damage", "evaded"] and (target == &"" or StringName(String(e.get("target", ""))) == target):
			out.append(e)
	return out


## The "damage" amounts of `events` landing on `target`, in order.
static func amounts(events: Array[Dictionary], target: StringName) -> Array[int]:
	var out: Array[int] = []
	for e in hits_of(events, target):
		if String(e["type"]) == "damage":
			out.append(int(e["amount"]))
	return out


## Puts `stacks` CORRUPTED stacks on each of the operative's `slots`.
static func corrupt(s: CombatSession, slots: Array, stacks: int = 1) -> void:
	for slot: int in slots:
		s.state.player.wheel.add_stacks(slot, RC.Status.CORRUPTED, stacks, WheelState.NO_STACK_LIMIT)
