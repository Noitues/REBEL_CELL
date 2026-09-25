"""M7 pools (GAP_ANALYSIS P1 6-7): shared cards to 60, Firmware to 18, Daemons to 24,
defense assets to 8, shop slices to 12, Terminal events to 40. Only existing effect types.
EffectType: DMG 0, BLOCK 1, SHIELD 2, EVADE 3, STATUS 4, NUDGE 5, SPIN 6, FLIP 7, RESPIN 8,
FREEZE 9, RESIST 10, BREACH 11, RAM 12, HEAL 14, CLEANSE 15, SNAP 16, DRAW 17,
DOUBLE_NUDGE 20, HEAT 21, CYCLES 22, SCHEMATICS 23, CUSTOM 24.
Target: SELF 0, OWN_WHEEL 1, TARGET_WHEEL 2, POINTER_TARGET 3, ALL_ENEMIES 4, CAMPAIGN 6.
WheelTarget OWN 0, ENEMY 1, ANY 2. Status CORRUPTED 1, OVERCLOCKED 2, ENCRYPTED 3, PARASITE 4.
SlicePick UNDER_POINTER 0, RANDOM_NON_MISS 1, CHOSEN 2. Ring OUTER 0, INNER 1, WHOLE 2.
Trigger COMBAT_START 1, TURN_START 2, CARD_PLAYED 3, NUDGE 4, SLICE_TRIGGER 5, PERFECT 6,
MISS_SLICE 7, TURN_END 8, COMBAT_END 9, RACK 10, NETRUN_COMPLETE 11. Tier PARTIAL 0, GOOD 1,
PERFECT 2. SliceType ATK 0, CRIT 1, DEF 2, EVADE 3, SHIELD 4, DEPLOY 5, HEAL 6, AFFLICT 7, MISS 8."""
import os
import re
HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "gen_classes.py"), encoding="utf-8").read()
exec(_src[:_src.index("# ---- standalone ring segments")])

CAL = "res://scripts/core/handlers/calibrate_handler.gd"
written = {"cards": 0, "firmware": 0, "daemons": 0, "assets": 0, "slices": 0, "events": 0}


def fx(r, i, type_, target, amount=None, **kw):
    return r.effect("fx%d" % i, type_, target, amount, **kw)


