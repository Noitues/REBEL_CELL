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
