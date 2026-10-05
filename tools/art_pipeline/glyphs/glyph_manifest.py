"""ART-1 1C: the production glyph list, in atlas order.

Each row: (atlas name, source, source id, meaning).
  source "r40"      -> art-concepts-r43:docs/concepts/round40_hub_inner_ring/scripts/slicelib.glyph_mask(id)
                       (chains round 40 -> 39 -> 38 -> 17 -> 16 ... so round 17 glyphs come out unchanged)
  source "priority" -> round18_corp_wheels/scripts/glyph_priority.priority()
  source "fw"       -> round34_firmware_daemons/scripts/fwlib.ICONS[id] (firmware glyphs and Daemon sigils)
  source "pending"  -> the stand-in for ids whose art does not exist yet (not a bible glyph)

Order: docs/art_reference/glyphs/index.txt (round 17) with the program names, placeholders left out and
JUDGEMENT replaced by PRIORITY in its slot (round 18); then hubs, segments (bible 3.5 "join the same
atlas"), Firmware and Daemons (round 34), the Exploit kinds (round 38/39) and the pending stand-in.
"""

ROWS = [
    # --- slice programs (round 34 names, round 17 glyphs)
    ("slice_shim", "r40", "EXPLOIT", "ATTACK: damage (dagger)"),
    ("slice_overflow", "r40", "ZERO-DAY", "CRIT: big damage (burst)"),
    ("slice_defrag", "r40", "FIREWALL", "DEFEND: block (wall + flame)"),
    ("slice_sandbox", "r40", "SANDBOX", "SHIELD: persists (sand pile)"),
    ("slice_detour", "r40", "PROXY", "EVADE: dodge next hit (chevrons)"),
    ("slice_hotfix", "r40", "PATCH", "HEAL: restore HP (crossed band-aids)"),
    ("slice_infect", "r40", "BIOHAZ", "AFFLICT: status on target (biohazard)"),
    ("slice_trojan", "r40", "TROJAN", "DEPLOY: dock drones (horse)"),
    ("slice_null", "r40", "NULL", "MISS: nothing (1/0)"),
    # --- corporation specials
    ("special_priority", "priority", "PRIORITY", "Meridian: drains RAM (alarm beacon); replaces JUDGEMENT"),
    ("special_citation", "r40", "CITATION", "Halcyon: plants PARASITE (receipt)"),
    ("special_solar_flare", "r40", "FLARE", "Orbital: overclock then corrupt (sun on the horizon)"),
    ("special_dose", "r40", "DOSE", "Solace: corrupts (capsule)"),
    ("special_weight", "r40", "WEIGHT", "+1 resistance (anvil); was INERTIA"),
    ("special_drone", "r40", "DRONE", "satellite docked on a slice (quad-rotor)"),
    # --- statuses
    ("status_corrupted", "r40", "ST_CORRUPTED", "slice output broken (hurts)"),
    ("status_parasite", "r40", "ST_PARASITE", "half output (hurts)"),
    ("status_overclocked", "r40", "ST_OVERCLOCKED", "1.5x once, then CORRUPTED"),
    ("status_encrypted", "r40", "ST_ENCRYPTED", "absorbs the next status"),
    ("status_cleanse", "r40", "ST_CLEANSE", "ESC keycap"),
    # --- slice states
    ("state_frozen", "r40", "ST_FROZEN", "slice skips / is held"),
    ("state_locked", "r40", "ST_LOCKED", "slice can't be changed"),
    ("state_burning", "r40", "ST_BURNING", "loses value each turn"),
    ("state_empowered", "r40", "ST_EMPOWERED", "boosted next trigger"),
    # --- pictograms
    ("picto_spin", "r40", "PI_SPIN_CW", "spin n ticks clockwise"),
    ("picto_spin_ccw", "r40", "PI_SPIN_CCW", "spin n anticlockwise"),
    ("picto_momentum", "r40", "PI_MOMENTUM", "big 2 runs; 5 if you spin first"),
    ("picto_respin", "r40", "PI_RESPIN", "respin to random tick"),
    ("picto_nudge", "r40", "PI_NUDGE", "free +-1 tick, either way"),
    ("picto_nudge_inner", "r40", "PI_NUDGE_INNER", "+-1 on the inner ring"),
    ("picto_free_nudge", "r40", "PI_FREE", "next n nudges free"),
    ("picto_again", "r40", "PI_AGAIN", "nudges trigger twice"),
    ("picto_flip", "r40", "PI_FLIP", "mirror the wheel"),
    ("picto_snap", "r40", "PI_SNAP", "snap to slice centre"),
    ("picto_ring_lock", "r40", "PI_RING_LOCK", "inner ring holds"),
    ("picto_perfect", "r40", "PI_PERFECT", "perfect mark (RAM+)"),
    ("picto_draw", "r40", "PI_DRAW", "draw n cards"),
    ("picto_ram", "r40", "PI_RAM", "gain / lose RAM"),
    ("picto_breach", "r40", "PI_BREACH", "disable the hub"),
    ("picto_undock", "r40", "PI_UNDOCK", "move a satellite"),
    ("picto_block", "r40", "PI_BLOCK", "gain n block"),
    ("picto_all_targets", "r40", "PI_ALL", "every enemy"),
    ("picto_take_dmg", "r40", "PI_SELF_DMG", "you take n"),
    ("picto_exhaust", "r40", "PI_EXHAUST", "card torn in two"),
    ("picto_target", "r40", "PI_RETICLE", "aim reticle"),
    ("picto_no_damage", "r40", "PI_REFUSAL", "refused / blocked"),
    ("picto_hp", "r40", "PI_HP", "health"),
    # --- hub cores (round 38-40, LOCKED in bible 3.3)
    ("hub_breaker_core", "r40", "CORE_breaker_core", "crowbar striking a spiderweb of glass cracks"),
    ("hub_wrecker_core", "r40", "CORE_wrecker_core", "sledgehammer"),
    ("hub_ghost_core", "r40", "CORE_ghost_core", "hood with mesh eyes"),
    ("hub_phantom_core", "r40", "CORE_phantom_core", "mask (the hub draws the echo trail as motion)"),
    ("hub_phantom_echo", "r40", "CORE_phantom_echo", "mask + echo outlines: Phantom's static icon"),
    ("hub_rig_core", "r40", "CORE_rig_core", "firmware chip dropping into a socket"),
    ("hub_overclock_core", "r40", "CORE_overclock_core", "RPM gauge, needle in the red"),
    ("hub_swarm_core", "r40", "CORE_swarm_core", "three linked drones"),
    ("hub_hive_core", "r40", "CORE_hive_core", "hex cell holding 4 nodes"),
    ("hub_compliance_lock", "r40", "HUB_compliance_lock", "rubber stamp"),
    ("hub_customs_seal", "r40", "HUB_priority_routing", "express arrow overtaking two lanes (was Priority Routing)"),
    ("hub_emergency_powers", "r40", "HUB_emergency_powers", "siren dome"),
    ("hub_station_keeping", "r40", "HUB_station_keeping", "satellite"),
    ("hub_auto_renew", "r40", "HUB_auto_renew", "renew loop round a plus"),
    ("hub_root_access", "r40", "HUB_root_access", "terminal with #_"),
    # --- inner-ring segments (round 38, bible 3.10)
    ("seg_x2", "r40", "SEG_x2", "x2"),
    ("seg_pierce", "r40", "SEG_pierce", "arrow through a brick slab"),
    ("seg_corrupt", "r40", "SEG_corrupt", "glitched block"),
    ("seg_anchor", "r40", "SEG_anchor", "anchor"),
    ("seg_accelerator", "r40", "SEG_accelerator", "gear + speed lines"),
    ("seg_echo", "r40", "SEG_echo", "block + two arcs"),
    ("seg_blank", "r40", "SEG_blank", "dash"),
    # --- Firmware effect glyphs (round 33/34, bible 3.9)
    ("fw_patch_plus", "fw", "patch_plus", "double plus"),
    ("fw_hardened", "fw", "hardened", "armoured hex with ***"),
    ("fw_burner", "fw", "burner", "gas ring"),
    ("fw_leech", "fw", "leech", "fanged drop"),
    ("fw_mirror", "fw", "mirror", "mirror"),
    ("fw_shunt", "fw", "shunt", "fork with two arrowheads"),
    ("fw_overvolt", "fw", "overvolt", "bolt"),
    ("fw_bulkhead", "fw", "bulkhead", "blast door"),
    ("fw_siphon", "fw", "siphon", "pipe"),
    ("fw_static_coat", "fw", "static_coat", "zig-zag shield"),
    ("fw_barbed_wire", "fw", "barbed_wire", "barbed wire"),
    ("fw_recycler", "fw", "recycler", "three-arrow triangle"),
    ("fw_counterstrike", "fw", "counterstrike", "two-way arrows"),
    ("fw_nanite_mesh", "fw", "nanite_mesh", "hex cluster"),
    ("fw_power_cell", "fw", "power_cell", "battery"),
    ("fw_tracer", "fw", "tracer", "tracer round"),
    ("fw_skimmer", "fw", "skimmer", "coin stack"),
    ("fw_coolant_loop", "fw", "coolant_loop", "radiator coil"),
    # --- Daemon sigils (round 33/34, bible 3.13)
    ("daemon_clean_signal", "fw", "clean_signal", "Daemon sigil"),
    ("daemon_kernel_sync", "fw", "kernel_sync", "Daemon sigil"),
    ("daemon_zero_day", "fw", "zero_day", "Daemon sigil"),
    ("daemon_botnet_seed", "fw", "botnet_seed", "Daemon sigil"),
    ("daemon_adrenal_loop", "fw", "adrenal_loop", "Daemon sigil"),
    ("daemon_cascade", "fw", "cascade", "Daemon sigil"),
    ("daemon_fault_tolerance", "fw", "fault_tolerance", "Daemon sigil"),
    ("daemon_fail_forward", "fw", "fail_forward", "Daemon sigil"),
    ("daemon_stolen_intent", "fw", "stolen_intent", "Daemon sigil"),
    ("daemon_twin_pointer", "fw", "twin_pointer", "Daemon sigil"),
    ("daemon_warm_boot", "fw", "warm_boot", "Daemon sigil"),
    ("daemon_shield_cache", "fw", "shield_cache", "Daemon sigil"),
    ("daemon_idle_armor", "fw", "idle_armor", "Daemon sigil"),
    ("daemon_static_field", "fw", "static_field", "Daemon sigil"),
    ("daemon_linked_bus", "fw", "linked_bus", "Daemon sigil"),
    ("daemon_tuning_fork", "fw", "tuning_fork", "Daemon sigil"),
    ("daemon_feedback_loop", "fw", "feedback_loop", "Daemon sigil"),
    ("daemon_salvager", "fw", "salvager", "Daemon sigil"),
    ("daemon_field_medic", "fw", "field_medic", "Daemon sigil"),
    ("daemon_bounty_code", "fw", "bounty_code", "Daemon sigil"),
    ("daemon_rack_skimmer", "fw", "rack_skimmer", "Daemon sigil"),
    ("daemon_cold_exit", "fw", "cold_exit", "Daemon sigil"),
    ("daemon_scrubber", "fw", "scrubber", "Daemon sigil"),
    ("daemon_log_wiper", "fw", "log_wiper", "Daemon sigil"),
    # --- Exploit kinds (round 38 exploit_items / round 39 exploits_v2: INTEL binoculars, BREACH key;
    #     VIRUS reuses status_corrupted)
    ("exploit_intel", "r40", "RECON", "INTEL Exploit: binoculars"),
    ("exploit_breach", "r40", "KEY", "BREACH Exploit: key"),
    # --- stand-in for ids with no art yet (DECISIONS open question)
    ("pending", "pending", "", "no art yet: neutral rounded square"),
]

NAMES = [r[0] for r in ROWS]
