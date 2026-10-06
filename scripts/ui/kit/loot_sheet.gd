class_name LootSheet
extends PanelContainer
## ART-9 4A (ART_BIBLE v2 §4.11 Reward LOCKED A; round 31 `reward_screen`, `reward_reveal`,
## round 32 `reward_screen_v2`): the loot as a sheet of stickers on their liner. A dark header
## names the sheet ("LOOT SHEET // FIGHT WON // PICK 1 OF 3"), the white liner carries a faint
## repeated print and a kiss-cut slot under each sticker (the taken slot stays as a shiny empty
## outline), the foot says what happens ("x1 CARD TO DECK // UNPICKED STICKERS FALL OFF") with a
## barcode. A pick peels its sticker off the sheet (`loot_peel`: its corner curls up) as it flies
## to the deck. Put the stickers in `row`. View only.

## Header and foot heights, the liner's margin and the slot's corner radius (px at scale 1).
const HEAD_H := 34.0
const FOOT_H := 30.0
const PAD := 22.0
const SLOT_R := 10.0
## The foot's lettering (px at scale 1).
const PRINT_PX := 12
const HEAD_PX := 16
## The barcode's bars (px).
const BARCODE := Vector2(150, 18)

var head_text: String = ""
var head_tag: String = ""
var foot_text: String = ""
var text_scale: float = 1.0
var row: HBoxContainer
## Each sticker's slot (local rects), kept when a sticker leaves (its empty outline stays).
var _slots: Array[Rect2] = []
## The peel playing: the slot it lifts from, the sticker's colour and its progress (0..1).
var _peel_rect: Rect2 = Rect2()
var _peel_col: Color = Palette.TEXT_HI
var peel_t: float = 0.0:
	set(v):
		peel_t = v
		queue_redraw()


func _init(p_head: String = "", p_tag: String = "", p_foot: String = "", ts: float = 1.0) -> void:
	name = "LootSheet"
	head_text = p_head
	head_tag = p_tag
	foot_text = p_foot
	text_scale = ts
	add_theme_stylebox_override(&"panel", _margins(ts))
	row = HBoxContainer.new()
	row.name = "Stickers"
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	add_child(row)
	row.sort_children.connect(_note_slots)
	MotionSkip.register_passive(self)  # the peel ends with any press that ends a motion


func _margins(ts: float) -> StyleBoxEmpty:
	var sb := StyleBoxEmpty.new()
	sb.content_margin_left = PAD * ts
	sb.content_margin_right = PAD * ts
	sb.content_margin_top = (HEAD_H + PAD * 0.6) * ts
	sb.content_margin_bottom = (FOOT_H + PAD * 0.6) * ts
	return sb


func _note_slots() -> void:
	_slots.clear()
	for c in row.get_children():
		var cc := c as Control
		if cc != null:
			_slots.append(Rect2(cc.position + row.position, cc.size))
	queue_redraw()


## MotionSkip: the peel is playing.
func motion_running() -> bool:
	return _peel_tween != null and _peel_tween.is_valid() and _peel_tween.is_running()


## MotionSkip: the peel ends (the sticker is off the sheet).
func complete_motion() -> void:
	if _peel_tween != null and _peel_tween.is_valid():
		_peel_tween.kill()
	_peel_tween = null
	peel_t = 0.0


var _peel_tween: Tween = null


## Peels the sticker in `slot` (local rect) off the sheet, in `col` (`loot_peel`).
func peel(slot: Rect2, col: Color) -> void:
	_peel_rect = slot
	_peel_col = col
	if not Motion.live(&"loot_peel"):
		peel_t = 0.0
		return
	var e := Motion.entry(&"loot_peel")
	complete_motion()
	_peel_tween = create_tween()
	_peel_tween.tween_property(self, ^"peel_t", 1.0, Motion.seconds(&"loot_peel")).from(0.0).set_ease(e.ease).set_trans(e.trans)
	_peel_tween.tween_property(self, ^"peel_t", 0.0, 0.0)


func _draw() -> void:
	var s := text_scale
	var r := Rect2(Vector2.ZERO, size)
	draw_rect(Rect2(r.position + Vector2(6, 9), r.size), Palette.SHADOW)
	var liner := Rect2(r.position + Vector2(0, HEAD_H * s), Vector2(r.size.x, r.size.y - HEAD_H * s))
	# the concept's liner (reward.liner: silicone paper, its faint repeat print), cut to the sheet
	var lt := MainframeArt.tex("liner")
	if lt != null:
		var src := Vector2(minf(liner.size.x / MainframeArt.SCALE, lt.get_size().x), minf(liner.size.y / MainframeArt.SCALE, lt.get_size().y))
		draw_texture_rect_region(lt, liner, Rect2(Vector2.ZERO, src))
	else:
		draw_rect(liner, Palette.LINER)
	# the kiss-cut slots (reward.kiss_cut; a shiny empty outline where a sticker was taken)
	var slot := MainframeArt.tex("slot_empty")
	for sl in _slots:
		var g := sl.grow(5.0 * s)
		if slot != null:
			draw_texture_rect(slot, g, false)
		else:
			draw_rect(g, Color(Palette.TEXT_LO, 0.55), false, 1.5)
	# the head bar and the foot (their words are the game's: drawn live)
	var mono := Palette.mono()
	var ps := roundi(PRINT_PX * s)
	draw_rect(Rect2(r.position, Vector2(r.size.x, HEAD_H * s)), Palette.LABEL_TAPE)
	var hs := roundi(HEAD_PX * s)
	draw_string(mono, Vector2(PAD * s, (HEAD_H * s + mono.get_ascent(hs) - mono.get_descent(hs)) * 0.5), head_text, HORIZONTAL_ALIGNMENT_LEFT, r.size.x * 0.7, hs, Palette.TEXT_HI)
	draw_string(mono, Vector2(r.size.x * 0.7, (HEAD_H * s + mono.get_ascent(hs) - mono.get_descent(hs)) * 0.5), head_tag, HORIZONTAL_ALIGNMENT_RIGHT, r.size.x * 0.3 - PAD * s, hs, Palette.CRT_AMBER)
	var fy := r.end.y - FOOT_H * s * 0.4
	draw_string(mono, Vector2(PAD * s, fy), foot_text, HORIZONTAL_ALIGNMENT_LEFT, r.size.x - BARCODE.x * s - PAD * 3.0 * s, ps, Palette.TEXT_LO)
	var bx := r.end.x - PAD * s - BARCODE.x * s
	for i in int(BARCODE.x * s / 2.0):
		if absi(hash([i, 3])) % 3 != 0:
			draw_rect(Rect2(bx + i * 2.0, fy - BARCODE.y * s, 1.0 + float(absi(hash([i, 5])) % 2), BARCODE.y * s), Palette.INK)
	# the peel: the sticker's corner curling up off the slot
	if peel_t > 0.0 and _peel_rect.size != Vector2.ZERO:
		var c := _peel_rect.end
		var curl := minf(_peel_rect.size.x, _peel_rect.size.y) * Motion.amplitude(&"loot_peel") * peel_t
		var back := PackedVector2Array([c - Vector2(curl, 0), c, c - Vector2(0, curl)])
		draw_colored_polygon(back, Palette.LINER)
		var flap := PackedVector2Array([c - Vector2(curl, 0), c - Vector2(curl, curl) * 1.05, c - Vector2(0, curl)])
		draw_colored_polygon(flap, Palette.TEXT_HI)
		draw_polyline(flap + PackedVector2Array([flap[0]]), Color(_peel_col, 0.8), 1.5, true)
