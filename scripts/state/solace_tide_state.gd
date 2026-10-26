class_name SolaceTideState
extends RefCounted
## The Solace raid's state (the Infected Tide, H5; SOLACE_RAID_SPEC.md sections 1 and 9). It replaces `infection_bp`
## (R-G). Two parts:
## - the tide block proper (saved inside SolaceCampaignTheme in Phase 2b): the defense deck and its id counters, the
##   ghost kit, the cadence and sacrifice counters, `purge_queued`, `dose_spent`, `breach_fails`;
## - the working view of the campaign fields the tide reads and writes (heat, Schematics, HOME integrity, the Sites'
##   condition, the Exploits held, ...). Phase 2b loads them from CampaignState before a raid and writes them back
##   after, so the core is testable without a campaign.
## Site conditions use `Cond`; a Site that is not in `owned` is not the Cell's (a CLEARED Site waits in `pending`).
## Runtime values only: nothing here is content.

## A Site's condition. TAKEN is the corp's: it is not a raid target any more and can be claimed back.
enum Cond { OK, DOWN, TAKEN }

## The `lost` words (also the Verdict words, see RaidOutcome.verdict_of_tide).
const LOST_NONE := ""
const LOST_BREACHED := "BREACHED"
const LOST_CITY := "CITY_LOST"

## Card verbs. GUARD / SHIFT / JAM are placeable; WOUND is INFECTED; DOSE is the antidote sample.
const VERB_GUARD := "GUARD"
const VERB_SHIFT := "SHIFT"
const VERB_JAM := "JAM"
const VERB_WOUND := "WOUND"
const VERB_DOSE := "DOSE"

# --- the tide block ---
## The defense deck: Array of [id: String, type: String, verb: String], kept sorted (id, then type, then verb).
## An INFECTED card (WOUND) holds the Site it is tied to in `type` ("HOME" for a HOME hit); a DOSE card "-".
var deck: Array = []
var inf_n: int = 0
var dose_n: int = 0
var asset_n: int = 0
var ghost: int = 0
var lost_since_raid: int = 0
var last_lost: StringName = &""
## Raid index of the last SACRIFICE; -9 = never.
var last_sac: int = -9
var raid_n: int = 0
var netruns_since_raid: int = 0
var purge_queued: bool = false
var dose_spent: int = 0
## Failed Genome Core breaches since the Exploits were last (re-)taken.
var breach_fails: int = 0
## A netrun crossed a raid Heat level for the first time since the last `note_netrun` (the campaign sets it when a
## Heat threshold fires; the netrun's close reads and clears it). Phase 2b; not in the spec's section 9 list.
var heat_crossed: bool = false
## DECAY of the pending raid has run and is part of the campaign (a raid is one checkpoint: DECAY is never undone, and an
## opened raid that is saved and loaded does not decay twice). Cleared when the raid resolves.
var decayed: bool = false
## Not saved: the weakest Heat band this raid's HOME hit may have (a story or retaliation raid, 0 = the Heat decides).
var min_band: int = 0

# --- the working view of the campaign ---
var heat: int = 0
## Schematics (the oracle's "bank").
var schematics: int = 0
## HOME integrity and its maximum.
var home: int = 0
var home_max: int = 0
## site -> Cond for every Site the Cell owns (claimed): Array keys are StringName.
var owned: Dictionary = {}
## Sites cleared by a netrun and waiting to be installed (sorted).
var pending: Array[StringName] = []
## The Exploit Sites whose Exploit is held (sorted) and the objective Sites already done (sorted).
var held: Array[StringName] = []
var obj_done: Array[StringName] = []
var deaths: int = 0
## "" while the campaign lives, else LOST_BREACHED or LOST_CITY.
var lost: String = LOST_NONE
## The Genome Core breach succeeded.
var won: bool = false
## The Heat levels (raid thresholds, the PURGE level included) already crossed.
var crossed_heat: Array[int] = []
var cools: int = 0
## INFECTED cards ever added, and Sites ever lost (statistics; the golden carries them).
var infected_total: int = 0
var sites_lost: int = 0


