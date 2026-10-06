class_name HeatGlitchPreview
extends Control
## ART-10 4C: the HEAT GLITCH preview in Options (ART_BIBLE v2 §4.13, §5.5; round 31
## `settings_menu.jpg` "HEAT GLITCH PREVIEW (HUNTED, 82)"): the round 18 storyboard's ON frame
## (slip + split) and OFF frame (the static corp edge tint only) side by side. The frame
## that matches the setting is outlined in cyan; under the flash limiter or reduce effects
## the ON frame reads LIMITED (tears only at NOTICED strength). It draws a still: the
## motion itself belongs to the Heat glitch layer. View only.

## One frame's size (px at 1280x720) and the gap between the two.
const FRAME := Vector2(187, 98)
## The storyboard's ON and OFF frames (280 x 147 at the 1920 board; two thirds in the game).
const ART_ON := "res://assets/ui/menus/glitch/glitch_on.png"
const ART_OFF := "res://assets/ui/menus/glitch/glitch_off.png"
const GAP := 12.0
const CAPTION_STEP := UiTheme.CAPTION


## The baked art this view draws, held while it lives (a texture loaded only inside _draw
## was freed before the frame drew it: a white box).
var _held: Dictionary = {}


func _init() -> void:
	name = "HeatGlitchPreview"
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _ready() -> void:
	Settings.changed.connect(_changed)


func _exit_tree() -> void:
	if Settings.changed.is_connected(_changed):
		Settings.changed.disconnect(_changed)


func _changed() -> void:
	update_minimum_size()
	queue_redraw()


## True when the glitch is held to its limited form (flash limiter or reduce effects).
static func limited() -> bool:
	return Settings.flash_limiter or Settings.reduce_effects


func _get_minimum_size() -> Vector2:
	var cp := Chrome.px(CAPTION_STEP)
	return Vector2(FRAME.x * 2.0 + GAP, FRAME.y + Palette.mono().get_height(cp) + 6.0)


func _draw() -> void:
	var f := Palette.mono()
	var cp := Chrome.px(CAPTION_STEP)
	for i in 2:
		var on := i == 0
		var r := Rect2(Vector2(i * (FRAME.x + GAP), 0), FRAME)
		# The concept's frames (round 18 heat_glitch_storyboard, cropped as round 31 settings.py
		# crops them; baked by tools/art/bake_menus_r33.py).
		var tex := Chrome.held(_held, ART_ON if on else ART_OFF)
		if tex != null:
			draw_texture_rect(tex, r, false)
		var chosen := Settings.heat_glitch == on
		draw_rect(r, Palette.NET_CYAN if chosen else Color(Palette.NET_CYAN, 0.3), false, 2.0 if chosen else 1.0)
		var words := (tr("LIMITED // slow layer only") if limited() else tr("ON // slip + split")) if on else tr("OFF // static edge tint")
		draw_string(f, Vector2(r.position.x, r.end.y + 4.0 + f.get_ascent(cp)), words, HORIZONTAL_ALIGNMENT_LEFT, FRAME.x, cp,
			Palette.NET_CYAN if chosen else Palette.TEXT_LO)
