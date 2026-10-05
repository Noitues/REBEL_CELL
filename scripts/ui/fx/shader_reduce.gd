class_name ShaderReduce
extends RefCounted
## ART-0 E (ported from the art-pass W6 shader library, ART_BIBLE v2 5.4): the one
## reduce-effects control every animating shader reads, the `reduce_effects` uniform of
## `shaders/lib/rc_common.gdshaderinc` (1 under reduce effects, 0 otherwise). On the art-pass
## branch it was a global shader uniform in project.godot; main keeps project.godot as it is,
## so each ShaderMaterial built on such a shader is tracked here and set when the setting
## changes. Fx calls `set_reduce` from Settings on start and on every change; a view that
## builds a material calls `track`. View only: no game state.

## The uniform's name in rc_common.
const UNIFORM := &"reduce_effects"

## The value last set (0 or 1): new materials start at it.
static var value: float = 0.0
static var _materials: Array[WeakRef] = []


## Sets `mat`'s reduce_effects to the current value and keeps it in step with later changes
## (held weakly: a freed material drops out). Returns `mat`.
static func track(mat: ShaderMaterial) -> ShaderMaterial:
	if mat == null:
		return mat
	mat.set_shader_parameter(UNIFORM, value)
	for w in _materials:
		if w.get_ref() == mat:
			return mat
	_materials.append(weakref(mat))
	return mat


## Sets every tracked material's reduce_effects: 1.0 when `reduce` is on, else 0.0.
static func set_reduce(reduce: bool) -> void:
	value = 1.0 if reduce else 0.0
	var kept: Array[WeakRef] = []
	for w in _materials:
		var m := w.get_ref() as ShaderMaterial
		if m != null:
			m.set_shader_parameter(UNIFORM, value)
			kept.append(w)
	_materials = kept


## How many tracked materials are still alive (tests).
static func tracked_count() -> int:
	var n := 0
	for w in _materials:
		if w.get_ref() != null:
			n += 1
	return n


## Lets the tracked materials go (Fx at exit, like UiTheme.release).
static func release() -> void:
	_materials.clear()
