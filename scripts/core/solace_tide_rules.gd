class_name SolaceTideRules
extends RefCounted
## The Solace raid, the Infected Tide (H5): the pure rules of SOLACE_RAID_SPEC.md, ported from the oracle
## tools/raid_concepts/sweep_g1.py (variant H5). No Node, no global randomness: the draws take an RNG stream
## (the campaign's `raids` stream), every number comes from CampaignConfigData (`solace_tide_*` and the existing
## Heat, economy and Bloom keys). Static functions over a `SolaceTideBoard` (the graph) and a `SolaceTideState`.
##
## A raid, in order (SolaceTideRules.begin_raid ... finish_raid):
##   DECAY -> DRAW (lines) -> HAND -> PLAN (placements) -> launch (known beams shown) -> RESPONSE ->
##   known beams fire -> sealed A -> sealed B (the corp picks B by `b_rule`) -> hunter -> close -> HQ step.
## `play` resolves one outcome; `forecast` returns every outcome of a setup (A x B slot x hunter) and equals `play`
## row for row (preview == result).
##
## Data forms (plain, JSON-compatible; the golden uses the same):
##   line     {"kind": "ROUTE"|"STREET", "cells": Array[StringName] (scan order), "type": "D"|"N"|"E", "home": bool}
##   place    {"sentries": {site: card_id}, "ghost": &"" (none) | &"HOME"}
##   response ["HOLD"] | ["REDEPLOY", from, to] | ["DEPLOY", type, site] | ["SACRIFICE", site] | ["JAM"] | ["JAM_B"]
##            | ["DIVERT", known_index, cells]
##   trace    [[beam, site_or_"HOME", "block"|"hit"|"home"|"shield"], ...]

const TYPES: Array[String] = ["D", "N", "E"]
## The ghost value and the trace word for HOME.
const HOME_WORD: StringName = &"HOME"
const PLACEABLE: Array[String] = ["GUARD", "SHIFT", "JAM"]
## Responses that cost the card-response Heat.
const CARD_RESPONSES: Array[String] = ["REDEPLOY", "DEPLOY", "JAM", "JAM_B", "DIVERT"]
const BUILD_CLEAN := "CLEAN"
const BUILD_COOL := "COOL"

## Raid tier words, worst first (the spec's order of checks).
const TIER_BREACHED := "BREACHED"
const TIER_DAMAGED := "DAMAGED"
const TIER_EVADED := "EVADED"
const TIER_BATTERED := "BATTERED"
const TIER_HOLDS := "HOLDS"


## One raid's working board during a sweep.
class Sweep extends RefCounted:
	## site -> card id of the sentry standing there.
	var sent: Dictionary = {}
	var ghost: StringName = &""
	## site -> SolaceTideState.Cond, as the raid changes it.
	var owned: Dictionary = {}
	var home: int = 0
	var home_hit: bool = false
	var shield: bool = false
	## Sites already hit this raid.
	var seen: Dictionary = {}
	var touches: int = 0
	var taken: int = 0
	var jam_b: bool = false
	var bpick: int = -1
	var lean: int = -1
	var home_dmg: int = 0
	var trace: Array = []
	var beam: String = ""
	## Known beams that fire after the RESPONSE.
	var n_known: int = 0
	## [known index, cells] after a DIVERT, else empty.
	var divert: Array = []
	## The raid's Heat before close: the state's Heat plus the ghost's.
	var heat: int = 0
	## The response hand: [id, type, verb] of the hand cards not placed.
	var rhand: Array = []

	func duplicate_sweep() -> Sweep:
		var o := Sweep.new()
		o.sent = sent.duplicate()
		o.ghost = ghost
		o.owned = owned.duplicate()
		o.home = home
		o.home_hit = home_hit
		o.shield = shield
		o.seen = seen.duplicate()
		o.touches = touches
		o.taken = taken
		o.jam_b = jam_b
		o.bpick = bpick
		o.lean = lean
		o.home_dmg = home_dmg
		o.trace = trace.duplicate(true)
		o.beam = beam
		o.n_known = n_known
		o.divert = divert.duplicate(true)
		o.heat = heat
		o.rhand = rhand
		return o


## One raid's fixed inputs: the board, the config, the drawn lines, the hand and what follows from them.
class Ctx extends RefCounted:
	var board: SolaceTideBoard
	var cfg: CampaignConfigData
	var draw: Dictionary = {}
	## Hand card ids in drawn order.
	var hand: Array = []
	## card id -> [type, verb].
	var cards: Dictionary = {}
	## The live Sites on this raid's lines, sorted: the only Sites a sentry or SACRIFICE can matter on.
	var rel: Array[StringName] = []
	var sac_ok: bool = true
	## Per known beam, its DIVERT targets (empty when DIVERT is off).
	var nbrs: Array = []


# ------------------------------------------------------------------------------------------------ small rules
## The Heat band: COOL 0, NOTICED 1, FLAGGED 2, HUNTED 3, PURGE 4.
static func band(heat: int, cfg: CampaignConfigData) -> int:
	var n := 0
	for lv in cfg.heat_band_levels():
		if heat >= lv:
			n += 1
	return n


## Cards in the raid hand at `heat`.
static func hand_size(heat: int, cfg: CampaignConfigData) -> int:
	var n := cfg.solace_tide_hand_base
	for lv in cfg.solace_tide_hand_heat:
		if heat >= lv:
			n += 1
	return n


## Known beams that fire at `heat` (the raid's Heat with the ghost's).
static func known_count(heat: int, cfg: CampaignConfigData) -> int:
	var n := 1
	for lv in cfg.solace_tide_beam_heat:
		if heat >= lv:
			n += 1
	return n


