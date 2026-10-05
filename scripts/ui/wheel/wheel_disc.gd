class_name WheelDisc
extends ColorRect
## The wheel's disc layer (ART-2 2A; ART_BIBLE v2 6.2): one quad under the WheelView's own drawing
## (`show_behind_parent`) running `shaders/wheel/wheel_disc.gdshader`, which draws every radial
## layer: slice CRT screens with tier, state overlay and landing flash, the D4 bezel and rail tint,
## the boss threat ring, the inner ring and the hub CRT disc, the lifted active slice. The view
## calls `sync()` with what it shows; this node never reads game state on its own.

const SHADER := preload("res://shaders/wheel/wheel_disc.gdshader")
## Master units from the centre to the quad's edge (the threat ring ends at 444, ART_BIBLE 3.2).
const EXT := 470.0
## Master units of the slice rim (the recipes' R_OUT): the view's radius maps to it.
const R_OUT := 360.0
const MAX_SLICES := 8

var mat: ShaderMaterial = null


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	show_behind_parent = true
	color = Palette.AUTO
	mat = ShaderMaterial.new()
	mat.shader = SHADER
	material = mat


## Places the quad on `center` (local to the parent) for a slice rim of `radius` px.
func place(center: Vector2, radius: float) -> void:
	var k := radius / R_OUT
	var half := EXT * k
	position = center - Vector2(half, half)
	size = Vector2(half, half) * 2.0
	mat.set_shader_parameter(&"ext", EXT)
	mat.set_shader_parameter(&"px", 1.0 / maxf(k, 0.001))


## Sets the kit's textures and tables.
func set_kit(kit: WheelKit) -> void:
	var meta := WheelKit.meta()
	mat.set_shader_parameter(&"screens", kit.screens)
	mat.set_shader_parameter(&"scenes", kit.scenes)
	mat.set_shader_parameter(&"has_scene", kit.scenes != null)
	var rows := kit.scene_rows()
	mat.set_shader_parameter(&"scene_yc", rows.x)
	mat.set_shader_parameter(&"scene_cut", rows.y)
	mat.set_shader_parameter(&"frames", int(meta.get("frames", 12)))
	mat.set_shader_parameter(&"rows", (meta.get("kinds", []) as Array).size() if meta.has("kinds") else 10)
	var tex: Array = meta.get("tex", [374, 215])
	mat.set_shader_parameter(&"tex_size", Vector2(float(tex[0]), float(tex[1])))
	mat.set_shader_parameter(&"r_out_s", float(meta.get("r_out_s", 349.9)))
	mat.set_shader_parameter(&"theme", kit.theme)
	mat.set_shader_parameter(&"tier", kit.tier)
	mat.set_shader_parameter(&"accent", kit.accent)
	mat.set_shader_parameter(&"tier_prim", kit.tier_primary)
	mat.set_shader_parameter(&"tier_sec", kit.tier_secondary)
	mat.set_shader_parameter(&"boss", kit.is_boss)
	mat.set_shader_parameter(&"elite", kit.is_elite)
	var bug := WheelGlyphs.texture(WheelGlyphs.status_id(RC.Status.PARASITE))
	mat.set_shader_parameter(&"bug_tex", bug)
	mat.set_shader_parameter(&"has_bug", bug != null)


## Sets one uniform (the view's per-frame values: rotation, flashes, time).
func put(param: StringName, value: Variant) -> void:
	mat.set_shader_parameter(param, value)


## Starts or stops the screens' loop (`wheel_screen_loop`, T0 ambient): the CRT flipbooks and the
## state overlays run on its clock; off (reduce effects, headless, the entry switched off) they hold
## their first frame, the end state.
func run_screens() -> void:
	var on := visible and Motion.live(&"wheel_screen_loop")
	if not on:
		_clock = 0.0
		put(&"frame_pos", 0.0)
		put(&"t_s", 0.0)
	set_process(on)


var _clock: float = 0.0


## Seconds the screens' loop has run (0 when it holds): the view's own churning bits follow it.
func clock() -> float:
	return _clock


func _ready() -> void:
	run_screens()


func _process(delta: float) -> void:
	if not Motion.live(&"wheel_screen_loop"):
		run_screens()
		return
	_clock += delta
	var period := maxf(0.001, Motion.seconds(&"wheel_screen_loop"))
	var frames := float(WheelKit.meta().get("frames", 12))
	put(&"frame_pos", fposmod(_clock / period, 1.0) * frames)
	put(&"t_s", fposmod(_clock, period * Motion.amplitude(&"wheel_screen_loop")))
