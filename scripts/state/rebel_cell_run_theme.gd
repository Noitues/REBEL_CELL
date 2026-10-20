class_name RebelCellRunTheme
extends CorpThemeBlock
## Plan 2 WH-02: REBEL_CELL DISPATCH's netrun fields (WH-01 table, rebel_cell.md section 2),
## in the run's corp_theme block. No rules yet (WH-30).

## The three-lane strike; null outside HQ runs.
var hq_strike: HqStrikeState = null


func _new_child(field: String) -> CorpThemeBlock:
	return HqStrikeState.new() if field == "hq_strike" else null
