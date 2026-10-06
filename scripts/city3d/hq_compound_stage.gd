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


## The HQ-run page's camera: the manifest's (`camera`), widened and re-centred to hold every
## point of `pts` (the run's nodes and its entry) `margin_px` inside the view when the
## reference framing leaves one out (the entry stands outside some compounds' framing), up to
## `max_share` times the reference ortho.
static func run_camera(cfg: CityConfig, m: Dictionary, at: Transform3D, size: Vector2, pts: Array[Vector3], margin_px: float,
		max_share: float) -> CityIsoCamera:
	var cam := camera(cfg, m, at, size)
	var inner := Rect2(Vector2.ZERO, size).grow(-margin_px)
	var all_in := true
	for p in pts:
		if not inner.has_point(cam.project(p)):
			all_in = false
			break
	if all_in or pts.is_empty():
		return cam
	var ref := cam.ortho
	var margin_bu := margin_px * ref / maxf(size.x, 1.0)
	cam.fit(pts, margin_bu, ref, ref * max_share)
	return cam


## The Central Server's name on the compound (the manifest's, e.g. DISPATCH CORE).
static func server_name(m: Dictionary) -> String:
	return String((m.get("anchors", {}) as Dictionary).get("server_name", ""))
