class_name EnrageFixture
extends RefCounted
## Plan 2 N4 builders: enemies whose six slices are all SHIM `hit`, of a chosen class, with
## an optional authored enrage, and sessions moved to a given turn. In memory only.


## An EnrageData with the given numbers.
static func enrage(start: int, every: int, pct: int, resist: int = 0) -> EnrageData:
	var e := EnrageData.new()
	e.start_turn = start
	e.every_n_turns = every
	e.damage_pct_step = pct
	e.resistance_step = resist
	return e


## An enemy of class `cls` (RC.EnemyClass), `hp` HP, every slice SHIM `hit`, one needle per
## entry of `pointers`, with `authored` as its enrage (null = class default).
static func enemy(id: StringName, cls: int, hit: int, hp: int = 999, authored: EnrageData = null, pointers: Array = [0]) -> EnemyData:
	var shim := CombatFixture.slice(StringName("%s_shim" % id), RC.SliceType.SHIM, hit)
	var w := CombatFixture.wheel([shim, shim, shim, shim, shim, shim], null, pointers)
	var e := PhaseFixture.enemy(id, hp, [], cls, w)
	e.enrage = authored
	return e


## A session against `data` whose operative deals `dmg` per needle (0 = harmless).
static func session(data: EnemyData, dmg: int = 0, seed: int = 4242, extra: Array = []) -> CombatSession:
	return PhaseFixture.session(data, dmg, [0], seed, extra)


## Moves `s` to the start of turn `turn` (runs start_turn from turn - 1; no player actions).
static func to_turn(s: CombatSession, turn: int) -> void:
	s.state.turn = turn - 1
	var events: Array[Dictionary] = []
	s.resolver.start_turn(s.state, s.rng, events)


## Aims both wheels at a slice centre (PERFECT, full output) and returns the enemy.
static func aim(s: CombatSession) -> CombatantState:
	return PhaseFixture.aim(s)


## The operative's HP lost by ending the turn now: [previewed, actual].
static func hp_lost_preview_and_actual(s: CombatSession) -> Array[int]:
	var hp := s.state.player.hp
	var pv := s.preview_end_turn()
	var previewed := hp - pv.resolved_state.player.hp
	var r := s.apply(CombatAction.end_turn())
	var actual := hp - r.resolved_state.player.hp
	return [previewed, actual]
