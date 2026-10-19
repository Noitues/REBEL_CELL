class_name BloomState
extends CorpThemeBlock
## Plan 2 WH-02: Solace THE BLOOM's netrun fields (WH-01 table, solace.md section 2), in the
## run's corp_theme block. Thousandths of a layer. No rules yet (WH-11). An older save loads
## disabled and DORMANT.

var front_milli: int = 0
var layer_milli: int = 0
var doses_taken: int = 0
var caught: bool = false
## False when absent, outside Solace, or when the pace table gives 0.
var enabled: bool = false
## Free and bought doses not yet used.
var doses_held: int = 0
