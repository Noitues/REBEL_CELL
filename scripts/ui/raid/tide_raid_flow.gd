class_name TideRaidFlow
extends RefCounted
## Phase 3: the player's way through one Solace Infected Tide raid, over SolaceTideRaid (the rules). The flow decides nothing the
## rules decide: it holds the phase, the picked card, the choices the screen offers (the response rows, their worst and best
## tiers, the guard line, the confirms) and calls SolaceTideRaid / RunManager for every change of state. The screen
## (TideRaidScreen) draws it and tells it what the player pressed; the flow has no Node.
##
## Phases: DECAY (the beat), DRAW (the hand), PLAN (cards on Sites, the ghost), FORECAST (the 12 outcomes), REVEAL (sealed A),
## RESPONSE, PLAYOUT (known beams, sealed A, the B lean and pick, sealed B, the hunter), AFTERMATH (the stamp), HQ_STEP, DONE.
## Undo works in PLAN and FORECAST (SolaceTideRaid.rewind) and the response can be re-picked; the RESPONSE commit is the
## checkpoint: the raid resolves and nothing rewinds after it.

enum Phase { DECAY, DRAW, PLAN, FORECAST, REVEAL, RESPONSE, PLAYOUT, AFTERMATH, HQ_STEP, DONE }

const HOLD := "HOLD"
## The paid-row mean tolerance when ranking responses.
const MEAN_EPS := 1e-6
## The friction words of the launch confirm.
const FRICTION_NONE := ""
const FRICTION_BREACH := "breach"
const FRICTION_LOSS := "loss"
const FRICTION_LAST := "last"

var raid: SolaceTideRaid
var campaign: CampaignState
var corp: CorporationData
var cfg: CampaignConfigData
var phase: int = Phase.DECAY
## The hand card the player picked (not yet placed), "" when none.
var sel_card: String = ""
## The HUD numbers as they stood after DECAY (kept until the aftermath shows the result).
var hud_pre: Dictionary = {}
## True when every response row yields one tier on every outcome (LOCKED): the raid resolves fast, no RESPONSE panel.
var fast: bool = false
## The friction the launch armed (a second press launches).
var launch_armed: bool = false
## The HOLD confirm: HOLD loses HOME integrity some row saves; a second press commits.
var hold_armed: bool = false
## The lethal confirm: the picked response ends the campaign on some outcome; a second press commits.
var lethal_armed: bool = false
var _lethal_key: String = ""
## INFECTED cards the playout has landed so far (the HUD, the meter and the deck strip tick with them); -1 outside the playout.
var landed: int = -1
## The raids pending when the response was committed (the top bar's RAIDS holds this until the aftermath); -1 before.
var raids_before: int = -1
var _fresh: Array = []
var _fresh_ready: bool = false
## The RESPONSE rows (groups) of the current placement and the picked one.
var groups: Array = []
var ghosts: Array = []
## head -> how many rows of it fold into HOLD (they change nothing this raid).
var folded: Dictionary = {}
var resp_sel: int = -1
## The raid played (SolaceTideRules.play result), the events RunManager returned and the campaign's `last_raid`.
var result: Dictionary = {}
var events: Array[Dictionary] = []
var last_raid: Dictionary = {}
## DECAY's INFECTED accounting (SolaceTideTally.decay_tally), empty when DECAY did not run for this raid.
var decay_tally: Dictionary = {}
## The beats the screen plays after the commit (see `beats`).
var _beats: Array = []
var _fc_key: String = ""
var _fc: Array = []
var _guard_key: String = ""
var _guard: Dictionary = {}
## Raid lines the HQ step still offers: the options (SolaceTideRules.between_options) are read live from the campaign.


## Opens the pending raid of `campaign` (DECAY runs now). Null when the corporation does not play the tide.
static func open(p_campaign: CampaignState, p_corp: CorporationData, p_cfg: CampaignConfigData, pending: Dictionary) -> TideRaidFlow:
	if p_campaign == null or not SolaceTideCampaign.active(p_campaign) or not CampaignRules.uses_tide(p_corp):
		return null
	var f := TideRaidFlow.new()
	f.campaign = p_campaign
	f.corp = p_corp
	f.cfg = p_cfg
	var pre: SolaceTideState = null
	if SolaceTideCampaign.raids_fought(p_campaign) > 0 and not p_campaign.corp_theme.solace.tide.decayed:
		pre = SolaceTideCampaign.load_state(p_campaign, p_corp, p_cfg)
	f.raid = SolaceTideRaid.open(p_campaign, p_corp, p_cfg, pending)
	if pre != null:
		f.decay_tally = SolaceTideTally.decay_tally(pre, p_cfg)
	f.hud_pre = f.hud_of(f.raid.st)
	f.phase = Phase.DECAY
	return f


# ------------------------------------------------------------------------------------------------ small reads
func ctx() -> SolaceTideRules.Ctx:
	return raid.ctx


func board() -> SolaceTideBoard:
	return raid.ctx.board if raid.ctx != null else SolaceTideCampaign.board_for(corp, cfg)


## The HUD numbers of a tide state: INFECTED and healthy cards, the CITY LOST line, HOME, Heat and its band, the hand and beam
## counts, the DOSE cards and the deck.
func hud_of(st: SolaceTideState) -> Dictionary:
	var wounds := st.wound_count()
	var healthy := st.deck.size() - wounds
	return {"infected": wounds, "healthy": healthy, "margin": SolaceTideRules.loss_margin(st), "doses": st.dose_cards().size(), "home": st.home, "home_max": st.home_max, "heat": st.heat,
		"band": SolaceTideRules.band(st.heat, cfg), "hand": SolaceTideRules.hand_size(st.heat, cfg), "beams": SolaceTideRules.known_count(st.heat, cfg),
		"ghost": st.ghost, "deck": st.deck.duplicate(true), "schematics": st.schematics}


## The HUD numbers now: before the raid until the aftermath, then what the campaign holds.
func hud() -> Dictionary:
	if phase == Phase.PLAYOUT and raid.resolved and not raid.over and landed >= 0:
		return hud_live(landed)
	if phase >= Phase.AFTERMATH and phase != Phase.DONE and raid.resolved:
		return hud_of(SolaceTideCampaign.load_state(campaign, corp, cfg)) if not raid.over else hud_pre
	return hud_pre


