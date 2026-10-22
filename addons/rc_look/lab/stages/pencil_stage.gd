extends RcLookLabStage
## LOOK-TOOLBOX module 12 in the lab: the grease pencil through its public API only (PencilSet, GreasePencilWord,
## PencilShapes, HandMarks, RcPencilWorldAnchor), laid out as the golden plates' marks: the combat aim arc and loop
## (r11 combat_boss_night), the overlay kit's HIT IT, rings and what-if arrow (round 3 04_kit_sheet), the red underline
## with its hook (r11), the grid and route TARGET, the raid threat route, the netrun plan in orange, the hand marks, a
## ring pinned to a 3D box, and the RC Wax alphabet. Canvas px (1280 x 720).

## Cell origins (canvas px).
const AIM := Vector2(20, 20)
const KIT := Vector2(450, 20)
const TARGETS := Vector2(880, 20)
const LINES := Vector2(20, 360)
const ROUTES := Vector2(450, 360)
const MARKS := Vector2(880, 360)
## The alphabet's baseline and type step.
const ALPHA_AT := Vector2(30, 690)
const ALPHA_STEP := UiTheme.TITLE
## The 3D cell: its rect (canvas px), the box, the camera.
const WORLD_RECT := Rect2(1080, 360, 190, 170)
const BOX := Vector3(1.2, 1.6, 1.2)
const CAM_AT := Vector3(2.6, 2.4, 3.4)
## A dim plate behind the wheel and the chips (the concept's dark glass), its alpha.
const PLATE := Color(0.02, 0.025, 0.04, 0.55)

var _set_pencil: PencilSet
var _cam: Camera3D
var _vp_box: SubViewportContainer
var _anchor: RcPencilWorldAnchor
var _anchor_set: PencilSet


func _ready() -> void:
	_set_pencil = PencilSet.under(self)
	_build_world()


func settle_frames() -> int:
	return 45


func apply(_time: StringName, quality: RcLookQualityState) -> void:
	Settings.reduce_effects = quality.reduce_effects
	Settings.reduce_motion = quality.reduce_motion
	Settings.high_contrast = quality.high_contrast
	Settings.changed.emit()
	_set_pencil.wipe_all()
	for c in _set_pencil.get_children():
		c.free()
	_set_pencil.free()
	_set_pencil = PencilSet.under(self)
	_lay()
	queue_redraw()


func _draw() -> void:
	# the wheel the aim points at and the chips the lines underline: neutral props
	draw_circle(AIM + Vector2(330, 130), 78.0, PLATE)
	draw_arc(AIM + Vector2(330, 130), 78.0, 0.0, TAU, 64, Color(0.55, 0.45, 0.25), 3.0)
	draw_rect(Rect2(LINES + Vector2(20, 20), Vector2(170, 40)), PLATE)
	draw_rect(Rect2(LINES + Vector2(230, 20), Vector2(170, 40)), PLATE)
	draw_rect(Rect2(MARKS + Vector2(0, 0), Vector2(80, 110)), PLATE)
	draw_rect(Rect2(MARKS + Vector2(100, 0), Vector2(80, 110)), PLATE)
	var f := Palette.display()
	draw_string(f, LINES + Vector2(32, 50), "NEXT 27 (-14)", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Palette.PAPER)
	draw_string(f, LINES + Vector2(242, 50), "HP 60-56", HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Palette.PAPER)
	for p: Vector2 in [ROUTES + Vector2(30, 280), ROUTES + Vector2(380, 40), ROUTES + Vector2(40, 40), ROUTES + Vector2(380, 290)]:
		draw_circle(p, 10.0, Palette.PAPER)


