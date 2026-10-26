class_name SolaceTideCampaign
extends RefCounted
## Phase 2b: the Solace Infected Tide inside a campaign (SOLACE_RAID_SPEC.md sections 2, 5, 6, 8, 9). CampaignRules calls
## this wherever `CorporationData.raid_model` is "tide". The tide's own block lives in `campaign.corp_theme.solace.tide`
## (the deck, the counters); everything else the tide reads (Heat, Schematics, HOME, the Sites' condition, the Exploits
## held) is the campaign's own. `load_state` builds a working SolaceTideState from both, SolaceTideRules plays on it, and
## `store_state` writes the result back, so the core rules stay testable without a campaign.
##
## Site mapping: a claimed Site is OK or DOWN (the node's condition), a TAKEN Site is TAKEN, a CLEARED Site waits in `pending`.
## Pure functions of the campaign, the corporation and the config; the raid's draws come from the `raids` stream of
## `raid_streams`, which depends only on the campaign seed and the raid's index (so a projection equals the result and a
## load resumes identically).

## The id prefix of a derived class card (an operative stationed on a Site): the card is never saved in the deck.
const CLASS_CARD_PREFIX := "c_"

## Boards by (City Grid instance, route length): a board is pure data built from the grid, never from a state.
static var _boards: Dictionary = {}


## True when `corp`'s campaign plays the Infected Tide.
static func applies(corp: CorporationData) -> bool:
	return corp != null and corp.uses_tide()


## True when `campaign` carries a tide (started by `start`).
static func active(campaign: CampaignState) -> bool:
	return campaign != null and campaign.corp_theme.solace.tide != null


## The tide block of a new campaign: the config's start deck, the ghost kit.
static func start(campaign: CampaignState, cfg: CampaignConfigData) -> void:
	campaign.corp_theme.solace.tide = SolaceTideState.start(cfg, campaign.grid.home_max_integrity)


## The board of `corp`'s City Grid.
static func board_for(corp: CorporationData, cfg: CampaignConfigData) -> SolaceTideBoard:
	var key := "%d:%d" % [corp.city_grid.get_instance_id(), cfg.solace_tide_route_max_links]
	if not _boards.has(key):
		_boards[key] = SolaceTideBoard.from_grid(corp.city_grid, cfg.solace_tide_route_max_links)
	return _boards[key]


## The `raids` RngService stream of raid number `raid_idx` (0-based) of a campaign seed: a pure function of both.
static func raid_streams(campaign_seed: int, raid_idx: int) -> RandomNumberGenerator:
	return RngStreams.seeded(RngStreams.derive_seed(campaign_seed, StringName("tide_raid_%d" % raid_idx))).get_stream(&"raids")


## The weakest Heat band the HOME hit of a raid queued by `source` may have (config): story and retaliation raids carry their own
## strength; every other source (cadence, Heat level) is decided by the Heat alone (0).
static func trigger_band(source: int, cfg: CampaignConfigData) -> int:
	match source:
		RC.RaidTriggerSource.STORY:
			return cfg.solace_tide_story_band
		RC.RaidTriggerSource.RETALIATION:
			return cfg.solace_tide_retaliation_band
	return 0


## Raids fought so far (each one adds to exactly one of the two counters).
static func raids_fought(campaign: CampaignState) -> int:
	return campaign.raids_won + campaign.raids_lost


## INFECTED cards in the defense deck (0 outside a tide campaign): the Bloom's start and the Genome Core's strength read it.
static func infected_count(campaign: CampaignState) -> int:
	if not active(campaign):
		return 0
	var n := 0
	for c in campaign.corp_theme.solace.tide.deck:
		if c[2] == SolaceTideState.VERB_WOUND:
			n += 1
	return n


