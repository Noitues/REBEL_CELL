class_name DragGhost
extends Control
## The drag preview of a card (Animation pass ANIM-3): Godot moves this holder with the
## cursor every frame; the card inside trails it with a lag (`drag_ghost_follow`: duration
## = the time constant, amplitude = the ghost's alpha) and tilts with the cursor's speed
## (`drag_ghost_tilt`: duration = smoothing, amplitude = most degrees). Under reduce
## effects and headless it sits on the cursor, untilted. View only.
## W4 (ART_BIBLE 6.3): a dragged card (ZineCard, card Look) is shown at CARD_SCALE so it
## never covers the target hub it is aimed at; center_global() is where the aim line
## starts (W3).

## The dragged card's scale (the ghost of a card; other items keep their size).
const CARD_SCALE := 0.6


## The item shown (a ZineCard in combat; operatives, assets and chips since ANIM-4).
var card: Control
## Where the card's centre is drawn (global), trailing the holder.
var _lagged: Vector2 = Vector2.INF
var _tilt: float = 0.0
var _last: Vector2 = Vector2.INF


func _init(p_card: Control) -> void:
	card = p_card
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	card.mouse_filter = Control.MOUSE_FILTER_IGNORE
	card.modulate.a = Motion.amplitude(&"drag_ghost_follow")
	add_child(card)
	card.position = -card.size * 0.5
	card.pivot_offset = card.size * 0.5
	if card is ZineCard and (card as ZineCard).look == ZineCard.Look.STICKER:
		card.scale = Vector2.ONE * CARD_SCALE


func _ready() -> void:
	card.pivot_offset = card.size * 0.5
	card.rotation = 0.0


func _process(delta: float) -> void:
	step(delta)


## Moves the card one frame of `delta` seconds toward the holder (tests and the lab call
## it with a fixed delta).
func step(delta: float) -> void:
	var target := global_position
	if _lagged == Vector2.INF or not Motion.live(&"drag_ghost_follow"):
		_lagged = target
		_last = target
		card.position = -card.size * 0.5
		card.rotation = 0.0
		return
	var tau := maxf(0.001, Motion.seconds(&"drag_ghost_follow"))
	_lagged = _lagged.lerp(target, 1.0 - exp(-delta / tau))
	var vx := (target.x - _last.x) / maxf(delta, 0.001)
	_last = target
	# The cursor speed (px/s) that gives the full tilt is `drag_ghost_tilt_speed`'s amplitude.
	var want := clampf(vx / maxf(1.0, Motion.amplitude(&"drag_ghost_tilt_speed")), -1.0, 1.0) * deg_to_rad(Motion.amplitude(&"drag_ghost_tilt"))
	var ttau := maxf(0.001, Motion.seconds(&"drag_ghost_tilt"))
	_tilt = lerpf(_tilt, want, 1.0 - exp(-delta / ttau))
	card.position = _lagged - target - card.size * 0.5
	card.rotation = _tilt


## The card's centre on screen now (where a cancelled drag starts its way home).
func card_center() -> Vector2:
	return center_global()


## W4 (for W3's aim line): the dragged card's centre on screen, through its lag, tilt and
## CARD_SCALE (the holder's position before it is in a tree).
func center_global() -> Vector2:
	if not is_inside_tree():
		return global_position
	return card.get_global_transform() * (card.size * 0.5)
