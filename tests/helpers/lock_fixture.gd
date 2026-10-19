class_name LockFixture
extends RefCounted
## Plan 2 N7 test arena: an operative on a NULL wheel with four cards (a nudge card, a respin
## card, a LOCK_NUDGE card and a LOCK_RESPIN card, all 0 RAM) against one enemy whose slot 0
## carries a lock slice (kind per `opts`). Built fresh per call; nothing shared between tests.

const NUDGE_CARD := &"lk_nudge"
const RESPIN_CARD := &"lk_respin"
const LOCK_NUDGE_CARD := &"lk_lock_nudge"
const LOCK_RESPIN_CARD := &"lk_lock_respin"
const ENEMY := &"lk_enemy"
const SLICE_SOURCE := &"lk_lock_slice"


## `opts`: "enemy_lock" (RC.EffectType the enemy slice applies at RESOLVE, default LOCK_NUDGE;
## -1 for none), "seed" (default 4242), "phases" (Array of thresholds for a boss).
static func session(opts: Dictionary = {}) -> CombatSession:
	var null_slice := CombatFixture.slice(&"lk_null", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	var pw := CombatFixture.wheel([null_slice, null_slice, null_slice, null_slice, null_slice, null_slice])
	var nudge := CombatFixture.card(NUDGE_CARD, [CombatFixture.effect(RC.EffectType.NUDGE, RC.EffectTarget.OWN_WHEEL, 1)], 0, RC.WheelTarget.OWN)
	var respin := CombatFixture.card(RESPIN_CARD, [CombatFixture.effect(RC.EffectType.RESPIN, RC.EffectTarget.OWN_WHEEL, 0, RC.RingScope.WHOLE_WHEEL)], 0, RC.WheelTarget.OWN)
	var lock_n := CombatFixture.card(LOCK_NUDGE_CARD, [CombatFixture.effect(RC.EffectType.LOCK_NUDGE, RC.EffectTarget.TARGET_WHEEL, 1)], 0, RC.WheelTarget.ENEMY)
	var lock_r := CombatFixture.card(LOCK_RESPIN_CARD, [CombatFixture.effect(RC.EffectType.LOCK_RESPIN, RC.EffectTarget.TARGET_WHEEL, 1)], 0, RC.WheelTarget.ENEMY)
	var deck: Array[CardData] = [nudge, respin, lock_n, lock_r]
	var cls := CombatFixture.operative_class(&"lk_class", 200, pw, deck)
	var lock_type: int = int(opts.get("enemy_lock", RC.EffectType.LOCK_NUDGE))
	var extra: Array[TriggeredEffectData] = []
	if lock_type >= 0:
		var fx: Array[EffectData] = [CombatFixture.effect(lock_type, RC.EffectTarget.TARGET_WHEEL, 1)]
		extra.append(CombatFixture.triggered(RC.Trigger.ON_SLICE_TRIGGER, fx))
	var lock_slice := CombatFixture.slice(SLICE_SOURCE, RC.SliceType.SHIM, 0, RC.TargetRule.POINTER, extra)
	var ew := CombatFixture.wheel([lock_slice, null_slice, null_slice, null_slice, null_slice, null_slice])
	var enemy := CombatFixture.enemy(ENEMY, 300, ew)
	var content: Array = [cls, null_slice, lock_slice, nudge, respin, lock_n, lock_r, enemy]
	var s := CombatSession.start(CombatFixture.resolver(content), cls.id, [ENEMY], int(opts.get("seed", 4242)))
	stage(s)
	return s


## Hand = the four cards, RAM 6, both pointers on slot 0 (the enemy's lock slice fires at
## RESOLVE), and that is the checkpoint.
static func stage(s: CombatSession) -> void:
	s.state.hand = [NUDGE_CARD, RESPIN_CARD, LOCK_NUDGE_CARD, LOCK_RESPIN_CARD]
	s.state.ram = 6
	s.state.free_nudges = 1
	CombatFixture.land(s.state.player, 0)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 0)
	s._set_checkpoint()
