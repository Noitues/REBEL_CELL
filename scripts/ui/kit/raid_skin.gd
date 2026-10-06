class_name RaidSkin
extends RefCounted
## ART-6 3A (ART_BIBLE v2 §1.2, §4.8 "Panels re-skin per raiding corp (one corp theme
## resource)"): the raiding corporation's house style for the raid's stolen documents (the
## work order, THREAT INTEL, the after-action report) and the raid's shared looks (grease
## pencil, holo, paper), built from the corporation id. View only: no rule reads it.

## Corporations whose kit the raid knows (the order every sheet and sweep walks).
const CORPS: Array[StringName] = [&"meridian", &"solace", &"halcyon", &"orbital", &"rebel_cell"]
## Each corporation's letterhead line under its name on the documents (ART_BIBLE §1.2 corp
## paper: letterhead per corp; round 21 report_doc).
const DIVISIONS := {
	&"meridian": "FREIGHT SECURITY  //  YARD OPERATIONS  //  CUSTOMS", # TR
	&"solace": "PATIENT RECOVERY  //  COLLECTIONS  //  COMPLIANCE", # TR
	&"halcyon": "CIVIC ORDER  //  PUBLIC SAFETY  //  COMPLIANCE", # TR
	&"orbital": "GROUND SEGMENT  //  DEBRIS CONTROL  //  LICENSING", # TR
	&"rebel_cell": "DISPATCH  //  INTERNAL AFFAIRS  //  CLEAN-UP", # TR
}
## Work-order number prefix per corp (round 21: "WO 50-HC-114").
const CODES := {&"meridian": "MF", &"solace": "SB", &"halcyon": "HC", &"orbital": "OC", &"rebel_cell": "RC"}
## The DECRYPTED holo's fill share of the corp tint (§1.2: corp tint at about 78 %).
const HOLO_TINT := 0.78
## Paper ink lightness steps for the letterhead colour (the corp hue darkened to read on paper).
const LETTERHEAD_DARKEN := 0.45

var corporation_id: StringName = &""
## The corp's own hue (§2.4).
var hue: Color = Palette.NET_CYAN
## Its hue darkened for ink on paper (letterhead, rule line, seal).
var paper_hue: Color = Palette.INK
## The holo's tint (the corp hue, a little lifted so dark kits still glow).
var holo: Color = Palette.NET_CYAN


static var _cache: Dictionary = {}


## The skin of corporation `corporation_id` (cached; a fresh one for an unknown id).
static func of(corporation_id: StringName) -> RaidSkin:
	if _cache.has(corporation_id):
		return _cache[corporation_id]
	var s := RaidSkin.new()
	s.corporation_id = corporation_id
	s.hue = Palette.corp_color(corporation_id)
	s.paper_hue = s.hue.darkened(LETTERHEAD_DARKEN)
	# A pale kit (Orbital's ice white) inks as its steel blue on paper (§2.4: its material
	# carries it, never the pale hue on pale stock).
	if Palette.luminance(s.paper_hue) > Palette.luminance(Palette.TEXT_LO) * 0.5:
		s.paper_hue = Palette.NIGHT_SKY.lerp(s.hue, 0.35)
	s.holo = s.hue.lerp(Palette.TEXT_HI, 0.12)
	_cache[corporation_id] = s
	return s


## The letterhead's division line, translated.
func division() -> String:
	return TranslationServer.translate(String(DIVISIONS.get(corporation_id, DIVISIONS[&"halcyon"])))


## The corporation's display name in capitals ("HALCYON CIVIC"), from content.
func corp_name() -> String:
	var corp: Resource = RunManager.lookup().get_content(corporation_id) if RunManager != null else null
	return (TextDb.t(corp, "display_name") if corp != null else String(corporation_id)).to_upper()


## A work-order number for raid `raid_id` (deterministic: the id's hash, never an RNG).
func order_number(raid_id: StringName, heat: int) -> String:
	var h := absi(hash(String(raid_id))) % 1000
	return "WO %02d-%s-%03d" % [clampi(heat, 0, 99), String(CODES.get(corporation_id, "XX")), h]

