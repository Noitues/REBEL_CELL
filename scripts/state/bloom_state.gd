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
## WH-11: an HQ run (HQ numbers; one front shared by both towers).
var hq: bool = false
## WH-11: Exploit keys held for this run (Intel reveals the whole ladder gap and halves turn cost, Virus scales pace).
var key_intel: bool = false
var key_virus: bool = false
## Solace v2: the Breach key (one-time setback on the first node entry, ACROSS is free).
var key_breach: bool = false
## Solace v2: the setback has fired this netrun.
var breach_applied: bool = false
## Solace v2: the Heat band's pace percent, refreshed by the session before each entry / fight end.
var heat_pct: int = 100
