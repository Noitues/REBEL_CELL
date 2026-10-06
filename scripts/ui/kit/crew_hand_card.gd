class_name CrewHandCard
extends Button
## HQ-B (M14, HQ redesign direction B "THE HAND"; `direction_B.png`, `direction_B_market.jpg`): an
## operative as a card in the HQ's hand: the class's colour band over the corp's photo print
## of the operative (PortraitBust, the face it wears on every screen), the name in Anton,
## the rank, and a status chip (READY / ON <SITE> / FLATLINED). Picked, it lifts out of the
## hand with a lime keyline (the raid's "parked" card); greyed, it says the rule's reason
## for the selected Site in its chip and tooltip (Q12, `RANK 1 NEEDED FOR T2`). As a HIRE
## card (`hire`) it is a class's rookie with the HIRE stamp over the print and its price in
## the chip. A drawn object: it grows with the text up to HqLayout.OBJECT_SCALE_MAX (STYLE
## 5.6). Button signals; the scene decides what a press means. View only.

## The rubber stamp over a flatlined print and over a HIRE print (translation keys).
const FLATLINED := "FLATLINED" # TR
const HIRE := "HIRE" # TR
const READY := "READY" # TR
const ON_SITE := "ON %s" # TR
## Geometry (px at 1.0): the colour band, the print's inset, the name and rank lettering,
## the chip's lettering and height, the keyline when picked, the stamp's lettering and tilt.
const BAND := 6.0
const INSET := 6.0
const NAME_PX := 20
const RANK_PX := 13
const CHIP_PX := 10
const CHIP_H := 16.0
const KEYLINE := 3.0
const STAMP_PX := 22
const STAMP_TILT := -0.2
## How grey an ineligible card is (share).
const GREY := 0.65

var class_id: StringName = &""
var operative_id: StringName = &""
var display_name: String = ""
var rank: int = 0
## The status chip's words (already translated: READY, ON <SITE>, a refusal, a price).
var status: String = ""
var status_color: Color = Palette.CELL_ACID
var dead: bool = false
var hire: bool = false
## The rule's reason this operative can't run the selected Site ("" = eligible).
var refusal: String = ""
## Picked (lifted, with the lime keyline): the runner, or the recruit in focus.
var picked: bool = false:
	set(v):
		picked = v
		queue_redraw()
var _hot: bool = false


func _init(p_class: StringName = &"", p_operative: StringName = &"", p_name: String = "", p_rank: int = 0) -> void:
	class_id = p_class
	operative_id = p_operative
	display_name = p_name
	rank = p_rank
	flat = true
	focus_mode = Control.FOCUS_ALL
	auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	custom_minimum_size = card_size()
	size_flags_vertical = Control.SIZE_SHRINK_END  # it stands on the hand's foot; picked, it lifts into the room over it
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	mouse_entered.connect(_set_hot.bind(true))
	mouse_exited.connect(_set_hot.bind(false))
	focus_entered.connect(_set_hot.bind(true))
	focus_exited.connect(_set_hot.bind(false))
	MotionSkip.register_passive(self)  # ANIM-R6 D7


## A card's size at the current text scale.
static func card_size() -> Vector2:
	return (HqLayout.CARD * HqLayout.object_scale(Settings.text_scale)).ceil()


func _set_hot(on: bool) -> void:
	_hot = on
	queue_redraw()
	tilt(on and not disabled)


## HQ-B (g): `polaroid_tilt` (ANIM-6 4.13), re-pointed from the old dossier's Polaroid: a hovered
## or focused card tilts by the entry's amplitude about its middle, and back at rest.
func tilt(on: bool) -> void:
	pivot_offset = size * 0.5
	var to := Motion.amplitude(&"polaroid_tilt") if on else 0.0
	_tilt_tween = Motion.run(&"polaroid_tilt", self, ^"rotation_degrees", to)
	if _tilt_tween == null:
		rotation_degrees = to


var _tilt_tween: Tween = null


## MotionSkip (ANIM-R6 D7, a short motion: `register_passive`): the tilt still lands.
func motion_running() -> bool:
	return _tilt_tween != null and _tilt_tween.is_valid() and _tilt_tween.is_running()


## MotionSkip: the card at its tilt's rest.
func complete_motion() -> void:
	Motion.settle(self, ^"rotation_degrees")
	_tilt_tween = null


## The lift out of the hand when picked (px, upward).
func lift() -> float:
	return HqLayout.LIFT * HqLayout.object_scale(Settings.text_scale) if picked else 0.0


