extends SceneTree
const BalanceContent := preload("res://tools/balance/balance_content.gd")
## Measurement tool (docs/design/raid_concepts/RESPONSE_CENSUS.md): how often does the RESPONSE matter in the real game?
## Plays Solace campaigns with the builtin bot through the real core (SolaceTideRaid), and at every raid, after the placement
## and with the real sealed A known, takes a census of every response option against HOLD.
##   godot --headless --path . -s tools/raid_tide/response_census.gd -- --seeds 1000:1059 --policy auto|oracle [--out file]
## Placement policies: `auto` = SolaceTideCampaign.auto_plan (the tide_sim skilled player: least damage under HOLD);
## `oracle` = the placement with the best expected damage when the best response is picked per real A (the lab oracle's
## greedy_plan, in the game's damage weights). The response played, for both: the option with the least damage over the
## rows of the real A (ties keep the earlier option, HOLD first). One line per raid ("RAID {json}") and a summary of the run.
## Read-only on the rules: nothing under scripts/ changes. No RNG of its own (the campaign's streams do all the drawing).

const TIER_RANK := {"EVADED": 0, "HOLDS": 1, "BATTERED": 2, "DAMAGED": 3, "BREACHED": 4}

var _cfg: CampaignConfigData
var _policy: String = "auto"
var _records: Array = []


class CensusSim extends CampaignSimulator:
	var host: Object
	var policy: String = "auto"

	## The raid hook: the base class fights each pending raid through CampaignRules; here the tide raid is opened and played
	## by the census so every raid can be measured before it resolves.
	func _fight_raids(c: CampaignState, stats: Dictionary) -> void:
		var guard := 0
		while not c.pending_raids.is_empty() and not c.is_over() and guard < 10:
			guard += 1
			_deploy_armory(c)
			var pending: Dictionary = c.pending_raids[0]
			c.pending_raids.erase(pending)
			c.next_raid_mods = {}
			var raid := SolaceTideRaid.open(c, corp, config, pending)
			if not raid.over:
				host.call("census", raid, policy, c.campaign_seed)
				raid.resolve()
			if probe != null:
				probe.on_raid(c)
			stats["raids"] = int(stats["raids"]) + 1
			stats["heat_peak"] = maxi(int(stats["heat_peak"]), c.heat)


func _init() -> void:
	process_frame.connect(_run, CONNECT_ONE_SHOT)


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var seeds: Array = []
	var specs: Array = []
	var out_path := ""
	var i := 0
	while i < args.size():
		match String(args[i]):
			"--seeds":
				var p := String(args[i + 1]).split(":")
				for s in range(int(p[0]), int(p[1]) + 1):
					seeds.append(s)
				i += 2
			"--set":
				specs.append(String(args[i + 1]))
				i += 2
			"--policy":
				_policy = String(args[i + 1])
				i += 2
			"--out":
				out_path = String(args[i + 1])
				i += 2
			_:
				i += 1
	var content := BalanceContent.new(root.get_node(^"ContentRegistry"))
	var errors := content.apply_all(specs)
	if not errors.is_empty():
		printerr("response_census: ", errors)
	_cfg = content.config
	var resolver := CombatResolver.new(content.config, content.lookup)
	resolver.quiet = true
	for sd in seeds:
		var sim := CensusSim.new(resolver, &"solace", &"breaker")
		sim.host = self
		sim.policy = _policy
		var r: Dictionary = sim.run_campaign(sd, 0, 60)
		print("CAMP %d %s runs=%d raids=%d" % [sd, r["outcome"], r["runs"], r["raids"]])
	if out_path != "":
		var f := FileAccess.open(out_path, FileAccess.WRITE)
		for rec in _records:
			f.store_line(JSON.stringify(rec))
		f.close()
	quit(0)


# ------------------------------------------------------------------------------------------------ the census
func _damage_rows(raid: SolaceTideRaid, fc: Array, a: int = -1) -> int:
	var d := 0
	for r in fc:
		if a >= 0 and int(r["a"]) != a:
			continue
		d += SolaceTideCampaign.damage_of(raid.st, r["result"]["state"], _cfg)
	return d


func _opts_for(raid: SolaceTideRaid, place: Dictionary) -> Array:
	return SolaceTideRules.response_options(raid.ctx, SolaceTideRules.launch(raid.ctx, raid.st, place))


