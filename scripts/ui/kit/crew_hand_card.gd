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
## B4 (round 44): the runner's tag over its polaroid (a translation key) and its gap (px at
## 1.0); the room the hand keeps over the cards for it (px at 1.0).
const RUNNER := "RUNNER" # TR
const TAG_GAP := 3.0
const TAG_ROOM := 16.0
## B4: a greyed polaroid's paper darkened and its ink lightened by these shares.
const GREY_PAPER := 0.35
const GREY_INK := 0.35
## B4 (round 44: the polaroids lie a little askew): the rest tilts (degrees) by the card's place
## in the hand, repeating (a fixed table, never an RNG).
const TILTS: Array[float] = [-2.0, 1.2, -0.8, 1.6, -1.4]
## B4: the flatlined print through greyscale (ART-9's grey_dim: full grey, a little darker).
const GREY_SHADER := preload("res://shaders/grey_dim.gdshader")
const DEAD_DIM := 0.25

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
		if _photo != null:
			_photo.queue_redraw()
			_over.queue_redraw()
## B4: the card's tilt at rest (degrees; `TILTS` by its place in the hand, `rest_tilt_for`).
var rest_tilt: float = 0.0:
	set(v):
		rest_tilt = v
		pivot_offset = size * 0.5
		rotation_degrees = v
var _hot: bool = false
## B4: the print (drawn through greyscale when flatlined) and the stamp over it.
var _photo: Control = null
var _over: Control = null


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
	_photo = Control.new()
	_photo.name = "Photo"
	_photo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_photo.draw.connect(_draw_photo)
	add_child(_photo, false, Node.INTERNAL_MODE_FRONT)
	_over = Control.new()
	_over.name = "Over"
	_over.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_over.draw.connect(_draw_over)
	add_child(_over, false, Node.INTERNAL_MODE_FRONT)
	resized.connect(_fit_children)


## B4: puts the tilt back after the hand's layout (rest, or the hover tilt while hot; a running
## tilt motion keeps its own).
func _retilt() -> void:
	if motion_running():
		return
	pivot_offset = size * 0.5
	rotation_degrees = rest_tilt + (Motion.amplitude(&"polaroid_tilt") if _hot and not disabled else 0.0)


## B4: the rest tilt of the card at place `i` in the hand.
static func rest_tilt_for(i: int) -> float:
	return TILTS[posmod(i, TILTS.size())]


func _fit_children() -> void:
	pivot_offset = size * 0.5
	for k in [_photo, _over]:
		(k as Control).position = Vector2.ZERO
		(k as Control).size = size
		(k as Control).queue_redraw()


func _notification(what: int) -> void:
	if what == NOTIFICATION_PARENTED:
		# A container lays its children out level (Container.fit_child_in_rect zeroes rotation):
		# the rest tilt goes back on after each sort.
		var box := get_parent() as Container
		if box != null and not box.sort_children.is_connected(_retilt):
			box.sort_children.connect(_retilt)
	if what == NOTIFICATION_DRAW and _photo != null:
		# The greyscale goes on with death (and off for a living card), drawn the same frame.
		var want := dead
		if want != (_photo.material != null):
			if want:
				var m := ShaderMaterial.new()
				m.shader = GREY_SHADER
				m.set_shader_parameter(&"grey", 1.0)
				m.set_shader_parameter(&"dim", DEAD_DIM)
				_photo.material = m
			else:
				_photo.material = null
		_photo.queue_redraw()
		_over.queue_redraw()


## B4: the print on its dark photo ground (greyed when the card is ineligible).
func _draw_photo() -> void:
	var pic := pic_rect()
	var grey := refusal != "" and not dead
	_photo.draw_rect(pic, Palette.NIGHT_SKY)
	var tex := PortraitBust.print_texture(class_id, PortraitBust.variant_for(class_id, operative_id if not hire else &"")) if PortraitBust.has_class(class_id) else null
	if tex != null:
		var at := tex as AtlasTexture
		var region := PortraitBust.square_region(at.region) if at != null else Rect2(Vector2.ZERO, tex.get_size())
		region.size.y = minf(region.size.y, region.size.x * pic.size.y / maxf(1.0, pic.size.x))
		_photo.draw_texture_rect_region(at.atlas if at != null else tex, pic, region, Palette.NO_TINT if not grey else Palette.NO_TINT.darkened(1.0 - GREY))
	else:
		PortraitArt.draw(_photo, pic, PortraitArt.operative_subject(class_id, operative_id, display_name))


