class_name FlightFx
extends CanvasLayer
## Flights and stamps over a screen (Animation pass ANIM-6, ANIMATION_HANDOFF 4.19-4.20,
## STYLE_GUIDE 5.3), shared by every screen and open to later slices (the raid setup's
## asset drops can fly with it): a picture of a control (its last drawn frame) or a node
## copy flies from where it was to a point (the top bar's icon, the deck), optionally after
## a stamp lands on it ("SOLD"), and shrinks into its target; a stamp can also land on a
## spot by itself (the chosen event outcome). The layer lives on the current scene over its
## pages, so a page rebuilt after the action (the Modem after a purchase) does not cut the
## flight short. The state already holds the result: this only replays it. Under reduce
## effects, headless and for a disabled entry nothing flies. `finish_all` ends every flight
## (tests, skips). View only: never game state.

const LAYER := 80
const NODE_NAME := "FlightFx"
## Share of a flight spent lifting before it travels (the lift is the entry's
## `lift` argument); the arrival fades over the last FADE_SHARE.
const LIFT_SHARE := 0.25
const FADE_SHARE := 0.3
## Every flight shrinks to this entry's amplitude as it arrives (the Modem's `buy_fly`: one
## size for anything landing in a top bar icon).
const ARRIVE_MOTION := &"buy_fly"
## A stamp's lettering relative to the stamped height, its border and its colour.
const STAMP_TEXT_SHARE := 0.34
const STAMP_BORDER := 3.0
const STAMP_TILT := -0.2
## event_choice_stamp: share spent stamping down, then holding; the rest fades.
const STAMP_DOWN_SHARE := 0.25
const STAMP_HOLD_SHARE := 0.45

## Flights and stamps on screen: [{node, tween, to}]
var flights: Array[Dictionary] = []


## The layer on `screen` (the scene that shows the flights; made on first use).
static func layer_for(screen: Node) -> FlightFx:
	if screen == null or not is_instance_valid(screen) or not screen.is_inside_tree():
		return null
	var layer := screen.get_node_or_null(NodePath(NODE_NAME)) as FlightFx
	if layer == null:
		layer = FlightFx.new()
		layer.name = NODE_NAME
		layer.layer = LAYER
		screen.add_child(layer)
	return layer


## The layer on `screen` if it has one (null otherwise; never makes one).
static func existing(screen: Node) -> FlightFx:
	if screen == null or not is_instance_valid(screen):
		return null
	return screen.get_node_or_null(NodePath(NODE_NAME)) as FlightFx


## Flights and stamps running on `screen` (0 when none).
static func active_count(screen: Node) -> int:
	var l := existing(screen)
	return l.flights.size() if l != null else 0


## Ends every flight and stamp on `screen` at once.
static func finish_all(screen: Node) -> void:
	var l := existing(screen)
	if l != null:
		l.finish()


## A picture of `c` as last drawn (its global rect of the viewport's last frame); null when
## there is no frame to read (headless).
static func snapshot(c: Control) -> Texture2D:
	if c == null or not c.is_inside_tree() or DisplayServer.get_name() == "headless":
		return null
	var vp := c.get_viewport()
	var tex := vp.get_texture() if vp != null else null
	var img := tex.get_image() if tex != null else null
	if img == null or img.is_empty():
		return null
	var r := Rect2i(c.get_global_rect()).intersection(Rect2i(Vector2i.ZERO, img.get_size()))
	if not r.has_area():
		return null
	return ImageTexture.create_from_image(img.get_region(r))


## Flies a picture of `source` to `to` (global) with motion `id` (its duration and ease): it lifts `lift` px,
## (after a `stamp` word lands on it, when given) travels, shrinks to ARRIVE_MOTION's
## amplitude and fades into its target. Returns the flying node, or null.
static func fly(screen: Node, source: Control, to: Vector2, id: StringName, stamp: String = "", lift: float = 0.0, clip: Rect2 = Rect2()) -> Control:
	if not Motion.live(id) or source == null or not source.is_inside_tree():
		return null
	return fly_node(screen, picture_of(source), source.get_global_rect(), to, id, stamp, lift, clip)