## Per option of `place`: its forecast. Returns {"opts", "fcs"}.
func _forecasts(raid: SolaceTideRaid, place: Dictionary) -> Dictionary:
	var opts := _opts_for(raid, place)
	var fcs: Array = []
	for o in opts:
		fcs.append(SolaceTideRules.forecast(raid.ctx, raid.st, place, o))
	return {"opts": opts, "fcs": fcs}


## The option index with the least damage over route `a`'s rows (strictly lower replaces; HOLD is index 0).
func _best_for_a(raid: SolaceTideRaid, fcs: Array, a: int) -> int:
	var best := 0
	var bv := _damage_rows(raid, fcs[0], a)
	for k in range(1, fcs.size()):
		var v := _damage_rows(raid, fcs[k], a)
		if v < bv:
			bv = v
			best = k
	return best


func _place_score_oracle(raid: SolaceTideRaid, place: Dictionary) -> int:
	var fx := _forecasts(raid, place)
	var n := (raid.ctx.draw["cands"] as Array).size()
	var tot := 0
	for a in n:
		var k := _best_for_a(raid, fx["fcs"], a)
		tot += _damage_rows(raid, fx["fcs"][k], a)
	return tot


## Real board, then the same raid on a counterfactual healthy board (every TAKEN district back to OK, lines and hand redrawn from the
## same raid stream), which is measured and never played.
func census(raid: SolaceTideRaid, policy: String, campaign_seed: int) -> void:
	_census_core(raid, policy, campaign_seed, "real", true)
	var st2 := raid.st.duplicate_state()
	var changed := false
	for s in st2.owned.keys():
		if int(st2.owned[s]) != SolaceTideState.Cond.OK:
			st2.owned[s] = SolaceTideState.Cond.OK
			changed = true
	if not changed:
		return
	var rng := SolaceTideCampaign.raid_streams(campaign_seed, raid.raid_idx)
	var draw := SolaceTideRules.draw_lines(raid.ctx.board, st2, _cfg, rng)
	var hand := SolaceTideRules.draw_hand(st2, _cfg, rng)
	var fake := SolaceTideRaid.new()
	fake.cfg = _cfg
	fake.raid_idx = raid.raid_idx
	fake.st = st2
	fake.ctx = SolaceTideRules.make_ctx(raid.ctx.board, st2, _cfg, draw, hand, raid.raid_idx)
	_census_core(fake, policy, campaign_seed, "healthy", false)


