class_name RcLookGrade
extends RefCounted
## LOOK-TOOLBOX module 9 (post chain): the shared grade. The shader side is rc_grade.gdshaderinc (rcl_grade); this is
## its exact GDScript mirror for tests, contrast checks and previews, plus the preset lookup and a material filler.
## Pure: no Node, no Settings.

## Rec.709 luma weights (the shader's rcl_luma).
const LUMA := Vector3(0.2126, 0.7152, 0.0722)

static var _cfg: RcLookGradeConfig


## The shipped presets (addons/rc_look/config/look_grade.tres), loaded once.
static func default_config() -> RcLookGradeConfig:
	if _cfg == null:
		_cfg = load(RcLookGradeConfig.DEFAULT_PATH) as RcLookGradeConfig
	return _cfg


## A shipped preset by name (null when unknown).
static func preset(name: StringName) -> RcLookGradePreset:
	return default_config().presets.get(name) as RcLookGradePreset


## Extended Reinhard on one linear channel (white <= 0: unchanged), as rcl_shoulder.
static func shoulder(lin: float, white: float) -> float:
	if white <= 0.0:
		return lin
	return lin * (1.0 + lin / (white * white)) / (1.0 + lin)


## The grade on an sRGB colour, as rcl_grade: linear, x exposure, shoulder, sRGB, x tint (clamped), saturation.
## Alpha passes through.
static func grade(c: Color, exposure: float, white: float, tint: Color, saturation: float) -> Color:
	var lc := c.srgb_to_linear()
	var e := Color(shoulder(maxf(lc.r * exposure, 0.0), white), shoulder(maxf(lc.g * exposure, 0.0), white),
			shoulder(maxf(lc.b * exposure, 0.0), white)).linear_to_srgb()
	var g := Vector3(clampf(e.r * tint.r, 0.0, 1.0), clampf(e.g * tint.g, 0.0, 1.0), clampf(e.b * tint.b, 0.0, 1.0))
	var grey := g.dot(LUMA)
	var o := Vector3(grey, grey, grey).lerp(g, saturation)
	return Color(o.x, o.y, o.z, c.a)


## `grade` with a preset's numbers.
static func grade_preset(c: Color, p: RcLookGradePreset) -> Color:
	return grade(c, p.exposure, p.white, p.tint, p.saturation)


## Writes a preset into a material's `<prefix>exposure`, `<prefix>white`, `<prefix>tint`, `<prefix>saturation`.
static func apply(mat: ShaderMaterial, p: RcLookGradePreset, prefix: String = "grade_") -> void:
	mat.set_shader_parameter(prefix + "exposure", p.exposure)
	mat.set_shader_parameter(prefix + "white", p.white)
	mat.set_shader_parameter(prefix + "tint", Vector3(p.tint.r, p.tint.g, p.tint.b))
	mat.set_shader_parameter(prefix + "saturation", p.saturation)
