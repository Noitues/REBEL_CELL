class_name NodeBackdrop
extends TextureRect
## ART-7 3B (ART_BIBLE v2 §4.6 "Node backdrops", round 36 `node_backdrop`): the dressed room a
## netrun node is entered into, behind that node's screen (its event, its shop, its loot): a
## still baked from round 36's tower rooms (Blender, the Cv2 + E finish) per node kind and
## corporation, in `assets/backdrops/netrun/<corp>_<kind>.jpg`. Kinds: fight, elite, event,
## shop, rack (CityMapOverlay route kinds). A missing still shows nothing (the city stays).
## The fight's own arena backdrop is the combat screen's (Group 2). View only.

const DIR := "res://assets/backdrops/netrun/"
## The darkening laid over the still so the page on it reads (alpha).
const DIM := 0.35

var kind: String = ""
var corp: StringName = &""


func _init() -> void:
	name = "NodeBackdrop"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	visible = false


## The still's path for route kind `p_kind` of corporation `p_corp`.
static func path_for(p_kind: String, p_corp: StringName) -> String:
	return DIR + "%s_%s.jpg" % [p_corp, p_kind]


## True when a still exists for that kind and corporation.
static func has_still(p_kind: String, p_corp: StringName) -> bool:
	return ResourceLoader.exists(path_for(p_kind, p_corp))


## Shows the room of kind `p_kind` for corporation `p_corp` ("" hides it).
func show_room(p_kind: String, p_corp: StringName) -> void:
	if p_kind == "" or not has_still(p_kind, p_corp):
		visible = false
		kind = ""
		return
	if p_kind != kind or p_corp != corp:
		texture = load(path_for(p_kind, p_corp)) as Texture2D
	kind = p_kind
	corp = p_corp
	visible = texture != null
	queue_redraw()


func _draw() -> void:
	if visible:
		draw_rect(Rect2(Vector2.ZERO, size), Color(Palette.NIGHT_SKY, DIM))