## HOME integrity one hit removes. `purge` = the raid the first crossing of the PURGE level queued.
static func home_damage(heat: int, purge: bool, cfg: CampaignConfigData) -> int:
	var t := cfg.solace_tide_home_hit_damage_by_band
	if purge:
		return t[4]
	return t[mini(3, band(heat, cfg))]


## Adds `delta` Heat (clamped 0..heat_max). Returns true when a raid Heat level (25 / 50 / 75 / PURGE) is crossed for
## the first time; crossing the PURGE level also queues the PURGE raid.
static func add_heat(st: SolaceTideState, delta: int, cfg: CampaignConfigData) -> bool:
	st.heat = clampi(st.heat + delta, 0, cfg.heat_max)
	var levels := cfg.heat_band_levels()
	var fresh := false
	for i in levels.size():
		var lv: int = levels[i]
		if st.heat >= lv and not st.crossed_heat.has(lv):
			st.crossed_heat.append(lv)
			fresh = true
			if i == levels.size() - 1:
				st.purge_queued = true
	IdSort.sort_ids(st.crossed_heat)
	return fresh


## CITY LOST / BREACHED check (R-E): HOME at 0, or INFECTED cards outnumber healthy cards (DOSE counts as healthy).
static func check_loss(st: SolaceTideState) -> void:
	if st.lost != SolaceTideState.LOST_NONE:
		return
	if st.home <= 0:
		st.lost = SolaceTideState.LOST_BREACHED
		return
	var w := st.wound_count()
	if w > st.deck.size() - w:
		st.lost = SolaceTideState.LOST_CITY


## Adds one INFECTED card per site (id "w%03d"; `type` = the site). `loss` = they are lost Sites (they count toward
## the spread and set `last_lost` to the lowest site id); a HOME hit is not a loss.
static func add_infected(st: SolaceTideState, sites: Array, loss: bool = true) -> void:
	if sites.is_empty():
		return
	var lowest := String(sites[0])
	for s in sites:
		st.deck.append(["w%03d" % st.inf_n, String(s), SolaceTideState.VERB_WOUND])
		st.inf_n += 1
		if String(s) < lowest:
			lowest = String(s)
	st.sort_deck()
	st.infected_total += sites.size()
	if loss:
		st.lost_since_raid += sites.size()
		st.last_lost = StringName(lowest)


## A DOSE card arrives.
static func add_dose(st: SolaceTideState) -> void:
	st.deck.append(["x%d" % st.dose_n, "-", SolaceTideState.VERB_DOSE])
	st.dose_n += 1
	st.sort_deck()


## An Armory card drops (type D, N or E; verb GUARD).
static func add_asset(st: SolaceTideState, card_type: String) -> void:
	st.deck.append(["a%02d" % st.asset_n, card_type, SolaceTideState.VERB_GUARD])
	st.asset_n += 1
	st.sort_deck()


## What a Site is worth to the SACRIFICE choice: 0 when it is not live.
static func cell_value(board: SolaceTideBoard, cfg: CampaignConfigData, site: StringName, owned: Dictionary) -> int:
	if not owned.has(site) or int(owned[site]) == SolaceTideState.Cond.TAKEN:
		return 0
	return cfg.solace_tide_site_value(int(board.tier.get(site, 1)), bool(board.exploit.get(site, false)))


static func _live(owned: Dictionary, site: StringName) -> bool:
	return owned.has(site) and int(owned[site]) != SolaceTideState.Cond.TAKEN


# ------------------------------------------------------------------------------------------------ DECAY
## DECAY (every raid after the first, R-H): owned DOWN Sites go TAKEN, each adds an INFECTED card. Then the spread:
## `spread_min` or more Sites lost since the last raid. Doses (up to `doses_per_decay`) cancel the spread, else cure the
## highest-id INFECTED card. A spread still pending adds an INFECTED card tied to the last lost Site. Checks CITY LOST.
static func decay(st: SolaceTideState, cfg: CampaignConfigData) -> void:
	var downs: Array = []
	for s in st.owned.keys():
		if int(st.owned[s]) == SolaceTideState.Cond.DOWN:
			downs.append(s)
	IdSort.sort_ids(downs)
	for s in downs:
		st.owned[s] = SolaceTideState.Cond.TAKEN
	st.sites_lost += downs.size()
	add_infected(st, downs)
	var spread := st.lost_since_raid >= cfg.solace_tide_spread_min
	st.lost_since_raid = 0
	st.dose_spent = 0
	for _i in cfg.solace_tide_doses_per_decay:
		var dc := st.dose_cards()
		if dc.is_empty() or not (spread or st.wound_count() > 0):
			break
		st.remove_card(dc[0][0])
		st.dose_spent += 1
		if spread:
			spread = false
		else:
			var worst := ""
			for c in st.deck:
				if c[2] == SolaceTideState.VERB_WOUND and String(c[0]) > worst:
					worst = c[0]
			st.remove_card(worst)
	if spread:
		add_infected(st, [st.last_lost], false)
	check_loss(st)


# ------------------------------------------------------------------------------------------------ DRAW and HAND
static func _shuffle(arr: Array, rng: RandomNumberGenerator) -> void:
	for i in range(arr.size() - 1, 0, -1):
		var j := rng.randi_range(0, i)
		var t = arr[i]
		arr[i] = arr[j]
		arr[j] = t


static func _line(kind: String, cells: Array, line_type: String, home: bool) -> Dictionary:
	return {"kind": kind, "cells": cells, "type": line_type, "home": home}


