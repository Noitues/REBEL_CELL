extends RefCounted
## BalanceSkill (BALANCE_SIM S1, "skill knob"): the share of combat turns played well. Plugged into
## the simulators' `turn_override`. With probability `skill` the policy plays the turn (returns
## false); otherwise a novice turn is played here: up to `novice_max_actions` random legal
## actions (cards and nudges, never aimed) and End Turn. skill 1.0 is the policy unchanged;
## ~0.2 models the testers' 15-25 % Perfect rate against an expert. The dice come from an
## RngStreams stream seeded per campaign / run seed, so a seed always plays the same game.

const STREAM := &"balance_skill"

var skill: float = 1.0
var novice_max_actions: int = 2
var rng: RandomNumberGenerator = RandomNumberGenerator.new()


func _init(p_skill: float = 1.0, p_novice_max_actions: int = 2) -> void:
	skill = clampf(p_skill, 0.0, 1.0)
	novice_max_actions = maxi(0, p_novice_max_actions)


## Re-seeds the dice for one campaign / run / fight seed.
func reseed(root_seed: int) -> void:
	rng = RngStreams.make_stream(root_seed, STREAM)


## The `turn_override` callable body: true when this turn was played (and ended) here.
func play(s: NetrunSession) -> bool:
	if skill >= 1.0:
		return false  # no dice drawn at full skill: the policy's game is untouched
	if rng.randf() < skill:
		return false
	var acts := rng.randi_range(0, novice_max_actions)
	for i in acts:
		if not s.in_combat():
			return true
		var candidates := CombatBot._candidates(s.combat)
		if candidates.is_empty():
			break
		s.combat_action(candidates[rng.randi_range(0, candidates.size() - 1)])
	if s.in_combat():
		s.combat_action(CombatAction.end_turn())
	return true
