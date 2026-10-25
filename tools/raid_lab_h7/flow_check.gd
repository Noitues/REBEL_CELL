extends SceneTree
## Flow check of the lab model (not the golden parity): the visit rules and a full play of every seeded leg.
##   godot --headless --path . -s res://tools/raid_lab_h7/flow_check.gd

var _fails: int = 0


func _ok(label: String, cond: bool) -> void:
	if not cond:
		_fails += 1
	print("%s %s" % ["PASS" if cond else "FAIL", label])


func _init() -> void:
	var m := H7LabModel.new()
	_ok("five seeded legs", m.legs.size() == 5)
	_ok("opening bank is 14", m.state.bank == 14)
	_ok("buy TURRET at FW", m.buy_place("TURRET", "FW"))
	_ok("buy RAILGUN refused (bank 8 < 10)", not m.can_buy("RAILGUN"))
	_ok("buy ICE at RELAY", m.buy_place("ICE", "RELAY"))
	_ok("third buy refused (2 per visit)", not m.can_buy("DECOY"))
	_ok("undo removes the last buy", m.undo() and m.buys.size() == 1 and m.free_bank() == 8)
	_ok("crew stations at FW", m.station_crew("FW") and m.active_crew() == "FW")
	_ok("forecast shows 2 raids while the PROXY holds", m.forecast().size() == 2)
	for li in range(m.legs.size()):
		m.new_leg(li)
		var lost_seen := false
		for i in range(3):
			var affordable: Array = []
			for p in H7Data.PIECES:
				if m.can_buy(p):
					affordable.append(p)
			if not affordable.is_empty():
				var held: Array = []
				for n in H7Data.NODES:
					if m.state.holds(n):
						held.append(n)
				m.buy_place(affordable[(li + i) % affordable.size()], held[(li * 2 + i) % held.size()])
			var fc := m.forecast()
			var row := m.start_raid()
			_ok("leg %d raid %d forecast matches the real result" % [li, i],
				fc[0]["settle"].net == row["settle"].net and fc[0]["settle"].state.bank == row["settle"].state.bank)
			lost_seen = lost_seen or not m.state.lost.is_empty()
			if m.leg_over():
				break
			m.next_visit()
		_ok("leg %d finished with %d raids" % [li, m.history.size()], m.leg_over())
		if lost_seen:
			_ok("leg %d: crew locked when SAFEHOUSE lost (or held)" % li, m.crew_free() == not m.state.lost.has("SAFE"))
	print("FLOW %s" % ("PASS" if _fails == 0 else "FAIL"))
	quit(0 if _fails == 0 else 1)