## The raid's lines, from the `raids` stream (the order of draws is the spec's, section 4): candidate sort keys, the type
## permutation, real A, the drawn B, the known beams, the hunter type, its two streets and the real one. Returns
## {"known", "cands", "real_a", "real_b_drawn", "hunter_type", "hunters", "hunter_real", "n_paths"}. `st.raid_n` is
## this raid's index (the early-raid rule).
static func draw_lines(board: SolaceTideBoard, st: SolaceTideState, cfg: CampaignConfigData,
		rng: RandomNumberGenerator) -> Dictionary:
	var pool := board.route_pool
	var keys: Array = []
	for i in pool.size():
		var n := 0
		for s in pool[i]:
			if st.is_live(s):
				n += 1
		keys.append([i, -n, rng.randf()])
	keys.sort_custom(func(a: Array, b: Array) -> bool:
		if a[1] != b[1]:
			return a[1] < b[1]
		if a[2] != b[2]:
			return a[2] < b[2]
		return a[0] < b[0])
	var ncand := mini(mini(cfg.solace_tide_candidates, keys.size()), TYPES.size())
	var perm: Array = TYPES.duplicate()
	_shuffle(perm, rng)
	var cands: Array = []
	var cand_cells: Array = []
	for k in ncand:
		var cells: Array = pool[keys[k][0]]
		cand_cells.append(cells)
		cands.append(_line("ROUTE", cells.duplicate(), perm[k], true))
	var real := rng.randi_range(0, ncand - 1)
	var others: Array = []
	for k in ncand:
		if k != real:
			others.append(k)
	var real_b: int = others[rng.randi_range(0, others.size() - 1)]
	var spool := board.street_pool(cand_cells, st.owned)
	var known: Array = []
	for _i in 1 + cfg.solace_tide_beam_heat.size():
		var pct := cfg.solace_tide_early_route_pct if st.raid_n < cfg.solace_tide_early_raids else cfg.solace_tide_known_route_pct
		if rng.randf() * 100.0 < float(pct):
			var r: Array = pool[rng.randi_range(0, pool.size() - 1)]
			known.append(_line("ROUTE", r.duplicate(), TYPES[rng.randi_range(0, TYPES.size() - 1)], true))
		else:
			var c: Array = spool[rng.randi_range(0, spool.size() - 1)]
			known.append(_line("STREET", c.duplicate(), TYPES[rng.randi_range(0, TYPES.size() - 1)], false))
	var htype: String = TYPES[rng.randi_range(0, TYPES.size() - 1)]
	var hc: Array = []
	if spool.size() >= 2:
		var i1 := rng.randi_range(0, spool.size() - 1)
		var i2 := rng.randi_range(0, spool.size() - 2)
		if i2 >= i1:
			i2 += 1
		hc = [spool[i1], spool[i2]]
	else:
		hc = [spool[0], spool[0]]
	var hunters: Array = []
	for c in hc:
		hunters.append(_line("STREET", (c as Array).duplicate(), htype, false))
	var hreal := rng.randi_range(0, 1)
	return {"known": known, "cands": cands, "real_a": real, "real_b_drawn": real_b, "hunter_type": htype,
		"hunters": hunters, "hunter_real": hreal, "n_paths": pool.size()}


## The raid hand: the deck ids, sorted, shuffled from the same `raids` stream (after the lines), the first
## `hand_size(heat)`.
static func draw_hand(st: SolaceTideState, cfg: CampaignConfigData, rng: RandomNumberGenerator) -> Array:
	var ids: Array = []
	for c in st.deck:
		ids.append(String(c[0]))
	IdSort.sort_ids(ids)
	_shuffle(ids, rng)
	return ids.slice(0, mini(hand_size(st.heat, cfg), ids.size()))


## The other paths of a known beam's own pool that start or end at the same Site, in pool order: per known beam. A route
## bends within the route pool, a street within this raid's street pool.
static func divert_neighbors(board: SolaceTideBoard, draw: Dictionary, st: SolaceTideState) -> Array:
	var cand_cells: Array = []
	for ln in draw["cands"]:
		cand_cells.append(ln["cells"])
	var spool := board.street_pool(cand_cells, st.owned)
	var out: Array = []
	for ln in draw["known"]:
		var pool: Array = board.route_pool if ln["kind"] == "ROUTE" else spool
		var cells: Array = ln["cells"]
		var near: Array = []
		for p in pool:
			if not SolaceTideBoard._same(p, cells) and (p[0] == cells[0] or p[p.size() - 1] == cells[cells.size() - 1]):
				near.append(p)
		out.append(near)
	return out


## Builds a raid's context from its lines and hand. `raid_idx` is the raid's index (the SACRIFICE gap).
static func make_ctx(board: SolaceTideBoard, st: SolaceTideState, cfg: CampaignConfigData, draw: Dictionary,
		hand: Array, raid_idx: int) -> Ctx:
	var ctx := Ctx.new()
	ctx.board = board
	ctx.cfg = cfg
	ctx.draw = draw
	ctx.hand = hand
	ctx.sac_ok = raid_idx - st.last_sac >= cfg.solace_tide_sacrifice_gap
	for c in st.deck:
		ctx.cards[String(c[0])] = [String(c[1]), String(c[2])]
	var on_lines := {}
	var lines: Array = []
	lines.append_array(draw["known"])
	lines.append_array(draw["cands"])
	lines.append_array(draw["hunters"])
	for ln in lines:
		for s in ln["cells"]:
			on_lines[s] = true
	for s in board.sites:
		if on_lines.has(s) and st.is_live(s):
			ctx.rel.append(s)
	if cfg.solace_tide_divert:
		ctx.nbrs = divert_neighbors(board, draw, st)
	return ctx


