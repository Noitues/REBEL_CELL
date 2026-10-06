class_name ExitDialogs
extends RefCounted
## The three ways out (designer ruling 2026-10-05, GDD 4.5), as the pause menus ask them:
## abandon run and abandon campaign are 4C's AbandonDialog (round 33 `abandon_dialog`:
## `> CONFIRM // ABANDON RUN`, CANNOT UNDO, the costs, yellow CANCEL with the default focus,
## pink BURN IT held 0.8 s on the pad / keyboard); quit is 2D's ConfirmDialog
## (`> CONFIRM // QUIT`, not destructive) with its key hints. Each dialog's numbers are the
## rules' own preview (NetrunSession.abandon_preview, ExitRules.abandon_campaign_preview), so
## what it shows is what a confirm does. View only: the caller wires `confirmed` to RunManager.


## Abandon run, from `p` = RunManager.abandon_run_preview(): the operative lost with what is
## unbanked (Cycles, assets, cards / Firmware / Daemons gained this run, Rank), the death's
## Heat, and the banked Schematics that stay.
static func abandon_run(p: Dictionary) -> AbandonDialog:
	var who := String(p.get("operative", ""))
	var costs: Array = [[TextDb.mark("Cycles"), int(p.get("cycles", 0))], [TextDb.mark("Cards added"), int(p.get("cards_added", 0))],
		[TextDb.mark("Firmware"), int(p.get("firmware", 0))], [TextDb.mark("Daemons"), int(p.get("daemons", 0))],
		[TextDb.mark("Assets"), int(p.get("assets", 0))], [TextDb.mark("Rank"), int(p.get("rank", 0))]]
	var heat := tr_word("HEAT  %s   (operative death, tier %d)") % [TextDb.signed(int(p.get("heat", 0))), int(p.get("tier", 1))]
	var kept := tr_word("Schematics already banked at a Server Rack stay banked.")
	var d := AbandonDialog.new(tr_word("Abandon the run?"), TextDb.mark("BURN IT"), TextDb.mark("ABANDON RUN"),
		tr_word("%s is lost for good, with everything unbanked:") % who, costs, heat, kept,
		tr_word("abandon, lose %s [hold A]") % who, TextDb.mark("keep running [B]"))
	d.name = "AbandonRun"
	d.require_hold()
	return d


## Abandon campaign, from `p` = RunManager.abandon_campaign_preview(): what ends with it (runs,
## living operatives, Schematics, claimed Sites, Heat, ICE); it counts as a lost campaign; the
## profile's stats and achievements stay. `corporation` is the corporation's shown name.
static func abandon_campaign(p: Dictionary, corporation: String) -> AbandonDialog:
	var costs: Array = [[TextDb.mark("Runs"), int(p.get("runs", 0))], [TextDb.mark("Operatives"), int(p.get("operatives", 0))],
		[TextDb.mark("Schematics"), int(p.get("schematics", 0))], [TextDb.mark("Sites"), int(p.get("sites", 0))],
		[TextDb.mark("Heat"), int(p.get("heat", 0))], [TextDb.mark("ICE"), int(p.get("ice", 0))]]
	var d := AbandonDialog.new(tr_word("Abandon the campaign?"), TextDb.mark("BURN IT"), TextDb.mark("ABANDON CAMPAIGN"),
		tr_word("The campaign against %s ends here, with everything in it:") % corporation, costs,
		tr_word("It counts as a lost campaign."), tr_word("Your stats and achievements stay."),
		tr_word("abandon the campaign [hold A]"), TextDb.mark("keep fighting [B]"))
	d.name = "AbandonCampaign"
	d.require_hold()
	return d


## Quit (not destructive): the game saves where it is and the title's BREACH (Continue)
## picks it up; `in_run` names the run in the body.
static func quit(in_run: bool) -> ConfirmDialog:
	var body := tr_word("Your run is saved where it is: BREACH on the title picks it up.") if in_run \
		else tr_word("Your campaign is saved: BREACH on the title picks it up.")
	var d := ConfirmDialog.new(tr_word("Quit REBEL_CELL?"), TextDb.mark("QUIT"), TextDb.mark("CANCEL"), TextDb.mark("QUIT"), body, false,
		TextDb.mark("save and quit"), TextDb.mark("keep going"))
	d.name = "QuitConfirm"
	# The key hints ride as the stickers' keys, so they stay at big text (where the line drops).
	_hint(d.yes_button, "[A]")
	_hint(d.no_button, "[B]")
	return d


## Gives a quit sticker its key hint (SendItSticker's line keeps the key at every text size).
static func _hint(b: Button, key: String) -> void:
	var st := b as SendItSticker
	if st != null:
		st.key_hint = key
		st._fit_size()


## `key` through the TranslationServer once (static code has no Node.tr; export_text reads
## `tr_word("...")` literals as keys, as CityMapOverlay's).
static func tr_word(key: String) -> String:
	return String(TranslationServer.translate(key))
