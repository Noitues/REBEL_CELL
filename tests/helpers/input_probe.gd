class_name InputProbe
extends Node
## Test helper (ANIM-R2 R3): a scene-like node whose own `_input` reports every event it
## sees, to check what reaches a scene's handlers during a jack.

signal seen(event: InputEvent)


func _input(event: InputEvent) -> void:
	seen.emit(event)