## Starts raid `raid_idx`: resets the cadence count, runs DECAY (every raid after the first), then draws the lines and
## the hand from `rng` (the `raids` stream). Returns null when DECAY ended the campaign (CITY LOST).
static func begin_raid(board: SolaceTideBoard, st: SolaceTideState, cfg: CampaignConfigData,
		rng: RandomNumberGenerator, raid_idx: int) -> Ctx:
	st.netruns_since_raid = 0
	if raid_idx > 0:
		decay(st, cfg)
		if st.lost != SolaceTideState.LOST_NONE:
			return null
	st.raid_n = raid_idx
	var draw := draw_lines(board, st, cfg, rng)
	var hand := draw_hand(st, cfg, rng)
	return make_ctx(board, st, cfg, draw, hand, raid_idx)


# ------------------------------------------------------------------------------------------------ PLAN
## Every legal placement, in the oracle's order: at most `max_placed` hand cards (verb GUARD, SHIFT or JAM) on the raid's
## live Sites, one per Site, distinct by the (type, verb) signature per Site (a signature uses its lowest free id); then
## the same with the ghost on HOME while the kit has one. Returns Array of place dictionaries.
static func placements(ctx: Ctx, st: SolaceTideState) -> Array:
	var hids: Array = []
	for i in ctx.hand:
		if PLACEABLE.has(ctx.cards[i][1]):
			hids.append(i)
	var sigs: Array = []
	for i in hids:
		var sig: Array = ctx.cards[i]
		var known := false
		for s in sigs:
			if s[0] == sig[0] and s[1] == sig[1]:
				known = true
				break
		if not known:
			sigs.append(sig)
	var maps: Array = [{}]
	var cells := ctx.rel
	for a in cells.size():
		for s1 in sigs:
			var j1 := _pick(ctx, hids, s1, [])
			maps.append({cells[a]: j1})
			for b in range(a + 1, cells.size()):
				for s2 in sigs:
					var j2 := _pick(ctx, hids, s2, [j1])
					if j2 != "":
						maps.append({cells[a]: j1, cells[b]: j2})
	if ctx.cfg.solace_tide_max_placed < 2:
		var cut: Array = []
		for m in maps:
			if m.size() <= ctx.cfg.solace_tide_max_placed:
				cut.append(m)
		maps = cut
	var ghosts: Array[StringName] = [&""]
	if st.ghost > 0:
		ghosts.append(HOME_WORD)
	var out: Array = []
	for g in ghosts:
		for m in maps:
			out.append({"sentries": m, "ghost": g})
	return out


static func _pick(ctx: Ctx, hids: Array, sig: Array, used: Array) -> String:
	var best := ""
	for i in hids:
		if used.has(i):
			continue
		var c: Array = ctx.cards[i]
		if c[0] == sig[0] and c[1] == sig[1] and (best == "" or String(i) < best):
			best = i
	return best


# ------------------------------------------------------------------------------------------------ launch, RESPONSE
## Starts the sweep of a placement: the Heat with the ghost's, HOME's damage, the known beams that will fire, and the
## response hand. The known beams are shown here and fire after the RESPONSE (H5).
static func launch(ctx: Ctx, st: SolaceTideState, place: Dictionary) -> Sweep:
	var cfg := ctx.cfg
	var sw := Sweep.new()
	sw.ghost = place["ghost"]
	sw.heat = st.heat + (cfg.solace_tide_ghost_heat if sw.ghost != &"" else 0)
	sw.sent = (place["sentries"] as Dictionary).duplicate()
	sw.owned = st.owned.duplicate()
	sw.home = st.home
	sw.home_dmg = home_damage(st.heat, st.purge_queued, cfg)
	sw.n_known = known_count(sw.heat, cfg)
	var used := {}
	for j in sw.sent.values():
		used[j] = true
	for j in ctx.hand:
		if not used.has(j):
			sw.rhand.append([j, ctx.cards[j][0], ctx.cards[j][1]])
	return sw


static func _has_verb(rhand: Array, verb: String) -> bool:
	for c in rhand:
		if c[2] == verb:
			return true
	return false


## The lowest-id non-INFECTED response card of `card_type`, or "".
static func _deploy_card(rhand: Array, card_type: String) -> String:
	var best := ""
	for c in rhand:
		if c[1] == card_type and c[2] != SolaceTideState.VERB_WOUND and (best == "" or String(c[0]) < best):
			best = c[0]
	return best


## The RESPONSE options, in the spec's order: HOLD; REDEPLOY (a SHIFT card); DEPLOY (a card of a type); SACRIFICE;
## JAM and JAM_B (a JAM card); DIVERT (a SHIFT card, per fired known beam).
static func response_options(ctx: Ctx, sw: Sweep) -> Array:
	var board := ctx.board
	var out: Array = [["HOLD"]]
	var live_rel: Array[StringName] = []
	for s in ctx.rel:
		if _live(sw.owned, s):
			live_rel.append(s)
	var targets: Array[StringName] = []
	for s in live_rel:
		if not sw.sent.has(s):
			targets.append(s)
	if _has_verb(sw.rhand, SolaceTideState.VERB_SHIFT):
		for s in board.sites:
			if sw.sent.has(s):
				for t in targets:
					out.append(["REDEPLOY", s, t])
	for card_type in TYPES:
		if _deploy_card(sw.rhand, card_type) != "":
			for t in targets:
				out.append(["DEPLOY", card_type, t])
	if sw.ghost != HOME_WORD and not sw.home_hit and ctx.sac_ok:
		var sac: Array = live_rel.duplicate()
		var off: Array = []
		for s in board.sites:
			if not ctx.rel.has(s) and _live(sw.owned, s):
				off.append(s)
		if not off.is_empty():
			var cheapest: StringName = off[0]
			var cv := cell_value(board, ctx.cfg, cheapest, sw.owned)
			for s in off:
				var v := cell_value(board, ctx.cfg, s, sw.owned)
				if v < cv or (v == cv and String(s) < String(cheapest)):
					cheapest = s
					cv = v
			sac.append(cheapest)
		for s in sac:
			out.append(["SACRIFICE", s])
	if _has_verb(sw.rhand, SolaceTideState.VERB_JAM):
		out.append(["JAM"])
		out.append(["JAM_B"])
	if not ctx.nbrs.is_empty() and _has_verb(sw.rhand, SolaceTideState.VERB_SHIFT):
		for i in sw.n_known:
			for p in ctx.nbrs[i]:
				out.append(["DIVERT", i, p])
	return out


