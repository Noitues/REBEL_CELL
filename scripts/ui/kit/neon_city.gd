class_name NeonCity
extends Control
## The neon-night backdrop (STYLE_GUIDE 1, "Neon city"): one isometric city seen from
## above. Buildings are near-black, dark blue-grey and dark grey masses inked with neon
## outlines (roof edges and verticals) in amber, purple, pink, cyan and green; a sketch
## shader wobbles the lines so they read hand-drawn. The city is split into organic
## territories: each corporation owns one (its own building mix, more ink in its colour,
## a unique landmark HQ), with the neutral Sprawl between them. The camera looks at the
## territory named by `district` (or pans the whole city, `pan`). Geometry is built once
## per size into one triangle array; a light overlay animates traffic, beacons and rain
## unless reduce-effects. Every building's roof outline is kept (`roof_of`) so map
## overlays can mark real buildings. Pure view: deterministic, never touches game state.
##
## Baked (H20): building that geometry costs seconds and drawing it costs a full GPU pass
## every frame, so outside headless the city is painted ONCE per look into a texture
## (CityBakeCache, shared by every scene) and this control just draws the part of it the
## camera shows. A cheap live layer (window lights blinking, beacons, traffic sparks,
## sign flicker) keeps it alive; `influence` (CityInfluence) tints the territory as the
## Cell or the corporation gains ground, and is part of the bake key.

## Emitted after the city geometry is rebuilt (overlays re-read roofs and positions).
signal rebuilt
## ANIM-R1 M5: a territory change landed and left its marks (InfluenceSpread.marks).
signal territory_marked(marks: Array)
## ANIM-R1 M5: the marks or their stamping changed (a map overlay over the city redraws
## them above its dimming).
signal marks_changed

const SKETCH_SHADER := preload("res://shaders/city_sketch.gdshader")
const LIVE_SHADER := preload("res://shaders/city_live.gdshader")
const LIGHTS_SHADER := preload("res://shaders/city_lights.gdshader")
## The sketch shader's look parameters (copied to the bake painter, part of the key).
const SKETCH_PARAMS: Array[String] = ["wobble", "jitter", "saturation", "grain", "wall_mode"]
## Bake scale (texture px per city px): net maps zoom in (to 1.9), backdrops don't. Both
## are multiplied by the window's stretch (a 1080p window renders the 720p canvas 1.5x).
const BAKE_SCALE_MAP := 1.5
const BAKE_SCALE_BACKDROP := 1.0
const STRETCH_STEP := 0.25
## A bake covers the camera's view grown by REGION_MARGIN (world px) and snapped to
## REGION_SNAP; any later camera whose view fits inside a bake of the same look reuses it
## (the HQ backdrop, the netrun and the combat arena share one; a zoomed raid playout
## usually sits inside the Grid's). Bakes are painted in world space, so two bakes of
## one look match where they overlap.
const REGION_MARGIN := 160.0
const REGION_SNAP := 128.0
## Heat creep is baked in steps (a Heat point never re-bakes the city on its own).
const CREEP_STEP := 0.05
## Territory influence (CityInfluence): share of lines taking the lean colour at full
## influence, and how far the ground leans.
const INFLUENCE_INK_SHARE := 0.55
const INFLUENCE_GROUND_TINT := 0.16
## Live layer over the baked image: share of lit windows that blink, their period
## (seconds, min + hash spread) and on-share; at most LIGHTS_MAX / SPARKS_MAX drawn per
## frame. Blinks are small and slow (well under the flash limiter's 3 per second).
const LIGHT_PICK := 0.03
const LIGHT_PERIOD_MIN := 2.4
const LIGHT_PERIOD_SPREAD := 5.0
const LIGHT_ON_SHARE := 0.7
const LIGHT_GLOW := 3.0
const LIGHTS_MAX := 220
## Traffic dashes (Animation pass ANIM-6, ANIMATION_HANDOFF 4.23): the geometry records a
## spark on streets at least SPARK_TRAFFIC busy (SPARK_PICK of their lots); the live layer
## shows only those on the busiest streets (`city_traffic`: amplitude = the traffic a
## street needs, duration = seconds along one lot), as short bright dashes (SPARK_LENGTH of
## a lot, a white core over the street's ink).
const SPARK_TRAFFIC := 0.3
const SPARK_PICK := 0.35
const SPARK_LENGTH := 0.18
const SPARK_CORE := 0.55
const SPARKS_MAX := 120
const TRAFFIC_MOTION := &"city_traffic"
## Beacons blink per the `beacon_blink` motion entry: lit for its amplitude (share) of its
## duration (the period, seconds). A few HQ signs flicker (`city_sign_pick`: the share, by
## hash; `hq_sign_flicker`: duration = period, delay = dip seconds, amplitude = the dip's
## alpha). Window lights and beacons blink on the GPU (city_lights shader); dashes and signs
## are the only per-frame drawing, and reduce effects stops both.
const BEACON_MOTION := &"beacon_blink"
const BEACONS_MAX := 240
const SIGN_MOTION := &"hq_sign_flicker"
const SIGN_PICK_MOTION := &"city_sign_pick"

## Tile half-width / half-height of the isometric grid (2:1).
## ANIM-R1 M15: the smallest hatch step along a face (a share of its width).
const HATCH_STEP_MIN := 0.0005
const TILE_A := 34.0
const TILE_B := 17.0
## Streets are one lot wide; blocks between them run BLOCK_MIN..BLOCK_MAX lots, so the
## grid is irregular. (STREET_EVERY is the typical spacing, for overlays.)
const STREET_EVERY := 6
const BLOCK_MIN := 3
const BLOCK_MAX := 6
const GRID_RANGE := 260
## Neon ink colours (every district uses all five, weighted to its corporation).
const INKS: Array[Color] = [Color("#FFB000"), Color("#B04DFF"), Color("#FF3DA8"), Color("#5CE1FF"), Color("#3DFF8B")]
## Building masses: black, dark grey-blue, dark grey.
const FILLS: Array[Color] = [Color("#06070B"), Color("#141B2C"), Color("#1D2027")]
const GROUND := Color("#0A0C14")
const STREET := Color("#050609")
const FACE_LIGHT := Color("#2A3350")

## District profiles: building mix weights [box, stepped, cylinder, hex, taper, needle,
## warehouse], height scale, share of lines in the corporation colour, layout seed.
const DISTRICTS := {
	&"solace": {"mix": [3, 2, 4, 1, 1, 1, 1], "height": 1.0, "corp_ink": 0.58, "seed": 11},
	&"meridian": {"mix": [3, 2, 0, 0, 0, 0, 6], "height": 0.7, "corp_ink": 0.58, "seed": 23},
	&"halcyon": {"mix": [3, 4, 1, 0, 4, 0, 1], "height": 1.0, "corp_ink": 0.58, "seed": 37},
	&"orbital": {"mix": [2, 1, 2, 1, 1, 5, 0], "height": 1.35, "corp_ink": 0.58, "seed": 41},
	&"rebel_cell": {"mix": [4, 3, 2, 1, 1, 1, 2], "height": 1.0, "corp_ink": 0.58, "seed": 53},
	&"": {"mix": [4, 3, 2, 1, 1, 1, 2], "height": 1.0, "corp_ink": 0.0, "seed": 7},
}
enum Shape { BOX, STEPPED, CYLINDER, HEX, TAPER, NEEDLE, WAREHOUSE,
	PYRAMID, OBELISK, MASTABA, PAGODA, GABLE, CLOCKTOWER, DOME, MINARET, STEP_TEMPLE }

## Culture themes (design review): building mixes over every Shape, cyberpunk-inked.
const CULTURES := {
	"egyptian": [2, 1, 0, 0, 0, 0, 1, 4, 3, 5, 0, 0, 0, 0, 0, 0],
	"chinese": [3, 2, 0, 0, 0, 1, 0, 0, 0, 0, 6, 2, 0, 0, 0, 0],
	"english": [3, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 7, 1, 0, 0, 0],
	"mayan": [2, 4, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 5],
	"arabic": [3, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 3, 0],
}

## Territory centres (grid lots) and their pull (bigger = larger territory). The
## corporations' HQs stand on their centres; &"" entries are the neutral Sprawl.
const TERRITORIES: Array[Dictionary] = [
	{"id": &"", "at": Vector2(0, 0), "pull": 1.0},
	{"id": &"solace", "at": Vector2(-34, -4), "pull": 1.15},
	{"id": &"meridian", "at": Vector2(4, -36), "pull": 1.25},
	{"id": &"halcyon", "at": Vector2(36, 2), "pull": 1.0},
	{"id": &"orbital", "at": Vector2(-6, 34), "pull": 0.9},
	{"id": &"rebel_cell", "at": Vector2(30, 32), "pull": 0.8},
	{"id": &"", "at": Vector2(-36, -40), "pull": 0.9},
	{"id": &"", "at": Vector2(40, -38), "pull": 0.8},
]
## HQ plaza size (lots); the landmarks are drawn at HQ_SCALE of their base design.
const HQ_LOTS := 10
const HQ_SCALE := 2.0
## How far territory borders wander (lots), and how wide the mixed band along them is.
const BORDER_WARP := 11.0
const BORDER_BLEND := 7.0
## Ink palettes: 0 = full neon; 1-3 paler options (lerped toward a tint).
const INK_SETS: Array[Dictionary] = [
	{"name": "NEON", "tint": Color.WHITE, "amount": 0.0},
	{"name": "PASTEL NEON", "tint": Color.WHITE, "amount": 0.3},
	{"name": "FADED PRINT", "tint": Color("#C9BFD9"), "amount": 0.38},
	{"name": "COOL HAZE", "tint": Color("#D6F2FF"), "amount": 0.32},
]
## The Cell has no tower: its territory is ordinary city, and its roads etch a raised
## fist (traced from the reference icon; polygons in 0-1 image space, y down) that reads
## from above. FIST_SIZE is the fist's size on screen (px at zoom 1); the roads are
## FIST_ROAD_HALF px half-wide and lots within FIST_CLEAR px of a road stay empty. No
## ordinary street runs inside the fist: streets end on its outline and the blocks
## inside are built up like the rest of the city.
const FIST_TERRITORY := &"rebel_cell"
const FIST_SIZE := Vector2(1000, 1070)
const FIST_ROAD_HALF := 17.0
const FIST_CLEAR := 27.0
const FIST_POLYS := [
	[Vector2(0.545, 0.458), Vector2(0.425, 0.491), Vector2(0.487, 0.515)],
	[Vector2(0.909, 0.379), Vector2(0.724, 0.579), Vector2(0.779, 0.636), Vector2(0.994, 0.461)],
	[Vector2(0.88, 0.33), Vector2(0.76, 0.245), Vector2(0.558, 0.509), Vector2(0.682, 0.552)],
	[Vector2(0.227, 0.2), Vector2(0, 0.515), Vector2(0.347, 0.888), Vector2(0.328, 0.997), Vector2(0.776, 0.997), Vector2(0.773, 0.915), Vector2(0.89, 0.779), Vector2(0.919, 0.585), Vector2(0.782, 0.691), Vector2(0.672, 0.597), Vector2(0.464, 0.552), Vector2(0.662, 0.845), Vector2(0.701, 0.873), Vector2(0.636, 0.879), Vector2(0.614, 0.948), Vector2(0.584, 0.879), Vector2(0.519, 0.885), Vector2(0.594, 0.821), Vector2(0.399, 0.539), Vector2(0.247, 0.488), Vector2(0.299, 0.445), Vector2(0.289, 0.367), Vector2(0.315, 0.367), Vector2(0.367, 0.433), Vector2(0.471, 0.43), Vector2(0.542, 0.397), Vector2(0.549, 0.327)],
	[Vector2(0.584, 0.112), Vector2(0.49, 0.258), Vector2(0.604, 0.312), Vector2(0.601, 0.367), Vector2(0.727, 0.185)],
	[Vector2(0.396, 0), Vector2(0.289, 0.167), Vector2(0.438, 0.23), Vector2(0.536, 0.082)],
]
## The fist's whole silhouette (its pieces with the gaps between them closed): no
## ordinary street runs inside it.
const FIST_HULL := [Vector2(0.396, 0.000), Vector2(0.282, 0.188), Vector2(0.263, 0.203), Vector2(0.227, 0.200), Vector2(0.000, 0.515), Vector2(0.338, 0.879), Vector2(0.344, 0.918), Vector2(0.328, 0.997), Vector2(0.776, 0.997), Vector2(0.773, 0.921), Vector2(0.890, 0.779), Vector2(0.919, 0.600), Vector2(0.903, 0.545), Vector2(0.994, 0.458), Vector2(0.886, 0.364), Vector2(0.880, 0.330), Vector2(0.727, 0.227), Vector2(0.724, 0.182), Vector2(0.584, 0.112), Vector2(0.555, 0.109), Vector2(0.532, 0.079)]
## Wall textures (design review options): 0 none, 1 panel seams, 2 pen hatching (dark
## ink), 3 grime stipple, 4 concrete grain, 5 matte stone, 6 brushed metal, 7 hatching on
## stone, 8 hatching on metal. 4-8 use the sketch shader's `wall_mode` (1 grain, 2 stone,
## 3 metal) on the dark grey fills.
## 9 painted slate (the reference's panel 6): blue-grey faces lit from above, ledges,
## recessed panels, ribs and vents, roof rims, a soft painted grain (shader mode 4);
## 10 the same in a darker slate; 11 and 12 the painted slate tinted toward each
## building's line colour (light and strong tint), so the territories keep their colour.
const TEXTURE_NAMES: Array[String] = ["NONE", "PANEL SEAMS", "PEN HATCHING", "GRIME STIPPLE", "CONCRETE GRAIN",
	"MATTE STONE", "BRUSHED METAL", "HATCHING + STONE", "HATCHING + METAL", "PAINTED SLATE", "DARK SLATE",
	"TINTED SLATE", "STRONG TINTED SLATE"]
const TEXTURE_SHADER_MODE: Array[int] = [0, 0, 0, 0, 1, 2, 3, 2, 3, 4, 4, 5, 5]
## How far the tinted slates lean toward the building's ink (11, 12).
const SLATE_TINT: Array[float] = [0.3, 0.5]
## Painted slate: the base tone of the walls (light, dark) and the cool light they catch
## at the top.
const SLATE_TONES: Array[Color] = [Color("#4A556F"), Color("#232A3A")]
const SLATE_LIGHT := Color("#B8C4DE")
## Pan margin (px beyond the screen on every side) and speed.
const PAN_MARGIN := 360.0

## Decoration seed (a view hash, not game randomness).
var city_seed: int = 7
## 0 = full brightness, 1 = black. Keeps panels readable over the city.
var dim: float = 0.25
## The territory the camera looks at (&"" = the whole city from the Sprawl).
var district: StringName = &"":
	set(v):
		if v != district:
			district = v
			refresh()
## Slowly pan around the city (main menu). Frozen under reduce-effects.
var pan: bool = false:
	set(v):
		pan = v
		_apply_pan_margin()
## Ink palette (INK_SETS index).
## Camera override: this grid point lands on `focus_anchor` (a screen fraction).
var focus_grid: Vector2 = Vector2.INF
var focus_anchor: Vector2 = Vector2(0.5, 0.5)
## Culture theme per territory (corp id -> CULTURES key); empty = the base mixes.
var cultures: Dictionary = {}
## Design review: big territory names over each HQ (the zoomed-out overview).
var territory_labels: bool = false
var territory_label_px: float = 30.0
## Wall texture (TEXTURE_NAMES index). Baseline: strong tinted slate (owner's pick).
const DEFAULT_TEXTURE := 12
var face_texture: int = DEFAULT_TEXTURE:
	set(v):
		face_texture = v
		(material as ShaderMaterial).set_shader_parameter("wall_mode", TEXTURE_SHADER_MODE[clampi(v, 0, TEXTURE_SHADER_MODE.size() - 1)])
		refresh()
var ink_set: int = 3:
	set(v):
		ink_set = v
		refresh()
## Corporation colour (follows the district) and Heat creep (0-1, GDD 9.4).
var corp_color: Color = Palette.CORP_SOLACE
var corp_creep: float = 0.0
## Diagonal rain streaks (the physical world, seen through the HQ window).
var rain: bool = false
## Net mode: lanes read as circuit traces, a touch more cyan.
var net_mode: bool = false
## Animation clock, advanced unless reduce-effects.
var anim_t: float = 0.0
## Where the corporation HQ stands, as a fraction of the screen (ground point).
var hq_anchor: Vector2 = Vector2(0.8, 0.8)

var _fx: Control
var _built_for: Vector2 = Vector2.ZERO
## The camera inputs of the last draw that placed the roofs (see `camera_settled`).
var _drawn_camera: Array = []
var _trails: Array[Dictionary] = []
var _beacons: Array[Dictionary] = []
var _signs: Array[Dictionary] = []
var _verts := PackedVector2Array()
var _cols := PackedColorArray()
var _ox: float = 0.0
var _oy: float = 0.0
var _hq_rect: Rect2i = Rect2i()
var _profile: Dictionary = {}
## Territory of the lot being drawn and its corporation colour.
var _terr: StringName = &""
var _terr_col: Color = Color.WHITE
var _terr_next: StringName = &""
var _border: float = 0.0
var _hq_rects: Dictionary = {}  # corp id -> Rect2i
var _pan_t: float = 0.0
var _inks: Array[Color] = []
## Roof outline (screen points, local) of the building on each lot: Vector2i -> Dictionary
## {"roof": PackedVector2Array, "base": Vector2, "shape": int, "height": float}.
var _roofs: Dictionary = {}
## Street rows/columns and each lot's index inside its block (built per draw).
var _street_i: Dictionary = {}
var _street_j: Dictionary = {}
var _local_i: Dictionary = {}
var _local_j: Dictionary = {}
var _fist_segs: Array[PackedVector2Array] = []
var _fist_box: Rect2 = Rect2()
var _fist_hull := PackedVector2Array()
var _fist_cache: Dictionary = {}
var _drawing_hq: bool = false

## Draw from the shared baked image when the renderer can (false = always procedural).
var use_bake: bool = true
## Territory influence (CityInfluence.of); {} = none. Set with `set_influence`.
var influence: Dictionary = {}
## Set on a bake painter: the world rect (px) it paints; empty on a live city.
var painter_region: Rect2 = Rect2()
var _painter: bool = false
## The live layer: the baked image, the screen shade and the fx overlay (own material).
var _view: Control
## Offset from the stored overlay data (roofs, beacons...) to this control's space.
var _shift: Vector2 = Vector2.ZERO
var _baked_key: String = ""
var _live_for: Array = []
var _lights: Array[Dictionary] = []
var _live_lights: Array[Dictionary] = []
var _live_trails: Array[Dictionary] = []
var _live_beacons: Array[Dictionary] = []
var _lights_layer: Control
var _beacons_layer: Control
## Size at the last real resize (px); smaller changes are the pan's float jitter.
const RESIZE_EPSILON := 0.5
var _last_size: Vector2 = Vector2.ZERO
## Influence at the lot being drawn (-1 corporation .. +1 the Cell).
var _infl: float = 0.0
## Campaign the influence follows (read only), polled every INFLUENCE_POLL seconds:
## `follow_campaign` tracks RunManager's current campaign (the scene backdrops), else
## the one given to `bind_campaign`.
const INFLUENCE_POLL := 0.5
var follow_campaign: bool = false
var _campaign: CampaignState = null
var _corp: CorporationData = null
var _poll_t: float = 0.0

## Animation pass ANIM-5 (territory colour change): a change of influence does not jump.
## The new look is baked once, as always; while it lands the old image stays up, then the
## new one shows through the old as the tint spreads from the Sites that changed owner
## (InfluenceSpread, shaders/influence_reveal.gdshader). Nothing re-bakes mid-spread: the
## spread is two textures and a mask. Headless (no bake), reduce effects and a disabled
## entry show the new look at once.
const SPREAD_MOTION := &"influence_spread"
const FADE_MOTION := &"influence_crossfade"
const REVEAL_SHADER := preload("res://shaders/influence_reveal.gdshader")
## The last influence each city family (net/physical, district, campaign) showed, so a
## change made while the player was away (a run cleared a Site) spreads when they are
## back. View memory only.
static var _seen: Dictionary = {}
## A pinned influence (the raid playout holds the pre-raid tint until its end) or null.
var influence_pin: Variant = null
## The spread running: the old image ({"texture", "region"}; {} = light front only), its
## origins (grid lots), front colour and elapsed seconds (< 0: none).
var _spread_old: Dictionary = {}
var _spread_origins := PackedVector2Array()
var _spread_color: Color = Palette.CELL_TURF
var _spread_elapsed: float = -1.0
var _old_layer: Control
var _front_layer: Control

## ANIM-R2 R1: the live baked city's placement (a world-space twin that places buildings lot
## by lot when asked, never drawing), the bake the view waits for ({} when none), whether
## the sky showed since the last image, and the sky's veil over a bake fading in.
var _placing: bool = false
## Procedural builds so far (a build replaces the roofs: see `frame_stamp`).
var _built_serial: int = 0
var _placer: NeonCity = null
var _placer_key: String = ""
## The look may have changed since the placement was checked (a refresh, a redraw).
var _placer_stale: bool = true
var _fronts: Dictionary = {}
var _covers: Dictionary = {}
var _want: Dictionary = {}
var _sky_shown: bool = false
## ANIM-R6 A14 (combat, a minimal change here): while true, a bake that would land over the
## silhouette waits (the silhouette stays); set back to false, it lands and fades in. The
## fight holds it while a SEND IT replays, so the city never switches in mid-turn.
var hold_landing: bool = false:
	set(v):
		if v == hold_landing:
			return
		hold_landing = v
		if not v and _view != null:
			_view.queue_redraw()
var _veil: Control
const NO_LOT := Vector2i(-1073741824, -1073741824)
## Frames the camera must hold still before its bake is asked for (a fit moves it every
## frame for a few frames; each move used to start a bake of its own).
const BAKE_SETTLE_FRAMES := 3
## A finished bake of this look stands in while the view's own bakes only when it covers
## at least this share of the view.
const STANDIN_COVER := 0.9
const BAKE_FADE_MOTION := &"city_bake_fade"
## Slices a painter's build is split into (run on the worker pool in parallel, joined in
## order: the same triangles as one build).
const BUILD_SLICES := 12


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	material = ShaderMaterial.new()
	material.shader = SKETCH_SHADER
	material.set_shader_parameter("wall_mode", TEXTURE_SHADER_MODE[face_texture])
	_view = Control.new()
	_view.name = "CityView"
	_view.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_view.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_view.material = ShaderMaterial.new()
	(_view.material as ShaderMaterial).shader = LIVE_SHADER
	_view.draw.connect(_draw_view)
	add_child(_view)
	# ANIM-R2 R1: the sky over a bake that just landed, fading out (`city_bake_fade`): the
	# first layer over the view's own drawing, under the lights and the rest.
	_veil = Control.new()
	_veil.name = "BakeVeil"
	_veil.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_veil.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_veil.visible = false
	_veil.draw.connect(_draw_veil)
	# ANIM-R3 B4: the silhouette under the veil, over the view's sky.
	_sil = Control.new()
	_sil.name = "CitySilhouette"
	_sil.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_sil.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_sil.visible = false
	_sil.draw.connect(_draw_sil)
	_view.add_child(_sil)
	_view.add_child(_veil)
	_old_layer = _reveal_layer("InfluenceOld", 0, _draw_old)
	_lights_layer = _blink_layer("CityLights", LIGHT_ON_SHARE, _draw_lights)
	_beacons_layer = _blink_layer("CityBeacons", Motion.amplitude(BEACON_MOTION), _draw_beacons)
	_front_layer = _reveal_layer("InfluenceFront", 1, _draw_front)
	# ANIM-R1 M5: what the last territory change left on the city (outlines and stamps).
	_marks_layer = Control.new()
	_marks_layer.name = "TerritoryMarks"
	_marks_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_marks_layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_marks_layer.draw.connect(_draw_marks)
	add_child(_marks_layer)
	# ANIM-R6 C12: a map mounted or taken off redraws the city's marks (marks_on_map).
	child_entered_tree.connect(_on_child_changed)
	child_exiting_tree.connect(_on_child_changed)
	_fx = Control.new()
	_fx.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fx.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_fx.use_parent_material = true
	_fx.draw.connect(_draw_fx)
	_view.add_child(_fx)
	resized.connect(_on_resized)


