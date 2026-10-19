class_name RunThemeState
extends CorpThemeBlock
## Plan 2 WH-02 (REPLAN 2026-10-19 A 2.4): a netrun's corp_theme block (RunState.corp_theme),
## one typed sub-object per W2 corporation. Saved and hashed only when a field is not default.

## The HUD theme chip's look (NetrunSession.theme_chip): plain, a warning, a danger.
enum ChipKind { INFO, WARN, DANGER }

var solace: BloomState = BloomState.new()
var halcyon: HalcyonRunTheme = HalcyonRunTheme.new()
var rebel_cell: RebelCellRunTheme = RebelCellRunTheme.new()
var orbital: OrbitalRunTheme = OrbitalRunTheme.new()
var meridian: MeridianRunTheme = MeridianRunTheme.new()
