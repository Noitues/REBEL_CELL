class_name RaidThemeState
extends CorpThemeBlock
## Plan 2 WH-02 (REPLAN 2026-10-19 A 2.4): the raid's corp_theme block. A raid is resolved in
## one call (RaidResolver), so the raid's saved state is the campaign's: this block lives at
## CampaignThemeState.raid. One typed sub-object per corporation with raid fields.

var rebel_cell: RebelCellRaidTheme = RebelCellRaidTheme.new()
var orbital: OrbitalRaidTheme = OrbitalRaidTheme.new()
