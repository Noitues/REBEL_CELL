class_name SatelliteFixture
extends RefCounted
## N13 (fixed satellites): a host enemy with one 2-slice satellite docked on slot 2 at
## combat start, against an operative whose deck is exactly the cards given.

const SEED := 1313
const DOCK_SLOT := 2


static func host_wheel() -> WheelData:
	var slices: Array = []
	for i in RC.SLICES:
		slices.append(CombatFixture.slice(StringName("sf_h%d" % i), RC.SliceType.NULL, 0, RC.TargetRule.SELF))
	return CombatFixture.wheel(slices)


static func satellite(id: StringName = &"sf_sat", hp: int = 5) -> EnemyData:
	var m := CombatFixture.slice(&"sf_sat_null", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	return CombatFixture.enemy(id, hp, CombatFixture.wheel([m, m]))


## A fixture card (0 RAM, any wheel) with one effect of `type` on the target wheel.
static func move_card(id: StringName, type: int, amount: int = 1, undock: bool = false) -> CardData:
	var scope := RC.RingScope.WHOLE_WHEEL if type in [RC.EffectType.SPIN, RC.EffectType.FLIP, RC.EffectType.RESPIN] else RC.RingScope.OUTER
	var e := CombatFixture.effect(type, RC.EffectTarget.TARGET_WHEEL, amount, scope)
	e.undock = undock
	return CombatFixture.card(id, [e])


## Starts the combat. `spawns` replaces the default dock (one satellite on DOCK_SLOT);
## `p_hub` goes on the operative's wheel (its passives hear ON_SATELLITE_DESTROYED).
static func session(cards: Array[CardData], spawns: Array[SatelliteSpawnData] = [], p_hub: HubCoreData = null, extra: Array = []) -> CombatSession:
	var sat := satellite()
	if spawns.is_empty():
		spawns = [CombatFixture.spawn(sat, DOCK_SLOT)]
	var host := CombatFixture.enemy(&"sf_host", 200, host_wheel(), spawns)
	var m := CombatFixture.slice(&"sf_p_null", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	var cls := CombatFixture.operative_class(&"sf_class", 60, CombatFixture.wheel([m, m, m, m, m, m], p_hub), cards)
	var custom: Array = [cls, sat, host]
	for sp in spawns:
		custom.append(sp.satellite)
	custom.append_array(cards)
	custom.append_array(extra)
	return CombatSession.start(CombatFixture.resolver(custom), cls.id, [host.id], SEED)


static func sat_of(s: CombatSession) -> CombatantState:
	var sats := s.state.satellites_of(&"enemy_0")
	return sats[0] if not sats.is_empty() else null


static func play(s: CombatSession, id: StringName, wheel: StringName, direction: int = 1) -> CombatResult:
	var a := CombatAction.play_card(s.state.hand.find(id), wheel)
	a.direction = direction
	return s.apply(a)
