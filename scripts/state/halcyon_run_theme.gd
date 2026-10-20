class_name HalcyonRunTheme
extends CorpThemeBlock
## Plan 2 WH-02: Halcyon THE EYE's netrun fields (WH-01 table, halcyon.md section 2), in the
## run's corp_theme block. No rules yet (WH-21).

## Spotted level, 0-2.
var spotted_level: int = 0
## HQ only: the gaze phase (0-7) and its step counter.
var eye_phase: int = 0
var eye_step: int = 0
## Halcyon v2: an HQ run (the gaze, Alert, Stall and Cut the Power apply).
var hq: bool = false
## HQ: Alert (starts at spotted_level), the Eye's remaining asleep steps (Cut the Power), whether the
## Power Room's action was used, and whether a Stall was taken at the current layer.
var hq_alert: int = 0
var hq_asleep_left: int = 0
var power_cut_used: bool = false
var stalled_this_layer: bool = false