## A copy of how `source` looks now: a card draws a fresh copy of itself (ANIM-R3 A7: a
## snapshot of a card still dealing in was the empty slot, a grey blank card), anything else
## its last drawn frame, or (no frame to read: a headless capture or test) a paper card of
## its size.
static func picture_of(source: Control) -> Control:
	if source is ZineCard:
		var copy := (source as ZineCard).ghost_copy()
		copy.rotation = 0.0
		return copy
	var tex := snapshot(source)
	if tex != null:
		var pic := TextureRect.new()
		pic.texture = tex
		pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
		return pic
	var card := ColorRect.new()
	card.color = Palette.PAPER
	card.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return card


## Flies node `node` (a copy the layer now owns) from `from` (global rect) to `to`
## (global) on `screen`; see `fly`. Returns the node, or null (then freed). ANIM-R3 A7:
## with `clip` (global) the flight shows inside that rect only (loot not taken falls within
## its window, never across the page that comes in under it).
static func fly_node(screen: Node, node: Control, from: Rect2, to: Vector2, id: StringName, stamp: String = "", lift: float = 0.0, clip: Rect2 = Rect2()) -> Control:
	var l := layer_for(screen)
	if not Motion.live(id) or l == null:
		node.free()
		return null
	var holder: Control = null
	if clip.has_area():
		holder = Control.new()
		holder.name = "Clip"
		holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
		holder.clip_contents = true
		holder.position = clip.position
		holder.size = clip.size
		l.add_child(holder)
		holder.add_child(node)
		from.position -= clip.position
		to -= clip.position
	else:
		l.add_child(node)
	node.position = from.position
	node.size = from.size
	node.pivot_offset = from.size * 0.5
	var e := Motion.entry(id)
	var d := Motion.seconds(id)
	var tw := node.create_tween()
	tw.tween_interval(Motion.delay_of(id))
	if stamp != "" and Motion.live(&"sold_stamp"):
		var mark := l._stamp_mark(node, Rect2(Vector2.ZERO, from.size), stamp)
		tw.tween_method(func(v: float) -> void: mark.scale = Vector2.ONE * v, Motion.amplitude(&"sold_stamp"), 1.0, Motion.seconds(&"sold_stamp")) \
			.set_ease(Motion.entry(&"sold_stamp").ease).set_trans(Motion.entry(&"sold_stamp").trans)
	if lift != 0.0:
		tw.tween_property(node, "position:y", from.position.y - lift, d * LIFT_SHARE).set_ease(Tween.EASE_OUT)
	var end_pos := to - from.size * 0.5
	tw.tween_property(node, "position", end_pos, d).set_ease(e.ease).set_trans(e.trans)
	tw.parallel().tween_property(node, "scale", Vector2.ONE * Motion.amplitude(ARRIVE_MOTION), d).set_ease(e.ease).set_trans(e.trans)
	tw.parallel().tween_property(node, "modulate:a", 0.0, d * FADE_SHARE).set_delay(d * (1.0 - FADE_SHARE))
	var f := {"node": holder if holder != null else node, "tween": tw, "to": to + (clip.position if holder != null else Vector2.ZERO), "id": id}
	tw.tween_callback(l._end.bind(f))
	l.flights.append(f)
	return node


