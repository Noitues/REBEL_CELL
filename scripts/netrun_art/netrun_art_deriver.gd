class_name NetrunArtDeriver
extends RefCounted
## NA-21: the GDScript twin of the Python derive producers (`tools/netrun_art/derive/`, `hq/slots.py`). Turns the game's
## partial `derive_<run>.json` (version 1: kind, layout seed, run id, art seeds) plus the laid-out city, net and run graph
## into the full v2 file for a street or an HQ netrun. Pure and deterministic: no RNG, no Nodes; the same inputs give the
## same bytes (`derive_text`), and the Python oracle gives the same text (tests/netrun_art/test_na21_parity.gd).
## A failed derivation returns `{"error": message}` (the Python `DeriveError` / `SlotError`).

## `derive_<run>.json` version written by the twins.
const VERSION := 2


## The partial file the game writes: `version` 1, `kind`, `layout_seed` (u64 decimal string), `run`, `art_seeds`
## (the scene streams plus `landmark.<corp>` / `key_landmark.<corp>` for `corps`). Same shape as `NetrunArtExport.derive_json`.
static func game_partial(layout_seed: String, run: String, kind: String, corps: Array = []) -> Dictionary:
	return NetrunArtExport.derive_json(kind, ArtSeed.u64_from_str(layout_seed), run, corps)


## The street derive v2 dict for the Site `site` (or `{"error": message}`). `city` is the laid-out, zoned city.json,
## `partial` the game's partial file (empty: built from the city header).
static func derive_street(city: Dictionary, net: Dictionary, run_graph: Dictionary, site: String,
		partial: Dictionary = {}) -> Dictionary:
	return NetrunStreetDeriver.derive_street(city, net, run_graph, site, partial)


## The HQ derive v2 dict for `corp`'s HQ lot (or `{"error": message}`).
static func derive_hq(city: Dictionary, run_graph: Dictionary, corp: String, partial: Dictionary = {}) -> Dictionary:
	return NetrunHqSlots.derive_hq(city, run_graph, corp, partial)


## `poses_<run>.json` v1 for a derive v2 dict (street or HQ). `net` feeds the street dive's HQ page camera (`{}` for HQ).
static func poses(derive: Dictionary, city: Dictionary, run_graph: Dictionary, net: Dictionary = {}) -> Dictionary:
	return NetrunPoseBuilder.build_poses(derive, city, run_graph, net)


## Canonical contract text of a derive (or poses) dict: the one hand-written serializer, `NetrunArtExport.canonical`.
static func derive_text(derive: Dictionary) -> String:
	return NetrunArtExport.canonical(derive)