## A layer of GPU-blinking lights (city_lights shader), under the fx overlay.
func _blink_layer(layer_name: String, duty: float, painter: Callable) -> Control:
	var c := Control.new()
	c.name = layer_name
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	c.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var m := ShaderMaterial.new()
	m.shader = LIGHTS_SHADER
	m.set_shader_parameter("duty", duty)
	c.material = m
	c.draw.connect(painter)
	_view.add_child(c)
	return c


## A layer of the influence spread (ANIM-5): `mode` 0 the old image, 1 the front's glow.
func _reveal_layer(layer_name: String, mode: int, painter: Callable) -> Control:
	var c := Control.new()
	c.name = layer_name
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	c.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var m := ShaderMaterial.new()
	m.shader = REVEAL_SHADER
	m.set_shader_parameter("mode", mode)
	m.set_shader_parameter("tile", Vector2(TILE_A, TILE_B))
	c.material = m
	c.visible = false
	c.draw.connect(painter)
	_view.add_child(c)
	return c


func _notification(what: int) -> void:
	if what == NOTIFICATION_PREDELETE:
		_free_placement()
		free_slices()
	elif what == NOTIFICATION_VISIBILITY_CHANGED and not is_visible_in_tree():
		# ANIM-R6 B4 (netrun): hidden, the sky it showed is gone from the screen: a bake that
		# lands meanwhile shows at once when it comes back (the run's end after a fight that
		# was a session's first page faded in over the silhouette for 20 frames).
		_sky_shown = false


func _ready() -> void:
	Settings.changed.connect(_apply_effects)
	_apply_effects()
	sync_influence()


func _apply_effects() -> void:
	var live := not _painter and not Settings.reduce_effects
	var sm := material as ShaderMaterial
	sm.set_shader_parameter("scan_strength", 0.07 if live else 0.0)
	sm.set_shader_parameter("flicker", 0.012 if live else 0.0)
	var vm := _view.material as ShaderMaterial
	vm.set_shader_parameter("scan_strength", 0.07 if live else 0.0)
	vm.set_shader_parameter("flicker", 0.012 if live else 0.0)
	for layer in [_lights_layer, _beacons_layer]:
		((layer as Control).material as ShaderMaterial).set_shader_parameter("animate", 1.0 if live else 0.0)
	_fx.queue_redraw()


## A real resize re-frames the city; the menu pan's sub-pixel size jitter (its offsets
## move every frame) does not.
func _on_resized() -> void:
	if (size - _last_size).length() > RESIZE_EPSILON:
		_last_size = size
		refresh()


## Rebuilds the static city (after a district, colour or creep change). Baked, this only
## re-frames the cached image (or starts a bake when the look changed).
func refresh() -> void:
	_built_for = Vector2.ZERO
	_placer_stale = true
	queue_redraw()
	if _view != null:
		_view.queue_redraw()


## Follows a campaign's Grid for the territory influence (read only; null = none).
func bind_campaign(c: CampaignState, corp: CorporationData) -> void:
	_campaign = c
	_corp = corp
	set_influence(CityInfluence.of(c, corp))


## Sets the territory influence; re-frames (and re-bakes) only when it changed.
func set_influence(inf: Dictionary) -> void:
	if CityInfluence.signature(inf) == CityInfluence.signature(influence):
		return
	influence = inf
	refresh()


## True while this city draws the shared baked image (not headless, not a painter).
func is_baked() -> bool:
	return use_bake and not _painter and CityBakeCache.can_bake()


## Re-reads the followed campaign's influence (re-bakes only if it changed).
func sync_influence() -> void:
	if follow_campaign or _campaign != null:
		set_influence(_followed_influence())


## Holds the city on `inf` (a CityInfluence.of dictionary) whatever the followed campaign
## says, until `release_influence` (ANIM-5: the raid playout shows the pre-raid tint and
## lets the result spread at its end).
func pin_influence(inf: Dictionary) -> void:
	influence_pin = inf
	set_influence(inf)


## Lets the followed campaign's influence show again; a change spreads (ANIM-5).
func release_influence() -> void:
	influence_pin = null
	sync_influence()


## The campaign whose influence this city shows (null when none).
func _followed_campaign() -> CampaignState:
	if follow_campaign:
		return RunManager.campaign
	return _campaign


## The spread memory's key: world (net/physical), district and campaign.
func _family() -> String:
	var c := _followed_campaign()
	return "%s|%s|%s" % [net_mode, district, str(c.campaign_seed) + String(c.corporation_id) if c != null else "-"]


## True while a territory change is spreading (ANIM-5).
func spreading() -> bool:
	return _spread_elapsed >= 0.0


## True when the city shows its current look (its bake is on screen, or it spreads in,
## or the city draws procedurally): a territory change has landed.
func showing_current_look() -> bool:
	if not is_baked():
		return true
	return spreading() or (CityBakeCache.has(_baked_key) and String(CityBakeCache.entry(_baked_key).get("look", "")) == look_key())


## ANIM-R1 M8: true when the whole view is drawn from a finished bake of the current look
## (not a stand-in of another region, not the sky while one bakes), or the city draws
## procedurally.
func view_covered() -> bool:
	if not is_baked():
		return true
	var key := CityBakeCache.find(look_key(), view_rect())
	return key != "" and not CityBakeCache.entry(key).has("failed")


## The spread's eased progress: x = the front (0..1 of its reach), y = the cross-fade of
## the rest (0..1). (1, 1) when none runs (the end state).
func spread_progress() -> Vector2:
	if _spread_elapsed < 0.0:
		return Vector2.ONE
	var s := Motion.entry(SPREAD_MOTION)
	var f := Motion.entry(FADE_MOTION)
	var ds := maxf(Motion.seconds(SPREAD_MOTION), 0.001)
	var df := maxf(Motion.seconds(FADE_MOTION), 0.001)
	var ts := clampf(_spread_elapsed / ds, 0.0, 1.0)
	var tf := clampf((_spread_elapsed - Motion.delay_of(FADE_MOTION)) / df, 0.0, 1.0)
	return Vector2(float(Tween.interpolate_value(0.0, 1.0, ts, 1.0, s.trans, s.ease)),
		float(Tween.interpolate_value(0.0, 1.0, tf, 1.0, f.trans, f.ease)))


## Starts the spread from `prev` (the influence shown before) to the current one: the old
## image is the one on screen (or any bake of the old look over this view); without one
## only the light front plays over the new image.
func _start_spread(prev: Dictionary) -> void:
	if prev.is_empty() or influence.is_empty() or prev.get("corp") != influence.get("corp"):
		return
	var from := InfluenceSpread.origins(prev, influence)
	if from.is_empty():
		return
	if not Motion.live(SPREAD_MOTION):
		# ANIM-R2 R7: no spread plays, but its end state stays: the district's lasting tint.
		_spread_origins = from
		_spread_color = InfluenceSpread.front_color(prev, influence)
		_show_tint(Motion.amplitude(TINT_MOTION))
		return
	var old_look := look_key(prev)
	var old_key := ""
	if CityBakeCache.has(_baked_key) and CityBakeCache.entry(_baked_key).get("look", "") == old_look:
		old_key = _baked_key
	else:
		old_key = CityBakeCache.find(old_look, view_rect())
	_spread_old = {}
	if old_key != "":
		var oe := CityBakeCache.entry(old_key)
		if oe.has("texture"):
			_spread_old = {"texture": oe["texture"], "region": oe["region"]}
	_spread_origins = from
	_spread_color = InfluenceSpread.front_color(prev, influence)
	_spread_elapsed = 0.0
	for layer in [_old_layer, _front_layer]:
		var m := (layer as Control).material as ShaderMaterial
		m.set_shader_parameter("origins", from)
		m.set_shader_parameter("origin_count", from.size())
		m.set_shader_parameter("feather", Motion.amplitude(FADE_MOTION))
		m.set_shader_parameter("front_color", _spread_color)
		(layer as Control).visible = true
	_old_layer.visible = not _spread_old.is_empty()
	# ANIM-R2 R7: a stronger front, and the lasting tint washing in behind it.
	var fm := _front_layer.material as ShaderMaterial
	fm.set_shader_parameter("front_alpha", FRONT_ALPHA)
	tint_wash = 0.0
	Motion.run(TINT_MOTION, self, ^"tint_wash", Motion.amplitude(TINT_MOTION))
	_step_spread(0.0)


## ANIM-R2 R7: the lasting tint's strength over the changed district (0..`influence_tint`'s
## amplitude; it stays until the next change).
const TINT_MOTION := &"influence_tint"
## The spreading front's band strength (it was 0.5 and barely read at map scale).
const FRONT_ALPHA := 0.9
var tint_wash: float = 0.0:
	set(v):
		tint_wash = v
		if _front_layer != null:
			(_front_layer.material as ShaderMaterial).set_shader_parameter("wash", v)


## ANIM-R2 R7: the lasting tint alone (the front at full reach, its band gone) at `wash`.
func _show_tint(wash: float) -> void:
	var m := _front_layer.material as ShaderMaterial
	m.set_shader_parameter("origins", _spread_origins)
	m.set_shader_parameter("origin_count", _spread_origins.size())
	m.set_shader_parameter("feather", Motion.amplitude(FADE_MOTION))
	m.set_shader_parameter("front_color", _spread_color)
	m.set_shader_parameter("radius", Motion.amplitude(SPREAD_MOTION))
	m.set_shader_parameter("fade", 1.0)
	m.set_shader_parameter("cam", Vector2(_ox, _oy))
	tint_wash = wash
	_front_layer.visible = wash > 0.0
	_front_layer.queue_redraw()


## ANIM-R2 R7: the lasting tint's colour and strength now (a = 0 when none shows; tests).
func lasting_tint() -> Color:
	return Color(_spread_color, tint_wash) if _front_layer.visible else Color(0, 0, 0, 0)


## Advances the spread by `delta` seconds and updates the mask; ends it when both the
## front and the cross-fade are done.
func _step_spread(delta: float) -> void:
	if _spread_elapsed < 0.0:
		return
	_spread_elapsed += delta
	var p := spread_progress()
	for layer in [_old_layer, _front_layer]:
		var m := (layer as Control).material as ShaderMaterial
		m.set_shader_parameter("cam", Vector2(_ox, _oy))
		m.set_shader_parameter("radius", p.x * Motion.amplitude(SPREAD_MOTION))
		m.set_shader_parameter("fade", p.y)
	var done := Motion.seconds(SPREAD_MOTION) <= _spread_elapsed and Motion.delay_of(FADE_MOTION) + Motion.seconds(FADE_MOTION) <= _spread_elapsed
	if done or not Fx.effects_enabled():
		finish_spread()


## ANIM-R1 M5: the marks the last territory change left (InfluenceSpread.marks) and how far
## their stamps have stamped on (0..1, `influence_mark`). They stay until the next change.
var marks: Array[Dictionary] = []
var mark_t: float = 1.0:
	set(v):
		mark_t = v
		if mark_t >= 1.0:
			fading_marks = []
		if _marks_layer != null:
			_marks_layer.queue_redraw()
		marks_changed.emit()
## ANIM-R6 C12: the stamps of the change before, fading out as the new ones stamp on
## (1 - `mark_t`'s stamp alpha); gone once they have landed.
var fading_marks: Array[Dictionary] = []
var _marks_layer: Control
## A mark's outline (lots round its Site) and its stamp's lettering and lift (screen px).
## ANIM-R3 B6: the stamp sits right over its Site (it hung 70 px up a leader, under the
## labels); the district inside the outline is hatched (MARK_HATCH px apart, its lines at
## MARK_HATCH_ALPHA) over a MARK_FILL wash, so a claim reads without its colour.
const MARK_RADIUS := 2.2
const MARK_FONT := 20
const MARK_LIFT := 26.0
const MARK_PAD := 6.0
const MARK_FILL := 0.2
const MARK_HATCH := 9.0
const MARK_HATCH_ALPHA := 0.5
## ANIM-R4 H11d: what a map keeps clear for its words (its node labels and icons, this city's
## local px): a CLAIMED / SEIZED stamp takes the first spot round its Site that covers none
## of them (above, below, right, left; the least covered when all do), so it never hides the
## Site's name. Set by the map before it draws the stamps; [] draws them above the Site.
var stamp_avoid: Array[Rect2] = []
## The stamp's tilt (degrees) and its gap from what it keeps clear of (screen px).
const MARK_TILT := -6.0
const MARK_GAP := 4.0


## ANIM-R1 M5: a territory change from `prev` to `now` ends in lasting marks: an outline
## and a tint on each Site that changed hands and a CLAIMED / SEIZED stamp tied to it (it
## reads as "this block is now mine / theirs"). The stamps stamp on as the spread's front
## passes (`influence_mark`), at once when motion doesn't play. Emits territory_marked.
func mark_changes(prev: Dictionary, now: Dictionary) -> void:
	var before := marks
	marks = InfluenceSpread.marks(prev, now)
	if marks.is_empty():
		fading_marks = []
		return
	# ANIM-R6 C12: the stamps the last change left stay until the new ones land and fade out
	# as they stamp on (a claim's CLEARED vanished at once and CLAIMED came ~24 frames later
	# with nothing between): a cross-stamp. A stamp still landing lands first (its tween only).
	Motion._settle(self, ^"mark_t")
	fading_marks = before
	mark_t = 0.0
	if not Motion.run(&"influence_mark", self, ^"mark_t", 1.0):
		mark_t = 1.0
	_marks_layer.queue_redraw()
	territory_marked.emit(marks)


func _draw_marks() -> void:
	# ANIM-R6 C12: a map over the city draws the marks itself (over its dimming, stamps over its
	# labels): the city's own layer then draws none, so a stamp never shows twice (at 1.6 a
	# claim showed two CLEARED stamps: this layer's, placed before the map's labels, and the
	# map's).
	if not marks_on_map():
		draw_marks_on(_marks_layer)


## ANIM-R6 C12: true while a map overlay on this city draws its territory marks.
func marks_on_map() -> bool:
	for ch in get_children():
		if ch is CityMapOverlay and (ch as CanvasItem).visible and not ch.is_queued_for_deletion():
			return true
	return false


func _on_child_changed(_n: Node) -> void:
	if _marks_layer != null:
		_marks_layer.queue_redraw()


## Draws the marks on canvas item `ci` (in this city's local space: the city's own layer,
## or a map overlay over it, which draws them above its dimming and under its nodes).
## ANIM-R3 B6: `rings` (the outline, wash and hatch) and `stamps` (the CLAIMED / SEIZED
## stamps) can go on different layers: a map puts its stamps over its labels.
func draw_marks_on(ci: CanvasItem, rings: bool = true, stamps: bool = true) -> void:
	if marks.is_empty() or ci == null:
		return
	var _marks_layer := ci
	var k := 1.0 / maxf(0.001, scale.x)
	var fs := maxi(1, roundi(MARK_FONT * Settings.text_scale * k))
	var font := Palette.display()
	# ANIM-R6 C12: the old stamps fade out as the new ones stamp on (a site stamped anew shows
	# the old word under the new one's landing, then the new word alone).
	var landed := _mark_alpha()
	if stamps and landed < 1.0:
		for m: Dictionary in fading_marks:
			_draw_mark_stamp(ci, m, 1.0, 1.0 - landed, k, fs, font)
	for m: Dictionary in marks:
		var at: Vector2 = m["at"]
		var c := grid_to_local(at.x + 0.5, at.y + 0.5)
		var col: Color = m["color"]
		var ring := PackedVector2Array()
		for q in 33:
			var t := TAU * q / 32.0
			ring.append(c + Vector2(cos(t) * TILE_A, sin(t) * TILE_B) * MARK_RADIUS)
		if rings:
			_marks_layer.draw_colored_polygon(ring, Color(col, MARK_FILL))
			_hatch(_marks_layer, c, Vector2(TILE_A, TILE_B) * MARK_RADIUS, Color(col, MARK_HATCH_ALPHA), k)
			_marks_layer.draw_polyline(ring, Color(0, 0, 0, 0.8), 6.0 * k, true)
			_marks_layer.draw_polyline(ring, col, 3.0 * k, true)
		if not stamps:
			continue
		# The stamp, tied to its Site by a leader, stamping on from its amplitude's scale.
		var grow := lerpf(Motion.amplitude(&"influence_mark"), 1.0, mark_t) if mark_t < 1.0 else 1.0
		_draw_mark_stamp(ci, m, grow, landed, k, fs, font)


## ANIM-R6 C4: a new stamp's alpha: it fades in over `stamp_fade_in`'s share of its stamp-on
## (the inline x 2.0 was that share, 0.5), as the raid's stamps do.
func _mark_alpha() -> float:
	return clampf(mark_t / maxf(Motion.amplitude(&"stamp_fade_in"), 0.001), 0.0, 1.0)


## Mark `m`'s stamp on `ci` at scale `grow` and `alpha`, tied to its Site by a leader.
## ANIM-R4 H11d: at a spot clear of the map's labels (stamp_rect).
func _draw_mark_stamp(ci: CanvasItem, m: Dictionary, grow: float, alpha: float, k: float, fs: int, font: Font) -> void:
	var at: Vector2 = m["at"]
	var c := grid_to_local(at.x + 0.5, at.y + 0.5)
	var col: Color = m["color"]
	var word := CityMapOverlay.tr_word(String(m["word"]))
	var spot := stamp_rect(m)
	var anchor := spot.get_center()
	var edge := c + (anchor - c).normalized() * Vector2(TILE_A, TILE_B).length() * MARK_RADIUS * 0.5 if anchor != c else c
	ci.draw_line(edge, anchor, Color(col, 0.9 * alpha), 2.0 * k)
	ci.draw_set_transform(anchor, deg_to_rad(MARK_TILT), Vector2.ONE * grow)
	var box := Rect2(-spot.size * 0.5, spot.size)
	ci.draw_rect(box, Color(Palette.NIGHT_SKY, 0.9 * alpha))
	ci.draw_rect(box, Color(col, alpha), false, 3.0 * k)
	ci.draw_string(font, box.position + Vector2(MARK_PAD * k, MARK_PAD * k + font.get_ascent(fs)), word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(col, alpha))
	ci.draw_set_transform(Vector2.ZERO)


## ANIM-R4 H11d: where mark `m`'s stamp sits (this city's local px, unrotated): the first of
## above, below, right and left of its Site whose box (tilted, grown by MARK_GAP) covers none
## of `stamp_avoid`; the least covered one when every spot covers something.
func stamp_rect(m: Dictionary) -> Rect2:
	var k := 1.0 / maxf(0.001, scale.x)
	var fs := maxi(1, roundi(MARK_FONT * Settings.text_scale * k))
	var font := Palette.display()
	var word := CityMapOverlay.tr_word(String(m["word"]))
	var size := font.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs) + Vector2(MARK_PAD, MARK_PAD) * 2.0 * k
	var at: Vector2 = m["at"]
	var c := grid_to_local(at.x + 0.5, at.y + 0.5)
	var ry := TILE_B * MARK_RADIUS
	var rx := TILE_A * MARK_RADIUS * 0.5
	var lift := MARK_LIFT * k
	var spots: Array[Rect2] = [
		Rect2(Vector2(c.x - size.x * 0.5, c.y - ry - lift - size.y), size),
		Rect2(Vector2(c.x - size.x * 0.5, c.y + ry * 0.5 + lift * 0.5), size),
		Rect2(Vector2(c.x + rx + lift * 0.5, c.y - size.y * 0.5), size),
		Rect2(Vector2(c.x - rx - lift * 0.5 - size.x, c.y - size.y * 0.5), size),
	]
	var best := spots[0]
	var least := INF
	for spot in spots:
		var tilted := _tilted_bounds(spot, MARK_TILT).grow(MARK_GAP * k)
		var covered := 0.0
		for r in stamp_avoid:
			if tilted.intersects(r):
				covered += tilted.intersection(r).get_area()
		if covered <= 0.0:
			return spot
		if covered < least:
			least = covered
			best = spot
	return best


## The bounding box of `r` turned by `degrees` round its centre.
static func _tilted_bounds(r: Rect2, degrees: float) -> Rect2:
	var a := deg_to_rad(absf(degrees))
	var s := Vector2(r.size.x * cos(a) + r.size.y * sin(a), r.size.x * sin(a) + r.size.y * cos(a))
	return Rect2(r.get_center() - s * 0.5, s)


## ANIM-R3 B6: diagonal hatch lines across the ellipse of radii `r` round `c` (a claimed
## district reads without its colour).
func _hatch(ci: CanvasItem, c: Vector2, r: Vector2, col: Color, k: float) -> void:
	var step := MARK_HATCH * k
	var n := ceili(2.0 * (r.x + r.y) / maxf(step, 0.001))
	for i in range(-n, n + 1):
		# The line x - y = d (a 45 degree stroke) inside the ellipse (x/rx)^2 + (y/ry)^2 = 1.
		var d := i * step
		var a := 1.0 / (r.x * r.x) + 1.0 / (r.y * r.y)
		var b := 2.0 * d / (r.x * r.x)
		var cc := d * d / (r.x * r.x) - 1.0
		var disc := b * b - 4.0 * a * cc
		if disc <= 0.0:
			continue
		var y0 := (-b - sqrt(disc)) / (2.0 * a)
		var y1 := (-b + sqrt(disc)) / (2.0 * a)
		ci.draw_line(c + Vector2(y0 + d, y0), c + Vector2(y1 + d, y1), col, 1.5 * k)


## Jumps a running spread to its end (the new look alone).
func finish_spread() -> void:
	var was := _spread_elapsed >= 0.0
	_spread_elapsed = -1.0
	_spread_old = {}
	_old_layer.visible = false
	# ANIM-R2 R7: the district keeps its tint (the front's band goes).
	if was and not _spread_origins.is_empty():
		Motion._settle(self, ^"tint_wash")  # its tween only (the fade-in and stamps keep theirs)
		_show_tint(Motion.amplitude(TINT_MOTION))
	else:
		_front_layer.visible = false


## The old image under the camera, then the same shade the view draws (masked by the
## reveal shader).
func _draw_old() -> void:
	if _spread_old.is_empty():
		return
	var region: Rect2 = _spread_old["region"]
	_old_layer.draw_texture_rect(_spread_old["texture"], Rect2(region.position + _shift, region.size), false)
	_draw_shade(_old_layer)


## The front's glow: one rect the shader turns into the spreading band.
func _draw_front() -> void:
	_front_layer.draw_rect(Rect2(Vector2.ZERO, size), Color.WHITE)


## The influence of the followed campaign (the current one if nothing is followed).
func _followed_influence() -> Dictionary:
	if influence_pin != null:
		return influence_pin
	if follow_campaign:
		return CityInfluence.of(RunManager.campaign, RunManager.corporation)
	if _campaign != null:
		return CityInfluence.of(_campaign, _corp)
	return influence


func _process(delta: float) -> void:
	_step_silhouette()
	if not _want.is_empty() and Engine.get_process_frames() - int(_want["frame"]) >= BAKE_SETTLE_FRAMES:
		if _want["cam"] == _camera_key():
			_request_want()
	# Prebakes held for this city's own view go ahead once it is hidden (the page moved on).
	if not _deferred_prebakes.is_empty() and not is_visible_in_tree():
		_flush_prebakes()
	if follow_campaign or _campaign != null:
		_poll_t += delta
		if _poll_t >= INFLUENCE_POLL:
			_poll_t = 0.0
			sync_influence()
	if _spread_elapsed >= 0.0:
		_step_spread(delta)
	if not Fx.effects_enabled() or not is_visible_in_tree():
		return
	anim_t += delta
	if pan:
		# A slow Lissajous drift across the city (about 6 px/s at its fastest). ART-0 C (art
		# pass W7, reduce motion, ART_BIBLE §12): no camera moves, the pan holds its framing.
		if Motion.parallax_allowed():
			_pan_t += delta
		var dx := sin(_pan_t * 0.019) * PAN_MARGIN * 0.9
		var dy := sin(_pan_t * 0.013 + 1.0) * PAN_MARGIN * 0.7
		# Move, don't resize: four separate offsets made the size jitter every frame, and
		# every layer redrew (H20).
		position = Vector2(-PAN_MARGIN + dx, -PAN_MARGIN + dy)
	_fx.queue_redraw()