## Applies a response to the sweep (before any beam fires). It does not charge the Heat (`close` does).
static func respond(_ctx: Ctx, sw: Sweep, r: Array) -> void:
	match String(r[0]):
		"REDEPLOY":
			var card = sw.sent[r[1]]
			sw.sent.erase(r[1])
			sw.sent[r[2]] = card
		"DEPLOY":
			sw.sent[r[2]] = _deploy_card(sw.rhand, r[1])
		"SACRIFICE":
			if _live(sw.owned, r[1]):
				sw.owned[r[1]] = SolaceTideState.Cond.TAKEN
				sw.taken += 1
			sw.sent.erase(r[1])
			sw.shield = true
		"JAM_B":
			sw.jam_b = true
		"DIVERT":
			sw.divert = [int(r[1]), (r[2] as Array).duplicate()]


# ------------------------------------------------------------------------------------------------ the corp's B
## The live owned Sites on a route before its first sentry (the corp sees sentries, not their types).
static func route_pull(sw: Sweep, ln: Dictionary) -> int:
	var n := 0
	for cell in ln["cells"]:
		if cell == sw.ghost:
			continue
		if sw.sent.has(cell):
			break
		if _live(sw.owned, cell):
			n += 1
	return n


## The corp's B (an index into the two candidates other than A): the one with more unblocked owned Sites; a tie keeps
## `tie` (the lean shown at REVEAL A).
static func b_rule(ctx: Ctx, sw: Sweep, a: int, tie: int) -> int:
	var others := _others(ctx, a)
	var p0 := route_pull(sw, ctx.draw["cands"][others[0]])
	var p1 := route_pull(sw, ctx.draw["cands"][others[1]])
	if p0 > p1:
		return 0
	if p1 > p0:
		return 1
	return tie


static func _others(ctx: Ctx, a: int) -> Array:
	var out: Array = []
	for k in (ctx.draw["cands"] as Array).size():
		if k != a:
			out.append(k)
	return out


# ------------------------------------------------------------------------------------------------ SCAN, play
## SCAN one line: walk the cells in order (skipping the ghost's). A sentry of the line's type blocks and stops it; else
## the cell's live Site not yet hit is hit (OK -> DOWN, DOWN -> TAKEN, a TAKEN Site loses its sentry) and the beam goes
## on. A route that reaches HOME hits it once per raid (or the shield stops it) unless the ghost stands there.
static func scan(ctx: Ctx, sw: Sweep, ln: Dictionary) -> void:
	for cell in ln["cells"]:
		if cell == sw.ghost:
			continue
		if sw.sent.has(cell) and ctx.cards[sw.sent[cell]][0] == ln["type"]:
			sw.touches += 1
			sw.trace.append([sw.beam, String(cell), "block"])
			return
		if _live(sw.owned, cell) and not sw.seen.has(cell):
			if int(sw.owned[cell]) == SolaceTideState.Cond.OK:
				sw.owned[cell] = SolaceTideState.Cond.DOWN
			else:
				sw.owned[cell] = SolaceTideState.Cond.TAKEN
				sw.taken += 1
				sw.sent.erase(cell)
			sw.seen[cell] = true
			sw.touches += 1
			sw.trace.append([sw.beam, String(cell), "hit"])
	if ln["home"] and sw.ghost != HOME_WORD and not sw.home_hit:
		sw.touches += 1
		if sw.shield:
			sw.trace.append([sw.beam, "HOME", "shield"])
			return
		sw.home = maxi(0, sw.home - sw.home_dmg)
		sw.trace.append([sw.beam, "HOME", "home"])
		sw.home_hit = true


## The known beams fire after the RESPONSE; a DIVERT bends one onto its new cells.
static func fire_known(ctx: Ctx, sw: Sweep) -> void:
	for i in sw.n_known:
		var ln: Dictionary = ctx.draw["known"][i]
		if not sw.divert.is_empty() and sw.divert[0] == i:
			ln = _line(ln["kind"], sw.divert[1], ln["type"], ln["home"])
		sw.beam = "known%d" % i
		scan(ctx, sw, ln)


## The corp's pick of sealed B for A: the lean (on the board before the response, ties to 0), then the pick on the
## board after the response (ties keep the lean); JAM_B flips it.
static func pick_b(ctx: Ctx, pre: Sweep, post: Sweep, a: int) -> int:
	var lean := b_rule(ctx, pre, a, 0)
	post.lean = lean
	var bi := b_rule(ctx, post, a, lean)
	if post.jam_b:
		bi = 1 - bi
	post.bpick = bi
	return bi


