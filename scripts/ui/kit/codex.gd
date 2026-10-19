class_name Codex
extends RefCounted
## Plain-text descriptions of game content and rules for inspect tooltips and the codex
## screen (GDD 8.1, 9.5). Reads content only; never changes state.

const SLICE_TYPE_TEXT := {
	RC.SliceType.SHIM: "SHIM: deals damage to whatever sits at each pointer of the target wheel.",
	RC.SliceType.OVERFLOW: "OVERFLOW: deals high damage to whatever sits at each pointer of the target wheel.",
	RC.SliceType.DEFRAG: "BLOCK: gains block. Block is removed at the end of the turn.",
	RC.SliceType.SANDBOX: "SHIELD: gains shield. Shield persists across turns (cap 15).",
	RC.SliceType.DETOUR: "SANDBOX: 1 charge (2 on a Perfect). Each charge negates one incoming hit whole, Pierce too. Charges are removed at the end of the turn.",
	RC.SliceType.TROJAN: "TROJAN: docks a drone on your wheel. It resolves when its slice does and takes hits aimed there.",
	RC.SliceType.HOTFIX: "HOTFIX: restores HP.",
	RC.SliceType.INFECT: "INFECT: applies a status or a drain to your wheel (Dose corrupts, Priority drains RAM, Citation plants a Parasite, Solar Flare overclocks).",
	RC.SliceType.NULL: "NULL: nothing happens, unless a Daemon says otherwise.",
}
const STATUS_TEXT := {
	RC.Status.CORRUPTED: "CORRUPTED: when the slice resolves, 3 self-damage (+1 per MAJOR Heat threshold) and -1 RAM. Lasts until cleansed.",
	RC.Status.OVERCLOCKED: "OVERCLOCKED: 1.5x output on the slice's next trigger, then it becomes CORRUPTED.",
	RC.Status.ENCRYPTED: "ENCRYPTED: absorbs the next status applied to that slice.",
	RC.Status.OUTPUT_DOWN: "OUTPUT DOWN: the slice resolves at 25% less output per stack. Stacks add up (a Botnet parasite or a Halcyon Citation plants 2: half output). Lasts until cleansed.",
}
const TIER_TEXT := {
	RC.PrecisionTier.PERFECT: "PERFECT (offset 0): full output and the class Perfect hook.",
	RC.PrecisionTier.GOOD: "GOOD (offset 1): full output.",
	RC.PrecisionTier.WEAK: "WEAK (offset 2): half output.",
}
## Original slang (GDD 8.1). Never borrowed from existing IP.
const LEXICON := {
	"leash": "A subscription implant. Miss a payment and it bricks.",
	"subbie": "Corporate word for a customer. On the street, an insult.",
	"bricked": "An implant shut off for non-payment.",
	"ghosting": "Running a netrun without leaving traces.",
	"Cycles": "Netrun currency. Unspent Cycles convert to Schematics at 10:1.",
	"Core Schematics": "Campaign currency: nodes, repairs, recruits, Heat scrubs, unlocks.",
	"Heat": "How hard the corporation is looking for you. Thresholds fire raids and complications.",
	"ICE": "Difficulty ladder, 20 cumulative levels.",
	"DISPATCH": "The Cell's handler. Clean system text, always.",
	"Priority": "Meridian's fast lane: an enemy slice that bills your RAM for it.",
	"Citation": "Halcyon's fine: a Parasite on one of your slices until you cleanse it.",
	"Solar Flare": "Orbital's gift: your slice runs hot once (1.5x), then corrupts.",
	"Weight": "Heavy freight resists nudges; some Meridian slices add resistance as they hit.",
	"Mirror": "A copy of one of your own operatives. You will know it when you meet it.",
	# Plan 2 B-CODEX: the combat words the Codex never defined (PB-PT-003b C3). Drafted from GDD 2.1-2.7, 4.3, 11.1.
	"Nudge": "Moves one ring one tick (Q/E). The first nudge each turn is free, then each costs 1 RAM. Each tick is absorbed by 1 resistance.", # TR
	"Free nudge": "One nudge per turn costs no RAM. It refreshes at the start of every turn. Extra nudges cost 1 RAM each.", # TR
	"Tick": "The smallest division of a wheel: 30 per wheel, 5 per slice. The tick under the pointer decides which slice resolves and how precisely.", # TR
	"RAM": "Combat energy. Gain +4 each turn, max 12. Spent on cards, extra nudges (1 each) and respins (4). Drains stop at 0; there is no RAM debt.", # TR
	"Null": "The empty slice. Landing on it is the only miss, since there is no miss tier. Fault Tolerance, Cold Exit and CORRUPTED react to it.", # TR
	"Resistance": "Enemy ability: absorbs the first R ticks of your nudges and spins. While resistance is above 0, Flip and Respin are blocked entirely.", # TR
	"Blocked": "An action refused or a hit stopped. Flip and Respin are blocked while resistance is above 0. A satellite docked at a pointer takes the attack instead (bodyguard).", # TR
	"Guard": "Block and shield together. Block expires at the start of your next turn; shield persists (cap 15). A docked satellite takes Pointer hits aimed at its host slice.", # TR
	"Heat thresholds": "MINOR every 10, MAJOR at 25/50/75, PURGE at 100. Bands: COOL, NOTICED, FLAGGED, HUNTED, PURGE. Events fire once, on first crossing. Modifiers apply while Heat is at or above the threshold.", # TR
}


