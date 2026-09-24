class_name NetrunBoostData
extends Resource
## A one-time netrun boost bought at HQ for Schematics (GDD 11.4: 10-20) and consumed by
## the next run launched: starting Cycles, run-only cards, extra max RAM.

@export var id: StringName
@export var display_name: String
@export_multiline var description: String
@export_range(1, 100) var cost: int = 10
## Cycles the run starts with.
@export var cycles: int = 0
## Cards added to the working deck for this run only (removed on completion).
@export var temp_cards: Array[CardData] = []
## Added to the class max RAM for every combat of the run.
@export var max_ram_bonus: int = 0


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if cycles == 0 and temp_cards.is_empty() and max_ram_bonus == 0:
		errors.append("Boost %s does nothing." % id)
	return errors
