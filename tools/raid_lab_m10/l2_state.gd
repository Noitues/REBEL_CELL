class_name L2State
extends RefCounted
## The campaign numbers the rules read and write: Heat, bank (Schematics), home integrity and one status per asset
## ("OK" / "DOWN" / "TAKEN"). A value object; the rules always return a fresh one.

var heat: int = L2Config.START_HEAT
var bank: int = L2Config.START_BANK
var home_hp: int = L2Config.HOME_HP
var status: Dictionary = {}


func copy() -> L2State:
	var s := L2State.new()
	s.heat = heat
	s.bank = bank
	s.home_hp = home_hp
	s.status = status.duplicate()
	return s


## The golden's state dictionary: {heat, bank, home_hp, status: [[x, y, "OK"], ...]}.
static func from_golden(d: Dictionary) -> L2State:
	var s := L2State.new()
	s.heat = int(d["heat"])
	s.bank = int(d["bank"])
	s.home_hp = int(d["home_hp"])
	for e in d["status"]:
		s.status[Vector2i(int(e[0]), int(e[1]))] = String(e[2])
	return s


## Statuses sorted x first then y, as the golden's sorted tuples.
func status_list() -> Array:
	var keys: Array = status.keys()
	keys.sort_custom(func(a: Vector2i, b: Vector2i) -> bool: return a.x < b.x or (a.x == b.x and a.y < b.y))
	var out: Array = []
	for c in keys:
		out.append([c.x, c.y, status[c]])
	return out


func to_array() -> Array:
	return [heat, bank, home_hp, status_list()]


func count(what: String) -> int:
	var n := 0
	for c in status:
		if status[c] == what:
			n += 1
	return n
