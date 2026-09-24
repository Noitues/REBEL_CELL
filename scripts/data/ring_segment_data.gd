class_name RingSegmentData
extends Resource
## One of the 3 Inner Ring segments. Segments change wheel state or
## modify the outer slice that resolves with them.

@export var id: StringName
@export var display_name: String
@export_multiline var description: String
@export var output_multiplier: float = 1.0
## Ignore block and satellites.
@export var pierce: bool = false
@export var triggered_effects: Array[TriggeredEffectData] = []
