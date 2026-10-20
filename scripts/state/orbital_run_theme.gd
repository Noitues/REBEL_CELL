class_name OrbitalRunTheme
extends CorpThemeBlock
## Plan 2 WH-02: Orbital BLACKOUT's netrun fields (WH-01 table, orbital.md section 2), in the
## run's corp_theme block. No rules yet (WH-41).

## Dark fight node ids, sorted by id (IdSort).
var dark_nodes: Array[StringName] = []
## HQ only: layers lit up to (Uplink Dish clears).
var lit_until_layer: int = 0
