class_name RcLookVinylPreset
extends Resource
## LOOK-TOOLBOX module 13: one vinyl sticker stock or verb colour (RcLookVinyl, rc_vinyl.gdshaderinc). Read only.

## Which shader family draws it: the kit sticker (baked art + rc_vinyl_kit) or the chrome verb sticker (marker fills +
## rc_vinyl_chrome).
enum Family { KIT, CHROME }
## The chrome fill marker: magenta (gradient), green (glitch).
enum Marker { MAGENTA, GREEN }

@export var family: Family = Family.KIT
## The fill gradient, top and bottom (the lettering / face colour).
@export var fill_top: Color = Color.WHITE
@export var fill_bottom: Color = Color.WHITE
## The face is the holo foil (sticker_fill mode 1) instead of the gradient.
@export var holo_face: bool = false
## Kit: 1 = gloss vinyl, 0 = kraft. rim: the vinyl-thickness light. gloss_k: the rest gloss strength.
@export var glossy: float = 1.0
@export var rim: float = 0.8
@export var gloss_k: float = 0.22
## Kit: the adhesive back (backing lightened by backing_lighten, 0 = as is) and the shadow colour.
@export var backing: Color = Color.WHITE
@export var backing_lighten: float = 0.0
@export var shadow_color: Color = Color.BLACK
## Chrome: the marker the fill is drawn in.
@export var marker: Marker = Marker.MAGENTA


## Problems with the numbers (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	if glossy < 0.0 or glossy > 1.0:
		errs.append("glossy must be 0..1 (%s)" % glossy)
	if rim < 0.0 or rim > 2.0:
		errs.append("rim must be 0..2 (%s)" % rim)
	if gloss_k < 0.0 or gloss_k > 1.0:
		errs.append("gloss_k must be 0..1 (%s)" % gloss_k)
	if backing_lighten < 0.0 or backing_lighten > 1.0:
		errs.append("backing_lighten must be 0..1 (%s)" % backing_lighten)
	return errs


## The adhesive back colour.
func backing_color() -> Color:
	return backing.lightened(backing_lighten)
