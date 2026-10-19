class_name ListenerData
extends Resource
## Plan 2 N6: an enemy listener, "when the player does X, do these effects". Authored on an
## EnemyData (`listeners`, kept through phases) or on a HubCoreData (`listeners`, off while
## the Hub is breached, swapped by a phase's hub_override). Fires inside the player's
## accepted action (ON_NUDGE, ON_CARD_PLAYED, ON_RAM_SPENT) or after the slice passes of
## RESOLVE (ON_PERFECT, ON_HIT_DEALT). Draws no RNG, never fires another listener, and the
## preview shows its result exactly (rulings Q8 a, Q19).

## Triggers a listener may hear (validate refuses any other: `trigger_not_listenable`).
const TRIGGERS: Array[int] = [RC.Trigger.ON_NUDGE, RC.Trigger.ON_CARD_PLAYED, RC.Trigger.ON_PERFECT,
	RC.Trigger.ON_RAM_SPENT, RC.Trigger.ON_HIT_DEALT]
## Effect types that draw RNG (validate refuses them: `rng_effect`).
const RNG_TYPES: Array[int] = [RC.EffectType.RESPIN, RC.EffectType.DRAW_CARDS, RC.EffectType.CUSTOM]
## A cap left at this value is unauthored: per turn reads the config default, per combat is
## unlimited.
const UNAUTHORED: int = -1

@export var trigger: RC.Trigger = RC.Trigger.ON_PERFECT
## Effects run with the listening enemy as owner and the operative as the target.
## DEAL_DAMAGE FLAT scales by the owner's tier factor; PERCENT is a share of the owner's max
## HP, never rescaled.
@export var effects: Array[EffectData] = []
## Fires at most this often per turn; UNAUTHORED (-1) reads
## CampaignConfigData.listener_max_per_turn_default (designer 2026-10-18 N6 answer 1).
@export var max_per_turn: int = UNAUTHORED
## Fires at most this often per combat; UNAUTHORED (-1) = no combat cap.
@export var max_per_combat: int = UNAUTHORED
## ON_HIT_DEALT / ON_PERFECT: the least precision tier of the landing slice. Actions
## (nudge, card, RAM) carry no tier and always pass.
@export var min_tier: RC.PrecisionTier = RC.PrecisionTier.WEAK


## The per-turn cap in force: the authored one, else the config default.
func turn_cap(config: CampaignConfigData) -> int:
	return max_per_turn if max_per_turn != UNAUTHORED else config.listener_max_per_turn_default


## Each error starts with a stable code: trigger_not_listenable, no_effects, empty_effect,
## cap_not_positive, rng_effect, then the effect's own codes (PERCENT is allowed on
## DEAL_DAMAGE here: a share of the owner's max HP).
func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if not (int(trigger) in TRIGGERS):
		errors.append("trigger_not_listenable: %s is not a listener trigger." % _trigger_name())
	if effects.is_empty():
		errors.append("no_effects: listener on %s has no effects." % _trigger_name())
	for cap in [max_per_turn, max_per_combat]:
		if cap != UNAUTHORED and cap < 1:
			errors.append("cap_not_positive: listener cap %d; at least 1 (or -1 for unauthored)." % cap)
	for e in effects:
		if e == null:
			errors.append("empty_effect: listener on %s contains an empty entry." % _trigger_name())
			continue
		if int(e.type) in RNG_TYPES or e.slice_pick == RC.SlicePick.RANDOM_NON_NULL:
			errors.append("rng_effect: %s would draw RNG inside a listener." % RC.EffectType.keys()[e.type])
		for problem in e.validate():
			if e.type == RC.EffectType.DEAL_DAMAGE and problem.begins_with("mode_unsupported_for_type"):
				continue
			errors.append(problem)
	return errors


func _trigger_name() -> String:
	var keys := RC.Trigger.keys()
	return keys[trigger] if trigger >= 0 and trigger < keys.size() else str(trigger)
