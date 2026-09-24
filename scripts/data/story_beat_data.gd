class_name StoryBeatData
extends Resource
## One story reveal.

@export var id: StringName
@export var title: String
@export var speaker: RC.Voice = RC.Voice.NARRATOR
@export_multiline var text: String
## Contains a hidden DISPATCH clue.
@export var dispatch_clue: bool = false
## Revealing this beat queues the corporation's STORY raid (GDD 4.4).
@export var triggers_raid: bool = false
