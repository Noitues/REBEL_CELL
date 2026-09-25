class_name Codex
extends RefCounted
## Plain-text descriptions of game content and rules for inspect tooltips and the codex
## screen (GDD 8.1, 9.5). Reads content only; never changes state.

const SLICE_TYPE_TEXT := {
	RC.SliceType.ATTACK: "ATTACK: deals damage to whatever sits at each pointer of the target wheel.",
	RC.SliceType.CRIT: "CRIT: deals high damage to whatever sits at each pointer of the target wheel.",
	RC.SliceType.DEFEND: "DEFEND: gains block. Block expires at the start of your next turn.",
	RC.SliceType.SHIELD: "SHIELD: gains shield. Shield persists across turns (cap 15).",
	RC.SliceType.EVADE: "EVADE: cancels the next incoming ATTACK or CRIT this turn.",
	RC.SliceType.DEPLOY: "DEPLOY: docks a drone on your wheel. It resolves when its slice does and takes hits aimed there.",
	RC.SliceType.HEAL: "HEAL: restores HP.",
	RC.SliceType.AFFLICT: "AFFLICT: applies a status or a drain to your wheel (Dose corrupts, Tariff drains RAM, Citation plants a Parasite, Solar Flare overclocks).",
	RC.SliceType.MISS: "MISS: nothing happens, unless a Daemon says otherwise.",
}
const STATUS_TEXT := {
	RC.Status.CORRUPTED: "CORRUPTED: when the slice resolves, 3 self-damage (+1 per MAJOR Heat threshold) and -1 RAM. Lasts until cleansed.",
	RC.Status.OVERCLOCKED: "OVERCLOCKED: 1.5x output on the slice's next trigger, then it becomes CORRUPTED.",
	RC.Status.ENCRYPTED: "ENCRYPTED: absorbs the next status applied to that slice.",
	RC.Status.PARASITE: "PARASITE: something is feeding on the slice (a Botnet parasite, a Halcyon Citation); it resolves at half output until cleansed.",
}
const TIER_TEXT := {
	RC.PrecisionTier.PERFECT: "PERFECT (offset 0): full output and the class Perfect hook.",
	RC.PrecisionTier.GOOD: "GOOD (offset 1): full output.",
	RC.PrecisionTier.PARTIAL: "PARTIAL (offset 2): half output.",
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
	"Tariff": "Meridian's fee on every packet: an enemy slice that drains your RAM.",
	"Citation": "Halcyon's fine: a Parasite on one of your slices until you cleanse it.",
	"Solar Flare": "Orbital's gift: your slice runs hot once (1.5x), then corrupts.",
	"Inertia": "Heavy freight resists nudges; some Meridian slices add resistance as they hit.",
	"Mirror": "A copy of one of your own operatives. You will know it when you meet it.",
}


## One-paragraph description of any content resource, for tooltips.
static func describe(res: Resource) -> String:
	if res == null:
		return ""
	if res is SliceData:
		var s := res as SliceData
		var head := "%s %s" % [Palette.SLICE_GLYPHS.get(s.slice_type, "?"), s.display_name if s.display_name != "" else String(s.id)]
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
	if te.min_tier > RC.PrecisionTier.PARTIAL:
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
		_:
			if e.amount != 0:
				return "%s %+d" % [name, e.amount]
			return name


static func status_text(status: int) -> String:
	return STATUS_TEXT.get(status, "")


static func tier_text(tier: int) -> String:
	return TIER_TEXT.get(tier, "")


## Every codex entry, grouped by section, for the codex screen: {section: [{title, text}]}.
## Every codex entry, grouped by section. With a `profile`, enemies appear only once met
## (no spoilers for bosses and REBEL_CELL); without one (tests, tools) everything shows.
static func entries(lookup: ContentLookup, profile: ProfileState = null) -> Dictionary:
	var out := {"Slices": [], "Statuses & precision": [], "Classes": [], "Corporations": [], "Cards": [], "Firmware": [], "Daemons": [],
		"Ring segments": [], "Enemies": [], "Nodes": [], "Home servers": [], "Defense assets": [], "Threats": [], "Lexicon": []}
	for id in lookup.ids_of_class(&"ClassData"):
		var cls := lookup.get_content(id) as ClassData
		var hub := cls.starting_wheel.hub if cls.starting_wheel != null else null
		out["Classes"].append({"title": cls.display_name, "text": "%s\n%d HP. Hub %s: %s%s" % [cls.description, cls.base_hp,
			hub.display_name if hub != null else "-", hub.description if hub != null else "",
			("\nAlternative of %s." % cls.alternative_of) if cls.alternative_of != &"" else ""]})
	for id in lookup.ids_of_class(&"CorporationData"):
		var corp := lookup.get_content(id) as CorporationData
		if corp.generated_from_profile and profile != null and profile.best_ice_for(corp.id) < 0 and not profile.stats.has("use_seen:%s" % corp.final_boss.id):
			out["Corporations"].append({"title": "???", "text": "Something is waiting behind the other four."})
			continue
		out["Corporations"].append({"title": corp.display_name, "text": corp.description})
	for id in lookup.ids_of_class(&"HomeServerVariantData"):
		var v := lookup.get_content(id) as HomeServerVariantData
		out["Home servers"].append({"title": v.display_name, "text": v.description})
	for t in SLICE_TYPE_TEXT:
		out["Slices"].append({"title": "%s %s" % [Palette.SLICE_GLYPHS.get(t, ""), Palette.SLICE_NAMES.get(t, "")], "text": SLICE_TYPE_TEXT[t]})
	for st in STATUS_TEXT:
		out["Statuses & precision"].append({"title": "%s %s" % [Palette.STATUS_GLYPHS.get(st, ""), RC.Status.keys()[st]], "text": STATUS_TEXT[st]})
	for tier in TIER_TEXT:
		out["Statuses & precision"].append({"title": RC.PrecisionTier.keys()[tier], "text": TIER_TEXT[tier]})
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
			out[section].append({"title": String(res.get("display_name")) if res.get("display_name") != "" else String(id), "text": describe(res)})
	for word in LEXICON:
		out["Lexicon"].append({"title": word, "text": LEXICON[word]})
	return out