## B4: the rubber stamp over the print (FLATLINED in red over the grey print, HIRE in pink).
func _draw_over() -> void:
	var o := HqLayout.object_scale(Settings.text_scale)
	var pic := pic_rect()
	if dead:
		RaidPaper.draw_stamp(_over, pic.get_center(), tr(FLATLINED), roundi(STAMP_PX * o * 0.8), Palette.END_STAMP_RED, STAMP_TILT)
	elif hire:
		RaidPaper.draw_stamp(_over, pic.get_center(), tr(HIRE), roundi(STAMP_PX * o * 1.2), Palette.CELL_PINK, STAMP_TILT)
	if has_focus():
		KitState.draw_frame(_over, Rect2(Vector2(0, -lift()), size), KitState.FOCUS, false)


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
	var to := rest_tilt + (Motion.amplitude(&"polaroid_tilt") if on else 0.0)
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


## B4 (round 44 `hq_idle.png`: "the crew polaroids use the locked portrait v2 busts"): the
## print's rect on the card (local px, lifted with the card): a polaroid's white frame round a
## dark photo, the name printed under it on the paper, the status on a clipped terminal chip.
func pic_rect() -> Rect2:
	var o := HqLayout.object_scale(Settings.text_scale)
	var r := Rect2(Vector2(0, -lift()), size)
	var inset := INSET * o
	var name_h := Palette.display().get_height(roundi(NAME_PX * o))
	var chip_top := r.end.y - inset - CHIP_H * o
	var pic_h := maxf(1.0, chip_top - inset * 0.5 - name_h - (r.position.y + inset))
	return Rect2(r.position + Vector2(inset, inset), Vector2(r.size.x - inset * 2.0, pic_h))


func _draw() -> void:
	var o := HqLayout.object_scale(Settings.text_scale)
	var r := Rect2(Vector2(0, -lift()), size)
	var accent := Palette.class_accent(class_id)
	var grey := refusal != "" or dead
	draw_rect(Rect2(r.position + Vector2(4, 5) * o, r.size), Palette.SHADOW)
	if picked:
		draw_rect(r.grow(KEYLINE * o), PaletteSkins.chrome(Palette.NET_CYAN))
		# B4 (round 44): the runner's polaroid carries a cyan RUNNER tag over it.
		var mono_t := Palette.mono()
		var tpx := roundi(CHIP_PX * o)
		draw_string(mono_t, Vector2(r.position.x + INSET * o, r.position.y - KEYLINE * o - mono_t.get_descent(tpx) - TAG_GAP * o), tr(RUNNER), HORIZONTAL_ALIGNMENT_LEFT, -1, tpx,
			PaletteSkins.chrome(Palette.NET_CYAN))
	elif _hot and not disabled:
		draw_rect(r.grow(KEYLINE * o * 0.6), Color(Palette.CELL_ACID, 0.55))
	# The polaroid: paper all round (a HIRE card keeps the pink edge of the market's stock).
	draw_rect(r, Palette.PAPER if not grey else Palette.PAPER.darkened(GREY_PAPER))
	if hire:
		draw_rect(Rect2(r.position, Vector2(r.size.x, BAND * o)), Palette.CELL_PINK)
	var inset := INSET * o
	var chip_top := r.end.y - inset - CHIP_H * o
	var pic := pic_rect()
	# The photo itself is the Photo child (a flatlined one drawn through greyscale), its stamp
	# the Over child; the frame's words are drawn here.
	# Name and rank, printed on the paper.
	var disp := Palette.display()
	var mono := Palette.mono()
	var npx := roundi(NAME_PX * o)
	var rpx := roundi(RANK_PX * o)
	var name_y := pic.end.y + inset * 0.25 + disp.get_ascent(npx)
	var rank_text := "R%d" % rank
	var rw := mono.get_string_size(rank_text, HORIZONTAL_ALIGNMENT_LEFT, -1, rpx).x
	var name_px := name_font_size()
	draw_string(disp, Vector2(r.position.x + inset, name_y), display_name.to_upper(), HORIZONTAL_ALIGNMENT_LEFT, -1, name_px, Palette.INK if not grey else Palette.INK.lightened(GREY_INK))
	draw_string(mono, Vector2(r.end.x - inset - rw, name_y), rank_text, HORIZONTAL_ALIGNMENT_LEFT, -1, rpx, accent if not grey else Palette.INK.lightened(GREY_INK))
	# The status on a clipped terminal chip at the foot (it changes, so it is not printed).
	var cpx := roundi(CHIP_PX * o)
	var chip := Rect2(r.position.x + inset, chip_top, r.size.x - inset * 2.0, CHIP_H * o)
	var words := refusal if refusal != "" else status
	var col := Palette.HARM if refusal != "" else status_color
	draw_rect(chip, Palette.NIGHT_SKY)
	draw_rect(chip, col, false, 1.0)
	var fs := cpx
	while fs > 6 and mono.get_string_size(words, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > chip.size.x - 4.0:
		fs -= 1
	var tw := mono.get_string_size(words, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	draw_string(mono, Vector2(chip.get_center().x - tw * 0.5, chip.get_center().y + mono.get_ascent(fs) * 0.5 - mono.get_descent(fs) * 0.3), words, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)


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
