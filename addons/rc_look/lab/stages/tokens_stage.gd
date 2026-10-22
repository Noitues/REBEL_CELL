extends RcLookLabStage
## LOOK-TOOLBOX module 1 in the lab: every rc_ colour token drawn by a shader that reads it as a global uniform, beside
## its Palette value drawn by GDScript. Left and right halves of each chip match when the globals are current.

## The chip shader is built from the token set, so it reads every global by name (rc_look.gdshaderinc).
## Chip grid (px at 1080p): columns, chip size, gap, label height, the grid's origin.
const COLS := 8
const CHIP := Vector2(210.0, 56.0)
const GAP := Vector2(14.0, 30.0)
const ORIGIN := Vector2(60.0, 60.0)
const LABEL_SIZE := 15


func _ready() -> void:
	var tokens: RcLookTokens = load(RcLookTokens.DEFAULT_PATH)
	var v := tokens.values()
	var shader := Shader.new()
	shader.code = _chip_code(v.keys())
	var i := 0
	for n: String in v:
		var at := ORIGIN + Vector2((i % COLS) * (CHIP.x + GAP.x), (i / COLS) * (CHIP.y + GAP.y))
		var left := ColorRect.new()
		left.position = at
		left.size = Vector2(CHIP.x * 0.5, CHIP.y)
		left.color = v[n]
		add_child(left)
		var right := ColorRect.new()
		right.position = at + Vector2(CHIP.x * 0.5, 0.0)
		right.size = Vector2(CHIP.x * 0.5, CHIP.y)
		var m := ShaderMaterial.new()
		m.shader = shader
		m.set_shader_parameter(&"pick", i)
		right.material = m
		add_child(right)
		var l := Label.new()
		l.text = n.trim_prefix(RcLookTokens.PREFIX)
		l.position = at + Vector2(0.0, CHIP.y + 2.0)
		l.add_theme_font_size_override(&"font_size", LABEL_SIZE)
		add_child(l)
		i += 1


## A canvas shader that fills with global `names[pick]`.
static func _chip_code(names: Array) -> String:
	var lines := PackedStringArray(["shader_type canvas_item;", "#include \"res://addons/rc_look/shaders/rc_look.gdshaderinc\"",
		"uniform int pick = 0;", "void fragment() {", "\tvec4 c = vec4(1.0, 0.0, 1.0, 1.0);"])
	for k in names.size():
		lines.append("\tif (pick == %d) { c = %s; }" % [k, names[k]])
	lines.append("\tCOLOR = c;")
	lines.append("}")
	return "\n".join(lines)