## Deterministic 0-1 hash of three integers (view decoration only).
func _h(a: int, b: int, c: int = 0) -> float:
	var n := (a * 73856093) ^ (b * 19349663) ^ (c * 83492791) ^ (city_seed * 2654435761)
	n = (n ^ (n >> 13)) * 1274126177
	n = n ^ (n >> 16)
	return float(n & 0xFFFF) / 65535.0


## Line colour: the corporation's ink for its share of buildings, else any of the five.
func _ink(a: int, b: int) -> Color:
	if _infl != 0.0 and _h(a, b, 15) < absf(_infl) * INFLUENCE_INK_SHARE:
		return _pale(CityInfluence.color_for(influence, _infl))
	var share: float = float(_profile.get("corp_ink", 0.0))
	if _terr == district and district != &"":
		share += corp_creep * 0.35
	if _terr != &"" and _h(a, b, 12) < share:
		return _terr_col
	if net_mode and _h(a, b, 13) < 0.25:
		return _pale(Palette.NET_CYAN)
	return _inks[int(_h(a, b, 11) * _inks.size()) % _inks.size()]


## A street's ink: like `_ink` but at full neon strength (no palette paleness).
func _street_ink(a: int, b: int) -> Color:
	if _infl != 0.0 and _h(a, b, 16) < absf(_infl) * INFLUENCE_INK_SHARE:
		return CityInfluence.color_for(influence, _infl)
	var share: float = float(_profile.get("corp_ink", 0.0))
	if _terr != &"" and _h(a, b, 12) < share:
		return Palette.corp_color(_terr)
	return INKS[int(_h(a, b, 11) * INKS.size()) % INKS.size()]


## Applies the ink palette's paleness to a colour.
func _pale(c: Color) -> Color:
	var set_def: Dictionary = INK_SETS[clampi(ink_set, 0, INK_SETS.size() - 1)]
	return c.lerp(set_def["tint"], float(set_def["amount"]))


## Smooth value noise in 0-1 (for territory borders).
func _vnoise(x: float, y: float, salt: int) -> float:
	var xi := floori(x)
	var yi := floori(y)
	var fx := x - xi
	var fy := y - yi
	var u := fx * fx * (3.0 - 2.0 * fx)
	var v := fy * fy * (3.0 - 2.0 * fy)
	var a := lerpf(_h(xi, yi, salt), _h(xi + 1, yi, salt), u)
	var b := lerpf(_h(xi, yi + 1, salt), _h(xi + 1, yi + 1, salt), u)
	return lerpf(a, b, v)


## The territory owning lot (i, j): nearest centre (weighted by pull) after warping the
## lot by two octaves of noise, so borders are organic rather than straight.
func territory_at(i: int, j: int) -> StringName:
	return _territory_pair(i, j)[0]


## [owner, runner-up, border 0-1]: border is 1 on the dividing line, 0 deep inside.
func _territory_pair(i: int, j: int) -> Array:
	var w := Vector2(_vnoise(i * 0.07, j * 0.07, 70) - 0.5, _vnoise(i * 0.07, j * 0.07, 71) - 0.5) * BORDER_WARP * 2.0
	w += Vector2(_vnoise(i * 0.2, j * 0.2, 72) - 0.5, _vnoise(i * 0.2, j * 0.2, 73) - 0.5) * BORDER_WARP * 0.6
	var p := Vector2(i, j) + w
	var best: StringName = &""
	var best_d := INF
	var second: StringName = &""
	var second_d := INF
	for t in TERRITORIES:
		var d: float = p.distance_to(t["at"]) / float(t["pull"])
		if d < best_d:
			second = best
			second_d = best_d
			best_d = d
			best = t["id"]
		elif d < second_d:
			second_d = d
			second = t["id"]
	# Within ~BORDER_BLEND lots of the dividing line the two territories mix.
	var border := clampf(1.0 - (second_d - best_d) / BORDER_BLEND, 0.0, 1.0)
	return [best, second, border]


## Where a corporation's HQ stands (grid), or the city centre.
static func hq_of(corporation_id: StringName) -> Vector2:
	for t in TERRITORIES:
		if t["id"] == corporation_id:
			return t["at"]
	return Vector2.ZERO


func _set_lot_context(i: int, j: int) -> void:
	_apply_context(_territory_pair(i, j))


func _apply_context(pair: Array) -> void:
	_terr = pair[0]
	_terr_next = pair[1]
	_border = pair[2]
	_profile = DISTRICTS.get(_terr, DISTRICTS[&""])
	_terr_col = _pale(Palette.corp_color(_terr)) if _terr != &"" else Color.WHITE


## Screen position (local to this control) of grid point (x, y) with the current camera.
func grid_to_local(x: float, y: float) -> Vector2:
	return _iso(x, y)


## The building on lot (i, j): {"roof", "base", "shape", "height"} or {}. ANIM-R2 R1: a
## baked city answers from its placement (`_placement`), worked out lot by lot the moment
## it is asked, so a map draws its nodes on its first frame, long before the image lands.
func roof_of(i: int, j: int) -> Dictionary:
	var rec: Dictionary = _placement().placed_roof(Vector2i(i, j)) if is_baked() else _roofs.get(Vector2i(i, j), {})
	if rec.is_empty() or _shift == Vector2.ZERO:
		return rec
	# Baked: the roofs are stored in the image's space; move them under the camera.
	var out := rec.duplicate()
	out["roof"] = Transform2D(0.0, _shift) * (rec["roof"] as PackedVector2Array)
	out["base"] = (rec["base"] as Vector2) + _shift
	return out


## The nearest lot with a building to (x, y) within `radius` lots, avoiding `taken`.
func nearest_building(x: float, y: float, radius: int = 4, taken: Dictionary = {}) -> Vector2i:
	var best := Vector2i(roundi(x), roundi(y))
	var best_d := INF
	var src := _placement() if is_baked() else self
	for di in range(-radius, radius + 1):
		for dj in range(-radius, radius + 1):
			var l := Vector2i(roundi(x) + di, roundi(y) + dj)
			if not src._has_building(l) or taken.has(l):
				continue
			var d := Vector2(l).distance_to(Vector2(x, y))
			if d < best_d:
				best_d = d
				best = l
	return best


## True when lot (i, j) is a street (for overlays that route along streets).
func is_street(i: int, j: int) -> bool:
	# ANIM-R2 R1: a baked city asks its placement (its own street grid was never built, so
	# the game's routes cut across blocks while the headless tests' followed the streets).
	return _placement()._is_street_lot(i, j) if is_baked() else _is_street_lot(i, j)


## True when a building stands on lot `l` (a placement works it out without building it).
func _has_building(l: Vector2i) -> bool:
	return _front_of(l) != NO_LOT if _placing else _roofs.has(l)


func _apply_pan_margin() -> void:
	var m := PAN_MARGIN if pan else 0.0
	offset_left = -m
	offset_top = -m
	offset_right = m
	offset_bottom = m


## Grid space (lots) to screen.
func _iso(x: float, y: float) -> Vector2:
	return Vector2(_ox + (x - y) * TILE_A, _oy + (x + y) * TILE_B)


func _grid_of(p: Vector2) -> Vector2:
	var d := (p.x - _ox) / TILE_A
	var s := (p.y - _oy) / TILE_B
	return Vector2((s + d) * 0.5, (s - d) * 0.5)


## Camera: the focused HQ lands on hq_anchor; the whole city centres the Sprawl; a
## painter maps its region's corner to (0, 0).
func _camera() -> void:
	if _painter:
		_ox = 0.0
		_oy = 0.0
		return
	var focus := hq_of(district) + Vector2(HQ_LOTS * 0.5, HQ_LOTS * 0.5) if district != &"" else Vector2(0, 0)
	var anchor := Vector2(size.x * hq_anchor.x, size.y * hq_anchor.y) if district != &"" else size * 0.5
	if pan:
		anchor = size * 0.5
	if focus_grid != Vector2.INF:
		focus = focus_grid
		anchor = size * focus_anchor
	_ox = anchor.x - (focus.x - focus.y) * TILE_A
	_oy = anchor.y - (focus.x + focus.y) * TILE_B


## Works the camera out now from focus, anchor and size (ANIM-5: the camera rig reads the
## new frame before the city redraws).
## ANIM-R2 R1: a baked city's placement holds under any camera, so its roofs are known under
## the new one at once (`camera_settled`): a map's fit passes measure without a redraw each.
func update_camera() -> void:
	_camera()
	if is_baked():
		_shift = Vector2(_ox, _oy)
		_drawn_camera = _camera_key()


## World px (camera-free iso space) of grid point (x, y).
static func world_of(x: float, y: float) -> Vector2:
	return Vector2((x - y) * TILE_A, (x + y) * TILE_B)


## The world rect (px) this camera shows.
func view_rect() -> Rect2:
	return Rect2(-_ox, -_oy, size.x, size.y)


## The region to bake for the current camera: the view grown and snapped.
func bake_region() -> Rect2:
	return snap_region(view_rect().grow(REGION_MARGIN))


## The window's stretch of the 720p canvas (1 at 1280x720, 1.5 at 1080p), snapped.
func _stretch() -> float:
	if not is_inside_tree():
		return 1.0
	return maxf(1.0, snappedf(get_viewport().get_final_transform().get_scale().x, STRETCH_STEP))


## Texture px per city px for a bake of `region` (see BAKE_SCALE_*).
func bake_scale(region: Rect2) -> float:
	return CityBakeCache.fit_scale(region, (BAKE_SCALE_MAP if net_mode else BAKE_SCALE_BACKDROP) * _stretch())


## Everything that changes the baked look (not where the camera is), as a cache key;
## `inf` names another influence than the current one (ANIM-5: the old look of a spread).
func look_key(inf: Variant = null) -> String:
	var infl: Dictionary = influence if inf == null else inf
	var sketch := []
	for p in SKETCH_PARAMS:
		sketch.append(material.get_shader_parameter(p))
	var cult := []
	var names: Array = cultures.keys()
	names.sort()
	for k in names:
		cult.append([String(k), String(cultures[k])])
	return CityBakeCache.key_of([city_seed, String(district), net_mode, ink_set, face_texture, cult, _baked_creep(),
		CityInfluence.signature(infl), sketch, _stretch()])


## The cache key of one bake: the look and the region it covers.
func bake_key(region: Rect2) -> String:
	return look_key() + "@" + var_to_str(Rect2i(region))


func _baked_creep() -> float:
	return snappedf(corp_creep, CREEP_STEP)


## A painter for the bake cache: a copy of this city's look that paints `region` (world
## px) at `scale` into a SubViewport. It draws in world space (camera at the origin),
## placed so the region's corner lands on the viewport's corner.
func make_painter(region: Rect2, p_scale: float) -> NeonCity:
	var p := _twin()
	p.painter_region = region
	p.set_anchors_and_offsets_preset(Control.PRESET_TOP_LEFT)
	p.position = -region.position * p_scale
	p.size = region.size
	p.scale = Vector2(p_scale, p_scale)
	return p


## A copy of this city's look drawing in world space (camera at the origin), outside the
## tree: a bake's painter, one of its build slices or the placement. ANIM-R2 R11: the
## influence is copied (a painter's worker threads read it while this city may take a new
## one).
func _twin() -> NeonCity:
	var p := NeonCity.new()
	p._painter = true
	p.city_seed = city_seed
	p.district = district
	p.net_mode = net_mode
	p.ink_set = ink_set
	p.face_texture = face_texture
	p.cultures = cultures.duplicate()
	p.corp_creep = _baked_creep()
	p.influence = influence.duplicate(true)
	p.dim = 0.0
	for k in SKETCH_PARAMS:
		# Only values set on this city (unset ones read back null: keep the defaults).
		var v: Variant = material.get_shader_parameter(k)
		if v != null:
			p.material.set_shader_parameter(k, v)
	p.set_process(false)
	return p


## What a painter recorded besides pixels, in its image space (for the live layer).
func overlay_data() -> Dictionary:
	return {"roofs": _roofs, "beacons": _beacons, "lights": _lights, "trails": _trails, "signs": _signs}


func _draw() -> void:
	if is_baked():
		_view.queue_redraw()
		return
	_draw_city()


## The live, baked city: the cached image under the camera, then the screen shade.
## ANIM-R2 R1: a camera no finished bake of this look covers shows the night sky (or a
## stand-in that covers nearly all of it) while its bake runs; the placement answers the
## overlays at once all the same (`roof_of`), so a map is never empty; the bake is asked
## for once the camera has held still (`BAKE_SETTLE_FRAMES`: a fit's passes never start a
## bake each), or waits on a running one that will cover the view; when it lands it fades
## in over the sky (`city_bake_fade`).
func _draw_view() -> void:
	if not is_baked():
		return
	_view.draw_rect(Rect2(Vector2.ZERO, size), Palette.NIGHT_SKY)
	if size.x < 2.0 or size.y < 2.0:
		return
	_camera()
	_shift = Vector2(_ox, _oy)
	_placer_stale = true
	if _front_layer.visible:
		(_front_layer.material as ShaderMaterial).set_shader_parameter("cam", Vector2(_ox, _oy))
	# Read the territory now, not at the next poll: a scene whose campaign loads after
	# the backdrop is built would otherwise bake twice.
	var inf := _followed_influence()
	if CityInfluence.signature(inf) != CityInfluence.signature(influence):
		influence = inf
	var look := look_key()
	var view := view_rect()
	var key := CityBakeCache.find(look, view)
	if key != "" and not _drawable(CityBakeCache.entry(key)):
		# ANIM-R5 P1: a bake whose picture is not usable (CityBakeCache marks it failed): a
		# stand-in or the city's silhouette (below), never an empty map and never the
		# seconds-long procedural build on this thread; it is not asked for again.
		key = _stand_in(look, view)
	elif key != "":
		_want = {}
		_note_seen()
		_note_frame_size()
		if not _deferred_prebakes.is_empty():
			_flush_prebakes.call_deferred()
	else:
		_want_bake(look)
		_mark_early()
		key = _stand_in(look, view)
	if key != "" and hold_landing and _sky_shown and key != _baked_key:
		key = ""  # ANIM-R6 A14: it lands once the hold ends (between turns)
	if key == "":
		_sky_shown = true
		# ANIM-R3 B4: the city's shape, dim, from its placement while the image bakes (its own
		# layer: redrawing it never re-lays the maps over the view).
		_sil.visible = true
		_sil.queue_redraw()
		if _baked_key != "":
			_baked_key = ""
			_lights = []
			_beacons = []
			_trails = []
			_signs = []
			_live_for = []
		bake_fade = 0.0
	else:
		_sil.visible = false
		var e := CityBakeCache.entry(key)
		var region: Rect2 = e["region"]
		# ANIM-R6 C3: the view holds the picture it draws until it draws another: the cache may
		# drop the entry (LRU, byte budget) while this canvas still points at its texture, and a
		# kept bake's viewport goes with its last reference.
		drawn_texture = e["texture"]
		_view.draw_texture_rect(drawn_texture, Rect2(region.position + _shift, region.size), false)
		if key != _baked_key:
			_baked_key = key
			_beacons = e.get("beacons", [] as Array[Dictionary])
			_lights = e.get("lights", [] as Array[Dictionary])
			_trails = e.get("trails", [] as Array[Dictionary])
			_signs = e.get("signs", [] as Array[Dictionary])
			_live_for = []
			if _sky_shown:
				# It lands over the sky the view showed meanwhile: it fades in.
				_sky_shown = false
				bake_fade = 0.0
				if Motion.run(BAKE_FADE_MOTION, self, ^"bake_fade", 1.0) == null:
					bake_fade = 1.0
			elif bake_fade < 1.0 and not Motion.live(BAKE_FADE_MOTION):
				bake_fade = 1.0
	_draw_shade(_view)
	_collect_live()
	_built_for = size
	_drawn_camera = _camera_key()
	_fx.queue_redraw()
	rebuilt.emit()


## ANIM-R6 C3: the baked picture this view last drew (held until it draws another, so an
## entry evicted from CityBakeCache never frees a viewport this canvas still draws).
var drawn_texture: Texture2D = null


## ANIM-R2 R1: what shows while this view's bake runs: a finished bake of this look that
## covers at least STANDIN_COVER of the view, or the image on screen until now when it still
## covers the whole view (the old look while the new one bakes); else "" (the night sky: a
## strip of city over part of the screen, over the wheels, read worse than the dark).
func _stand_in(look: String, view: Rect2) -> String:
	var key := CityBakeCache.find_covering(look, view, STANDIN_COVER)
	if key != "" and _drawable(CityBakeCache.entry(key)):
		return key
	if _baked_key != "" and CityBakeCache.has(_baked_key):
		var e := CityBakeCache.entry(_baked_key)
		if _drawable(e) and (e.get("region", Rect2()) as Rect2).encloses(view):
			return _baked_key
	return ""


## ANIM-R5 P1: an entry whose picture can be drawn (not failed, its texture usable).
static func _drawable(e: Dictionary) -> bool:
	return not e.has("failed") and CityBakeCache.usable(e.get("texture") as Texture2D)


## ANIM-R2 R1: the view needs a bake of `look`: noted with the camera now, asked for once
## the camera has held still BAKE_SETTLE_FRAMES frames (`_process`).
func _want_bake(look: String) -> void:
	var cam := _camera_key()
	if _want.get("look", "") != look or _want.get("cam", []) != cam:
		_want = {"look": look, "cam": cam, "region": bake_region(), "frame": Engine.get_process_frames()}


## ANIM-R2 R1: asks for the wanted bake: nothing when one of its look now covers the view,
## a wait on a running one whose region will cover it, else a new bake (ahead of prebakes).
func _request_want() -> void:
	var w := _want
	_want = {}
	if w.is_empty() or not is_inside_tree() or not is_baked():
		return
	var look: String = w["look"]
	if look != look_key():
		_view.queue_redraw()
		return
	var view := view_rect()
	if CityBakeCache.find(look, view) != "":
		_view.queue_redraw()
		return
	var running := CityBakeCache.find_pending(look, view)
	if running != "":
		CityBakeCache.wait(running, _view)
		return
	var region: Rect2 = w["region"]
	CityBakeCache.request(look + "@" + var_to_str(Rect2i(region)), look, make_painter(region, bake_scale(region)), _view, true)


## ANIM-R2 R1: how far a bake that landed over the sky has faded in (0 the sky, 1 the city):
## the veil over it and the live layer follow.
var bake_fade: float = 1.0:
	set(v):
		bake_fade = clampf(v, 0.0, 1.0)
		if _veil != null:
			_veil.visible = bake_fade < 1.0 and _baked_key != ""
			_veil.modulate.a = 1.0 - bake_fade
			_lights_layer.modulate.a = bake_fade
			_beacons_layer.modulate.a = bake_fade
			if _veil.visible:
				_veil.queue_redraw()


func _draw_veil() -> void:
	_veil.draw_rect(Rect2(-size, size * 3.0), Palette.NIGHT_SKY)
	# ANIM-R3 B4: the image fades in from the silhouette the view showed, not from black.
	_draw_silhouette(_veil)
	_draw_shade(_veil)


## ANIM-R3 B4: while a view's bake runs, the city is drawn as its silhouette from the known
## placement (every building's lot footprint in view as a dim block with a faint outline and
## a low lift) so a map, the route or a fight's arena never shows an empty sky: the lots are
## the bake's own (the placement's `_front_of`, cheap: the buildings themselves are not
## built), worked out SILHOUETTE_BUDGET_USEC a frame (the layer redraws until all are known),
## and kept per look.
const SILHOUETTE_BUDGET_USEC := 8000
const SILHOUETTE_FILL := 0.9
const SILHOUETTE_EDGE := 0.4
## The block's lift (px, its top face drawn this far above its footprint).
const SILHOUETTE_LIFT := 10.0
## Lots beyond the view's corners the silhouette also covers (a tall roof leans in).
const SILHOUETTE_MARGIN := 3
var _silhouette: Dictionary = {}  # lot (Vector2i) -> the building's front lot (NO_LOT: none)
var _silhouette_look: String = ""
## Roofs drawn by the last silhouette pass, and whether it knew every lot in view (tests).
var silhouette_roofs: int = 0
var silhouette_done: bool = false
var _sil: Control


func _draw_sil() -> void:
	_draw_silhouette(_sil)


## ANIM-R3 B4: the silhouette's next slice of lots, a frame after the last (NeonCity's
## _process calls it).
func _step_silhouette() -> void:
	if _sil != null and _sil.visible and not silhouette_done:
		_sil.queue_redraw()


func _draw_silhouette(ci: CanvasItem) -> void:
	if not is_baked() or size.x < 2.0 or size.y < 2.0:
		return
	var look := look_key()
	if look != _silhouette_look:
		_silhouette.clear()
		_silhouette_look = look
	var corners: Array[Vector2] = [_grid_of(Vector2.ZERO), _grid_of(Vector2(size.x, 0)), _grid_of(Vector2(0, size.y)), _grid_of(size)]
	var lo := corners[0]
	var hi := corners[0]
	for c in corners:
		lo = lo.min(c)
		hi = hi.max(c)
	var i0 := floori(lo.x) - SILHOUETTE_MARGIN
	var i1 := ceili(hi.x) + SILHOUETTE_MARGIN
	var j0 := floori(lo.y) - SILHOUETTE_MARGIN
	var j1 := ceili(hi.y) + SILHOUETTE_MARGIN
	var t0 := Time.get_ticks_usec()
	var place := _placement()
	var fill := Color(Palette.NIGHT_BLOCK_LIT, SILHOUETTE_FILL)
	var side := Color(Palette.NIGHT_BLOCK, SILHOUETTE_FILL)
	var edge := Color(Palette.NET_CYAN, SILHOUETTE_EDGE)
	var seen := {}
	var done := true
	silhouette_roofs = 0
	var view := Rect2(Vector2.ZERO, size).grow(TILE_A * 2.0)
	var up := Vector2(0, -SILHOUETTE_LIFT)
	# From the view's middle outward (the part a map frames is known first), ring by ring.
	var mid := _grid_of(size * 0.5)
	var ci0 := clampi(roundi(mid.x), i0, i1)
	var cj0 := clampi(roundi(mid.y), j0, j1)
	var reach := maxi(maxi(ci0 - i0, i1 - ci0), maxi(cj0 - j0, j1 - cj0))
	for ring in reach + 1:
		for l: Vector2i in _ring_lots(Vector2i(ci0, cj0), ring, Rect2i(i0, j0, i1 - i0 + 1, j1 - j0 + 1)):
			if not _silhouette.has(l):
				if Time.get_ticks_usec() - t0 > SILHOUETTE_BUDGET_USEC:
					done = false
					continue
				_silhouette[l] = place._front_of(l)
			var f: Vector2i = _silhouette[l]
			if f == NO_LOT or seen.has(f):
				continue
			seen[f] = true
			var cell := place._cell_of(f.x, f.y)
			var a := _iso(cell.position.x, cell.position.y)
			if not view.has_point(a):
				continue
			var b := _iso(cell.end.x, cell.position.y)
			var c := _iso(cell.end.x, cell.end.y)
			var d := _iso(cell.position.x, cell.end.y)
			# The two lit sides, then the top face lifted, then its outline.
			ci.draw_colored_polygon(PackedVector2Array([d, c, c + up, d + up]), side)
			ci.draw_colored_polygon(PackedVector2Array([c, b, b + up, c + up]), side)
			var top := PackedVector2Array([a + up, b + up, c + up, d + up])
			ci.draw_colored_polygon(top, fill)
			ci.draw_polyline(top + PackedVector2Array([a + up]), edge, 1.0)
			silhouette_roofs += 1
	if ci == _sil:
		# The rest next frame when the budget ran out (_step_silhouette).
		silhouette_done = done


