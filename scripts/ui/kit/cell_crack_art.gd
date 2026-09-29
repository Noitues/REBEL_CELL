class_name CellCrackArt
extends Control
## Art pass W8d (ART_BIBLE §11 Campaign end LOST, critique 63): the Cell's own hexagon (the
## ring with the upward chevron, CELL_PINK), cracking when the campaign is lost. Baked art
## (assets/art/campaign_end/): the hexagon cut along its crack into two halves, and the
## crack itself. `set_crack` reveals the crack from the top down (INK over the pink);
## `set_split` then parts the halves (each tips away from the crack and drops a little).
## Reads without colour: a split hexagon. Presentation only: the stage drives both amounts;
## `set_crack(1)` + `set_split(1)` is the end state. Display only (no focus, no clicks).

const LEFT := "res://assets/art/campaign_end/cell_hex_left.svg"
const RIGHT := "res://assets/art/campaign_end/cell_hex_right.svg"
const CRACK := "res://assets/art/campaign_end/cell_hex_crack.svg"
## The art's size at text scale 1.0 (px; the SVGs' 240:260) and the most it grows.
const BASE_SIZE := Vector2(216, 234)
const GROW_MAX := 1.3
## The halves' parting at the end: the gap each side opens (px at 1.0), their tilt away from
## the crack (degrees) and their drop (px at 1.0).
const SPLIT_PX := 9.0
const SPLIT_DEG := 4.0
const SPLIT_DROP := 6.0

## The amounts shown (0..1).
var crack: float = 0.0
var split: float = 0.0
var _left: Texture2D = null
var _right: Texture2D = null
var _crack: Texture2D = null


func _init() -> void:
	name = "CellCrackArt"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	custom_minimum_size = art_size()
	resized.connect(_load)


## The art's size at the player's text size (px).
static func art_size() -> Vector2:
	return (BASE_SIZE * minf(Settings.text_scale, GROW_MAX)).round()


func _ready() -> void:
	_load()


func _load() -> void:
	var h := art_rect().size.y
	_left = SvgArt.texture(LEFT, h)
	_right = SvgArt.texture(RIGHT, h)
	_crack = SvgArt.texture(CRACK, h)
	queue_redraw()


## The hexagon's rect inside the control (its own aspect, centred, room left for the split).
func art_rect() -> Rect2:
	var k := minf(Settings.text_scale, GROW_MAX)
	var room := size - Vector2(SPLIT_PX * 2.0, SPLIT_DROP) * k
	var nat := SvgArt.natural_size(LEFT)
	var s := minf(room.x / nat.x, room.y / nat.y) if nat.x > 0.0 and nat.y > 0.0 else 1.0
	var sz := nat * s
	return Rect2(Vector2((size.x - sz.x) * 0.5, 0.0), sz)


## Shows the crack `t` of the way down (0 whole, 1 cracked through).
func set_crack(t: float) -> void:
	crack = clampf(t, 0.0, 1.0)
	queue_redraw()


## Parts the halves `t` of the way (0 together, 1 apart).
func set_split(t: float) -> void:
	split = clampf(t, 0.0, 1.0)
	queue_redraw()


## True when the hexagon shows cracked and parted (tests).
func broken() -> bool:
	return crack >= 1.0 and split >= 1.0


func _draw() -> void:
	if _left == null or _right == null:
		return
	var k := minf(Settings.text_scale, GROW_MAX)
	var r := art_rect()
	var ink := Palette.CELL_PINK
	var gap := SPLIT_PX * k * split
	var drop := SPLIT_DROP * k * split
	var tilt := deg_to_rad(SPLIT_DEG) * split
	# Each half tips away from the crack about its outer foot.
	var left_foot := Vector2(r.position.x, r.end.y)
	draw_set_transform(left_foot + Vector2(-gap, drop), -tilt, Vector2.ONE)
	draw_texture_rect(_left, Rect2(Vector2(0, -r.size.y), r.size), false, ink)
	var right_foot := Vector2(r.end.x, r.end.y)
	draw_set_transform(right_foot + Vector2(gap, drop), tilt, Vector2.ONE)
	draw_texture_rect(_right, Rect2(Vector2(-r.size.x, -r.size.y), r.size), false, ink)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	if _crack != null and crack > 0.0:
		# The crack runs down from the top (a region of the baked texture), over the gap.
		var src := Rect2(Vector2.ZERO, Vector2(_crack.get_size().x, _crack.get_size().y * crack))
		var dst := Rect2(r.position + Vector2(0, drop * 0.5), Vector2(r.size.x, r.size.y * crack))
		draw_texture_rect_region(_crack, dst, src, PaperInk.text(Palette.INK))
