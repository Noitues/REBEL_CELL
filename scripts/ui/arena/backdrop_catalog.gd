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
## {"focus": "compound" | "hq" | "site" | "site_landmark", "stage": the corp whose HQ compound
## is staged (the DISPATCH canyon) or &"", "camera": CityIsoCamera, "lot": the target's lot
## point, "won_site": the Site whose won lights show (&"" for an HQ), and for a fitted
## landmark "centre" / "top" (world) and, for a Site landmark, "landmark" (its corp)}. A boss
## fight frames the corp's whole HQ landmark (fit_box into backdrop_hq_frame; the Cell's: the
## staged DISPATCH canyon at the HQ run's camera, closer); a regular fight the corp's Site
## landmark stood on the run's Site lot (site_close_up_lot: kept clear of the city's edge;
## fit into backdrop_site_frame), else that lot's nearest building; a Site without a lot
## falls back to the HQ. Pure apart from reading the landmark glTFs' boxes.
static func city_shot(cfg: CityConfig, p: Dictionary, site_lots: Dictionary, size: Vector2) -> Dictionary:
	var corp: StringName = p.get("corp", DEFAULT_CORP)
	var site: StringName = p.get("site", &"")
	var boss := StringName(p.get("kind", KIND_HQ)) == KIND_HQ
	if boss and corp == CityView3D.CELL:
		var m := HqCompoundStage.manifest(corp)
		var at := HqCompoundStage.place(cfg, corp, m)
		var cam := HqCompoundStage.camera(cfg, m, at, size)
		cam.ortho *= cfg.backdrop_canyon_share
		return {"focus": "compound", "stage": corp, "camera": cam, "lot": HqCompoundStage.place_lot(corp, m), "won_site": &""}
	if not boss and site_lots.has(site):
		var lot := site_close_up_lot(cfg, site_lots[site])
		var landmark := CityLandmarks.site_path(corp)
		if landmark != "":
			# S-ARENA (BACKDROP-02): the corp's Site building stands on the Site's lot, framed.
			var at := lot.floor() + Vector2(0.5, 0.5)
			var box := landmark_box(cfg, landmark, at)
			var sc := fit_box(cfg, box, cfg.backdrop_site_frame, cfg.backdrop_site_ortho, size, cfg.backdrop_site_pitch_deg)
			return {"focus": "site_landmark", "stage": &"", "camera": sc, "lot": at, "won_site": site, "centre": box.get_center(),
				"landmark": corp, "top": Vector3(box.get_center().x, box.end.y, box.get_center().z)}
		var c := CityIsoCamera.make(cfg, CityIsoCamera.lot_to_world(cfg, lot, cfg.backdrop_site_lift), cfg.backdrop_site_ortho, size)
		c.pitch_deg = cfg.backdrop_site_pitch_deg
		return {"focus": "site", "stage": &"", "camera": c, "lot": lot, "won_site": site}
	var hq := NeonCity.hq_of(corp) + Vector2(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS) * 0.5
	var path := hq_landmark_path(corp)
	if path != "":
		# S-ARENA (BACKDROP-01): the whole HQ landmark (Solace's helix top included) between the
		# top bar and the hand (per corp: backdrop_hq_frame_by_corp / backdrop_hq_ortho_by_corp).
		var hbox := landmark_box(cfg, path, hq, corp)
		var least: float = cfg.backdrop_hq_ortho_by_corp.get(corp, cfg.backdrop_hq_ortho)
		var fc := fit_box(cfg, hbox, cfg.backdrop_hq_frame_by_corp.get(corp, cfg.backdrop_hq_frame), least, size, cfg.backdrop_hq_pitch_deg)
		return {"focus": "hq", "stage": &"", "camera": fc, "lot": hq, "won_site": &"", "centre": hbox.get_center(),
			"top": Vector3(hbox.get_center().x, hbox.end.y, hbox.get_center().z)}
	var h := CityIsoCamera.make(cfg, CityIsoCamera.lot_to_world(cfg, hq, cfg.backdrop_hq_lift), cfg.backdrop_hq_ortho_by_corp.get(corp, cfg.backdrop_hq_ortho), size)
	return {"focus": "hq", "stage": &"", "camera": h, "lot": hq, "won_site": &""}


## The lot the close-up stands a Site on: its layout point, kept backdrop_site_inset lots
## inside the city's edge (CityConfig.city_rect) so the close-up shows city all round (the
## Sites of a territory at the edge would leave half the frame the bare plane past it). Pure.
static func site_close_up_lot(cfg: CityConfig, lot: Vector2) -> Vector2:
	var r := Rect2(cfg.city_rect).grow(-float(cfg.backdrop_site_inset))
	return lot.clamp(r.position, r.end)
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


## A camera at the city's yaw and pitch `pitch_deg` that fits world box `box` into `frame` (share of the view)
## with its centre at the frame's centre; ortho at least `least` (the close-up never zooms in
## past the plain framing). Pure.
static func fit_box(cfg: CityConfig, box: AABB, frame: Rect2, least: float, size: Vector2, pitch_deg: float) -> CityIsoCamera:
	var c := CityIsoCamera.make(cfg, box.get_center(), least, size)
	c.pitch_deg = pitch_deg
	var r := c.right()
	var u := c.up()
	var lo := Vector2(INF, INF)
	var hi := Vector2(-INF, -INF)
	for k in 8:
		var p := box.get_endpoint(k) - box.get_center()
		var q := Vector2(p.dot(r), p.dot(u))
		lo = lo.min(q)
		hi = hi.max(q)
	var aspect := size.y / maxf(1.0, size.x)
	c.ortho = maxf(least, maxf((hi.x - lo.x) / maxf(0.01, frame.size.x), (hi.y - lo.y) / maxf(0.01, frame.size.y * aspect)))
	# Move the box's middle onto the frame's middle (screen share -> world along right / up).
	var mid := (lo + hi) * 0.5
	var want := frame.get_center()
	var oh := c.ortho * aspect
	var dx := mid.x - (want.x - 0.5) * c.ortho
	var dy := mid.y - (0.5 - want.y) * oh
	c.target = box.get_center() + r * dx + u * dy
	return c


## The close-up's lit night look (CityConfig backdrop_*), for CityView3D.set_night_share at
## night share 0: the concept stills' blue-grey rainy city, rain kept; the landmarks in their
## day look for a corp HQ shot, night for a Site or the neon DISPATCH canyon (`focus`: the shot's, CityConfig
## backdrop_hq_landmarks_night / backdrop_site_landmarks_night).
static func city_look(cfg: CityConfig, focus: String = "hq") -> Dictionary:
	var lm_night := cfg.backdrop_hq_landmarks_night if focus == "hq" else cfg.backdrop_site_landmarks_night
	return {"ramp": cfg.backdrop_ramp.duplicate(), "sky": cfg.backdrop_sky, "window_gain": cfg.backdrop_window_gain,
		"neon_gain": cfg.backdrop_neon_gain, "haze": cfg.backdrop_haze, "grade": cfg.backdrop_grade,
		"bloom": cfg.backdrop_bloom, "glow_threshold": cfg.backdrop_glow_threshold, "night": true,
		"landmarks_night": lm_night}