## The lots `r` steps (Chebyshev) round `c` inside `box` (r = 0: `c` itself).
static func _ring_lots(c: Vector2i, r: int, box: Rect2i) -> Array[Vector2i]:
	var out: Array[Vector2i] = []
	if r == 0:
		if box.has_point(c):
			out.append(c)
		return out
	for d in range(-r, r + 1):
		for l: Vector2i in [c + Vector2i(d, -r), c + Vector2i(d, r)]:
			if box.has_point(l):
				out.append(l)
	for d in range(-r + 1, r):
		for l: Vector2i in [c + Vector2i(-r, d), c + Vector2i(r, d)]:
			if box.has_point(l):
				out.append(l)
	return out


## The current look's own bake is on screen: when this family last showed another
## influence, that change spreads now (ANIM-5); then the family remembers this one.
func _note_seen() -> void:
	var fam := _family()
	var prev: Variant = _seen.get(fam)
	if prev != null and CityInfluence.signature(prev) != CityInfluence.signature(influence):
		_start_spread(prev)
		if _marked_sig != CityInfluence.signature(influence):
			mark_changes(prev, influence)
	_marked_sig = ""
	_seen[fam] = influence
	if _spread_elapsed >= 0.0:
		_old_layer.queue_redraw()
		_front_layer.queue_redraw()


## ANIM-R5 P2: a territory change whose new look is still baking stamps its marks (CLAIMED /
## SEIZED, the outline and hatch) at once, over the old image: a claim waited 3.6 s with no
## feedback for the bake before anything showed. The tint's spread follows when the bake lands
## (`_note_seen`, which then does not stamp them again). Not while the influence is pinned (a
## raid's playout lets its result spread at its end).
func _mark_early() -> void:
	if influence_pin != null:
		return
	var sig := CityInfluence.signature(influence)
	if sig == _marked_sig:
		return
	var prev: Variant = _seen.get(_family())
	if prev == null or CityInfluence.signature(prev) == sig:
		return
	_marked_sig = sig
	mark_changes(prev, influence)


## The influence whose marks stamped before its bake landed ("" when none: ANIM-R5 P2).
var _marked_sig: String = ""


## The live layer's visible share (culled to the view, capped), refreshed when the camera
## or the image changes.
func _collect_live() -> void:
	var sig := [_baked_key, _shift, size]
	if sig == _live_for:
		return
	_live_for = sig
	var vis := Rect2(-_shift, size).grow(LIGHT_GLOW * 4.0)
	_live_lights = _pick_visible(_lights, vis, "a", LIGHTS_MAX)
	_live_trails = _pick_visible(_busy_trails(), vis, "a", SPARKS_MAX)
	_live_beacons = _pick_visible(_beacons, vis, "pos", BEACONS_MAX)
	_lights_layer.queue_redraw()
	_beacons_layer.queue_redraw()


## Window lights for the GPU blink layer: a lit window (brighter, with a soft glow) shown
## while lit, a dark pane shown while off. Built once per camera, not per frame.
func _draw_lights() -> void:
	if _painter:
		return  # ANIM-R2 R11: blinking lights are live, never baked
	var pts := PackedVector2Array()
	var cols := PackedColorArray()
	var uvs := PackedVector2Array()
	for lt in _live_lights:
		var a: Vector2 = lt["a"] + _shift
		var w: Vector2 = lt["w"]
		var col: Color = lt["color"]
		var up := Vector2(0, -3.2)
		var period: float = lt["period"]
		var ph: float = lt["phase"]
		var g := Vector2(LIGHT_GLOW, LIGHT_GLOW * 0.6)
		var glow := [a + Vector2(-g.x, g.y), a + w + g, a + w + up + Vector2(g.x, -g.y), a + up - g]
		_blink_quad(pts, cols, uvs, glow, Color(col, 0.18), ph, period)
		_blink_quad(pts, cols, uvs, [a, a + w, a + w + up, a + up], col.lightened(0.35), ph, period)
		_blink_quad(pts, cols, uvs, [a, a + w, a + w + up, a + up], Color(Palette.NIGHT_SKY, 0.9), ph, -period)
	_submit(_lights_layer, pts, cols, uvs)


## Beacons for the GPU blink layer: a big halo and bright core while lit, a small dim
## one while off.
func _draw_beacons() -> void:
	if _painter:
		return
	var pts := PackedVector2Array()
	var cols := PackedColorArray()
	var uvs := PackedVector2Array()
	var period := Motion.entry(BEACON_MOTION).duration
	for bcn in _live_beacons:
		var p: Vector2 = bcn["pos"] + _shift
		var col: Color = bcn["color"]
		# Same timing as ever: lit while (phase * 3 + t) mod period < half the period.
		var ph := fmod(float(bcn["phase"]) * 3.0 / period, 1.0)
		_blink_hex(pts, cols, uvs, p, 5.0, Color(col, 0.25), ph, period)
		_blink_hex(pts, cols, uvs, p, 1.6, Color(col, 0.95), ph, period)
		_blink_hex(pts, cols, uvs, p, 3.0, Color(col, 0.1), ph, -period)
		_blink_hex(pts, cols, uvs, p, 1.6, Color(col, 0.4), ph, -period)
	_submit(_beacons_layer, pts, cols, uvs)


static func _blink_quad(pts: PackedVector2Array, cols: PackedColorArray, uvs: PackedVector2Array, q: Array, col: Color, phase: float, period: float) -> void:
	for k in [0, 1, 2, 0, 2, 3]:
		pts.append(q[k])
		cols.append(col)
		uvs.append(Vector2(phase, period))


static func _blink_hex(pts: PackedVector2Array, cols: PackedColorArray, uvs: PackedVector2Array, c: Vector2, r: float, col: Color, phase: float, period: float) -> void:
	for k in 6:
		pts.append(c)
		pts.append(c + Vector2.from_angle(TAU * k / 6.0) * r)
		pts.append(c + Vector2.from_angle(TAU * (k + 1) / 6.0) * r)
		for n in 3:
			cols.append(col)
			uvs.append(Vector2(phase, period))


static func _submit(layer: Control, pts: PackedVector2Array, cols: PackedColorArray, uvs: PackedVector2Array) -> void:
	if pts.is_empty():
		return
	var idx := PackedInt32Array()
	idx.resize(pts.size())
	for k in pts.size():
		idx[k] = k
	RenderingServer.canvas_item_add_triangle_array(layer.get_canvas_item(), idx, pts, cols, uvs)


## Deterministic 0-1 hash of a point (view decoration only).
func _hv(p: Vector2) -> float:
	return _h(int(p.x), int(p.y), 120)


## The traffic sparks on the busiest streets (`city_traffic`'s amplitude: the traffic a
## street needs), the only ones the live layer draws.
func _busy_trails() -> Array[Dictionary]:
	var least := Motion.amplitude(TRAFFIC_MOTION)
	var out: Array[Dictionary] = []
	for t in _trails:
		if float(t.get("traffic", 1.0)) >= least:
			out.append(t)
	return out


## Up to `cap` items whose `field` point lies in `vis`, spread evenly over the list.
static func _pick_visible(items: Array[Dictionary], vis: Rect2, field: String, cap: int) -> Array[Dictionary]:
	var inside: Array[Dictionary] = []
	for it in items:
		if vis.has_point(it[field]):
			inside.append(it)
	if inside.size() <= cap:
		return inside
	var out: Array[Dictionary] = []
	var stride := float(inside.size()) / cap
	for k in cap:
		out.append(inside[int(k * stride)])
	return out


## Haze (darker towards the top, for text), side vignette, and the dim veil.
func _draw_shade(ci: CanvasItem) -> void:
	if not pan:
		var top := Color(Palette.NIGHT_SKY, 0.7)
		var clear := Color(Palette.NIGHT_SKY, 0.0)
		ci.draw_polygon(PackedVector2Array([Vector2(0, 0), Vector2(size.x, 0), Vector2(size.x, size.y * 0.28), Vector2(0, size.y * 0.28)]), PackedColorArray([top, top, clear, clear]))
		var v := Color(0, 0, 0, 0.5)
		var c0 := Color(0, 0, 0, 0)
		ci.draw_polygon(PackedVector2Array([Vector2(0, 0), Vector2(size.x * 0.16, 0), Vector2(size.x * 0.16, size.y), Vector2(0, size.y)]), PackedColorArray([v, c0, c0, v]))
		ci.draw_polygon(PackedVector2Array([Vector2(size.x * 0.84, 0), Vector2(size.x, 0), Vector2(size.x, size.y), Vector2(size.x * 0.84, size.y)]), PackedColorArray([c0, v, v, c0]))
	if dim > 0.0:
		# ANIM-5: past the control too (the baked image reaches beyond it, and a camera ease
		# can show that margin for a moment).
		ci.draw_rect(Rect2(-size, size * 3.0), Color(Palette.NIGHT_SKY, dim))


## The procedural city (headless, painters, and any renderer that can't read back).
func _draw_city() -> void:
	if _painter:
		# A painter draws in world space, outside its own control rect: cull by the
		# region instead, or the viewport would skip it.
		RenderingServer.canvas_item_set_custom_rect(get_canvas_item(), true, painter_region)
	draw_rect(painter_region if _painter else Rect2(Vector2.ZERO, size), Palette.NIGHT_SKY)
	if size.x < 2.0 or size.y < 2.0:
		return
	_shift = Vector2.ZERO
	_baked_key = ""
	_camera()
	var idx := PackedInt32Array()
	if _prebuilt:
		# ANIM-R1 M2: a painter whose geometry was built off the main thread: CityBakeCache
		# submits it in chunks, a frame each (`submit_chunk`), so no frame copies millions of
		# vertices at once.
		_prebuilt = false
		_live_for = []
		_built_for = size
		_drawn_camera = _camera_key()
		rebuilt.emit()
		return
	else:
		var memo_key := _memo_key()
		if memo_key != "" and _geometry_memo.has(memo_key):
			_memo_restore(memo_key)
		else:
			_build_geometry()
			if memo_key != "":
				_memo_store(memo_key)
		_built_serial += 1
		idx.resize(_verts.size())
		for k in _verts.size():
			idx[k] = k
	if not _verts.is_empty():
		RenderingServer.canvas_item_add_triangle_array(get_canvas_item(), idx, _verts, _cols)
	_verts = PackedVector2Array()
	_cols = PackedColorArray()
	if not _painter:
		_draw_shade(self)
	var vis := Rect2(Vector2.ZERO, size).grow(LIGHT_GLOW * 4.0)
	_live_lights = _pick_visible(_lights, vis, "a", LIGHTS_MAX)
	_live_trails = _pick_visible(_busy_trails(), vis, "a", SPARKS_MAX)
	_live_beacons = _pick_visible(_beacons, vis, "pos", BEACONS_MAX)
	_lights_layer.queue_redraw()
	_beacons_layer.queue_redraw()
	_live_for = []
	_built_for = size
	_drawn_camera = _camera_key()
	_fx.queue_redraw()
	rebuilt.emit()


## ANIM-R1 M2: a painter's geometry built ahead of its first draw, the index list of one
## chunk, and the canvas items its chunks were submitted as.
var _prebuilt: bool = false
var _chunk_idx := PackedInt32Array()
var _chunk_rids: Array[RID] = []
## Vertices submitted per frame (a multiple of 3: whole triangles).
const CHUNK_VERTS := 240000
## ANIM-R2 R1 / R11: a painter's build split into slices (twins of it building a run of the
## lots each, on the worker pool at once), the lots in draw order with their territory
## context and influence, and the slices' own runs (first, last + 1). `cancelled` stops a
## build early (the game quits mid-bake).
var _slices: Array[NeonCity] = []
var _lot_list: Array[Vector2i] = []
var _lot_ctx: Array = []
var _lot_infl: Array[float] = []
var _run: Vector2i = Vector2i.ZERO
var _ground_verts := PackedVector2Array()
var _ground_cols := PackedColorArray()
var _ground_trails: Array[Dictionary] = []
var cancelled: bool = false
## ANIM-R2 R1: the built geometry as parts in draw order ([verts, cols] each: a sliced build's
## runs are submitted as they are, never copied into one array), where each starts and the
## vertices in all.
var _parts: Array = []
var _part_base := PackedInt32Array()
var _part_total: int = 0


## ANIM-R1 M2: builds a painter's whole geometry now, so its first draw only lays it out
## for `submit_chunk`. CityBakeCache runs this on a worker thread before the painter enters
## the tree (a node outside the tree, touching only its own data), so a bake never freezes
## a frame for the seconds the GDScript build takes (the raid playout froze ~2-4 s).
func prebuild() -> void:
	_camera()
	_build_geometry()
	_finish_prebuild()


func _finish_prebuild() -> void:
	if _parts.is_empty():
		_parts = [[_verts, _cols]]
	_part_base = PackedInt32Array()
	var total := 0
	var biggest := 0
	for part: Array in _parts:
		_part_base.append(total)
		total += (part[0] as PackedVector2Array).size()
		biggest = maxi(biggest, (part[0] as PackedVector2Array).size())
	_part_total = total
	_chunk_idx = PackedInt32Array()
	_chunk_idx.resize(mini(CHUNK_VERTS, biggest))
	for k in _chunk_idx.size():
		_chunk_idx[k] = k
	_prebuilt = true


## ANIM-R2 R1: makes this painter's `count` build slices and one for the fist roads (main
## thread: they are nodes).
func make_slices(count: int) -> void:
	free_slices()
	for n in count + 1:
		var t := NeonCity.new()
		t._painter = true
		t.set_process(false)
		# The look (setters run here, on the main thread; the worker only shares data).
		t.painter_region = painter_region
		t.city_seed = city_seed
		t.district = district
		t.net_mode = net_mode
		t.ink_set = ink_set
		t.face_texture = face_texture
		t.cultures = cultures
		t.corp_creep = corp_creep
		t.influence = influence
		_slices.append(t)


## Frees the build slices (main thread).
func free_slices() -> void:
	for t in _slices:
		if is_instance_valid(t):
			t.free()
	_slices.clear()


## ANIM-R2 R1, worker thread: the shared part of a sliced build (the palette, the HQs, the
## street grid, the fist and every lot in draw order with its context), then each slice's
## run of lots and the look it reads (shared, read only).
func prebuild_lots() -> void:
	_camera()
	_prepare_build()
	_order_lots()
	var count := _slices.size() - 1
	for n in count + 1:
		var t := _slices[n]
		t.corp_color = corp_color
		t._inks = _inks
		t._hq_rects = _hq_rects
		t._hq_rect = _hq_rect
		t._street_i = _street_i
		t._street_j = _street_j
		t._local_i = _local_i
		t._local_j = _local_j
		t._fist_segs = _fist_segs
		t._fist_box = _fist_box
		t._fist_hull = _fist_hull
		t._fist_cache = {}
		t._lot_list = _lot_list
		t._lot_ctx = _lot_ctx
		t._lot_infl = _lot_infl
		t._run = Vector2i(_lot_list.size() * n / count, _lot_list.size() * (n + 1) / count)


## ANIM-R2 R1, worker thread `n` of the group: slice `n` builds its run of lots, the ground
## pass and the standing pass apart (kept to be joined in the build's order).
func prebuild_slice(n: int) -> void:
	var t := _slices[n]
	t._camera()
	if n == _slices.size() - 1:
		# The last slice: the fist roads (drawn between the ground and the standing pass).
		t._infl = 0.0
		t._fist_roads()
		return
	t._pass_ground(t._run.x, t._run.y)
	t._ground_verts = t._verts
	t._ground_cols = t._cols
	t._ground_trails = t._trails
	t._verts = PackedVector2Array()
	t._cols = PackedColorArray()
	t._trails = []
	t._pass_standing(t._run.x, t._run.y)


## ANIM-R2 R1, worker thread: joins the slices in the build's order (every slice's ground,
## the fist roads, every slice's standing pass), exactly the one build's triangles, roofs,
## lights, trails, beacons and signs.
func prebuild_join() -> void:
	_verts = PackedVector2Array()
	_cols = PackedColorArray()
	_parts = []
	var lots: Array[NeonCity] = []
	lots.assign(_slices.slice(0, _slices.size() - 1))
	for t in lots:
		if not t._ground_verts.is_empty():
			_parts.append([t._ground_verts, t._ground_cols])
		_trails.append_array(t._ground_trails)
		t._ground_verts = PackedVector2Array()
		t._ground_cols = PackedColorArray()
	var fist: NeonCity = _slices[_slices.size() - 1]
	if not fist._verts.is_empty():
		_parts.append([fist._verts, fist._cols])
	fist._verts = PackedVector2Array()
	fist._cols = PackedColorArray()
	for t in lots:
		if not t._verts.is_empty():
			_parts.append([t._verts, t._cols])
		_lights.append_array(t._lights)
		_beacons.append_array(t._beacons)
		_signs.append_array(t._signs)
		_roofs.merge(t._roofs, true)
		t._verts = PackedVector2Array()
		t._cols = PackedColorArray()
	if _parts.is_empty():
		_parts = [[PackedVector2Array(), PackedColorArray()]]
	_finish_prebuild()


## ANIM-R1 M2: submits the prebuilt geometry's vertices from `from` (at most CHUNK_VERTS)
## as a canvas item under the painter; returns where the next chunk starts (-1: done, the
## vertex arrays let go).
func submit_chunk(from: int) -> int:
	if _parts.is_empty():
		_finish_prebuild()
	if from >= _part_total:
		_verts = PackedVector2Array()
		_cols = PackedColorArray()
		_parts = []
		_chunk_idx = PackedInt32Array()
		return -1
	# The part holding vertex `from` (a chunk never spans two parts).
	var k := _part_base.size() - 1
	while k > 0 and _part_base[k] > from:
		k -= 1
	var pv: PackedVector2Array = _parts[k][0]
	var pc: PackedColorArray = _parts[k][1]
	var at := from - _part_base[k]
	var end := mini(pv.size(), at + CHUNK_VERTS)
	var to := _part_base[k] + end
	var ci := RenderingServer.canvas_item_create()
	RenderingServer.canvas_item_set_parent(ci, get_canvas_item())
	RenderingServer.canvas_item_set_custom_rect(ci, true, painter_region)
	# In order after the painter's own drawing, with its sketch material (a chunk drawn out of
	# order, or without the material, lost the buildings or the look).
	RenderingServer.canvas_item_set_draw_index(ci, _chunk_rids.size())
	RenderingServer.canvas_item_set_use_parent_material(ci, true)
	var n := end - at
	var idx := _chunk_idx if n == _chunk_idx.size() else _chunk_idx.slice(0, n)
	RenderingServer.canvas_item_add_triangle_array(ci, idx, pv.slice(at, end), pc.slice(at, end))
	_chunk_rids.append(ci)
	return to


## ANIM-R1 M2: frees the canvas items `submit_chunk` made (after the bake is read).
func free_chunks() -> void:
	for ci in _chunk_rids:
		RenderingServer.free_rid(ci)
	_chunk_rids.clear()


## ANIM-R1 M2: bakes `region` (world px) of this city's look under influence `inf` (null:
## the current one) ahead of need (a raid's playout area behind its setup, the post-raid
## look while the raid plays), unless a finished or running bake of that look covers it.
## Returns the cache key ("" when nothing was needed, the city does not bake, or the bake
## waits). ANIM-R2 R1: a city on screen whose own view is not baked yet asks for it first:
## the prebake waits until the view's image has landed (it took the build slot before the
## view's own bake, and the raid setup sat 3.5 s on the sky).
## ANIM-R5 P2: `outlive` for a bake the next scene shows (CityBakeCache.request): it is not
## dropped when this scene goes.
## `creep` (>= 0) names another Heat creep than the city's (the look after a raid's Heat while
## the playout still holds the old one).
func prebake(region: Rect2, inf: Variant = null, outlive: bool = false, creep: float = -1.0) -> String:
	if not is_baked() or not is_inside_tree():
		return ""
	var held: Dictionary = (_followed_influence() if inf == null else inf as Dictionary).duplicate(true)
	if is_visible_in_tree() and not view_covered():
		_deferred_prebakes.append([region, held, outlive, creep])
		return ""
	var saved := influence
	var saved_creep := corp_creep
	influence = held
	if creep >= 0.0:
		corp_creep = creep
	var look := look_key()
	var key := ""
	if CityBakeCache.find(look, region) == "":
		var r := snap_region(region)
		key = look + "@" + var_to_str(Rect2i(r))
		# ANIM-R2 R1: nothing when a running bake of this look will cover it.
		var running := CityBakeCache.find_pending(look, region)
		if running != "":
			key = running
			if outlive:
				CityBakeCache.wait(running, CityBakeCache._holder())
		elif not CityBakeCache.has(key) and not CityBakeCache.is_pending(key):
			CityBakeCache.request(key, look, make_painter(r, bake_scale(r)), _view, false, outlive)
	influence = saved
	corp_creep = saved_creep
	return key


## ANIM-R5 P2: the bake region (world px, snapped, with its margin) a camera focused on grid
## point `focus` at `anchor` (0..1 of the screen) and `zoom` shows on a screen of
## `screen` px: a page's frame worked out before the page exists (the route after a raid
## interlude, a playout's fights).
func region_for(focus: Vector2, anchor: Vector2, zoom: float, screen: Vector2) -> Rect2:
	var view := screen / maxf(zoom, 0.001)
	var a := view * anchor
	var ox := a.x - (focus.x - focus.y) * TILE_A
	var oy := a.y - (focus.x + focus.y) * TILE_B
	return snap_region(Rect2(-ox, -oy, view.x, view.y).grow(REGION_MARGIN))


## ANIM-R2 R1: prebakes asked for while this city's own view was not baked yet ([region,
## influence] each), asked for once it is.
var _deferred_prebakes: Array = []


func _flush_prebakes() -> void:
	var todo := _deferred_prebakes
	_deferred_prebakes = []
	for q: Array in todo:
		prebake(q[0], q[1], bool(q[2]), float(q[3]))


## `region` (world px) grown out to the REGION_SNAP grid (bakes of nearby cameras share it).
static func snap_region(region: Rect2) -> Rect2:
	var p := (region.position / REGION_SNAP).floor() * REGION_SNAP
	var e := (region.end / REGION_SNAP).ceil() * REGION_SNAP
	return Rect2(p, e - p)


## ANIM-R2 R1: the bake region the default frame (the district's HQ at `hq_anchor`, no zoom,
## no pan) shows at `view_size` (the Modem, event and loot backdrops, a fight's arena).
func frame_region(view_size: Vector2) -> Rect2:
	var focus := hq_of(district) + Vector2(HQ_LOTS * 0.5, HQ_LOTS * 0.5) if district != &"" else Vector2.ZERO
	var anchor := Vector2(view_size.x * hq_anchor.x, view_size.y * hq_anchor.y) if district != &"" else view_size * 0.5
	var ox := anchor.x - (focus.x - focus.y) * TILE_A
	var oy := anchor.y - (focus.x + focus.y) * TILE_B
	return snap_region(Rect2(-ox, -oy, view_size.x, view_size.y).grow(REGION_MARGIN))


## ANIM-R2 R1 (view memory): the view sizes the net's default frame was last drawn at (a
## run's backdrop, a fight's arena), newest last, at most FRAME_SIZES_MAX.
static var frame_sizes: Array[Vector2] = []
const FRAME_SIZES_MAX := 4


func _note_frame_size() -> void:
	if not net_mode or pan or focus_grid != Vector2.INF or not scale.is_equal_approx(Vector2.ONE):
		return
	var at := frame_sizes.find(size)
	if at == frame_sizes.size() - 1 and at >= 0:
		return
	if at >= 0:
		frame_sizes.remove_at(at)
	frame_sizes.append(size)
	while frame_sizes.size() > FRAME_SIZES_MAX:
		frame_sizes.remove_at(0)


## ANIM-R2 R1: bakes, ahead, the default frame at every size in `sizes` and every size it was
## drawn at lately (one region enclosing them all): a fight's arena, the Modem, event and
## loot pages open on their city. Returns prebake's key.
func prebake_frames(sizes: Array[Vector2], outlive: bool = false) -> String:
	var all: Array[Vector2] = sizes.duplicate()
	for v in frame_sizes:
		if not all.has(v):
			all.append(v)
	var region := Rect2()
	for v in all:
		if v.x < 2.0 or v.y < 2.0:
			continue
		var r := frame_region(v)
		region = r if not region.has_area() else region.merge(r)
	if not region.has_area():
		return ""
	return prebake(region, null, outlive)