# ---- Shared cards ---------------------------------------------------------------------------
# (id, name, description, ram, cycles, wheel_target, exhaust, rarity, [effect tuples])
# effect tuple: (type, target, amount, {extra fields})
CARDS = [
    # Rotation
    ("whirl", "Whirl", "Spin a wheel 7 ticks.", 2, 55, 2, False, 0, [(6, 2, 7, {"ring_scope": 2})]),
    ("backspin", "Backspin", "Spin a wheel 9 ticks counter-clockwise.", 2, 60, 2, False, 0, [(6, 2, -9, {"ring_scope": 2})]),
    ("flick", "Flick", "Spin a wheel 1 tick.", 0, 50, 2, False, 0, [(6, 2, 1, {"ring_scope": 2})]),
    ("spin_cycle", "Spin Cycle", "Spin a wheel 12 ticks.", 3, 65, 2, False, 1, [(6, 2, 12, {"ring_scope": 2})]),
    ("gear_mesh", "Gear Mesh", "Spin the target and your own wheel 5 ticks.", 2, 65, 1, False, 1,
     [(6, 2, 5, {"ring_scope": 2}), (6, 1, 5, {"ring_scope": 2})]),
    ("inner_drift", "Inner Drift", "Move your inner ring 3 ticks.", 0, 50, 0, False, 0, [(5, 1, 3, {"ring_scope": 1})]),
    ("ratchet", "Ratchet", "Move your inner ring 8 ticks.", 2, 55, 0, False, 0, [(5, 1, 8, {"ring_scope": 1})]),
    ("tailspin", "Tailspin", "Spin a wheel 4 ticks and draw 1 card.", 2, 65, 2, False, 1,
     [(6, 2, 4, {"ring_scope": 2}), (17, 0, 1, {})]),
    # Precision
    ("tap_tap", "Tap Tap", "Three +-1 nudges on one ring.", 2, 60, 2, False, 0, [(5, 2, 3, {"ring_scope": 0})]),
    ("feather_touch", "Feather Touch", "One +-1 nudge.", 0, 50, 2, False, 0, [(5, 2, 1, {"ring_scope": 0})]),
    ("inner_snap", "Inner Snap", "Move your inner ring to the nearest segment centre.", 1, 60, 0, False, 1, [(16, 1, None, {"ring_scope": 1})]),
    ("lock_on", "Lock On", "Move your outer ring to the nearest slice centre (Perfect). Exhaust.", 0, 60, 0, True, 1, [(16, 1, None, {"ring_scope": 0})]),
    ("deep_calibrate", "Deep Calibrate", "Your next 3 nudges this turn are free. Exhaust.", 1, 60, 0, True, 1,
     [(24, 0, 3, {"custom_handler": "CAL"})]),
    ("overclock_nudges", "Nudge Driver", "Nudge cards trigger twice next turn.", 1, 65, 0, False, 2, [(20, 0, None, {})]),
    # Enemy control
    ("deep_strip", "Deep Strip", "Remove 4 resistance from the target.", 2, 65, 1, False, 1, [(10, 2, -4, {})]),
    ("short_circuit", "Short Circuit", "Disable the target Hub for 2 turns. Exhaust.", 3, 75, 1, True, 2, [(11, 2, 2, {})]),
    ("double_jam", "Double Jam", "Nudge an enemy wheel +-1 twice, ignoring resistance.", 3, 70, 1, False, 1,
     [(5, 2, 2, {"ring_scope": 0, "multiplier": "0.0"})]),
    ("cold_snap", "Cold Snap", "The target skips its next respin and you gain 3 block.", 3, 70, 1, False, 1,
     [(9, 2, None, {"ring_scope": 2}), (1, 0, 3, {})]),
    ("corrupt_packet", "Corrupt Packet", "CORRUPT the enemy slice under your pointer.", 1, 60, 1, False, 0,
     [(4, 2, None, {"status": 1, "slice_pick": 0})]),
    ("malware_drop", "Malware Drop", "CORRUPT a random non-Miss slice of the target.", 1, 55, 1, False, 0,
     [(4, 2, None, {"status": 1, "slice_pick": 1})]),
    ("leech_worm", "Leech Worm", "The enemy slice under your pointer gets a PARASITE (half output). Exhaust.", 3, 75, 1, True, 2,
     [(4, 2, None, {"status": 4, "slice_pick": 0})]),
    ("flip_switch", "Flip Switch", "Flip your own wheel.", 2, 60, 0, False, 0, [(7, 1, None, {"ring_scope": 2})]),
    ("reroll", "Reroll", "Respin a wheel to a random tick.", 2, 55, 2, False, 0, [(8, 2, None, {"ring_scope": 2})]),
    # Defence
    ("firewall", "Firewall", "Gain 6 block.", 1, 50, 0, False, 0, [(1, 0, 6, {})]),
    ("bulwark", "Bulwark", "Gain 12 block.", 2, 60, 0, False, 1, [(1, 0, 12, {})]),
    ("shield_wall", "Shield Wall", "Gain 4 shield.", 1, 55, 0, False, 0, [(2, 0, 4, {})]),
    ("duck", "Duck", "Evade the next incoming attack this turn.", 2, 60, 0, False, 1, [(3, 0, 1, {})]),
    ("patch_up", "Patch Up", "Heal 6. Exhaust.", 2, 60, 0, True, 0, [(14, 0, 6, {})]),
    ("sanitize", "Sanitize", "Remove CORRUPTED from a chosen slice and gain 3 block.", 1, 55, 0, False, 0,
     [(15, 1, None, {"slice_pick": 2}), (1, 0, 3, {})]),
    ("armor_plate", "Armor Plate", "ENCRYPT a chosen slice and gain 4 block.", 2, 60, 0, False, 1,
     [(4, 1, None, {"status": 3, "slice_pick": 2}), (1, 0, 4, {})]),
    ("stim_patch", "Stim Patch", "Heal 12. Exhaust.", 3, 70, 0, True, 2, [(14, 0, 12, {})]),
    # Utility
    ("hot_patch", "Hot Patch", "OVERCLOCK a chosen slice of your wheel: 1.5x on its next trigger, then it becomes CORRUPTED.", 2, 65, 0, False, 1,
     [(4, 1, None, {"status": 2, "slice_pick": 2})]),
    ("power_tap", "Power Tap", "Gain 2 RAM and take 3 damage.", 0, 55, 0, False, 0, [(12, 0, 2, {}), (0, 0, 3, {})]),
    ("data_surge", "Data Surge", "Draw 3 cards.", 2, 65, 0, False, 1, [(17, 0, 3, {})]),
    ("scrap_code", "Scrap Code", "Gain 1 RAM and draw 1 card. Exhaust.", 0, 50, 0, True, 0, [(12, 0, 1, {}), (17, 0, 1, {})]),
    ("static_shock", "Static Shock", "Deal 4 damage to the target.", 1, 55, 1, False, 0, [(0, 2, 4, {})]),
    ("overload", "Overload", "Deal 10 damage to the target and take 4. Exhaust.", 3, 70, 1, True, 1, [(0, 2, 10, {}), (0, 0, 4, {})]),
    ("arc_flash", "Arc Flash", "Deal 3 damage to every enemy.", 2, 65, 1, False, 1, [(0, 4, 3, {})]),
]

