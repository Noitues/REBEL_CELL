class_name InnerRingData
extends Resource

@export var segments: Array[RingSegmentData] = []


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if segments.size() != RC.RING_SEGMENTS:
		errors.append("Inner ring needs %d segments, has %d." % [RC.RING_SEGMENTS, segments.size()])
	for s in segments:
		if s == null:
			errors.append("Inner ring has an empty segment.")
	return errors