## The procedural city's geometry for the current camera and look: streets, the fist,
## every lot back to front into `_verts` / `_cols`, and the roofs, lights, trails,
## beacons and signs the overlays and the live layer read.
func _build_geometry() -> void:
	_prepare_build()
	_order_lots()
	# Pass 1, the ground (streets, plazas, lot floors); then the Cell's fist roads on top
	# of it; pass 2, everything standing, back to front, so towers overlap the roads.
	_pass_ground(0, _lot_list.size())
	_infl = 0.0
	_fist_roads()
	_pass_standing(0, _lot_list.size())
	_lot_list = []
	_lot_ctx = []
	_lot_infl = []


## The palette, fresh containers, the HQ plazas, the street grid and the fist (ANIM-R2 R1:
## shared by a whole build, a sliced one and the placement).
func _prepare_build() -> void:
	_inks.clear()
	for c in INKS:
		_inks.append(_pale(c))
	if district != &"":
		corp_color = _pale(Palette.corp_color(district))
	# Fresh containers (a live city may hold the bake cache's shared ones).
	_trails = []
	_beacons = []
	_signs = []
	_lights = []
	_roofs = {}
	_verts = PackedVector2Array()
	_cols = PackedColorArray()
	_hq_rects = {}
	for t in TERRITORIES:
		if t["id"] != &"":
			var at: Vector2 = t["at"]
			_hq_rects[t["id"]] = Rect2i(int(at.x), int(at.y), HQ_LOTS, HQ_LOTS)
	_hq_rect = _hq_rects.get(district, Rect2i())
	_build_streets()
	_build_fist()


## Every lot to draw, back to front, with its territory context and influence: the control
## (or, painting a bake, its region) plus margins for buildings standing below the edge and
## reaching up into it.
func _order_lots() -> void:
	var dr := painter_region if _painter else Rect2(Vector2.ZERO, size)
	var s_min := int(floor((dr.position.y - 40.0 - _oy) / TILE_B)) - 2
	var s_max := int((dr.end.y + 420.0 - _oy) / TILE_B) + 2
	var d_min := int(floor((dr.position.x - 80.0 - _ox) / TILE_A)) - 1
	var d_max := int((dr.end.x + 80.0 - _ox) / TILE_A) + 1
	_lot_list = []
	_lot_ctx = []
	_lot_infl = []
	for s in range(s_min, s_max):
		for d in range(d_min, d_max + 1):
			if posmod(s + d, 2) != 0:
				continue
			var i := (s + d) / 2
			var j := (s - d) / 2
			_lot_list.append(Vector2i(i, j))
			var pair := _territory_pair(i, j)
			_lot_ctx.append(pair)
			_lot_infl.append(CityInfluence.value_at(influence, Vector2(i + 0.5, j + 0.5), pair[0]))


## Pass 1 over lots [from, to): the ground (streets, plazas, lot floors).
func _pass_ground(from: int, to: int) -> void:
	for n in range(from, to):
		if cancelled:
			return
		var l := _lot_list[n]
		_apply_context(_lot_ctx[n])
		_infl = _lot_infl[n]
		if _hq_at(l.x, l.y) != &"":
			_plaza(l.x, l.y)
		elif _is_street_lot(l.x, l.y):
			_street(l.x, l.y, _street_i.has(l.x), _street_j.has(l.y))
		else:
			var p := _rect_pts(l.x, l.y, l.x + 1, l.y + 1)
			var ground := GROUND.lerp(CityInfluence.color_for(influence, _infl), absf(_infl) * INFLUENCE_GROUND_TINT)
			_quad(p[0], p[1], p[2], p[3], ground, ground, ground, ground)
	_infl = 0.0


## Pass 2 over lots [from, to): everything standing, back to front (the HQs from their
## front lot).
func _pass_standing(from: int, to: int) -> void:
	for n in range(from, to):
		if cancelled:
			return
		var l := _lot_list[n]
		_apply_context(_lot_ctx[n])
		_infl = _lot_infl[n]
		var in_hq := _hq_at(l.x, l.y)
		if in_hq != &"":
			var hr: Rect2i = _hq_rects[in_hq]
			if l.x == hr.end.x - 1 and l.y == hr.end.y - 1:
				_drawing_hq = true
				_infl = 0.0
				_hq(in_hq, hr)
				_drawing_hq = false
			continue
		if _is_street_lot(l.x, l.y):
			continue
		_lot(l.x, l.y)
	_infl = 0.0


# --- Placement (ANIM-R2 R1) -------------------------------------------------------------------
# A baked city's image takes a second or more to build and paint, but where its buildings
# stand is cheap to work out lot by lot. The live city keeps a world-space twin of its look
# (`_placement`) that answers `roof_of`, `nearest_building` and `is_street` the moment a map
# asks: the same roofs the bake shows (the same building code, only nothing emitted), so
# the nodes and labels draw on a map's first frame and stay put when the image lands.

## The placement for this city's look (made when the look's layout changed).
func _placement() -> NeonCity:
	if _placer != null and not _placer_stale:
		return _placer
	_placer_stale = false
	var cult := []
	var names: Array = cultures.keys()
	names.sort()
	for k in names:
		cult.append([String(k), String(cultures[k])])
	var key := var_to_str([city_seed, String(district), cult])
	if _placer == null or key != _placer_key:
		_free_placement()
		_placer = _twin()
		_placer._placing = true
		_placer._camera()
		_placer._prepare_build()
		_placer_key = key
	return _placer


func _free_placement() -> void:
	if _placer != null and is_instance_valid(_placer):
		_placer.free()
	_placer = null
	_placer_key = ""


## The lot whose building covers lot `l` (the front lot of its cell, as the build draws it:
## of the lots that may draw one over `l`, the last in draw order), or NO_LOT.
func _front_of(l: Vector2i) -> Vector2i:
	var known: Variant = _covers.get(l)
	if known != null:
		return known
	var best := NO_LOT
	# Draw order: by i + j, then i - j (a cell is at most 2x2, `l` in it).
	for f: Vector2i in [l, l + Vector2i(0, 1), l + Vector2i(1, 0), l + Vector2i(1, 1)]:
		if _builds_at(f) and _cell_of(f.x, f.y).has_point(l):
			best = f
	_covers[l] = best
	return best


## True when the build draws a building from lot `f` (as `_pass_standing` / `_lot` decide).
func _builds_at(f: Vector2i) -> bool:
	if _hq_at(f.x, f.y) != &"" or _is_street_lot(f.x, f.y) or _fist_dist(f.x, f.y) < FIST_CLEAR:
		return false
	return f == _cell_of(f.x, f.y).end - Vector2i.ONE


## The building on lot `l` in world space ({} when none), placed the first time it is asked.
func placed_roof(l: Vector2i) -> Dictionary:
	var f := _front_of(l)
	if f == NO_LOT:
		return {}
	if not _fronts.has(f):
		_apply_context(_territory_pair(f.x, f.y))
		_infl = 0.0
		_roofs = {}
		_building(_cell_of(f.x, f.y))
		_fronts[f] = _roofs.get(f, {})
		_roofs = {}
		_beacons = []
		_lights = []
	return _fronts[f]


## Test runs only (docs/TEST_SUITE.md): the procedural city's geometry is a pure function
## of the look and the camera, and building it costs seconds in GDScript, so under GUT a
## built geometry is kept by those inputs and a city drawn again with the same ones reuses
## it (the same triangles, roofs, lights, trails, beacons and signs). Off outside the test
## runner (the game bakes instead); a test can switch it off.
static var geometry_memo_enabled: bool = _is_gut_run()
## Test runs only: the headless city skips emitting its triangles (the dummy renderer
## never shows them) and still places every roof, light, trail, beacon and sign the
## overlays and tests read, exactly as a full build does. On outside the test runner;
## test_city_geometry_memo builds every district with it on.
static var emit_triangles: bool = not _is_gut_run()
## Kept geometries (least recently used drop out past GEOMETRY_MEMO_CAP).
const GEOMETRY_MEMO_CAP := 48
static var _geometry_memo: Dictionary = {}


## The memo key: every input the geometry reads (the look, the camera's result and the
## size), or "" when the memo is off or this city paints a bake.
func _memo_key() -> String:
	if not geometry_memo_enabled or _painter:
		return ""
	var cult := []
	var names: Array = cultures.keys()
	names.sort()
	for k in names:
		cult.append([String(k), String(cultures[k])])
	return var_to_str([emit_triangles, city_seed, String(district), net_mode, ink_set, face_texture, cult, corp_creep, corp_color,
		var_to_str(influence), size, _ox, _oy])


func _memo_store(key: String) -> void:
	_geometry_memo.erase(key)
	while _geometry_memo.size() >= GEOMETRY_MEMO_CAP:
		_geometry_memo.erase(_geometry_memo.keys()[0])
	# Containers a later build clears in place are copied; the rest are replaced by a
	# build, never changed after it (as with the bake cache's shared ones).
	_geometry_memo[key] = {"verts": _verts, "cols": _cols, "roofs": _roofs, "lights": _lights,
		"trails": _trails, "beacons": _beacons, "signs": _signs, "inks": _inks.duplicate(),
		"corp_color": corp_color, "hq_rects": _hq_rects.duplicate(), "hq_rect": _hq_rect,
		"street_i": _street_i, "street_j": _street_j, "local_i": _local_i, "local_j": _local_j,
		"fist_segs": _fist_segs.duplicate(), "fist_box": _fist_box, "fist_hull": _fist_hull,
		"fist_cache": _fist_cache.duplicate(), "terr": _terr, "terr_next": _terr_next,
		"border": _border, "profile": _profile, "terr_col": _terr_col}


func _memo_restore(key: String) -> void:
	var m: Dictionary = _geometry_memo[key]
	# Most recently used last.
	_geometry_memo.erase(key)
	_geometry_memo[key] = m
	_verts = m["verts"]
	_cols = m["cols"]
	_roofs = m["roofs"]
	_lights = m["lights"]
	_trails = m["trails"]
	_beacons = m["beacons"]
	_signs = m["signs"]
	_inks.assign(m["inks"])
	corp_color = m["corp_color"]
	_hq_rects = (m["hq_rects"] as Dictionary).duplicate()
	_hq_rect = m["hq_rect"]
	_street_i = m["street_i"]
	_street_j = m["street_j"]
	_local_i = m["local_i"]
	_local_j = m["local_j"]
	_fist_segs.assign(m["fist_segs"])
	_fist_box = m["fist_box"]
	_fist_hull = m["fist_hull"]
	_fist_cache = (m["fist_cache"] as Dictionary).duplicate()
	_terr = m["terr"]
	_terr_next = m["terr_next"]
	_border = m["border"]
	_profile = m["profile"]
	_terr_col = m["terr_col"]


## Whether this process runs the GUT test suite (as Settings.is_test_run, without naming
## the autoload: a static initializer can run before autoloads exist).
static func _is_gut_run() -> bool:
	for a in OS.get_cmdline_args():
		if a.ends_with("gut_cmdln.gd"):
			return true
	return false


## Empties the test-run geometry memo.
static func clear_geometry_memo() -> void:
	_geometry_memo.clear()


## ANIM-R2 R1: what a map's layout (the lot of each node, the street routes) depends on: a
## baked city's placement (the camera never changes it), or, drawn procedurally, the look
## and the camera (a build places only the lots it draws).
func placement_sig() -> String:
	if is_baked():
		_placement()
		return "placed:" + _placer_key
	return var_to_str([look_key(), _camera_key(), _built_serial])


## ANIM-R2 R9: what a roof's screen position depends on besides its lot: the frame the city
## was last drawn under (its camera and, baked, the image's shift) and its placement.
func frame_stamp() -> Array:
	return [_drawn_camera, _shift, _placer_key if is_baked() else "built", _built_serial]


## The camera's inputs (what `_camera` reads).
func _camera_key() -> Array:
	return [focus_grid, focus_anchor, size, district, pan, hq_anchor]


## True when the city was last drawn (and its roofs placed) under the current camera:
## overlays measuring node positions after a camera change wait for this (H23 #5).
func camera_settled() -> bool:
	return _drawn_camera == _camera_key()


## Irregular street spacing along both axes (deterministic per district).
func _build_streets() -> void:
	for axis in 2:
		var streets := {}
		var local := {}
		var pos := -GRID_RANGE
		while pos < GRID_RANGE:
			streets[pos] = true
			var block := BLOCK_MIN + int(_h(pos, axis, 60) * (BLOCK_MAX - BLOCK_MIN + 1))
			for k in block:
				local[pos + 1 + k] = k
			pos += block + 1
		if axis == 0:
			_street_i = streets
			_local_i = local
		else:
			_street_j = streets
			_local_j = local


## Traffic 0-1 of a street lot: some avenues are busy, and everything near the HQ is.
func _traffic(i: int, j: int, along_i: bool) -> float:
	var t := _h(i if along_i else 0, 0 if along_i else j, 61)
	t = t * t
	var d := _hq_distance(i, j)
	t = maxf(t, clampf(1.0 - d / 16.0, 0.0, 1.0))
	return t


## The corporation whose HQ plaza covers lot (i, j), or &"" (the Cell has none).
func _hq_at(i: int, j: int) -> StringName:
	for cid in _hq_rects:
		if cid != FIST_TERRITORY and (_hq_rects[cid] as Rect2i).has_point(Vector2i(i, j)):
			return cid
	return &""


## Screen segments of the fist roads (with the current camera) and their bounds.
func _build_fist() -> void:
	_fist_segs.clear()
	_fist_hull.clear()
	_fist_cache.clear()
	if not _hq_rects.has(FIST_TERRITORY):
		_fist_box = Rect2()
		return
	var hr: Rect2i = _hq_rects[FIST_TERRITORY]
	var c := _iso(hr.position.x + HQ_LOTS * 0.5, hr.position.y + HQ_LOTS * 0.5)
	for v: Vector2 in FIST_HULL:
		_fist_hull.append(c + (v - Vector2(0.5, 0.5)) * FIST_SIZE)
	for poly: Array in FIST_POLYS:
		for q in poly.size():
			var a: Vector2 = c + (poly[q] - Vector2(0.5, 0.5)) * FIST_SIZE
			var b: Vector2 = c + (poly[(q + 1) % poly.size()] - Vector2(0.5, 0.5)) * FIST_SIZE
			_fist_segs.append(PackedVector2Array([a, b]))
	_fist_box = Rect2(c - FIST_SIZE * 0.5, FIST_SIZE).grow(FIST_ROAD_HALF * 2.0)


## Screen distance (px) from lot (i, j)'s centre to the nearest fist road, or INF.
func _fist_dist(i: int, j: int) -> float:
	var key := Vector2i(i, j)
	if _fist_cache.has(key):
		return _fist_cache[key]
	var p := _iso(i + 0.5, j + 0.5)
	var best := INF
	if not _fist_segs.is_empty() and _fist_box.has_point(p):
		for sg in _fist_segs:
			best = minf(best, p.distance_to(Geometry2D.get_closest_point_to_segment(p, sg[0], sg[1])))
	_fist_cache[key] = best
	return best


## True when lot (i, j) lies inside the fist (its shapes or its roads).
func _in_fist(i: int, j: int) -> bool:
	if _fist_dist(i, j) < FIST_ROAD_HALF * 2.0:
		return true
	var p := _iso(i + 0.5, j + 0.5)
	if not _fist_box.has_point(p):
		return false
	return Geometry2D.is_point_in_polygon(p, _fist_hull)


## True for an ordinary street lot (streets stop at the fist's outline).
func _is_street_lot(i: int, j: int) -> bool:
	return (_street_i.has(i) or _street_j.has(j)) and not _in_fist(i, j)


## The fist roads: like the busiest streets (many skinny marker strokes side by side),
## wider still, in the Cell's full-strength colour.
func _fist_roads() -> void:
	var col := Palette.corp_color(FIST_TERRITORY)
	var strokes := 28
	for n in _fist_segs.size():
		var a: Vector2 = _fist_segs[n][0]
		var b: Vector2 = _fist_segs[n][1]
		if a.distance_to(b) < 1.0:
			continue
		var dir := (b - a).normalized()
		var nn := dir.orthogonal()
		# Dark roadbed first, overshooting so the corners join.
		var e0 := a - dir * FIST_ROAD_HALF
		var e1 := b + dir * FIST_ROAD_HALF
		var bed := STREET
		_quad(e0 - nn * (FIST_ROAD_HALF + 4.0), e1 - nn * (FIST_ROAD_HALF + 4.0), e1 + nn * (FIST_ROAD_HALF + 4.0), e0 + nn * (FIST_ROAD_HALF + 4.0), bed, bed, bed, bed)
		var g := Color(col, 0.14)
		_quad(e0 - nn * (FIST_ROAD_HALF + 6.0), e1 - nn * (FIST_ROAD_HALF + 6.0), e1 + nn * (FIST_ROAD_HALF + 6.0), e0 + nn * (FIST_ROAD_HALF + 6.0), g, g, g, g)
		for k in strokes:
			var t := (float(k) + 0.5) / strokes * 2.0 - 1.0
			var lane := t * FIST_ROAD_HALF + (_h(n, k, 87) - 0.5) * 1.6
			var over := FIST_ROAD_HALF * (0.4 + 0.6 * _h(k, n, 88))
			var alpha := 0.55 + 0.4 * _h(n + k, 5, 89)
			_ink_line(a + nn * lane - dir * over, b + nn * lane + dir * over, Color(col, alpha), 0.9 + _h(k, n, 86) * 0.6, false)


## Distance (lots) to the nearest corporation HQ centre (the Cell has no HQ).
func _hq_distance(i: int, j: int) -> float:
	var best := INF
	for cid in _hq_rects:
		if cid == FIST_TERRITORY:
			continue
		best = minf(best, Vector2(i, j).distance_to(Vector2((_hq_rects[cid] as Rect2i).get_center())))
	return best


# --- Primitives ---------------------------------------------------------------------------

func _tri(a: Vector2, b: Vector2, c: Vector2, ca: Color, cb: Color, cc: Color) -> void:
	if not emit_triangles or _placing:
		return
	# ANIM-R2 R1: pushed one by one (append_array of an Array literal built a temporary
	# Array per triangle: most of a bake's build time).
	_verts.push_back(a)
	_verts.push_back(b)
	_verts.push_back(c)
	_cols.push_back(ca)
	_cols.push_back(cb)
	_cols.push_back(cc)


func _quad(a: Vector2, b: Vector2, c: Vector2, d: Vector2, ca: Color, cb: Color, cc: Color, cd: Color) -> void:
	if not emit_triangles or _placing:
		return
	_verts.push_back(a)
	_verts.push_back(b)
	_verts.push_back(c)
	_verts.push_back(a)
	_verts.push_back(c)
	_verts.push_back(d)
	_cols.push_back(ca)
	_cols.push_back(cb)
	_cols.push_back(cc)
	_cols.push_back(ca)
	_cols.push_back(cc)
	_cols.push_back(cd)


func _poly(pts: PackedVector2Array, col: Color) -> void:
	if not emit_triangles or _placing:
		return
	var c := Vector2.ZERO
	for p in pts:
		c += p
	c /= pts.size()
	for k in pts.size():
		_tri(c, pts[k], pts[(k + 1) % pts.size()], col, col, col)


## An inked line, drawn like a pen stroke: a soft glow, then a slightly bowed core in
## short segments (the sketch shader's wobble bends them further) whose thickness wanders
## and tapers, overshooting the corners by a varying amount, then a faint second pass a
## hair off the first, as if the line was gone over again.
func _ink_line(a: Vector2, b: Vector2, col: Color, width: float = 1.3, glow: bool = true) -> void:
	if not emit_triangles or _placing:
		return
	var length := a.distance_to(b)
	if length < 0.5:
		return
	var seed_a := int(a.x * 7.0 + b.y * 3.0)
	var seed_b := int(a.y * 5.0 + b.x * 11.0)
	var dir := (b - a) / length
	var n := dir.orthogonal()
	var over0 := 0.5 + _h(seed_a, seed_b, 22) * 3.5
	var over1 := 0.5 + _h(seed_b, seed_a, 23) * 3.5
	var a0 := a - dir * over0
	var b0 := b + dir * over1
	if glow:
		var g := Color(col, 0.15)
		_quad(a0 - n * 3.5, b0 - n * 3.5, b0 + n * 3.5, a0 + n * 3.5, g, g, g, g)
	var bow := (_h(seed_a, seed_b, 24) - 0.5) * minf(4.0, length * 0.05)
	_stroke(a0, b0, n, bow, width, Color(col, col.a * 0.95), seed_a)
	# The second pass: offset, shorter at one end, fainter and thinner.
	var shift := n * (0.8 + _h(seed_a, seed_b, 25) * 1.2) * (1.0 if _h(seed_b, seed_a, 26) < 0.5 else -1.0)
	var trim := dir * (_h(seed_a, seed_b, 27) * 4.0)
	_stroke(a0 + shift + trim, b0 + shift - trim * 0.5, n, -bow * 0.6, width * 0.65, Color(col, col.a * 0.45), seed_b)


func _stroke(a: Vector2, b: Vector2, n: Vector2, bow: float, width: float, col: Color, key: int) -> void:
	if not emit_triangles or _placing:
		return
	var steps := clampi(int(a.distance_to(b) / 5.0), 2, 400)
	var prev_l := Vector2.ZERO
	var prev_r := Vector2.ZERO
	for k in steps + 1:
		var t := float(k) / steps
		var p := a.lerp(b, t) + n * sin(t * PI) * bow
		var taper := clampf(minf(t, 1.0 - t) * 6.0, 0.65, 1.0)
		var w := width * taper * (0.75 + 0.5 * _h(key, k, 21))
		var l := p - n * w * 0.5
		var r := p + n * w * 0.5
		if k > 0:
			_quad(prev_l, l, r, prev_r, col, col, col, col)
		prev_l = l
		prev_r = r


## Grid rectangle footprint (lots) as screen points: back, right, front, left.
func _rect_pts(x0: float, y0: float, x1: float, y1: float) -> PackedVector2Array:
	return PackedVector2Array([_iso(x0, y0), _iso(x1, y0), _iso(x1, y1), _iso(x0, y1)])


## A grid rectangle turned by `angle` (radians) about its centre, as screen points.
func _turned(angle: float, x0: float, y0: float, x1: float, y1: float) -> PackedVector2Array:
	if absf(angle) < 0.001:
		return _rect_pts(x0, y0, x1, y1)
	var c := Vector2((x0 + x1) * 0.5, (y0 + y1) * 0.5)
	var pts := PackedVector2Array()
	for q in [Vector2(x0, y0), Vector2(x1, y0), Vector2(x1, y1), Vector2(x0, y1)]:
		var v: Vector2 = (q - c).rotated(angle) + c
		pts.append(_iso(v.x, v.y))
	return pts


## Regular n-gon footprint of grid radius r around (cx, cy).
func _ngon(cx: float, cy: float, r: float, n: int, rot: float = 0.0) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for k in n:
		var t := rot + TAU * k / n
		pts.append(_iso(cx + cos(t) * r, cy + sin(t) * r))
	return pts


