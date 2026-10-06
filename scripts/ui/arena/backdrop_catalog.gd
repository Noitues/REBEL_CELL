class_name BackdropCatalog
extends RefCounted
## Which combat backdrop a fight stands in front of (ART_BIBLE v2 §3.14, DECISIONS D17, built on its
## plan default pending the designer): a boss fight in front of its corporation's HQ, a regular fight
## at the target Site; night is the reference, day is the cool day. The stills are bakes of the
## concept generator scripts (art-concepts-r43, rounds 26 / 31 / 34) until ART-5's city lands: this
## file is the one seam ART-5 swaps (`still_path` / `won_mask_path` / `anchor`). Presentation only:
## it reads the campaign and the fight, never changes them.

const DIR := "res://assets/backdrops/combat/"
const KIND_HQ := &"hq"
const KIND_SITE := &"site"
## The fallback corporation when a fight names none (the standalone combat scene's picker).
const DEFAULT_CORP := &"meridian"
## A campaign's runs alternate night and the cool day: the run count's remainder by this picks day
## when it equals DAY_REMAINDER (DECISIONS "Art direction — ART-2 2B": the game has no clock yet).
const DAY_EVERY := 2
const DAY_REMAINDER := 1
## Corporations whose backdrops exist only at night (the REBEL_CELL canyon is a neon night street).
const NIGHT_ONLY: Array[StringName] = [&"rebel_cell"]
## Top-centre of each target's silhouette (share of the still), where "OURS NOW" is pencilled once
## the fight is won; measured from the won masks (the bake's silhouette pass).
const ANCHORS := {
	&"meridian_hq": Vector2(0.47, 0.16), &"meridian_site": Vector2(0.50, 0.27),
	&"solace_hq": Vector2(0.50, 0.16), &"solace_site": Vector2(0.48, 0.29),
	&"halcyon_hq": Vector2(0.50, 0.16), &"halcyon_site": Vector2(0.50, 0.23),
	&"orbital_hq": Vector2(0.50, 0.16), &"orbital_site": Vector2(0.51, 0.16),
	&"rebel_cell_hq": Vector2(0.50, 0.16), &"rebel_cell_site": Vector2(0.50, 0.16),
}
## The anchor when a place has none.
const ANCHOR_FALLBACK := Vector2(0.5, 0.2)
## Places whose fight-won look is another still rather than a lights mask: the DISPATCH canyon's
## hijacked signs give way to the Cell's own street (the HOME canyon).
const WON_STILLS := {&"rebel_cell_hq": "rebel_cell_site_night"}


## The place a fight stands in: {corp, kind (hq for a boss fight | site), day, site (the
## run's Site id, &"" when none)}.
static func place(corporation_id: StringName, boss: bool, day: bool, site_id: StringName = &"") -> Dictionary:
	var corp := corporation_id if corporation_id != &"" else DEFAULT_CORP
	return {"corp": corp, "kind": KIND_HQ if boss else KIND_SITE, "day": day and not NIGHT_ONLY.has(corp), "site": site_id}


## Whether this campaign's current run plays by day (see DAY_EVERY); no campaign: night.
static func is_day(campaign: CampaignState) -> bool:
	return campaign != null and posmod(campaign.runs_started, DAY_EVERY) == DAY_REMAINDER


## The place of a fight against `enemies` (EnemyData of each foe that is not a satellite) in
## `campaign`: the corporation is the campaign's, else the first enemy's.
static func place_for(campaign: CampaignState, enemies: Array[EnemyData], site_id: StringName = &"") -> Dictionary:
	var corp: StringName = campaign.corporation_id if campaign != null else &""
	var boss := false
	for e in enemies:
		if e == null:
			continue
		boss = boss or e.is_boss
		if corp == &"":
			corp = e.corporation_id
	return place(corp, boss, is_day(campaign), site_id)


## The file name stem of `p` (corp_kind_time).
static func stem(p: Dictionary) -> String:
	return "%s_%s_%s" % [String(p["corp"]), String(p["kind"]), "day" if bool(p["day"]) else "night"]


## The still for `p`: its own, else the night one, else the corporation's HQ night, else the default.
static func still_path(p: Dictionary) -> String:
	for s in _candidates(p):
		var path := DIR + s + ".jpg"
		if ResourceLoader.exists(path):
			return path
	return ""


