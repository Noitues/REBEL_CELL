class_name EyeRules
extends RefCounted
## Halcyon v2 THE EYE (themes/v2/halcyon.md): pure rules. Sector and bearing maths, the campaign
## turn move and fix, the launch snapshot, the Blade (slot, level, class), the HQ gaze (node
## states, beam, Alert, Lockdown) and the raid wedge. Every number is config.
## Bearings are integer degrees 0-359, 0 = up on the Grid map, clockwise.

const HALCYON_ID := &"halcyon"
## A node's state in the Eye: OPEN (dark side), SPOTTED (a fight in the eye), SHUTTERED (a non-fight
## node in the eye, cannot be entered) or BLOCKED (on the beam, whatever its kind).
enum NodeState { OPEN, SPOTTED, SHUTTERED, BLOCKED }


## Whether `corp` is Halcyon (the Eye rules apply).
static func applies(corp: CorporationData) -> bool:
	return corp != null and corp.id == HALCYON_ID


## Octants on the dial (360 / step).
static func octants(config: CampaignConfigData) -> int:
	return maxi(1, 360 / maxi(1, config.eye_step_deg))


## The district bearing of `site_id` from the home server (the Eye marker): integer degrees,
## -1 when the site or home is unknown. A site on the marker itself reads 0.
static func bearing_deg(grid: CityGridData, site_id: StringName) -> int:
	if grid == null:
		return -1
	var home: SiteData = null
	var site: SiteData = null
	for s in grid.sites:
		if s == null:
			continue
		if s.id == grid.home_site_id:
			home = s
		if s.id == site_id:
			site = s
	if home == null or site == null:
		return -1
	var d: Vector2 = site.map_position - home.map_position
	if d == Vector2.ZERO:
		return 0
	return posmod(roundi(rad_to_deg(atan2(d.x, -d.y))), 360)


## The octant (0..octants-1) whose centre is nearest `bearing` (a tie goes to the lower octant).
static func octant_of(bearing: int, config: CampaignConfigData) -> int:
	var step := maxi(1, config.eye_step_deg)
	var b := posmod(bearing, 360)
	var k := (b * 2 + step - 1) / (2 * step)
	return posmod(k, octants(config))


## The centre of octant `index`.
static func centre_deg(index: int, config: CampaignConfigData) -> int:
	return posmod(config.eye_step_deg * index, 360)


## Half-open sector [centre - w/2, centre + w/2).
static func in_sector(bearing: int, centre: int, config: CampaignConfigData) -> bool:
	var half := config.eye_sector_deg / 2
	return posmod(bearing - centre + half, 360) < config.eye_sector_deg


## The first eye_index of a campaign, from stream `eye_start` (drawn once, then stored).
static func draw_start(campaign_seed: int, config: CampaignConfigData) -> int:
	return RngStreams.make_stream(campaign_seed, RngStreams.EYE_START_STREAM).randi_range(0, octants(config) - 1)


## The launch snapshot (rule 6): 0 not Spotted, 1 Spotted with the Eye moving, 2 Spotted with it
## FIXED. A `bearing` of -1 (unknown) is not Spotted.
static func spotted_level(theme: HalcyonCampaignTheme, bearing: int, config: CampaignConfigData) -> int:
	if bearing < 0 or not in_sector(bearing, centre_deg(theme.eye_index, config), config):
		return 0
	return 2 if theme.eye_fixed_left > 0 else 1


## One campaign turn (one ended netrun, won, died or abandoned): the Eye ticks (a fixed Eye counts
## down, else it moves), then an Exploit taken this turn (`fix_bearing` >= 0) re-aims and resets the
## fix. Returns {"moved": bool, "fixed": bool}.
static func campaign_turn(theme: HalcyonCampaignTheme, config: CampaignConfigData, fix_bearing: int = -1) -> Dictionary:
	var moved := false
	if theme.eye_fixed_left > 0:
		theme.eye_fixed_left -= 1
	else:
		theme.eye_index = posmod(theme.eye_index + config.eye_move_per_turn, octants(config))
		moved = true
	var fixed := false
	if fix_bearing >= 0:
		theme.eye_index = octant_of(fix_bearing, config)
		theme.eye_fixed_left = config.eye_fix_turns
		fixed = true
	return {"moved": moved, "fixed": fixed}


## What the next campaign turn does, for the cards: {"index": octant after the tick, "fixed_left":
## turns left after it}. Nothing is drawn.
static func next_turn_preview(theme: HalcyonCampaignTheme, config: CampaignConfigData) -> Dictionary:
	var copy := theme.copy() as HalcyonCampaignTheme
	campaign_turn(copy, config)
	return {"index": copy.eye_index, "fixed_left": copy.eye_fixed_left}