func _census_core(raid: SolaceTideRaid, policy: String, campaign_seed: int, mode: String, play: bool) -> void:
	# --- placement
	if policy == "oracle":
		var best_score := -1
		var best_place: Dictionary = {"sentries": {}, "ghost": &""}
		for p in raid.placements():
			var sc := _place_score_oracle(raid, p)
			if best_score < 0 or sc < best_score:
				best_score = sc
				best_place = p
		raid.place = best_place
	else:
		raid.plan_auto()
	var place := raid.place
	var ctx := raid.ctx
	var st := raid.st
	var fx := _forecasts(raid, place)
	var opts: Array = fx["opts"]
	var fcs: Array = fx["fcs"]
	var real_a := int(ctx.draw["real_a"])
	var real_h := int(ctx.draw["hunter_real"])
	# --- the played response: the best for the real A
	var pick := _best_for_a(raid, fcs, real_a)
	var hold_fc: Array = fcs[0]
	var hold_real := _row(hold_fc, real_a, real_h)
	var pick_real := _row(fcs[pick], real_a, real_h)
	var hold_tiers: Dictionary = {}
	var hold_tier_list: Array = []
	for r in hold_fc:
		hold_tiers[r["tier"]] = true
		hold_tier_list.append(String(r["tier"]))
	var hold_out := _sigs(raid, hold_fc, false)
	var hold_heat := _sigs(raid, hold_fc, true)
	var hold_ui := _ui_sigs(hold_fc)
	var hold_worst := _worst(hold_fc)
	var hold_best := _best(hold_fc)
	var hold_cells := _traced_cells(raid, hold_fc)
	var rec := {"mode": mode, "seed": campaign_seed, "raid": raid.raid_idx, "heat": st.heat, "n_opts": opts.size(), "locked": hold_tiers.size() == 1,
		"sac_ok": ctx.sac_ok, "ghost": String(place["ghost"]), "n_sent": (place["sentries"] as Dictionary).size(),
		"hand": ctx.hand.size(), "hold_tier": hold_real["tier"], "pick_tier": pick_real["tier"], "pick": opts[pick][0],
		"lab_decides": String(pick_real["tier"]) != String(hold_real["tier"]),
		"decides_state": _out_sig(raid, pick_real) != _out_sig(raid, hold_real)}
	# Hand composition for the response.
	var sw := SolaceTideRules.launch(ctx, st, place)
	var n_shift := 0
	var n_jam := 0
	for c in sw.rhand:
		if c[2] == SolaceTideState.VERB_SHIFT:
			n_shift += 1
		elif c[2] == SolaceTideState.VERB_JAM:
			n_jam += 1
	rec["rhand"] = sw.rhand.size()
	rec["rhand_shift"] = n_shift
	rec["rhand_jam"] = n_jam
	# Placed sentries, live relevant targets.
	var live_rel := 0
	for s in ctx.rel:
		if st.is_live(s):
			live_rel += 1
	rec["rel"] = live_rel
	# Per option.
	var heads_avail := {}
	var heads_diff := {}
	var heads_diff_tier := {}
	var heads_diff_ui := {}
	var heads_tie := {}
	var heads_better := {}
	var heads_worse := {}
	var inf_deltas: Array = []
	var n_diff := 0
	var n_diff_ui := 0
	var n_diff_tier := 0
	var n_diff_range := 0
	var n_better := 0
	var n_worse := 0
	var n_diff_heat_only := 0
	var fold_total := 0
	var fold_heat_differs := 0
	var fold_inf_differs := 0
	var fold_lethal_differs := 0
	var fold_out_differs := 0
	var fold_examples: Array = []
	var ties: Dictionary = {}
	var hold_damage := _damage_rows(raid, hold_fc)
	for k in range(1, opts.size()):
		var o: Array = opts[k]
		var head := String(o[0])
		var fc: Array = fcs[k]
		heads_avail[head] = int(heads_avail.get(head, 0)) + 1
		var sg := _sigs(raid, fc, false)
		var sh := _sigs(raid, fc, true)
		var d_out: bool = sg != hold_out
		var d_heat: bool = sh != hold_heat
		var d_ui: bool = _ui_sigs(fc) != hold_ui
		var d_tier := false
		for j in fc.size():
			if String(fc[j]["tier"]) != hold_tier_list[j]:
				d_tier = true
				break
		var d_range: bool = _worst(fc) != hold_worst or _best(fc) != hold_best
		var dmg := _damage_rows(raid, fc)
		var infd := 0.0
		for r in fc:
			infd += float((r["result"]["state"] as SolaceTideState).wound_count() - st.wound_count())
		infd /= float(fc.size())
		var hinf := 0.0
		for r in hold_fc:
			hinf += float((r["result"]["state"] as SolaceTideState).wound_count() - st.wound_count())
		hinf /= float(hold_fc.size())
		inf_deltas.append(infd - hinf)
		if d_out:
			n_diff += 1
			heads_diff[head] = int(heads_diff.get(head, 0)) + 1
			if dmg < hold_damage:
				n_better += 1
				heads_better[head] = int(heads_better.get(head, 0)) + 1
			elif dmg > hold_damage:
				n_worse += 1
				heads_worse[head] = int(heads_worse.get(head, 0)) + 1
		else:
			heads_tie[head] = int(heads_tie.get(head, 0)) + 1
			var why := _tie_reason(raid, o, fc, hold_fc, hold_cells)
			ties[why] = int(ties.get(why, 0)) + 1
			if d_heat:
				n_diff_heat_only += 1
		if d_ui:
			n_diff_ui += 1
			heads_diff_ui[head] = int(heads_diff_ui.get(head, 0)) + 1
		if d_tier:
			n_diff_tier += 1
			heads_diff_tier[head] = int(heads_diff_tier.get(head, 0)) + 1
		if d_range:
			n_diff_range += 1
		# The UI fold rule (tide_raid_flow._build_responses): a CARD response (not SACRIFICE) whose tier/HOME/owned signature
		# equals HOLD's on every row is folded into "N more choices change nothing".
		if SolaceTideRules.CARD_RESPONSES.has(head) and not d_ui:
			fold_total += 1
			var f_heat := _heat_delta_sets(raid, fc) != _heat_delta_sets(raid, hold_fc)
			var f_inf := _inf_delta_sets(raid, fc) != _inf_delta_sets(raid, hold_fc)
			var f_let := _lethal_sets(fc) != _lethal_sets(hold_fc)
			fold_heat_differs += 1 if f_heat else 0
			fold_inf_differs += 1 if f_inf else 0
			fold_lethal_differs += 1 if f_let else 0
			var f_any: bool = f_inf or f_let
			fold_out_differs += 1 if f_any else 0
			if f_any and fold_examples.size() < 3:
				fold_examples.append(JSON.stringify(o))
	rec["n_diff"] = n_diff
	rec["n_diff_ui"] = n_diff_ui
	rec["n_diff_tier"] = n_diff_tier
	rec["n_diff_range"] = n_diff_range
	rec["n_better"] = n_better
	rec["n_worse"] = n_worse
	rec["n_heat_only"] = n_diff_heat_only
	rec["inf_deltas"] = inf_deltas
	rec["avail"] = heads_avail
	rec["diff"] = heads_diff
	rec["diff_tier"] = heads_diff_tier
	rec["diff_ui"] = heads_diff_ui
	rec["tie"] = heads_tie
	rec["better"] = heads_better
	rec["worse"] = heads_worse
	rec["ties"] = ties
	rec["fold_total"] = fold_total
	rec["fold_heat_differs"] = fold_heat_differs
	rec["fold_inf_differs"] = fold_inf_differs
	rec["fold_lethal_differs"] = fold_lethal_differs
	rec["fold_out_differs"] = fold_out_differs
	rec["fold_examples"] = fold_examples
	rec["hold_mean_inf"] = _mean_inf(raid, hold_fc)
	# What the placement could do without any response: how many other placements change the HOLD tier (context).
	var home_rows := 0
	var home_known_rows := 0
	var touched_sites := {}
	for r in hold_fc:
		var hh := false
		var hk := false
		for t in r["result"]["trace"]:
			if String(t[1]) == "HOME" and String(t[2]) == "home":
				hh = true
				if String(t[0]).begins_with("known"):
					hk = true
		home_rows += 1 if hh else 0
		home_known_rows += 1 if hk else 0
	for c in hold_cells.keys():
		if c != "HOME":
			touched_sites[c] = true
	rec["home_rows"] = home_rows
	rec["home_known_rows"] = home_known_rows
	rec["n_known"] = sw.n_known
	rec["home_dmg"] = sw.home_dmg
	rec["touched_sites"] = touched_sites.size()
	var live_owned := 0
	for s in st.owned.keys():
		if st.is_live(s):
			live_owned += 1
	rec["live_owned"] = live_owned
	rec["n_places"] = raid.placements().size()
	_records.append(rec)
	print("RAID " + JSON.stringify(rec))
	# --- play it
	if play:
		raid.set_response(opts[pick])


