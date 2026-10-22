class_name H7Sim
extends RefCounted
## Raid resolver for the H7 rule set. Port of tools/raid_concepts/sim.py run() with the toggles
## fixed_routes, avoid_home, tiebreak weakest, ice_blocks, no_cascade, crew_flat, traits and the
## Lockdown link freeze. Deterministic, no randomness, no nodes.

var _hp: Dictionary = {}
var _cond: Dictionary = {}
var _threats: Dictionary = {}
var _ids: Array = []
var _assets: Dictionary = {}
var _frozen: Array = []


func _is_frozen(a: String, b: String) -> bool:
	for f in _frozen:
		if (f[0] == a and f[1] == b) or (f[0] == b and f[1] == a):
			return true
	return false


func _bfs(src: String, blocked: Array = []) -> Dictionary:
	var dist := {src: 0}
	var q: Array = [src]
	while not q.is_empty():
		var n: String = q.pop_front()
		for m in H7Data.adj(n):
			if _is_frozen(n, m):
				continue
			if not dist.has(m) and not blocked.has(m):
				dist[m] = dist[n] + 1
				q.append(m)
	return dist


func _next_hop(cur: String, target: String) -> String:
	var blocked: Array = ["HOME"] if (target != "HOME" and cur != "HOME") else []
	var dt := _bfs(target, blocked)
	if not dt.has(cur):
		dt = _bfs(target)
	var cands: Array = []
	for m in H7Data.adj(cur):
		if dt.has(m) and dt[m] == dt[cur] - 1:
			cands.append(m)
	if cands.is_empty():
		return cur
	cands.sort_custom(func(a: String, b: String) -> bool:
		var ha: int = _hp.get(a, 999)
		var hb: int = _hp.get(b, 999)
		return ha < hb if ha != hb else a < b)
	return cands[0]


func _live(n: String) -> bool:
	return _hp.has(n) and _cond[n] == "ok" and n != "HOME"


func _active() -> Array:
	var out: Array = []
	for id in _ids:
		var t: Dictionary = _threats[id]
		if t["hp"] > 0 and not t["home"]:
			out.append(t)
	return out


func _live_nodes() -> Array:
	var out: Array = []
	for n in _hp:
		if _live(n):
			out.append(n)
	return out


func _pick(t: Dictionary) -> String:
	var decoys: Array = []
	if not t["traits"].has("BLIND"):
		for n in _assets:
			if _assets[n].has("DECOY") and _live(n):
				decoys.append(n)
	if not decoys.is_empty():
		decoys.sort()
		return decoys[0]
	var live := _live_nodes()
	if live.is_empty():
		return "HOME"
	if t["route"] == "value":
		live.sort_custom(func(a: String, b: String) -> bool:
			var ka: int = -H7Data.PRIORITY[a] * 1000 - H7Data.INSTALL[a]
			var kb: int = -H7Data.PRIORITY[b] * 1000 - H7Data.INSTALL[b]
			return ka < kb if ka != kb else a < b)
		return live[0]
	if t["route"] == "weakest":
		live.sort_custom(func(a: String, b: String) -> bool:
			return _hp[a] < _hp[b] if _hp[a] != _hp[b] else a < b)
		return live[0]
	return "HOME"


