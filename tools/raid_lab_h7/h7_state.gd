class_name H7State
extends RefCounted
## Campaign state between raids (mirror of h7_campaign.State): bank, fortress, lost nodes, survivors.

var bank: int = H7Data.START
## node -> Array of piece ids, in placement order.
var fort: Dictionary = {}
## Nodes TAKEN earlier in the leg (sorted); they stay lost for the leg and are corp footholds.
var lost: Array = []
## Survivors who rejoin the next raid: Array of [id, entry].
var surv: Array = []


## Deep copy.
func copy() -> H7State:
	var s := H7State.new()
	s.bank = bank
	s.fort = fort.duplicate(true)
	s.lost = lost.duplicate()
	s.surv = surv.duplicate(true)
	return s


## True while the node job still works (the node is not lost).
func holds(node: String) -> bool:
	return not lost.has(node)


## Income per visit after the first raid: base plus the Vault and Relay while they hold.
func income() -> int:
	return H7Data.BASE_INCOME + (H7Data.VAULT_INC if holds("VAULT") else 0) + (H7Data.RELAY_INC if holds("RELAY") else 0)


## Raids visible ahead (the PROXY's intel): 2 while it holds, else 1.
func intel_ahead() -> int:
	return 2 if holds("PROXY") else 1