func _row(fc: Array, a: int, h: int) -> Dictionary:
	for r in fc:
		if int(r["a"]) == a and int(r["hunter"]) == h:
			return r
	return fc[0]


func _mean_inf(raid: SolaceTideRaid, fc: Array) -> float:
	var s := 0.0
	for r in fc:
		s += float((r["result"]["state"] as SolaceTideState).wound_count() - raid.st.wound_count())
	return s / float(fc.size())


func _worst(fc: Array) -> String:
	var w := ""
	for r in fc:
		var t := String(r["tier"])
		if w == "" or int(TIER_RANK[t]) > int(TIER_RANK[w]):
			w = t
	return w


func _best(fc: Array) -> String:
	var b := ""
	for r in fc:
		var t := String(r["tier"])
		if b == "" or int(TIER_RANK[t]) < int(TIER_RANK[b]):
			b = t
	return b


func _owned_str(ns: SolaceTideState) -> String:
	var ks: Array = ns.owned.keys()
	IdSort.sort_ids(ks)
	var s := ""
	for k in ks:
		s += "%s=%d," % [k, int(ns.owned[k])]
	return s


## The tide screen's own signature (tide_raid_flow._signature): tier / HOME / owned.
func _ui_sigs(fc: Array) -> Array:
	var out: Array = []
	for r in fc:
		var ns: SolaceTideState = r["result"]["state"]
		out.append("%s/%d/%s" % [r["tier"], ns.home, _owned_str(ns)])
	return out


func _out_sig(raid: SolaceTideRaid, r: Dictionary) -> String:
	var ns: SolaceTideState = r["result"]["state"]
	return "%s/%d/%s/%d/%s" % [r["tier"], ns.home, _owned_str(ns), ns.wound_count() - raid.st.wound_count(), ns.lost]


## The full outcome signature per row: tier, HOME, owned, INFECTED added, lost; with the Heat when `with_heat`.
func _sigs(raid: SolaceTideRaid, fc: Array, with_heat: bool) -> Array:
	var out: Array = []
	for r in fc:
		var ns: SolaceTideState = r["result"]["state"]
		var s := _out_sig(raid, r)
		if with_heat:
			s += "/h%d" % (ns.heat - raid.st.heat)
		out.append(s)
	return out


