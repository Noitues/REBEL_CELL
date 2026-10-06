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
	&"precision_perfect", &"precision_good_ring", &"precision_weak", &"precision_blink", &"precision_null_static",  # 4.4
	&"card_hover", &"card_play", &"card_draw", &"card_exhaust",  # 4.5
	&"send_it_press", &"send_it_drips", &"resolve_pass", &"resolve_pulse",  # 4.6
	&"number_float", &"number_crit", &"hp_lag",  # 4.7
	&"intent_flip",  # 4.8
	&"rewind_scrub",  # 4.9
	&"pointer_flicker", &"orbit_trail",  # 4.10
	&"enemy_break", &"hub_shatter",  # 4.11
	&"heat_pulse", &"heat_letters_shake", &"poster_stamp",  # 4.12
	&"hq_crt_hum", &"radio_type", &"jack_ring_breathe", &"polaroid_tilt",  # 4.13
	&"site_outline_draw", &"map_camera_ease", &"route_crawl", &"asset_drop",  # 4.14
	&"raid_move", &"turret_trace", &"raid_flip",  # 4.15
	&"route_pulse", &"node_pop", &"visited_dim",  # 4.16
	&"panel_in", &"panel_crt_roll", &"panel_drop",  # 4.17
	&"menu_cursor_blink", &"menu_type", &"menu_highlight",  # 4.18
	&"mainframe_sign_warmup", &"mainframe_trace", &"buy_fly", &"note_flap",  # 4.19
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
	&"jack_arrive", &"jack_arrival_wait", &"select_ring_pulse", &"loot_reject", &"home_number_fly", &"influence_mark", &"heat_number_pop", &"heat_banner",
	# ANIM-R1 combat and input: the SEND IT replay's legibility, refusals, SEND IT's mark,
	# and inline numbers moved into the table.
	&"resolve_landing_hold", &"landing_pulse", &"resolve_result_hold", &"result_caption", &"result_stamp",
	&"number_to_hp", &"hit_flash", &"hit_shake", &"enemy_enter", &"victory_flash", &"boss_phase_flash",
	&"ram_refusal", &"ram_refusal_pop", &"send_it_ready", &"send_it_drips_share", &"drag_ghost_tilt_speed",
	&"toast_note_hold", &"stamp_fade_in",
	# ANIM-R2 city, maps and transitions: the bake fade-in, the jack's CONNECTING line, raid
	# readability, the lasting territory tint, the route target's pulse.
	&"city_bake_fade", &"jack_connect", &"raid_outcome_stagger", &"raid_result_banner", &"asset_drop_stamp", &"influence_tint", &"route_target_pulse",
	# ANIM-R2 combat, events and screens: a hit's absorb, the RAM spend float, the price refusal.
	&"hit_absorb", &"ram_spend_float", &"price_refusal",
	# ANIM-R3 city, raid, jack, heat and route: the drop's camera wait moved into the table.
	&"asset_drop_wait", &"asset_drop_grow", &"forecast_change", &"jack_dissolve",
	# ANIM-R3 combat, input and screens: a hit's outcome where it struck, the forecast kept
	# through the replay (its ticks and its fade), a status landing on its slice.
	&"impact_mark", &"forecast_tick", &"forecast_fade", &"status_mark",
	# ANIM-R4 city, raid, Heat, route and HQ.
	&"forecast_change_fade", &"raid_incoming_hold", &"forecast_road_pulse",
	# ANIM-R4 combat, input and screens: motion shares that were inline (the projectile's
	# flight, the riding number's swap, shrink and PERFECT size, the break's crack, the MAINFRAME
	# tubes' strike and flicker), the two sides' hits one after the other, the RAM refill.
	&"hit_line_flight", &"ride_swap", &"ride_shrink", &"ride_perfect", &"break_crack", &"mainframe_sign_strike", &"mainframe_sign_flicker",
	&"resolve_side_gap", &"resolve_attacker_gap", &"ram_refill_float", &"event_type",
	# ANIM-R5 combat: the lost fight's DEFEAT stamp that stays.
	&"defeat_stamp",
	# ANIM-R5 netrun screens: a flight's landing pulses its top bar tag.
	&"flight_land_pulse",
	# ANIM-R6 rules: a flight's lift and fade shares and a stamp's down and hold shares
	# (were inline in FlightFx).
	&"flight_lift_share", &"flight_fade_share", &"choice_stamp_down_share", &"choice_stamp_hold_share",
	# ANIM-R6 city: inline shares moved into the table (the raid volley's stagger, the Heat
	# pulse's rise).
	&"raid_shot_stagger", &"heat_pulse_rise",
	# ANIM-R6 city: the threats still standing withdraw at a raid's verdict.
	&"raid_threat_withdraw",
	# ANIM-R6 combat: the tutorial's Next pulses while it waits for it.
	&"tutorial_next_pulse",
	# ART-0 E (ported from art-pass W6, ART_BIBLE v2 5.3): the wheel-local T3 bursts that
	# retire the full-screen Perfect and boss-phase flashes.
	&"wheel_burst_perfect", &"wheel_burst_phase",
	# ART-2 2B (wheel attachments and the arena): the won backdrop, the drone bloom, the card-play
	# preview's chevrons and ghosts, the Daemon rack's idle scan.
	&"backdrop_won_lights", &"drone_bloom", &"preview_chevron_chase", &"preview_ghost", &"daemon_rack_scan",
	# ART-2 2C (ART_BIBLE v2 §3.15, §3.18, §3.20): the sticker card's peel and slap, the 0/1
	# shards, the locked effect set, temporary labels, triggers and the Heat city.
	&"card_peel", &"card_slap_ring", &"hit_shards", &"hit_crit_streaks", &"hit_blocked_wall", &"block_wall", &"shield_hex",
	&"heal_inflow", &"evade_token", &"corrupt_apply", &"corrupt_tick", &"drone_deploy", &"drone_attack", &"drone_destroyed",
	&"enemy_defeated_bits", &"phase_change_bits", &"respin_bits", &"nudge_resist_bits", &"ram_gain_bits", &"temp_label",
	&"daemon_trigger", &"firmware_trigger", &"heat_city_beacon", &"heat_city_sweep",
	# ART-0 audit B1: the Heat glitch Options extra (ART_BIBLE v2 5.5).
	&"heat_glitch",

	# ART-1 1B material kit (ART_BIBLE v2 1.2, 6.3; round 3 combined_v2 lifecycle): the CRT
	# terminal, the vinyl sticker, the grease pencil, the holo, the light spill and the bits.
	&"crt_type_on", &"crt_caret_blink", &"crt_hex_scroll",
	&"sticker_slap", &"sticker_peel", &"sticker_dissolve", &"sticker_gloss_sweep", &"sticker_sweep_period", &"sticker_peel_back", &"sticker_corner_flutter",
	&"sticker_hover", &"sticker_press",
	&"pencil_write_on", &"pencil_wipe", &"pencil_glint",
	&"holo_bands", &"light_spill_breathe", &"bits_flight",
	# ART-0 F (ported from art-pass W2 / W8a): the pad focus scale, the refused state, and a
	# modal's open and close (PageTransition.open_modal / close_modal).
	&"focus_scale", &"button_refused", &"modal_in", &"modal_out",
	# ART-10 4C (ART_BIBLE v2 4.13, round 33 ui_chrome): the title's SIMULATE glitch and neon
	# sign loops, the ON AIR ticker.
	&"title_glitch_burst", &"title_sign_flicker", &"on_air_ticker",
	# ART-7 3B (ART_BIBLE v2 4.6): the netrun map's hidden-node reveal and calm Heat, and the
	# jack-in transition's beats (terminal, link rain, CRT collapse, wheel slap and spin, lens).
	&"route_node_reveal", &"route_heat_orbit", &"route_searchlight",
	&"jack_terminal_type", &"jack_link_rain", &"jack_crt_collapse", &"jack_wheel_slap", &"jack_wheel_spin", &"jack_lens",
	&"mainframe_takeover", &"mainframe_rain", &"shop_wheel_spin", &"loot_peel", &"event_cam_noise",  # ART-9 4A
	# ART-6 3A (raid presentation): pencil marks, routes, panels, stickers and the drag.
	&"raid_mark_write", &"raid_mark_hold", &"raid_mark_wipe", &"raid_breached_write", &"raid_bits_burst", &"raid_slow_field", &"raid_ice_grow", &"raid_repair_rise", &"raid_route_write", &"raid_route_wipe", &"raid_dock_circle", &"raid_drag_arrow", &"raid_beacon_idle",
	&"raid_incoming",  # B3 (review section c): the raid interlude's INCOMING transition
	# ART-2 2A (the wheel stack): the screens' loop, the telemetry scroll, the precision landings, the hub states.
	&"wheel_screen_loop", &"wheel_telemetry_scroll", &"precision_latch", &"precision_word", &"precision_stutter", &"hub_defeat_drain", &"hub_lockdown_drain",

	# ART-11 4D (ART_BIBLE v2 §4.8): the campaign lost lock (RansomLock), the audit dossier
	# (AuditDossier); the run end's verdict slaps with 1B's sticker_slap.
	&"ransom_glitch", &"ransom_wipe", &"ransom_padlock", &"ransom_notice_in", &"ransom_verb_stamp", &"ransom_sticker_curl",
	&"ransom_sticker_drop", &"ransom_sticker_stagger", &"ransom_countdown", &"ransom_wipe_hold", &"ransom_cut",
	&"dossier_open", &"dossier_stamp", &"dossier_note", &"dossier_note_stagger",
	&"dossier_poster",  # M14 parity END-03: the won file's CORP DOWN poster
	# ART-9 4B (ART_BIBLE v2 §4.11 / §4.12): the portrait feed's live clock, its blink and
	# talking mouth, DISPATCH's voice trace (PortraitFeed).
	&"portrait_feed", &"portrait_blink", &"portrait_talk", &"dispatch_trace",
	# ART-5 5c city motion (CityMotionLayers): the sky lanes, street traffic, billboards, aviation
	# lights, the Heat / suspicion rig and the day / night crossfade.
	&"sky_lane_cars", &"street_cars", &"holo_billboard", &"aviation_blink", &"searchlight_sweep", &"chopper_orbit",
	&"drone_orbit", &"police_strobe", &"alarm_beacon", &"heat_node_light", &"city_light_fade",
	# ART-8 8w Central Server gate (bible 4.9): the keycards' stagger, the socket's ring, BREACH turning pink.
	&"gate_keycard_stagger", &"gate_socket_ring", &"gate_breach_ready",
	# ART-5 5e: the Cell's blackout reveal on the Grid's city (CityView3D.set_cell_reveal).
	&"cell_fist_reveal",
	# ABANDON-QUIT (designer ruling 2026-10-05): the hold on an abandon dialog's verb (AbandonDialog).
	&"dialog_hold_confirm",
]

