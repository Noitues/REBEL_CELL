class_name EnrageBadge
extends Badge
## W0 ARTFIX: the enrage buff's badge, with its own tooltip plate. The engine's native tooltip
## opens at the pointer and covered the boss wheel's top-left slices and its needle (the
## information that matters at turn 10); this plate stands OUTSIDE the disc: below-right of the
## badge, `PLATE_GAP` px clear of the wheel's rim ring, clamped to the view, on the standard dark
## tooltip plate. The badge's `tooltip_text` stays (the words), the native popup is suppressed.
## View only.

## Gap between the plate and the rim ring (px at text scale 1.0).
const PLATE_GAP := 12.0
## Gap between the badge and the plate's top edge (px at text scale 1.0).
const BADGE_GAP := 4.0
## Plate padding (px at text scale 1.0) and its step when it is pushed clear of the disc.
const PLATE_PAD := Vector2(8.0, 6.0)
const PUSH_STEP := 2.0

var _plate: PanelContainer = null


func _init() -> void:
	super._init()
	mouse_entered.connect(show_plate)
	mouse_exited.connect(hide_plate)


## No native popup: the plate below is the tooltip.
func _get_tooltip(_at: Vector2) -> String:
	return ""


## Where the plate of size `sz` stands (global): below-right of `badge`, at least `gap` px from the
## rim circle (`center`, `radius`), inside `bounds`. Pushed right first (away from the disc), then
## down; held inside `bounds` last.
static func plate_rect(badge: Rect2, sz: Vector2, center: Vector2, radius: float, bounds: Rect2, gap: float, gap_badge: float) -> Rect2:
	var rect := Rect2(Vector2(clampf(badge.position.x, bounds.position.x, maxf(bounds.position.x, bounds.end.x - sz.x)), badge.end.y + gap_badge), sz)
	var tries := 0
	while _clear_of_rim(rect, center, radius + gap) == false and tries < 400:
		var right := Rect2(rect.position + Vector2(PUSH_STEP, 0.0), sz)
		if right.end.x <= bounds.end.x:
			rect = right
		else:
			rect = Rect2(rect.position + Vector2(0.0, PUSH_STEP), sz)
		tries += 1
	var x := clampf(rect.position.x, bounds.position.x, maxf(bounds.position.x, bounds.end.x - sz.x))
	var y := clampf(rect.position.y, bounds.position.y, maxf(bounds.position.y, bounds.end.y - sz.y))
	return Rect2(Vector2(x, y), sz)


static func _clear_of_rim(rect: Rect2, center: Vector2, reach: float) -> bool:
	var nearest := Vector2(clampf(center.x, rect.position.x, rect.end.x), clampf(center.y, rect.position.y, rect.end.y))
	return nearest.distance_to(center) >= reach


## Opens the plate (hover; the lab and captures call it directly).
func show_plate() -> void:
	if tooltip_text == "":
		return
	hide_plate()
	var ts := Settings.text_scale
	_plate = PanelContainer.new()
	_plate.name = "EnragePlate"
	_plate.top_level = true
	_plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_plate.z_index = 100
	var sb: StyleBox = get_theme_stylebox(&"panel", &"TooltipPanel")
	if sb == null or sb is StyleBoxEmpty:
		var flat := StyleBoxFlat.new()
		flat.bg_color = Color(Palette.NIGHT_SKY, 0.96)
		flat.border_color = PaletteSkins.chrome(HudSkin.TERMINAL_EDGE)
		flat.set_border_width_all(1)
		sb = flat
	sb = sb.duplicate()
	sb.content_margin_left = PLATE_PAD.x * ts
	sb.content_margin_right = PLATE_PAD.x * ts
	sb.content_margin_top = PLATE_PAD.y * ts
	sb.content_margin_bottom = PLATE_PAD.y * ts
	_plate.add_theme_stylebox_override(&"panel", sb)
	var tip := UiTip.make(tooltip_text)
	_plate.add_child(tip)
	add_child(_plate)
	_plate.reset_size()
	var sz := _plate.get_combined_minimum_size()
	var view := get_parent() as Control
	var center := get_global_rect().get_center()
	var radius := 0.0
	if view is WheelView:
		center = (view as WheelView).global_center()
		radius = (view as WheelView).rim_radius()
	var bounds := get_viewport_rect()
	_plate.global_position = plate_rect(get_global_rect(), sz, center, radius, bounds, PLATE_GAP * ts, BADGE_GAP * ts).position


## Closes the plate.
func hide_plate() -> void:
	if _plate != null and is_instance_valid(_plate):
		_plate.queue_free()
	_plate = null
