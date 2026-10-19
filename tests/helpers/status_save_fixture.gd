class_name StatusSaveFixture
extends RefCounted
## N8: the fight the v2 save fixtures (`tests/fixtures/saves/v2/`) were recorded from, on the
## v2 build (before ×N status stacks). A test that migrates a fixture rebuilds the same
## content here, so the loaded session resolves against what it was saved with. Only content
## builders: nothing here may read slot statuses (it ran on both sides of the format change).

const SEED := 8080
## The satellite's dock on the enemy and the drone's dock on the operative.
const DOCK_SLOT := 2
const DRONE_SLOT := 4
## The fixture files, by name (tests/fixtures/saves/v2/<name>.json).
const FIXTURE_DIR := "res://tests/fixtures/saves/v2/"
const FIXTURES: Array[String] = ["v2_empty", "v2_corrupted_overclocked", "v2_parasite_slice",
	"v2_midfight_checkpoint", "v2_botnet_drones", "v2_satellite_status"]


static func _atk() -> SliceData:
	return CombatFixture.slice(&"ssf_atk10", RC.SliceType.SHIM, 10)


static func _null() -> SliceData:
	return CombatFixture.slice(&"ssf_null", RC.SliceType.NULL, 0, RC.TargetRule.SELF)


## The operative's one card: OVERCLOCKED on its own slice under the pointer (1 RAM).
static func overdrive() -> CardData:
	return CombatFixture.card(&"ssf_overdrive", [CombatFixture.effect(RC.EffectType.APPLY_STATUS, RC.EffectTarget.OWN_WHEEL, 0, RC.RingScope.OUTER, 1.0, RC.Status.OVERCLOCKED)], 1, RC.WheelTarget.OWN)


static func satellite() -> EnemyData:
	var a := _atk()
	return CombatFixture.enemy(&"ssf_sat", 30, CombatFixture.wheel([a, a]))


## The Botnet-style drone template docked on the operative.
static func drone() -> EnemyData:
	var a := _atk()
	return CombatFixture.enemy(&"ssf_drone", 12, CombatFixture.wheel([a, a, a]))


static func enemy() -> EnemyData:
	var a := _atk()
	return CombatFixture.enemy(&"ssf_enemy", 300, CombatFixture.wheel([a, a, a, a, a, a]), [CombatFixture.spawn(satellite(), DOCK_SLOT)])


static func operative() -> ClassData:
	var a := _atk()
	var deck: Array[CardData] = [overdrive(), overdrive(), overdrive(), overdrive(), overdrive()]
	return CombatFixture.operative_class(&"ssf_class", 90, CombatFixture.wheel([a, a, a, a, a, _null()]), deck)


static func resolver() -> CombatResolver:
	var sat := satellite()
	var en := enemy()
	en.spawns[0].satellite = sat
	return CombatFixture.resolver([operative(), en, sat, drone(), overdrive()])


## A fresh session of the fixture fight, pointers parked: operative slot 1, enemy slot 0.
static func start() -> CombatSession:
	var s := CombatSession.start(resolver(), &"ssf_class", [&"ssf_enemy"], SEED)
	CombatFixture.land(s.state.player, 1)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 0)
	return s


## Docks one drone on the operative (DRONE_SLOT).
static func dock_drone(s: CombatSession) -> CombatantState:
	var events: Array[Dictionary] = []
	return s.resolver.fx.deploy_drone(s.state, s.state.player, drone(), DRONE_SLOT, events)


## The fixture's saved session (inside the run-shaped wrapper the fixtures use).
static func session_dict(file: Dictionary) -> Dictionary:
	return (file.get("run", {}) as Dictionary).get("combat", {})


## HP of every combatant of `state`, by id (what an End Turn is compared on).
static func hp_by_id(state: CombatState) -> Dictionary:
	var out := {}
	for c in [state.player] + state.drones + state.enemies:
		if c != null:
			out[String(c.id)] = c.hp
	return out