## The HUD while the playout runs: the state after DECAY with the first `n` INFECTED cards the raid adds already in the deck (the
## cards land one by one as the beams hit; the rest of the numbers stay as they were until the aftermath).
func hud_live(n: int) -> Dictionary:
	var out := hud_pre.duplicate(true)
	var fresh := new_wounds()
	var s: SolaceTideState = raid.st.duplicate_state()
	for i in mini(n, fresh.size()):
		s.deck.append(fresh[i])
	s.sort_deck()
	var h := hud_of(s)
	for k in ["infected", "healthy", "margin", "deck"]:
		out[k] = h[k]
	return out


## The INFECTED cards the resolved raid added to the deck, in deck order (empty before the resolve).
func new_wounds() -> Array:
	if _fresh_ready:
		return _fresh
	var out: Array = []
	if not raid.resolved or raid.over:
		return out
	var post := SolaceTideCampaign.load_state(campaign, corp, cfg)
	var had := {}
	for c in raid.st.deck:
		had[String(c[0])] = true
	for c in post.deck:
		if not had.has(String(c[0])) and String(c[2]) == SolaceTideState.VERB_WOUND:
			out.append(c)
	_fresh = out
	_fresh_ready = true
	return out


## The playout landed one more INFECTED card (the screen tells the flow at the beat a Site is lost).
func land_infected() -> void:
	if landed >= 0:
		landed = mini(landed + 1, new_wounds().size())


## The top bar's RAIDS count while the playout runs (the raid is not dealt with until the aftermath); -1 = the campaign's own.
func raids_shown() -> int:
	return raids_before if phase == Phase.PLAYOUT and raids_before >= 0 else -1


## The raid's number as the player counts it: the first raid of the campaign is 1.
func raid_number() -> int:
	return raid.raid_idx + 1


## How many more INFECTED cards end the city, at the HUD numbers `h` (the state at PLAN).
## How many more INFECTED cards end the city (SolaceTideRules.loss_margin of the HUD's state).
func loss_margin(h: Dictionary = {}) -> int:
	var hh := h if not h.is_empty() else hud()
	return int(hh["margin"])


## True when one more INFECTED card ends the city (margin 1) or the city already falls when this raid closes (margin 0).
func loss_warning() -> bool:
	return loss_margin() <= 1


## The Heat levels (config) with what each adds to the raid: [{heat, beam (bool), card (bool)}].
func heat_ticks() -> Array:
	var out: Array = []
	var levels := {}
	for lv in cfg.solace_tide_hand_heat:
		levels[int(lv)] = levels.get(int(lv), {"heat": int(lv), "beam": false, "card": false})
		levels[int(lv)]["card"] = true
	for lv in cfg.solace_tide_beam_heat:
		levels[int(lv)] = levels.get(int(lv), {"heat": int(lv), "beam": false, "card": false})
		levels[int(lv)]["beam"] = true
	var ks: Array = levels.keys()
	ks.sort_custom(func(a: int, b: int) -> bool: return a < b)
	for k in ks:
		out.append(levels[k])
	return out


func site_name(id: StringName) -> String:
	if id == board().home or id == SolaceTideRules.HOME_WORD:
		return "HOME"
	var sd := corp.city_grid.get_site(id)
	if sd == null:
		return TextDb.mark("Site")
	var nm := TextDb.t(sd, "display_name")
	return nm if nm != "" else TextDb.mark("Site")


## Hand cards in drawn order: {id, type, verb, site (the Site it stands on or ""), extra (the card a Heat level dealt)}.
func hand_cards() -> Array:
	var out: Array = []
	if raid.ctx == null:
		return out
	var on := {}
	for s in raid.place["sentries"]:
		on[raid.place["sentries"][s]] = s
	var i := 0
	for id in raid.ctx.hand:
		var c: Array = raid.ctx.cards[id]
		out.append({"id": id, "type": c[0], "verb": c[1], "site": String(on.get(id, "")), "extra": i >= cfg.solace_tide_hand_base})
		i += 1
	return out


## The Sites a sentry can stand on this raid (live Sites on the raid's lines), sorted.
func placeable_sites() -> Array[StringName]:
	var out: Array[StringName] = []
	if raid.ctx == null:
		return out
	for s in raid.ctx.rel:
		if not (raid.place["sentries"] as Dictionary).has(s):
			out.append(s)
	return out


## Every raid line as {name, kind, cells, type, state}: the known beams (fired after the RESPONSE), the sealed candidates and the
## hunter's two streets.
func lines() -> Array:
	var out: Array = []
	if raid.ctx == null:
		return out
	var d: Dictionary = raid.ctx.draw
	for i in (d["known"] as Array).size():
		out.append({"name": "known%d" % i, "role": "known", "index": i, "line": d["known"][i], "fires": i < SolaceTideRules.known_count(raid_heat(), cfg)})
	for i in (d["cands"] as Array).size():
		out.append({"name": "cand%d" % i, "role": "cand", "index": i, "line": d["cands"][i], "fires": true})
	for i in (d["hunters"] as Array).size():
		out.append({"name": "hunter%d" % i, "role": "hunter", "index": i, "line": d["hunters"][i], "fires": true})
	return out


## The Heat the raid fires its known beams at (the state's, plus the ghost's when it is placed).
func raid_heat() -> int:
	return raid.st.heat + (cfg.solace_tide_ghost_heat if raid.place["ghost"] != &"" else 0)


## How many known beams fire with the current placement.
func known_firing() -> int:
	return SolaceTideRules.known_count(raid_heat(), cfg)


# ------------------------------------------------------------------------------------------------ phases
## Moves to the next beat (DECAY -> DRAW -> PLAN, AFTERMATH -> HQ_STEP).
func advance() -> void:
	match phase:
		Phase.DECAY:
			phase = Phase.AFTERMATH if raid.over else Phase.DRAW
			if raid.over:
				_settle_lost()
		Phase.DRAW:
			phase = Phase.PLAN
		Phase.AFTERMATH:
			phase = Phase.DONE if campaign.is_over() else Phase.HQ_STEP
		Phase.HQ_STEP:
			phase = Phase.DONE


## DECAY ended the campaign: the raid closes as CITY LOST through RunManager (pending consumed, saved).
func _settle_lost() -> void:
	events = RunManager.fight_tide_raid(raid)
	last_raid = campaign.last_raid.duplicate(true)