# --- The Blade ---------------------------------------------------------------------------------

## The fight class of a node for the Blade tables: NORMAL, ELITE, RACK, MINI_BOSS or BOSS.
static func fight_class(node: Dictionary, final_street_node: bool = false) -> StringName:
	if bool(node.get("boss", false)):
		return &"BOSS"
	if bool(node.get("mini_boss", false)) or final_street_node:
		return &"MINI_BOSS"
	if int(node.get("type", -1)) == RC.InfilNodeType.SERVER_RACK:
		return &"RACK"
	if bool(node.get("elite", false)):
		return &"ELITE"
	return &"NORMAL"


## Whether the Blade is on a fight of `cls` at `level` (0 never; 1 and 2 by the config tables).
static func blade_applies(level: int, cls: StringName, config: CampaignConfigData) -> bool:
	if level <= 0:
		return false
	return config.blade_classes_l1.has(cls) if level == 1 else config.blade_classes_l2.has(cls)


## The slot the scan line marks on `turn` (1-based): `(turn - 1) mod n` over the non-empty slots
## in slot order. -1 when the wheel has none. Never random.
static func blade_slot(slot_sizes: PackedInt32Array, turn: int) -> int:
	var slots: Array[int] = []
	for i in slot_sizes.size():
		if slot_sizes[i] > 0:
			slots.append(i)
	if slots.is_empty():
		return -1
	return slots[posmod(turn - 1, slots.size())]


## Heat a fight adds at Spotted level 2 (Elite fights only).
static func spotted_heat(level: int, cls: StringName, config: CampaignConfigData) -> int:
	return config.spotted_elite_heat if level >= 2 and cls == &"ELITE" else 0


# --- The HQ gaze -------------------------------------------------------------------------------

## Gaze centre at `step` for a run launched at `phase`.
static func gaze_centre(phase: int, step: int, config: CampaignConfigData) -> int:
	return centre_deg(phase + step, config)


## Lockdown (Alert at the threshold, for the rest of the run).
static func lockdown(alert: int, config: CampaignConfigData) -> bool:
	return alert >= config.hq_lockdown_alert


## The beam half width: multiplied in Lockdown.
static func beam_half_width(alert: int, config: CampaignConfigData) -> int:
	return config.hq_beam_half_width_deg * (config.hq_lockdown_beam_mult if lockdown(alert, config) else 1)


## The Blade level on a fight in the eye: the launch level, plus the bonus in Lockdown, capped.
static func hq_blade_level(spotted: int, alert: int, config: CampaignConfigData) -> int:
	var bonus := config.hq_lockdown_blade_bonus if lockdown(alert, config) else 0
	return mini(config.blade_level_max, spotted + bonus)


## Whether `node` is a fight (Router, Elite, Rack, mini-boss, boss) rather than a non-fight room.
static func is_fight(node: Dictionary) -> bool:
	if bool(node.get("rest", false)) or bool(node.get("cache", false)) or bool(node.get("power", false)):
		return false
	var t := int(node.get("type", -1))
	return t == RC.InfilNodeType.ROUTER or t == RC.InfilNodeType.SERVER_RACK


## A node's state under the Eye at `step` (rules 13-14). `asleep` (Cut the Power): no sector and
## no beam, so every node is OPEN.
static func node_state(node: Dictionary, phase: int, step: int, alert: int, asleep: bool, config: CampaignConfigData) -> NodeState:
	if asleep:
		return NodeState.OPEN
	var az := int(node.get("az", 0))
	var centre := gaze_centre(phase, step, config)
	var off := absi(posmod(az - centre + 180, 360) - 180)
	if off <= beam_half_width(alert, config):
		return NodeState.BLOCKED
	if not in_sector(az, centre, config):
		return NodeState.OPEN
	return NodeState.SPOTTED if is_fight(node) else NodeState.SHUTTERED


## Whether a node in `state` can be entered.
static func enterable(state: NodeState) -> bool:
	return state == NodeState.OPEN or state == NodeState.SPOTTED


# --- Raid wedge --------------------------------------------------------------------------------

## The percent a corporate threat on a node at `bearing` deals extra (rule 21): inside the sector
## of the Eye (the fixed area when FIXED); the same figure moving or fixed.
static func raid_damage_pct(theme: HalcyonCampaignTheme, bearing: int, config: CampaignConfigData) -> int:
	if bearing < 0:
		return 0
	return config.raid_eye_damage_pct if in_sector(bearing, centre_deg(theme.eye_index, config), config) else 0
