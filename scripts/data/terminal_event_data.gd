class_name TerminalEventData
extends Resource
## A Terminal node event (4.1), including ambient lore and DISPATCH clues.

@export var id: StringName
@export var title: String
@export var speaker: RC.Voice = RC.Voice.NARRATOR
@export_multiline var text: String
@export var choices: Array[EventChoiceData] = []
## Empty = any corporation.
@export var corporation_id: StringName = &""
@export_range(1, 4) var min_tier: int = 1
@export var dispatch_clue: bool = false
## Corporation id this event hints at. Empty = none.
@export var foreshadows: StringName = &""
@export var weight: float = 1.0
## Plan 2 EV-01: where the event is drawn. TERMINAL = a netrun Terminal node (the only venue
## with a host today). RAID_WIN (after a raid is won) and HQ_VIEW (at the HQ) are authored
## ahead of their hosts; the Terminal pool never draws them.
enum Venue { TERMINAL, RAID_WIN, HQ_VIEW }
@export var venue: Venue = Venue.TERMINAL


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if choices.is_empty():
		errors.append("event_no_choices: an event needs at least one choice.")
	for c in choices:
		if c != null:
			errors.append_array(c.validate())
	return errors