for cid, name, desc, ram, cyc, wt, exhaust, rarity, effects in CARDS:
    r = Res("CardData", "res://scripts/data/card_data.gd")
    fx_script = r.script(S_EFFECT)
    subs = []
    for i, (t, tgt, amt, extra) in enumerate(effects):
        kw = dict(extra)
        if kw.get("custom_handler") == "CAL":
            kw["custom_handler"] = r.script(CAL)
        subs.append(fx(r, i, t, tgt, amt, **kw))
    r.main = ['id = &"%s"' % cid, 'display_name = "%s"' % name, 'description = "%s"' % desc, "rarity = %d" % rarity,
              "ram_cost = %d" % ram, "cycle_cost = %d" % cyc, "wheel_target = %d" % wt, "effects = " + arr(fx_script, subs)]
    if exhaust:
        r.main.append("exhaust = true")
    r.write("content/cards/%s.tres" % cid, "Shared card (M7 pool, decision 2026-09-24).")
    written["cards"] += 1

# ---- Firmware -------------------------------------------------------------------------------------
# (id, name, desc, rarity, cycles, allowed types, output multiplier, [(trigger, min_tier, limit, [effects])])
FIRMWARE = [
    ("overvolt", "Overvolt", "ATK and CRIT slices: output +25%.", 0, 90, [0, 1], 1.25, []),
    ("bulkhead", "Bulkhead", "DEF and SHIELD slices: output +50%.", 0, 90, [2, 4], 1.5, []),
    ("siphon", "Siphon", "ATK slice heals you 2 on Good or better.", 0, 100, [0], 1.0, [(5, 1, 0, [(14, 0, 2)])]),
    ("static_coat", "Static Coat", "DEF slice also grants 2 shield.", 0, 100, [2], 1.0, [(5, 0, 0, [(2, 0, 2)])]),
    ("barbed_wire", "Barbed Wire", "DEF slice also deals 2 damage to the pointer target.", 0, 100, [2], 1.0, [(5, 0, 0, [(0, 3, 2)])]),
    ("tracer", "Tracer", "ATK or CRIT slice strips 1 resistance from the target on a Perfect.", 1, 120, [0, 1], 1.0, [(5, 2, 0, [(10, 3, -1)])]),
    ("coolant_loop", "Coolant Loop", "Once per combat, a Perfect on this slice lowers Heat by 1.", 2, 150, [], 1.0, [(5, 2, 1, [(21, 6, -1)])]),
    ("skimmer", "Skimmer", "ATK slice: +3 Cycles on a Perfect (twice per combat).", 1, 120, [0], 1.0, [(5, 2, 2, [(22, 6, 3)])]),
    ("counterstrike", "Counterstrike", "EVADE slice also deals 4 damage to the pointer target.", 1, 110, [3], 1.0, [(5, 0, 0, [(0, 3, 4)])]),
    ("nanite_mesh", "Nanite Mesh", "HEAL slice: output +50%, and it cleanses itself after resolving.", 1, 110, [6], 1.5, [(5, 0, 0, [(15, 1, None, {"slice_pick": 0})])]),
    ("power_cell", "Power Cell", "SHIELD slice also restores 1 RAM.", 1, 110, [4], 1.0, [(5, 0, 0, [(12, 0, 1)])]),
    ("recycler", "Recycler", "The Miss slice restores 2 RAM when it resolves.", 0, 90, [8], 1.0, [(5, 0, 0, [(12, 0, 2)])]),
]
for fid, name, desc, rarity, cyc, types, mult, tes in FIRMWARE:
    r = Res("FirmwareData", "res://scripts/data/firmware_data.gd")
    te_script = r.script(S_TE)
    te_list = []
    for j, (trig, tier, limit, effs) in enumerate(tes):
        subs = []
        for i, e in enumerate(effs):
            t, tgt, amt = e[0], e[1], e[2]
            kw = e[3] if len(e) > 3 else {}
            subs.append(r.effect("fx%d_%d" % (j, i), t, tgt, amt, **kw))
        fields = [("trigger", trig), ("min_tier", tier)]
        if limit:
            fields.append(("limit_per_combat", limit))
        fields.append(("effects", arr(r.script(S_EFFECT), subs)))
        te_list.append(r.sub("te%d" % j, S_TE, fields))
    r.main = ['id = &"%s"' % fid, 'display_name = "%s"' % name, 'description = "%s"' % desc, "rarity = %d" % rarity,
              "cycle_cost = %d" % cyc, "allowed_slice_types = Array[int]([%s])" % ", ".join(str(t) for t in types)]
    if mult != 1.0:
        r.main.append("output_multiplier = %s" % mult)
    if te_list:
        r.main.append("triggered_effects = " + arr(te_script, te_list))
    r.write("content/firmware/%s.tres" % fid, "Firmware (M7 pool, decision 2026-09-24).")
    written["firmware"] += 1