func _draw() -> void:
	var o := HqLayout.object_scale(Settings.text_scale)
	var r := Rect2(Vector2(0, -lift()), size)
	var accent := Palette.class_accent(class_id)
	var grey := refusal != "" or dead
	draw_rect(Rect2(r.position + Vector2(4, 5) * o, r.size), Palette.SHADOW)
	if picked:
		draw_rect(r.grow(KEYLINE * o), Palette.CELL_ACID)
	elif _hot and not disabled:
		draw_rect(r.grow(KEYLINE * o * 0.6), Color(Palette.CELL_ACID, 0.55))
	draw_rect(r, Palette.NIGHT_SKY)
	draw_rect(r, Color(Palette.PAPER, 0.85), false, 2.0 * o)
	draw_rect(Rect2(r.position, Vector2(r.size.x, BAND * o)), Palette.CELL_PINK if hire else accent)
	# The photo print, square, under the band.
	var inset := INSET * o
	# The print takes what the name line and the chip leave (its head and shoulders).
	var name_h := Palette.display().get_height(roundi(NAME_PX * o))
	var chip_top := r.end.y - inset - CHIP_H * o
	var pic_top := BAND * o + inset
	var pic_h := maxf(1.0, chip_top - inset * 0.5 - name_h - (r.position.y + pic_top))
	var pic := Rect2(r.position + Vector2(inset, pic_top), Vector2(r.size.x - inset * 2.0, pic_h))
	var tex := PortraitBust.print_texture(class_id, PortraitBust.variant_for(class_id, operative_id if not hire else &"")) if PortraitBust.has_class(class_id) else null
	draw_rect(pic, Palette.PAPER_ALT)
	if tex != null:
		var at := tex as AtlasTexture
		var region := PortraitBust.square_region(at.region) if at != null else Rect2(Vector2.ZERO, tex.get_size())
		region.size.y = minf(region.size.y, region.size.x * pic.size.y / maxf(1.0, pic.size.x))
		draw_texture_rect_region(at.atlas if at != null else tex, pic, region, Palette.NO_TINT if not grey else Palette.NO_TINT.darkened(1.0 - GREY))
	else:
		PortraitArt.draw(self, pic, PortraitArt.operative_subject(class_id, operative_id, display_name))
	if dead:
		RaidPaper.draw_stamp(self, pic.get_center(), tr(FLATLINED), roundi(STAMP_PX * o * 0.8), Palette.END_STAMP_RED, STAMP_TILT)
	elif hire:
		RaidPaper.draw_stamp(self, pic.get_center(), tr(HIRE), roundi(STAMP_PX * o * 1.2), Palette.CELL_PINK, STAMP_TILT)
	# Name and rank.
	var disp := Palette.display()
	var mono := Palette.mono()
	var npx := roundi(NAME_PX * o)
	var rpx := roundi(RANK_PX * o)
	var name_y := pic.end.y + inset * 0.25 + disp.get_ascent(npx)
	var rank_text := "R%d" % rank
	var rw := mono.get_string_size(rank_text, HORIZONTAL_ALIGNMENT_LEFT, -1, rpx).x
	var name_px := name_font_size()
	draw_string(disp, Vector2(r.position.x + inset, name_y), display_name.to_upper(), HORIZONTAL_ALIGNMENT_LEFT, -1, name_px, Palette.PAPER if not grey else Palette.TEXT_MID)
	draw_string(mono, Vector2(r.end.x - inset - rw, name_y), rank_text, HORIZONTAL_ALIGNMENT_LEFT, -1, rpx, accent if not grey else Palette.TEXT_MID)
	# The status chip at the foot.
	var cpx := roundi(CHIP_PX * o)
	var chip := Rect2(r.position.x + inset, chip_top, r.size.x - inset * 2.0, CHIP_H * o)
	var words := refusal if refusal != "" else status
	var col := Palette.HARM if refusal != "" else status_color
	draw_rect(chip, Color(col, 0.12))
	draw_rect(chip, col, false, 1.0)
	var fs := cpx
	while fs > 6 and mono.get_string_size(words, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > chip.size.x - 4.0:
		fs -= 1
	var tw := mono.get_string_size(words, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	draw_string(mono, Vector2(chip.get_center().x - tw * 0.5, chip.get_center().y + mono.get_ascent(fs) * 0.5 - mono.get_descent(fs) * 0.3), words, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
	if has_focus():
		KitState.draw_frame(self, r, KitState.FOCUS, false)


## The name's room on the card (px): the card's width less its insets and the rank.
func name_room() -> float:
	var o := HqLayout.object_scale(Settings.text_scale)
	var rw := Palette.mono().get_string_size("R%d" % rank, HORIZONTAL_ALIGNMENT_LEFT, -1, roundi(RANK_PX * o)).x
	return size.x - INSET * o * 3.0 - rw


## The name's font size: the card's name size, stepped down until the name fits its room
## (never under the chip's size).
func name_font_size() -> int:
	var disp := Palette.display()
	var px := roundi(NAME_PX * HqLayout.object_scale(Settings.text_scale))
	while px > CHIP_PX and disp.get_string_size(display_name.to_upper(), HORIZONTAL_ALIGNMENT_LEFT, -1, px).x > name_room():
		px -= 1
	return px


## The card's words for tests and screen readers: name, rank and the chip.
func shown_words() -> String:
	return "%s R%d %s" % [display_name, rank, refusal if refusal != "" else status]