## The won mask that goes with `still_path(p)` (R = the target's silhouette, G = its lights), or "".
static func won_mask_path(p: Dictionary) -> String:
	var still := still_path(p)
	if still == "":
		return ""
	var path := still.trim_suffix(".jpg") + "_won.png"
	return path if ResourceLoader.exists(path) else ""


## The still a won fight crossfades to (see WON_STILLS), or "" when the won look is the lights mask.
static func won_still_path(p: Dictionary) -> String:
	var s: String = WON_STILLS.get(StringName("%s_%s" % [String(p["corp"]), String(p["kind"])]), "")
	if s == "":
		return ""
	var path := DIR + s + ".jpg"
	return path if ResourceLoader.exists(path) else ""


## Where "OURS NOW" stands on the still (share of its size).
static func anchor(p: Dictionary) -> Vector2:
	return ANCHORS.get(StringName("%s_%s" % [String(p["corp"]), String(p["kind"])]), ANCHOR_FALLBACK)


static func _candidates(p: Dictionary) -> Array[String]:
	var night := p.duplicate()
	night["day"] = false
	var boss := night.duplicate()
	boss["kind"] = KIND_HQ
	var fallback := place(DEFAULT_CORP, true, false)
	var out: Array[String] = [stem(p), stem(night), stem(boss), stem(fallback)]
	return out


# --- D17 on the city (ART-8 8w): the backdrop is a close-up of the one city ------------------

## True when the backdrop is the city's close-up: a renderer, and the city quality tier
## `tier` (CityConfig.tier_for) takes it (CityConfig.backdrop_city_tiers); else the stills.
static func city_mode(cfg: CityConfig, tier: int, can_render: bool) -> bool:
	return can_render and tier >= 0 and tier < cfg.backdrop_city_tiers.size() and cfg.backdrop_city_tiers[tier]


## The city close-up of place `p` (`site_lots`: Site id -> lot point, CityLayout.site_points):
## {"focus": "compound" | "hq" | "site", "stage": the corp whose HQ compound is staged (the
## DISPATCH canyon) or &"", "camera": CityIsoCamera, "lot": the target's lot point, "won_site":
## the Site whose won lights show (&"" for an HQ), "centre" / "top" (world) of what is framed,
## for a Site "hq_box" (the HQ in its back) and, when the fought Site is the one carrying the
## corp's Site landmark, "landmark" (its corp)}. A boss fight is the special view: the corp's
## whole HQ landmark fitted into backdrop_hq_frame (the Cell's: the staged DISPATCH canyon at
## the HQ run's camera, closer). A regular fight frames the fought Site's own lot, looking from
## it toward the corp's HQ so the HQ stands in the back of the shot (site_shot); a Site without
## a lot falls back to the HQ. Pure apart from reading the landmark glTFs' boxes.
static func city_shot(cfg: CityConfig, p: Dictionary, site_lots: Dictionary, size: Vector2) -> Dictionary:
	var corp: StringName = p.get("corp", DEFAULT_CORP)
	var site: StringName = p.get("site", &"")
	var boss := StringName(p.get("kind", KIND_HQ)) == KIND_HQ
	if boss and corp == CityView3D.CELL:
		var m := HqCompoundStage.manifest(corp)
		var at := HqCompoundStage.place(cfg, corp, m)
		var cam := HqCompoundStage.page_camera(cfg, m, at, size)  # B2 (D1): the canyon's own perspective street view
		cam.ortho *= cfg.backdrop_canyon_share
		return {"focus": "compound", "stage": corp, "camera": cam, "lot": HqCompoundStage.place_lot(corp, m), "won_site": &""}
	if not boss and site_lots.has(site):
		return site_shot(cfg, corp, site, site_lots, size)
	var hq := hq_lot(corp)
	var path := hq_landmark_path(corp)
	if path != "":
		# S-ARENA (BACKDROP-01): the whole HQ landmark (Solace's helix top included) between the
		# top bar and the hand (per corp: backdrop_hq_frame_by_corp / backdrop_hq_ortho_by_corp).
		var hbox := landmark_box(cfg, path, hq, corp)
		var least: float = cfg.backdrop_hq_ortho_by_corp.get(corp, cfg.backdrop_hq_ortho)
		var fc := fit_box(cfg, hbox, cfg.backdrop_hq_frame_by_corp.get(corp, cfg.backdrop_hq_frame), least, size, cfg.backdrop_close_pitch_deg)
		return {"focus": "hq", "stage": &"", "camera": fc, "lot": hq, "won_site": &"", "centre": hbox.get_center(),
			"top": Vector3(hbox.get_center().x, hbox.end.y, hbox.get_center().z), "subject": hbox}
	var h := CityIsoCamera.make(cfg, CityIsoCamera.lot_to_world(cfg, hq, cfg.backdrop_hq_lift), cfg.backdrop_hq_ortho_by_corp.get(corp, cfg.backdrop_hq_ortho), size)
	h.pitch_deg = cfg.backdrop_close_pitch_deg  # B2 (D1): the perspective close-up here too
	h.fov_deg = cfg.backdrop_close_fov_deg
	return {"focus": "hq", "stage": &"", "camera": h, "lot": hq, "won_site": &""}