# ------------------------------------------------------------------------------------------------ campaign <-> state
## The tide's working state for `campaign`: its block plus the campaign fields it reads, and the class cards of the
## operatives stationed on Sites (R-C). Null without a tide.
static func load_state(campaign: CampaignState, corp: CorporationData, cfg: CampaignConfigData) -> SolaceTideState:
	if not active(campaign):
		return null
	var st := SolaceTideState.from_block(campaign.corp_theme.solace.tide.block_dict())
	var grid := campaign.grid
	st.heat = campaign.heat
	st.schematics = campaign.schematics
	st.home = grid.home_integrity
	st.home_max = grid.home_max_integrity
	st.deaths = campaign.deaths
	st.cools = campaign.heat_purchases
	st.won = campaign.outcome == CampaignState.Outcome.WON
	var ids: Array = grid.sites.keys()
	IdSort.sort_ids(ids)
	for id in ids:
		if id == grid.home_site_id:
			continue
		match grid.status_of(id):
			GridState.SiteStatus.CLAIMED:
				st.owned[id] = SolaceTideState.Cond.DOWN if int(grid.site(id).get("condition", GridState.Condition.OK)) == GridState.Condition.DOWN \
					else SolaceTideState.Cond.OK
			GridState.SiteStatus.TAKEN:
				st.owned[id] = SolaceTideState.Cond.TAKEN
			GridState.SiteStatus.CLEARED:
				st.pending.append(id)
	for s in corp.city_grid.sites:
		if s == null:
			continue
		if s.objective == RC.SiteObjective.EXPLOIT and campaign.has_exploit(s.exploit_type):
			st.held.append(s.id)
		if s.objective == RC.SiteObjective.HEAT_REDUCTION and not grid.is_corporate(s.id):
			st.obj_done.append(s.id)
	IdSort.sort_ids(st.held)
	IdSort.sort_ids(st.obj_done)
	for lv in cfg.heat_band_levels():
		if campaign.thresholds_fired.has(lv):
			st.crossed_heat.append(lv)
	for o in campaign.living_operatives():
		var site := CampaignRules.stationed_site(campaign, o.id)
		var card := cfg.solace_tide_class_card(o.class_id)
		if site != &"" and not card.is_empty():
			st.deck.append([CLASS_CARD_PREFIX + String(o.id), card[1], card[2]])
	st.sort_deck()
	return st


## Writes a played state back: the tide block (the derived class cards dropped), Heat, Schematics, HOME, the Sites' condition
## (a Site the tide took becomes TAKEN: its node, assets and operative are lost) and the outcome (`lost`). Returns events.
static func store_state(campaign: CampaignState, st: SolaceTideState) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	var block := SolaceTideState.from_block(st.block_dict())
	var kept: Array = []
	for c in block.deck:
		if not String(c[0]).begins_with(CLASS_CARD_PREFIX):
			kept.append(c)
	block.deck = kept
	campaign.corp_theme.solace.tide = block
	campaign.heat = st.heat
	campaign.schematics = st.schematics
	var grid := campaign.grid
	grid.home_integrity = st.home
	grid.sites[grid.home_site_id]["integrity"] = st.home
	var ids: Array = st.owned.keys()
	IdSort.sort_ids(ids)
	for id in ids:
		var s := grid.site(id)
		var cond := int(st.owned[id])
		if cond == SolaceTideState.Cond.TAKEN:
			if grid.is_claimed(id):
				if String(s.get("stationed", "")) != "":
					events.append({"type": "recalled", "operative": s["stationed"], "text": "%s returns to the reserves from TAKEN %s." % [s["stationed"], id]})
				s["status"] = GridState.SiteStatus.TAKEN
				s["node_type"] = ""
				s["integrity"] = 0
				s["max_integrity"] = 0
				s["condition"] = GridState.Condition.OK
				s["assets"] = []
				s["stationed"] = ""
				events.append({"type": "taken", "site": id, "text": "%s is TAKEN." % id})
		elif grid.is_claimed(id):
			if cond == SolaceTideState.Cond.DOWN and int(s.get("condition", GridState.Condition.OK)) != GridState.Condition.DOWN:
				s["condition"] = GridState.Condition.DOWN
				s["integrity"] = 0
				if String(s.get("stationed", "")) != "":
					events.append({"type": "recalled", "operative": s["stationed"], "text": "%s returns to the reserves from DOWN %s." % [s["stationed"], id]})
					s["stationed"] = ""
				events.append({"type": "down", "site": id, "text": "%s goes DOWN." % id})
	grid.frozen_links.clear()
	if st.lost != SolaceTideState.LOST_NONE:
		campaign.outcome = CampaignState.Outcome.LOST
		if st.lost == SolaceTideState.LOST_CITY:
			events.append({"type": "city_lost", "text": "CITY LOST: the infection outnumbers the healthy defenses. Campaign lost."})
		else:
			events.append({"type": "campaign_lost", "text": "The home server is BREACHED. Campaign lost."})
	return events


## The Bloom's start arguments for a netrun (R-D): the INFECTED count, the campaign's Heat band and whether a held Exploit gives
## the Virus key. Without a tide the count is 0 and BloomRules.begin changes nothing.
static func front_args(campaign: CampaignState, corp: CorporationData, cfg: CampaignConfigData) -> Dictionary:
	var virus := false
	if corp != null:
		for ex in corp.exploits:
			if ex != null and campaign.has_exploit(ex.exploit_type) and ex.bloom_pace_cut:
				virus = true
	return {"infected": infected_count(campaign), "band": SolaceRaidRules.heat_band_index(campaign, cfg), "virus": virus}


