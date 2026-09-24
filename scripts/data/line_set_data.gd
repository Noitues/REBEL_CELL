class_name LineSetData
extends Resource
## A set of voice lines for one speaker (GDD 8.1 tone map): DISPATCH briefings for a
## corporation, a class's operative barks, the pirate-radio DJ, corporate raid warnings.

@export var id: StringName
@export var speaker: RC.Voice = RC.Voice.DISPATCH
## Empty = any corporation.
@export var corporation_id: StringName = &""
## Barks: the class that says them. Empty = any.
@export var class_id: StringName = &""
@export var lines: Array[VoiceLineData] = []


func lines_for(key: String) -> Array[VoiceLineData]:
	var out: Array[VoiceLineData] = []
	for l in lines:
		if l != null and l.key == key:
			out.append(l)
	return out


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	for l in lines:
		if l == null:
			errors.append("Line set %s has an empty entry." % id)
		elif l.key == "" or l.text == "":
			errors.append("Line set %s has a line without key or text." % id)
	return errors
