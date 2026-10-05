class_name BackdropCatalog
extends RefCounted
## Which combat backdrop a fight stands in front of (ART_BIBLE v2 §3.14, DECISIONS D17, built on its
## plan default pending the designer): a boss fight in front of its corporation's HQ, a regular fight
## at the target Site; night is the reference, day is the cool day. The stills are bakes of the
## concept generator scripts (art-concepts-r43, rounds 26 / 31 / 34) until ART-5's city lands: this
## file is the one seam ART-5 swaps (`still_path` / `won_mask_path` / `anchor`). Presentation only:
## it reads the campaign and the fight, never changes them.

const DIR := "res://assets/backdrops/combat/"
const KIND_BOSS := &"boss"
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
	&"meridian_boss": Vector2(0.47, 0.16), &"meridian_site": Vector2(0.50, 0.27),
	&"solace_boss": Vector2(0.50, 0.16), &"solace_site": Vector2(0.48, 0.29),
	&"halcyon_boss": Vector2(0.50, 0.16), &"halcyon_site": Vector2(0.50, 0.23),
	&"orbital_boss": Vector2(0.50, 0.16), &"orbital_site": Vector2(0.51, 0.16),
	&"rebel_cell_boss": Vector2(0.50, 0.16), &"rebel_cell_site": Vector2(0.50, 0.16),
}
## The anchor when a place has none.
const ANCHOR_FALLBACK := Vector2(0.5, 0.2)
## Places whose fight-won look is another still rather than a lights mask: the DISPATCH canyon's
## hijacked signs give way to the Cell's own street (the HOME canyon).
const WON_STILLS := {&"rebel_cell_boss": "rebel_cell_site_night"}


## The place a fight stands in: {corp, kind (boss | site), day}.
static func place(corporation_id: StringName, boss: bool, day: bool) -> Dictionary:
	var corp := corporation_id if corporation_id != &"" else DEFAULT_CORP
	return {"corp": corp, "kind": KIND_BOSS if boss else KIND_SITE, "day": day and not NIGHT_ONLY.has(corp)}


## Whether this campaign's current run plays by day (see DAY_EVERY); no campaign: night.
static func is_day(campaign: CampaignState) -> bool:
	return campaign != null and posmod(campaign.runs_started, DAY_EVERY) == DAY_REMAINDER


## The place of a fight against `enemies` (EnemyData of each foe that is not a satellite) in
## `campaign`: the corporation is the campaign's, else the first enemy's.
static func place_for(campaign: CampaignState, enemies: Array[EnemyData]) -> Dictionary:
	var corp: StringName = campaign.corporation_id if campaign != null else &""
	var boss := false
	for e in enemies:
		if e == null:
			continue
		boss = boss or e.is_boss
		if corp == &"":
			corp = e.corporation_id
	return place(corp, boss, is_day(campaign))


## The file name stem of `p` (corp_kind_time).
static func stem(p: Dictionary) -> String:
	return "%s_%s_%s" % [String(p["corp"]), String(p["kind"]), "day" if bool(p["day"]) else "night"]


## The still for `p`: its own, else the night one, else the corporation's boss night, else the default.
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
	boss["kind"] = KIND_BOSS
	var fallback := place(DEFAULT_CORP, true, false)
	var out: Array[String] = [stem(p), stem(night), stem(boss), stem(fallback)]
	return out