# ---- Daemons ---------------------------------------------------------------------------------------
# (id, name, desc, rarity, cycles, trigger, min_tier, consecutive, [effects])
DAEMONS = [
    ("warm_boot", "Warm Boot", "Start every combat with +2 RAM.", 1, 180, 1, 0, 1, [(12, 0, 2)]),
    ("shield_cache", "Shield Cache", "Start every combat with 5 shield.", 1, 180, 1, 0, 1, [(2, 0, 5)]),
    ("idle_armor", "Idle Armor", "Gain 2 block at the start of every turn.", 1, 190, 2, 0, 1, [(1, 0, 2)]),
    ("adrenal_loop", "Adrenal Loop", "Each Perfect heals 2.", 1, 200, 6, 2, 1, [(14, 0, 2)]),
    ("fail_forward", "Fail Forward", "The Miss slice restores 2 RAM.", 1, 170, 7, 0, 1, [(12, 0, 2)]),
    ("feedback_loop", "Feedback Loop", "Every card you play deals 1 damage to every enemy.", 2, 230, 3, 0, 1, [(0, 4, 1)]),
    ("tuning_fork", "Tuning Fork", "Every nudge action grants 1 block.", 1, 170, 4, 0, 1, [(1, 0, 1)]),
    ("static_field", "Static Field", "At the start of every turn, deal 1 damage to every enemy.", 2, 220, 2, 0, 1, [(0, 4, 1)]),
    ("cascade", "Cascade", "Two Perfects in a row: +1 RAM.", 1, 190, 6, 2, 2, [(12, 0, 1)]),
    ("salvager", "Salvager", "+5 Cycles after every won fight.", 0, 160, 9, 0, 1, [(22, 6, 5)]),
    ("field_medic", "Field Medic", "Heal 4 after every won fight.", 0, 160, 9, 0, 1, [(14, 0, 4)]),
    ("bounty_code", "Bounty Code", "+1 Schematic banked after every won fight.", 2, 240, 9, 0, 1, [(23, 6, 1)]),
    ("rack_skimmer", "Rack Skimmer", "Capturing a Server Rack banks 3 extra Schematics.", 1, 200, 10, 0, 1, [(23, 6, 3)]),
    ("log_wiper", "Log Wiper", "Finishing a netrun lowers Heat by 1.", 2, 240, 11, 0, 1, [(21, 6, -1)]),
]
for did, name, desc, rarity, cyc, trig, tier, consec, effs in DAEMONS:
    r = Res("DaemonData", "res://scripts/data/daemon_data.gd")
    subs = [r.effect("fx%d" % i, t, tgt, amt) for i, (t, tgt, amt) in enumerate(effs)]
    fields = [("trigger", trig), ("min_tier", tier)]
    if consec > 1:
        fields.append(("consecutive_required", consec))
    fields.append(("effects", arr(r.script(S_EFFECT), subs)))
    te = r.sub("te", S_TE, fields)
    r.main = ['id = &"%s"' % did, 'display_name = "%s"' % name, 'description = "%s"' % desc, "rarity = %d" % rarity,
              "cycle_cost = %d" % cyc, "triggered_effects = " + arr(r.script(S_TE), [te])]
    r.write("content/daemons/%s.tres" % did, "Daemon (M7 pool, decision 2026-09-24).")
    written["daemons"] += 1

