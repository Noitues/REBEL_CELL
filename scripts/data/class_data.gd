class_name ClassData
extends Resource
## An operative class (Section 5).

@export var id: StringName
@export var display_name: String
@export_multiline var description: String
@export var portrait: Texture2D
@export var starting_wheel: WheelData
@export var starting_deck: Array[CardData] = []
## The class's 1-2 exclusive cards, added to reward pools for this class.
@export var exclusive_cards: Array[CardData] = []
@export var base_hp: int = 60
@export var starting_ram: int = 6
@export var max_ram: int = 12
@export var ram_regen: int = 4
@export var free_nudges_per_turn: int = 1
## Applied to the node this operative is stationed on during raids.
@export var station_bonus: Array[TriggeredEffectData] = []
@export var rank_rewards: Array[RankRewardData] = []
## Class alternatives: id of the base class this one varies (same deck,
## different core, or the reverse). Empty for base classes.
@export var alternative_of: StringName = &""


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if starting_wheel == null:
		errors.append("Class %s has no starting wheel." % id)
	else:
		errors.append_array(starting_wheel.validate())
		if starting_wheel.hub == null or starting_wheel.hub.perfect_hook == null:
			errors.append("Class %s needs a Hub Core with a Perfect hook." % id)
	if starting_deck.is_empty():
		errors.append("Class %s has an empty starting deck." % id)
	for c in exclusive_cards:
		if c and c.class_id != id:
			errors.append("Exclusive card %s is not tagged with class_id %s." % [c.id, id])
	var seen := {}
	for r in rank_rewards:
		if r == null:
			continue
		if seen.has(r.rank):
			errors.append("Class %s has two rewards for rank %d." % [id, r.rank])
		seen[r.rank] = true
	return errors
