class_name DefenseAssetData
extends Resource
## A run-collected asset placed on a node during Cell Defense setup.

@export var asset_type: RC.AssetType = RC.AssetType.TURRET
@export var id: StringName
@export var display_name: String
@export_multiline var description: String
@export var rarity: RC.Rarity = RC.Rarity.COMMON
@export var integrity: int = 10
@export var damage: int = 0
## 0 = only its own node; 1 = adjacent nodes too, etc.
@export var range_hops: int = 0
@export var shots_per_step: int = 1
@export var targeting: RC.AssetTargeting = RC.AssetTargeting.FIRST_IN_PATH
## ICE Lock: steps a threat is held.
@export var delay_steps: int = 0
## Decoy: how strongly it pulls threat routing toward itself.
@export var decoy_pull: int = 0