func _lay() -> void:
	var s := _set_pencil
	s.begin()
	# the combat aim: a bowed hero arrow from the card to the wheel, the hero loop round it
	var aim := {"from": AIM + Vector2(30, 300), "to": AIM + Vector2(330, 130), "stop": 86.0,
		"loop": {"key": "w", "center": AIM + Vector2(330, 130), "radius": 78.0}}
	var sh := AimLinePencil.shapes(aim)
	s.stroke("aim", sh["arrow"], GreasePencilMark.Ink.PLAN, PencilSet.AUTO, 0.0, false, AimLinePencil.ARROW_SEED, true)
	s.stroke("loop", sh["loop"], GreasePencilMark.Ink.PLAN, PencilSet.AUTO, 0.0, false, AimLinePencil.LOOP_SEED, true)
	# the overlay kit: HIT IT, its hand arrow into a hero ring; a plan ring; a what-if arrow
	s.word("hit", "HIT IT", KIT + Vector2(95, 45), UiTheme.DISPLAY, GreasePencilMark.Ink.THREAT, 1.0, PencilSet.AUTO, 0.0, -0.03, true)
	var shaft := PencilShapes.hand_path(PencilShapes.bezier(KIT + Vector2(195, 62), KIT + Vector2(225, 82), KIT + Vector2(262, 62)), 9,
		GreasePencilMark.stroke_width())
	s.stroke("hit_arrow", PencilShapes.arrow(shaft, GreasePencilMark.stroke_width() * RaidPencil.HEAD_LEN, 9), GreasePencilMark.Ink.THREAT)
	s.circle("hit_ring", KIT + Vector2(320, 55), Vector2(48, 46), GreasePencilMark.Ink.THREAT, 5, PencilSet.AUTO, true)
	s.circle("plan_ring", KIT + Vector2(70, 180), Vector2(40, 50), GreasePencilMark.Ink.PLAN, 21, PencilSet.AUTO, true)
	var wi := PencilShapes.hand_path(PencilShapes.bezier(KIT + Vector2(10, 300), KIT + Vector2(200, 230), KIT + Vector2(330, 180)), 4,
		GreasePencilMark.stroke_width())
	s.stroke("whatif", PencilShapes.arrow(wi, GreasePencilMark.stroke_width() * RaidPencil.HEAD_LEN, 4), GreasePencilMark.Ink.PLAN,
		PencilSet.AUTO, 0.0, true, 4)
	# the grid TARGET (ring and word clear of it) and the route TARGET with its arrow
	s.circle("t_ring", TARGETS + Vector2(250, 90), Vector2(70, 44), GreasePencilMark.Ink.THREAT, CityMapOverlay.TARGET_SEED, PencilSet.AUTO, true)
	s.word("t_word", "TARGET", TARGETS + Vector2(95, 150), UiTheme.HEADING, GreasePencilMark.Ink.THREAT, 1.0, PencilSet.AUTO, 0.0, -0.06, true)
	s.word("r_word", "TARGET", TARGETS + Vector2(120, 240), RouteOverlay.TARGET_FONT, GreasePencilMark.Ink.THREAT, 1.0, PencilSet.AUTO, 0.0, -0.12)
	var ra := PencilShapes.hand_path(PackedVector2Array([TARGETS + Vector2(200, 285), TARGETS + Vector2(320, 278)]), 12, GreasePencilMark.stroke_width())
	s.stroke("r_arrow", PencilShapes.arrow(ra, GreasePencilMark.stroke_width() * RaidPencil.HEAD_LEN, 12), GreasePencilMark.Ink.THREAT)
	# the underlines under the chips: red (a loss) and yellow (the result), each with its hook
	s.stroke("u_red", [PencilShapes.hand_line(LINES + Vector2(22, 72), LINES + Vector2(188, 72), 17, GreasePencilMark.stroke_width())],
		GreasePencilMark.Ink.THREAT)
	s.stroke("u_yel", [PencilShapes.hand_line(LINES + Vector2(232, 72), LINES + Vector2(398, 72), 23, GreasePencilMark.stroke_width())],
		GreasePencilMark.Ink.PLAN)
	s.word("note", "PLAY IT SAFE??", LINES + Vector2(210, 160), UiTheme.TITLE, GreasePencilMark.Ink.PLAN, 1.0, PencilSet.AUTO, 0.0, -0.06)
	s.word("down", "Down with the Oligarchy!", LINES + Vector2(210, 230), UiTheme.LABEL, GreasePencilMark.Ink.PLAN, 1.0, PencilSet.AUTO, 0.0, -0.04)
	# the raid threat route (street corners) and the netrun plan (orange) along its link
	var threat := PackedVector2Array([ROUTES + Vector2(30, 280), ROUTES + Vector2(140, 280), ROUTES + Vector2(140, 170),
		ROUTES + Vector2(290, 170), ROUTES + Vector2(380, 40)])
	s.stroke("threat", PencilShapes.arrow(PencilShapes.hand_route(threat, 31, GreasePencilMark.stroke_width()),
		GreasePencilMark.stroke_width() * RaidPencil.HEAD_LEN, 31), GreasePencilMark.Ink.THREAT)
	var plan := PackedVector2Array([ROUTES + Vector2(40, 40), ROUTES + Vector2(40, 120), ROUTES + Vector2(230, 120),
		ROUTES + Vector2(230, 290), ROUTES + Vector2(366, 290)])
	s.stroke("plan", PencilShapes.arrow(PencilShapes.hand_route(plan, 4417, GreasePencilMark.stroke_width()),
		GreasePencilMark.stroke_width() * RaidPencil.HEAD_LEN, 4417), GreasePencilMark.Ink.PLAN_NETRUN)
	# the hand marks (remove / upgrade) through HandMarks' strokes
	s.stroke("x", HandMarks.x_strokes(Rect2(MARKS, Vector2(80, 110)), 613), GreasePencilMark.Ink.THREAT)
	s.stroke("o", HandMarks.loop_strokes(MARKS + Vector2(140, 55), Vector2(38, 44), 613), GreasePencilMark.Ink.PLAN)
	# the alphabet
	s.word("abc", "ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789 !?", ALPHA_AT + Vector2(560, 0), ALPHA_STEP, GreasePencilMark.Ink.PLAN,
		1.0, PencilSet.AUTO, 0.0, 0.0)
	s.end()
	# the ring pinned to the 3D box's top
	_anchor.follow()
	_anchor_set.begin()
	_anchor_set.circle("box", Vector2.ZERO, Vector2(46, 26), GreasePencilMark.Ink.THREAT, 77, PencilSet.AUTO, true)
	_anchor_set.end()