## One full raid on one outcome: sealed A = candidate `a`, hunter street `h` (the real ones are in the draw). Returns
## {"state", "tier", "sweep", "trace", "lean", "b_pick", "home_dmg"}. The state is the end of the raid before
## `finish_raid`.
static func play(ctx: Ctx, st: SolaceTideState, place: Dictionary, resp: Array, a: int, h: int) -> Dictionary:
	var sw := launch(ctx, st, place)
	var pre := sw.duplicate_sweep()
	respond(ctx, sw, resp)
	var bi := pick_b(ctx, pre, sw, a)
	fire_known(ctx, sw)
	sw.beam = "sealed_a"
	scan(ctx, sw, ctx.draw["cands"][a])
	sw.beam = "sealed_b"
	scan(ctx, sw, ctx.draw["cands"][_others(ctx, a)[bi]])
	if resp[0] != "JAM":
		sw.beam = "hunter"
		scan(ctx, sw, ctx.draw["hunters"][h])
	var ns := close(ctx, st, place, sw, resp)
	return _result(ns, tier_of(st, ns, sw), sw)


static func _result(ns: SolaceTideState, tier_word: String, sw: Sweep) -> Dictionary:
	return {"state": ns, "tier": tier_word, "sweep": sw, "trace": sw.trace, "lean": sw.lean, "b_pick": sw.bpick,
		"home_dmg": sw.home_dmg}


## The preview of a setup: every outcome of the raid, 12 rows for A 0..2 x B slot 0..1 x hunter 0..1, each
## {"a", "b_slot", "hunter", "tier", "result"} where result is what `play` returns. Shares the work before the
## outcome splits (launch, response, known beams), so it is a separate path from `play` and must equal it (the B slot is
## the corp's pick, so both slots of a row are the same outcome).
static func forecast(ctx: Ctx, st: SolaceTideState, place: Dictionary, resp: Array) -> Array:
	var sw0 := launch(ctx, st, place)
	var sw1 := sw0.duplicate_sweep()
	respond(ctx, sw1, resp)
	var swk := sw1.duplicate_sweep()
	fire_known(ctx, swk)
	var rows: Array = []
	var n := (ctx.draw["cands"] as Array).size()
	var by_ah := {}
	for a in n:
		var post := sw1.duplicate_sweep()
		var bi := pick_b(ctx, sw0, post, a)
		var sw2 := swk.duplicate_sweep()
		sw2.lean = post.lean
		sw2.bpick = post.bpick
		sw2.beam = "sealed_a"
		scan(ctx, sw2, ctx.draw["cands"][a])
		sw2.beam = "sealed_b"
		scan(ctx, sw2, ctx.draw["cands"][_others(ctx, a)[bi]])
		for h in 2:
			var sw3 := sw2.duplicate_sweep()
			if resp[0] != "JAM":
				sw3.beam = "hunter"
				scan(ctx, sw3, ctx.draw["hunters"][h])
			var ns := close(ctx, st, place, sw3, resp)
			by_ah[a * 2 + h] = _result(ns, tier_of(st, ns, sw3), sw3)
	for a in n:
		for slot in 2:
			for h in 2:
				var res: Dictionary = by_ah[a * 2 + h]
				rows.append({"a": a, "b_slot": slot, "hunter": h, "tier": res["tier"], "result": res})
	return rows


# ------------------------------------------------------------------------------------------------ close, tiers
## Closes a raid: the new state. INFECTED cards for the Sites newly TAKEN (id order) and, after them, one tied to HOME
## for a HOME hit (H5); the Heat (ghost, card response, clean defense); the Schematics of a clean defense; the ghost
## used; CITY LOST / BREACHED. Does not reset `purge_queued` or set `last_sac` (`finish_raid`).
static func close(ctx: Ctx, st: SolaceTideState, place: Dictionary, sw: Sweep, resp: Array) -> SolaceTideState:
	var cfg := ctx.cfg
	var ns := st.duplicate_state()
	ns.owned = sw.owned.duplicate()
	ns.home = sw.home
	var heat := sw.heat
	var changed := false
	for s in sw.owned.keys():
		if int(sw.owned[s]) != int(st.owned.get(s, -1)):
			changed = true
			break
	if sw.home >= st.home and not changed:
		heat += cfg.clean_defense_heat
		ns.schematics += cfg.raid_schematics_by_tier[maxi(0, band(st.heat, cfg) - 1)]
	if CARD_RESPONSES.has(String(resp[0])):
		heat += cfg.solace_tide_card_response_heat
	ns.heat = clampi(heat, 0, cfg.heat_max)
	if place["ghost"] != &"":
		ns.ghost -= 1
	ns.sites_lost += sw.taken
	var fresh: Array = []
	for s in sw.owned.keys():
		if int(sw.owned[s]) == SolaceTideState.Cond.TAKEN and int(st.owned.get(s, -1)) != SolaceTideState.Cond.TAKEN:
			fresh.append(s)
	IdSort.sort_ids(fresh)
	add_infected(ns, fresh)
	if sw.home_hit and cfg.solace_tide_home_hit_infects:
		add_infected(ns, [HOME_WORD], false)
	check_loss(ns)
	return ns


