class_name RebelCellBuilder
extends RefCounted
## REBEL_CELL (GDD 8.5): the final corporation, built from the player's profile. Pure: it
## reads a template CorporationData and a usage snapshot and returns NEW resources (the
## loaded template is never modified; its grid and story are deep-copied).
##   - elites mirror your most-used classes: their wheels, with every slice upgraded to the
##     nearest slice of the same type at 1.5x the output, and a hub carrying the combat
##     effects of your most-used data Daemons;
##   - Site names carry your most-used node types;
##   - raid threats are mirrors of your most-used defense assets.
## Same snapshot + same content = same corporation (ties break by id).

const ID := &"rebel_cell"
## How many of each kind the snapshot keeps.
const TOP_CLASSES := 2
const TOP_DAEMONS := 3
const TOP_NODES := 3
const TOP_ASSETS := 3
## Defaults for config.mirror_* when no config is passed (tools, tests). 1.5x keeps a Tier 1
## Mirror in line with the other corporations' elites; 2x killed rookies in two turns.
const MIRROR_OUTPUT_FACTOR := 1.5
## Mirrored assets march as threats with this integrity multiple and damage bonus.
const MIRROR_THREAT_INTEGRITY := 1.5
const MIRROR_THREAT_DAMAGE_BONUS := 2
static var _factor := MIRROR_OUTPUT_FACTOR
static var _threat_integrity := MIRROR_THREAT_INTEGRITY
static var _threat_damage := MIRROR_THREAT_DAMAGE_BONUS
const FALLBACK_NODES: Array[StringName] = [&"relay", &"firewall_relay", &"safehouse"]
const FALLBACK_ASSETS: Array[StringName] = [&"turret", &"ice_lock", &"decoy"]


## The usage snapshot a campaign is built (and rebuilt on resume) from.
static func snapshot(profile: ProfileState, fallback_class: StringName) -> Dictionary:
	var classes := _top(profile, "class", TOP_CLASSES)
	if classes.is_empty():
		classes.append(fallback_class)
	var nodes := _top(profile, "node", TOP_NODES)
	if nodes.is_empty():
		nodes = FALLBACK_NODES.duplicate()
	var assets := _top(profile, "asset", TOP_ASSETS)
	if assets.is_empty():
		assets = FALLBACK_ASSETS.duplicate()
	return {"classes": _strings(classes), "daemons": _strings(_top(profile, "daemon", TOP_DAEMONS)),
		"nodes": _strings(nodes), "assets": _strings(assets)}


static func _top(profile: ProfileState, kind: String, n: int) -> Array[StringName]:
	if profile == null:
		return [] as Array[StringName]
	return profile.top_used(kind, n)


## Builds the campaign's REBEL_CELL from `template` and `snap`. Register the result in the
## lookup (ContentLookup.add walks it) so netruns and raids can resolve the new ids.
static func build(template: CorporationData, snap: Dictionary, lookup: ContentLookup, config: CampaignConfigData = null) -> CorporationData:
	_factor = config.mirror_output_factor if config != null else MIRROR_OUTPUT_FACTOR
	_threat_integrity = config.mirror_threat_integrity if config != null else MIRROR_THREAT_INTEGRITY
	_threat_damage = config.mirror_threat_damage_bonus if config != null else MIRROR_THREAT_DAMAGE_BONUS
	var corp := template.duplicate(true) as CorporationData
	corp.generated_from_profile = true
	var elite_base: EnemyData = template.elites[0] if not template.elites.is_empty() else null
	var hub := _daemon_hub(snap.get("daemons", []), lookup)
	var elites: Array[EnemyData] = []
	for cid in snap.get("classes", []):
		var cls := lookup.get_content(StringName(String(cid))) as ClassData
		if cls != null:
			elites.append(_mirror_elite(cls, elite_base, hub, lookup))
	if not elites.is_empty():
		corp.elites = elites
	_rename_sites(corp.city_grid, snap.get("nodes", []), lookup)
	var threats: Array[ThreatData] = []
	for aid in snap.get("assets", []):
		var asset := lookup.get_content(StringName(String(aid))) as DefenseAssetData
		if asset != null:
			threats.append(_mirror_threat(asset))
	if not threats.is_empty():
		corp.raids = _mirror_raids(template.raids, threats)
	return corp


# --- Elites ------------------------------------------------------------------------------

static func _mirror_elite(cls: ClassData, base: EnemyData, hub: HubCoreData, lookup: ContentLookup) -> EnemyData:
	var e := EnemyData.new()
	e.id = StringName("rc_mirror_%s" % cls.id)
	e.display_name = "Mirror %s" % cls.display_name
	e.description = "Your %s, turned against you: its wheel, hitting harder." % cls.display_name
	e.corporation_id = ID
	e.hp = base.hp if base != null else 150
	e.is_elite = true
	e.cycle_reward = base.cycle_reward if base != null else 35
	var w := WheelData.new()
	w.slice_count = cls.starting_wheel.slice_count
	var slots: Array[WheelSlotData] = []
	for slot in cls.starting_wheel.slots:
		var s := WheelSlotData.new()
		s.slice = _stronger(slot.slice if slot != null else null, lookup)
		slots.append(s)
	w.slots = slots
	# One pointer like the wheel it mirrors (two made a Tier 1 Mirror Breaker a rookie killer).
	w.pointer_ticks = PackedInt32Array([0])
	w.passive_resistance = 1
	w.hub = hub
	e.wheel = w
	return e


