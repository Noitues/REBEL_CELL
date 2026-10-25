class_name H7Campaign
extends RefCounted
## Leg rules of the H7 Bastion: rosters (foothold entry, corp adaptation), raid resolution and settlement.
## Port of tools/raid_concepts/h7_campaign.py (roster_for, raid_result, settle).


## The piece type with the most coin invested (ties by id), or "" for an empty fortress.
static func invested(fort: Dictionary) -> String:
	var tot := {}
	for node in fort:
		for p in fort[node]:
			tot[p] = tot.get(p, 0) + H7Data.COST[p]
	var best := ""
	for p in tot:
		if best == "" or tot[p] > tot[best] or (tot[p] == tot[best] and p < best):
			best = p
	return best


## The raid as telegraphed: Array of [id, entry, traits], corp roster first, survivors after.
static func roster_for(leg: Array, i: int, st: H7State) -> Array:
	var base: Array = []
	for t in leg[i]:
		base.append([t[0], t[1]])
	if not st.lost.is_empty():
		var first := 0
		for j in range(base.size()):
			if base[j][0] < base[first][0]:
				first = j
		var sl: Array = st.lost.duplicate()
		sl.sort()
		base[first][1] = sl[0]
	var top := invested(st.fort)
	var counter: String = H7Data.COUNTER[top] if top != "" else ""
	var tough := 0
	for j in range(base.size()):
		var hj: int = H7Data.THREAT_DEF[base[j][0]][0]
		var ht: int = H7Data.THREAT_DEF[base[tough][0]][0]
		if hj > ht or (hj == ht and base[j][0] < base[tough][0]):
			tough = j
	var out: Array = []
	for j in range(base.size()):
		var traits: Array = [counter] if (counter != "" and j == tough) else []
		out.append([base[j][0], base[j][1], traits])
	for s in st.surv:
		out.append([s[0], s[1], []])
	return out


## Resolves a raid for the state plus this visit's buys. Returns {"fort", "r"}.
static func raid_result(st: H7State, buy: Array, place: Array, crew: String, roster: Array) -> Dictionary:
	var fort: Dictionary = st.fort.duplicate(true)
	for k in range(buy.size()):
		if not fort.has(place[k]):
			fort[place[k]] = []
		fort[place[k]].append(buy[k])
	var c := "" if st.lost.has("SAFE") else crew
	var r := H7Sim.new().run(fort, c, roster, st.lost)
	return {"fort": fort, "r": r}


## Payout, repair bill, lost nodes, survivors and income. raid index i of n_raids.
static func settle(st: H7State, fort: Dictionary, r: H7Result, roster: Array, i: int, buy: Array, n_raids: int) -> H7Settle:
	var out := H7Settle.new()
	var kills: Array = r.kill_ids()
	out.kills = kills.size()
	out.pay = H7Data.SALVAGE * kills.size() + (H7Data.BONUS if r.clean else 0)
	var bill: int = r.home_before - r.home_after
	for k in r.nodes:
		if k == "HOME" or st.lost.has(k):
			continue
		var v: Dictionary = r.nodes[k]
		if v["outcome"] == "scuffed" and not r.clean:
			bill += v["before"] - v["after"]
		elif v["outcome"] == "down":
			bill += H7Data.INSTALL[k] >> 1
	out.bill = bill
	out.net = out.pay - bill
	for b in buy:
		out.spend += H7Data.COST[b]
	var bank: int = st.bank - out.spend + out.pay - bill
	var ns := H7State.new()
	if r.breached:
		ns.bank = H7Data.BREACH_SCORE
		ns.lost = st.lost.duplicate()
		out.state = ns
		return out
	var lost: Array = st.lost.duplicate()
	for k in r.nodes:
		if r.nodes[k]["outcome"] == "taken" and k != "HOME" and not lost.has(k):
			lost.append(k)
	var nf: Dictionary = fort.duplicate(true)
	for k in lost:
		nf.erase(k)
	var surv: Array = []
	for tid in r.routes:
		if not kills.has(tid):
			var base: String = tid.split("#")[0]
			var entry := "C1"
			for t in roster:
				if t[0] == tid:
					entry = t[1]
					break
			surv.append(["%s#%d" % [base, i + 2], entry])
	lost.sort()
	ns.fort = nf
	ns.lost = lost
	ns.surv = surv
	if i < n_raids - 1:
		var inc: int = H7Data.BASE_INCOME
		if not lost.has("VAULT"):
			inc += H7Data.VAULT_INC
		if not lost.has("RELAY"):
			inc += H7Data.RELAY_INC
		out.income = inc
		bank += inc
	ns.bank = bank
	out.state = ns
	return out


## Forecast with this fortress and no further buys: this raid plus up to n_ahead - 1 telegraphed raids.
## Each entry: {roster, r, settle, fort, before (H7State)}. Crew stays where it is while its node holds.
static func forecast(leg: Array, i: int, st: H7State, buy: Array, place: Array, crew: String, n_ahead: int) -> Array:
	var rows: Array = []
	var cur := st
	var b := buy
	var p := place
	var cr := crew
	for j in range(i, mini(i + n_ahead, leg.size())):
		var roster := roster_for(leg, j, cur)
		var rr := raid_result(cur, b, p, cr, roster)
		var s := settle(cur, rr["fort"], rr["r"], roster, j, b, leg.size())
		rows.append({"roster": roster, "r": rr["r"], "settle": s, "fort": rr["fort"], "before": cur})
		if rr["r"].breached:
			break
		cur = s.state
		b = []
		p = []
		if cr != "" and cur.lost.has(cr):
			cr = "" if cur.lost.has("SAFE") else "SAFE"
	return rows
