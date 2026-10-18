class_name PhaseFixture
extends RefCounted
## Plan 2 N3 builders: enemies with phases (class, HP, thresholds) and an operative whose
## needles land SHIM hits of a fixed size, all in memory (no .tres dependency).


static func phase(threshold: float, cleanse: int = RC.CleanseScope.NONE, override: WheelData = null) -> BossPhaseData:
	var p := BossPhaseData.new()
	p.hp_threshold_pct = threshold
	p.cleanse_on_enter = cleanse
	p.wheel_override = override
	return p


## An enemy of class `cls` (RC.EnemyClass) with one phase entry per threshold.
static func enemy(id: StringName, hp: int, thresholds: Array, cls: int = RC.EnemyClass.BOSS, p_wheel: WheelData = null) -> EnemyData:
	var e := CombatFixture.enemy(id, hp, p_wheel if p_wheel != null else CombatFixture.null_wheel())
	e.is_boss = cls == RC.EnemyClass.BOSS
	e.is_mini_boss = cls == RC.EnemyClass.MINI_BOSS
	e.is_elite = cls == RC.EnemyClass.ELITE
	var ps: Array[BossPhaseData] = []
	for t in thresholds:
		ps.append(phase(float(t)))
	e.phases = ps
	return e


## An operative whose six slices are all SHIM `dmg`, one needle per entry of `pointers`.
static func operative(id: StringName, dmg: int, pointers: Array = [0]) -> ClassData:
	var shim := CombatFixture.slice(StringName("%s_shim" % id), RC.SliceType.SHIM, dmg)
	var noop: Array[CardData] = [CombatFixture.card(StringName("%s_noop" % id), [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	return CombatFixture.operative_class(id, 60, CombatFixture.wheel([shim, shim, shim, shim, shim, shim], null, pointers), noop)


## A session: the operative hits `dmg` per needle at `data`.
static func session(data: EnemyData, dmg: int, pointers: Array = [0], seed: int = 1001, extra: Array = []) -> CombatSession:
	var cls := operative(StringName("%s_op" % data.id), dmg, pointers)
	var content: Array = [cls, data]
	content.append_array(extra)
	return CombatSession.start(CombatFixture.resolver(content), cls.id, [data.id], seed)


## Puts every operative needle on a slice centre (PERFECT, full output) and the enemy on
## slot 0, then returns the enemy.
static func aim(s: CombatSession) -> CombatantState:
	CombatFixture.land(s.state.player, 0)
	var e := s.state.get_combatant(&"enemy_0")
	CombatFixture.land(e, 0)
	return e


## A bare combatant with `hp` of `max_hp` and the next threshold `threshold` (0 = none).
static func combatant(hp: int, max_hp: int, threshold: float) -> CombatantState:
	var c := CombatantState.new()
	c.id = &"pf_target"
	c.display_name = "pf_target"
	c.max_hp = max_hp
	c.hp = hp
	c.wheel = WheelState.from_wheel_data(CombatFixture.null_wheel())
	c.next_threshold_bp = roundi(threshold * RC.THRESHOLD_SCALE)
	return c


static func sum_of(events: Array[Dictionary], type: String, key: String) -> int:
	var n := 0
	for e in events:
		if String(e.get("type", "")) == type:
			n += int(e.get(key, 0))
	return n
