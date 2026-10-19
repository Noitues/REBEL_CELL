class_name ListenerFixture
extends RefCounted
## Plan 2 N6 test arena: an operative whose wheel has one SHIM (slot 0, `shim` damage) and
## NULLs elsewhere, a deck of fixture cards, and one or two enemies on NULL wheels carrying
## enemy listeners (own and Hub). Built fresh per call; nothing shared between tests.

const ENEMY_HP := 300
const PLAYER_HP := 200
## Card ids in every arena deck: lf_zap (2 RAM, 1 damage), lf_free (0 RAM, 1 block),
## lf_pricey (99 RAM).
const ZAP := &"lf_zap"
const FREE := &"lf_free"
const PRICEY := &"lf_pricey"


static func listener(trigger: int, effects: Array[EffectData], per_turn: int = ListenerData.UNAUTHORED,
		per_combat: int = ListenerData.UNAUTHORED, min_tier: int = RC.PrecisionTier.WEAK) -> ListenerData:
	var l := ListenerData.new()
	l.trigger = trigger
	l.effects = effects
	l.max_per_turn = per_turn
	l.max_per_combat = per_combat
	l.min_tier = min_tier
	return l


## The listening enemy gains `n` BLOCK.
static func block(n: int) -> EffectData:
	return CombatFixture.effect(RC.EffectType.GAIN_BLOCK, RC.EffectTarget.SELF, n)


## The listening enemy hits the operative for `n` (FLAT; PERCENT when `percent`).
static func hit(n: int, percent: bool = false) -> EffectData:
	var e := CombatFixture.effect(RC.EffectType.DEAL_DAMAGE, RC.EffectTarget.TARGET_WHEEL, n)
	if percent:
		e.amount_mode = RC.AmountMode.PERCENT
	return e


## A session. `opts`: "hub" (Array[ListenerData] on the enemy Hub), "second" (Array[ListenerData]
## for a second enemy, enemy_1), "factor" (enemy tier damage factor), "seed", "shim" (the
## operative's SHIM output), "shims" (slots holding that SHIM, default [0]), "pointers"
## (operative pointer ticks), "deck" (Array of card ids,
## default 5 x lf_zap), "prefix" (content id prefix, default "lf").
static func session(listeners: Array[ListenerData], opts: Dictionary = {}) -> CombatSession:
	var prefix := String(opts.get("prefix", "lf"))
	var null_slice := CombatFixture.slice(StringName(prefix + "_null"), RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	var shim := CombatFixture.slice(StringName(prefix + "_shim"), RC.SliceType.SHIM, int(opts.get("shim", 7)))
	var slices := [null_slice, null_slice, null_slice, null_slice, null_slice, null_slice]
	for slot in opts.get("shims", [0]):
		slices[int(slot)] = shim
	var pw := CombatFixture.wheel(slices, null, opts.get("pointers", [0]))
	var zap := CombatFixture.card(ZAP, [CombatFixture.effect(RC.EffectType.DEAL_DAMAGE, RC.EffectTarget.TARGET_WHEEL, 1)], 2)
	var free := CombatFixture.card(FREE, [CombatFixture.effect(RC.EffectType.GAIN_BLOCK, RC.EffectTarget.SELF, 1)], 0)
	var pricey := CombatFixture.card(PRICEY, [CombatFixture.effect(RC.EffectType.GAIN_BLOCK, RC.EffectTarget.SELF, 1)], 99)
	var deck: Array[CardData] = []
	var lookup_cards := {ZAP: zap, FREE: free, PRICEY: pricey}
	for id in opts.get("deck", [ZAP, ZAP, ZAP, ZAP, ZAP]):
		deck.append(lookup_cards[StringName(id)])
	var cls := CombatFixture.operative_class(StringName(prefix + "_class"), PLAYER_HP, pw, deck)
	var custom: Array = [cls, null_slice, shim, zap, free, pricey]
	var hub: HubCoreData = null
	var hub_listeners: Array[ListenerData] = []
	hub_listeners.assign(opts.get("hub", []))
	if not hub_listeners.is_empty():
		hub = CombatFixture.hub(StringName(prefix + "_hub"))
		hub.listeners = hub_listeners
		custom.append(hub)
	var enemy := CombatFixture.enemy(StringName(prefix + "_enemy"), ENEMY_HP, CombatFixture.null_wheel(0, hub))
	enemy.listeners = listeners
	custom.append(enemy)
	var ids: Array[StringName] = [enemy.id]
	if opts.has("second"):
		var other := CombatFixture.enemy(StringName(prefix + "_enemy_b"), ENEMY_HP, CombatFixture.null_wheel())
		var second: Array[ListenerData] = []
		second.assign(opts["second"])
		other.listeners = second
		custom.append(other)
		ids.append(other.id)
	var resolver := CombatFixture.resolver(custom)
	var factor := float(opts.get("factor", 1.0))
	var o := {"enemy_scale": 1.0, "enemy_output_scale": factor}
	return CombatSession.start(resolver, cls.id, ids, int(opts.get("seed", 1000)), &"", 0, o)


## Puts `cards` in the hand, sets RAM and makes that the checkpoint (so rewinds land here).
static func stage(s: CombatSession, cards: Array = [], ram: int = -1) -> void:
	var hand: Array[StringName] = []
	for c in cards:
		hand.append(StringName(c))
	s.state.hand = hand
	if ram >= 0:
		s.state.ram = ram
	s._set_checkpoint()


## Parks the operative's pointer `pointer_index` on slot 0 at `offset` and the enemies on
## NULL, then makes that the checkpoint.
static func aim(s: CombatSession, offset: int = 0, pointer_index: int = 0) -> void:
	CombatFixture.land(s.state.player, 0, offset, pointer_index)
	s._set_checkpoint()


## The "listener" events of `r`, optionally only from `owner`.
static func fires(r: CombatResult, owner: StringName = &"") -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for e in CombatFixture.events_of(r, "listener"):
		if owner == &"" or e["owner"] == owner:
			out.append(e)
	return out


## The enemy's combat fire count of listener `index` (own listeners) in `s`.
static func combat_fires(state: CombatState, index: int = 0, enemy_id: StringName = &"enemy_0", prefix: String = "lf_enemy") -> int:
	var c := state.get_combatant(enemy_id)
	return int(c.listener_fires_combat.get(CombatResolver.listener_key(StringName(prefix), index), 0))
