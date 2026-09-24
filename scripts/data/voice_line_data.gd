class_name VoiceLineData
extends Resource
## One spoken or subtitled line (GDD 8.2, 8.6, 9.6). Keys route lines to moments:
##   "site:<site_id>"      DISPATCH briefing before a netrun at that Site
##   "raid:<raid_id>"      raid warning (Corpo voice or DISPATCH)
##   "threshold:<heat>"    Heat threshold crossed
##   "boss", "win", "loss" the breach, the campaign end
##   "bark:<trigger>"      operative barks: perfect, miss, hurt, victory, defeat, deploy, jack_in
##   "dj"                  pirate-radio lines at HQ
##   "run_start", "run_complete", "run_died", "rack"
## Several lines may share a key; Dialogue picks one deterministically.

@export var key: String = ""
@export_multiline var text: String = ""
## DISPATCH voice drift (GDD 8.2): 0 = human, 1 = slipping, 2 = machine. A line plays only
## once the profile's drift stage has reached it; higher stages replace lower ones.
@export_range(0, 2) var drift_stage: int = 0
## The line carries a hidden DISPATCH clue.
@export var dispatch_clue: bool = false
## Optional voice-over clip (recorded later); empty = subtitle only.
@export var audio_path: String = ""
