class_name MeridianRunTheme
extends CorpThemeBlock
## Plan 2 WH-02: Meridian A PAYLOAD's netrun fields (WH-01 table, meridian.md section 2), in
## the run's corp_theme block. Load, capacity and Over are derived, never saved. No rules yet
## (WH-51).

## Capacity change; each Weigh Station passed subtracts the penalty (stored negative).
var capacity_bonus: int = 0
## The layers of the Weigh Stations passed.
var weigh_stations_passed: PackedInt32Array = PackedInt32Array()