# ---- Defense assets ----------------------------------------------------------------------------------
# (id, name, desc, type, integrity, damage, range, shots, targeting, delay, pull, rarity)
ASSETS = [
    ("railgun", "Railgun", "8 damage, range 2, targets the hardest-hitting threat.", 0, 8, 8, 2, 1, 2, 0, 0, 2),
    ("flak_array", "Flak Array", "2 damage three times a step, range 1, targets the weakest threat.", 0, 10, 2, 1, 3, 1, 0, 0, 1),
    ("sentry", "Sentry", "3 damage twice a step on its own node only. Sturdy.", 0, 16, 3, 0, 2, 0, 0, 0, 0),
    ("tar_pit", "Tar Pit", "Holds a threat for 3 steps. Fragile.", 1, 6, 0, 0, 1, 0, 3, 0, 1),
    ("honeypot_node", "Honeypot", "Pull 5: strongly attracts threat routing.", 2, 8, 0, 0, 1, 0, 0, 5, 1),
]
for aid, name, desc, atype, integ, dmg, rng_, shots, targ, delay, pull, rarity in ASSETS:
    r = Res("DefenseAssetData", "res://scripts/data/defense_asset_data.gd")
    r.main = ["asset_type = %d" % atype, 'id = &"%s"' % aid, 'display_name = "%s"' % name, 'description = "%s"' % desc,
              "rarity = %d" % rarity, "integrity = %d" % integ, "damage = %d" % dmg, "range_hops = %d" % rng_,
              "shots_per_step = %d" % shots, "targeting = %d" % targ, "delay_steps = %d" % delay, "decoy_pull = %d" % pull]
    r.write("content/assets/%s.tres" % aid, "Defense asset (M7 pool, decision 2026-09-24).")
    written["assets"] += 1

# ---- New shop slices ------------------------------------------------------------------------------------
for sid, name, stype, rule, out in [("shield_8", "Shield 8", 4, 0, 8), ("evade_2", "Evade 2", 3, 0, 2)]:
    path = "content/slices/%s.tres" % sid
    text = ('[gd_resource type="Resource" script_class="SliceData" format=3]\n\n'
            '[ext_resource type="Script" path="res://scripts/data/slice_data.gd" id="1"]\n\n'
            '[resource]\nscript = ExtResource("1")\nid = &"%s"\ndisplay_name = "%s"\nslice_type = %d\ntarget_rule = %d\nbase_output = %d\n'
            % (sid, name, stype, rule, out))
    open(path, "w", encoding="utf-8", newline="\n").write(text)
    print("wrote", path)
    written["slices"] += 1

