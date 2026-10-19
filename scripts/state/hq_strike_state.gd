class_name HqStrikeState
extends CorpThemeBlock
## Plan 2 WH-02: REBEL_CELL DISPATCH's three-lane HQ strike (WH-01 table, rebel_cell.md
## section 2), held by RebelCellRunTheme.hq_strike during an HQ run only. No rules yet (WH-30).

enum Phase { ROUTE, THROWN, FINALE }
enum LaneStatus { ALIVE, ARMED, DARK }
## focus_lane outside the finale.
const NO_FOCUS: int = -1

## One per lane, in CampaignConfigData.hq_lane_ids order: {"lane_id", "operative_id",
## "layer", "node_id", "status" (LaneStatus)}.
var lanes: Array[Dictionary] = []
## One map graph per lane (MapGraph.to_dict), built once at launch from the map stream.
var graphs: Array[Dictionary] = []
var phase: int = Phase.ROUTE
## Finale only: the lane in focus.
var focus_lane: int = NO_FOCUS
