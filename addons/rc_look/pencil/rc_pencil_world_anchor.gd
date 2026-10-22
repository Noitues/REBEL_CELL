class_name RcPencilWorldAnchor
extends Node2D
## LOOK-TOOLBOX 12: a pencil pin on a world point. Put marks and words under it in local px round the point: each frame
## it moves to `world` through `projector` (RcPencilAnchor: a Camera3D or a Callable) in its parent's px, and hides
## while the point is behind the camera. `scale_unit` > 0 also scales it so `scale_unit` world units are `unit_px` px
## (a ring that keeps the size of its building as the camera zooms); 0 keeps one screen size (the wax's width is one
## screen width anyway). Static under reduce motion like the camera it follows. View only.

## The world point and the projector (Camera3D or Callable (Vector3) -> Vector2).
var world: Vector3 = Vector3.ZERO
var projector: Variant = null
## World units that should measure `unit_px` px at the point (0: no world scale).
var scale_unit: float = 0.0
var unit_px: float = 1.0


func _init(p_projector: Variant = null, p_world: Vector3 = Vector3.ZERO) -> void:
	projector = p_projector
	world = p_world


func _process(_delta: float) -> void:
	follow()


## Moves to the world point now (tests and owners that lay their marks in the same frame call it directly).
func follow() -> void:
	var parent := get_parent() as CanvasItem
	var s := RcPencilAnchor.screen_point(projector, world)
	visible = s.is_finite()
	if not visible:
		return
	position = RcPencilAnchor.to_canvas(parent, s) if parent != null else s
	if scale_unit > 0.0:
		var k := RcPencilAnchor.px_per_unit(projector, world) * scale_unit / maxf(unit_px, 0.001)
		if k > 0.0:
			scale = Vector2.ONE * k
