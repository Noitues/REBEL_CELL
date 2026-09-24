class_name CombatEngine
extends Node
## Node wrapper around CombatSession (TECH_SPEC 5.6). Holds the live session, calls
## the pure core, and emits what changed. Views never touch the session directly.

signal fight_started(state: CombatState)
signal state_changed(state: CombatState, events: Array[Dictionary])
signal action_refused(reason: String)
signal fight_ended(outcome: int)

var resolver: CombatResolver = null
var session: CombatSession = null
## When set, actions go through the netrun (which settles rewards when a fight ends).
var netrun: NetrunSession = null


func _ready() -> void:
	if resolver == null:
		resolver = make_resolver()


## Drives the netrun's live combat instead of a standalone fight.
func adopt_netrun(p_netrun: NetrunSession) -> void:
	netrun = p_netrun
	resolver = p_netrun.resolver
	session = p_netrun.combat
	if session != null:
		fight_started.emit(session.state)
		state_changed.emit(session.state, session.last_events)


## Resolver over the whole ContentRegistry and the global config.
static func make_resolver() -> CombatResolver:
	var lookup := ContentLookup.new().add_registry(ContentRegistry)
	return CombatResolver.new(ContentRegistry.config, lookup)


func has_fight() -> bool:
	return session != null


func state() -> CombatState:
	return session.state if session != null else null


## Starts a new fight and announces its first state.
func start_fight(class_id: StringName, enemy_ids: Array[StringName], combat_seed: int, ring_id: StringName = &"") -> void:
	if resolver == null:
		resolver = make_resolver()
	session = CombatSession.start(resolver, class_id, enemy_ids, combat_seed, ring_id)
	fight_started.emit(session.state)
	state_changed.emit(session.state, session.last_events)


## Applies a player action; refused actions only emit action_refused.
func submit(action: CombatAction) -> bool:
	if session == null:
		action_refused.emit("No fight in progress.")
		return false
	var result := netrun.combat_action(action) if netrun != null else session.apply(action)
	if not result.ok():
		action_refused.emit(result.error)
		return false
	state_changed.emit(session.state, result.events)
	if session.state.is_over():
		fight_ended.emit(session.state.outcome)
	return true


func rewind() -> bool:
	if session == null:
		return false
	var result := netrun.combat_rewind() if netrun != null else session.rewind()
	if not result.ok():
		action_refused.emit(result.error)
		return false
	state_changed.emit(session.state, result.events)
	return true


func can_rewind() -> bool:
	return session != null and session.can_rewind()


func preview(action: CombatAction) -> CombatResult:
	return session.preview(action) if session != null else null


func preview_end_turn() -> CombatResult:
	return session.preview_end_turn() if session != null else null


func readouts(c: CombatantState) -> Array[Dictionary]:
	return resolver.pointer_readouts(session.state, c)


func validate(action: CombatAction) -> String:
	return resolver.validate_action(session.state, action) if session != null else "No fight."


func content(id: StringName) -> Resource:
	return resolver.lookup.get_content(id)
