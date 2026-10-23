class_name L4State
extends RefCounted
## The campaign numbers the rules read and write: Heat, bank (Schematics), home integrity, one status per asset
## ("OK" / "DOWN" / "TAKEN") and the leg kit (ghosts, decoys, spoofs, dark charges left). A value object; the rules return fresh ones.

var heat: int = L4Config.START_HEAT
var bank: int = L4Config.START_BANK
var home_hp: int = L4Config.HOME_HP
var status: Dictionary = {}
var kit: Dictionary = L4Config.KIT_START.duplicate()


func copy() -> L4State:
	var s := L4State.new()
	s.heat = heat
	s.bank = bank
	s.home_hp = home_hp
	s.status = status.duplicate()
	s.kit = kit.duplicate()
	return s


## The golden's state dictionary: {heat, bank, home_hp, status: [[x, y, "OK"], ...], kit: {...}}.
static func from_golden(d: Dictionary) -> L4State:
	var s := L4State.new()
	s.heat = int(d["heat"])
	s.bank = int(d["bank"])
	s.home_hp = int(d["home_hp"])
	for e in d["status"]:
		s.status[Vector2i(int(e[0]), int(e[1]))] = String(e[2])
	s.kit = {}
	for k in L4Config.KITS:
		s.kit[k] = int(d["kit"][k])
	return s


## Statuses sorted x first then y, as the golden's sorted tuples.
func status_list() -> Array:
	var keys: Array = status.keys()
	keys.sort_custom(func(a: Vector2i, b: Vector2i) -> bool: return a.x < b.x or (a.x == b.x and a.y < b.y))
	var out: Array = []
	for c in keys:
		out.append([c.x, c.y, status[c]])
	return out


## [heat, bank, home_hp, statuses, ghost, decoy, spoof, dark] for comparisons.
func to_array() -> Array:
	return [heat, bank, home_hp, status_list(), int(kit["ghost"]), int(kit["decoy"]), int(kit["spoof"]), int(kit["dark"])]


func count(what: String) -> int:
	var n := 0
	for c in status:
		if status[c] == what:
			n += 1
	return n
