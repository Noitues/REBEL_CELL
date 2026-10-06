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
## the Site whose won lights show (&"" for an HQ)}. A boss fight frames the corp's HQ (the
## Cell's: the staged DISPATCH canyon at the HQ run's camera, closer); a regular fight the
## run's Site lot; a Site without a lot falls back to the HQ. Pure.
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
		var lot: Vector2 = site_lots[site]
		var c := CityIsoCamera.make(cfg, CityIsoCamera.lot_to_world(cfg, lot, cfg.backdrop_site_lift), cfg.backdrop_site_ortho, size)
		return {"focus": "site", "stage": &"", "camera": c, "lot": lot, "won_site": site}
	var hq := NeonCity.hq_of(corp) + Vector2(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS) * 0.5
	var h := CityIsoCamera.make(cfg, CityIsoCamera.lot_to_world(cfg, hq, cfg.backdrop_hq_lift), cfg.backdrop_hq_ortho, size)
	return {"focus": "hq", "stage": &"", "camera": h, "lot": hq, "won_site": &""}