## Resolves one raid. assets: node -> Array of piece ids; crew: node id or "" for none;
## threats: Array of [id, entry, traits]; start_taken: nodes already TAKEN.
func run(assets: Dictionary, crew: String, threats: Array, start_taken: Array) -> H7Result:
	_assets = assets
	_hp = H7Data.NODE_HP.duplicate()
	_cond = {}
	for k in _hp:
		_cond[k] = "taken" if start_taken.has(k) else "ok"
	_threats = {}
	_ids = []
	for item in threats:
		var tid: String = item[0]
		var entry: String = item[1]
		var traits: Array = item[2] if item.size() > 2 else []
		var base: String = tid.split("#")[0]
		var d: Array = H7Data.THREAT_DEF[base]
		var site: String = entry if entry != "" else d[4]
		_threats[tid] = {"id": tid, "base": base, "hp": d[0], "dmg": d[1], "spd": d[2], "route": d[3],
			"site": site, "hold": 0, "home": false, "left": false, "path": [site], "traits": traits.duplicate(),
			"locked": "", "route_fixed": []}
		# Mirrors the python dict: a repeated id (two survivors of the same type) replaces the first entry
		# but keeps its place, so only one fights.
		if not _ids.has(tid):
			_ids.append(tid)
	var order: Array = _ids.duplicate()
	_ids.sort()
	var held_by := {}
	for id in _ids:
		held_by[id] = []
	_frozen = []
	var has_lockdown := false
	for id in _ids:
		if _threats[id]["base"] == "LOCKDOWN":
			has_lockdown = true
	if has_lockdown:
		var nb: Array = H7Data.adj("HOME").duplicate()
		nb.sort_custom(func(a: String, b: String) -> bool:
			var ca: int = _assets[a].size() if _assets.has(a) else 0
			var cb: int = _assets[b].size() if _assets.has(b) else 0
			return ca > cb if ca != cb else a < b)
		var pair: Array = ["HOME", nb[0]]
		pair.sort()
		_frozen.append(pair)
	var res := H7Result.new()
	var down_now: Array = []
	var taken_now: Array = []
	var step := 0
	while step < H7Data.STEP_CAP:
		step += 1
		var ev := {"step": step, "moves": [], "holds": [], "shots": [], "hits": [], "down": [], "taken": [],
			"kills": [], "targets": {}}
		if _active().is_empty():
			step -= 1
			break
		if step == 1:
			for t in _active():
				var tgt := _pick(t)
				t["locked"] = tgt
				var route: Array = [t["site"]]
				while route[-1] != tgt:
					var nx := _next_hop(route[-1], tgt)
					if nx == route[-1]:
						break
					route.append(nx)
				t["route_fixed"] = route
		for t in _active():
			var tgt2: String = t["locked"]
			ev["targets"][t["id"]] = tgt2
			if tgt2 != "HOME" and _cond.get(tgt2, "") == "taken":
				t["home"] = true
				t["left"] = true
				continue
			if t["hold"] > 0:
				t["hold"] -= 1
				ev["holds"].append([t["id"], t["site"], t["hold"]])
				continue
			var rf: Array = t["route_fixed"]
			var i: int = rf.find(t["site"]) if rf.has(t["site"]) else rf.size() - 1
			var frm: String = t["site"]
			var moved := 0
			while moved < t["spd"] and i < rf.size() - 1:
				i += 1
				t["site"] = rf[i]
				t["path"].append(rf[i])
				moved += 1
				if rf[i] == "HOME" or _live(rf[i]):
					break
			if moved > 0:
				ev["moves"].append([t["id"], frm, t["site"]])
		# ICE holds an arriving threat once per holder.
		for t in _active():
			var s: String = t["site"]
			if not (_hp.has(s) and (_live(s) or s == "HOME")) or t["hold"] > 0 or t["traits"].has("FROSTPROOF"):
				continue
			for h in H7Data.HOLDERS:
				var key: String = s + "#" + h[0]
				if _assets.has(s) and _assets[s].has(h[0]) and not held_by[t["id"]].has(key):
					held_by[t["id"]].append(key)
					t["hold"] = h[1]
					ev["holds"].append([t["id"], s, t["hold"]])
					break
		# Fire: nodes in sorted order, built-in gun first, then deployed pieces in placement order.
		var sites: Array = _hp.keys()
		sites.sort()
		var dh := _bfs("HOME")
		for site in sites:
			if not (_live(site) or site == "HOME"):
				continue
			var guns: Array = []
			if site == "FW":
				guns.append(["FWGUN", 3, 0, 1, "first"])
			if _assets.has(site):
				for a in _assets[site]:
					if H7Data.GUNS.has(a):
						var g: Array = H7Data.GUNS[a]
						guns.append([a, g[0], g[1], g[2], g[3]])
			var flat: int = H7Data.CREW_FLAT if crew == site else 0
			var dist := _bfs(site)
			for gun in guns:
				var dmg: int = gun[1] + flat
				for _s in range(gun[3]):
					var cands: Array = []
					for t in _active():
						if dist.get(t["site"], 99) <= gun[2]:
							cands.append(t)
					if cands.is_empty():
						break
					var high: bool = gun[4] == "high"
					cands.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
						if high and a["dmg"] != b["dmg"]:
							return a["dmg"] > b["dmg"]
						var da: int = dh.get(a["site"], 99)
						var db: int = dh.get(b["site"], 99)
						if da != db:
							return da < db
						return a["id"] < b["id"])
					var tt: Dictionary = cands[0]
					if (tt["traits"].has("PLATED") and dmg >= 8) or (tt["traits"].has("ARMORED") and dmg < 5):
						ev["shots"].append([site, gun[0], tt["id"], 0, tt["hp"]])
						continue
					tt["hp"] -= dmg
					ev["shots"].append([site, gun[0], tt["id"], dmg, maxi(0, tt["hp"])])
					if tt["hp"] <= 0:
						ev["kills"].append([tt["id"], tt["site"]])
		# Damage.
		for t in _active():
			var s2: String = t["site"]
			if t["hold"] > 0:
				continue
			if s2 == "HOME":
				_hp["HOME"] = maxi(0, _hp["HOME"] - t["dmg"])
				t["home"] = true
				ev["hits"].append([t["id"], "HOME", t["dmg"], _hp["HOME"]])
				continue
			if not _hp.has(s2):
				continue
			if _cond[s2] == "down":
				_cond[s2] = "taken"
				taken_now.append(s2)
				ev["taken"].append(s2)
				t["home"] = true
				t["left"] = true
				continue
			if _cond[s2] == "taken":
				continue
			_hp[s2] -= t["dmg"]
			ev["hits"].append([t["id"], s2, t["dmg"], maxi(0, _hp[s2])])
			if _hp[s2] <= 0:
				_hp[s2] = 0
				_cond[s2] = "down"
				down_now.append(s2)
				ev["down"].append(s2)
		var snap := {}
		for id in order:
			var v: Dictionary = _threats[id]
			snap[id] = [v["site"], maxi(0, v["hp"]), v["hp"] > 0 and not v["home"], v["hold"]]
		ev["threats"] = snap
		ev["hp"] = _hp.duplicate()
		ev["cond"] = _cond.duplicate()
		res.steps.append(ev)
		if _hp["HOME"] <= 0:
			break
	for t in _active():
		var s3: String = t["site"]
		if _hp.has(s3) and s3 != "HOME" and _cond[s3] != "taken":
			_cond[s3] = "taken"
			taken_now.append(s3)
	for k in H7Data.NODE_HP:
		var before: int = H7Data.NODE_HP[k]
		var out: String = _cond[k]
		if k == "HOME":
			out = "breached" if _hp["HOME"] <= 0 else "holds"
		elif out == "ok":
			out = "scuffed" if _hp[k] < before else "holds"
		if k == "HOME" and out == "holds" and _hp[k] < before:
			out = "scuffed"
		res.nodes[k] = {"before": before, "after": _hp[k], "outcome": out}
	res.clean = _hp["HOME"] >= H7Data.NODE_HP["HOME"] and down_now.is_empty() and taken_now.is_empty()
	res.home_before = H7Data.NODE_HP["HOME"]
	res.home_after = _hp["HOME"]
	res.breached = _hp["HOME"] <= 0
	for id in order:
		var v2: Dictionary = _threats[id]
		if v2["hp"] <= 0:
			res.killed.append(id)
		if v2["home"] and not v2["left"]:
			res.reached_home.append(id)
		res.routes[id] = v2["route_fixed"] if not v2["route_fixed"].is_empty() else v2["path"]
	res.frozen = _frozen.duplicate(true)
	return res
