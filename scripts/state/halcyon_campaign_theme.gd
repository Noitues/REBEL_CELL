class_name HalcyonCampaignTheme
extends CorpThemeBlock
## Plan 2 WH-02: Halcyon THE EYE's campaign fields (WH-01 table, halcyon.md section 2), in the
## campaign's corp_theme block. No rules yet (WH-21: the first eye_index comes from the
## eye_start stream, checkpointed, never redrawn on load).

## The Eye's octant, 0-7.
var eye_index: int = 0
## Netruns the Eye stays fixed (0-2).
var eye_fixed_left: int = 0
