extends Node
## ColorblindFilter autoload (ART_BIBLE §12, art pass W9): keeps one ColorblindLayer (the
## full-screen daltonize pass) in the tree while `Settings.colorblind_mode` is deutan,
## protan or tritan, and none at all while it is off (no layer, no cost). Follows
## Settings.changed. View only.

## The correction layer, or null while the mode is off.
var layer: ColorblindLayer = null


func _ready() -> void:
	Settings.changed.connect(sync)
	sync()


## Adds, updates or frees the layer to match `Settings.colorblind_mode`.
func sync() -> void:
	var mode: StringName = Settings.colorblind_mode
	if not ColorblindLayer.MODES.has(mode):
		if layer != null and is_instance_valid(layer):
			layer.queue_free()
			remove_child(layer)
		layer = null
		return
	if layer == null or not is_instance_valid(layer):
		layer = ColorblindLayer.new(mode)
		add_child(layer)
	else:
		layer.set_mode(mode)


## The mode the screen is corrected for (&"off" when no layer is up).
func active_mode() -> StringName:
	return layer.mode if layer != null and is_instance_valid(layer) else &"off"