## Extrudes a convex ground footprint: faces shaded by facing (left faces catch the
## city glow), a roof, window rows on vertical faces, and neon ink on the roof edge and
## the visible verticals. `z0` lifts the base (tiers); `top_scale` < 1 tapers it.
## Returns the roof points.
func _extrude(base: PackedVector2Array, z0: float, h: float, top_scale: float, fill: Color, ink: Color, lit: float = 0.2, key: int = 0) -> PackedVector2Array:
	var n := base.size()
	var c := Vector2.ZERO
	for p in base:
		c += p
	c /= n
	var bot := PackedVector2Array()
	var top := PackedVector2Array()
	for p in base:
		bot.append(p + Vector2(0, -z0))
		top.append(c + (p - c) * top_scale + Vector2(0, -z0 - h))
	if _placing:
		return top  # ANIM-R2 R1: the placement needs the roof, nothing drawn
	var faces: Array[Dictionary] = []
	for k in n:
		var a := bot[k]
		var b := bot[(k + 1) % n]
		var e := b - a
		var nrm := Vector2(e.y, -e.x).normalized()
		if nrm.dot((a + b) * 0.5 - (c + Vector2(0, -z0))) < 0.0:
			nrm = -nrm
		if top_scale >= 0.99 and nrm.y <= 0.02:
			continue
		faces.append({"k": k, "n": nrm, "y": (a.y + b.y) * 0.5})
	faces.sort_custom(func(f1: Dictionary, f2: Dictionary) -> bool: return f1["y"] < f2["y"])
	var visible_v := {}
	for f in faces:
		var k: int = f["k"]
		var k2 := (k + 1) % n
		var nrm: Vector2 = f["n"]
		var light := clampf(0.5 - nrm.x * 0.5, 0.0, 1.0)
		var up_col := fill.lerp(FACE_LIGHT, 0.12 + light * 0.35)
		var low_col := fill.darkened(0.35)
		var slate := _slate()
		if slate:
			# Painted slate: lit from above, the base falling into shadow.
			var tone := fill.lerp(_slate_tone(ink), 0.8)
			var catch := 1.0 if face_texture == 9 else 0.6
			up_col = tone.lerp(SLATE_LIGHT, (0.12 + light * 0.34) * catch)
			low_col = tone.darkened(0.6 - light * 0.2)
		_quad(bot[k], bot[k2], top[k2], top[k], low_col, low_col, up_col, up_col)
		if slate and h > 10.0:
			_greeble_face(bot[k], bot[k2], top[k2], top[k], light, key * 31 + k, top_scale >= 0.99)
		if face_texture in [1, 2, 3, 7, 8] and h > 6.0:
			_texture_face(bot[k], bot[k2], top[k2], top[k], nrm.x > 0.0, key * 31 + k)
		if nrm.y > 0.02:
			visible_v[k] = true
			visible_v[k2] = true
		if top_scale >= 0.99 and h > 14.0:
			_windows(bot[k], bot[k2], h, lit, key * 31 + k, nrm.x < 0.0)
	if top_scale > 0.05:
		if _slate():
			# Roof: a lit slab with a raised rim and a recessed inner deck.
			var roof_col := fill.lerp(_slate_tone(ink), 0.8).lerp(SLATE_LIGHT, 0.22)
			_poly(top, roof_col)
			var tc := Vector2.ZERO
			for q in top:
				tc += q
			tc /= n
			var inner := PackedVector2Array()
			for q in top:
				inner.append(tc + (q - tc) * 0.74)
			_poly(inner, roof_col.darkened(0.3))
			for q in n:
				_hair(inner[q], inner[(q + 1) % n], Color(SLATE_LIGHT, 0.35 if inner[q].y > tc.y else 0.15), 1.0)
				_hair(inner[q] + Vector2(0, 1.2), inner[(q + 1) % n] + Vector2(0, 1.2), Color(0, 0, 0, 0.4), 1.0)
			if h > 14.0 and _h(key, n, 96) < 0.45 and top[0].distance_to(top[2 % n]) > 24.0:
				_extrude(_roof_box(tc + Vector2(0, z0 + h), key), z0 + h, 5.0 + _h(key, 2, 97) * 7.0, 1.0, fill, Color(SLATE_LIGHT, 0.5), 0.0, key + 7)
		else:
			_poly(top, fill.lerp(FACE_LIGHT, 0.25))
		for k in n:
			_ink_line(top[k], top[(k + 1) % n], ink)
	var verticals: Array = visible_v.keys()
	if _slate() and n > 4 and verticals.size() > 3:
		# Painted slate: a round tower keeps only its silhouette and front edge, so the
		# wall reads as one smooth shaded mass.
		verticals.sort_custom(func(k1: int, k2: int) -> bool: return bot[k1].x < bot[k2].x)
		var front: int = verticals[0]
		for k in verticals:
			if bot[k].y > bot[front].y:
				front = k
		verticals = [verticals[0], verticals[verticals.size() - 1], front]
	for k in verticals:
		# Verticals at the silhouette and the front corners.
		_ink_line(bot[k], top[k], ink, 1.7, true)
	return top


## True while walls are painted slate (textures 9-12; the HQs keep their own look).
func _slate() -> bool:
	return face_texture in [9, 10, 11, 12] and not _drawing_hq


## The wall's slate: plain (9), dark (10), or leaning toward the building's `ink` (11, 12).
func _slate_tone(ink: Color) -> Color:
	if face_texture >= 11:
		return SLATE_TONES[0].lerp(Color(ink, 1.0), SLATE_TINT[face_texture - 11])
	return SLATE_TONES[0 if face_texture == 9 else 1]


## A small rooftop box (plant room, vent housing) about the roof's centre (`ground`: that
## centre dropped to street level), returned as a footprint for _extrude.
func _roof_box(ground: Vector2, key: int) -> PackedVector2Array:
	var g := _grid_of(ground)
	var w := 0.12 + _h(key, 3, 98) * 0.1
	var off := Vector2(_h(key, 4, 98) - 0.5, _h(key, 5, 98) - 0.5) * 0.2
	return _rect_pts(g.x - w + off.x, g.y - w + off.y, g.x + w + off.x, g.y + w + off.y)


## Painted-slate detail on a wall a-b (bottom) / d-c (top), in face space (u across,
## v up): ledges between storey groups (a light lip over a dark shadow), and in each
## band a recessed panel, vertical ribs or a vent grille. `light` 0-1 is how much the
## face is lit. Straight walls only get the full set.
func _greeble_face(a: Vector2, b: Vector2, c: Vector2, d: Vector2, light: float, key: int, straight: bool) -> void:
	var wpx := a.distance_to(b)
	var hpx := a.distance_to(d)
	if wpx < 6.0 or hpx < 8.0:
		return
	var hi := Color(SLATE_LIGHT, 0.3 + light * 0.4)
	var lo := Color(0, 0, 0, 0.6)
	var at := func(u: float, v: float) -> Vector2: return a.lerp(b, u).lerp(d.lerp(c, u), v)
	# Top lip: a bright bevel just under the roof edge.
	_hair(at.call(0.0, 1.0 - 2.0 / hpx), at.call(1.0, 1.0 - 2.0 / hpx), Color(SLATE_LIGHT, 0.25 + light * 0.35), 1.2)
	if not straight:
		return
	var y := 0.0
	var band := 0
	while y < hpx - 8.0:
		var bh := 14.0 + _h(key, band, 100) * 26.0
		var y1 := minf(hpx - 4.0, y + bh)
		var v0 := (y + 2.0) / hpx
		var v1 := (y1 - 2.0) / hpx
		match int(_h(key, band, 101) * 6.0):
			0, 1:
				# Recessed panel: darker inset, shadow along its top, lit lip along its foot.
				var u0 := 0.1 + _h(key, band, 102) * 0.08
				var u1 := 0.9 - _h(key, band, 103) * 0.08
				var shade := Color(0, 0, 0, 0.32)
				_quad(at.call(u0, v0), at.call(u1, v0), at.call(u1, v1), at.call(u0, v1), shade, shade, shade, shade)
				_hair(at.call(u0, v1), at.call(u1, v1), lo, 1.1)
				_hair(at.call(u0, v0), at.call(u1, v0), hi, 1.0)
				_hair(at.call(u1, v0), at.call(u1, v1), Color(hi, hi.a * 0.6), 0.8)
			2:
				# Vertical ribs.
				var ribs := maxi(2, int(wpx / 9.0))
				for q in ribs:
					var u := (q + 0.5) / ribs
					_hair(at.call(u, v0), at.call(u, v1), hi, 1.0)
					_hair(at.call(u + 1.4 / wpx, v0), at.call(u + 1.4 / wpx, v1), Color(0, 0, 0, 0.35), 1.0)
			3:
				# Vent grille: a small block of slats.
				var gu := 0.2 + _h(key, band, 104) * 0.4
				var gw := minf(0.35, 22.0 / wpx)
				var slats := maxi(2, int((y1 - y) / 3.5))
				var box := Color(0, 0, 0, 0.3)
				_quad(at.call(gu, v0), at.call(gu + gw, v0), at.call(gu + gw, v1), at.call(gu, v1), box, box, box, box)
				for q in slats:
					var v := lerpf(v0, v1, (q + 0.5) / slats)
					_hair(at.call(gu, v), at.call(gu + gw, v), hi, 0.8)
			4:
				# Light slots: a few tall amber strips glowing out of the wall.
				var slots := clampi(int(wpx / 14.0), 1, 4)
				var amber := Color(_inks[0], 0.55 + light * 0.3)
				for q in slots:
					var u := (q + 0.5) / slots + (_h(key, band * 7 + q, 105) - 0.5) * 0.08
					var sw := 1.6 / wpx
					_quad(at.call(u - sw, v0 + 0.02), at.call(u + sw, v0 + 0.02), at.call(u + sw, v1 - 0.02), at.call(u - sw, v1 - 0.02), amber, amber, amber, amber)
		# Ledge over the band: lit lip, shadow under it.
		if y1 < hpx - 6.0:
			var vl := y1 / hpx
			_hair(at.call(0.0, vl), at.call(1.0, vl), Color(SLATE_LIGHT, 0.2 + light * 0.35), 1.2)
			_hair(at.call(0.0, vl - 1.6 / hpx), at.call(1.0, vl - 1.6 / hpx), lo, 1.2)
		y = y1
		band += 1


## Wall texture on the face a-b (bottom) / d-c (top), under the windows.
func _texture_face(a: Vector2, b: Vector2, c: Vector2, d: Vector2, shaded: bool, key: int) -> void:
	var wpx := a.distance_to(b)
	var hpx := a.distance_to(d)
	if wpx < 3.0 or hpx < 3.0:
		return
	var tone := Color("#8A97C8")
	match 2 if face_texture >= 7 else face_texture:
		1:
			# Panel seams: a floor line every two storeys, a joint every ~24 px.
			var rows := int(hpx / 16.0)
			for r in range(1, rows + 1):
				var v := (r * 16.0 - 1.5) / hpx
				_hair(a.lerp(d, v), b.lerp(c, v), Color(tone, 0.4 if r % 3 else 0.65), 1.0)
			var cols := int(wpx / 24.0)
			for q in range(1, cols + 1):
				var u := float(q) / (cols + 1)
				_hair(a.lerp(b, u), d.lerp(c, u), Color(tone, 0.32), 0.9)
		2:
			# Pen hatching at 45 degrees in dark ink: close on the shaded side, open on the
			# lit side.
			var gap := 3.5 if shaded else 5.0
			var rise := hpx / wpx
			var u0 := -rise
			# ANIM-R1 M15: a bounded count of hatch lines (a face measured huge never loops).
			if not is_finite(rise) or gap / wpx < HATCH_STEP_MIN:
				return
			while u0 < 1.0:
				var v_lo := maxf(0.0, -u0 / rise)
				var v_hi := minf(1.0, (1.0 - u0) / rise)
				if v_hi > v_lo:
					var p0 := a.lerp(b, u0 + rise * v_lo).lerp(d.lerp(c, u0 + rise * v_lo), v_lo)
					var p1 := a.lerp(b, u0 + rise * v_hi).lerp(d.lerp(c, u0 + rise * v_hi), v_hi)
					_hair(p0, p1, Color(0.01, 0.01, 0.02, 0.7 if shaded else 0.55), 1.1)
				u0 += gap / wpx
		3:
			# Grime: specks gathering toward the street, lighter and darker.
			var n := mini(420, int(wpx * hpx / 22.0))
			for q in n:
				var u := _h(key, q, 90)
				var v := pow(_h(key, q, 91), 2.2)
				var p := a.lerp(b, u).lerp(d.lerp(c, u), v)
				var sc := Color(tone, 0.55) if q % 3 else Color(0, 0, 0, 0.55)
				var s := 0.7 + _h(q, key, 92) * 1.1
				_quad(p + Vector2(-s, 0), p + Vector2(0, -s), p + Vector2(s, 0), p + Vector2(0, s), sc, sc, sc, sc)


## A plain straight hairline (one quad), for dense texture work.
func _hair(a: Vector2, b: Vector2, col: Color, width: float) -> void:
	var n := (b - a).orthogonal().normalized() * width * 0.5
	_quad(a - n, b - n, b + n, a + n, col, col, col, col)


func _windows(a: Vector2, b: Vector2, h: float, lit: float, key: int, bright: bool) -> void:
	var cols_n := maxi(1, int(a.distance_to(b) / 11.0))
	var rows := int((h - 6.0) / 8.0)
	var step := (b - a) / cols_n
	for ci in cols_n:
		for r in rows:
			var roll := _h(key, ci, r)
			if roll > lit:
				continue
			var o := a + step * (ci + 0.3) + Vector2(0, -5.0 - r * 8.0)
			var w := step * 0.4
			var wc: Color
			var t := roll / maxf(lit, 0.001)
			if t < 0.4:
				wc = Color(_inks[0], 0.75)
			elif t < 0.62:
				wc = Color(_inks[3], 0.7)
			elif t < 0.78:
				wc = Color(_terr_col if _terr != &"" else _inks[4], 0.75)
			elif t < 0.9:
				wc = Color(_inks[2], 0.7)
			else:
				wc = Color(_inks[1], 0.75)
			if not bright:
				wc = wc.darkened(0.3)
			_quad(o, o + w, o + w + Vector2(0, -3.2), o + Vector2(0, -3.2), wc, wc, wc, wc)
			if _h(key, ci * 64 + r, 110) < LIGHT_PICK:
				# A blinking light for the live layer (the baked window stays lit).
				_lights.append({"a": o, "w": w, "color": Color(wc, 1.0), "phase": _h(key, ci * 64 + r, 111),
					"period": LIGHT_PERIOD_MIN + _h(key, ci * 64 + r, 112) * LIGHT_PERIOD_SPREAD})


# --- Lots ---------------------------------------------------------------------------------

func _street(i: int, j: int, along_i: bool, along_j: bool) -> void:
	var p := _rect_pts(i, j, i + 1, j + 1)
	_quad(p[0], p[1], p[2], p[3], STREET, STREET, STREET, STREET)
	if along_i and along_j:
		return  # crossings stay dark; the strokes overshoot into them
	var traffic := _traffic(i, j, along_i)
	# Streets keep the original full-strength neon (only the buildings take the paler
	# palette), so the street grid reads over the city.
	var col := Palette.NET_CYAN if net_mode and _h(i, j, 62) < 0.5 else _street_ink(i if along_i else 0, j if along_j else 0)
	var a := _iso(i + 0.5, j) if along_i else _iso(i, j + 0.5)
	var b := _iso(i + 0.5, j + 1) if along_i else _iso(i + 1, j + 0.5)
	var nn := (b - a).orthogonal().normalized()
	var dir := (b - a).normalized()
	if traffic >= SPARK_TRAFFIC and _h(i, j, 63) < SPARK_PICK:
		# A traffic spark for the live layer, sliding along this lot of the street.
		var lane_off := nn * (_h(i, j, 64) - 0.5) * 6.0
		var fwd := _h(i if along_i else 0, 0 if along_i else j, 66) < 0.5
		_trails.append({"a": (a if fwd else b) + lane_off, "b": (b if fwd else a) + lane_off, "color": col, "phase": _h(i, j, 65), "width": 2.0, "traffic": traffic})
	# Fine-tip marker: the street's width is built from many skinny strokes laid side by
	# side, each a little crooked and overlapping its neighbours. Busy streets get more
	# strokes (up to ~12) and so read wider; quiet ones 2-3.
	var strokes := 7 + int(traffic * 23.0)
	var half := 1.5 + strokes * 0.42
	var g := Color(col, 0.05 + traffic * 0.08)
	_quad(a - nn * (half + 3.0), b - nn * (half + 3.0), b + nn * (half + 3.0), a + nn * (half + 3.0), g, g, g, g)
	# Each stroke keeps its lane along the whole street (keyed by the street, not the
	# lot) so it reads as one long pen line; per-lot it only wanders a little.
	var street_key := i if along_i else j
	for k in strokes:
		var t := (float(k) + 0.5) / strokes * 2.0 - 1.0
		var lane := t * half + (_h(street_key, k, 81) - 0.5) * 1.8
		var w0 := (_h(i, j * 7 + k, 82) - 0.5) * 0.9
		var w1 := (_h(i, j * 7 + k + 1, 82) - 0.5) * 0.9
		var alpha := 0.45 + 0.4 * _h(street_key + k, 3, 85) + traffic * 0.15
		_ink_line(a + nn * (lane + w0) - dir * 2.0, b + nn * (lane + w1) + dir * 2.0, Color(col, alpha), 0.8 + _h(k, street_key, 86) * 0.6, false)


func _plaza(i: int, j: int) -> void:
	var p := _rect_pts(i, j, i + 1, j + 1)
	var col := GROUND.lerp(_terr_col, 0.06)
	_quad(p[0], p[1], p[2], p[3], col, col, col, col)


## Merged cells inside a block: lots pair up in 2x2 quadrants (when the quadrant fits
## inside the block) as one 2x2, two slabs, or singles. Returns the cell of lot (i, j).
func _cell_of(i: int, j: int) -> Rect2i:
	var li: int = _local_i.get(i, 0)
	var lj: int = _local_j.get(j, 0)
	var qi := i - li % 2
	var qj := j - lj % 2
	var wide := not _street_i.has(qi + 1) and not _street_i.has(qi)
	var deep := not _street_j.has(qj + 1) and not _street_j.has(qj)
	var mode := int(_h(qi, qj, 30) * 6.0)
	# Merged buildings never straddle a fist road.
	if mode <= 2 and _fist_box.has_point(_iso(qi + 1.0, qj + 1.0)):
		for di in 2:
			for dj in 2:
				if _fist_dist(qi + di, qj + dj) < FIST_CLEAR:
					return Rect2i(i, j, 1, 1)
	if mode == 0 and wide and deep:
		return Rect2i(qi, qj, 2, 2)
	if mode == 1 and wide:
		return Rect2i(qi, j, 2, 1)
	if mode == 2 and deep:
		return Rect2i(i, qj, 1, 2)
	return Rect2i(i, j, 1, 1)


func _lot(i: int, j: int) -> void:
	if _fist_dist(i, j) < FIST_CLEAR:
		return  # a fist road runs here
	var cell := _cell_of(i, j)
	# A merged building is drawn once, from its front lot (correct depth order).
	if i != cell.end.x - 1 or j != cell.end.y - 1:
		return
	_building(cell)


func _pick_shape(ci: int, cj: int) -> int:
	var mix: Array = _profile["mix"]
	var owner := _terr
	# Border blend: near the dividing line some buildings take the neighbour's style.
	if _border > 0.0 and _h(ci, cj, 41) < _border * 0.5:
		owner = _terr_next
		mix = DISTRICTS.get(owner, DISTRICTS[&""])["mix"]
	if cultures.has(owner):
		mix = CULTURES.get(cultures[owner], mix)
	var total := 0
	for w in mix:
		total += int(w)
	var roll := _h(ci, cj, 40 + int(_profile.get("seed", 0))) * total
	for k in mix.size():
		roll -= int(mix[k])
		if roll < 0.0:
			return k
	return Shape.BOX