# ------------------------------------------------------------------------------------------------ PLAN
func pick_card(id: String) -> bool:
	if phase != Phase.PLAN:
		return false
	for c in hand_cards():
		if c["id"] == id and c["site"] == "" and SolaceTideRules.PLACEABLE.has(c["verb"]):
			sel_card = id if sel_card != id else ""
			return true
	return false


## Why card `id` cannot be placed on `site` ("" when it can).
func place_error(id: String, site: StringName) -> String:
	if id == "":
		return TextDb.mark("Pick a card first.")
	if not SolaceTideRules.PLACEABLE.has(raid.ctx.cards[id][1]):
		return TextDb.mark("That card cannot stand guard.")
	if not raid.ctx.rel.has(site):
		return TextDb.mark("No beam reaches that district.")
	if (raid.place["sentries"] as Dictionary).has(site):
		return TextDb.mark("A sentry already stands there.")
	if (raid.place["sentries"] as Dictionary).size() >= cfg.solace_tide_max_placed:
		return TextDb.mark("Only %d cards can stand guard.") % cfg.solace_tide_max_placed
	return ""


## Places the picked card on `site` (a Site on the raid's lines). Returns the error ("" = placed).
func place_on(site: StringName) -> String:
	if phase != Phase.PLAN:
		return TextDb.mark("Not now.")
	var err := place_error(sel_card, site)
	if err != "":
		return err
	var sent: Dictionary = (raid.place["sentries"] as Dictionary).duplicate()
	sent[site] = sel_card
	sel_card = ""
	raid.set_place({"sentries": normalize(sent), "ghost": raid.place["ghost"]})
	return ""


## Takes the sentry on `site` back to the hand.
func unplace(site: StringName) -> void:
	if phase != Phase.PLAN or not (raid.place["sentries"] as Dictionary).has(site):
		return
	var sent: Dictionary = (raid.place["sentries"] as Dictionary).duplicate()
	sent.erase(site)
	raid.set_place({"sentries": normalize(sent), "ghost": raid.place["ghost"]})


## The ghost on HOME (+Heat when launched) or off it. False when the kit has none.
func toggle_ghost() -> bool:
	if phase != Phase.PLAN:
		return false
	var on: bool = raid.place["ghost"] != &""
	if not on and raid.st.ghost <= 0:
		return false
	raid.set_place({"sentries": (raid.place["sentries"] as Dictionary).duplicate(), "ghost": &"" if on else SolaceTideRules.HOME_WORD})
	return true


## The placement as SolaceTideRules.placements lists it: in Site order each sentry takes the lowest free card id of its
## (type, verb) signature.
func normalize(sent: Dictionary) -> Dictionary:
	var sites: Array = sent.keys()
	IdSort.sort_ids(sites)
	var used: Array = []
	var out := {}
	for s in sites:
		var sig: Array = raid.ctx.cards[sent[s]]
		var pick := SolaceTideRules._pick(raid.ctx, raid.ctx.hand, sig, used)
		used.append(pick)
		out[s] = pick
	return out


func can_undo() -> bool:
	return (phase == Phase.PLAN or phase == Phase.FORECAST) and raid.can_rewind()


func undo() -> bool:
	if not can_undo():
		return false
	sel_card = ""
	return raid.rewind()


## True when the placement is one SolaceTideRules.placements lists (the flow test pins it).
func place_is_legal() -> bool:
	for p in raid.placements():
		if _same_place(p, raid.place):
			return true
	return false


static func _same_place(a: Dictionary, b: Dictionary) -> bool:
	if a["ghost"] != b["ghost"]:
		return false
	var sa: Dictionary = a["sentries"]
	var sb: Dictionary = b["sentries"]
	if sa.size() != sb.size():
		return false
	for k in sa.keys():
		if not sb.has(k) or sb[k] != sa[k]:
			return false
	return true


# ------------------------------------------------------------------------------------------------ forecast, guard
## The 12 outcomes of the current placement under `resp` (default HOLD), cached.
func forecast(resp: Array = [HOLD]) -> Array:
	var key := str([raid.place, resp])
	if key != _fc_key:
		_fc_key = key
		_fc = SolaceTideRules.forecast(raid.ctx, raid.st, raid.place, resp)
	return _fc


## [worst, best] tier over outcome rows.
func tier_range(rows: Array) -> Array:
	var worst := ""
	var best := ""
	for r in rows:
		var t := String(r["tier"])
		if worst == "" or TideGlyphs.rank(t) > TideGlyphs.rank(worst):
			worst = t
		if best == "" or TideGlyphs.rank(t) < TideGlyphs.rank(best):
			best = t
	if worst == "":
		return [SolaceTideRules.TIER_HOLDS, SolaceTideRules.TIER_HOLDS]
	return [worst, best]


## The mean damage of outcome rows in the automatic defense's weights (lower is better).
func mean_damage(rows: Array) -> float:
	var total := 0.0
	for r in rows:
		total += float(SolaceTideCampaign.damage_of(raid.st, r["result"]["state"], cfg))
	return total / maxf(1.0, rows.size())


## The lowest HOME over outcome rows.
func min_home(rows: Array) -> int:
	var lo := 1 << 30
	for r in rows:
		lo = mini(lo, (r["result"]["state"] as SolaceTideState).home)
	return lo


## The worst tier of each candidate route A (0..2) under HOLD: the HOME tier glyph at the end of each route.
func route_tiers() -> Array:
	var out: Array = []
	var n := (raid.ctx.draw["cands"] as Array).size()
	for a in n:
		var rows: Array = []
		for r in forecast():
			if r["a"] == a:
				rows.append(r)
		out.append(tier_range(rows)[0])
	return out


## The plan's forecast under HOLD: {worst, best, locked (one tier on every outcome), home_drop (HOME falls on every outcome),
## home_breach, home_now}.
func plan_summary() -> Dictionary:
	var rows := forecast()
	var rng := tier_range(rows)
	var all_loss := not rows.is_empty()
	var all_breach := all_loss
	for r in rows:
		var h := (r["result"]["state"] as SolaceTideState).home
		if h >= raid.st.home:
			all_loss = false
		if h > 0:
			all_breach = false
	return {"worst": rng[0], "best": rng[1], "locked": rng[0] == rng[1], "home_drop": all_loss, "home_breach": all_breach, "home_now": raid.st.home}


