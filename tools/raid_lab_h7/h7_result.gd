class_name H7Result
extends RefCounted
## One resolved raid: the step log plus the per-node outcome (mirror of the python sim Result).

## Per step: Dictionary with moves, holds, shots, hits, down, taken, kills, targets, threats, hp, cond.
var steps: Array = []
## node -> {before, after, outcome} (outcome: holds, scuffed, down, taken, breached).
var nodes: Dictionary = {}
var home_before: int = 0
var home_after: int = 0
var killed: Array = []
var reached_home: Array = []
var clean: bool = false
var breached: bool = false
## threat id -> Array of node ids (the fixed route).
var routes: Dictionary = {}
## Frozen links: Array of [a, b] sorted pairs.
var frozen: Array = []


## Threat ids killed during the raid (sorted).
func kill_ids() -> Array:
	var out: Array = []
	for ev in steps:
		for k in ev["kills"]:
			if not out.has(k[0]):
				out.append(k[0])
	out.sort()
	return out