func _heat_delta_sets(raid: SolaceTideRaid, fc: Array) -> Array:
	var out: Array = []
	for r in fc:
		out.append((r["result"]["state"] as SolaceTideState).heat - raid.st.heat)
	return out


func _inf_delta_sets(raid: SolaceTideRaid, fc: Array) -> Array:
	var out: Array = []
	for r in fc:
		out.append((r["result"]["state"] as SolaceTideState).wound_count() - raid.st.wound_count())
	return out


func _lethal_sets(fc: Array) -> Array:
	var out: Array = []
	for r in fc:
		out.append((r["result"]["state"] as SolaceTideState).lost)
	return out


## Every cell any trace entry of the rows names: {cell: {"kinds": {kind: true}, "types": {beam type: true}}}.
func _traced_cells(raid: SolaceTideRaid, fc: Array) -> Dictionary:
	var out := {}
	for r in fc:
		for t in r["result"]["trace"]:
			var cell := String(t[1])
			if not out.has(cell):
				out[cell] = {"kinds": {}, "types": {}}
			out[cell]["kinds"][String(t[2])] = true
			var ty := _beam_type(raid, String(t[0]), r)
			if ty != "":
				out[cell]["types"][ty] = true
	return out


func _beam_type(raid: SolaceTideRaid, beam: String, row: Dictionary) -> String:
	var d: Dictionary = raid.ctx.draw
	if beam.begins_with("known"):
		return String(d["known"][int(beam.substr(5))]["type"])
	if beam == "sealed_a":
		return String(d["cands"][int(row["a"])]["type"])
	if beam == "sealed_b":
		var others: Array = []
		for k in (d["cands"] as Array).size():
			if k != int(row["a"]):
				others.append(k)
		return String(d["cands"][others[int(row["result"]["b_pick"])]]["type"])
	if beam == "hunter":
		return String(d["hunters"][int(row["hunter"])]["type"])
	return ""


func _hunter_touches(fc: Array) -> bool:
	for r in fc:
		for t in r["result"]["trace"]:
			if String(t[0]) == "hunter":
				return true
	return false


func _lines_through(raid: SolaceTideRaid, site: StringName) -> Array:
	var types: Array = []
	for group in ["known", "cands", "hunters"]:
		for ln in raid.ctx.draw[group]:
			for c in ln["cells"]:
				if c == site:
					types.append(String(ln["type"]))
					break
	return types


## Why a response that gives HOLD's outcome on every row (tier, HOME, owned, INFECTED, lost) ties with it.
func _tie_reason(raid: SolaceTideRaid, o: Array, fc: Array, hold_fc: Array, hold_cells: Dictionary) -> String:
	var head := String(o[0])
	match head:
		"DEPLOY":
			var t := String(o[2])
			if not hold_cells.has(t):
				return "DEPLOY: the target district is on no beam that fires"
			var ty: Dictionary = hold_cells[t]["types"]
			if not ty.has(String(o[1])):
				return "DEPLOY: beams reach the target but none of the card's type (type mismatch)"
			if ty.size() > 1:
				return "DEPLOY: a beam of the card's type reaches the target but a beam of another type also hits it (one hit per district stands)"
			return "DEPLOY: only beams of the card's type reach the target, outcome still unchanged"
		"REDEPLOY":
			var t := String(o[2])
			var src := String(o[1])
			var src_used: bool = hold_cells.has(src) and (hold_cells[src]["kinds"] as Dictionary).has("block")
			var tgt_used := hold_cells.has(t)
			if not src_used and not tgt_used:
				return "MOVE: the sentry blocks nothing and the target is on no beam that fires"
			if not src_used:
				return "MOVE: the sentry blocks nothing; the target is touched but the outcome is unchanged"
			return "MOVE: the source blocks, the target adds nothing"
		"JAM":
			if not _hunter_touches(hold_fc):
				return "JAM: the hunter beam touches nothing"
			return "JAM: the hunter touches a district but the outcome is unchanged"
		"JAM_B":
			var same := true
			for j in range(0, fc.size()):
				if str(fc[j]["tier"]) != str(hold_fc[j]["tier"]):
					same = false
			return "JAM_B: both B candidates give the same outcome" if same else "JAM_B: other"
		"DIVERT":
			return "DIVERT: the bent beam lands on the same result"
		"SACRIFICE":
			return "SACRIFICE: other"
	return head + ": other"
