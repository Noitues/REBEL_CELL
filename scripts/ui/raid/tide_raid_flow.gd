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
## The RESPONSE rows (groups) of the current placement and the picked one.
var groups: Array = []
var ghosts: Array = []
var resp_sel: int = -1
## The raid played (SolaceTideRules.play result), the events RunManager returned and the campaign's `last_raid`.
var result: Dictionary = {}
var events: Array[Dictionary] = []
var last_raid: Dictionary = {}
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
	f.raid = SolaceTideRaid.open(p_campaign, p_corp, p_cfg, pending)
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
	return {"infected": wounds, "healthy": healthy, "doses": st.dose_cards().size(), "home": st.home, "home_max": st.home_max, "heat": st.heat,
		"band": SolaceTideRules.band(st.heat, cfg), "hand": SolaceTideRules.hand_size(st.heat, cfg), "beams": SolaceTideRules.known_count(st.heat, cfg),
		"ghost": st.ghost, "deck": st.deck.duplicate(true), "schematics": st.schematics}


## The HUD numbers now: before the raid until the aftermath, then what the campaign holds.
func hud() -> Dictionary:
	if phase >= Phase.AFTERMATH and phase != Phase.DONE and raid.resolved:
		return hud_of(SolaceTideCampaign.load_state(campaign, corp, cfg)) if not raid.over else hud_pre
	return hud_pre


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
	ks.sort()
	for k in ks:
		out.append(levels[k])
	return out


func site_name(id: StringName) -> String:
	if id == board().home or id == SolaceTideRules.HOME_WORD:
		return "HOME"
	var sd := corp.city_grid.get_site(id)
	return SiteText.tiered(sd, campaign.grid.home_site_id) if sd != null else String(id)


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
	groups = good + rest
	_build_ghosts(opts)


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
	var tiers := {}
	for g in groups:
		for m in g["members"]:
			var fc := SolaceTideRules.forecast(raid.ctx, raid.st, raid.place, m["resp"])
			for r in fc:
				tiers[r["tier"]] = true
	return tiers.size() <= 1


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
		if g["better"]:
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
	var members: Array = groups[gi]["members"]
	return members[clampi(mi, 0, members.size() - 1)]["resp"]


## Commits the response: the raid plays (the checkpoint). HOLD that loses HOME integrity a visible row saves needs a second
## press (returns "confirm"). Returns "committed", "confirm" or "no".
func commit(resp: Array, force: bool = false) -> String:
	if phase != Phase.RESPONSE and not (phase == Phase.REVEAL and fast):
		return "no"
	if String(resp[0]) == HOLD and not force and not fast and not hold_armed and hold_worse_group() >= 0:
		hold_armed = true
		return "confirm"
	hold_armed = false
	raid.set_response(resp)
	result = SolaceTideRules.play(raid.ctx, raid.st, raid.place, raid.resp, int(raid.ctx.draw["real_a"]), int(raid.ctx.draw["hunter_real"]))
	_beats = _make_beats(result)
	events = RunManager.fight_tide_raid(raid)
	last_raid = campaign.last_raid.duplicate(true)
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
		"campaign_lost": bool(lr.get("campaign_lost", false))}


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


## Applies the HQ step `opt` = [repair Site or &"", build "" / "CLEAN" / "COOL", patch bool] (CampaignRules.tide_hq_step) and
## ends the raid. Returns the events.
func apply_hq_step(opt: Array) -> Array[Dictionary]:
	var ev := CampaignRules.tide_hq_step(campaign, cfg, RunManager.lookup(), opt)
	RunManager.autosave()
	phase = Phase.DONE
	return ev