## The launch confirm: "breach" (HOME breaks on every outcome), "loss" (HOME drops on every outcome), "last" (HOME is at 1), "".
func friction() -> String:
	var s := plan_summary()
	if s["home_breach"]:
		return FRICTION_BREACH
	if s["home_drop"]:
		return FRICTION_LOSS
	if raid.st.home == 1:
		return FRICTION_LAST
	return FRICTION_NONE


func to_forecast() -> bool:
	if phase != Phase.PLAN or not place_is_legal():
		return false
	launch_armed = false
	phase = Phase.FORECAST
	return true


func back_to_plan() -> void:
	if phase == Phase.FORECAST:
		launch_armed = false
		phase = Phase.PLAN


## LAUNCH: sealed A is revealed. With a friction the first press only arms ("confirm" is returned), the second launches.
## Returns "launched", "confirm" or "no".
func launch() -> String:
	if phase != Phase.FORECAST or not place_is_legal():
		return "no"
	if friction() != FRICTION_NONE and not launch_armed:
		launch_armed = true
		return "confirm"
	launch_armed = false
	_build_responses()
	fast = _uniform()
	phase = Phase.REVEAL
	return "launched"


## The real sealed route A (an index into the candidates) the REVEAL shows.
func real_a() -> int:
	return int(raid.ctx.draw["real_a"])


func reveal_done() -> void:
	if phase == Phase.REVEAL:
		phase = Phase.RESPONSE
		resp_sel = -1
		hold_armed = false


# ------------------------------------------------------------------------------------------------ RESPONSE
## Builds the response rows: every `response_options` entry with its 12 outcomes, merged when the outcomes are identical (one
## kind), the rows that beat HOLD first (best mean first), the ghost rows for the kinds that cannot be played.
func _build_responses() -> void:
	var opts := raid.response_options()
	var rows: Array = []
	var hold_row: Dictionary = {}
	for i in opts.size():
		var r: Array = opts[i]
		var fc := SolaceTideRules.forecast(raid.ctx, raid.st, raid.place, r)
		var rng := tier_range(fc)
		var row := {"resp": r, "head": String(r[0]), "worst": rng[0], "best": rng[1], "mean": mean_damage(fc), "min_home": min_home(fc),
			"sig": _signature(fc), "index": i}
		row.merge(outcome_stats(fc))
		rows.append(row)
		if row["head"] == HOLD:
			hold_row = row
	var by_key := {}
	groups = []
	for row in rows:
		var key := String(row["head"]) + "|" + String(row["sig"])
		if row["head"] == HOLD or row["head"] == "JAM" or row["head"] == "JAM_B":
			key += "|%d" % int(row["index"])
		if row["head"] == "DEPLOY":
			key += "|" + String(row["resp"][1])
		if by_key.has(key):
			(groups[by_key[key]]["members"] as Array).append(row)
		else:
			by_key[key] = groups.size()
			var better := false
			if not hold_row.is_empty() and row["head"] != HOLD:
				var rw := TideGlyphs.rank(row["worst"])
				var hw := TideGlyphs.rank(hold_row["worst"])
				better = rw < hw or (rw == hw and float(row["mean"]) < float(hold_row["mean"]) - MEAN_EPS)
			var nothing: bool = not hold_row.is_empty() and row["head"] != HOLD and row["sig"] == hold_row["sig"] \
				and SolaceTideRules.CARD_RESPONSES.has(String(row["head"]))
			groups.append({"members": [row], "better": better, "changes_nothing": nothing, "first": groups.size()})
	# A card response whose every outcome equals HOLD's is not a choice: it folds into the HOLD row ("+N same as hold").
	var kept: Array = []
	var same_n := 0
	folded = {}
	for g in groups:
		if bool(g["changes_nothing"]):
			same_n += (g["members"] as Array).size()
			var fh := String(g["members"][0]["head"])
			folded[fh] = int(folded.get(fh, 0)) + (g["members"] as Array).size()
		else:
			kept.append(g)
	groups = kept
	for g in groups:
		g["same"] = same_n if String(g["members"][0]["head"]) == HOLD else 0
		var any := false
		var every := true
		for m in g["members"]:
			any = any or bool(m["lethal_any"])
			every = every and bool(m["lethal_all"])
		g["lethal_any"] = any
		g["lethal_all"] = every
	var good: Array = []
	var rest: Array = []
	for g in groups:
		(good if g["better"] else rest).append(g)
	good.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		var ma := float(a["members"][0]["mean"])
		var mb := float(b["members"][0]["mean"])
		if absf(ma - mb) > MEAN_EPS:
			return ma < mb
		return int(a["first"]) < int(b["first"]))
	# A row that can end the campaign ranks below every row that cannot, whatever its tier.
	var safe: Array = []
	var deadly: Array = []
	for g in good + rest:
		(deadly if bool(g["lethal_any"]) else safe).append(g)
	groups = safe + deadly
	_label_groups()
	_build_ghosts(opts)


## What a set of outcome rows (a forecast, from SolaceTideRules.forecast) does to the Heat and to the INFECTED count, and whether it ends the
## campaign: {heat_lo, heat_hi (the Heat change), inf_lo, inf_hi (the INFECTED cards added), lethal_any, lethal_all (the campaign is lost on
## some / every outcome), n}. Read from the rules' own states, so it equals what the resolve gives.
func outcome_stats(rows: Array) -> Dictionary:
	var out := {"heat_lo": 0, "heat_hi": 0, "inf_lo": 0, "inf_hi": 0, "lethal_any": false, "lethal_all": not rows.is_empty(), "n": rows.size()}
	var first := true
	for r in rows:
		var ns: SolaceTideState = r["result"]["state"]
		var dh := ns.heat - raid.st.heat
		var di := ns.wound_count() - raid.st.wound_count()
		var dead := ns.lost != SolaceTideState.LOST_NONE
		if first:
			out["heat_lo"] = dh
			out["heat_hi"] = dh
			out["inf_lo"] = di
			out["inf_hi"] = di
			first = false
		else:
			out["heat_lo"] = mini(int(out["heat_lo"]), dh)
			out["heat_hi"] = maxi(int(out["heat_hi"]), dh)
			out["inf_lo"] = mini(int(out["inf_lo"]), di)
			out["inf_hi"] = maxi(int(out["inf_hi"]), di)
		out["lethal_any"] = bool(out["lethal_any"]) or dead
		out["lethal_all"] = bool(out["lethal_all"]) and dead
	return out