## One-paragraph description of any content resource, for tooltips. W2-A3 (R2): a status the
## text names comes with its definition (HARDENED's "ENCRYPTED" says what ENCRYPTED does).
static func describe(res: Resource) -> String:
	return with_status_defs(_describe_base(res))


## `text` followed by the definition of every status it names that it does not define itself
## (in status order; one pass, so a definition's own mentions add nothing).
static func with_status_defs(text: String) -> String:
	if text == "":
		return text
	var out := text
	for st in STATUS_TEXT:
		var word := String(Palette.STATUS_WORDS.get(st, ""))
		var def: String = STATUS_TEXT[st]
		if word != "" and text.contains(word) and not text.contains(def):
			out += "\n" + def
	return out


static func _describe_base(res: Resource) -> String:
	if res == null:
		return ""
	if res is SliceData:
		var s := res as SliceData
		var head: String = s.display_name if s.display_name != "" else String(s.id)  # ART-2 2A: no text symbol (the atlas glyph is the icon)
		var out := "%s\n%s" % [head, SLICE_TYPE_TEXT.get(s.slice_type, "")]
		if s.base_output > 0:
			out += "\nBase output %d." % s.base_output
		for te in s.extra_effects:
			if te != null:
				out += "\n" + describe_triggered(te)
		return out
	if res is FirmwareData:
		var f := res as FirmwareData
		return "Firmware %s\n%s" % [f.display_name, f.description]
	if res is DaemonData:
		var d := res as DaemonData
		return "Daemon %s\n%s" % [d.display_name, d.description]
	if res is CardData:
		var c := res as CardData
		return "%s (RAM %d)\n%s%s" % [c.display_name, c.ram_cost, c.description, "\nExhaust." if c.exhaust else ""]
	if res is RingSegmentData:
		var r := res as RingSegmentData
		return "Ring segment %s\n%s" % [r.display_name, r.description]
	if res is HubCoreData:
		var h := res as HubCoreData
		return "Hub %s\n%s%s" % [h.display_name, h.description, ("\nResistance %d." % h.hub_resistance) if h.hub_resistance > 0 else ""]
	if res is EnemyData:
		var e := res as EnemyData
		var slices := PackedStringArray()
		if e.wheel != null:
			for slot in e.wheel.slots:
				if slot != null and slot.slice != null:
					slices.append(slot.slice.display_name if slot.slice.display_name != "" else String(slot.slice.id))
		return "%s (%d HP)\n%s\nWheel: %s" % [e.display_name, e.hp, e.description, ", ".join(slices)]
	if res is NetworkNodeData:
		var n := res as NetworkNodeData
		return "%s (integrity %d, %d Schematics)\n%s" % [n.display_name, n.integrity, n.install_cost, n.description]
	if res is DefenseAssetData:
		var a := res as DefenseAssetData
		return "%s (integrity %d)\n%s" % [a.display_name, a.integrity, a.description]
	if res is ThreatData:
		var t := res as ThreatData
		return "%s (integrity %d, damage %d, speed %d)\n%s" % [t.display_name, t.integrity, t.damage, t.edges_per_step, t.description]
	if "display_name" in res and "description" in res:
		return "%s\n%s" % [res.get("display_name"), res.get("description")]
	return String(res.get("id")) if "id" in res else res.resource_path