## The centre lot point of `corp`'s HQ (NeonCity's HQ block).
static func hq_lot(corp: StringName) -> Vector2:
	return NeonCity.hq_of(corp) + Vector2(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS) * 0.5


## The world box of `corp`'s HQ as a Site shot's back: its landmark's body, else a block of
## backdrop_site_hq_height over its HQ lots.
static func hq_box(cfg: CityConfig, corp: StringName) -> AABB:
	var hq := hq_lot(corp)
	var path := hq_landmark_path(corp)
	if path != "":
		return landmark_box(cfg, path, hq, corp)
	var half := float(NeonCity.HQ_LOTS) * 0.5 * cfg.lot_bu
	var c := CityIsoCamera.lot_to_world(cfg, hq)
	return AABB(c - Vector3(half, 0.0, half), Vector3(half * 2.0, cfg.backdrop_site_hq_height, half * 2.0))


## Parity fix S-ARENA round 2 (designer 2026-10-05: every fight gets its own backdrop; this is
## the placeholder): a regular fight's shot of the fought Site's own lot (its layout point,
## never moved). The subject is the Site's building (`subject`: its world box, CombatBackdrop
## measures it on the model; else the corp's Site landmark when this Site carries it, else a
## nominal block of backdrop_site_reach lots, backdrop_site_height tall), fitted large into
## backdrop_site_frame at backdrop_close_pitch_deg (B2: in perspective); the camera looks from it toward the corp's
## HQ (yaw on the Site -> HQ line) and zooms out round the subject, by backdrop_site_zoom_step,
## while the subject keeps backdrop_site_subject_min of the view's width, until the HQ shows in the back (its point at
## backdrop_site_hq_show of its height below backdrop_site_hq_top of the view). Pure.
static func site_shot(cfg: CityConfig, corp: StringName, site: StringName, site_lots: Dictionary, size: Vector2, subject: AABB = AABB()) -> Dictionary:
	var lot: Vector2 = site_lots[site]
	var own := CityLandmarks.site_of(cfg, corp) == site and CityLandmarks.site_path(corp) != ""
	var at := CityLandmarks.site_lot(cfg, corp, site_lots) if own else lot
	var sbox := subject
	if sbox.size != Vector3.ZERO:
		var grow := Vector2(maxf(0.0, cfg.backdrop_site_subject_span - sbox.size.x), maxf(0.0, cfg.backdrop_site_subject_span - sbox.size.z)) * 0.5
		sbox = AABB(sbox.position - Vector3(grow.x, 0.0, grow.y), sbox.size + Vector3(grow.x, 0.0, grow.y) * 2.0)
	if sbox.size == Vector3.ZERO:
		if own:
			sbox = landmark_box(cfg, CityLandmarks.site_path(corp), at)
		else:
			var half := float(cfg.backdrop_site_reach) * cfg.lot_bu
			var c := CityIsoCamera.lot_to_world(cfg, at)
			sbox = AABB(c - Vector3(half, 0.0, half), Vector3(half * 2.0, cfg.backdrop_site_height, half * 2.0))
	var hbox := hq_box(cfg, corp)
	var yaw := site_yaw(cfg, sbox.get_center(), hbox.get_center())
	var cam := fit_box(cfg, sbox, cfg.backdrop_site_frame, cfg.backdrop_site_ortho, size, cfg.backdrop_close_pitch_deg, yaw)
	var base := cam.ortho
	var hq_pt := Vector3(hbox.get_center().x, hbox.position.y + hbox.size.y * cfg.backdrop_site_hq_show, hbox.get_center().z)
	var ext := _screen_extent(cam, sbox).size
	var widest := maxf(base, maxf(ext.x, ext.y * size.x / maxf(1.0, size.y)) / maxf(0.01, cfg.backdrop_site_subject_min))
	while cam.project(hq_pt).y < cfg.backdrop_site_hq_top * size.y and cam.ortho * cfg.backdrop_site_zoom_step <= widest:
		cam.ortho *= cfg.backdrop_site_zoom_step
		aim(cam, sbox, cfg.backdrop_site_frame.get_center())
	var out := {"focus": "site", "stage": &"", "camera": cam, "lot": at, "won_site": site, "centre": sbox.get_center(),
		"top": Vector3(sbox.get_center().x, sbox.end.y, sbox.get_center().z), "subject": sbox, "hq_box": hbox}
	if own:
		out["landmark"] = corp
	return out


