class_name UiMotionData
extends Resource
## Every UI animation's timing in one resource (`content/config/ui_motion.tres`,
## ANIMATION_HANDOFF 3): durations, delays, eases and amplitudes live here, never inline.
## Read-only at runtime; the `Motion` kit reads it by id.

## Every id the game and the motion roadmap name (ANIMATION_HANDOFF 4.1-4.24, plus the
## shared ones moved out of Fx and Toast). Content validation requires each in the table.
const REQUIRED_IDS: Array[StringName] = [
	&"screen_flash", &"hit_freeze", &"saved_stamp", &"toast",
	&"jack_in", &"jack_out", &"jack_fade_reduced",  # 4.1
	&"wheel_spin", &"wheel_spin_blur",  # 4.2
	&"wheel_nudge",  # 4.3
	&"precision_perfect", &"precision_good_ring", &"precision_partial", &"precision_blink", &"precision_miss_static",  # 4.4
	&"card_hover", &"card_play", &"card_draw", &"card_exhaust",  # 4.5
	&"send_it_press", &"send_it_drips", &"resolve_pass", &"resolve_pulse",  # 4.6
	&"number_float", &"number_crit", &"hp_lag",  # 4.7
	&"intent_flip",  # 4.8
	&"rewind_scrub",  # 4.9
	&"pointer_flicker", &"orbit_trail",  # 4.10
	&"enemy_break", &"hub_shatter",  # 4.11
	&"heat_pulse", &"heat_letters_shake", &"poster_stamp", &"net_creep",  # 4.12
	&"hq_crt_hum", &"radio_type", &"jack_ring_breathe", &"polaroid_tilt",  # 4.13
	&"site_outline_draw", &"map_camera_ease", &"route_crawl", &"asset_drop",  # 4.14
	&"raid_move", &"turret_trace", &"raid_flip",  # 4.15
	&"route_pulse", &"node_pop", &"visited_dim",  # 4.16
	&"panel_in", &"panel_crt_roll", &"panel_drop",  # 4.17
	&"menu_cursor_blink", &"menu_type", &"menu_highlight",  # 4.18
	&"modem_sign_warmup", &"modem_trace", &"buy_fly", &"note_flap",  # 4.19
	&"loot_fan", &"loot_pick", &"count_up",  # 4.20
	&"dispatch_type", &"subtitle_bar_in",  # 4.21
	&"drip_grow", &"drip_halo",  # 4.22
	&"beacon_blink", &"city_traffic", &"hq_sign_flicker",  # 4.23
	&"sticky_bump", &"number_roll",  # 4.24
	# Animation pass scope beyond the handoff roadmap (designer, 2026-09-27):
	&"ice_lock_ring", &"decoy_fire", &"raid_hit_effect", &"node_damage_number", &"forecast_stamp_resolve",  # raid execution
	&"card_pickup", &"drag_ghost_follow", &"drop_zone_pulse", &"aim_line_draw", &"target_snap", &"drag_cancel_return",  # card targeting
	&"card_stamp", &"effect_burst", &"card_discard",  # card execution
	&"resolve_beat", &"block_number", &"heal_number", &"hp_drain", &"status_stamp", &"last_turn_reveal",  # end-turn resolution
	&"wheel_respin", &"inner_ring_turn", &"pointer_migrate", &"pointer_orbit", &"enemy_turn_spin",  # spinner movement
	&"drag_pickup", &"drag_follow", &"drop_settle", &"drop_reject", &"loadout_swap", &"crew_assign",  # drag and drop
	&"influence_crossfade", &"influence_spread",  # city influence
	# Animation pass ANIM-2 / ANIM-3 (combat): ids the combat motion added.
	&"resolve_sequence", &"hit_line", &"victory_stamp", &"combat_end_hold", &"wheel_flip", &"dead_wheel_fade",  # ANIM-2
	&"drag_ghost_tilt", &"card_pile", &"hand_reflow", &"ram_tick", &"ram_pending_blink",  # ANIM-3
	# Animation pass ANIM-5 (map, raid, jack and Heat motion):
	&"jack_scanlines", &"raid_step_gap", &"home_lag", &"minimap_pulse", &"select_ring_ease", &"legend_fold",
	# Animation pass ANIM-4 (HQ drag and drop):
	&"drop_stamp", &"market_fly",
	# Animation pass ANIM-6 (screens, menus and ambience): ids the screen motion added.
	&"saved_stamp_in", &"pad_prompts_in", &"focus_tip_in", &"event_outcome_pop", &"event_choice_stamp",
	&"sold_stamp", &"caption_crossfade", &"city_sign_pick",
	# Animation pass ANIM-4b (drag and drop in the run):
	&"drop_buy", &"shred_feed",
	# Animation pass ANIM-R1 (the first fix batch): inline fractions moved into the table,
	# the jack's arrival wait, and the campaign screens' readability motion.
	&"net_creep_recede", &"jack_arrive", &"jack_arrival_wait", &"select_ring_pulse", &"loot_reject", &"home_number_fly", &"influence_mark", &"heat_number_pop", &"heat_banner",
]

@export var entries: Array[UiMotionEntryData] = []


## The entry with `id`, or null. Linear scan (the `Motion` kit keeps its own index).
func find(id: StringName) -> UiMotionEntryData:
	for e in entries:
		if e != null and e.id == id:
			return e
	return null


## Every entry id in file order.
func ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for e in entries:
		if e != null:
			out.append(e.id)
	return out


## Problems with the table: empty slots and repeated ids (each entry checks itself).
func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	var seen := {}
	for e in entries:
		if e == null:
			errors.append("Motion table has an empty entry.")
			continue
		if seen.has(e.id):
			errors.append("Motion id %s appears twice." % e.id)
		seen[e.id] = true
	return errors
