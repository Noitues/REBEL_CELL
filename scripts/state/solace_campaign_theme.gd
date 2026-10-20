class_name SolaceCampaignTheme
extends CorpThemeBlock
## Solace v2 (S1): the campaign's population infection, basis points 0..10000. One campaign
## figure: it persists across raids and netruns, is never reset per raid, and falls only by the
## decay hooks (SolaceRaidRules). Saved only when above 0; an older save loads 0.

var infection_bp: int = 0
