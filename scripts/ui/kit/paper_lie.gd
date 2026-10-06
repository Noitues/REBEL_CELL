class_name PaperLie
extends RefCounted
## B5 (integration review D24: "Work orders and dossiers lack the paper clip and the 1 to 2 degree tilt with a
## contact shadow that the concepts have (round 21 raid_report). Add a tilt from a seeded stream and a 6 px
## shadow."): how a sheet of paper lies on the world. A seeded tilt of 1 to 2 degrees either way (KitNoise: view
## decoration, never game RNG), a soft 6 px contact shadow (1080p px), and the concepts' own paper clip
## (`kit44.work_order`'s clip, exported unchanged by tools/art/export_paper_clip.py). Static helpers; a view only.

## The tilt's range (degrees, either way).
const TILT_MIN_DEG := 1.0
const TILT_MAX_DEG := 2.0
## The contact shadow: its reach (1080p px), its offset down (share of the reach), its darkness at the paper's
## edge, and the rings it is drawn in (a soft edge with draws only).
const SHADOW_PX_1080 := 6.0
const SHADOW_DROP := 0.5
const SHADOW_ALPHA := 0.45
const SHADOW_RINGS := 4
## The board height the 1080p numbers are measured on.
const BOARD_H := 1080.0
## The concept's paper clip (exported at 2x the 1080p board).
const CLIP := preload("res://assets/ui/paper/paper_clip.png")
const CLIP_EXPORT_SCALE := 2.0
## The clip's inset from the paper's right edge (1080p px; kit44: 10) and how far it rises over the top edge
## (share of its height: the clip grips the edge).
const CLIP_INSET_1080 := 10.0
const CLIP_RISE := 0.3


## The tilt (degrees) of the paper seeded by `seed`: 1 to 2 degrees, its side from the seed too.
static func tilt_deg(seed: int) -> float:
	var h := KitNoise.h11(seed, 24, 1)
	var mag := lerpf(TILT_MIN_DEG, TILT_MAX_DEG, absf(KitNoise.h11(seed, 24, 2)))
	return mag if h >= 0.0 else -mag


## 1080p px on a screen `screen_h` px high.
static func px(v_1080: float, screen_h: float) -> float:
	return v_1080 * screen_h / BOARD_H


## The contact shadow's reach (px) on a screen `screen_h` px high.
static func shadow_px(screen_h: float) -> float:
	return px(SHADOW_PX_1080, screen_h)


## Draws the soft contact shadow of a sheet at `r` (in `ci`'s space) on a screen `screen_h` px high: rings that
## fade out over the reach, dropped down by SHADOW_DROP of it. Draw it before the paper.
static func draw_contact_shadow(ci: CanvasItem, r: Rect2, screen_h: float) -> void:
	var reach := shadow_px(screen_h)
	var at := r
	at.position.y += reach * SHADOW_DROP
	for i in SHADOW_RINGS:
		var t := float(i + 1) / float(SHADOW_RINGS)
		ci.draw_rect(at.grow(reach * t), Color(Palette.SHADOW, SHADOW_ALPHA / float(SHADOW_RINGS)))


## The clip's size (px) on a screen `screen_h` px high.
static func clip_size(screen_h: float) -> Vector2:
	return CLIP.get_size() / CLIP_EXPORT_SCALE * screen_h / BOARD_H


## Where the clip goes on a sheet at `r` (its rect): at the top right, gripping the top edge.
static func clip_rect(r: Rect2, screen_h: float) -> Rect2:
	var s := clip_size(screen_h)
	return Rect2(Vector2(r.end.x - s.x - px(CLIP_INSET_1080, screen_h), r.position.y - s.y * CLIP_RISE), s)


## Draws the concept's paper clip on the sheet at `r` (draw it after the paper).
static func draw_clip(ci: CanvasItem, r: Rect2, screen_h: float) -> void:
	ci.draw_texture_rect(CLIP, clip_rect(r, screen_h), false)
