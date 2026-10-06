class_name SliceStockWheel
extends Control
## ART-9 4A (ART_BIBLE v2 §4.10, LOCKED option B; round 33 `slice_wheel_offscreen`): the
## MAINFRAME's slice stock as a 12-slice wheel mostly below the screen. It spins once on entering
## (`shop_wheel_spin`, easing out) and stops with the slices for sale at the top, where the needle
## would be: those wedges are the buyable items (full brightness, yellow rim arcs, kraft tags tied
## to their rims); the rest are greyscale, darkened and padlocked (the stock not on sale). No
## needle. The wedges for sale are ShopItems in `items` (they turn with the wheel). A press that
## ends a motion lands the spin; reduce effects and headless show it stopped. View only.

const SLICES := 12
const STEP := TAU / SLICES
## Outer and inner radius (px at scale 1) and the visible band's inner edge.
const R_OUT := 313.0
const R_IN := 92.0
## The tag room above a wedge for sale (px at scale 1).
const TAG_ROOM := 34.0
## The padlock's place on a wedge not for sale (share of the radius).
const LOCK_AT := 0.5
## Darkening of the stock not on sale (bible: greyscale, darkened 60 %), through this shader.
const DIM := 0.6
const GREY := preload("res://shaders/grey_dim.gdshader")

## The hub's position (local): the shop places the wheel so it sits below the screen.
var hub: Vector2 = Vector2.ZERO
var radius: float = R_OUT
## The wedges for sale end this far from the hub (px; the layout keeps them above the screen's
## foot, so every item is on screen whole).
var inner_visible: float = R_IN
## The wheel's turn now (radians; 0 = at rest, the stock for sale on top).
var turn: float = 0.0
## Draws the wedges for sale while the wheel turns and the padlocks (over the greyed stock).
var _top: Control
## The items for sale (ShopItem wedges, left to right) and the wedge index each sits on.
var items: Array[ShopItem] = []
var _tween: Tween = null


func _init() -> void:
	name = "SliceStockWheel"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	MotionSkip.register_passive(self)
	var m := ShaderMaterial.new()
	m.shader = GREY
	m.set_shader_parameter(&"dim", DIM)
	material = m
	_top = Control.new()
	_top.name = "Top"
	_top.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_top.set_anchors_preset(Control.PRESET_FULL_RECT)
	_top.draw.connect(_draw_top)
	# internal (front: drawn under the wedges, as the first child), so the wheel's children are its
	# wedges for sale only, in order
	add_child(_top, false, Node.INTERNAL_MODE_FRONT)


## Wedge index of the k-th item for sale (centred at the top: -1, 0, +1 ... about 0).
static func sale_wedge(k: int, n: int) -> int:
	return k - (n - 1) / 2 if n > 0 else 0


## Puts `item` on the wheel as the k-th of `n` slices for sale.
func add_item(item: ShopItem, k: int, n: int) -> void:
	item.as_wedge(Vector2.ZERO, radius, R_IN)
	item.set_meta(&"wedge", sale_wedge(k, n))
	item.set_meta(BuyButton.TAG_AT_TOP, true)
	items.append(item)
	add_child(item)
	item.ready.connect(place_items)
	place_items()