## The chunk keys (CityModel's grid, sorted row by row) round lot point `lot` (within
## backdrop_extend_lots) that model chunks `have` (key -> {"rect"}) lack in full: the city past
## city_rect's edge (cut chunks included), which a Site shot's close-up records for itself so
## no bare plane shows round a Site at the edge. Pure.
static func extension_keys(cfg: CityConfig, lot: Vector2, have: Dictionary) -> Array[Vector2i]:
	var n := cfg.chunk_lots
	var r := float(cfg.backdrop_extend_lots)
	var lo := Vector2i(floori((lot.x - r) / n), floori((lot.y - r) / n))
	var hi := Vector2i(floori((lot.x + r) / n), floori((lot.y + r) / n))
	var out: Array[Vector2i] = []
	for y in range(lo.y, hi.y + 1):
		for x in range(lo.x, hi.x + 1):
			var k := Vector2i(x, y)
			var full := Rect2i(k * n, Vector2i(n, n))
			if not have.has(k) or (have[k]["rect"] as Rect2i) != full:
				out.append(k)
	return out


## The yaw (degrees) a Site shot looks along: of the city's own four diagonal views (yaw_deg +
## k * 90, the iso look and its light kept), the one that looks most from the Site toward its
## corp's HQ (the HQ in the back; ties: the lower k). Sites lie near the city's edge and their
## HQ inward, so the bare plane past the edge stays behind the camera. Pure.
static func site_yaw(cfg: CityConfig, from: Vector3, to: Vector3) -> float:
	var d := Vector2(to.x - from.x, to.z - from.z)
	if d.length() < 0.001:
		return cfg.yaw_deg
	var best := cfg.yaw_deg
	var best_dot := -INF
	for k in 4:
		var yaw := cfg.yaw_deg + 90.0 * k
		var f := Vector2(cos(deg_to_rad(yaw)), -sin(deg_to_rad(yaw)))
		var dot := f.dot(d.normalized())
		if dot > best_dot + 0.000001:
			best_dot = dot
			best = yaw
	return best
## The HQ landmark glTF of `corp` ("" when it has none: the stand-in tower).
static func hq_landmark_path(corp: StringName) -> String:
	var p := "%s/%s/%s_hq.glb" % [CityLandmarks.DIR, corp, corp]
	return p if ResourceLoader.exists(p) else ""


## The world box of landmark glTF `path` standing on lot point `lot` (as CityView3D places it),
## only its meshes named with a word of CityConfig.backdrop_fit_keep (the body, not the beams
## and rays spread over the ground; for an HQ `corp` listed in backdrop_hq_fit_keep_by_corp, its
## words); CityLandmarks.box_of when none is.
static func landmark_box(cfg: CityConfig, path: String, lot: Vector2, corp: StringName = &"") -> AABB:
	var keep: PackedStringArray = cfg.backdrop_hq_fit_keep_by_corp.get(corp, cfg.backdrop_fit_keep)
	var key := "%s|%s" % [path, ",".join(keep)]
	if not _fit_boxes.has(key):
		_fit_boxes[key] = _body_box(path, keep)
	var b: AABB = _fit_boxes[key]
	b.position += CityIsoCamera.lot_to_world(cfg, lot)
	return b


