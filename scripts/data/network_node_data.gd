class_name NetworkNodeData
extends Resource
## A node you install on your home server or a claimed Site.

@export var id: StringName
@export var node_type: RC.NetworkNodeType = RC.NetworkNodeType.RELAY
@export var display_name: String
@export_multiline var description: String
@export var install_cost: int = 20
## Repair cost for a Disabled node = install_cost * this.
@export var repair_cost_ratio: float = 0.5
@export var integrity: int = 20
@export var asset_slots: int = 0
## Always-present defence (e.g. Firewall Relay turret). Not counted in asset_slots.
@export var built_in_asset: DefenseAssetData
@export var station_slots: int = 0
## Higher = raids prefer this node (Vault Terminals).
@export var raid_priority: int = 0
## e.g. Proxy Relay: ON_NETRUN_COMPLETE -> MODIFY_HEAT -1 (CAMPAIGN).
@export var passive_effects: Array[TriggeredEffectData] = []
@export var adjacency_bonuses: Array[AdjacencyBonusData] = []
## Building this node provokes a raid.
@export var triggers_raid: bool = false
## Must be unlocked on the Profile layer before it can be built.
@export var profile_unlock_required: bool = false
