class_name HqCompoundStage
extends RefCounted
## ART-8 8w: where an HQ compound (8p's glTF, bible 4.7) stands in the one city and how the
## HQ-run page looks at it. Pure maths over the compound's manifest and layout table: the
## place transform (the manifest's `place_lot`, else the HQ lot's centre), the run's node
## points in the world (HqCompoundLayout through the place), the footprint the city's own
## buildings give way inside, and the camera (the manifest's yaw, pitch and reference
## framing). DISPATCH's compound is the round 43 Tokyo canyon (yaw 180 / pitch 40, looking
## down the street); the corps keep the city azimuth at 55 degrees.
## View-side only: it reads content and never changes game state.

const ASSETS_DIR := "res://assets/city/hq_compounds"
const LAYOUT_DIR := "res://content/city/hq_compounds"

static var _manifests: Dictionary = {}


## The manifest of `corp`'s compound ({} when it has none).
static func manifest(corp: StringName) -> Dictionary:
	if _manifests.has(corp):
		return _manifests[corp]
	var out := {}
	var f := FileAccess.open("%s/%s/manifest.json" % [ASSETS_DIR, corp], FileAccess.READ)
	if f != null:
		var m: Variant = JSON.parse_string(f.get_as_text())
		if m is Dictionary:
			out = m
	_manifests[corp] = out
	return out


## The layout table of `corp`'s compound (null when it has none). Read-only.
static func layout(corp: StringName) -> HqCompoundLayoutData:
	var path := "%s/%s.tres" % [LAYOUT_DIR, corp]
	return load(path) as HqCompoundLayoutData if ResourceLoader.exists(path) else null


## The glTF of `corp`'s compound (res path, "" when the manifest lists none).
static func model_path(corp: StringName, m: Dictionary) -> String:
	for f in m.get("files", []):
		if String(f.get("kind", "")) == "gltf":
			return "%s/%s/%s" % [ASSETS_DIR, corp, String(f.get("path", ""))]
	return ""


## The lot point the compound's origin stands on: the manifest's `place_lot` (the canyon
## sits on round 34's own canyon lots), else the centre of `hq_rect` (the HQ lot, CityModel.hqs),
## else NeonCity's HQ square of `corp`.
static func place_lot(corp: StringName, m: Dictionary, hq_rect: Rect2i = Rect2i()) -> Vector2:
	var pl: Variant = m.get("place_lot")
	if pl is Array and (pl as Array).size() == 2:
		return Vector2(float(pl[0]), float(pl[1]))
	if hq_rect.has_area():
		return Vector2(hq_rect.get_center())
	return NeonCity.hq_of(corp) + Vector2(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS) * 0.5


## The compound's place in the world: its frame is the city's (Godot / glTF, Y up, metres),
## so only the origin moves.
static func place(cfg: CityConfig, corp: StringName, m: Dictionary, hq_rect: Rect2i = Rect2i()) -> Transform3D:
	return Transform3D(Basis(), CityIsoCamera.lot_to_world(cfg, place_lot(corp, m, hq_rect)))


## Every node of `graph` -> its world point on the compound placed at `at` (node-id order;
## nodes without a slot are left out).
static func node_points(l: HqCompoundLayoutData, graph: MapGraph, at: Transform3D) -> Dictionary:
	var out := {}
	if l == null or graph == null:
		return out
	var local := HqCompoundLayout.positions(l, graph)
	for id: StringName in local:
		out[id] = at * (local[id] as Vector3)
	return out


## Where the run enters the compound (world).
static func entry_point(l: HqCompoundLayoutData, at: Transform3D) -> Vector3:
	return at * l.entry if l != null else at.origin


## The Central Server's world point.
static func server_point(l: HqCompoundLayoutData, at: Transform3D) -> Vector3:
	return at * l.central_server if l != null else at.origin


## The compound's ground box (world X/Z) from the manifest's footprint.
static func footprint_rect(m: Dictionary, at: Transform3D) -> Rect2:
	var fp: Dictionary = m.get("footprint", {})
	var lo: Array = fp.get("min", [0, 0, 0])
	var hi: Array = fp.get("max", [0, 0, 0])
	var a := at * Vector3(float(lo[0]), 0.0, float(lo[2]))
	var b := at * Vector3(float(hi[0]), 0.0, float(hi[2]))
	return Rect2(Vector2(minf(a.x, b.x), minf(a.z, b.z)), Vector2(absf(b.x - a.x), absf(b.z - a.z)))