## A fresh campaign's tide: the config's start deck, the ghost kit, HOME whole.
static func start(cfg: CampaignConfigData, home_max_integrity: int) -> SolaceTideState:
	var s := SolaceTideState.new()
	s.deck = cfg.solace_tide_start_cards()
	s.sort_deck()
	s.ghost = cfg.solace_tide_ghost_start
	s.schematics = cfg.starting_schematics
	s.home_max = home_max_integrity
	s.home = home_max_integrity
	return s


## Sorts the deck by (id, type, verb) in text order.
func sort_deck() -> void:
	deck.sort_custom(card_less)


## True when card a sorts before card b.
static func card_less(a: Array, b: Array) -> bool:
	for i in 3:
		if String(a[i]) != String(b[i]):
			return String(a[i]) < String(b[i])
	return false


## INFECTED cards in the deck.
func wound_count() -> int:
	var n := 0
	for c in deck:
		if c[2] == VERB_WOUND:
			n += 1
	return n


## The DOSE cards, in deck (id) order.
func dose_cards() -> Array:
	var out: Array = []
	for c in deck:
		if c[2] == VERB_DOSE:
			out.append(c)
	return out


## Removes the card with this id.
func remove_card(card_id: String) -> void:
	for i in deck.size():
		if deck[i][0] == card_id:
			deck.remove_at(i)
			return


## True when `site` is a live Cell Site (OK or DOWN).
func is_live(site: StringName) -> bool:
	if not owned.has(site):
		return false
	return int(owned[site]) != Cond.TAKEN


func duplicate_state() -> SolaceTideState:
	var s := SolaceTideState.new()
	s.deck = []
	for c in deck:
		s.deck.append((c as Array).duplicate())
	s.inf_n = inf_n
	s.dose_n = dose_n
	s.asset_n = asset_n
	s.ghost = ghost
	s.lost_since_raid = lost_since_raid
	s.last_lost = last_lost
	s.last_sac = last_sac
	s.raid_n = raid_n
	s.netruns_since_raid = netruns_since_raid
	s.purge_queued = purge_queued
	s.dose_spent = dose_spent
	s.breach_fails = breach_fails
	s.heat_crossed = heat_crossed
	s.decayed = decayed
	s.min_band = min_band
	s.heat = heat
	s.schematics = schematics
	s.home = home
	s.home_max = home_max
	s.owned = owned.duplicate()
	s.pending = pending.duplicate()
	s.held = held.duplicate()
	s.obj_done = obj_done.duplicate()
	s.deaths = deaths
	s.lost = lost
	s.won = won
	s.crossed_heat = crossed_heat.duplicate()
	s.cools = cools
	s.infected_total = infected_total
	s.sites_lost = sites_lost
	return s


static func cond_word(c: int) -> String:
	match c:
		Cond.DOWN:
			return "DOWN"
		Cond.TAKEN:
			return "TAKEN"
	return "OK"


static func cond_of(word: String) -> int:
	match word:
		"DOWN":
			return Cond.DOWN
		"TAKEN":
			return Cond.TAKEN
	return Cond.OK


## The state as plain data in the golden's form (solace_raid_golden.json `state_json`) plus the tide counters the golden
## leaves out (`raid_n`, `netruns_since_raid`, `home_max`). JSON-compatible; the save and the parity test use it.
func to_dict() -> Dictionary:
	var ids: Array = owned.keys()
	IdSort.sort_ids(ids)
	var own: Array = []
	for s in ids:
		own.append([String(s), cond_word(int(owned[s]))])
	var d_deck: Array = []
	for c in deck:
		d_deck.append([String(c[0]), String(c[1]), String(c[2])])
	return {"heat": heat, "bank": schematics, "home": home, "owned": own, "deck": d_deck, "ghost": ghost,
		"held": _strings(held), "pending": _strings(pending), "obj_done": _strings(obj_done), "deaths": deaths,
		"lost": lost, "won": won, "crossed_heat": crossed_heat.duplicate(), "purge_queued": purge_queued,
		"lost_since_raid": lost_since_raid, "last_lost": String(last_lost), "inf_n": inf_n, "dose_n": dose_n,
		"asset_n": asset_n, "last_sac": last_sac, "cools": cools, "infected_total": infected_total,
		"sites_lost": sites_lost, "dose_spent": dose_spent, "breach_fails": breach_fails, "raid_n": raid_n,
		"netruns_since_raid": netruns_since_raid, "home_max": home_max}


