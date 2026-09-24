class_name StoryPathData
extends Resource
## One of a corporation's 5-6 hidden story paths (8.4). Picked at random
## at campaign start; beats reveal in the order Exploits are collected.

@export var id: StringName
@export var title: String
@export_multiline var premise: String
## Revealed by the 1st, 2nd, 3rd... Exploit collected.
@export var beats: Array[StoryBeatData] = []
## Revealed by Exploits beyond the minimum.
@export var bonus_beats: Array[StoryBeatData] = []
@export var finale: StoryBeatData
## Corporation id or &"dispatch" this path hints at. Empty = none.
@export var foreshadows: StringName = &""
@export var weight: float = 1.0


func validate(min_exploits: int) -> PackedStringArray:
	var errors := PackedStringArray()
	if beats.size() < min_exploits:
		errors.append("Path %s needs at least %d beats, has %d." % [id, min_exploits, beats.size()])
	if finale == null:
		errors.append("Path %s has no finale." % id)
	return errors