# ------------------------------------------------------------------------------------------------ the raid
## The automatic defense: the placement with the least damage over the forecast's 12 outcomes under HOLD (the config's
## weights; the first of equal ones). Returns {"place": ..., "resp": ["HOLD"]}.
static func auto_plan(ctx: SolaceTideRules.Ctx, st: SolaceTideState, cfg: CampaignConfigData) -> Dictionary:
	var best_place: Dictionary = {"sentries": {}, "ghost": &""}
	var best := -1
	var resp: Array = ["HOLD"]
	for place in SolaceTideRules.placements(ctx, st):
		var score := 0
		for row in SolaceTideRules.forecast(ctx, st, place, resp):
			score += _damage(st, row["result"]["state"], cfg)
		if best < 0 or score < best:
			best = score
			best_place = place
	return {"place": best_place, "resp": resp}


static func _damage(before: SolaceTideState, after: SolaceTideState, cfg: CampaignConfigData) -> int:
	var taken := 0
	var down := 0
	for s in after.owned.keys():
		var was := int(before.owned.get(s, -1))
		var now := int(after.owned[s])
		if now == SolaceTideState.Cond.TAKEN and was != SolaceTideState.Cond.TAKEN:
			taken += 1
		elif now == SolaceTideState.Cond.DOWN and was == SolaceTideState.Cond.OK:
			down += 1
	return maxi(0, before.home - after.home) * cfg.solace_tide_auto_home_weight + taken * cfg.solace_tide_auto_taken_weight \
		+ down * cfg.solace_tide_auto_down_weight


## Plays the pending tide raid out and applies it (SolaceTideRaid: open -> play -> resolve). `pending["plan"]` ({"place",
## "resp"}) is the player's defense; without it the automatic one is used. Returns events.
static func fight(campaign: CampaignState, corp: CorporationData, cfg: CampaignConfigData, _lookup: ContentLookup,
		pending: Dictionary) -> Array[Dictionary]:
	if not active(campaign):
		return []
	var raid := SolaceTideRaid.open(campaign, corp, cfg, pending)
	if raid.over:
		var lost_events := raid.open_events.duplicate()
		lost_events.append({"type": "raid_end", "won": false, "tier": "CITY LOST", "text": "Tide raid %d: CITY LOST in the DECAY." % (raid.raid_idx + 1)})
		return lost_events
	var plan: Dictionary = pending.get("plan", {})
	if plan.is_empty():
		raid.plan_auto()
	else:
		raid.place = plan["place"]
		raid.resp = plan["resp"]
	return raid.resolve()


## True when every Site of `b` has the condition `a` gives it.
static func owned_same(a: Dictionary, b: Dictionary) -> bool:
	for k in b.keys():
		if int(a.get(k, -1)) != int(b[k]):
			return false
	return true


# ------------------------------------------------------------------------------------------------ the netrun's close
## The close of every netrun, deaths included (SPEC section 2 and 6): a failed Genome Core breach counts (one retry, then
## the held Exploits are spent), a DOSE card arrives every `dose_every` netruns, the raid Heat levels the Heat has reached
## fire, the cadence counts the netrun and a raid is queued when it is due. `breach_failed` = a run on the Genome Core died.
## Returns events. The campaign's own rules already paid the netrun's Heat, Schematics and Exploit.
static func netrun_closed(campaign: CampaignState, corp: CorporationData, cfg: CampaignConfigData, breach_failed: bool) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	if not active(campaign) or campaign.is_over():
		return events
	var tide := campaign.corp_theme.solace.tide
	if breach_failed:
		var scratch := SolaceTideState.new()
		scratch.breach_fails = tide.breach_fails
		if SolaceTideRules.breach_retry(scratch, cfg):
			campaign.exploits.clear()
			events.append({"type": "exploits_spent", "text": "The breach failed again: Solace patched the Exploits. Take them again."})
		else:
			events.append({"type": "breach_retry", "text": "The breach failed. One more attempt is allowed."})
		tide.breach_fails = scratch.breach_fails
	var n := campaign.runs_completed + campaign.deaths
	if cfg.solace_tide_dose_every > 0 and n % cfg.solace_tide_dose_every == 0:
		SolaceTideRules.add_dose(tide)
		events.append({"type": "dose", "text": "A stolen antidote sample (DOSE) joins the defense deck."})
	sweep_crossings(campaign, cfg)
	var st := load_state(campaign, corp, cfg)
	SolaceTideRules.check_loss(st)
	if st.lost != SolaceTideState.LOST_NONE:
		events.append_array(store_state(campaign, st))
		return events
	var crossed := tide.heat_crossed
	tide.heat_crossed = false
	st = SolaceTideState.from_block(tide.block_dict())
	if SolaceTideRules.note_netrun(st, cfg, crossed):
		if campaign.pending_raids.is_empty():
			var raid := CampaignRules.tide_raid_for(corp, crossed)
			campaign.pending_raids.append({"raid_id": String(raid.id) if raid != null else "", "source": RC.RaidTriggerSource.HEAT_THRESHOLD \
				if crossed else RC.RaidTriggerSource.TERRITORY_CLAIM, "site_id": "", "corporation": String(campaign.corporation_id), "model": "tide"})
			events.append({"type": "raid_pending", "raid_id": raid.id if raid != null else &"",
				"text": "A tide raid is coming (%s)." % ("Heat level crossed" if crossed else "%d netruns since the last raid" % st.netruns_since_raid)})
	tide.netruns_since_raid = st.netruns_since_raid
	return events