## The raid tier: BREACHED (HOME 0), DAMAGED (HOME lower), EVADED (nothing touched, nothing taken), BATTERED (two or
## more Sites newly DOWN or one newly TAKEN), else HOLDS.
static func tier_of(before: SolaceTideState, after: SolaceTideState, sw: Sweep) -> String:
	if after.home <= 0:
		return TIER_BREACHED
	if after.home < before.home:
		return TIER_DAMAGED
	var new_down := 0
	var new_taken := 0
	for s in after.owned.keys():
		var was := int(before.owned.get(s, -1))
		var now := int(after.owned[s])
		if now == SolaceTideState.Cond.DOWN and was == SolaceTideState.Cond.OK:
			new_down += 1
		if now == SolaceTideState.Cond.TAKEN and was != SolaceTideState.Cond.TAKEN:
			new_taken += 1
	if sw.touches == 0 and new_taken == 0:
		return TIER_EVADED
	return TIER_BATTERED if new_down >= 2 or new_taken >= 1 else TIER_HOLDS


## After the raid is read: the PURGE raid has fired, and a SACRIFICE sets the gap counter.
static func finish_raid(ns: SolaceTideState, resp: Array, raid_idx: int) -> void:
	ns.purge_queued = false
	if resp[0] == "SACRIFICE":
		ns.last_sac = raid_idx


# ------------------------------------------------------------------------------------------------ the HQ step
## The Schematics to patch HOME: [points, cost] for every point the Schematics buy (1.0 each by default).
static func patch_cost(st: SolaceTideState, cfg: CampaignConfigData) -> Array:
	var missing := st.home_max - st.home
	var per := cfg.home_repair_cost_per_point
	var n := mini(missing, floori(float(st.schematics) / maxf(0.0001, per)))
	if n > 0:
		return [n, ceili(n * per)]
	return [0, 0]


## The Schematics to repair one DOWN Site.
static func repair_cost(cfg: CampaignConfigData) -> int:
	return int(cfg.node_base_cost * cfg.node_repair_ratio)


## The HQ Heat purchase's price: the base plus the increment for each one already made.
static func cool_price(st: SolaceTideState, cfg: CampaignConfigData) -> int:
	return cfg.heat_purchase_cost + cfg.heat_purchase_increment * st.cools


## The HQ step options after a raid, in order: [repair (a DOWN Site id or &""), build ("", "CLEAN", "COOL"), patch].
static func between_options(st: SolaceTideState, cfg: CampaignConfigData) -> Array:
	var downs: Array = []
	for s in st.owned.keys():
		if int(st.owned[s]) == SolaceTideState.Cond.DOWN:
			downs.append(s)
	IdSort.sort_ids(downs)
	var builds: Array = [""]
	if st.wound_count() > 0:
		builds.append(BUILD_CLEAN)
	if st.heat > 0:
		builds.append(BUILD_COOL)
	var patches: Array = [false]
	if st.home < st.home_max:
		patches.append(true)
	var repairs: Array = [&""]
	repairs.append_array(downs)
	var out: Array = []
	for r in repairs:
		var rc := repair_cost(cfg) if r != &"" else 0
		for b in builds:
			var bc := 0
			if b == BUILD_CLEAN:
				bc = cfg.solace_tide_clean_price
			elif b == BUILD_COOL:
				bc = cool_price(st, cfg)
			for pt in patches:
				if rc + bc + (1 if pt else 0) <= st.schematics:
					out.append([r, b, pt])
	return out


## The HQ step, in order: PATCH (every HOME point the Schematics buy), REPAIR one DOWN Site, CLEAN or COOL, then install
## the CLEARED Sites while node_base_cost is affordable. Returns the new state.
static func between(st: SolaceTideState, opt: Array, cfg: CampaignConfigData) -> SolaceTideState:
	var ns := st.duplicate_state()
	var rep: StringName = opt[0]
	var build: String = opt[1]
	if opt[2]:
		var pc := patch_cost(ns, cfg)
		if pc[0] > 0:
			ns.schematics -= pc[1]
			ns.home += pc[0]
	if rep != &"" and ns.owned.get(rep, -1) == SolaceTideState.Cond.DOWN and ns.schematics >= repair_cost(cfg):
		ns.schematics -= repair_cost(cfg)
		ns.owned[rep] = SolaceTideState.Cond.OK
	if build == BUILD_COOL and ns.schematics >= cool_price(ns, cfg):
		ns.schematics -= cool_price(ns, cfg)
		ns.cools += 1
		add_heat(ns, -cfg.heat_purchase_amount, cfg)
	if build == BUILD_CLEAN and ns.schematics >= cfg.solace_tide_clean_price and ns.wound_count() > 0:
		ns.schematics -= cfg.solace_tide_clean_price
		var worst := ""
		for c in ns.deck:
			if c[2] == SolaceTideState.VERB_WOUND and String(c[0]) > worst:
				worst = c[0]
		ns.remove_card(worst)
	install_pending(ns, cfg)
	return ns


## CLEARED Sites wait for Schematics: in id order, each is installed (node_base_cost) while the Schematics allow.
static func install_pending(st: SolaceTideState, cfg: CampaignConfigData) -> void:
	var left: Array[StringName] = []
	for s in st.pending:
		if st.schematics >= cfg.node_base_cost and st.owned.get(s, -1) != SolaceTideState.Cond.OK:
			st.schematics -= cfg.node_base_cost
			st.owned[s] = SolaceTideState.Cond.OK
		else:
			left.append(s)
	st.pending = left


