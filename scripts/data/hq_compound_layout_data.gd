class_name HqCompoundLayoutData
extends Resource
## ART-8 8p: where a corporation's HQ-run nodes stand on its overhead compound model
## (bible 4.7). One per corporation, `content/city/hq_compounds/<corp>.tres`, id
## `hq_compound_<corporation id>` (see id_for). Written by
## tools/art_pipeline/city/make_hq_compounds.py from the same spec that builds the model;
## read-only at runtime. HqCompoundLayout (scripts/core/) maps a run's nodes onto it.
##
## Positions are in the compound model's frame (Godot / glTF: Y up, metres, origin = the
## compound's ground centre), each on a static part of the model. Slot rows follow the
## current HQ-run rules (GDD 4.2): `layer_slots` holds `slots_per_layer` slots for each of
## the map's layers before the final one, layer 1 first, slots left to right on screen;
## the final node (the Central Server) stands at `central_server`.

const ID_PREFIX := "hq_compound_"

## `hq_compound_<corporation id>`.
@export var id: StringName
@export var corporation_id: StringName
## The folder of the exported model and its manifest.json (res://assets/city/hq_compounds/<corp>).
@export var asset_dir: String = ""
## Slots per layer row (= CampaignConfigData.map_nodes_max).
@export var slots_per_layer: int = 4
## Row-major: layer 1 slot 0 first.
@export var layer_slots: PackedVector3Array = PackedVector3Array()
## The Central Server: the final node of a run map and the single node of the breach.
@export var central_server: Vector3 = Vector3.ZERO
## Where the run enters the compound (the walked path starts here; not a node).
@export var entry: Vector3 = Vector3.ZERO


## The content id of `corporation_id`'s layout.
static func id_for(p_corporation_id: StringName) -> StringName:
	return StringName(ID_PREFIX + String(p_corporation_id))


## Number of layer rows (layers before the final one).
func layer_rows() -> int:
	return floori(float(layer_slots.size()) / float(slots_per_layer)) if slots_per_layer > 0 else 0


## Slot `slot` (0-based) of layer `layer` (1-based).
func slot_position(layer: int, slot: int) -> Vector3:
	return layer_slots[(layer - 1) * slots_per_layer + slot]


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if corporation_id == &"":
		errors.append("HQ compound layout has no corporation_id.")
	elif id != id_for(corporation_id):
		errors.append("HQ compound layout id %s, expected %s." % [id, id_for(corporation_id)])
	if asset_dir == "":
		errors.append("HQ compound layout %s has no asset_dir." % id)
	if slots_per_layer < 1:
		errors.append("HQ compound layout %s: slots_per_layer %d." % [id, slots_per_layer])
	elif layer_slots.is_empty() or layer_slots.size() % slots_per_layer != 0:
		errors.append("HQ compound layout %s: %d slots is not whole rows of %d." % [id, layer_slots.size(), slots_per_layer])
	return errors
