class_name RcLookGradePreset
extends Resource
## LOOK-TOOLBOX module 9: one grade's numbers (RcLookGrade, rc_grade.gdshaderinc). Read only.

## Linear-light gain before the shoulder.
@export var exposure: float = 1.0
## Exposed linear light that lands on display white (0: no shoulder, a plain clip).
@export var white: float = 0.0
## Display-space multiply after the shoulder (clamped to 0..1).
@export var tint: Color = Color(1.0, 1.0, 1.0)
## Saturation around the Rec.709 luma (0 grey, 1 unchanged).
@export var saturation: float = 1.0


## Problems with the numbers (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	if exposure <= 0.0:
		errs.append("exposure must be > 0 (%s)" % exposure)
	if white < 0.0:
		errs.append("white must be >= 0 (%s)" % white)
	if saturation < 0.0:
		errs.append("saturation must be >= 0 (%s)" % saturation)
	return errs
