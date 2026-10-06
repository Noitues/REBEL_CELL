class_name PaperStaging
extends RefCounted
## D24: how a corp paper sits on the table. A slight tilt (1 to 2 degrees, either way) from a
## seeded stream keyed by the document's id, a 6 px contact shadow under it and the steel paper
## clip over its top edge (the clip is the art pass's own drawing, ui19.dossier, moved here
## from RaidPaper so the operative dossier shares it). The same stock rule as the case files
## (B5, `CaseFileCard.TILT`): paper carries a slight rotation. Pure helpers, no state.

## The tilt's range (degrees, magnitude) and the stream that draws it.
const TILT_MIN := 1.0
const TILT_MAX := 2.0
const STREAM := &"paper"
## The contact shadow's reach below the sheet (px at text scale 1.0), the layers it is built
## from and each layer's alpha.
const SHADOW_PX := 6.0
const SHADOW_LAYERS := 3
const SHADOW_ALPHA := 0.22
## The clip (px at 1.0): its width and height, and how far it rises over the paper's top edge.
const CLIP_W := 13.0
const CLIP_H := 24.0
const CLIP_RISE := 10.0
## How far the clip bites into the sheet (px at 1.0): the sheet keeps its top padding this deep so
## the letterhead starts below the jaw (D24).
const CLIP_BITE := CLIP_H - CLIP_RISE
## The clip's wire widths (px at 1.0) and the shade under it.
const CLIP_WIRE := 2.0
const CLIP_UNDER := 3.0
const CLIP_UNDER_ALPHA := 0.6


## The tilt (degrees) of the paper whose content id is `id`: 1 to 2 in magnitude, either way,
## the same every time for the same id.
static func tilt_degrees(id: String) -> float:
	var rng := RngStreams.make_stream(hash(id), STREAM)
	var mag := rng.randf_range(TILT_MIN, TILT_MAX)
	return mag if rng.randi() % 2 == 0 else -mag


## How far a `size` sheet tilted `deg` degrees about its centre reaches beyond its own rect on
## each side (px): what its neighbours keep clear of.
static func reach(size: Vector2, deg: float) -> Vector2:
	var a := absf(deg_to_rad(deg))
	var half := size * 0.5
	var rot := Vector2(half.x * cos(a) + half.y * sin(a), half.x * sin(a) + half.y * cos(a))
	return (rot - half).max(Vector2.ZERO)


## The contact shadow under a sheet of `size` (drawn on `ci`, in the sheet's own space, so it
## turns with it): soft layers growing to SHADOW_PX below and a little round it.
static func draw_shadow(ci: CanvasItem, size: Vector2, k: float) -> void:
	var reach_px := SHADOW_PX * k
	for i in SHADOW_LAYERS:
		var t := float(SHADOW_LAYERS - i) / SHADOW_LAYERS
		var grow := reach_px * (1.0 - t) * 0.5
		var r := Rect2(Vector2(-grow, reach_px * t * 0.5), size + Vector2(grow * 2.0, reach_px * t * 0.5 + grow))
		ci.draw_rect(r, Color(Palette.SHADOW, SHADOW_ALPHA))


## The steel paper clip over the sheet's top edge at x = `x` (px, already scaled by `k`).
static func draw_clip(on: CanvasItem, x: float, k: float) -> void:
	var steel := Palette.TEXT_MID
	for j in 2:
		var w := (CLIP_W - j * 4.0) * k
		var h := (CLIP_H - j * 9.0) * k
		var top := (-CLIP_RISE + j * 4.0) * k
		var r := Rect2(x - w * 0.5, top, w, h)
		var under := Color(Palette.NIGHT_SKY, CLIP_UNDER_ALPHA)
		on.draw_line(r.position + Vector2(0, w * 0.5), Vector2(r.position.x, r.end.y - w * 0.5), under, CLIP_UNDER * k)
		on.draw_line(Vector2(r.end.x, r.position.y + w * 0.5), r.end - Vector2(0, w * 0.5), under, CLIP_UNDER * k)
		on.draw_arc(Vector2(x, r.position.y + w * 0.5), w * 0.5, PI, TAU, 10, steel, CLIP_WIRE * k)
		on.draw_arc(Vector2(x, r.end.y - w * 0.5), w * 0.5, 0, PI, 10, steel, CLIP_WIRE * k)
		on.draw_line(r.position + Vector2(0, w * 0.5), Vector2(r.position.x, r.end.y - w * 0.5), steel, CLIP_WIRE * k)
		on.draw_line(Vector2(r.end.x, r.position.y + w * 0.5), r.end - Vector2(0, w * 0.5), steel, CLIP_WIRE * k)
