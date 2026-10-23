extends RcLookLabStage
## LOOK-TOOLBOX module 17 in the lab: the Blender exports' material slots. Each tile renders one export (the post-import
## pilots, a landmark, street kit pieces) with every surface in a flat colour by its look role (RcLookSlots.of), so a slot
## that falls to the wrong role shows at a glance; the tile's label lists slot -> family:role, and an unlisted slot in red.
## Day / night and the quality state change nothing (slots are data). View only.

const FILES: Array[String] = [
	"res://assets/raid/uplink/uplink_pads.glb",
	"res://assets/city/roof_props/roof_props.glb",
	"res://assets/city/landmarks/meridian/meridian_hq.glb",
	"res://assets/street_kit/lamp_post.glb",
	"res://assets/street_kit/neon_blade_tube.glb",
	"res://assets/street_kit/lit_window.glb",
	"res://assets/street_kit/awning.glb",
	"res://assets/street_kit/ground_car.glb",
]
const COLS := 4
const MARGIN := 16.0
const LABEL_PX := 12
const LABEL_H := 88.0
const LABEL_COLOR := Color(0.88, 0.9, 0.95)
const BAD_COLOR := Color(1.0, 0.25, 0.25)
const BG := Color(0.11, 0.11, 0.13)
## Role -> flat colour (the street surfaces, the landmark roles by number; anything else grey).
const ROLE_COLORS := {"solid": Color(0.45, 0.45, 0.5), "conc": Color(0.62, 0.58, 0.5), "panel": Color(0.35, 0.55, 0.75),
	"glass": Color(0.5, 0.85, 0.95), "win": Color(1.0, 0.85, 0.4), "neon": Color(1.0, 0.3, 0.75), "lamp_emit": Color(1.0, 0.95, 0.7),
	"car_head": Color(1.0, 0.97, 0.9), "car_tail": Color(1.0, 0.18, 0.14),
	"-1": Color(1.0, 1.0, 1.0), "0": Color(0.5, 0.5, 0.55), "1": Color(0.3, 0.3, 0.35), "2": Color(0.9, 0.75, 0.5),
	"3": Color(1.0, 0.3, 0.75), "4": Color(1.0, 0.85, 0.4), "5": Color(0.95, 0.6, 0.2), "6": Color(0.8, 0.7, 0.3),
	"7": Color(0.95, 0.4, 0.1), "8": Color(0.4, 0.9, 0.6)}
const OTHER := Color(0.6, 0.6, 0.6)
## Camera: yaw / pitch (deg) round the export's box, its distance in box diagonals, the light.
const YAW := 35.0
const PITCH := 22.0
const DIST_K := 1.25
const FOV := 40.0

var _built := false


func apply(_time: StringName, _quality: RcLookQualityState) -> void:
	if _built:
		return
	_built = true
	var vs := get_viewport_rect().size
	var rows := int(ceil(float(FILES.size()) / COLS))
	var tile := Vector2((vs.x - MARGIN * (COLS + 1)) / COLS, (vs.y - MARGIN * (rows + 1)) / rows - LABEL_H)
	var bg := ColorRect.new()
	bg.color = BG
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	for i in FILES.size():
		var at := Vector2(MARGIN + (i % COLS) * (tile.x + MARGIN), MARGIN + (i / COLS) * (tile.y + LABEL_H + MARGIN))
		_tile(FILES[i], at, tile)


func settle_frames() -> int:
	return 12


func _tile(file: String, at: Vector2, size: Vector2) -> void:
	var svc := SubViewportContainer.new()
	svc.position = at
	svc.size = size
	svc.stretch = true
	add_child(svc)
	var vp := SubViewport.new()
	vp.own_world_3d = true
	vp.transparent_bg = false
	svc.add_child(vp)
	var root := (load(file) as PackedScene).instantiate() as Node3D
	vp.add_child(root)
	var box := AABB()
	var first := true
	var lines := PackedStringArray([file.get_file()])
	var seen := {}
	for e: Dictionary in RcLookSlots.surfaces(root):
		var mi := root.get_node(NodePath(String(e["node"]))) as MeshInstance3D if String(e["node"]) != "." else root as MeshInstance3D
		var key := str(e["role"])
		var mat := StandardMaterial3D.new()
		mat.shading_mode = BaseMaterial3D.SHADING_MODE_PER_PIXEL
		mat.albedo_color = ROLE_COLORS.get(key, OTHER) if bool(e["listed"]) else BAD_COLOR
		mi.set_surface_override_material(int(e["surface"]), mat)
		var wb := mi.global_transform * mi.mesh.get_aabb()
		box = wb if first else box.merge(wb)
		first = false
		var line := "%s -> %s:%s%s" % [e["slot"], e["family"], e["role"], "" if bool(e["listed"]) else "  UNLISTED"]
		if not seen.has(line):
			seen[line] = true
			lines.append(line)
	var cam := Camera3D.new()
	cam.fov = FOV
	vp.add_child(cam)
	var c := box.get_center()
	var d := box.size.length() * DIST_K
	var dir := Vector3(sin(deg_to_rad(YAW)) * cos(deg_to_rad(PITCH)), sin(deg_to_rad(PITCH)), cos(deg_to_rad(YAW)) * cos(deg_to_rad(PITCH)))
	cam.look_at_from_position(c + dir * d, c)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-50.0, 30.0, 0.0)
	vp.add_child(sun)
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = BG.lightened(0.08)
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color(0.5, 0.5, 0.55)
	vp.add_child(env)
	var lab := Label.new()
	lab.position = at + Vector2(0.0, size.y + 2.0)
	lab.size = Vector2(size.x, LABEL_H)
	lab.add_theme_font_size_override(&"font_size", LABEL_PX)
	lab.add_theme_color_override(&"font_color", LABEL_COLOR if not "\n".join(lines).contains("UNLISTED") else BAD_COLOR)
	lab.text = "\n".join(lines)
	lab.clip_text = true
	add_child(lab)