p = "content/config/campaign_config.tres"
s = open(p, encoding="utf-8").read()
if "sl_shield_8" not in s:
    new_ext = "".join('[ext_resource type="Resource" path="res://content/slices/%s.tres" id="sl_%s"]\n' % (x, x)
                      for x in ["atk_10", "crit_16", "heal_6", "shield_8", "evade_2"] if ('id="sl_%s"' % x) not in s)
    first = s.index("[ext_resource")
    s = s[:first] + new_ext + s[first:]
    s = s.replace('ExtResource("sl_evade_1")])', 'ExtResource("sl_evade_1"), ExtResource("sl_atk_10"), ExtResource("sl_crit_16"), ExtResource("sl_heal_6"), ExtResource("sl_shield_8"), ExtResource("sl_evade_2")])', 1)
    m = re.search(r"load_steps=(\d+)", s)
    s = s.replace(m.group(0), "load_steps=%d" % (int(m.group(1)) + new_ext.count("[ext_resource")), 1)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("patched shop slices")

# ---- Terminal events -------------------------------------------------------------------------------------
# choice: (label, result, cycle_cost, hp_cost, [(type, target, amount)], reward_path or None)
EV = []


def event(eid, title, text, choices, speaker=0, corp="solace", min_tier=1, weight=1.0):
    EV.append((eid, title, text, choices, speaker, corp, min_tier, weight))


LEAVE = ("Walk on", "Nothing ventured. Nothing flagged.", 0, 0, [], None)
C = "res://content/cards/%s.tres"
F = "res://content/firmware/%s.tres"
D = "res://content/daemons/%s.tres"
A = "res://content/assets/%s.tres"

event("ev_wellness_kiosk", "Wellness Kiosk",
      "A Solace kiosk offers a free wellness scan. The fine print is longer than the kiosk.",
      [("Take the scan (+10 HP, +2 Heat)", "It heals you, then files you under 'engaged customer'.", 0, 0, [(14, 0, 10), (21, 6, 2)], None),
       ("Jam the scanner (+15 Cycles)", "Coins spill out of the refund slot.", 0, 3, [(22, 6, 15)], None), LEAVE])
event("ev_expired_samples", "Expired Samples",
      "A crate of expired Solace stims, stamped NOT FOR RESALE.",
      [("Pop one (+6 HP)", "Past the date, still in the vein.", 0, 0, [(14, 0, 6)], None),
       ("Resell them (+20 Cycles, +1 Heat)", "A street medic pays in cash and doesn't ask.", 0, 0, [(22, 6, 20), (21, 6, 1)], None), LEAVE])
event("ev_billing_loop", "Billing Loop",
      "A billing process is stuck charging the same account forever. You could redirect it.",
      [("Redirect it to the Cell (+30 Cycles, +3 Heat)", "Money arrives. So does attention.", 0, 0, [(22, 6, 30), (21, 6, 3)], None),
       ("Kill the loop (-1 Heat)", "Somewhere a family stops being charged. Nobody at Solace notices.", 0, 0, [(21, 6, -1)], None), LEAVE])
event("ev_patient_records", "Patient Records",
      "A records terminal left logged in. Thousands of leashes, each one a monthly fee.",
      [("Copy the index (+2 Schematics banked)", "Useful maps of who owes what.", 0, 0, [(23, 6, 2)], None),
       ("Wipe a street's debt (-2 Heat, 5 damage)", "The terminal bites back, but the street gets a clean month.", 0, 0, [(21, 6, -2), (0, 0, 5)], None), LEAVE])
event("ev_side_effects", "Side Effects",
      "A courier drone drops a parcel of experimental firmware marked TRIAL COHORT B.",
      [("Install the trial build", "It works. You try not to think about cohort A.", 0, 4, [], F % "overvolt"),
       ("Sell the parcel (+25 Cycles)", "Trial code sells well downtown.", 0, 0, [(22, 6, 25)], None), LEAVE])
event("ev_night_shift_nurse", "Night Shift",
      "A Solace nurse on a smoke break recognises the Cell's tag and says nothing for a long time.",
      [("Ask for help (+15 HP)", "She patches you up and tells you which cameras are fake.", 0, 0, [(14, 0, 15)], None),
       ("Ask for her badge (Card: Lock On)", "She hands it over. 'Make it count.'", 0, 0, [], C % "lock_on"), LEAVE], speaker=1)
