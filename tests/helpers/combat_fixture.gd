class_name CombatFixture
extends RefCounted
## Builders for combat tests: in-memory content, resolvers over real + custom content,
## and helpers to park a pointer on a chosen slice. Never modifies loaded content.

const CONFIG_PATH := "res://content/config/campaign_config.tres"


static func config() -> CampaignConfigData:
	return load(CONFIG_PATH)


static func slice(id: StringName, type: int, output: int, rule: int = RC.TargetRule.POINTER, extra: Array[TriggeredEffectData] = []) -> SliceData:
	var s := SliceData.new()
	s.id = id
	s.display_name = String(id)
	s.slice_type = type
	s.target_rule = rule
	s.base_output = output
	s.extra_effects = extra
	return s


static func effect(type: int, target: int, amount: int = 0, scope: int = RC.RingScope.OUTER, mult: float = 1.0, status: int = RC.Status.NONE, pick: int = RC.SlicePick.UNDER_POINTER) -> EffectData:
	var e := EffectData.new()
	e.type = type
	e.target = target
	e.amount = amount
	e.ring_scope = scope
	e.multiplier = mult
	e.status = status
	e.slice_pick = pick
	return e


static func triggered(trigger: int, effects: Array[EffectData], min_tier: int = RC.PrecisionTier.PARTIAL, consecutive: int = 1, limit: int = 0) -> TriggeredEffectData:
	var t := TriggeredEffectData.new()
	t.trigger = trigger
	t.effects = effects
	t.min_tier = min_tier
	t.consecutive_required = consecutive
	t.limit_per_combat = limit
	return t


static func hub(id: StringName, resistance: int = 0, passives: Array[TriggeredEffectData] = [], hook: TriggeredEffectData = null) -> HubCoreData:
	var h := HubCoreData.new()
	h.id = id
	h.display_name = String(id)
	h.hub_resistance = resistance
	h.passive_effects = passives
	h.perfect_hook = hook
	return h


static func segment(id: StringName, mult: float = 1.0, pierce: bool = false, effects: Array[TriggeredEffectData] = []) -> RingSegmentData:
	var s := RingSegmentData.new()
	s.id = id
	s.display_name = String(id)
	s.output_multiplier = mult
	s.pierce = pierce
	s.triggered_effects = effects
	return s


static func ring(segments: Array[RingSegmentData]) -> InnerRingData:
	var r := InnerRingData.new()
	r.segments = segments
	return r


static func wheel(slices: Array, p_hub: HubCoreData = null, pointers: Array = [0], passive_resistance: int = 0, p_ring: InnerRingData = null, firmware: Array = []) -> WheelData:
	var w := WheelData.new()
	w.slice_count = slices.size()
	var slots: Array[WheelSlotData] = []
	for i in slices.size():
		var slot := WheelSlotData.new()
		slot.slice = slices[i]
		if i < firmware.size() and firmware[i] != null:
			slot.firmware = firmware[i]
		slots.append(slot)
	w.slots = slots
	w.hub = p_hub
	w.inner_ring = p_ring
	w.pointer_ticks = PackedInt32Array(pointers)
	w.passive_resistance = passive_resistance
	return w


static func enemy(id: StringName, hp: int, p_wheel: WheelData, spawns: Array[SatelliteSpawnData] = []) -> EnemyData:
	var e := EnemyData.new()
	e.id = id
	e.display_name = String(id)
	e.hp = hp
	e.wheel = p_wheel
	e.spawns = spawns
	return e


static func spawn(satellite: EnemyData, dock_slot: int, max_active: int = 1) -> SatelliteSpawnData:
	var sp := SatelliteSpawnData.new()
	sp.satellite = satellite
	sp.trigger = RC.Trigger.ON_COMBAT_START
	sp.dock_slot = dock_slot
	sp.max_active = max_active
	return sp


static func card(id: StringName, effects: Array[EffectData], ram: int = 0, wheel_target: int = RC.WheelTarget.ANY, exhaust: bool = false) -> CardData:
	var c := CardData.new()
	c.id = id
	c.display_name = String(id)
	c.effects = effects
	c.ram_cost = ram
	c.wheel_target = wheel_target
	c.exhaust = exhaust
	return c


static func operative_class(id: StringName, hp: int, p_wheel: WheelData, deck: Array[CardData]) -> ClassData:
	var c := ClassData.new()
	c.id = id
	c.display_name = String(id)
	c.base_hp = hp
	c.starting_wheel = p_wheel
	c.starting_deck = deck
	c.starting_ram = 6
	c.max_ram = 12
	c.ram_regen = 4
	c.free_nudges_per_turn = 1
	return c


## A 6-slice wheel that never does anything (all Miss), for passive punching bags.
static func miss_wheel(passive_resistance: int = 0, p_hub: HubCoreData = null, pointers: Array = [0]) -> WheelData:
	var m := slice(&"fx_miss", RC.SliceType.MISS, 0, RC.TargetRule.SELF)
	return wheel([m, m, m, m, m, m], p_hub, pointers, passive_resistance)


## Resolver over the real content registry plus any custom resources.
static func resolver(custom: Array = []) -> CombatResolver:
	var lookup := ContentLookup.new().add_registry(ContentRegistry)
	for res in custom:
		lookup.add(res)
	return CombatResolver.new(config(), lookup)


static func rng(seed: int) -> RandomNumberGenerator:
	var r := RandomNumberGenerator.new()
	r.seed = seed
	return r


## Parks pointer `pointer_index` of `c` on slice `slot` at `offset` ticks from its centre.
static func land(c: CombatantState, slot: int, offset: int = 0, pointer_index: int = 0) -> void:
	c.wheel.flipped = false
	c.wheel.rotation = WheelMath.slice_center(slot, c.wheel.slice_count) + offset - c.wheel.pointer_ticks[pointer_index]


## Parks the inner ring so `segment_index` sits under pointer `pointer_index`.
static func land_inner(c: CombatantState, segment_index: int, pointer_index: int = 0) -> void:
	c.wheel.inner_rotation = segment_index * RC.TICKS_PER_RING_SEGMENT - c.wheel.pointer_ticks[pointer_index]


static func events_of(result: CombatResult, type: String) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for e in result.events:
		if e.get("type", "") == type:
			out.append(e)
	return out


static func index_of_event(result: CombatResult, type: String, key: String = "", value: Variant = null) -> int:
	for i in result.events.size():
		var e := result.events[i]
		if e.get("type", "") == type and (key == "" or e.get(key) == value):
			return i
	return -1
