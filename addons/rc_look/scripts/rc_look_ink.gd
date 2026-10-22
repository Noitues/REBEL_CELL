class_name RcLookInk
extends RefCounted
## LOOK-TOOLBOX module 5: ink. The shader side is rc_ink.gdshaderinc; this is its exact GDScript mirror plus the presets
## (config/look_ink.tres: "hull" for props / busts / aircraft, "post" for the city's edge pass, "post_backdrop" for the
## combat backdrop's coarser pass). Pure: no Node, no Settings.

const DEFAULT_PATH := "res://addons/rc_look/config/look_ink.tres"
const REQUIRED: Array[StringName] = [&"hull", &"post"]

static var _cfg: RcLookInkConfig


## The shipped presets, loaded once.
static func default_config() -> RcLookInkConfig:
	if _cfg == null:
		_cfg = load(DEFAULT_PATH) as RcLookInkConfig
	return _cfg


## A shipped preset by name (null when unknown).
static func preset(name: StringName) -> RcLookInkPreset:
	return default_config().presets.get(name) as RcLookInkPreset


## The hull's width with a wobble (n01: a 0..1 noise at the vertex), as rcl_hull_width.
static func hull_width(width_px: float, wobble: float, n01: float) -> float:
	return width_px * (1.0 + wobble * (n01 - 0.5) * 2.0)


## The hull vertex grown `width_px` px outward on screen, as rcl_hull_clip (clip = x, y, z, w).
static func hull_clip(clip: Vector4, n_clip: Vector2, width_px: float, viewport: Vector2) -> Vector4:
	var off := n_clip * width_px * 2.0 / viewport * clip.w
	return Vector4(clip.x + off.x, clip.y + off.y, clip.z, clip.w)


## 1 where the normal / material code changes past thr (c = normal xyz, material w), as rcl_ink_normal_edge.
static func normal_edge(c0: Vector4, cn: Vector4, thr: float) -> float:
	var d := Vector3(cn.x - c0.x, cn.y - c0.y, cn.z - c0.z).length() * 0.5 + absf(cn.w - c0.w)
	return 0.0 if d < thr else 1.0


## The depth step that counts as an edge at this ortho size, as rcl_ink_depth_thr.
static func depth_thr(edge: float, ortho: float, ortho_ref: float) -> float:
	return edge * (ortho / ortho_ref)


## 1 where the view depth jumps past thr, as rcl_ink_depth_edge.
static func depth_edge(zc: float, zn: float, thr: float) -> float:
	return 0.0 if absf(zn - zc) < thr else 1.0