static func describe_triggered(te: TriggeredEffectData) -> String:
	var parts := PackedStringArray()
	for e in te.effects:
		if e != null:
			parts.append(describe_effect(e))
	var when := String(RC.Trigger.keys()[te.trigger]).to_lower().replace("_", " ")
	if te.min_tier > RC.PrecisionTier.WEAK:
		when += " (%s or better)" % String(RC.PrecisionTier.keys()[te.min_tier]).to_lower()
	if te.consecutive_required > 1:
		when += " x%d in a row" % te.consecutive_required
	if te.limit_per_combat > 0:
		when += ", %d per combat" % te.limit_per_combat
	return "%s: %s" % [when, ", ".join(parts)]


static func describe_effect(e: EffectData) -> String:
	var name := String(RC.EffectType.keys()[e.type]).to_lower().replace("_", " ")
	match e.type:
		RC.EffectType.APPLY_STATUS:
			return "apply %s" % RC.Status.keys()[e.status]
		RC.EffectType.RETRIGGER:
			return "resolve again at x%.1f" % e.multiplier
		RC.EffectType.NUDGE:
			return "nudge x%d%s" % [maxi(1, e.amount), " ignoring resistance" if e.multiplier == 0.0 else ""]
		RC.EffectType.CUSTOM:
			return "special"
		RC.EffectType.EVADE:
			return "SANDBOX +%d" % maxi(1, e.amount)
		_:
			if e.amount != 0:
				return "%s %+d" % [name, e.amount]
			return name


## What `status` does; with `stacks` of 2 or more, followed by the stack line (N8).
static func status_text(status: int, stacks: int = 1) -> String:
	var text: String = STATUS_TEXT.get(status, "")
	if stacks >= 2 and text != "":
		text += "\n" + TranslationServer.translate("×%d: %d stacks of %s on this slice.") % [stacks, stacks,
			TranslationServer.translate(String(Palette.STATUS_WORDS.get(status, "")))]
	return text


static func tier_text(tier: int) -> String:
	return TIER_TEXT.get(tier, "")