## Fires every raid Heat level the Heat has reached and that has not fired (SolaceTideRules.add_heat's rule, by state): the
## threshold's one-time effects run (complications) and `tide.heat_crossed` is set; crossing the PURGE level queues the PURGE
## raid's damage. A level reached during a raid (clean-defense Heat, ghost Heat) therefore fires at the next netrun's close.
static func sweep_crossings(campaign: CampaignState, cfg: CampaignConfigData) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	var levels: Array = []
	for t in cfg.heat_thresholds:
		if t != null and (t.kind == RC.ThresholdKind.MAJOR or t.kind == RC.ThresholdKind.PURGE):
			levels.append(t)
	levels.sort_custom(func(a: HeatThresholdData, b: HeatThresholdData) -> bool: return a.heat < b.heat)
	for t in levels:
		if campaign.heat >= t.heat and not campaign.thresholds_fired.has(t.heat):
			campaign.thresholds_fired.append(t.heat)
			events.append_array(HeatRules.fire_threshold(campaign, t))
	return events


# ------------------------------------------------------------------------------------------------ the Armory (R-C)
## An Armory asset becomes a defense card (R-C): the type and verb come from its asset type (config). Returns the card or [].
static func asset_banked(campaign: CampaignState, cfg: CampaignConfigData, lookup: ContentLookup, asset_id: StringName) -> Array:
	if not active(campaign) or lookup == null:
		return []
	var asset := lookup.get_content(asset_id) as DefenseAssetData
	if asset == null:
		return []
	var tide := campaign.corp_theme.solace.tide
	var tv := cfg.solace_tide_asset_card(int(asset.asset_type))
	SolaceTideRules.add_asset(tide, String(tv[0]), String(tv[1]))
	return _newest_asset_card(tide)


static func _newest_asset_card(tide: SolaceTideState) -> Array:
	var id := "a%02d" % (tide.asset_n - 1)
	for c in tide.deck:
		if c[0] == id:
			return c
	return []


# ------------------------------------------------------------------------------------------------ the HQ step
## The CLEAN purchase's price (config).
static func clean_price(cfg: CampaignConfigData) -> int:
	return cfg.solace_tide_clean_price


## Why CLEAN is refused ("" when allowed): no tide, no INFECTED card, or too few Schematics.
static func clean_error(campaign: CampaignState, cfg: CampaignConfigData) -> String:
	if not active(campaign):
		return "This campaign has no infection."
	if infected_count(campaign) <= 0:
		return "No district is infected."
	if campaign.schematics < clean_price(cfg):
		return "CLEAN costs %d Schematics." % clean_price(cfg)
	return ""


## CLEAN (SPEC section 6): pays the price and removes the highest-id INFECTED card. Returns events.
static func clean(campaign: CampaignState, cfg: CampaignConfigData) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	var err := clean_error(campaign, cfg)
	if err != "":
		events.append({"type": "refused", "text": err})
		return events
	var tide := campaign.corp_theme.solace.tide
	var worst := ""
	for c in tide.deck:
		if c[2] == SolaceTideState.VERB_WOUND and String(c[0]) > worst:
			worst = c[0]
	tide.remove_card(worst)
	campaign.schematics -= clean_price(cfg)
	events.append({"type": "clean", "card": worst, "cost": clean_price(cfg),
		"text": "CLEAN: one infected district is cured (-%d Schematics)." % clean_price(cfg)})
	return events
