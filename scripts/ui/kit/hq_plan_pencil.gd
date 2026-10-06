class_name HqPlanPencil
extends Control
## B4 (round 44 `hq_idle.png`, "the one plan"): the HQ idle's one true plan in yellow wax: an
## arrow along the real border link the run will use, from the network's owned end to the
## selected Site (JACK IN's link; the RUNNER tag on the crew's polaroid says who goes). It is
## the kit's one wax (PencilSet: 9 px at 1080p, the under-shadow), written on in 0.4 s when it
## first shows and wiped with the cloth when the plan goes (D25: a pencil never fades). It
## follows the camera each frame (the link's street route, as the map draws it) and stops short
## of the Site's marker so the head points at it. Nothing shows while there is no plan (a Cell
## node selected, no runnable Site, the raid setup). View only: it reads the map.

## The arrow's head (px at 1080), the gap it keeps from the Site's marker (px at 1080), the
## seed of its hand.
const HEAD_PX := 26.0
const STOP_PX := 10.0
const SEED := 4417
## The layout's reference height (px lengths above are at 1080 tall).
const REFERENCE_H := 1080.0

## The map the plan is drawn on, and the link: from the owned end to the Site (&"" = none).
var overlay: CityMapOverlay = null
var from_id: StringName = &""
var to_id: StringName = &""
var pencil: PencilSet


func _init() -> void:
	name = "PlanPencil"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	pencil = PencilSet.under(self)


## Sets the plan (an empty `to` wipes it).
func set_plan(p_overlay: CityMapOverlay, p_from: StringName, p_to: StringName) -> void:
	overlay = p_overlay
	from_id = p_from
	to_id = p_to
	refresh()


func _process(_delta: float) -> void:
	refresh()


## The plan's points now (this control's local px; empty with no plan or off the map).
func plan_points() -> PackedVector2Array:
	var out := PackedVector2Array()
	if overlay == null or not is_instance_valid(overlay) or from_id == &"" or to_id == &"" or not is_inside_tree():
		return out
	var route := overlay.route_between(from_id, to_id)
	if route.size() < 2:
		return out
	var xf := get_global_transform_with_canvas().affine_inverse() * overlay.get_global_transform_with_canvas()
	for p in route:
		out.append(xf * overlay.grid_point_local(p))
	# Start and end on the two markers (the route runs door to door), the head short of the Site.
	var a := overlay.icon_at(from_id)
	var b := overlay.icon_at(to_id)
	if a.is_finite():
		out[0] = xf * a
	if b.is_finite():
		var end := xf * b
		var r := 0.0
		for n in overlay.nodes:
			if n["id"] == to_id:
				r = overlay.icon_radius(n) * xf.get_scale().x
		var k := size.y / REFERENCE_H if size.y > 0.0 else 1.0
		var prev := out[out.size() - 2]
		out[out.size() - 1] = end - (end - prev).normalized() * (r + STOP_PX * k)
	return out


## Lays the arrow (or wipes it when there is no plan).
func refresh() -> void:
	pencil.begin()
	var pts := plan_points()
	if pts.size() >= 2:
		var k := size.y / REFERENCE_H if size.y > 0.0 else 1.0
		pencil.stroke("plan", PencilShapes.arrow(pts, HEAD_PX * k, SEED), GreasePencilMark.Ink.PLAN, PencilSet.AUTO, 0.0, false, SEED)
	pencil.end()