## ANIM-R5: what switching an entry off (`enabled = false`) does, by kind of entry.
## - An entry with a motion of its own (played through Motion.run / fade / pop / ... or
##   gated on Motion.live): off, it shows its end state at once (live() is false).
## - A part of another motion that a view reads as a number (a share of its time, a gap,
##   a riding size): OFF_PARTS below. Off, Motion.seconds and Motion.delay_of give 0 (the
##   part takes no time) and Motion.amplitude gives the listed value (the part shows no
##   motion: 0 for a share, px or frames; 1 for a scale).
## - A tuning of another entry with nothing of its own to switch off: ALWAYS_ON below.
##   validate() refuses it switched off (switch off the entry it tunes instead).
const OFF_PARTS: Dictionary = {
	&"hit_line_flight": 0.0, &"ride_swap": 0.0, &"ride_shrink": 1.0, &"ride_perfect": 1.0,
	&"break_crack": 0.0, &"mainframe_sign_strike": 0.0, &"mainframe_sign_flicker": 0.0,
	&"forecast_change_fade": 0.0, &"resolve_side_gap": 0.0, &"resolve_attacker_gap": 0.0,
	&"drag_ghost_tilt": 0.0, &"hit_freeze": 0.0, &"stamp_fade_in": 0.0,
	# ANIM-R6 city: the gap between raid steps and the raid volley's stagger (a share).
	&"raid_step_gap": 0.0, &"raid_shot_stagger": 0.0,
	# ART-11 4D: the lock's sticker stagger and the dossier's note stagger (off = together).
	&"ransom_sticker_stagger": 0.0, &"dossier_note_stagger": 0.0,
}
## ANIM-R5: tunings of another entry (see OFF_PARTS): never switched off.
const ALWAYS_ON: Array[StringName] = [&"drag_ghost_tilt_speed", &"send_it_drips_share", &"heat_pulse_rise",
	&"flight_lift_share", &"flight_fade_share", &"choice_stamp_down_share", &"choice_stamp_hold_share", &"sticker_sweep_period", &"sticker_peel_back"]

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
		if not e.enabled and ALWAYS_ON.has(e.id):
			errors.append("Motion %s tunes another entry and can't be switched off (switch that entry off)." % e.id)
	return errors
