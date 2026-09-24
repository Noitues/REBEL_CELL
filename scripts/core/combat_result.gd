class_name CombatResult
extends RefCounted
## What CombatResolver.apply() returns: the new state, the events that explain it, and
## an error when the action was refused (state is then the input, untouched).

var state: CombatState = null
## Plain dictionaries: {"type": String, "text": String, ...}. Views animate these.
var events: Array[Dictionary] = []
var error: String = ""
## END_TURN only: the state right after RESOLVE, before the next START_TURN. This is
## what the End Turn preview shows.
var resolved_state: CombatState = null


func ok() -> bool:
	return error == ""


## Log lines, one per event.
func texts() -> PackedStringArray:
	var out := PackedStringArray()
	for e in events:
		if e.has("text"):
			out.append(String(e["text"]))
	return out
