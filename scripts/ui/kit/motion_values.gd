class_name MotionValues
extends Node
## ANIM-R2 R9: named values a view's motion tweens (`Motion.run(id, values, ^"name", to)`),
## kept on a plain node so a tween step redraws only what the view says (`changed`), not the
## whole view: a map's selection draw-on redrew every node and label each frame. View only.

## `name` took a new value.
signal changed(name: StringName)

var _values: Dictionary = {}


func _init(defaults: Dictionary = {}) -> void:
	name = "MotionValues"
	_values = defaults.duplicate()


## The value of `key` (`fallback` when unset).
func value(key: StringName, fallback: float = 1.0) -> float:
	return float(_values.get(key, fallback))


## Sets `key` and says so.
func put(key: StringName, v: float) -> void:
	_values[key] = v
	changed.emit(key)


func _get(property: StringName) -> Variant:
	if _values.has(property):
		return _values[property]
	return null


func _set(property: StringName, v: Variant) -> bool:
	if _values.has(property):
		put(property, float(v))
		return true
	return false
