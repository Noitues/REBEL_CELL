class_name RaidWaveData
extends Resource

## Repeat a ThreatData to send several.
@export var threats: Array[ThreatData] = []
## Site ids to enter from. Empty = corporate Sites next to your territory.
@export var entry_site_ids: Array[StringName] = []
