class_name StreetRouteConfigData
extends Resource
## NA-23: every tuning number of the street netrun view (room interiors, the grease-pencil links, vinyl stickers, option
## chips, the TARGET mark and edge arrow, the hover power cut, the camera tween). The shipped values live in
## `content/config/street_route.tres`. Camera timings and the occlusion ease stay in `NetrunArtConfigData` (`rig.t_step`,
## `t_zoom`, `t_hover_in`, `t_hover_out`, `occlusion.ease_s`). Read-only at runtime; PIPELINE_SPEC 9.2-9.5b.

## Where the shipped config lives.
const CONFIG_PATH := "res://content/config/street_route.tres"

static var _shipped: StreetRouteConfigData = null

## Room interiors: kind colours (rgb), the shell gains, the frame, the prop colour, the elite colour.
@export var rooms: Dictionary = {}
## Link states (9.2): per state colour, width px at 1080, dash [on, off] px (empty = solid), alpha, glow; the hand wobble,
## the clear pad round a sticker, the reveal seconds.
@export var links: Dictionary = {}
## Stickers (9.3): radius px at 1080, anchor on the room (share of its left edge / height), number chip size, minimum
## sticker size at 720p.
@export var stickers: Dictionary = {}
## The red TARGET mark and its edge arrow (9.5b): visible-share switch, hysteresis, cross-fade, margins.
@export var target: Dictionary = {}
## The hover power cut (9.4): grade levels, mask grow / blur, ease seconds.
@export var hover: Dictionary = {}
## The frame: usable-area margins (HUD, legend strip, ROUTE window), the legend strip.
@export var frame: Dictionary = {}
## The street fog and its fog-only lights (calibrated on the netrun camera for the 12.1 value band; NA-24 owns the dressing):
## the fog density multiplier at OVERVIEW and at DECISION (eased by `zoom_detail`), `front_sym`, the lights.
@export var atmosphere: Dictionary = {}
## The street's look on the city (NA-23c): `building` = `city_building` uniform overrides the rig sets on the netrun street only
## (wash, floor-band trims), `lane` = the lane lines (`gain`, `sat` of `route_lane`), `haze` = [OVERVIEW, DECISION] depth-haze
## density (`haze_k`; the near DECISION frame keeps its facades), `exposure` = [OVERVIEW, DECISION] tonemap exposure (the 12.1 value
## band solved on both framings; `atmosphere.exposure` is the fallback of a pose-less rig),
## `frame` = [OVERVIEW, DECISION] brightness factor of the room frame bars.
@export var look: Dictionary = {}

## Keys each Dictionary field must hold.
const REQUIRED: Dictionary = {
	"rooms": ["colors", "elite", "wall_gain", "floor_gain", "ceil_gain", "side_gain", "prop", "frame", "frame_bu", "frame_gain",
		"glass_pad_bu", "energy_idle", "energy_lit"],
	"links": ["walked", "option", "ahead", "past", "wobble_px", "clear_pad_px", "ref_h"],
	"stickers": ["radius_px", "anchor", "chip_px", "min_px_720", "ref_h"],
	"target": ["switch_share", "hysteresis", "fade_s", "margin_px", "circle_pad_px"],
	"hover": ["cut_level", "cut_desat", "branch_boost", "type_glow", "grow_px", "blur_px", "mask_scale"],
	"frame": ["top_px", "bottom_px", "left_px", "right_px", "ref_h"],
	"atmosphere": ["density", "exposure", "front_sym", "glow_count", "glow_energy", "glow_range", "glow_height", "glow_side", "haze_mul"],
	"look": ["building", "lane", "haze", "exposure", "frame"],
}


## Problems of this config: a missing key, a bad range. Empty when sound.
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	for field: String in REQUIRED:
		var d: Dictionary = get(field)
		for key: String in REQUIRED[field]:
			if not d.has(key):
				errs.append("%s.%s missing" % [field, key])
	if errs.is_empty():
		if float(hover["cut_level"]) < 0.0 or float(hover["cut_level"]) > 1.0:
			errs.append("hover.cut_level must be within 0..1")
		if float(target["switch_share"]) <= 0.0 or float(target["switch_share"]) >= 1.0:
			errs.append("target.switch_share must be within 0..1")
		for kind: String in ["router", "terminal", "mainframe", "server_rack", "rest", "workshop", "cache"]:
			if not (rooms["colors"] as Dictionary).has(kind):
				errs.append("rooms.colors.%s missing" % kind)
	return errs


## The shipped config (loaded once, then cached).
static func shipped() -> StreetRouteConfigData:
	if _shipped == null:
		_shipped = load(CONFIG_PATH) as StreetRouteConfigData
	return _shipped
