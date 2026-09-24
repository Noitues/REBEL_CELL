class_name RankRewardData
extends Resource
## What an operative gains on reaching a rank (5.2).

@export_range(1, 10) var rank: int = 1
## Highest netrun tier this rank can enter.
@export_range(1, 4) var max_netrun_tier: int = 2
## Installed at this rank (Rank 1: class Inner Ring).
@export var inner_ring: InnerRingData
## Replaces the Hub Core at this rank (Rank 2).
@export var hub_upgrade: HubCoreData
## Segment swap choices unlocked at this rank (Rank 3).
@export var ring_segment_options: Array[RingSegmentData] = []
## Station bonus strength at this rank (1.0 = base).
@export var station_bonus_multiplier: float = 1.0