func _building(cell: Rect2i) -> void:
	var ci := cell.position.x
	var cj := cell.position.y
	var big := cell.size.x * cell.size.y
	var district_h := _h(floori(ci / float(STREET_EVERY)), floori(cj / float(STREET_EVERY)), 9)
	var r := _h(ci, cj, 2)
	var hs: float = _profile["height"]
	var h := (8.0 + pow(r, 2.7) * 100.0 + district_h * 28.0) * hs * (1.0 + 0.12 * (big - 1))
	if r > 0.965:
		h += 90.0 * hs
	# Low-rise around each HQ: its busy streets and the landmark read clearly.
	h *= lerpf(0.3, 1.0, clampf((_hq_distance(ci, cj) - 6.0) / 7.0, 0.0, 1.0))
	var fill := FILLS[int(_h(ci, cj, 5) * FILLS.size()) % FILLS.size()]
	var ink := _ink(ci, cj)
	var lit := 0.12 + district_h * 0.22
	var inset := 0.1 + _h(ci, cj, 1) * 0.14
	var x0 := ci + inset
	var y0 := cj + inset
	var x1 := cell.end.x - inset
	var y1 := cell.end.y - inset
	# Off the grid: nudge the footprint and turn some buildings a little.
	var jx := (_h(ci, cj, 15) - 0.5) * inset * 1.4
	var jy := (_h(ci, cj, 16) - 0.5) * inset * 1.4
	x0 += jx
	x1 += jx
	y0 += jy
	y1 += jy
	var cx := (x0 + x1) * 0.5
	var cy := (y0 + y1) * 0.5
	var half := minf(x1 - x0, y1 - y0) * 0.5
	var turn := (_h(ci, cj, 17) - 0.5) * 0.7 if _h(ci, cj, 18) < 0.45 else 0.0
	var shape := _pick_shape(ci, cj)
	var key := ci * 97 + cj
	var roof: PackedVector2Array
	match shape:
		Shape.STEPPED:
			var h1 := h * 0.5
			_extrude(_turned(turn, x0, y0, x1, y1), 0.0, h1, 1.0, fill, ink, lit, key)
			var k := 0.14 + _h(ci, cj, 6) * 0.08
			roof = _extrude(_turned(turn, x0 + k, y0 + k, x1 - k, y1 - k), h1, h * 0.35, 1.0, fill, ink, lit, key + 1)
			if big > 1 or h > 60.0:
				roof = _extrude(_turned(turn, x0 + k * 2.0, y0 + k * 2.0, x1 - k * 2.0, y1 - k * 2.0), h1 + h * 0.35, h * 0.3 + 10.0, 1.0, fill, ink, lit, key + 2)
		Shape.CYLINDER:
			roof = _extrude(_ngon(cx, cy, half, 8, PI / 8.0), 0.0, h + 10.0, 1.0, fill, ink, lit, key)
			if _h(ci, cj, 7) < 0.5:
				_extrude(_ngon(cx, cy, half * 0.6, 8, PI / 8.0), h + 10.0, 8.0, 0.55, fill, ink, 0.0, key + 1)
		Shape.HEX:
			roof = _extrude(_ngon(cx, cy, half, 6, _h(ci, cj, 8) * PI + turn), 0.0, h, 1.0, fill, ink, lit, key)
		Shape.TAPER:
			roof = _extrude(_turned(turn, x0, y0, x1, y1), 0.0, h * 1.1 + 20.0, 0.5, fill, ink, lit, key)
		Shape.NEEDLE:
			var nh := h * 1.3 + 40.0
			roof = _extrude(_ngon(cx, cy, half * 0.55, 6, 0.3), 0.0, nh, 1.0, fill, ink, lit, key)
			var tip := _iso(cx, cy) + Vector2(0, -nh)
			_ink_line(tip, tip + Vector2(0, -26), ink, 1.0, false)
			_beacons.append({"pos": tip + Vector2(0, -27), "color": ink, "phase": _h(ci, cj, 8)})
		Shape.WAREHOUSE:
			var wh := 9.0 + r * 16.0
			roof = _extrude(_turned(turn, x0, y0, x1, y1), 0.0, wh, 1.0, fill, ink, lit * 0.5, key)
			for k in 3:
				var t := (k + 1) / 4.0
				_ink_line(_iso(lerpf(x0, x1, t), y0) + Vector2(0, -wh), _iso(lerpf(x0, x1, t), y1) + Vector2(0, -wh), Color(ink, 0.35), 1.0, false)
		Shape.PYRAMID:
			roof = _extrude(_rect_pts(x0, y0, x1, y1), 0.0, 30.0 + h * 0.6, 0.03, fill, ink, lit, key)
		Shape.OBELISK:
			var oh := h * 1.1 + 40.0
			var k := (x1 - x0) * 0.36
			_extrude(_rect_pts(cx - k, cy - k, cx + k, cy + k), 0.0, oh, 0.7, fill, ink, lit, key)
			roof = _extrude(_rect_pts(cx - k * 0.7, cy - k * 0.7, cx + k * 0.7, cy + k * 0.7), oh, 12.0, 0.03, fill, ink, 0.0, key + 1)
		Shape.MASTABA:
			roof = _extrude(_rect_pts(x0, y0, x1, y1), 0.0, 12.0 + r * 14.0, 0.82, fill, ink, lit * 0.5, key)
		Shape.PAGODA:
			var tiers := 3 + int(_h(ci, cj, 50) * 2.0)
			var z := 0.0
			var th := maxf(14.0, h / tiers)
			for t in tiers:
				var k := (x1 - x0) * (0.1 + t * 0.07)
				_extrude(_rect_pts(x0 + k, y0 + k, x1 - k, y1 - k), z, th * 0.7, 1.0, fill, ink, lit, key + t * 3)
				z += th * 0.7
				var e := (x1 - x0) * (0.02 + t * 0.07)
				roof = _extrude(_rect_pts(x0 + e - 0.08, y0 + e - 0.08, x1 - e + 0.08, y1 - e + 0.08), z, th * 0.3, 0.55, fill.lerp(FACE_LIGHT, 0.2), ink, 0.0, key + t * 3 + 1)
				z += th * 0.3
		Shape.GABLE:
			var wall := 14.0 + h * 0.45
			_extrude(_rect_pts(x0, y0, x1, y1), 0.0, wall, 1.0, fill, ink, lit, key)
			roof = _gable(x0, y0, x1, y1, wall, 10.0 + (y1 - y0) * 12.0, fill, ink)
		Shape.CLOCKTOWER:
			var ch := h * 1.2 + 60.0
			var k := (x1 - x0) * 0.25
			_extrude(_rect_pts(x0 + k, y0 + k, x1 - k, y1 - k), 0.0, ch, 1.0, fill, ink, lit, key)
			roof = _extrude(_rect_pts(x0 + k, y0 + k, x1 - k, y1 - k), ch, 24.0, 0.03, fill, ink, 0.0, key + 1)
			var face := _iso(x1 - k, (y0 + y1) * 0.5) + Vector2(-TILE_A * 0.25, -ch + 16)
			var fc := Color(_inks[0], 0.9)
			for q in 12:
				var a0 := TAU * q / 12.0
				var a1 := TAU * (q + 1) / 12.0
				_ink_line(face + Vector2(cos(a0) * 7, sin(a0) * 8), face + Vector2(cos(a1) * 7, sin(a1) * 8), fc, 1.2, false)
			_ink_line(face, face + Vector2(0, -6), fc, 1.2, false)
			_ink_line(face, face + Vector2(4, 1), fc, 1.2, false)
		Shape.DOME:
			var dh := 12.0 + h * 0.5
			roof = _extrude(_ngon(cx, cy, half, 10, 0.1), 0.0, dh, 1.0, fill, ink, lit, key)
			_dome(_iso(cx, cy) + Vector2(0, -dh), half * TILE_A, fill, ink)
		Shape.MINARET:
			var mh := h * 1.3 + 70.0
			var k := half * 0.4
			_extrude(_ngon(cx, cy, k, 8, 0.2), 0.0, mh, 1.0, fill, ink, lit, key)
			_extrude(_ngon(cx, cy, k * 1.6, 8, 0.2), mh * 0.72, 4.0, 1.0, fill, ink, 0.0, key + 1)
			roof = _extrude(_ngon(cx, cy, k, 8, 0.2), mh, 16.0, 0.05, fill, ink, 0.0, key + 2)
			_beacons.append({"pos": _iso(cx, cy) + Vector2(0, -mh - 18), "color": ink, "phase": _h(ci, cj, 8)})
		Shape.STEP_TEMPLE:
			var steps := 4
			var sh := maxf(10.0, (h * 0.8 + 30.0) / (steps + 1))
			for t in steps:
				var k := (x1 - x0) * t * 0.09
				roof = _extrude(_rect_pts(x0 + k, y0 + k, x1 - k, y1 - k), t * sh, sh, 1.0, fill, ink, 0.0, key + t)
			var k2 := (x1 - x0) * 0.33
			roof = _extrude(_rect_pts(x0 + k2, y0 + k2, x1 - k2, y1 - k2), steps * sh, sh * 1.1, 1.0, fill.lerp(FACE_LIGHT, 0.2), ink, lit, key + 9)
			# Stair up the front face.
			var st_a := _iso((x0 + x1) * 0.5, y1)
			_ink_line(st_a + Vector2(-5, 0), st_a + Vector2(-5, -steps * sh) + Vector2(0, (x1 - x0) * TILE_B * 0.3), Color(ink, 0.7), 1.0, false)
			_ink_line(st_a + Vector2(5, 0), st_a + Vector2(5, -steps * sh) + Vector2(0, (x1 - x0) * TILE_B * 0.3), Color(ink, 0.7), 1.0, false)
		_:
			roof = _extrude(_turned(turn, x0, y0, x1, y1), 0.0, h, 1.0, fill, ink, lit, key)
	# Roof clutter: antennae, a lit sign, a beacon on the tall ones.
	var rc := Vector2.ZERO
	for q in roof:
		rc += q
	rc /= maxf(1.0, roof.size())
	var rec := {"roof": roof, "base": _iso(cx, cy), "shape": shape, "height": h, "cell": cell}
	for li in range(cell.position.x, cell.end.x):
		for lj in range(cell.position.y, cell.end.y):
			_roofs[Vector2i(li, lj)] = rec
	var clutter := _h(ci, cj, 14)
	if clutter < 0.18 and h > 30.0:
		_ink_line(rc, rc + Vector2(0, -12.0 - clutter * 60.0), Color(ink, 0.8), 1.0, false)
	elif clutter > 0.86 and roof.size() >= 4:
		var sc := Color(_ink(ci + 5, cj), 0.85)
		_quad(rc + Vector2(-6, -2), rc + Vector2(6, -2), rc + Vector2(6, -9), rc + Vector2(-6, -9), sc, sc, sc, sc)
	if r > 0.92:
		_beacons.append({"pos": rc + Vector2(0, -3), "color": ink, "phase": _h(ci, cj, 8)})


## A gabled roof on a wall of height `z`: ridge along i, slopes and gable ends; returns
## the ridge-and-eaves outline as the roof points.
func _gable(x0: float, y0: float, x1: float, y1: float, z: float, rh: float, fill: Color, ink: Color) -> PackedVector2Array:
	var up := Vector2(0, -z)
	var cy := (y0 + y1) * 0.5
	var b0 := _iso(x0, y0) + up
	var b1 := _iso(x1, y0) + up
	var f0 := _iso(x0, y1) + up
	var f1 := _iso(x1, y1) + up
	var ra := _iso(x0, cy) + up + Vector2(0, -rh)
	var rb := _iso(x1, cy) + up + Vector2(0, -rh)
	var back := fill.lerp(FACE_LIGHT, 0.1)
	var front := fill.lerp(FACE_LIGHT, 0.3)
	_quad(b0, b1, rb, ra, back, back, back, back)
	_tri(b0, f0, ra, back, back, back)
	_quad(f0, f1, rb, ra, front, front, front, front)
	_tri(b1, f1, rb, fill.darkened(0.2), fill.darkened(0.2), fill.darkened(0.2))
	_ink_line(ra, rb, ink)
	_ink_line(f0, f1, ink)
	_ink_line(f0, ra, ink)
	_ink_line(f1, rb, ink)
	_ink_line(b1, rb, Color(ink, 0.7), 1.1, false)
	return PackedVector2Array([ra, rb, f1, f0])


## A dome over a drum top centred at `c`, screen radius `rad`.
func _dome(c: Vector2, rad: float, fill: Color, ink: Color) -> void:
	var pts := PackedVector2Array()
	for k in 13:
		var a := PI + PI * k / 12.0
		pts.append(c + Vector2(cos(a) * rad, sin(a) * rad * 1.1))
	var body := pts.duplicate()
	body.append(c + Vector2(rad, 0))
	_poly(body, fill.lerp(FACE_LIGHT, 0.3))
	for k in 12:
		_ink_line(pts[k], pts[k + 1], ink, 1.3, k % 3 == 0)
	_ink_line(pts[6], pts[6] + Vector2(0, -10), ink, 1.1, false)
	_ink_line(c + Vector2(0, -rad * 1.1), c + Vector2(0, -rad * 0.2), Color(ink, 0.4), 1.0, false)


# --- Corporation HQs ----------------------------------------------------------------------

## The district's landmark, one per corporation, standing on its plaza.
func _hq(corp: StringName, rect: Rect2i) -> void:
	var k := HQ_SCALE
	var cx := rect.position.x + HQ_LOTS * 0.5
	var cy := rect.position.y + HQ_LOTS * 0.5
	var col := _pale(Palette.corp_color(corp))
	var dark := FILLS[0]
	var mid := FILLS[1]
	var grey := FILLS[2]
	var base := _iso(cx, cy)
	# Plaza: two rings, spokes and corner lamps.
	for rr in [2.3 * k, 2.0 * k]:
		var ring := _ngon(cx, cy, rr, 32)
		for m in ring.size():
			_ink_line(ring[m], ring[(m + 1) % ring.size()], Color(col, 0.45), 1.0, false)
	for m in 8:
		var a := TAU * m / 8.0
		_ink_line(_iso(cx + cos(a) * 2.0 * k, cy + sin(a) * 2.0 * k), _iso(cx + cos(a) * 2.3 * k, cy + sin(a) * 2.3 * k), Color(col, 0.6), 1.0, false)
		if m % 2 == 0:
			var lamp := _iso(cx + cos(a + 0.4) * 2.45 * k, cy + sin(a + 0.4) * 2.45 * k)
			_ink_line(lamp, lamp + Vector2(0, -18), Color(col, 0.8), 1.0, false)
			_beacons.append({"pos": lamp + Vector2(0, -20), "color": col, "phase": m * 0.13})
	match String(cultures.get(corp, "")):
		"chinese":
			_hq_pagoda(cx, cy, k, col, base)
			_sign(base + Vector2(-50, -330.0 * k), String(corp).to_upper(), col)
			return
		"egyptian":
			_hq_pyramid(cx, cy, k, col, base)
			_sign(base + Vector2(-46, -250.0 * k), String(corp).to_upper(), col)
			return
		"english":
			_hq_big_ben(cx, cy, k, col, base)
			_sign(base + Vector2(40.0 * k, -200.0 * k), String(corp).to_upper(), col)
			return
	match corp:
		&"solace":
			# The Double Helix: a podium with pods, and on it the tower as a DNA strand, two
			# helices wound round each other and joined by bridges (the base pairs).
			_extrude(_ngon(cx, cy, 1.9 * k, 8, PI / 8.0), 0.0, 30.0 * k, 1.0, grey, col, 0.35, 900)
			_hq_dna(cx, cy, k, col, 30.0 * k, 340.0 * k)
			_sign(base + Vector2(-40, -395.0 * k), "SOLACE", col)
		&"meridian":
			# Freight Ziggurat: terraces with loading bays, container yards, a tower with a
			# helipad and a big crane swinging a container.
			_extrude(_rect_pts(cx - 2.0 * k, cy - 2.0 * k, cx + 2.0 * k, cy + 2.0 * k), 0.0, 44.0 * k, 1.0, mid, col, 0.25, 910)
			for m in 5:
				var bay := _iso(cx - 2.0 * k + (m + 0.6) * 0.75 * k, cy + 2.0 * k)
				_quad(bay, bay + Vector2(20, -10), bay + Vector2(20, -38), bay + Vector2(0, -28), Color(_inks[0], 0.25), Color(_inks[0], 0.25), Color(_inks[0], 0.25), Color(_inks[0], 0.25))
				_ink_line(bay + Vector2(0, -28), bay + Vector2(20, -38), _inks[0], 1.2, false)
			_extrude(_rect_pts(cx - 1.4 * k, cy - 1.4 * k, cx + 1.4 * k, cy + 1.4 * k), 44.0 * k, 44.0 * k, 1.0, dark, col, 0.25, 911)
			for row in 2:
				for m in 6:
					var bx := cx - 1.3 * k + m * 0.43 * k
					var cc: Color = [_inks[0], _inks[3], _inks[2], col, _inks[1], _inks[4]][(m + row) % 6]
					_extrude(_rect_pts(bx, cy + 1.45 * k + row * 0.25 * k, bx + 0.36 * k, cy + 1.66 * k + row * 0.25 * k), 44.0 * k, (10.0 + ((m + row) % 3) * 8.0) * k, 1.0, dark, cc, 0.0, 913 + m + row * 6)
			_extrude(_rect_pts(cx - 0.7 * k, cy - 0.7 * k, cx + 0.7 * k, cy + 0.7 * k), 88.0 * k, 110.0 * k, 1.0, mid, col, 0.35, 912)
			var pad := _ngon(cx, cy, 0.5 * k, 24)
			for q in pad.size():
				_ink_line(pad[q] + Vector2(0, -198.0 * k), pad[(q + 1) % pad.size()] + Vector2(0, -198.0 * k), _inks[0], 1.2, false)
			var hc := base + Vector2(0, -198.0 * k)
			_ink_line(hc + Vector2(-8, -6), hc + Vector2(-8, 6), _inks[0], 1.6, false)
			_ink_line(hc + Vector2(8, -6), hc + Vector2(8, 6), _inks[0], 1.6, false)
			_ink_line(hc + Vector2(-8, 0), hc + Vector2(8, 0), _inks[0], 1.6, false)
			var mast := _iso(cx + 0.7 * k, cy - 0.7 * k) + Vector2(0, -198.0 * k)
			_ink_line(mast, mast + Vector2(0, -40.0 * k), col, 2.0)
			for q in 4:
				_ink_line(mast + Vector2(-4, -q * 10.0 * k), mast + Vector2(4, -(q + 1) * 10.0 * k), Color(col, 0.6), 1.0, false)
			var jib := mast + Vector2(-150.0 * k, -30.0 * k)
			_ink_line(mast + Vector2(0, -40.0 * k), jib, col, 2.0)
			_ink_line(mast + Vector2(0, -40.0 * k), mast + Vector2(40.0 * k, -20.0 * k), col, 1.6)
			for q in 6:
				var t := (q + 1) / 7.0
				_ink_line((mast + Vector2(0, -40.0 * k)).lerp(jib, t), (mast + Vector2(0, -34.0 * k)).lerp(jib + Vector2(0, 6), t + 0.07), Color(col, 0.5), 1.0, false)
			_ink_line(jib, jib + Vector2(0, 50.0 * k), Color(col, 0.8), 1.0, false)
			var box := jib + Vector2(0, 50.0 * k)
			var bw := 12.0 * k
			_quad(box + Vector2(-bw, 0), box + Vector2(bw, 0), box + Vector2(bw, 14.0 * k), box + Vector2(-bw, 14.0 * k), dark, dark, dark, dark)
			for e in [[Vector2(-bw, 0), Vector2(bw, 0)], [Vector2(bw, 0), Vector2(bw, 14.0 * k)], [Vector2(bw, 14.0 * k), Vector2(-bw, 14.0 * k)], [Vector2(-bw, 14.0 * k), Vector2(-bw, 0)]]:
				_ink_line(box + e[0], box + e[1], _inks[0], 1.4, false)
			for q in 4:
				_ink_line(box + Vector2(-bw + (q + 1) * bw * 0.4, 2), box + Vector2(-bw + (q + 1) * bw * 0.4, 14.0 * k - 2), Color(_inks[0], 0.5), 1.0, false)
			_beacons.append({"pos": mast + Vector2(0, -42.0 * k), "color": col, "phase": 0.5})
			_sign(base + Vector2(-50, -262.0 * k), "MERIDIAN", col)
		&"halcyon":
			# Civic Pyramid: four tiers with colonnades and a grand stair, flanking obelisks,
			# banners and a floating halo.
			for m in [Vector2(-2.1, 2.1), Vector2(2.1, -2.1)]:
				var ox: float = cx + m.x * k
				var oy: float = cy + m.y * k
				_extrude(_rect_pts(ox - 0.18 * k, oy - 0.18 * k, ox + 0.18 * k, oy + 0.18 * k), 0.0, 90.0 * k, 0.7, dark, col, 0.0, 925)
				_extrude(_rect_pts(ox - 0.13 * k, oy - 0.13 * k, ox + 0.13 * k, oy + 0.13 * k), 90.0 * k, 10.0 * k, 0.03, dark, col, 0.0, 926)
			for t in 4:
				var r := (2.0 - t * 0.45) * k
				_extrude(_rect_pts(cx - r, cy - r, cx + r, cy + r), t * 38.0 * k, 38.0 * k, 1.0 if t < 3 else 0.2, mid if t % 2 == 0 else dark, col, 0.2, 920 + t)
				# Colonnade on the front faces.
				if t < 3:
					for q in 7:
						var f := float(q + 1) / 8.0
						var p0 := _iso(cx - r + 2.0 * r * f, cy + r) + Vector2(0, -t * 38.0 * k)
						_ink_line(p0 + Vector2(0, -4), p0 + Vector2(0, -34.0 * k), Color(col, 0.35), 1.0, false)
			# The grand stair up the front.
			var st0 := _iso(cx, cy + 2.0 * k)
			for q in 12:
				var y := -q * 12.0 * k
				var w := (18.0 - q * 0.9) * k
				_ink_line(st0 + Vector2(-w * 0.5, y), st0 + Vector2(w * 0.5, y - w * 0.25), Color(col, 0.7), 1.0, false)
			var apex := base + Vector2(0, -190.0 * k)
			var halo := PackedVector2Array()
			for q in 33:
				halo.append(apex + Vector2(cos(TAU * q / 32.0) * 46.0 * k, sin(TAU * q / 32.0) * 14.0 * k - 20.0 * k))
			for q in 32:
				_ink_line(halo[q], halo[q + 1], col, 1.8)
			for sx in [-1.0, 1.0]:
				var pole := base + Vector2(sx * 120.0 * k, -80.0 * k)
				_ink_line(pole, pole + Vector2(0, -60.0 * k), Color(col, 0.8), 1.2, false)
				var ban := PackedVector2Array([pole + Vector2(0, -60.0 * k), pole + Vector2(sx * 22.0 * k, -56.0 * k), pole + Vector2(sx * 20.0 * k, -30.0 * k), pole + Vector2(0, -34.0 * k)])
				_poly(ban, Color(col, 0.45))
			_ink_line(apex, apex + Vector2(0, -44.0 * k), Color(col, 0.8), 1.2, false)
			_beacons.append({"pos": apex + Vector2(0, -46.0 * k), "color": col, "phase": 0.7})
			_sign(base + Vector2(-46, -268.0 * k), "HALCYON", col)
		&"orbital":
			# Orbital Tether: a ring platform with docking arms, a needle with collars every
			# storey band, a counterweight and its tether beam into the sky.
			_extrude(_ngon(cx, cy, 2.0 * k, 12, PI / 12.0), 0.0, 22.0 * k, 1.0, mid, col, 0.2, 930)
			for m in 6:
				var a := TAU * m / 6.0
				var p0 := _iso(cx + cos(a) * 2.0 * k, cy + sin(a) * 2.0 * k) + Vector2(0, -22.0 * k)
				var p1 := _iso(cx + cos(a) * 2.6 * k, cy + sin(a) * 2.6 * k) + Vector2(0, -30.0 * k)
				_ink_line(p0, p1, col, 1.4)
				_beacons.append({"pos": p1, "color": col, "phase": m * 0.2})
			_extrude(_ngon(cx, cy, 0.6 * k, 6), 22.0 * k, 300.0 * k, 0.7, dark, col, 0.35, 931)
			for q in 5:
				var hh := (60.0 + q * 52.0) * k
				var rr := _ngon(cx, cy, (0.75 - q * 0.05) * k, 6)
				for m in rr.size():
					_ink_line(rr[m] + Vector2(0, -hh), rr[(m + 1) % rr.size()] + Vector2(0, -hh), col, 1.4)
			var tip := base + Vector2(0, -322.0 * k)
			_extrude(_ngon(cx, cy, 0.35 * k, 8), 322.0 * k, 14.0 * k, 1.0, grey, col, 0.0, 932)
			var beam := Color(col, 0.12)
			_quad(tip + Vector2(-9.0 * k, 0), tip + Vector2(9.0 * k, 0), Vector2(tip.x + 5.0 * k, -2000), Vector2(tip.x - 5.0 * k, -2000), beam, beam, Color(col, 0.0), Color(col, 0.0))
			_ink_line(tip, Vector2(tip.x, -2000), Color(col, 0.7), 1.4, false)
			_beacons.append({"pos": tip + Vector2(0, -16.0 * k), "color": col, "phase": 0.1})
			_sign(base + Vector2(30.0 * k, -160.0 * k), "ORBITAL", col)


## Chinese HQ: a seven-tier pagoda tower, every tier under a sweeping roof whose four
## corners turn up, a spire of rings on top.
func _hq_pagoda(cx: float, cy: float, k: float, col: Color, base: Vector2) -> void:
	_extrude(_rect_pts(cx - 1.9 * k, cy - 1.9 * k, cx + 1.9 * k, cy + 1.9 * k), 0.0, 14.0 * k, 1.0, FILLS[2], col, 0.2, 960)
	var z := 14.0 * k
	for t in 7:
		var r := (1.25 - t * 0.12) * k
		var body := (32.0 - t * 2.0) * k
		_extrude(_rect_pts(cx - r, cy - r, cx + r, cy + r), z, body, 1.0, FILLS[1] if t % 2 == 0 else FILLS[0], col, 0.35, 961 + t * 2)
		z += body
		z = _pagoda_roof(cx, cy, r * 1.45, r * 0.55, z, (12.0 - t * 0.8) * k, col)
	var tip := base + Vector2(0, -z)
	for q in 5:
		var rr := (7.0 - q) * k * 0.9
		_ink_line(tip + Vector2(-rr, -q * 7.0 * k), tip + Vector2(rr, -q * 7.0 * k), col, 1.4)
	_ink_line(tip, tip + Vector2(0, -48.0 * k), col, 1.8)
	_beacons.append({"pos": tip + Vector2(0, -50.0 * k), "color": col, "phase": 0.3})


## One pagoda roof from half-width `r0` (eaves) up to `r1` at the ridge; its four eave
## corners flick outward and up. Returns the height reached.
func _pagoda_roof(cx: float, cy: float, r0: float, r1: float, z: float, h: float, col: Color) -> float:
	_extrude(_rect_pts(cx - r0, cy - r0, cx + r0, cy + r0), z, h, r1 / r0, FILLS[0].lerp(col, 0.12), col, 0.0, 990)
	for q in [Vector2(-1, -1), Vector2(1, -1), Vector2(1, 1), Vector2(-1, 1)]:
		var c := _iso(cx + q.x * r0, cy + q.y * r0) + Vector2(0, -z)
		var out := (c - _iso(cx, cy) - Vector2(0, -z)).normalized()
		var tip := c + out * h * 0.9 + Vector2(0, -h * 0.9)
		var mid := c + out * h * 0.6 + Vector2(0, -h * 0.1)
		_ink_line(c, mid, col, 1.6, false)
		_ink_line(mid, tip, col, 1.6, false)
		_beacons.append({"pos": tip, "color": col, "phase": 0.05 * q.x + 0.1})
	return z + h


