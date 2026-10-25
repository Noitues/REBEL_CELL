class_name H7Data
extends RefCounted
## Constants and content tables for the H7 Bastion raid lab.
## Ported from tools/raid_concepts/sim.py, depth_harness.py and h7_campaign.py (python source of truth).

const GOLDEN_PATH := "res://tools/raid_concepts/h7_golden.json"
const LEGS_PATH := "res://tools/raid_lab_h7/data/h7_golden.json"

const NODES: Array[String] = ["HOME", "FW", "VAULT", "SAFE", "RELAY", "PROXY"]
const NODE_HP := {"HOME": 50, "FW": 30, "VAULT": 20, "SAFE": 20, "RELAY": 15, "PROXY": 15}
## Install cost per node; a DOWN node's repair is half.
const INSTALL := {"FW": 16, "VAULT": 16, "SAFE": 12, "RELAY": 8, "PROXY": 10}
const PRIORITY := {"VAULT": 3, "FW": 1, "SAFE": 1, "RELAY": 1, "PROXY": 1}
const LINKS := [["HOME", "FW"], ["HOME", "VAULT"], ["HOME", "SAFE"], ["FW", "RELAY"], ["VAULT", "RELAY"],
	["VAULT", "PROXY"], ["SAFE", "PROXY"], ["RELAY", "C1"], ["PROXY", "C2"]]
## Fortress pieces in shop order.
const PIECES: Array[String] = ["TURRET", "SENTRY", "RAILGUN", "ICE", "DECOY"]
const COST := {"TURRET": 6, "SENTRY": 7, "RAILGUN": 10, "ICE": 5, "DECOY": 4}
## Guns: damage, reach (hops), shots per step, targeting.
const GUNS := {"TURRET": [4, 1, 1, "first"], "SENTRY": [3, 0, 2, "first"], "RAILGUN": [8, 2, 1, "high"]}
const HOLDERS := [["ICE", 2], ["TARPIT", 3]]
const COUNTER := {"RAILGUN": "PLATED", "TURRET": "ARMORED", "SENTRY": "ARMORED", "ICE": "FROSTPROOF",
	"DECOY": "BLIND"}
## Threat table: hp, damage, speed, routing, default entry.
const THREAT_DEF := {
	"AUDITOR": [8, 3, 2, "value", "C2"], "COLLECTOR": [12, 5, 1, "home", "C1"],
	"ENFORCER": [25, 9, 1, "weakest", "C2"], "LOCKDOWN": [18, 6, 1, "weakest", "C1"],
	"COURIER": [8, 3, 2, "value", "C2"], "INSPECTOR": [10, 4, 2, "value", "C1"],
	"BAILIFF": [30, 10, 1, "weakest", "C2"], "HAULER": [28, 10, 1, "weakest", "C1"],
}
const THREAT_SHORT := {"AUDITOR": "AUD", "COLLECTOR": "COL", "ENFORCER": "ENF", "LOCKDOWN": "LCK",
	"COURIER": "COU", "INSPECTOR": "INS", "BAILIFF": "BAI", "HAULER": "HAU"}
const START := 14
const BASE_INCOME := 8
const VAULT_INC := 3
const RELAY_INC := 2
const BREACH_SCORE := -100
const SALVAGE := 4
const BONUS := 6
const CREW_FLAT := 2
const STEP_CAP := 30
const HEATS := [26, 51, 76]
const NETRUNS := [2, 3, 3]
const RAIDS_PER_LEG := 3

static var _adj: Dictionary = {}


## Sorted adjacency list of a node (corp sites included).
static func adj(n: String) -> Array:
	if _adj.is_empty():
		for l in LINKS:
			if not _adj.has(l[0]):
				_adj[l[0]] = []
			if not _adj.has(l[1]):
				_adj[l[1]] = []
			_adj[l[0]].append(l[1])
			_adj[l[1]].append(l[0])
		for k in _adj:
			_adj[k].sort()
	return _adj[n]


## Loads a JSON file into a Dictionary (empty when missing).
static func load_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return parsed if parsed is Dictionary else {}


## The 5 seeded legs: Array of legs, each 3 raids, each Array of [threat id, entry].
static func load_legs() -> Array:
	return load_json(LEGS_PATH).get("legs", [])