## Fitted landmark boxes (model space), cached per file and keep list.
static var _fit_boxes: Dictionary = {}


static func _body_box(path: String, keep: PackedStringArray) -> AABB:
	var scene := load(path) as PackedScene if ResourceLoader.exists(path) else null
	if scene == null:
		return CityLandmarks.box_of(path)
	var root := scene.instantiate() as Node3D
	var out := AABB()
	var first := true
	for mi in root.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		if m.mesh == null or not _kept(String(m.name), keep):
			continue
		var xf := Transform3D()
		var n: Node = m
		while n != null and n != root:
			xf = (n as Node3D).transform * xf
			n = n.get_parent()
		var b := xf * m.mesh.get_aabb()
		if b.size == Vector3.ZERO:
			continue  # an empty animation frame's mesh
		out = b if first else out.merge(b)
		first = false
	root.free()
	return CityLandmarks.box_of(path) if first else out


static func _kept(mesh_name: String, keep: PackedStringArray) -> bool:
	for w in keep:
		if mesh_name.contains(w):
			return true
	return false


## A camera at pitch `pitch_deg` (and yaw `yaw_deg`; NAN: the city's) that fits world box
## `box` into `frame` (share of the view) with its middle at the frame's middle; ortho at least
## `least` (the close-up never zooms in past the plain framing). B2 (D1): a perspective view
## (CityConfig.backdrop_close_fov_deg; `ortho` is its width at the target's depth): the plain
## fit is refined FIT_PASSES times on the box's projected corners (its near face draws larger).
## Pure.
static func fit_box(cfg: CityConfig, box: AABB, frame: Rect2, least: float, size: Vector2, pitch_deg: float, yaw_deg: float = NAN) -> CityIsoCamera:
	var c := CityIsoCamera.make(cfg, box.get_center(), least, size)
	c.pitch_deg = pitch_deg
	c.fov_deg = cfg.backdrop_close_fov_deg
	if not is_nan(yaw_deg):
		c.yaw_deg = yaw_deg
	var ext := _screen_extent(c, box)
	var aspect := size.y / maxf(1.0, size.x)
	c.ortho = maxf(least, maxf(ext.size.x / maxf(0.01, frame.size.x), ext.size.y / maxf(0.01, frame.size.y * aspect)))
	aim(c, box, frame.get_center())
	for i in FIT_PASSES:
		var px := projected_box(c, box)
		if not px.has_area():
			break
		var want := Rect2(frame.position * size, frame.size * size)
		var k := maxf(px.size.x / maxf(1.0, want.size.x), px.size.y / maxf(1.0, want.size.y))
		c.ortho = maxf(least, c.ortho * k)
		px = projected_box(c, box)
		if px.has_area():
			# Slide the view in its own plane so the box's middle lands on the frame's middle.
			var d := (px.get_center() - want.get_center()) * c.bu_per_px()
			c.target += c.right() * d.x - c.up() * d.y
	return c


## The screen box (px) of world box `box`'s eight corners through camera `c` (Rect2() when a
## corner is behind the eye).
static func projected_box(c: CityIsoCamera, box: AABB) -> Rect2:
	var out := Rect2()
	for k in 8:
		var p := c.project(box.get_endpoint(k))
		if not p.is_finite():
			return Rect2()
		out = Rect2(p, Vector2.ZERO) if k == 0 else out.expand(p)
	return out


## B2 (D1): refinement passes of a perspective fit.
const FIT_PASSES := 3