func _build_world() -> void:
	_vp_box = SubViewportContainer.new()
	_vp_box.position = WORLD_RECT.position
	_vp_box.size = WORLD_RECT.size
	_vp_box.stretch = true
	add_child(_vp_box)
	var vp := SubViewport.new()
	vp.own_world_3d = true
	vp.transparent_bg = true
	_vp_box.add_child(vp)
	var box := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = BOX
	box.mesh = mesh
	vp.add_child(box)
	var sun := DirectionalLight3D.new()
	sun.rotation = Vector3(-0.9, 0.6, 0.0)
	vp.add_child(sun)
	_cam = Camera3D.new()
	vp.add_child(_cam)
	_cam.look_at_from_position(CAM_AT, Vector3.ZERO)
	_anchor = RcPencilWorldAnchor.new(_project, Vector3(0.0, BOX.y * 0.5, 0.0))
	add_child(_anchor)
	_anchor_set = PencilSet.under(_anchor)


## The box's world point in the lab's viewport px: the sub-viewport camera, then the container's place.
func _project(p: Vector3) -> Vector2:
	if _cam == null or _cam.is_position_behind(p):
		return Vector2.INF
	var vp := _cam.get_viewport() as SubViewport
	var k := _vp_box.size / Vector2(vp.size)
	return _vp_box.get_global_transform_with_canvas() * (_cam.unproject_position(p) * k)