## Places each wedge for sale (its bounding box with the tag on its rim) at rest; while the wheel
## turns they hide and the wheel draws them turning.
func place_items() -> void:
	for it in items:
		if not is_instance_valid(it):
			continue
		var a := int(it.get_meta(&"wedge", 0)) * STEP
		# the wedge's lowest inner corner stays above the screen's foot
		var r_in := maxf(R_IN, inner_visible / maxf(0.2, cos(absf(a) + STEP * 0.5)))
		var tag := TAG_ROOM * it.text_scale
		var rim := hub + Vector2(sin(a), -cos(a)) * (radius + tag * 0.45)
		var box := Rect2(rim, Vector2.ZERO).grow_individual(tag * 2.4, tag * 0.6, tag * 2.4, tag * 0.6)
		for k in 9:
			var t := a - STEP * 0.5 + STEP * k / 8.0
			box = box.expand(hub + Vector2(sin(t), -cos(t)) * radius).expand(hub + Vector2(sin(t), -cos(t)) * r_in)
		it.radius_in = r_in
		it.wedge_angle = a
		it.rotation = 0.0
		it.pivot_offset = Vector2.ZERO
		it.position = box.position
		it.custom_minimum_size = box.size
		it.size = box.size
		it.hub = hub - box.position
		it.set_meta(BuyButton.TAG_SPOT, rim - box.position)
		it.set_meta(BuyButton.TAG_TURN, a)
		if it.buy_button != null:
			it.buy_button.refit()
		if it.glyph != null:
			it.with_glyph(it.glyph.glyph)
		it.modulate.a = 1.0 if is_zero_approx(turn) else 0.0
		it.queue_redraw()
	queue_redraw()
	if _top != null:
		_top.queue_redraw()


## Spins the wheel in (several turns, easing out) when its motion plays.
func spin_in() -> void:
	land()
	if not Motion.live(&"shop_wheel_spin"):
		return
	var e := Motion.entry(&"shop_wheel_spin")
	turn = -TAU * maxf(1.0, Motion.amplitude(&"shop_wheel_spin"))
	place_items()
	_tween = create_tween()
	_tween.tween_method(func(v: float) -> void:
		turn = v
		place_items(), turn, 0.0, Motion.seconds(&"shop_wheel_spin")).set_delay(Motion.delay_of(&"shop_wheel_spin")).set_ease(e.ease).set_trans(e.trans)


## The wheel at rest (the spin's end state).
func land() -> void:
	if _tween != null and _tween.is_valid():
		_tween.kill()
	_tween = null
	turn = 0.0
	place_items()


## MotionSkip: the wheel is still spinning.
func motion_running() -> bool:
	return _tween != null and _tween.is_valid() and _tween.is_running()


## MotionSkip: lands the spin at once.
func complete_motion() -> void:
	land()


func _draw() -> void:
	# the concept's stock wheel (assets.shop_wheel12), greyed and darkened by this item's shader,
	# turning with the spin; the wedges for sale cover its top three at rest
	var t := MainframeArt.tex("wheel_stock")
	if t == null:
		draw_circle(hub, radius, Palette.CHIP_EPOXY)
		return
	var k := radius / float(MainframeArt.meta().get("wedge_radius", 470))
	draw_set_transform(hub, turn, Vector2(k, k))
	draw_texture_rect(t, Rect2(-MainframeArt.anchor("wheel_stock"), t.get_size()), false)
	draw_set_transform(Vector2.ZERO)


## The padlocks on the wedges not for sale (over the greyed wheel, in their own colour).
func _draw_top() -> void:
	var sale := _sale()
	var lock := MainframeArt.tex("lock")
	if lock == null:
		return
	var sz := lock.get_size() * MainframeArt.SCALE
	for i in SLICES:
		var wi := i - SLICES / 2
		if sale.has(wi) and is_zero_approx(turn):
			continue
		var a := turn + wi * STEP
		var at := hub + Vector2(sin(a), -cos(a)) * (radius * LOCK_AT)
		if not sale.has(wi):
			_top.draw_texture_rect(lock, Rect2(at - sz * 0.5, sz), false)


## Wedge index -> the item's art id, for the wedges for sale.
func _sale() -> Dictionary:
	var sale := {}
	for it in items:
		if is_instance_valid(it):
			sale[int(it.get_meta(&"wedge", 0))] = it.art_id
	return sale


func _band(a: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for k in 9:
		var t := a - STEP * 0.5 + STEP * k / 8.0
		pts.append(hub + Vector2(sin(t), -cos(t)) * radius)
	pts.append(hub)
	return pts