## The stats of response `r` (a response array) over the placement now.
func resp_stats(r: Array) -> Dictionary:
	return outcome_stats(SolaceTideRules.forecast(raid.ctx, raid.st, raid.place, r))


## The tiles of route column `a` under HOLD: one per (tier, INFECTED added, ends the campaign), worst first, each
## {tier, n, inf (cards added), lethal}. The forecast column draws them.
func route_tiles(a: int) -> Array:
	var by_key := {}
	for r in forecast():
		if int(r["a"]) != a:
			continue
		var ns: SolaceTideState = r["result"]["state"]
		var di := ns.wound_count() - raid.st.wound_count()
		var dead := ns.lost != SolaceTideState.LOST_NONE
		var key := "%s|%d|%s" % [r["tier"], di, dead]
		if not by_key.has(key):
			by_key[key] = {"tier": String(r["tier"]), "n": 0, "inf": di, "lethal": dead}
		by_key[key]["n"] = int(by_key[key]["n"]) + 1
	var out: Array = by_key.values()
	out.sort_custom(func(x: Dictionary, y: Dictionary) -> bool:
		if bool(x["lethal"]) != bool(y["lethal"]):
			return bool(x["lethal"])
		var rx := TideGlyphs.rank(String(x["tier"]))
		var ry := TideGlyphs.rank(String(y["tier"]))
		if rx != ry:
			return rx > ry
		return int(x["inf"]) > int(y["inf"]))
	return out


## The Heat the plan leaves under HOLD: {now, lo, hi} (the Heat now, and the lowest and highest Heat after the raid). The ghost and the
## clean-defense bonus are in it; equals the real Heat change of a HOLD (the forecast is the resolve).
func pending_heat() -> Dictionary:
	var st := outcome_stats(forecast())
	return {"now": raid.st.heat, "lo": raid.st.heat + int(st["heat_lo"]), "hi": raid.st.heat + int(st["heat_hi"])}


## The forecast row of the real outcome (the real sealed A and hunter street) for response `r`: what `commit` will play.
func real_row(r: Array) -> Dictionary:
	var a := int(raid.ctx.draw["real_a"])
	var h := int(raid.ctx.draw["hunter_real"])
	for row in SolaceTideRules.forecast(raid.ctx, raid.st, raid.place, r):
		if int(row["a"]) == a and int(row["hunter"]) == h and int(row["b_slot"]) == 0:
			return row
	return {}


func type_name(t: String) -> String:
	match t:
		"D":
			return tr("DRONE")
		"N":
			return tr("NETRUNNER")
		"E":
			return tr("ENFORCER")
	return t


## The short text of response `r`: the verb and where (the row's glyph and chips carry the rest).
func resp_label(r: Array) -> String:
	match String(r[0]):
		"HOLD":
			return tr("HOLD")
		"JAM":
			return tr("JAM hunter")
		"JAM_B":
			return tr("JAM sealed B")
		"DEPLOY":
			return tr("DEPLOY > %s") % site_name(StringName(r[2]))
		"SACRIFICE":
			return tr("SACRIFICE %s") % site_name(StringName(r[1]))
		"REDEPLOY":
			return tr("MOVE %s > %s") % [site_name(StringName(r[1])), site_name(StringName(r[2]))]
		"DIVERT":
			return tr("DIVERT beam %d") % (int(r[1]) + 1)
	return String(r[0])


## The long text of response `r`: names the card or the path too, so two rows never read alike.
func resp_label_long(r: Array) -> String:
	match String(r[0]):
		"DEPLOY":
			return tr("DEPLOY %s > %s") % [type_name(String(r[1])), site_name(StringName(r[2]))]
		"DIVERT":
			return tr("DIVERT beam %d via %s") % [int(r[1]) + 1, _divert_via(r)]
	return resp_label(r)


## The district a DIVERT's new path goes through that the beam's own line does not (its last cell when none differs).
func _divert_via(r: Array) -> String:
	var known: Array = raid.ctx.draw["known"][int(r[1])]["cells"]
	var path: Array = r[2]
	for c in path:
		if not known.has(c):
			return site_name(StringName(String(c)))
	return site_name(StringName(String(path[path.size() - 1]))) if not path.is_empty() else tr("a new street")


## Gives every group its `label`: short text, "xN" when variants share it, the long form when two groups would read alike, and a
## number as the last resort. Row labels are unique.
func _label_groups() -> void:
	var seen := {}
	for g in groups:
		var members: Array = g["members"]
		var lab := resp_label(members[0]["resp"])
		if members.size() > 1:
			lab = _multi_label(g)
		g["label"] = lab
		seen[lab] = int(seen.get(lab, 0)) + 1
	for g in groups:
		if int(seen[g["label"]]) > 1:
			var members: Array = g["members"]
			var lab := resp_label_long(members[0]["resp"])
			if members.size() > 1:
				lab = "%s  x%d" % [_multi_base(members[0]["resp"], true), members.size()]
			g["label"] = lab
	var used := {}
	for g in groups:
		var lab: String = g["label"]
		if used.has(lab):
			used[lab] = int(used[lab]) + 1
			g["label"] = "%s (%d)" % [lab, int(used[lab])]
		else:
			used[lab] = 1


func _multi_label(g: Dictionary) -> String:
	var members: Array = g["members"]
	return "%s  x%d" % [_multi_base(members[0]["resp"], false), members.size()]


func _multi_base(r0: Array, long: bool) -> String:
	match String(r0[0]):
		"REDEPLOY":
			return tr("MOVE %s") % site_name(StringName(r0[1]))
		"DEPLOY":
			return tr("DEPLOY %s") % type_name(String(r0[1]))
		"SACRIFICE":
			return tr("SACRIFICE")
		"DIVERT":
			return tr("DIVERT beam %d via %s") % [int(r0[1]) + 1, _divert_via(r0)] if long else tr("DIVERT beam %d") % (int(r0[1]) + 1)
	return String(r0[0])


