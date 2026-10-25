class_name H7LabModel
extends RefCounted
## Play state of one leg: the visit (pending buys, crew), the raid in play and the leg history.
## Only calls the H7 rules; the view reads it and draws.

const MAX_BUYS := 2

var legs: Array = []
var leg_index: int = 0
var raid_index: int = 0
var state: H7State = H7State.new()
var buys: Array = []
var places: Array = []
var crew: String = "SAFE"
## Settled raids of this leg: {roster, r, settle, fort, buy, place, crew, before}.
var history: Array = []
## Bank after each raid, starting with the opening bank.
var bank_line: Array = [H7Data.START]
var breached: bool = false


func _init() -> void:
	legs = H7Data.load_legs()
	new_leg(0)


## The current leg: Array of 3 raids.
func leg() -> Array:
	return legs[leg_index]


## Starts leg `idx` from scratch.
func new_leg(idx: int) -> void:
	leg_index = clampi(idx, 0, legs.size() - 1)
	raid_index = 0
	state = H7State.new()
	buys = []
	places = []
	crew = "SAFE"
	history = []
	bank_line = [H7Data.START]
	breached = false


## Coins still free this visit (bank minus pending buys).
func free_bank() -> int:
	return state.bank - pending_cost()


## Coins committed by pending buys.
func pending_cost() -> int:
	var c := 0
	for b in buys:
		c += H7Data.COST[b]
	return c


## True when `piece` can be bought now: under the per-visit cap and within the bank.
func can_buy(piece: String) -> bool:
	return buys.size() < MAX_BUYS and H7Data.COST[piece] <= free_bank()


## Buys `piece` and places it on a held node. Returns false when refused.
func buy_place(piece: String, node: String) -> bool:
	if not can_buy(piece) or state.lost.has(node) or not H7Data.NODES.has(node):
		return false
	buys.append(piece)
	places.append(node)
	return true


## Undoes the last pending purchase (allowed until START RAID).
func undo() -> bool:
	if buys.is_empty():
		return false
	buys.pop_back()
	places.pop_back()
	return true


## True while the SAFEHOUSE holds, so the crew can be stationed.
func crew_free() -> bool:
	return not state.lost.has("SAFE")


## Stations the crew on a held node (only while the SAFEHOUSE holds).
func station_crew(node: String) -> bool:
	if not crew_free() or state.lost.has(node) or not H7Data.NODES.has(node):
		return false
	crew = node
	return true


## The crew node that actually fires ("" when the SAFEHOUSE is lost).
func active_crew() -> String:
	return crew if crew_free() and not state.lost.has(crew) else ""


## Forecast of this raid and the remaining telegraphed raids with this fortress and no further buys.
func forecast() -> Array:
	return H7Campaign.forecast(leg(), raid_index, state, buys, places, active_crew(), state.intel_ahead())


## Resolves the raid at hand with the pending buys, advances the state and returns the history row.
func start_raid() -> Dictionary:
	var roster := H7Campaign.roster_for(leg(), raid_index, state)
	var rr := H7Campaign.raid_result(state, buys, places, active_crew(), roster)
	var s := H7Campaign.settle(state, rr["fort"], rr["r"], roster, raid_index, buys, leg().size())
	var row := {"roster": roster, "r": rr["r"], "settle": s, "fort": rr["fort"], "buy": buys.duplicate(),
		"place": places.duplicate(), "crew": active_crew(), "before": state}
	history.append(row)
	state = s.state
	breached = rr["r"].breached
	bank_line.append(state.bank)
	return row


## Moves to the next visit after an aftermath (carries the crew if its node still holds).
func next_visit() -> void:
	raid_index += 1
	buys = []
	places = []
	if state.lost.has(crew):
		crew = "SAFE" if crew_free() else ""


## True when the leg is over (all raids settled or breached).
func leg_over() -> bool:
	return breached or (raid_index >= leg().size() - 1 and history.size() > raid_index)


## Count of CLEAN raids in the history.
func clean_count() -> int:
	var n := 0
	for h in history:
		if h["r"].clean:
			n += 1
	return n