## Every codex entry, grouped by section, for the codex screen: {section: [{title, text}]}.
## Every codex entry, grouped by section. With a `profile`, enemies appear only once met
## (no spoilers for bosses and REBEL_CELL); without one (tests, tools) everything shows.
## Parity CODEX-01 (ported from art-m13-final scripts/ui/kit/codex.gd, art pass W8a): an entry
## also names what its glyph is drawn from, so the view needs no lookup of its own: `slice`
## (RC.SliceType), `status` (RC.Status), `tier` (RC.PrecisionTier), `corporation` (a corp id),
## `hub` (a class's hub core id) and `id` (the content id of a card, Firmware, Daemon, ring
## segment, enemy, node, defense asset or threat).
static func entries(lookup: ContentLookup, profile: ProfileState = null) -> Dictionary:
	var out := {"Slices": [], "Statuses & precision": [], "Classes": [], "Corporations": [], "Cards": [], "Firmware": [], "Daemons": [], # TR
		"Ring segments": [], "Enemies": [], "Nodes": [], "Home servers": [], "Defense assets": [], "Threats": [], "Lexicon": []} # TR
	for id in lookup.ids_of_class(&"ClassData"):
		var cls := lookup.get_content(id) as ClassData
		var hub := cls.starting_wheel.hub if cls.starting_wheel != null else null
		out["Classes"].append({"title": cls.display_name, "text": "%s\n%d HP. Hub %s: %s%s" % [cls.description, cls.base_hp,
			hub.display_name if hub != null else "-", hub.description if hub != null else "",
			("\nAlternative of %s." % cls.alternative_of) if cls.alternative_of != &"" else ""], "hub": hub.id if hub != null else &""})
	for id in lookup.ids_of_class(&"CorporationData"):
		var corp := lookup.get_content(id) as CorporationData
		if corp.generated_from_profile and profile != null and profile.best_ice_for(corp.id) < 0 and not profile.stats.has("use_seen:%s" % corp.final_boss.id):
			out["Corporations"].append({"title": "???", "text": "Something is waiting behind the other four."})
			continue
		out["Corporations"].append({"title": corp.display_name, "text": corp.description, "corporation": corp.id})
	for id in lookup.ids_of_class(&"HomeServerVariantData"):
		var v := lookup.get_content(id) as HomeServerVariantData
		out["Home servers"].append({"title": v.display_name, "text": v.description})
	for t in SLICE_TYPE_TEXT:
		out["Slices"].append({"title": String(Palette.SLICE_NAMES.get(t, "")), "text": SLICE_TYPE_TEXT[t], "slice": t})
	# The status's glyph is the 1C atlas's (the view draws it): the title is its name alone.
	for st in STATUS_TEXT:
		out["Statuses & precision"].append({"title": String(Palette.STATUS_WORDS.get(st, RC.Status.keys()[st])), "text": STATUS_TEXT[st], "status": st})
	for tier in TIER_TEXT:
		out["Statuses & precision"].append({"title": RC.PrecisionTier.keys()[tier], "text": TIER_TEXT[tier], "tier": tier})
	var sections := {"Cards": &"CardData", "Firmware": &"FirmwareData", "Daemons": &"DaemonData", "Ring segments": &"RingSegmentData",
		"Enemies": &"EnemyData", "Nodes": &"NetworkNodeData", "Defense assets": &"DefenseAssetData", "Threats": &"ThreatData"}
	for section in sections:
		for id in lookup.ids_of_class(sections[section]):
			var res := lookup.get_content(id)
			if res is CardData and not (res as CardData).offered:
				continue
			if res is EnemyData and profile != null and not profile.stats.has("use_seen:%s" % id):
				continue
			if res is EnemyData and (res as EnemyData).corporation_id == &"":
				continue  # templates and class drones
			var entry := {"title": String(res.get("display_name")) if res.get("display_name") != "" else String(id), "text": describe(res), "id": id}
			if res is EnemyData:
				entry["corporation"] = (res as EnemyData).corporation_id
			elif res is CardData and not (res as CardData).effects.is_empty() and (res as CardData).effects[0] != null:
				entry["effect"] = (res as CardData).effects[0].type  # what the card does first
			out[section].append(entry)
	for word in LEXICON:
		out["Lexicon"].append({"title": word, "text": LEXICON[word]})
	# HQ-B (designer ruling Q8): the campaign's story so far (its revealed beats) heads the Codex
	# while a campaign is loaded (it was the HQ's window).
	var beats := story_entries()
	if beats.is_empty():
		return out
	var with_story := {STORY: beats}
	with_story.merge(out)
	return with_story


## Plan 2 B-CODEX: the entries of `all` (Codex.entries) whose title or text contains `query`
## (case-insensitive), as {section, title, text, ...} rows in section then entry order; titles
## matching rank before text-only matches. Empty query returns [].
static func search(all: Dictionary, query: String) -> Array:
	var q := query.strip_edges().to_lower()
	var by_title: Array = []
	var by_text: Array = []
	if q == "":
		return by_title
	for section in all:
		for e in all[section]:
			var row: Dictionary = (e as Dictionary).duplicate()
			row["section"] = section
			if String(row.get("title", "")).to_lower().contains(q):
				by_title.append(row)
			elif String(row.get("text", "")).to_lower().contains(q):
				by_text.append(row)
	by_title.append_array(by_text)
	return by_title


## HQ-B (Q8): the Codex's STORY section's key (a translation key).
const STORY := "Story" # TR


## HQ-B (Q8): the loaded campaign's revealed story beats as Codex entries ([] with no campaign
## or none revealed yet), the beats' words through TextDb.
static func story_entries() -> Array:
	var out: Array = []
	var c := RunManager.campaign
	if c == null or RunManager.corporation == null:
		return out
	for b in CampaignRules.revealed_beats(c, RunManager.corporation):
		out.append({"title": TextDb.t(b, "title"), "text": TextDb.t(b, "text")})
	return out