## What a response needs from the hand: {kind ("" | "SHIFT" | "JAM" | type letter), have (bool)}. The flow's rows are built from the rules' options,
## which offer a row only when the card is in the response hand; this reads it back so the screen can name the card and a test can pin it.
func resp_need(r: Array) -> Dictionary:
	var sw := SolaceTideRules.launch(raid.ctx, raid.st, raid.place)
	match String(r[0]):
		"REDEPLOY", "DIVERT":
			return {"kind": SolaceTideState.VERB_SHIFT, "have": SolaceTideRules._has_verb(sw.rhand, SolaceTideState.VERB_SHIFT)}
		"JAM", "JAM_B":
			return {"kind": SolaceTideState.VERB_JAM, "have": SolaceTideRules._has_verb(sw.rhand, SolaceTideState.VERB_JAM)}
		"DEPLOY":
			var id := SolaceTideRules._deploy_card(sw.rhand, String(r[1]))
			return {"kind": String(r[1]), "have": id != "", "card": id}
	return {"kind": "", "have": true}


func _signature(fc: Array) -> String:
	var parts := PackedStringArray()
	for r in fc:
		var ns: SolaceTideState = r["result"]["state"]
		var ks: Array = ns.owned.keys()
		IdSort.sort_ids(ks)
		var s := ""
		for k in ks:
			s += "%s=%d," % [k, int(ns.owned[k])]
		parts.append("%s/%d/%s" % [r["tier"], ns.home, s])
	return "|".join(parts)


func _uniform() -> bool:
	# One tier everywhere is not enough to skip the choice: a response that adds INFECTED cards or ends the run is a decision too.
	var tiers := {}
	var marks := {}
	for g in groups:
		for m in g["members"]:
			var fc := SolaceTideRules.forecast(raid.ctx, raid.st, raid.place, m["resp"])
			for r in fc:
				tiers[r["tier"]] = true
				var ns: SolaceTideState = r["result"]["state"]
				marks["%d|%s" % [ns.wound_count() - raid.st.wound_count(), ns.lost != SolaceTideState.LOST_NONE]] = true
	return tiers.size() <= 1 and marks.size() <= 1


func _build_ghosts(opts: Array) -> void:
	ghosts = []
	var heads := {}
	for r in opts:
		heads[String(r[0])] = true
	var sw := SolaceTideRules.launch(raid.ctx, raid.st, raid.place)
	var has_shift := false
	var has_jam := false
	for c in sw.rhand:
		has_shift = has_shift or c[2] == SolaceTideState.VERB_SHIFT
		has_jam = has_jam or c[2] == SolaceTideState.VERB_JAM
	var sent_n := (raid.place["sentries"] as Dictionary).size()
	if not heads.has("REDEPLOY"):
		if not has_shift:
			ghosts.append(["REDEPLOY", TextDb.mark("REDEPLOY: no SHIFT card in hand")])
		elif sent_n == 0:
			ghosts.append(["REDEPLOY", TextDb.mark("REDEPLOY: no sentry on the board")])
		else:
			ghosts.append(["REDEPLOY", TextDb.mark("REDEPLOY: no free district")])
	if not heads.has("DEPLOY"):
		ghosts.append(["DEPLOY", TextDb.mark("DEPLOY: no card left in hand") if sw.rhand.is_empty() else TextDb.mark("DEPLOY: no free district")])
	if not heads.has("JAM"):
		ghosts.append(["JAM", TextDb.mark("JAM: no JAM card in hand")])
	if cfg.solace_tide_divert and not heads.has("DIVERT"):
		ghosts.append(["DIVERT", TextDb.mark("DIVERT: no SHIFT card in hand") if not has_shift else TextDb.mark("DIVERT: no beam to bend")])
	if not heads.has("SACRIFICE"):
		ghosts.append(["SACRIFICE", TextDb.mark("SACRIFICE: not available this raid")])
	# A card the player holds for the RESPONSE always gets a row or a reason: the rows that fold into HOLD say so.
	var shown := {}
	for g in groups:
		shown[String(g["members"][0]["head"])] = true
	var words := {"REDEPLOY": "MOVE", "DEPLOY": "DEPLOY", "DIVERT": "DIVERT", "JAM": "JAM", "JAM_B": "JAM sealed B"}
	var hs: Array = folded.keys()
	hs.sort()
	for h in hs:
		if not shown.has(h) and words.has(h):
			ghosts.append([h, tr("%s: same result as HOLD") % tr(String(words[h]))])


## The honest guard line of the plan (HOLD) and the best row: {hold, best: {resp, worst} | {}, uniform}. In PLAN it is
## computed over every response row of the current placement.
func guard() -> Dictionary:
	var key := str(raid.place)
	if key == _guard_key:
		return _guard
	var saved_groups := groups
	var saved_ghosts := ghosts
	_build_responses()
	var out := _guard_of_groups()
	out["uniform"] = _uniform()
	groups = saved_groups
	ghosts = saved_ghosts
	_guard_key = key
	_guard = out
	return out


func _guard_of_groups() -> Dictionary:
	var hold_w := SolaceTideRules.TIER_HOLDS
	var best: Dictionary = {}
	for g in groups:
		var m: Dictionary = g["members"][0]
		if m["head"] == HOLD:
			hold_w = m["worst"]
	for g in groups:
		if g["better"] and not bool(g["lethal_any"]):
			var m: Dictionary = g["members"][0]
			if best.is_empty() or TideGlyphs.rank(m["worst"]) < TideGlyphs.rank(best["worst"]) \
					or (TideGlyphs.rank(m["worst"]) == TideGlyphs.rank(best["worst"]) and float(m["mean"]) < float(best["mean"]) - MEAN_EPS):
				best = {"resp": m["resp"], "worst": m["worst"], "mean": m["mean"]}
	return {"hold": hold_w, "best": best}


## The group whose row HOLD loses HOME integrity to: some row saves a HOME pip HOLD loses on its worst outcome. -1 when none.
func hold_worse_group() -> int:
	var hold: Dictionary = {}
	for g in groups:
		if g["members"][0]["head"] == HOLD:
			hold = g["members"][0]
	if hold.is_empty() or int(hold["min_home"]) >= raid.st.home:
		return -1
	var best := -1
	for i in groups.size():
		var m: Dictionary = groups[i]["members"][0]
		if m["head"] == HOLD:
			continue
		if int(m["min_home"]) > int(hold["min_home"]):
			if best < 0 or int(m["min_home"]) > int(groups[best]["members"][0]["min_home"]):
				best = i
	return best


## Picks response group `gi` (and, with several variants, member `mi`); the board previews it. Returns the response array.
func select_group(gi: int, mi: int = 0) -> Array:
	if phase != Phase.RESPONSE or gi < 0 or gi >= groups.size():
		return []
	resp_sel = gi
	hold_armed = false
	lethal_armed = false
	var members: Array = groups[gi]["members"]
	return members[clampi(mi, 0, members.size() - 1)]["resp"]