event("ev_recall_van", "Recall Van",
      "An unmarked recall van idles in the alley, back doors open, full of repossessed implants.",
      [("Loot it (+35 Cycles, +4 Heat)", "Chrome by the handful. The van's camera saw everything.", 0, 0, [(22, 6, 35), (21, 6, 4)], None),
       ("Strip the tracker (Asset: Tar Pit)", "The tracker makes a nice trap.", 0, 3, [], A % "tar_pit"), LEAVE])
event("ev_loyalty_points", "Loyalty Points",
      "A glitched loyalty account shows ten million Solace Care Points. They expire at midnight.",
      [("Spend them (Daemon: Field Medic)", "The points buy a care routine nobody should have.", 20, 0, [], D % "field_medic"),
       ("Cash them out (+20 Cycles)", "The exchange rate is terrible. The Cycles are real.", 0, 0, [(22, 6, 20)], None), LEAVE])
event("ev_quarantine_ward", "Quarantine Ward",
      "The door reads QUARANTINE. The lock reads OFFLINE. Something inside hums.",
      [("Go in (Daemon: Static Field, 8 damage)", "A rogue process latches onto you. It's on your side. Mostly.", 0, 8, [], D % "static_field"),
       LEAVE], min_tier=2)
event("ev_pharma_rep", "Pharma Rep",
      "A Solace rep offers the Cell a 'partnership': stop hitting their clinics and receive a stipend.",
      [("Take the stipend (+40 Cycles, +5 Heat)", "Solace never pays without logging it.", 0, 0, [(22, 6, 40), (21, 6, 5)], None),
       ("Tell them where to shove it (-1 Heat)", "Saying no quietly is still a kind of ghosting.", 0, 0, [(21, 6, -1)], None), LEAVE], speaker=2)
event("ev_open_source_clinic", "Open Clinic",
      "A free clinic runs on stolen Solace firmware. The medic wants a better firewall.",
      [("Donate 20 Cycles (-2 Heat)", "The clinic stays open another week, and the street remembers.", 20, 0, [(21, 6, -2)], None),
       ("Trade code (Firmware: Nanite Mesh)", "She swaps you a healing build for a patch.", 0, 0, [], F % "nanite_mesh"), LEAVE], speaker=1)
event("ev_broken_leash", "Broken Leash",
      "A kid with a bricked leash implant asks if you can make it work again.",
      [("Fix it (5 damage, -2 Heat)", "It sparks. It works. You feel it in your own jaw.", 0, 5, [(21, 6, -2)], None),
       ("Pay for a real fix (15 Cycles, -1 Heat)", "A back-alley doc takes the Cycles and the kid.", 15, 0, [(21, 6, -1)], None), LEAVE])
event("ev_signal_booster", "Signal Booster",
      "A rooftop booster relays Solace telemetry. It could relay something else.",
      [("Tap it (Daemon: Warm Boot)", "A little more power every time you jack in.", 0, 0, [(21, 6, 2)], D % "warm_boot"),
       ("Smash it (-1 Heat)", "Telemetry for six blocks goes dark.", 0, 0, [(21, 6, -1)], None), LEAVE])
event("ev_diagnostic_bay", "Diagnostic Bay",
      "A diagnostic bay will scan your rig for faults. Solace charges for the scan and the faults.",
      [("Run diagnostics (Card: Sanitize)", "It finds a fault and, grudgingly, a fix.", 10, 0, [], C % "sanitize"),
       ("Overclock the bay (Card: Hot Patch, +1 Heat)", "Everything runs hotter now, including you.", 0, 0, [(21, 6, 1)], C % "hot_patch"), LEAVE])
event("ev_insurance_claim", "Insurance Claim",
      "A Solace claims form, pre-filled, for an injury you haven't had yet.",
      [("File it and get hurt (+30 Cycles, 6 damage)", "The payout clears before the bruise does.", 0, 6, [(22, 6, 30)], None),
       ("Forge the adjuster's approval (+2 Schematics banked, +3 Heat)", "Approved. Flagged. Both.", 0, 0, [(23, 6, 2), (21, 6, 3)], None), LEAVE], min_tier=2)