## Egyptian HQ: a large sloped (truncated pyramid) base, a ramp up its front flanked by
## obelisks, and a great pyramid standing on the base.
func _hq_pyramid(cx: float, cy: float, k: float, col: Color, base: Vector2) -> void:
	var half := 1.75 * k
	var bh := 52.0 * k
	var ts := 0.8
	_extrude(_rect_pts(cx - half, cy - half, cx + half, cy + half), 0.0, bh, ts, FILLS[1], col, 0.25, 970)
	# Coursed stone lines on the two visible slopes.
	for q in 5:
		var f := float(q + 1) / 6.0
		var hh := bh * f
		var rr := half * lerpf(1.0, ts, f)
		_ink_line(_iso(cx - rr, cy + rr) + Vector2(0, -hh), _iso(cx + rr, cy + rr) + Vector2(0, -hh), Color(col, 0.35), 1.0, false)
		_ink_line(_iso(cx + rr, cy - rr) + Vector2(0, -hh), _iso(cx + rr, cy + rr) + Vector2(0, -hh), Color(col, 0.25), 1.0, false)
	# The ramp: from the plaza in front up to the top edge of the base.
	var rw := 0.42 * k
	var g0 := _iso(cx - rw, cy + half + 0.9 * k)
	var g1 := _iso(cx + rw, cy + half + 0.9 * k)
	var t0 := _iso(cx - rw, cy + half * ts) + Vector2(0, -bh)
	var t1 := _iso(cx + rw, cy + half * ts) + Vector2(0, -bh)
	var ramp := FILLS[2].lerp(col, 0.15)
	_quad(g0, g1, t1, t0, ramp, ramp, ramp.lightened(0.1), ramp.lightened(0.1))
	_ink_line(g0, t0, col, 1.6)
	_ink_line(g1, t1, col, 1.6)
	for q in 9:
		var f := float(q + 1) / 10.0
		_ink_line(g0.lerp(t0, f), g1.lerp(t1, f), Color(col, 0.4), 1.0, false)
	for sx in [-1.0, 1.0]:
		var ox: float = cx + sx * (rw + 0.35 * k)
		var oy: float = cy + half + 0.75 * k
		_extrude(_rect_pts(ox - 0.14 * k, oy - 0.14 * k, ox + 0.14 * k, oy + 0.14 * k), 0.0, 80.0 * k, 0.65, FILLS[0], col, 0.0, 975)
		_extrude(_rect_pts(ox - 0.09 * k, oy - 0.09 * k, ox + 0.09 * k, oy + 0.09 * k), 80.0 * k, 9.0 * k, 0.03, FILLS[0], col, 0.0, 976)
		_beacons.append({"pos": _iso(ox, oy) + Vector2(0, -92.0 * k), "color": col, "phase": 0.4 + sx * 0.1})
	# The flat terrace on top of the base: a parapet rim and paving lines, so the pyramid
	# stands on level ground (slope, flat, slope).
	var tr := half * ts
	var rim := [_iso(cx - tr, cy - tr), _iso(cx + tr, cy - tr), _iso(cx + tr, cy + tr), _iso(cx - tr, cy + tr)]
	for q in 4:
		_ink_line(rim[q] + Vector2(0, -bh - 4.0 * k), rim[(q + 1) % 4] + Vector2(0, -bh - 4.0 * k), Color(col, 0.7), 1.2, false)
	var pr := tr * 0.66
	for q in 3:
		var f := lerpf(pr, tr, float(q + 1) / 4.0)
		_ink_line(_iso(cx - f, cy + f) + Vector2(0, -bh), _iso(cx + f, cy + f) + Vector2(0, -bh), Color(col, 0.3), 1.0, false)
		_ink_line(_iso(cx + f, cy - f) + Vector2(0, -bh), _iso(cx + f, cy + f) + Vector2(0, -bh), Color(col, 0.22), 1.0, false)
	# The great pyramid on the terrace, with a gilded cap.
	# Colonnades along the terrace's two front edges (either side of the ramp head).
	var gold := _pale(Palette.RESIST_GOLD)
	for side in 2:
		var cols_n := 9
		var prev_top := Vector2.INF
		for q in cols_n:
			var f := lerpf(-0.92, 0.92, float(q) / (cols_n - 1))
			if side == 0 and absf(f * tr) < rw * 1.3:
				prev_top = Vector2.INF
				continue
			var g := Vector2(cx + f * tr, cy + tr * 0.94) if side == 0 else Vector2(cx + tr * 0.94, cy + f * tr)
			var foot := _iso(g.x, g.y) + Vector2(0, -bh)
			var top := foot + Vector2(0, -16.0 * k)
			_ink_line(foot, top, Color(col, 0.85), 2.2, false)
			_hair(top + Vector2(-3, 0), top + Vector2(3, 0), gold, 1.4)
			if prev_top != Vector2.INF:
				_hair(prev_top + Vector2(0, -1.5), top + Vector2(0, -1.5), Color(gold, 0.8), 1.6)
			prev_top = top
	# Hieroglyph friezes: a band of little signs round the base's two visible slopes.
	_frieze(_iso(cx - half, cy + half), _iso(cx + half, cy + half), _iso(cx - tr, cy + tr) + Vector2(0, -bh), _iso(cx + tr, cy + tr) + Vector2(0, -bh), 0.42, 0.58, 26, 0.09, gold, 0)
	_frieze(_iso(cx + half, cy + half), _iso(cx + half, cy - half), _iso(cx + tr, cy + tr) + Vector2(0, -bh), _iso(cx + tr, cy - tr) + Vector2(0, -bh), 0.42, 0.58, 26, 0.0, gold, 1)
	# Braziers on the terrace corners.
	for cc in [Vector2(-1, 1), Vector2(1, 1), Vector2(1, -1)]:
		var bp := _iso(cx + cc.x * tr * 0.97, cy + cc.y * tr * 0.97) + Vector2(0, -bh)
		_ink_line(bp, bp + Vector2(0, -12.0 * k), Color(gold, 0.9), 1.6, false)
		_beacons.append({"pos": bp + Vector2(0, -14.0 * k), "color": Palette.CRT_AMBER, "phase": cc.x * 0.2 + cc.y * 0.1})
	# The great pyramid on the terrace: gentler slopes, stone courses, a gilded cap and
	# an entrance where the ramp arrives.
	var ph := 82.0 * k
	_extrude(_rect_pts(cx - pr, cy - pr, cx + pr, cy + pr), bh, ph, 0.12, FILLS[1].lerp(col, 0.06), col, 0.2, 977)
	for q in 7:
		var f := float(q + 1) / 8.0
		var hh := bh + ph * f
		var rr := pr * lerpf(1.0, 0.12, f)
		_hair(_iso(cx - rr, cy + rr) + Vector2(0, -hh), _iso(cx + rr, cy + rr) + Vector2(0, -hh), Color(col, 0.3), 1.0)
		_hair(_iso(cx + rr, cy - rr) + Vector2(0, -hh), _iso(cx + rr, cy + rr) + Vector2(0, -hh), Color(col, 0.22), 1.0)
	# The same gold frieze round the pyramid, above the doorway.
	var pt := pr * 0.12
	var ptop := bh + ph
	_frieze(_iso(cx - pr, cy + pr) + Vector2(0, -bh), _iso(cx + pr, cy + pr) + Vector2(0, -bh), _iso(cx - pt, cy + pt) + Vector2(0, -ptop), _iso(cx + pt, cy + pt) + Vector2(0, -ptop), 0.3, 0.42, 18, 0.0, gold, 2)
	_frieze(_iso(cx + pr, cy + pr) + Vector2(0, -bh), _iso(cx + pr, cy - pr) + Vector2(0, -bh), _iso(cx + pt, cy + pt) + Vector2(0, -ptop), _iso(cx + pt, cy - pt) + Vector2(0, -ptop), 0.3, 0.42, 18, 0.0, gold, 3)
	# Entrance: a dark doorway with a gold lintel on the front slope.
	var dw := 0.16 * k
	var d0 := _iso(cx - dw, cy + pr) + Vector2(0, -bh)
	var d1 := _iso(cx + dw, cy + pr) + Vector2(0, -bh)
	var dz := ph * 0.2
	var dr := pr * lerpf(1.0, 0.12, 0.2)
	var d2 := _iso(cx + dw * 0.7, cy + dr) + Vector2(0, -bh - dz)
	var d3 := _iso(cx - dw * 0.7, cy + dr) + Vector2(0, -bh - dz)
	_quad(d0, d1, d2, d3, FILLS[0], FILLS[0], FILLS[0], FILLS[0])
	_hair(d3 + Vector2(-4, 0), d2 + Vector2(4, 0), gold, 2.0)
	_hair(d0, d3, Color(col, 0.8), 1.2)
	_hair(d1, d2, Color(col, 0.8), 1.2)
	# The cap, and a gold seam up the pyramid's front edge.
	_hair(_iso(cx + pr, cy + pr) + Vector2(0, -bh), _iso(cx + pr * 0.12, cy + pr * 0.12) + Vector2(0, -bh - ph), Color(gold, 0.55), 1.4)
	_extrude(_rect_pts(cx - pr * 0.12, cy - pr * 0.12, cx + pr * 0.12, cy + pr * 0.12), bh + ph, 16.0 * k, 0.03, Palette.RESIST_GOLD.darkened(0.4), Palette.RESIST_GOLD, 0.0, 978)
	_beacons.append({"pos": base + Vector2(0, -(bh + ph + 20.0 * k)), "color": col, "phase": 0.7})


## Solace's tower: a DNA double helix from height z0 to z1. Two strands (thick tubes)
## wind round a vertical axis; every few steps a bridge joins them, each half in one of
## the paired base colours. Pieces are sorted back to front so the strands pass in front
## of and behind each other; the far side is drawn dimmer.
func _hq_dna(cx: float, cy: float, k: float, col: Color, z0: float, z1: float) -> void:
	var r := 1.5 * k
	var turns := 2.5
	var n := 110
	var tube := 14.0 * k
	var pairs := [[_inks[0], _inks[3]], [_inks[2], col]]
	var pieces: Array[Dictionary] = []
	var pts: Array = [[], []]
	for q in n + 1:
		var t := float(q) / n
		for sn in 2:
			var a := t * turns * TAU + sn * PI
			var g := Vector2(cx + cos(a) * r, cy + sin(a) * r)
			pts[sn].append({"g": g, "p": _iso(g.x, g.y) + Vector2(0, -lerpf(z0, z1, t))})
	for sn in 2:
		for q in n:
			var g0: Vector2 = pts[sn][q]["g"]
			var g1: Vector2 = pts[sn][q + 1]["g"]
			pieces.append({"d": (g0.x + g0.y + g1.x + g1.y) * 0.5, "kind": 0, "a": pts[sn][q]["p"], "b": pts[sn][q + 1]["p"], "q": q})
	for q in range(2, n - 1, 4):
		var pa: Vector2 = pts[0][q]["p"]
		var pb: Vector2 = pts[1][q]["p"]
		var mid := (pa + pb) * 0.5
		var ga: Vector2 = pts[0][q]["g"]
		var gb: Vector2 = pts[1][q]["g"]
		var pair: Array = pairs[(q / 4) % 2]
		var flip := (q / 8) % 2 == 1
		pieces.append({"d": (ga.x + ga.y + cx + cy) * 0.5, "kind": 1, "a": pa, "b": mid, "col": pair[1 if flip else 0]})
		pieces.append({"d": (gb.x + gb.y + cx + cy) * 0.5, "kind": 1, "a": mid, "b": pb, "col": pair[0 if flip else 1]})
	pieces.sort_custom(func(p1: Dictionary, p2: Dictionary) -> bool: return p1["d"] < p2["d"])
	var centre := cx + cy
	for pc in pieces:
		var a: Vector2 = pc["a"]
		var b: Vector2 = pc["b"]
		# 0 on the far side of the axis, 1 on the near side.
		var near := clampf((float(pc["d"]) - centre) / (2.0 * r) + 0.5, 0.0, 1.0)
		var dir := (b - a).normalized()
		var nn := dir.orthogonal()
		if pc["kind"] == 0:
			var e0 := a - dir * tube * 0.15
			var e1 := b + dir * tube * 0.15
			var body := FILLS[1].lerp(col, 0.12 + near * 0.12).darkened(0.3 * (1.0 - near))
			_quad(e0 - nn * tube * 0.5, e1 - nn * tube * 0.5, e1 + nn * tube * 0.5, e0 + nn * tube * 0.5, body, body, body, body)
			# Neon tube outline: a wide soft glow, then a bright core on each edge.
			var glow := Color(col, 0.1 + 0.14 * near)
			var edge := Color(col.lightened(0.25), 0.55 + 0.45 * near)
			for side in [-1.0, 1.0]:
				var o: Vector2 = nn * tube * 0.5 * side
				_hair(e0 + o, e1 + o, glow, 9.0)
				_hair(e0 + o, e1 + o, Color(col, 0.35 + 0.3 * near), 4.0)
				_hair(e0 + o, e1 + o, edge, 2.0)
			_hair(a + nn * tube * 0.12, b + nn * tube * 0.12, Color(col.lightened(0.5), 0.15 + 0.4 * near), tube * 0.18)
			if near > 0.55 and int(pc["q"]) % 3 == 0:
				var w := (a + b) * 0.5 - nn * tube * 0.2
				var wc := Color(_inks[int(pc["q"]) % _inks.size()], 0.8)
				_quad(w + Vector2(-2, 0), w + Vector2(0, -2), w + Vector2(2, 0), w + Vector2(0, 2), wc, wc, wc, wc)
		else:
			# A bridge: a deck with a rail, in the base's colour.
			var bc: Color = pc["col"]
			var deck := FILLS[0].lerp(bc, 0.35)
			var hw := tube * 0.22
			_quad(a - nn * hw, b - nn * hw, b + nn * hw, a + nn * hw, deck, deck, deck, deck)
			_hair(a, b, Color(bc, 0.12 + 0.1 * near), hw * 2.0 + 8.0)
			_hair(a - nn * hw, b - nn * hw, Color(bc.lightened(0.2), 0.6 + 0.4 * near), 2.0)
			_hair(a + nn * hw, b + nn * hw, Color(bc, 0.45 + 0.4 * near), 1.4)
	# Caps: a node on each strand's top, and a beacon over the axis.
	for sn in 2:
		var tp: Vector2 = pts[sn][n]["p"]
		_quad(tp + Vector2(-tube * 0.6, 0), tp + Vector2(0, -tube * 0.6), tp + Vector2(tube * 0.6, 0), tp + Vector2(0, tube * 0.6), col, col, col, col)
		_beacons.append({"pos": tp + Vector2(0, -tube), "color": col, "phase": 0.2 + sn * 0.3})
	_beacons.append({"pos": _iso(cx, cy) + Vector2(0, -z1 - 40.0 * k), "color": col, "phase": 0.5})


## A gold hieroglyph frieze on a sloped face (bottom edge p00-p10, top edge p01-p11):
## two rules at heights v0 and v1 (0-1 up the face) with `count` little signs between
## them; `gap` leaves the middle of the band open (for a ramp).
func _frieze(p00: Vector2, p10: Vector2, p01: Vector2, p11: Vector2, v0: float, v1: float, count: int, gap: float, gold: Color, salt: int) -> void:
	var band_col := Color(gold, 0.6)
	_hair(p00.lerp(p01, v0), p10.lerp(p11, v0), band_col, 1.2)
	_hair(p00.lerp(p01, v1), p10.lerp(p11, v1), band_col, 1.2)
	for q in count:
		var u := (q + 0.5) / count
		if absf(u - 0.5) < gap:
			continue
		var gp := p00.lerp(p10, u).lerp(p01.lerp(p11, u), (v0 + v1) * 0.5)
		var gh := (v1 - v0) * p00.lerp(p10, u).distance_to(p01.lerp(p11, u)) * 0.32
		var gc := Color(gold, 0.75)
		match int(_h(q, salt, 95) * 4.0):
			0:
				_hair(gp + Vector2(0, -gh), gp + Vector2(0, gh), gc, 1.2)
			1:
				for m in 6:
					var a0 := TAU * m / 6.0
					_hair(gp + Vector2(cos(a0), sin(a0)) * gh * 0.7, gp + Vector2(cos(a0 + TAU / 6.0), sin(a0 + TAU / 6.0)) * gh * 0.7, gc, 1.0)
			2:
				_hair(gp + Vector2(-gh * 0.6, gh * 0.4), gp + Vector2(0, -gh * 0.5), gc, 1.0)
				_hair(gp + Vector2(0, -gh * 0.5), gp + Vector2(gh * 0.6, gh * 0.4), gc, 1.0)
			_:
				_hair(gp + Vector2(-gh * 0.6, -gh * 0.3), gp + Vector2(gh * 0.6, -gh * 0.3), gc, 1.0)
				_hair(gp + Vector2(0, -gh * 0.3), gp + Vector2(0, gh), gc, 1.0)


## English HQ: a great clock tower (Big Ben style) with glowing clock faces, a belfry and a
## pinnacled spire, beside a long gabled hall.
func _hq_big_ben(cx: float, cy: float, k: float, col: Color, base: Vector2) -> void:
	# The hall behind and to the side.
	_extrude(_rect_pts(cx - 2.2 * k, cy - 1.9 * k, cx + 2.2 * k, cy - 0.9 * k), 0.0, 34.0 * k, 1.0, FILLS[1], col, 0.3, 980)
	_gable(cx - 2.2 * k, cy - 1.9 * k, cx + 2.2 * k, cy - 0.9 * k, 34.0 * k, 22.0 * k, FILLS[0], col)
	var r := 0.55 * k
	var th := 230.0 * k
	_extrude(_rect_pts(cx - r, cy - r, cx + r, cy + r), 0.0, th, 1.0, FILLS[1], col, 0.35, 981)
	# Vertical tracery up the two visible faces.
	for q in 3:
		var f := float(q + 1) / 4.0
		var pa := _iso(cx - r + 2.0 * r * f, cy + r)
		var pb := _iso(cx + r, cy - r + 2.0 * r * f)
		_ink_line(pa + Vector2(0, -6), pa + Vector2(0, -th + 6), Color(col, 0.35), 1.0, false)
		_ink_line(pb + Vector2(0, -6), pb + Vector2(0, -th + 6), Color(col, 0.25), 1.0, false)
	# Clock stage, a little wider, with a face on each visible side.
	var cr := 0.68 * k
	var ch := 58.0 * k
	_extrude(_rect_pts(cx - cr, cy - cr, cx + cr, cy + cr), th, ch, 1.0, FILLS[0], col, 0.0, 982)
	var face_col := Color(Palette.CRT_AMBER, 0.95)
	for side in 2:
		var fc: Vector2
		var u: Vector2
		if side == 0:
			fc = _iso(cx, cy + cr) + Vector2(0, -th - ch * 0.5)
			u = (_iso(1, 0) - _iso(0, 0)).normalized()
		else:
			fc = _iso(cx + cr, cy) + Vector2(0, -th - ch * 0.5)
			u = (_iso(0, 1) - _iso(0, 0)).normalized()
		var rad := cr * TILE_A * 0.72
		var ring := PackedVector2Array()
		for q in 33:
			var a := TAU * q / 32.0
			ring.append(fc + u * cos(a) * rad + Vector2(0, -1) * sin(a) * rad * 0.95)
		_poly(ring, Color(Palette.CRT_AMBER, 0.25))
		for q in 32:
			_ink_line(ring[q], ring[q + 1], face_col, 1.4, false)
		for q in 12:
			var a := TAU * q / 12.0
			var p0 := fc + u * cos(a) * rad * 0.8 + Vector2(0, -1) * sin(a) * rad * 0.8
			_ink_line(p0, fc + u * cos(a) * rad * 0.92 + Vector2(0, -1) * sin(a) * rad * 0.92, face_col, 1.0, false)
		_ink_line(fc, fc + Vector2(0, -rad * 0.62), face_col, 1.8, false)
		_ink_line(fc, fc + u * rad * 0.45, face_col, 1.8, false)
	# Belfry, then the spire with corner pinnacles.
	var br := 0.5 * k
	_extrude(_rect_pts(cx - br, cy - br, cx + br, cy + br), th + ch, 30.0 * k, 1.0, FILLS[1], col, 0.4, 983)
	_extrude(_rect_pts(cx - br, cy - br, cx + br, cy + br), th + ch + 30.0 * k, 80.0 * k, 0.05, FILLS[0], col, 0.0, 984)
	for q in [Vector2(-1, -1), Vector2(1, -1), Vector2(1, 1), Vector2(-1, 1)]:
		var p0 := _iso(cx + q.x * br, cy + q.y * br) + Vector2(0, -(th + ch + 30.0 * k))
		_ink_line(p0, p0 + Vector2(0, -22.0 * k), col, 1.3, false)
	_beacons.append({"pos": base + Vector2(0, -(th + ch + 118.0 * k)), "color": col, "phase": 0.2})


## A neon name plate floating over an HQ (drawn by the overlay).
func _sign(at: Vector2, text: String, col: Color) -> void:
	_signs.append({"pos": at, "text": text, "color": col})


func _draw_fx() -> void:
	# ANIM-R2 R11: a painter bakes no live layer (the signs, sparks and rain are drawn live
	# over the image; the synchronous bake drew the signs into it too, twice over the live one).
	if _built_for != size or _painter:
		return
	if territory_labels:
		var inv := 1.0 / maxf(0.01, scale.x)
		for t in TERRITORIES:
			var name := "THE SPRAWL" if t["id"] == &"" else String(t["id"]).to_upper()
			var at: Vector2 = t["at"]
			var k := territory_label_px / 30.0 * inv
			var p := _iso(at.x + HQ_LOTS * 0.5, at.y + HQ_LOTS * 0.5) + Vector2(-120, -40) * k
			if t["id"] == FIST_TERRITORY:
				p.y -= FIST_SIZE.y * 0.56  # above the fist, not over it
			var col := Palette.PAPER if t["id"] == &"" else Palette.corp_color(t["id"])
			_fx.draw_rect(Rect2(p - Vector2(8, 30) * k, Vector2(260, 40) * k), Color(0, 0, 0, 0.75))
			_fx.draw_string(Palette.display(), p, name, HORIZONTAL_ALIGNMENT_LEFT, -1, int(30 * k), col)
	# Everything below was recorded in the image's space (baked) or the city's (not).
	_fx.draw_set_transform(_shift)
	var flicker := Motion.live(SIGN_MOTION)
	var period := maxf(0.1, Motion.entry(SIGN_MOTION).duration)
	var dip := Motion.entry(SIGN_MOTION).delay / period
	var pick := Motion.amplitude(SIGN_PICK_MOTION)
	for sg in _signs:
		var p: Vector2 = sg["pos"]
		var col: Color = sg["color"]
		# Neon flicker on a few signs: a short dip once a period (hash-phased and hash-picked
		# per sign, so the city never strobes).
		if flicker and _h(int(p.x), int(p.y), 121) < pick:
			var ph := fmod(anim_t / period + _hv(p), 1.0)
			if ph < dip:
				col = Color(col, Motion.amplitude(SIGN_MOTION))
		var w := Palette.mono().get_string_size(sg["text"], HORIZONTAL_ALIGNMENT_LEFT, -1, 14).x + 14
		_fx.draw_rect(Rect2(p, Vector2(w, 22)), Color(Palette.NIGHT_SKY, 0.85))
		_fx.draw_rect(Rect2(p, Vector2(w, 22)), Color(col, 0.2 * col.a), false, 5.0)
		_fx.draw_rect(Rect2(p, Vector2(w, 22)), col, false, 1.2)
		_fx.draw_string(Palette.mono(), p + Vector2(7, 16), sg["text"], HORIZONTAL_ALIGNMENT_LEFT, -1, 14, col.lightened(0.3))
	# Traffic: small bright dashes sliding along the busiest lanes. (Window lights and
	# beacons blink on the GPU: _draw_lights / _draw_beacons.)
	if Motion.live(TRAFFIC_MOTION):
		var speed := 1.0 / maxf(0.1, Motion.entry(TRAFFIC_MOTION).duration)
		for t in _live_trails:
			var a: Vector2 = t["a"]
			var b: Vector2 = t["b"]
			var k := fmod(float(t["phase"]) + anim_t * speed, 1.0)
			var p := a.lerp(b, k)
			var col: Color = t["color"]
			var w := float(t.get("width", 2.0))
			_fx.draw_line(p, p + (b - a) * SPARK_LENGTH, Color(col.lightened(0.3), 0.9), w)
			_fx.draw_line(p + (b - a) * SPARK_LENGTH * 0.3, p + (b - a) * SPARK_LENGTH * 0.8, Color(1, 1, 1, SPARK_CORE), w * 0.5)
	_fx.draw_set_transform(Vector2.ZERO)
	if rain:
		var off := fmod(anim_t * 480.0, 80.0)
		for k in 70:
			var rx := fmod(float(k * 97 + city_seed * 13), size.x + 80.0) - 40.0
			var ry := fmod(float((k * 53) % 720) + off * (1.0 + (k % 3) * 0.35), size.y)
			_fx.draw_line(Vector2(rx, ry), Vector2(rx - 5, ry + 22), Color(Palette.NET_CYAN, 0.18), 1.0)