## True when response `resp` ends the campaign on some outcome (read from the forecast, as the rows are).
func is_lethal(resp: Array) -> bool:
	return bool(resp_stats(resp)["lethal_any"])


## Commits the response: the raid plays (the checkpoint). A response that ends the campaign on some outcome needs a second press
## (returns "confirm"); so does HOLD when it loses HOME integrity a visible row saves. Returns "committed", "confirm" or "no".
func commit(resp: Array, force: bool = false) -> String:
	if phase != Phase.RESPONSE and not (phase == Phase.REVEAL and fast):
		return "no"
	if not force and is_lethal(resp) and not (lethal_armed and _lethal_key == str(resp)):
		lethal_armed = true
		_lethal_key = str(resp)
		hold_armed = false
		return "confirm"
	if String(resp[0]) == HOLD and not force and not fast and not hold_armed and hold_worse_group() >= 0:
		hold_armed = true
		return "confirm"
	hold_armed = false
	lethal_armed = false
	raids_before = campaign.pending_raids.size()
	_fresh_ready = false
	raid.set_response(resp)
	result = SolaceTideRules.play(raid.ctx, raid.st, raid.place, raid.resp, int(raid.ctx.draw["real_a"]), int(raid.ctx.draw["hunter_real"]))
	_beats = _make_beats(result)
	events = RunManager.fight_tide_raid(raid)
	last_raid = campaign.last_raid.duplicate(true)
	landed = 0
	phase = Phase.PLAYOUT
	return "committed"


## Fast resolve (LOCKED): HOLD, no RESPONSE panel.
func commit_fast() -> String:
	return commit([HOLD], true)


## The playout beats in firing order: {beam, label, line, trace (the entries of this beam), kind}.
func beats() -> Array:
	return _beats


func _make_beats(res: Dictionary) -> Array:
	var out: Array = []
	var sw: SolaceTideRules.Sweep = res["sweep"]
	var d: Dictionary = raid.ctx.draw
	var trace: Array = res["trace"]
	for i in sw.n_known:
		var ln: Dictionary = d["known"][i]
		if not sw.divert.is_empty() and int(sw.divert[0]) == i:
			ln = SolaceTideRules._line(ln["kind"], sw.divert[1], ln["type"], ln["home"])
		out.append({"beam": "known%d" % i, "kind": "known", "line": ln, "trace": _of(trace, "known%d" % i)})
	var a := int(d["real_a"])
	out.append({"beam": "sealed_a", "kind": "sealed_a", "line": d["cands"][a], "trace": _of(trace, "sealed_a")})
	var others := SolaceTideRules._others(raid.ctx, a)
	out.append({"beam": "sealed_b", "kind": "sealed_b", "line": d["cands"][others[sw.bpick]], "trace": _of(trace, "sealed_b"),
		"lean": res["lean"], "pick": res["b_pick"], "flipped": sw.jam_b})
	if raid.resp[0] != "JAM":
		out.append({"beam": "hunter", "kind": "hunter", "line": d["hunters"][int(d["hunter_real"])], "trace": _of(trace, "hunter")})
	else:
		out.append({"beam": "hunter", "kind": "hunter_jammed", "line": d["hunters"][int(d["hunter_real"])], "trace": []})
	return out


static func _of(trace: Array, beam: String) -> Array:
	var out: Array = []
	for e in trace:
		if e[0] == beam:
			out.append(e)
	return out


func playout_done() -> void:
	if phase == Phase.PLAYOUT:
		landed = -1
		phase = Phase.AFTERMATH


# ------------------------------------------------------------------------------------------------ AFTERMATH, HQ step
## The aftermath words: {tier, banner (CELL HOLDS / BREACHED / CITY LOST), lines}.
func aftermath() -> Dictionary:
	var lr := last_raid
	var tier_word := String(lr.get("tier", ""))
	var banner := "CELL HOLDS"
	if String(lr.get("lost", "")) == SolaceTideState.LOST_CITY or tier_word == "CITY LOST":
		banner = "CITY LOST"
	elif String(lr.get("lost", "")) == SolaceTideState.LOST_BREACHED or tier_word == SolaceTideRules.TIER_BREACHED:
		banner = "BREACHED"
	return {"tier": tier_word, "banner": banner, "home_before": int(lr.get("home_before", 0)), "home_after": int(lr.get("home_after", 0)),
		"down": lr.get("down", []), "taken": lr.get("taken", []), "infected": int(lr.get("infected", 0)),
		"heat_delta": int(lr.get("heat_delta", 0)), "schematics_delta": int(lr.get("schematics_delta", 0)), "lost": String(lr.get("lost", "")),
		"campaign_lost": bool(lr.get("campaign_lost", false)), "tally": infected_tally(), "raided": raid.resolved and not raid.over}


## The Sites DECAY took (DOWN to TAKEN), in id order, read from the events DECAY produced.
func decay_sites() -> Array[StringName]:
	var out: Array[StringName] = []
	for e in raid.open_events:
		if String(e.get("type", "")) == "taken":
			out.append(StringName(String(e["site"])))
	IdSort.sort_ids(out)
	return out


## Where the INFECTED count of this raid came from: {before (the count when the raid opened, before DECAY), decay (DECAY's tally or {}),
## mid (the count after DECAY, when the raid itself begins), raid (the raid's tally or {} when DECAY ended the campaign), after}. DECAY's
## changes end at `mid` and the raid's start there: the two never share a row.
func infected_tally() -> Dictionary:
	var after := int(last_raid.get("infected", hud_pre["infected"]))
	var out := {"before": int(decay_tally.get("before", hud_pre["infected"])), "decay": decay_tally, "mid": int(hud_pre["infected"]), "raid": {}, "after": after}
	if raid.resolved and not raid.over:
		out["raid"] = SolaceTideTally.raid_tally(int(hud_pre["infected"]), after, (last_raid.get("taken", []) as Array).size())
	return out


## The HQ step choices now (SolaceTideRules.between_options on the campaign's state).
func hq_options() -> Array:
	var st := SolaceTideCampaign.load_state(campaign, corp, cfg)
	return SolaceTideRules.between_options(st, cfg)