## A stamp landing on `rect` (global): a picture of `source` (or a `word` in a stamp box)
## stamps down from the entry's amplitude scale, holds and fades (`event_choice_stamp`).
static func stamp_on(screen: Node, source: Control, word: String, id: StringName = &"event_choice_stamp") -> Control:
	if not Motion.live(id) or source == null or not source.is_inside_tree():
		return null
	var l := layer_for(screen)
	if l == null:
		return null
	var r := source.get_global_rect()
	var holder := Control.new()
	holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_child(holder)
	holder.position = r.position
	holder.size = r.size
	holder.pivot_offset = r.size * 0.5
	var tex := snapshot(source)
	if tex != null:
		var pic := TextureRect.new()
		pic.texture = tex
		pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
		holder.add_child(pic)
	if word != "":
		l._stamp_mark(holder, Rect2(Vector2.ZERO, r.size), word)
	var e := Motion.entry(id)
	var d := Motion.seconds(id)
	holder.scale = Vector2.ONE * Motion.amplitude(id)
	holder.modulate.a = 0.0
	var tw := holder.create_tween()
	tw.tween_interval(Motion.delay_of(id))
	tw.tween_property(holder, "scale", Vector2.ONE, d * STAMP_DOWN_SHARE).set_ease(e.ease).set_trans(e.trans)
	tw.parallel().tween_property(holder, "modulate:a", 1.0, d * STAMP_DOWN_SHARE * Motion.amplitude(&"stamp_fade_in"))
	tw.tween_interval(d * STAMP_HOLD_SHARE)
	tw.tween_property(holder, "modulate:a", 0.0, d * (1.0 - STAMP_DOWN_SHARE - STAMP_HOLD_SHARE))
	var f := {"node": holder, "tween": tw, "to": r.get_center(), "id": id}
	tw.tween_callback(l._end.bind(f))
	l.flights.append(f)
	return holder


## A rubber-stamp box with `word` on `onto` (pink ink, tilted), as big as `box` allows.
func _stamp_mark(onto: Control, box: Rect2, word: String) -> Control:
	return stamp_mark(onto, box, word)


## The same stamp box as a flight's (ANIM-4b: a drag purchase's landing copy carries SOLD).
static func stamp_mark(onto: Control, box: Rect2, word: String) -> Control:
	var mark := Control.new()
	mark.name = "Stamp"
	mark.mouse_filter = Control.MOUSE_FILTER_IGNORE
	mark.size = box.size
	mark.pivot_offset = box.size * 0.5
	var fs := maxi(10, roundi(minf(box.size.y, box.size.x * 0.6) * STAMP_TEXT_SHARE))
	mark.draw.connect(func() -> void:
		var f := Palette.display()
		var w := f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + fs * 0.6
		var h := fs * 1.3
		mark.draw_set_transform(box.size * 0.5, STAMP_TILT, Vector2.ONE)
		mark.draw_rect(Rect2(-w * 0.5, -h * 0.5, w, h), Color(Palette.PAPER, 0.85))
		mark.draw_rect(Rect2(-w * 0.5, -h * 0.5, w, h), Palette.CELL_PINK, false, STAMP_BORDER)
		mark.draw_string(f, Vector2(-w * 0.5, fs * 0.4), word, HORIZONTAL_ALIGNMENT_CENTER, w, fs, Palette.CELL_PINK))
	onto.add_child(mark)
	return mark


## Ends every flight and stamp now.
func finish() -> void:
	for f in flights.duplicate():
		_end(f)


func _end(f: Dictionary) -> void:
	var tw: Tween = f["tween"]
	if tw != null and tw.is_valid():
		tw.kill()
	var n: Node = f["node"]
	if is_instance_valid(n):
		n.queue_free()
	flights.erase(f)


func _input(event: InputEvent) -> void:
	# ANIM-R1 (MotionSkip): a press (key, click or pad button) ends the flights and stamps
	# and is consumed; it does nothing else.
	if flights.is_empty():
		return
	# ANIM-R4 C2 (MotionSkip.verdict): a press that works the screen ends them and passes on;
	# an open pause menu keeps its presses.
	# ANIM-R5 (MotionSkip.handle): the press completes every running motion, not only these.
	MotionSkip.handle(event, self)


func _init() -> void:
	MotionSkip.register(self)


## MotionSkip (ANIM-R5): a flight or stamp plays.
func motion_running() -> bool:
	return not flights.is_empty()


## MotionSkip (ANIM-R5): every flight and stamp at its end.
func complete_motion() -> void:
	finish()