## B2 (D1): the street-level close-up's view cut for camera `c` on subject box `box`
## (CityView3D.set_view_cut takes `occludes` bound to it): only the procedural buildings that
## would hide the subject give way: nearer the eye than the subject's front (less
## CityConfig.backdrop_close_cut_margin), inside the wedge from the eye to the subject's sides
## (that margin wider), and taller than the sight line from the eye to the subject's height at
## backdrop_close_sight_share. Low roofs in front and the city to the sides stay (the concepts
## look over rooftops at the landmark). {eye, fwd, right, front, lo, hi, pad, base_y} (world). Pure.
static func view_cut(cfg: CityConfig, c: CityIsoCamera, box: AABB) -> Dictionary:
	var eye := c.eye()
	var f := c.forward()
	var fwd := Vector2(f.x, f.z).normalized()
	var right := Vector2(-fwd.y, fwd.x)
	var e2 := Vector2(eye.x, eye.z)
	var front := INF
	var lo := INF
	var hi := -INF
	for k in 8:
		var p := box.get_endpoint(k)
		var v := Vector2(p.x, p.z) - e2
		var d := maxf(v.dot(fwd), 0.001)
		front = minf(front, d)
		lo = minf(lo, v.dot(right) / d)
		hi = maxf(hi, v.dot(right) / d)
	return {"eye": eye, "fwd": fwd, "right": right, "front": front - cfg.backdrop_close_cut_margin, "sub": front,
		"lo": lo, "hi": hi, "pad": cfg.backdrop_close_cut_margin, "base_y": box.position.y + box.size.y * cfg.backdrop_close_sight_share}


## B2 (D1): whether a building at ground point `centre` (world X/Z) with its roof at `top` (BU)
## hides the subject of view cut `cut` (`view_cut`). Pure.
static func occludes(centre: Vector2, top: float, cut: Dictionary) -> bool:
	var eye: Vector3 = cut["eye"]
	var v := centre - Vector2(eye.x, eye.z)
	var d := v.dot(cut["fwd"])
	if d <= 0.0 or d >= float(cut["front"]):
		return false
	var s := v.dot(cut["right"])
	var pad := float(cut["pad"])
	if s < float(cut["lo"]) * d - pad or s > float(cut["hi"]) * d + pad:
		return false
	var line := eye.y + (float(cut["base_y"]) - eye.y) * d / maxf(float(cut["sub"]), 0.001)
	return top > line


## Moves camera `c`'s target (its ortho, yaw and pitch kept) so world box `box`'s screen middle
## lands at `want` (share of the view). Pure.
static func aim(c: CityIsoCamera, box: AABB, want: Vector2) -> void:
	var ext := _screen_extent(c, box)
	var mid := ext.get_center()
	var oh := c.ortho * c.viewport.y / maxf(1.0, c.viewport.x)
	var dx := mid.x - (want.x - 0.5) * c.ortho
	var dy := mid.y - (0.5 - want.y) * oh
	c.target = box.get_center() + c.right() * dx + c.up() * dy


## `box`'s extent in camera `c`'s right / up axes round its centre (world units).
static func _screen_extent(c: CityIsoCamera, box: AABB) -> Rect2:
	var r := c.right()
	var u := c.up()
	var lo := Vector2(INF, INF)
	var hi := Vector2(-INF, -INF)
	for k in 8:
		var p := box.get_endpoint(k) - box.get_center()
		var q := Vector2(p.dot(r), p.dot(u))
		lo = lo.min(q)
		hi = hi.max(q)
	return Rect2(lo, hi - lo)


## The close-up's lit night look (CityConfig backdrop_*), for CityView3D.set_night_share at
## night share 0: the concept stills' blue-grey rainy city, rain kept; the landmarks in their
## day look for a corp HQ shot, night for a Site or the neon DISPATCH canyon (`focus`: the shot's, CityConfig
## backdrop_hq_landmarks_night / backdrop_site_landmarks_night).
static func city_look(cfg: CityConfig, focus: String = "hq") -> Dictionary:
	var lm_night := cfg.backdrop_hq_landmarks_night if focus == "hq" else cfg.backdrop_site_landmarks_night
	return {"ramp": cfg.backdrop_ramp.duplicate(), "sky": cfg.backdrop_sky, "window_gain": cfg.backdrop_window_gain,
		"neon_gain": cfg.backdrop_neon_gain, "haze": cfg.backdrop_sky, "haze_k": cfg.backdrop_haze_k, "grade": cfg.backdrop_grade,
		"bloom": cfg.backdrop_bloom, "glow_threshold": cfg.backdrop_glow_threshold, "night": true,
		"landmarks_night": lm_night}

