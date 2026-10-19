class_name CampaignThemeState
extends CorpThemeBlock
## Plan 2 WH-02 (REPLAN 2026-10-19 A 2.4): a campaign's corp_theme block
## (CampaignState.corp_theme), one typed sub-object per W2 corporation with campaign fields,
## and the raid block. Saved and hashed only when a field is not default.

var halcyon: HalcyonCampaignTheme = HalcyonCampaignTheme.new()
var rebel_cell: RebelCellCampaignTheme = RebelCellCampaignTheme.new()
var raid: RaidThemeState = RaidThemeState.new()