## The pieces of the HQ step the campaign offers: {downs, can_clean, can_cool, can_patch, cleared (Sites waiting to be installed),
## prices}.
func hq_menu() -> Dictionary:
	var st := SolaceTideCampaign.load_state(campaign, corp, cfg)
	var downs: Array = []
	for s in st.owned.keys():
		if int(st.owned[s]) == SolaceTideState.Cond.DOWN:
			downs.append(s)
	IdSort.sort_ids(downs)
	return {"downs": downs, "can_clean": st.wound_count() > 0, "can_cool": st.heat > 0, "can_patch": st.home < st.home_max,
		"cleared": st.pending.duplicate(), "schematics": st.schematics, "repair_cost": SolaceTideRules.repair_cost(cfg),
		"clean_price": cfg.solace_tide_clean_price, "cool_price": SolaceTideRules.cool_price(st, cfg),
		"patch": SolaceTideRules.patch_cost(st, cfg)}


## Every action the HQ step offers, whether it can be taken now or not, for the selection `sel` = [repair Site or &"", build "" / "CLEAN" /
## "COOL", patch bool]: [{kind ("patch" | "repair" | "clean" | "cool" | "install"), site, cost, points, enabled, why (a key, "" when enabled),
## why_args, picked}]. An action is disabled for a missing need (HOME full, nothing DOWN, no INFECTED card, Heat 0) or when it, added to the
## other picked actions, costs more Schematics than the Cell holds. The patch runs first and takes every HOME point the Schematics buy
## (CampaignRules.tide_hq_step), so its cost is the real one.
func hq_actions(sel: Array) -> Array:
	var st := SolaceTideCampaign.load_state(campaign, corp, cfg)
	var out: Array = []
	var have := st.schematics
	var patch := SolaceTideRules.patch_cost(st, cfg)
	var repair_c := SolaceTideRules.repair_cost(cfg)
	var clean_c := cfg.solace_tide_clean_price
	var cool_c := SolaceTideRules.cool_price(st, cfg)
	var picked_patch := bool(sel[2])
	var picked_repair := StringName(sel[0]) != &""
	var build := String(sel[1])
	var spend_patch := int(patch[1]) if picked_patch else 0
	var spend_repair := repair_c if picked_repair else 0
	var spend_build := (clean_c if build == SolaceTideRules.BUILD_CLEAN else (cool_c if build == SolaceTideRules.BUILD_COOL else 0))
	# PATCH HOME.
	var p := {"kind": "patch", "site": &"", "cost": int(patch[1]), "points": int(patch[0]), "picked": picked_patch, "enabled": true, "why": "", "why_args": []}
	if st.home >= st.home_max:
		_refuse(p, TextDb.mark("HOME is at full integrity."))
	elif int(patch[0]) <= 0:
		_refuse(p, TextDb.mark("Not enough Schematics to patch HOME."))
	elif not picked_patch and int(patch[1]) + spend_repair + spend_build > have:
		_refuse(p, TextDb.mark("Needs %d Schematics with the rest of your picks, %d held."), [int(patch[1]) + spend_repair + spend_build, have])
	out.append(p)
	# REPAIR, one row per DOWN district, or one disabled row when none is.
	var downs: Array = []
	for s in st.owned.keys():
		if int(st.owned[s]) == SolaceTideState.Cond.DOWN:
			downs.append(s)
	IdSort.sort_ids(downs)
	if downs.is_empty():
		var r := {"kind": "repair", "site": &"", "cost": repair_c, "points": 0, "picked": false, "enabled": true, "why": "", "why_args": []}
		_refuse(r, TextDb.mark("No district is DOWN."))
		out.append(r)
	for d in downs:
		var r := {"kind": "repair", "site": d, "cost": repair_c, "points": 0, "picked": StringName(sel[0]) == d, "enabled": true, "why": "", "why_args": []}
		if not r["picked"] and repair_c + spend_patch + spend_build > have:
			_refuse(r, TextDb.mark("Needs %d Schematics with the rest of your picks, %d held."), [repair_c + spend_patch + spend_build, have])
		out.append(r)
	# CLEAN and COOL (one build).
	var c := {"kind": "clean", "site": &"", "cost": clean_c, "points": 0, "picked": build == SolaceTideRules.BUILD_CLEAN, "enabled": true, "why": "", "why_args": []}
	if st.wound_count() <= 0:
		_refuse(c, TextDb.mark("No INFECTED card to clean."))
	elif not c["picked"] and clean_c + spend_patch + spend_repair > have:
		_refuse(c, TextDb.mark("Needs %d Schematics with the rest of your picks, %d held."), [clean_c + spend_patch + spend_repair, have])
	out.append(c)
	var k := {"kind": "cool", "site": &"", "cost": cool_c, "points": 0, "picked": build == SolaceTideRules.BUILD_COOL, "enabled": true, "why": "", "why_args": []}
	if st.heat <= 0:
		_refuse(k, TextDb.mark("Heat is already 0."))
	elif not k["picked"] and cool_c + spend_patch + spend_repair > have:
		_refuse(k, TextDb.mark("Needs %d Schematics with the rest of your picks, %d held."), [cool_c + spend_patch + spend_repair, have])
	out.append(k)
	# INSTALL: the cleared districts are installed at the HQ map, not by this step.
	var inst := {"kind": "install", "site": &"", "cost": cfg.node_base_cost, "points": st.pending.size(), "picked": false, "enabled": false, "why": "", "why_args": []}
	_refuse(inst, TextDb.mark("Installed at the HQ map after this step.") if st.pending.size() > 0 else TextDb.mark("No cleared district waits to be installed."))
	out.append(inst)
	return out


func _refuse(a: Dictionary, why: String, args: Array = []) -> void:
	a["enabled"] = false
	a["why"] = why
	a["why_args"] = args


## The Schematics the picks `sel` cost, in the order the step runs them.
func hq_total(sel: Array) -> int:
	var total := 0
	for a in hq_actions(sel):
		if bool(a["picked"]):
			total += int(a["cost"])
	return total


## Applies the HQ step `opt` =[repair Site or &"", build "" / "CLEAN" / "COOL", patch bool] (CampaignRules.tide_hq_step) and
## ends the raid. Returns the events.
func apply_hq_step(opt: Array) -> Array[Dictionary]:
	var ev := CampaignRules.tide_hq_step(campaign, cfg, RunManager.lookup(), opt)
	RunManager.autosave()
	phase = Phase.DONE
	return ev