## The HQ-run camera: the manifest's yaw and pitch, its reference target (through `at`) and
## ortho width, at viewport `size`.
static func camera(cfg: CityConfig, m: Dictionary, at: Transform3D, size: Vector2) -> CityIsoCamera:
	var s: Dictionary = m.get("settings", {})
	var ref: Dictionary = s.get("reference_camera", {})
	var t: Array = ref.get("target", [0, 0, 0])
	var c := CityIsoCamera.make(cfg, at * Vector3(float(t[0]), float(t[1]), float(t[2])), float(ref.get("ortho", cfg.views["close"][2])), size)
	c.yaw_deg = float(s.get("yaw_deg", cfg.yaw_deg))
	c.pitch_deg = float(s.get("pitch_deg", cfg.pitch_deg))
	return c


## Parity S-HQRUN: the HQ-run page's own framing of the compound: the manifest's camera
## (`camera`) with the page's per-corporation framing from `cfg` (the round 43 concepts'
## distance, aim, pitch and yaw: `hq_run_*_by_corp`). The combat backdrop keeps `camera`.
static func page_camera(cfg: CityConfig, m: Dictionary, at: Transform3D, size: Vector2, pts: Array[Vector3] = [],
		aim: Rect2 = Rect2()) -> CityIsoCamera:
	var cam := camera(cfg, m, at, size)
	var corp := StringName(String(m.get("corp", "")))
	cam.ortho *= float(cfg.hq_run_ortho_scale_by_corp.get(corp, 1.0))
	var shift: Variant = cfg.hq_run_target_by_corp.get(corp)
	if shift is Vector3:
		cam.target += at.basis * (shift as Vector3)
	cam.pitch_deg = float(cfg.hq_run_pitch_by_corp.get(corp, cam.pitch_deg))
	cam.yaw_deg = float(cfg.hq_run_yaw_by_corp.get(corp, cam.yaw_deg))
	cam.fov_deg = float(cfg.hq_run_fov_by_corp.get(corp, 0.0))
	if not cam.perspective() and cfg.hq_run_landmark_share > 0.0:
		_fill_landmark(cam, m, at, size, pts, aim, cfg.hq_run_landmark_share, cfg.hq_run_landmark_width_max)
	return cam


## B4 (review D18, round 43 `hq_*_compound.png`; art director's fix: measure the run, not the
## crane boom or the spire): an orthographic page's width and aim so the landmark box (the
## union of the compound's footprint box placed at `at` and the run's points `pts`) stands
## `share` of the frame's height, centred in `aim` (the page's free part; the frame when empty);
## a wide, low box (Meridian's yard) is held to `width_max` of the frame's width instead.
static func _fill_landmark(cam: CityIsoCamera, m: Dictionary, at: Transform3D, size: Vector2, pts: Array[Vector3], aim: Rect2,
		share: float, width_max: float) -> void:
	var box := landmark_box(cam, m, at, pts)
	if not box.has_area():
		return
	var aspect := size.x / maxf(size.y, 1.0)
	cam.ortho = maxf(box.size.y / share * aspect, box.size.x / maxf(width_max, 0.01))
	var room := aim if aim.has_area() else Rect2(Vector2.ZERO, size)
	var oh := cam.ortho * size.y / maxf(size.x, 1.0)
	# The screen-plane centre that puts the box's middle at the room's middle.
	var xc := (room.get_center().x / size.x - 0.5) * cam.ortho
	var yc := (0.5 - room.get_center().y / size.y) * oh
	var c := box.get_center()
	var o := cam.right() * (c.x - xc) + cam.up() * (c.y - yc)
	var f := cam.forward()
	cam.target = o + f * ((0.0 - o.y) / f.y)


## B4: the landmark box on `cam`'s screen plane (world units along its right and up axes): the
## eight corners of the manifest's footprint placed at `at`, with the run's points `pts`.
static func landmark_box(cam: CityIsoCamera, m: Dictionary, at: Transform3D, pts: Array[Vector3] = []) -> Rect2:
	var world: Array[Vector3] = []
	var fp: Dictionary = m.get("footprint", {})
	if not fp.is_empty():
		var lo: Array = fp.get("min", [0, 0, 0])
		var hi: Array = fp.get("max", [0, 0, 0])
		for i in 8:
			world.append(at * Vector3(float(hi[0] if i & 1 else lo[0]), float(hi[1] if i & 2 else lo[1]), float(hi[2] if i & 4 else lo[2])))
	world.append_array(pts)
	var r := cam.right()
	var u := cam.up()
	var box := Rect2()
	var first := true
	for p in world:
		var q := Vector2(p.dot(r), p.dot(u))
		box = Rect2(q, Vector2.ZERO) if first else box.expand(q)
		first = false
	return box


