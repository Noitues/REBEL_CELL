class_name RcLookBloomConfig
extends Resource
## LOOK Solace THE BLOOM A "Necrosis" (designer 2026-10-22): every number of the Bloom's look (addons/rc_look/config/look_bloom.tres).
## The numbers are the concept's own (art-pass docs/concepts/solace_vertical/bloom: bloom3d_street.make_cfg / STATE_TUNE for the
## street, bloom3d_hq_run.cfg_for for the HQ helix); the shader (shaders/city/bloom_necrosis.gdshaderinc) holds only the node graphs'
## structure. Read-only content: BloomLook reads it, nothing writes it.

## Street skin uniforms (shader `bl_*` names without the prefix): pink, plum, rough, seed, cover_k, veins, edge_k, hatch_k, vscale, vw,
## ew, hatch_scale, tend, tend_h. Colours are linear RGB arrays.
@export var street: Dictionary = {}
## Street skin overrides per band name (CREEPING, CLOSE, CATCHING): the concept's per-state tune.
@export var street_bands: Dictionary = {}
## The street frame and the keep-outs: x0 / y0 (the concept plate's street start, so its noise numbers hold), the route-room box margins
## (room_mx / room_mz: share of the room's size, room_y / room_z: BU added), the link box margins, cull_ahead (a box this far ahead of the
## front is dropped), max_boxes, facade_off (BU the facade ribbons stand off the rooms' front), layer_slope_min (BU per layer when the layer
## columns give none).
@export var street_frame: Dictionary = {}
## The vein ribbons that crawl ahead of the front on the road (bloom3d_ribbons.make): seed, n_ground, n_facade, width, strength, y0, y1,
## z_ground, reach_layers (the reach in LAYERS: BloomLook turns it into BU by the layout's layer spacing), len_min_share, fork, facade_h, step
## (per band: strength via street_bands.ribbons_strength).
@export var ribbons: Dictionary = {}
## HQ helix skin / window-dim uniforms (names without the `bl_` prefix) and the plate's helix numbers (radius, floor_h, theta0, twist,
## tube_r, podium, stair_deg), the front's height over a route node (front_over_node), the decision's lift (decision_lift), the route-room
## spheres (room_r) and the role -> mode table (roles: 1 skin, 2 window light).
@export var hq: Dictionary = {}
## The faint spore haze above the HQ front: h (BU tall, plate units), r, density k, emission, noise scale, below (BU under the front),
## decision_share (the share of it the decision shot keeps: the camera stands in it). Godot's fog emission is not Blender's volume
## emission: k / emission are tuned to the overview's read (the concept's 0.004 / 0.07 gave no visible haze).
@export var haze: Dictionary = {}


## Problems with the config (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	for k: String in ["pink", "plum", "rough", "seed", "cover_k", "veins", "edge_k", "hatch_k", "vscale", "vw", "ew", "hatch_scale", "tend_layers", "tend_h", "lean", "wall_vw", "wall_veins", "wall_hatch"]:
		if not street.has(k):
			errs.append("street.%s missing" % k)
	for b: String in ["CREEPING", "CLOSE", "CATCHING"]:
		if not street_bands.has(b):
			errs.append("street_bands.%s missing" % b)
	for k: String in ["x0", "y0", "room_mx", "room_mz", "room_y0", "room_y1", "room_z", "link_x", "link_y", "link_z", "cull_ahead", "max_boxes", "layer_spacing_min", "layer_spacing_ref"]:
		if not street_frame.has(k):
			errs.append("street_frame.%s missing" % k)
	for k: String in ["seed", "n_ground", "n_facade", "width", "strength", "y0", "y1", "z_ground", "reach_layers", "len_min_share", "fork", "facade_h", "step"]:
		if not ribbons.has(k):
			errs.append("ribbons.%s missing" % k)
	for k: String in ["pink", "plum", "rough", "seed", "cover_k", "veins", "edge_k", "hatch_k", "vscale", "vw", "ew", "hatch_scale", "swell", "tongue",
			"reach", "ahead_k", "win_dim", "win_r", "radius", "floor_h", "theta0", "twist", "tube_r", "podium", "stair_deg", "stair_w", "front_over_node",
			"decision_lift", "room_r", "roles", "face_front_deg", "node_over_floor", "win_zc"]:
		if not hq.has(k):
			errs.append("hq.%s missing" % k)
	for k: String in ["h", "r", "k", "emission", "scale", "below", "decision_share"]:
		if not haze.has(k):
			errs.append("haze.%s missing" % k)
	if int(street_frame.get("max_boxes", 0)) > 128:
		errs.append("street_frame.max_boxes is over the shader's 128")
	return errs
