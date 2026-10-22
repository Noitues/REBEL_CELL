extends GutTest
## LOOK-TOOLBOX (fast tier): the shared sight rule (RcLookOcclusion). With a plain pinhole looking down +Z at a subject
## box: a tall block in front gives way, a low one under the sight line off to the side stays, nothing behind the
## subject's middle or inside its footprint is cut, and an obstacle that covers the subject on screen goes even outside
## the wedge. The combat backdrop's view cut is this rule (BackdropCatalog.view_cut / occludes).

const EYE := Vector3(0.0, 10.0, 0.0)
const FOCAL := 800.0
const SCREEN_MID := Vector2(960.0, 540.0)

var _s: Dictionary


## A pinhole looking down +Z (y up): non-finite behind the eye.
static func _project(p: Vector3) -> Vector2:
	var z := p.z - EYE.z
	if z <= 0.01:
		return Vector2(INF, INF)
	return SCREEN_MID + Vector2((p.x - EYE.x) / z, -(p.y - EYE.y) / z) * FOCAL


func before_each() -> void:
	var subject := AABB(Vector3(-10.0, 0.0, 200.0), Vector3(20.0, 60.0, 20.0))
	_s = RcLookOcclusion.sight(_project, EYE, Vector3(0.0, 0.0, 1.0), subject, 4.0, 0.5, 24.0, 5.0)


func test_a_tall_block_in_front_gives_way() -> void:
	assert_true(RcLookOcclusion.hides(_s, Vector2(0.0, 100.0), 80.0))


func test_what_stands_behind_or_in_the_subject_stays() -> void:
	assert_false(RcLookOcclusion.hides(_s, Vector2(0.0, 260.0), 300.0), "behind the subject")
	assert_false(RcLookOcclusion.hides(_s, Vector2(0.0, 205.0), 300.0), "the subject's own footprint")
	assert_false(RcLookOcclusion.hides(_s, Vector2(0.0, -20.0), 300.0), "behind the eye")


func test_a_low_roof_off_the_subject_stays() -> void:
	assert_false(RcLookOcclusion.hides(_s, Vector2(60.0, 100.0), 2.0), "low and to the side: no overlap on screen")


func test_the_screen_rule_cuts_outside_the_wedge() -> void:
	# Just outside the wedge at this depth, but its footprint still covers the subject on screen.
	var at := Vector2(10.0, 100.0)
	var v := at - Vector2(EYE.x, EYE.z)
	assert_true(v.x > float(_s["hi"]) * v.y + float(_s["pad"]), "outside the wedge")
	assert_true(RcLookOcclusion.hides(_s, at, 120.0), "but it covers the subject on screen")


func test_screen_box_is_empty_behind_the_eye() -> void:
	assert_eq(RcLookOcclusion.screen_box(_project, AABB(Vector3(-1, 0, -5), Vector3(2, 2, 2))), Rect2())