## The block the campaign saves (SOLACE_RAID_SPEC.md section 9, plus `heat_crossed`): the deck as [[id, type, verb], ...] and
## the counters. The working view of the campaign fields (Heat, HOME, Site conditions, ...) is not saved here: the
## campaign owns them and `SolaceTideCampaign` loads them before every raid.
func block_dict() -> Dictionary:
	var d_deck: Array = []
	for c in deck:
		d_deck.append([String(c[0]), String(c[1]), String(c[2])])
	return {"deck": d_deck, "inf_n": inf_n, "dose_n": dose_n, "asset_n": asset_n, "ghost": ghost,
		"lost_since_raid": lost_since_raid, "last_lost": String(last_lost), "last_sac": last_sac, "raid_n": raid_n,
		"netruns_since_raid": netruns_since_raid, "purge_queued": purge_queued, "dose_spent": dose_spent,
		"breach_fails": breach_fails, "heat_crossed": heat_crossed, "decayed": decayed}


## A state with only the tide block filled (the inverse of `block_dict`; the JSON round trip gives floats for ints).
static func from_block(d: Dictionary) -> SolaceTideState:
	var s := SolaceTideState.new()
	for c in d.get("deck", []):
		s.deck.append([String(c[0]), String(c[1]), String(c[2])])
	s.inf_n = int(d.get("inf_n", 0))
	s.dose_n = int(d.get("dose_n", 0))
	s.asset_n = int(d.get("asset_n", 0))
	s.ghost = int(d.get("ghost", 0))
	s.lost_since_raid = int(d.get("lost_since_raid", 0))
	s.last_lost = StringName(String(d.get("last_lost", "")))
	s.last_sac = int(d.get("last_sac", -9))
	s.raid_n = int(d.get("raid_n", 0))
	s.netruns_since_raid = int(d.get("netruns_since_raid", 0))
	s.purge_queued = bool(d.get("purge_queued", false))
	s.dose_spent = int(d.get("dose_spent", 0))
	s.breach_fails = int(d.get("breach_fails", 0))
	s.heat_crossed = bool(d.get("heat_crossed", false))
	s.decayed = bool(d.get("decayed", false))
	return s


static func from_dict(d: Dictionary) -> SolaceTideState:
	var s := SolaceTideState.new()
	s.heat = int(d.get("heat", 0))
	s.schematics = int(d.get("bank", 0))
	s.home = int(d.get("home", 0))
	s.home_max = int(d.get("home_max", s.home))
	for pair in d.get("owned", []):
		s.owned[StringName(String(pair[0]))] = cond_of(String(pair[1]))
	for c in d.get("deck", []):
		s.deck.append([String(c[0]), String(c[1]), String(c[2])])
	s.ghost = int(d.get("ghost", 0))
	s.held = _ids(d.get("held", []))
	s.pending = _ids(d.get("pending", []))
	s.obj_done = _ids(d.get("obj_done", []))
	s.deaths = int(d.get("deaths", 0))
	s.lost = String(d.get("lost", ""))
	s.won = bool(d.get("won", false))
	for h in d.get("crossed_heat", []):
		s.crossed_heat.append(int(h))
	s.purge_queued = bool(d.get("purge_queued", false))
	s.lost_since_raid = int(d.get("lost_since_raid", 0))
	s.last_lost = StringName(String(d.get("last_lost", "")))
	s.inf_n = int(d.get("inf_n", 0))
	s.dose_n = int(d.get("dose_n", 0))
	s.asset_n = int(d.get("asset_n", 0))
	s.last_sac = int(d.get("last_sac", -9))
	s.cools = int(d.get("cools", 0))
	s.infected_total = int(d.get("infected_total", 0))
	s.sites_lost = int(d.get("sites_lost", 0))
	s.dose_spent = int(d.get("dose_spent", 0))
	s.breach_fails = int(d.get("breach_fails", 0))
	s.raid_n = int(d.get("raid_n", 0))
	s.netruns_since_raid = int(d.get("netruns_since_raid", 0))
	return s


static func _strings(ids: Array) -> Array:
	var out: Array = []
	for i in ids:
		out.append(String(i))
	return out


static func _ids(raw: Array) -> Array[StringName]:
	var out: Array[StringName] = []
	for i in raw:
		out.append(StringName(String(i)))
	return out
