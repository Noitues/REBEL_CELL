class_name RebelCellCampaignTheme
extends CorpThemeBlock
## Plan 2 WH-02: REBEL_CELL DISPATCH's campaign fields (WH-01 table, rebel_cell.md section 2),
## in the campaign's corp_theme block. The table's per-Site `lane_tag` lives here as a map so
## the Grid's Site state keeps its format. No rules yet (WH-30).

## Site id -> lane tag; a Site not listed has CampaignConfigData.lane_tag_default.
var lane_tags: Dictionary[StringName, StringName] = {}
var lanes_scouted: Array[StringName] = []


## The lane tag of `site_id` (`default_tag` when none is set).
func lane_tag(site_id: StringName, default_tag: StringName) -> StringName:
	return lane_tags.get(site_id, default_tag)