event("ev_orbital_ad", "Orbital Ad",
      "Satellite adverts for 'Solace Premium Forever' cross the sky. Someone hacked one to say FOREVER IS A LEASH.",
      [("Add your tag (-1 Heat)", "The sky carries the Cell's name for an hour.", 0, 0, [(21, 6, -1)], None),
       ("Trace the hacker (Card: Feather Touch)", "You find a note, and a trick with a single tick.", 0, 0, [], C % "feather_touch"), LEAVE])
event("ev_supply_closet", "Supply Closet",
      "A maintenance closet behind the clinic. Somebody left the good tools.",
      [("Take the kit (Card: Bulwark)", "Heavy, reliable, perfectly boring.", 0, 0, [], C % "bulwark"),
       ("Take the batteries (+2 Schematics banked)", "Fresh cells, easily resold.", 0, 0, [(23, 6, 2)], None), LEAVE])
event("ev_audit_trail", "Audit Trail",
      "Your own intrusion is showing up in a Solace audit log, line by line, in real time.",
      [("Scrub it (15 Cycles, -3 Heat)", "Line by line, it forgets you.", 15, 0, [(21, 6, -3)], None),
       ("Let it run (+1 Heat)", "Somebody at Solace gets a very interesting morning.", 0, 0, [(21, 6, 1)], None)], speaker=4)
event("ev_rival_crew", "Rival Crew",
      "Another crew is looting the same node. Their leader grins. 'Split it?'",
      [("Split it (+20 Cycles)", "Honour among thieves, for once.", 0, 0, [(22, 6, 20)], None),
       ("Take it all (+40 Cycles, 10 damage)", "You win. It hurts.", 0, 10, [(22, 6, 40)], None),
       ("Trade gear (Asset: Flak Array)", "They're keen on your old shoes. You're keen on their flak.", 10, 0, [], A % "flak_array")], speaker=1, corp="")
event("ev_ghost_market", "Ghost Market",
      "A pop-up market in a dead subnet. The prices are high and the vendors are anonymous.",
      [("Buy a daemon (40 Cycles: Salvager)", "It pays for itself. Eventually.", 40, 0, [], D % "salvager"),
       ("Buy a blueprint (30 Cycles: Firmware Recycler)", "Your Miss slice is less of a waste now.", 30, 0, [], F % "recycler"), LEAVE], corp="")
event("ev_shutdown_notice", "Shutdown Notice",
      "Solace is shutting down a clinic tomorrow. The staff are allowed to take nothing.",
      [("Help them take everything (+3 Heat, Card: Stim Patch)", "They leave with the supplies. You leave with a thank-you.", 0, 0, [(21, 6, 3)], C % "stim_patch"),
       ("Take a map of the building (+2 Schematics banked)", "Floor plans are worth more than medicine to the Cell.", 0, 0, [(23, 6, 2)], None), LEAVE], min_tier=2)

for eid, title, text, choices, speaker, corp, min_tier, weight in EV:
    r = Res("TerminalEventData", "res://scripts/data/terminal_event_data.gd")
    csubs = []
    for ci, (label, result, cyc, hp, effs, reward) in enumerate(choices):
        esubs = [r.effect("fx%d_%d" % (ci, i), t, tgt, amt) for i, (t, tgt, amt) in enumerate(effs)]
        fields = [("label", '"%s"' % label), ("result_text", '"%s"' % result)]
        if cyc:
            fields.append(("cycle_cost", cyc))
        if hp:
            fields.append(("hp_cost", hp))
        if esubs:
            fields.append(("effects", arr(r.script(S_EFFECT), esubs)))
        if reward:
            fields.append(("reward", r.res(reward)))
        csubs.append(r.sub("c%d" % ci, "res://scripts/data/event_choice_data.gd", fields))
    r.main = ['id = &"%s"' % eid, 'title = "%s"' % title, "speaker = %d" % speaker, 'text = "%s"' % text,
              "choices = " + arr(r.script("res://scripts/data/event_choice_data.gd"), csubs)]
    if corp:
        r.main.append('corporation_id = &"%s"' % corp)
    if min_tier > 1:
        r.main.append("min_tier = %d" % min_tier)
    r.write("content/events/%s.tres" % eid, "Terminal event (M7 Solace depth, decision 2026-09-24).")
    written["events"] += 1

print("WRITTEN", written)
