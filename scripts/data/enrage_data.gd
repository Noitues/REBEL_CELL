class_name EnrageData
extends Resource
## Plan 2 R4 / N4: a turn-based enrage. From `start_turn` on, every `every_n_turns` turns the
## enemy gains one step; each step adds `damage_pct_step` percent to its hits (additive:
## 3 steps of 25 % is x1.75, never 1.25^3; designer ruling Q33, 2026-10-18) and
## `resistance_step` to its per-turn resistance. The step is a pure function of the turn
## counter: no RNG, nothing to save beyond the turn. Class defaults live in
## CampaignConfigData (enrage_*_by_class); an EnemyData may author its own.

## The first turn of step 1 (turn 1 is the first turn of the fight).
@export var start_turn: int = 10
## Turns between steps after step 1.
@export var every_n_turns: int = 5
## Percent added to the enemy's hits per step (RC.PERCENT_MAX = x2 per step).
@export var damage_pct_step: int = 25
## Resistance added to the enemy's per-turn resistance per step (Q16: an option for
## authored enrages; the class defaults are damage-only).
@export var resistance_step: int = 0


## Each error starts with the offending field's name.
func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if start_turn < 1:
		errors.append("start_turn: enrage start_turn %d must be >= 1." % start_turn)
	if every_n_turns < 1:
		errors.append("every_n_turns: enrage every_n_turns %d must be >= 1." % every_n_turns)
	if damage_pct_step < 0:
		errors.append("damage_pct_step: enrage damage_pct_step %d must be >= 0." % damage_pct_step)
	if resistance_step < 0:
		errors.append("resistance_step: enrage resistance_step %d must be >= 0." % resistance_step)
	return errors


## The step on `turn`: 0 before start_turn, then 1 + one per every_n_turns.
func enrage_step(turn: int) -> int:
	if turn < start_turn or every_n_turns < 1:
		return 0
	@warning_ignore("integer_division")
	return 1 + (turn - start_turn) / every_n_turns


## The hit factor at `step` in percent (100 = unchanged): 100 + step x damage_pct_step.
func damage_percent_at_step(step: int) -> int:
	return RC.PERCENT_MAX + maxi(0, step) * damage_pct_step


## The hit factor on `turn` as a float (for display): 1 + step x pct.
func enrage_multiplier(turn: int) -> float:
	return float(damage_percent_at_step(enrage_step(turn))) / RC.PERCENT_MAX


## The resistance `step` adds.
func resistance_at_step(step: int) -> int:
	return maxi(0, step) * resistance_step


## The first turn of step `step` + 1 (the next step after `step`).
func next_step_turn(step: int) -> int:
	return start_turn + maxi(0, step) * every_n_turns


## `amount` scaled by `percent` (damage_percent_at_step), in integers, rounded half up (10 at x1.25 is 13).
static func scale_hit(amount: int, percent: int) -> int:
	if amount <= 0 or percent == RC.PERCENT_MAX:
		return amount
	@warning_ignore("integer_division")
	return (amount * percent + RC.PERCENT_MAX / 2) / RC.PERCENT_MAX
