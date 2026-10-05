class_name CorpHouseStyle
extends RefCounted
## ART-11 4D (ART_BIBLE v2 §4.8, ref `campaign_end/round20_raid_world/campaign_lost.jpg`): the
## winning corporation's ransomware house style for the campaign lost lock (option A), and its
## letterhead on the audit dossier: who beat the Cell, in their own words and with their own
## verb (PROCESSED / RECLAIMED / TREATED / DE-ORBITED / OVERWRITTEN). Words are keys (one tr
## where they show); colours are Palette tokens; the hue is the corporation's own. Pure look
## data: it reads no state.

## The full-screen motif the takeover lays over the city (round 20 `motif`).
enum Motif { BLUEPRINT, HAZARD, CELLS, STARS, GLITCH }
## The face the notice's head line uses (round 20: Bahnschrift, Anton, Plex, Bahnschrift,
## marker; v2 §2.9 keeps DISPATCH on Share Tech Mono, so its marker head becomes mono).
enum Face { LETTERHEAD, DISPLAY, MONO }

var corp_id: StringName = &""
## The house's name on the notice ("" = the corporation's own display name).
var house_name: String = ""
var head: String = ""
var sub: String = ""
var verb: String = ""
var ref: String = ""
var division: String = ""
var auditor: String = ""
var motif: int = Motif.BLUEPRINT
var face: int = Face.LETTERHEAD

## Each corporation's words (keys; round 20 lost20.py CORP_STYLE, round 21 letterhead). Solace's
## verb is TREATED (the bible's locked verb list; the concept sheet stamped STERILE).
const HEADS := {&"halcyon": "YOUR CELL HAS BEEN PROCESSED", &"meridian": "CARGO RECLAIMED", &"solace": "YOUR CELL HAS BEEN TREATED", # TR
	&"orbital": "SIGNAL DE-ORBITED", &"rebel_cell": "DISPATCH HAS YOUR CELL"} # TR
const SUBS := {&"halcyon": "Civic Order 7/88: network assets taken, operatives reclassified.", # TR
	&"meridian": "Manifest closed: every node repossessed under freight lien.", # TR
	&"solace": "Infection contained. Please remain calm while we sterilise your network.", # TR
	&"orbital": "Your uplink has been reassigned to the commons. Burn-up in progress.", # TR
	&"rebel_cell": "you were always a copy. the original sends its regards."} # TR
const VERBS := {&"halcyon": "PROCESSED", &"meridian": "RECLAIMED", &"solace": "TREATED", &"orbital": "DE-ORBITED", &"rebel_cell": "OVERWRITTEN"} # TR
const REFS := {&"halcyon": "REF HC-7718/CELL", &"meridian": "MANIFEST MF-0041-C", &"solace": "CASE SB-2210/QUARANTINE", # TR
	&"orbital": "TLE OC-55 / DECAY", &"rebel_cell": "DISPATCH // ECHO 00"} # TR
const DIVISIONS := {&"halcyon": "COMPLIANCE DIVISION", &"meridian": "LIEN RECOVERY", &"solace": "CONTAINMENT OFFICE", # TR
	&"orbital": "TRAFFIC CONTROL", &"rebel_cell": "ECHO"} # TR
## Who files the audit dossier (round 21: "filed by: A. VANCE, AUDIT 7"; names, not words).
const AUDITORS := {&"halcyon": "A. VANCE", &"meridian": "R. OKAFOR", &"solace": "DR. L. MERCER", &"orbital": "K. TANAKA", &"rebel_cell": "ECHO 00"}
## A house that signs with a name other than the corporation's (keys).
const NAMES := {&"rebel_cell": "DISPATCH"} # TR
const MOTIFS := {&"halcyon": Motif.BLUEPRINT, &"meridian": Motif.HAZARD, &"solace": Motif.CELLS, &"orbital": Motif.STARS, &"rebel_cell": Motif.GLITCH}
const FACES := {&"halcyon": Face.LETTERHEAD, &"meridian": Face.DISPLAY, &"solace": Face.LETTERHEAD, &"orbital": Face.LETTERHEAD, &"rebel_cell": Face.MONO}
## The style a corporation without one of its own wears (Halcyon's: the civic default).
const FALLBACK := &"halcyon"


## The house style of corporation `corporation_id` (FALLBACK's words for an unknown one, in
## that corporation's own hue).
static func of(corporation_id: StringName) -> CorpHouseStyle:
	var s := CorpHouseStyle.new()
	s.corp_id = corporation_id
	var k := corporation_id if HEADS.has(corporation_id) else FALLBACK
	s.house_name = String(NAMES.get(k, ""))
	s.head = String(HEADS[k])
	s.sub = String(SUBS[k])
	s.verb = String(VERBS[k])
	s.ref = String(REFS[k])
	s.division = String(DIVISIONS[k])
	s.auditor = String(AUDITORS[k])
	s.motif = int(MOTIFS[k])
	s.face = int(FACES[k])
	return s


## The corporations with a house style of their own, in id order.
static func known_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for k in HEADS:
		out.append(k)
	out.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	return out


## The house's hue (the corporation's own colour).
func color() -> Color:
	return Palette.corp_color(corp_id)


## The notice's back (dark, in the house's hue family).
func back() -> Color:
	return Palette.END_HOUSE_BACK.get(corp_id, Palette.END_HOUSE_BACK[FALLBACK])


## The house's accent: the countdown, the progress, the padlocks and the verb stamp.
func accent() -> Color:
	return Palette.END_HOUSE_ACCENT.get(corp_id, Palette.END_HOUSE_ACCENT[FALLBACK])


## The house's name as the notice prints it (translated): its own (DISPATCH) or `display_name`.
func name_shown(display_name: String) -> String:
	return TranslationServer.translate(house_name) if house_name != "" else display_name


## The notice's head-line face.
func head_font() -> Font:
	match face:
		Face.DISPLAY:
			return Palette.display()
		Face.MONO:
			return Palette.mono()
	return Palette.body_medium()