## B4 (D18): the share of a `size` page's height the landmark box (footprint and run) stands on
## camera `cam`.
static func landmark_share(cam: CityIsoCamera, m: Dictionary, at: Transform3D, size: Vector2, pts: Array[Vector3] = []) -> float:
	if cam.perspective():
		return 0.0
	var oh := cam.ortho * size.y / maxf(size.x, 1.0)
	return landmark_box(cam, m, at, pts).size.y / maxf(oh, 0.001)


## The HQ-run page's camera: `page_camera`, widened and re-centred to hold every
## point of `pts` (the run's nodes and its entry) `margin_px` inside the view (inside
## `free_rect` instead when it has an area: the part of the page its chrome leaves free) when
## the reference framing leaves one out (the entry stands outside some compounds' framing), up
## to `max_share` times the reference ortho. An orthographic view fits the points and centres
## them in the free part; a perspective view keeps its width. Either then aims at the points'
## middle (`cfg.hq_run_fit_pans` passes) and steps back (`ortho` times `cfg.hq_run_fit_step`)
## until every point is in.
static func run_camera(cfg: CityConfig, m: Dictionary, at: Transform3D, size: Vector2, pts: Array[Vector3], margin_px: float,
		max_share: float, free_rect: Rect2 = Rect2()) -> CityIsoCamera:
	var inner := free_rect if free_rect.has_area() else Rect2(Vector2.ZERO, size).grow(-margin_px)
	var cam := page_camera(cfg, m, at, size, pts, inner)
	if pts.is_empty() or _holds(cam, pts, inner):
		return cam
	var ref := cam.ortho
	if not cam.perspective():
		_fit_into(cam, pts, inner, size, ref, ref * max_share)
	for i in cfg.hq_run_fit_pans:
		if _holds(cam, pts, inner):
			break
		cam.pan_px(_screen_box(cam, pts).get_center() - inner.get_center())
	var widest := ref * (minf(max_share, cfg.hq_run_fit_share_perspective) if cam.perspective() else max_share)
	while cam.ortho < widest and not _holds(cam, pts, inner):
		cam.ortho = minf(cam.ortho * cfg.hq_run_fit_step, widest)
	# Still too tall at the widest: the top of the run (the Central Server and its chip) stays
	# in; the entry may sit under the foot.
	for i in cfg.hq_run_fit_pans:
		var top := _screen_box(cam, pts).position.y
		if top >= inner.position.y - 0.5:
			break
		cam.pan_px(Vector2(0.0, top - inner.position.y - cfg.hq_run_fit_slack_px))
	return cam


## Sets an orthographic `cam`'s width (clamped to [lo, hi]) and aim so the points' box fills
## at most `inner` (screen px of a `size` view) and sits at its centre.
static func _fit_into(cam: CityIsoCamera, pts: Array[Vector3], inner: Rect2, size: Vector2, lo: float, hi: float) -> void:
	var r := cam.right()
	var u := cam.up()
	var box := Rect2(Vector2(pts[0].dot(r), pts[0].dot(u)), Vector2.ZERO)
	for w in pts:
		box = box.expand(Vector2(w.dot(r), w.dot(u)))
	var need := maxf(box.size.x * size.x / maxf(inner.size.x, 1.0), box.size.y * size.x / maxf(inner.size.y, 1.0))
	cam.ortho = clampf(need, lo, hi)
	var oh := cam.ortho * size.y / size.x
	var xc := (inner.get_center().x / size.x - 0.5) * cam.ortho
	var yc := (0.5 - inner.get_center().y / size.y) * oh
	var c := box.get_center()
	var o := r * (c.x - xc) + u * (c.y - yc)
	var f := cam.forward()
	cam.target = o + f * ((0.0 - o.y) / f.y)


static func _screen_box(cam: CityIsoCamera, pts: Array[Vector3]) -> Rect2:
	var b := Rect2(cam.project(pts[0]), Vector2.ZERO)
	for w in pts:
		b = b.expand(cam.project(w))
	return b


static func _holds(cam: CityIsoCamera, pts: Array[Vector3], inner: Rect2) -> bool:
	for p in pts:
		if not inner.has_point(cam.project(p)):
			return false
	return true


## The Central Server's name on the compound (the manifest's, e.g. DISPATCH CORE).
static func server_name(m: Dictionary) -> String:
	return String((m.get("anchors", {}) as Dictionary).get("server_name", ""))