# ------------------------------------------------------------------------------------------------ netrun effects
## A completed netrun on `site` (&"" = a patrol run): rack Heat and Schematics of its tier (plus the elites' Heat and the
## unspent Cycles the caller passes), the Exploit (Heat again when it is re-taken), the objective's Heat change, and the
## Site becomes CLEARED (pending). Returns true when a raid Heat level was crossed.
static func netrun_complete(st: SolaceTideState, board: SolaceTideBoard, cfg: CampaignConfigData, site: StringName,
		extra_heat: int, extra_schematics: int) -> bool:
	var t := 1 if site == &"" else int(board.tier[site])
	var d := cfg.rack_heat_by_tier[t - 1] + extra_heat
	st.schematics += cfg.rack_schematics_by_tier[t - 1] + extra_schematics
	if site != &"":
		if board.exploit.get(site, false) and not st.held.has(site):
			st.held.append(site)
			IdSort.sort_ids(st.held)
			d += cfg.exploit_heat
		if board.objective_heat.has(site) and not st.obj_done.has(site):
			st.obj_done.append(site)
			IdSort.sort_ids(st.obj_done)
			d += int(board.objective_heat[site])
		if not st.is_live(site) and not st.pending.has(site):
			st.pending.append(site)
			IdSort.sort_ids(st.pending)
	return add_heat(st, d, cfg)


## A netrun death at `tier`: no Site is cleared, death Heat (base + tier). Returns true when a raid Heat level crossed.
static func netrun_death(st: SolaceTideState, cfg: CampaignConfigData, tier: int) -> bool:
	st.deaths += 1
	return add_heat(st, cfg.death_heat_base + tier, cfg)


## The close of every netrun, deaths included (netrun number `n`, from 1): a DOSE card every `dose_every`, then the
## CITY LOST check.
static func end_netrun(st: SolaceTideState, cfg: CampaignConfigData, n: int) -> void:
	if n % cfg.solace_tide_dose_every == 0:
		add_dose(st)
	check_loss(st)


## Counts a netrun toward the raid cadence. True when a raid fires after it: `crossed` (the netrun crossed a raid Heat
## level for the first time) or `raid_every` netruns since the last raid. `begin_raid` resets the count.
static func note_netrun(st: SolaceTideState, cfg: CampaignConfigData, crossed: bool) -> bool:
	st.netruns_since_raid += 1
	return crossed or st.netruns_since_raid >= cfg.solace_tide_raid_every


## The Genome Core breach failed (netrun number `n`): the breach operative dies (death Heat at tier 4); after more than
## `breach_retries` failures the held Exploits are spent (the corp patches them). Returns true when a Heat level crossed.
static func breach_failed(st: SolaceTideState, cfg: CampaignConfigData, n: int) -> bool:
	st.deaths += 1
	var crossed := add_heat(st, cfg.death_heat_base + 4, cfg)
	st.breach_fails += 1
	if st.breach_fails > cfg.solace_tide_breach_retries:
		st.held = []
		st.breach_fails = 0
	if n % cfg.solace_tide_dose_every == 0:
		add_dose(st)
	return crossed


## The Exploit Sites whose Exploit can be re-taken: still the Cell's and live, Exploit not held. Sorted.
static func retake_sites(st: SolaceTideState, board: SolaceTideBoard) -> Array[StringName]:
	var out: Array[StringName] = []
	for s in board.sites:
		if board.exploit.get(s, false) and st.is_live(s) and not st.held.has(s):
			out.append(s)
	return out


## R-D: the Bloom start front gap (milli) with `infected` INFECTED cards: `start_gap` less each card's share of an
## `entry_pace` step (solace_tide_infected_front_step_pct). Zero or less = CAUGHT at the first entry.
@warning_ignore("integer_division")
static func bloom_start_gap(start_gap: int, entry_pace: int, infected: int, cfg: CampaignConfigData) -> int:
	return start_gap - infected * entry_pace * cfg.solace_tide_infected_front_step_pct / 100


# ------------------------------------------------------------------------------------------------ JSON forms
## A line from its JSON form (cells to StringName).
static func line_from_json(d: Dictionary) -> Dictionary:
	var cells: Array = []
	for c in d["cells"]:
		cells.append(StringName(String(c)))
	return _line(String(d["kind"]), cells, String(d["type"]), bool(d["home"]))


## A draw from the golden's `draw` form.
static func draw_from_json(d: Dictionary) -> Dictionary:
	var out := {"known": [], "cands": [], "hunters": [], "real_a": int(d["real_a"]),
		"real_b_drawn": int(d["real_b_drawn"]), "hunter_type": String(d["hunter_type"]),
		"hunter_real": int(d["hunter_real"]), "n_paths": int(d["n_paths"])}
	for k in ["known", "cands", "hunters"]:
		for ln in d[k]:
			out[k].append(line_from_json(ln))
	return out


## A place from the golden's form {"sentries": [[site, card]] | {site: card}, "ghost": null | "HOME"}.
static func place_from_json(d: Dictionary) -> Dictionary:
	var m := {}
	var raw: Variant = d["sentries"]
	if raw is Array:
		for pair in raw:
			m[StringName(String(pair[0]))] = String(pair[1])
	else:
		for k in (raw as Dictionary).keys():
			m[StringName(String(k))] = String((raw as Dictionary)[k])
	var g: Variant = d.get("ghost")
	return {"sentries": m, "ghost": &"" if g == null else StringName(String(g))}


## A response from its JSON form (site ids to StringName).
static func response_from_json(r: Array) -> Array:
	match String(r[0]):
		"REDEPLOY":
			return ["REDEPLOY", StringName(String(r[1])), StringName(String(r[2]))]
		"DEPLOY":
			return ["DEPLOY", String(r[1]), StringName(String(r[2]))]
		"SACRIFICE":
			return ["SACRIFICE", StringName(String(r[1]))]
		"DIVERT":
			var cells: Array = []
			for c in r[2]:
				cells.append(StringName(String(c)))
			return ["DIVERT", int(r[1]), cells]
	return [String(r[0])]
