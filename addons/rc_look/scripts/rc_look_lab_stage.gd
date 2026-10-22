class_name RcLookLabStage
extends Control
## LOOK-TOOLBOX module 3: one module's lab stage. The look lab (addons/rc_look/lab/look_lab.tscn) adds the stage full
## screen over its neutral set and calls `apply` for each capture: day or night, and a quality state. A stage shows
## its module only through the module's public API, so the lab shows what the game gets. View only.

## Day or night ("day" / "night") and the quality state of the next capture. Override in a stage.
func apply(_time: StringName, _quality: RcLookQualityState) -> void:
	pass


## Frames to wait after `apply` before the capture (write-on motions, shader warm-up). Override when needed.
func settle_frames() -> int:
	return 6