## The plain slice of the same type whose output is closest to MIRROR_OUTPUT_FACTOR x yours
## and above it (ties: lower output, then id). Deploy slices become attacks (no drone).
static func _stronger(slice: SliceData, lookup: ContentLookup) -> SliceData:
	if slice == null or slice.slice_type == RC.SliceType.MISS:
		return slice
	var want_type := RC.SliceType.ATTACK if slice.slice_type == RC.SliceType.DEPLOY else slice.slice_type
	var base := maxi(1, slice.base_output) if slice.slice_type != RC.SliceType.DEPLOY else 6
	var want := base * _factor
	var best: SliceData = null
	for id in lookup.ids_of_class(&"SliceData"):
		var c := lookup.get_content(id) as SliceData
		if c == null or c.slice_type != want_type or not c.extra_effects.is_empty() or c.base_output <= base:
			continue
		if best == null:
			best = c
			continue
		var d := absf(c.base_output - want)
		var bd := absf(best.base_output - want)
		if d < bd or (d == bd and (c.base_output < best.base_output or (c.base_output == best.base_output and String(c.id) < String(best.id)))):
			best = c
	return best if best != null else slice


## A hub whose passive effects are the combat effects of your most-used data Daemons
## (damage, healing, block, shield on combat start, turn start, Perfect or Miss).
static func _daemon_hub(daemon_ids: Array, lookup: ContentLookup) -> HubCoreData:
	var effects: Array[TriggeredEffectData] = []
	var names := PackedStringArray()
	for did in daemon_ids:
		var d := lookup.get_content(StringName(String(did))) as DaemonData
		if d == null:
			continue
		for te in d.triggered_effects:
			if te == null or not te.trigger in [RC.Trigger.ON_COMBAT_START, RC.Trigger.ON_TURN_START, RC.Trigger.ON_PERFECT, RC.Trigger.ON_MISS_SLICE]:
				continue
			var ok := not te.effects.is_empty()
			for e in te.effects:
				if e == null or not e.type in [RC.EffectType.DEAL_DAMAGE, RC.EffectType.HEAL, RC.EffectType.GAIN_BLOCK, RC.EffectType.GAIN_SHIELD]:
					ok = false
			if ok:
				effects.append(te)
				names.append(d.display_name)
	if effects.is_empty():
		return null
	var hub := HubCoreData.new()
	hub.id = &"rc_mirror_hub"
	hub.display_name = "Mirrored Daemons"
	hub.description = "Runs your own Daemons: %s." % ", ".join(names)
	hub.passive_effects = effects
	return hub


# --- Grid and raids ---------------------------------------------------------------------------

static func _rename_sites(grid: CityGridData, node_ids: Array, lookup: ContentLookup) -> void:
	if grid == null or node_ids.is_empty():
		return
	var names: Array[String] = []
	for nid in node_ids:
		var n := lookup.get_content(StringName(String(nid))) as NetworkNodeData
		names.append(n.display_name if n != null else String(nid))
	var i := 0
	for s in grid.sites:
		if s.tier >= 1 and s.tier <= 3 and s.objective != RC.SiteObjective.HEAT_REDUCTION and s.id != grid.home_site_id:
			s.display_name = "%s: %s" % [names[i % names.size()], s.display_name]
			i += 1


static func _mirror_threat(asset: DefenseAssetData) -> ThreatData:
	var t := ThreatData.new()
	t.id = StringName("rc_threat_%s" % asset.id)
	t.display_name = "Mirror %s" % asset.display_name
	t.description = "Your own %s, marching on your home." % asset.display_name
	t.integrity = maxi(10, roundi(asset.integrity * _threat_integrity))
	t.damage = maxi(4, asset.damage + _threat_damage)
	match asset.asset_type:
		RC.AssetType.TURRET:
			t.routing = RC.ThreatRouting.WEAKEST_NODE
			t.edges_per_step = 1
		RC.AssetType.ICE_LOCK:
			t.routing = RC.ThreatRouting.SHORTEST_TO_HOME
			t.edges_per_step = 1
			t.freezes_edges = true
		_:
			t.routing = RC.ThreatRouting.HIGHEST_VALUE
			t.edges_per_step = 2
	return t


## One mirror raid per template raid: same id, source, reward and wave sizes, threats
## cycled from the mirrored assets (Icebreakers kept for retaliation).
static func _mirror_raids(template_raids: Array[RaidData], threats: Array[ThreatData]) -> Array[RaidData]:
	var out: Array[RaidData] = []
	var k := 0
	for tr in template_raids:
		if tr == null:
			continue
		var r := tr.duplicate(false) as RaidData
		var waves: Array[RaidWaveData] = []
		for tw in tr.waves:
			var w := RaidWaveData.new()
			var ts: Array[ThreatData] = []
			for t in tw.threats:
				if t != null and t.alters_edges:
					ts.append(t)
				else:
					ts.append(threats[k % threats.size()])
					k += 1
			w.threats = ts
			waves.append(w)
		r.waves = waves
		out.append(r)
	return out


static func _strings(ids: Array) -> Array:
	var out := []
	for x in ids:
		out.append(String(x))
	return out
