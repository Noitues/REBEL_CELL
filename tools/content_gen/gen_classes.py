"""Writes the Ghost, Rigger and Botnet classes (GDD 5.2, 5.3, 6.4) and their support
content. Enum values: EffectType DEAL_DAMAGE 0, EVADE 3, APPLY_STATUS 4, NUDGE 5, SPIN 6,
FREEZE 9, MODIFY_RESISTANCE 10, GAIN_RAM 12, HEAL 14, SNAP_TO_CENTER 16, DEPLOY_DRONE 18,
RETRIGGER 19, CUSTOM 24. EffectTarget SELF 0, OWN_WHEEL 1, TARGET_WHEEL 2, POINTER_TARGET 3.
Trigger PASSIVE 0, ON_PERFECT 6, ON_RAID_START 12. Status PARASITE 4. SlicePick CHOSEN 2.
WheelTarget OWN 0, ENEMY 1, ANY 2. SliceType DEPLOY 5. RingScope WHOLE 2."""
import os
# Repo root (this file lives in tools/content_gen/).
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

S_EFFECT = 'res://scripts/data/effect_data.gd'
S_TE = 'res://scripts/data/triggered_effect_data.gd'


class Res:
    """Tiny .tres writer: ext resources by path, sub-resources as ordered blocks."""
    def __init__(self, script_class, script_path):
        self.script_class = script_class
        self.ext = []  # (type, path, id)
        self.subs = []  # (id, lines)
        self.main = []
        self.add_ext("Script", script_path, "main_script")

    def add_ext(self, type_, path, id_=None):
        for t, p, i in self.ext:
            if p == path:
                return i
        id_ = id_ or "e%d" % len(self.ext)
        self.ext.append((type_, path, id_))
        return id_

    def script(self, path):
        return 'ExtResource("%s")' % self.add_ext("Script", path)

    def res(self, path):
        return 'ExtResource("%s")' % self.add_ext("Resource", path)

    def sub(self, id_, script_path, fields):
        lines = ['script = %s' % self.script(script_path)] + ["%s = %s" % (k, v) for k, v in fields]
        self.subs.append((id_, lines))
        return 'SubResource("%s")' % id_

    def effect(self, id_, type_, target, amount=None, **kw):
        fields = [("type", type_), ("target", target)]
        if amount is not None:
            fields.append(("amount", amount))
        for k, v in kw.items():
            fields.append((k, v))
        return self.sub(id_, S_EFFECT, fields)

    def te(self, id_, trigger, effects, min_tier=None):
        fields = [("trigger", trigger)]
        if min_tier is not None:
            fields.append(("min_tier", min_tier))
        fields.append(("effects", 'Array[%s]([%s])' % (self.script(S_EFFECT), ", ".join(effects))))
        return self.sub(id_, S_TE, fields)

    def write(self, path, header_comment=""):
        out = []
        for t, p, i in self.ext:
            out.append('[ext_resource type="%s" path="%s" id="%s"]' % (t, p, i))
        out.append("")
        if header_comment:
            out.extend("; " + l for l in header_comment.split("\n"))
            out.append("")
        for id_, lines in self.subs:
            out.append('[sub_resource type="Resource" id="%s"]' % id_)
            out.extend(lines)
            out.append("")
        out.append("[resource]")
        out.append('script = ExtResource("main_script")')
        out.extend(self.main)
        steps = len(self.ext) + len(self.subs) + 1
        text = '[gd_resource type="Resource" script_class="%s" load_steps=%d format=3]\n\n' % (self.script_class, steps) + "\n".join(out) + "\n"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8", newline="\n").write(text)
        print("wrote", path)


def arr(script_expr, items):
    return "Array[%s]([%s])" % (script_expr, ", ".join(items))


# ---- standalone ring segments (moved out of breaker_ring.tres) ----------------------------------------
for sid, name, desc, fields in [
    ("seg_x2", "x2", "Outer slice output doubled.", [("output_multiplier", "2.0")]),
    ("seg_pierce", "Pierce", "Ignore block and shield.", [("pierce", "true")]),
    ("seg_blank", "-", "No modifier.", []),
]:
    r = Res("RingSegmentData", "res://scripts/data/ring_segment_data.gd")
    r.main = ['id = &"%s"' % sid, 'display_name = "%s"' % name, 'description = "%s"' % desc] + ["%s = %s" % f for f in fields]
    r.write("content/rings/segments/%s.tres" % sid)

SEG = lambda s: "res://content/rings/segments/%s.tres" % s


def ring(path, segs, comment):
    r = Res("InnerRingData", "res://scripts/data/inner_ring_data.gd")
    seg_script = r.script("res://scripts/data/ring_segment_data.gd")
    r.main = ["segments = " + arr(seg_script, [r.res(SEG(s)) for s in segs])]
    r.write(path, comment)


ring("content/rings/breaker_ring.tres", ["seg_x2", "seg_pierce", "seg_blank"], "Breaker Rank 1 Inner Ring (GDD A.1 / 6.4): x2 / Pierce / blank.")
ring("content/rings/ghost_ring.tres", ["seg_pierce", "seg_x2", "seg_echo"], "Ghost Rank 1 Inner Ring: Pierce / x2 / Echo (decision 2026-09-24).")
ring("content/rings/rigger_ring.tres", ["seg_accelerator", "seg_x2", "seg_echo"], "Rigger Rank 1 Inner Ring: Accelerator / x2 / Echo (decision 2026-09-24).")
ring("content/rings/botnet_ring.tres", ["seg_echo", "seg_corrupt", "seg_x2"], "Botnet Rank 1 Inner Ring: Echo / Corrupt / x2 (decision 2026-09-24).")

# ---- Deploy slice ---------------------------------------------------------------------------------------
r = Res("SliceData", "res://scripts/data/slice_data.gd")
r.main = ['id = &"deploy_1"', 'display_name = "Deploy 1"', "slice_type = 5", "target_rule = 0", "base_output = 1"]
r.write("content/slices/deploy_1.tres", "DEPLOY (GDD 2.6): docks one drone of the Hub's template on this slice (or the next free one).")

# ---- Hub Cores ----------------------------------------------------------------------------------------------
def hub(hid, name, desc, passive=None, hook=None, extra=(), comment=""):
    r = Res("HubCoreData", "res://scripts/data/hub_core_data.gd")
    te_script = r.script(S_TE)
    lines = ['id = &"%s"' % hid, 'display_name = "%s"' % name, 'description = "%s"' % desc]
    if passive:
        lines.append("passive_effects = " + arr(te_script, passive(r)))
    if hook:
        lines.append("perfect_hook = " + hook(r))
    lines.extend(extra(r) if callable(extra) else extra)
    r.main = lines
    r.write("content/hub_cores/%s.tres" % hid, comment)

hub("ghost_core", "Ghost Core", "First nudge on an enemy wheel each turn ignores resistance. Perfect: strip 2 resistance and the slice resolves twice.",
    hook=lambda r: r.te("hook", 6, [r.effect("fx_strip", 10, 3, -2), r.effect("fx_retrigger", 19, 0, None, multiplier="1.0")], 2),
    extra=["free_resistance_nudges = 1"], comment="Ghost Core (GDD 5.2).")
hub("ghost_core_mk2", "Ghost Core Mk2", "First two nudges on enemy wheels each turn ignore resistance. Perfect: strip 3 resistance, evade the next attack, and the slice resolves twice.",
    hook=lambda r: r.te("hook", 6, [r.effect("fx_strip", 10, 3, -3), r.effect("fx_evade", 3, 0, 1), r.effect("fx_retrigger", 19, 0, None, multiplier="1.0")], 2),
    extra=["free_resistance_nudges = 2"], comment="Ghost Core Mk2, Rank 2 upgrade (decision 2026-09-24).")
hub("rig_core", "Rig Core", "+1 max RAM. Perfect: refund 1 RAM, gain a free nudge, and the slice resolves again at half.",
    hook=lambda r: r.te("hook", 6, [r.effect("fx_retrigger", 19, 0, None, multiplier="0.5"), r.effect("fx_ram", 12, 0, 1), r.effect("fx_nudge", 24, 0, 1, custom_handler=r.script("res://scripts/core/handlers/calibrate_handler.gd"))], 2),
    extra=["max_ram_bonus = 1"], comment="Rig Core (GDD 5.2). The free nudge reuses the Calibrate handler (amount = free nudges).")
hub("rig_core_mk2", "Rig Core Mk2", "+2 max RAM. Perfect: refund 2 RAM, gain a free nudge, and the slice resolves again at half.",
    hook=lambda r: r.te("hook", 6, [r.effect("fx_retrigger", 19, 0, None, multiplier="0.5"), r.effect("fx_ram", 12, 0, 2), r.effect("fx_nudge", 24, 0, 1, custom_handler=r.script("res://scripts/core/handlers/calibrate_handler.gd"))], 2),
    extra=["max_ram_bonus = 2"], comment="Rig Core Mk2, Rank 2 upgrade (decision 2026-09-24).")
hub("swarm_core", "Swarm Core", "Up to 3 drones; drones persist between the fights of a netrun. Perfect: the slice resolves again at half; on a Deploy, a parasite halves the target slice.",
    hook=lambda r: r.te("hook", 6, [r.effect("fx_retrigger", 19, 0, None, multiplier="0.5"), r.effect("fx_parasite", 24, 3, None, custom_handler=r.script("res://scripts/core/handlers/parasite_handler.gd"))], 2),
    extra=lambda r: ["max_drones = 3", "drone = " + r.res("res://content/enemies/botnet_drone.tres"), "drones_persist = true"],
    comment="Swarm Core (GDD 5.2).")
hub("swarm_core_mk2", "Swarm Core Mk2", "Up to 4 drones that persist between fights. Perfect: the slice resolves again at half; on a Deploy, a parasite halves the target slice.",
    hook=lambda r: r.te("hook", 6, [r.effect("fx_retrigger", 19, 0, None, multiplier="0.5"), r.effect("fx_parasite", 24, 3, None, custom_handler=r.script("res://scripts/core/handlers/parasite_handler.gd"))], 2),
    extra=lambda r: ["max_drones = 4", "drone = " + r.res("res://content/enemies/botnet_drone.tres"), "drones_persist = true"],
    comment="Swarm Core Mk2, Rank 2 upgrade (decision 2026-09-24).")

# ---- Class alternatives (GDD 3.4: same deck + different core). Decision 2026-09-24 -------------------------------
CAL = "res://scripts/core/handlers/calibrate_handler.gd"
hub("wrecker_core", "Wrecker Core", "No spin bonus. Perfect: the slice resolves again at 1.5x.",
    hook=lambda r: r.te("hook", 6, [r.effect("fx_retrigger", 19, 0, None, multiplier="1.5")], 2),
    comment="Wrecker Core: Breaker alternative (decision 2026-09-24).")
hub("wrecker_core_mk2", "Wrecker Core Mk2", "+1 spin on all cards. Perfect: the slice resolves again at 1.5x.",
    passive=lambda r: [r.te("te_spin", 0, [r.effect("fx_spin", 6, 1, 1, ring_scope=2)])],
    hook=lambda r: r.te("hook", 6, [r.effect("fx_retrigger", 19, 0, None, multiplier="1.5")], 2),
    comment="Wrecker Core Mk2, Rank 2 upgrade (decision 2026-09-24).")
hub("phantom_core", "Phantom Core", "A free nudge at the start of each turn. Perfect: evade the next attack and the slice resolves twice.",
    passive=lambda r: [r.te("te_nudge", 2, [r.effect("fx_nudge", 24, 0, 1, custom_handler=r.script(CAL))])],
    hook=lambda r: r.te("hook", 6, [r.effect("fx_evade", 3, 0, 1), r.effect("fx_retrigger", 19, 0, None, multiplier="1.0")], 2),
    comment="Phantom Core: Ghost alternative (decision 2026-09-24). The turn-start nudge reuses the Calibrate handler.")
hub("phantom_core_mk2", "Phantom Core Mk2", "Two free nudges at the start of each turn. Perfect: evade the next attack and the slice resolves twice.",
    passive=lambda r: [r.te("te_nudge", 2, [r.effect("fx_nudge", 24, 0, 2, custom_handler=r.script(CAL))])],
    hook=lambda r: r.te("hook", 6, [r.effect("fx_evade", 3, 0, 1), r.effect("fx_retrigger", 19, 0, None, multiplier="1.0")], 2),
    comment="Phantom Core Mk2, Rank 2 upgrade (decision 2026-09-24).")
hub("overclock_core", "Overclock Core", "+2 max RAM. Perfect: gain 2 RAM and the slice resolves again at half.",
    hook=lambda r: r.te("hook", 6, [r.effect("fx_retrigger", 19, 0, None, multiplier="0.5"), r.effect("fx_ram", 12, 0, 2)], 2),
    extra=["max_ram_bonus = 2"], comment="Overclock Core: Rigger alternative (decision 2026-09-24).")
hub("overclock_core_mk2", "Overclock Core Mk2", "+3 max RAM. Perfect: gain 3 RAM and the slice resolves again at half.",
    hook=lambda r: r.te("hook", 6, [r.effect("fx_retrigger", 19, 0, None, multiplier="0.5"), r.effect("fx_ram", 12, 0, 3)], 2),
    extra=["max_ram_bonus = 3"], comment="Overclock Core Mk2, Rank 2 upgrade (decision 2026-09-24).")
hub("hive_core", "Hive Core", "Up to 4 drones for this fight only. Perfect: dock a drone and the slice resolves again at half.",
    hook=lambda r: r.te("hook", 6, [r.effect("fx_retrigger", 19, 0, None, multiplier="0.5"), r.effect("fx_drone", 18, 0, 1)], 2),
    extra=lambda r: ["max_drones = 4", "drone = " + r.res("res://content/enemies/botnet_drone.tres")],
    comment="Hive Core: Botnet alternative (decision 2026-09-24). Drones do not persist.")
hub("hive_core_mk2", "Hive Core Mk2", "Up to 5 drones for this fight only. Perfect: dock a drone and the slice resolves again at half.",
    hook=lambda r: r.te("hook", 6, [r.effect("fx_retrigger", 19, 0, None, multiplier="0.5"), r.effect("fx_drone", 18, 0, 1)], 2),
    extra=lambda r: ["max_drones = 5", "drone = " + r.res("res://content/enemies/botnet_drone.tres")],
    comment="Hive Core Mk2, Rank 2 upgrade (decision 2026-09-24).")

# ---- Exclusive cards ------------------------------------------------------------------------------------------
def card(cid, name, desc, ram, cycle, cls, wheel_target, effects, exhaust=False, rarity=1):
    r = Res("CardData", "res://scripts/data/card_data.gd")
    fx_script = r.script(S_EFFECT)
    lines = ['id = &"%s"' % cid, 'display_name = "%s"' % name, 'description = "%s"' % desc, "rarity = %d" % rarity,
             "ram_cost = %d" % ram, "cycle_cost = %d" % cycle, 'class_id = &"%s"' % cls, "wheel_target = %d" % wheel_target,
             "effects = " + arr(fx_script, effects(r))]
    if exhaust:
        lines.append("exhaust = true")
    r.main = lines
    r.write("content/cards/%s.tres" % cid)

card("ghost_step", "Ghost Step", "Two nudges on an enemy wheel, ignoring resistance.", 1, 70, "ghost", 1,
     lambda r: [r.effect("fx", 5, 2, 2, ring_scope=0, multiplier="0.0")])
card("blind_spot", "Blind Spot", "The target skips its next respin and loses 1 resistance.", 2, 75, "ghost", 1,
     lambda r: [r.effect("fx_freeze", 9, 2), r.effect("fx_strip", 10, 2, -1)])
card("torque_wrench", "Torque Wrench", "Spin a wheel 5 ticks and gain a free nudge.", 1, 70, "rigger", 2,
     lambda r: [r.effect("fx_spin", 6, 2, 5, ring_scope=2), r.effect("fx_nudge", 24, 0, 1, custom_handler=r.script("res://scripts/core/handlers/calibrate_handler.gd"))])
card("hot_swap", "Hot Swap", "Snap your outer ring to the slice centre and gain 1 RAM.", 2, 75, "rigger", 0,
     lambda r: [r.effect("fx_snap", 16, 1, None, ring_scope=0), r.effect("fx_ram", 12, 0, 1)])
card("spawn_drone", "Spawn Drone", "Dock a drone on a chosen slice of your wheel.", 2, 75, "botnet", 0,
     lambda r: [r.effect("fx", 18, 0, 1, slice_pick=2)])
card("parasite_pulse", "Parasite Pulse", "The target's slice under the pointer gets a PARASITE (half output). Exhaust.", 2, 80, "botnet", 1,
     lambda r: [r.effect("fx", 4, 2, None, status=4, slice_pick=0)], exhaust=True)

# ---- Classes -------------------------------------------------------------------------------------------------------
def klass(cid, name, desc, hp, slices, hub_id, hub_mk2, ring_id, options, deck, exclusives, station, comment, alternative_of="", station_mult=None):
    r = Res("ClassData", "res://scripts/data/class_data.gd")
    slot_script = r.script("res://scripts/data/wheel_slot_data.gd")
    slots = []
    for i, sl in enumerate(slices):
        slots.append(r.sub("slot_%d" % i, "res://scripts/data/wheel_slot_data.gd", [("slice", r.res("res://content/slices/%s.tres" % sl))]))
    wheel = r.sub("wheel", "res://scripts/data/wheel_data.gd", [("slice_count", 6), ("slots", arr(slot_script, slots)),
        ("hub", r.res("res://content/hub_cores/%s.tres" % hub_id)), ("pointer_ticks", "PackedInt32Array(0)")])
    seg_script = r.script("res://scripts/data/ring_segment_data.gd")
    rr = r.script("res://scripts/data/rank_reward_data.gd")
    rank1 = r.sub("rank_1", "res://scripts/data/rank_reward_data.gd", [("rank", 1), ("max_netrun_tier", 2),
        ("inner_ring", r.res("res://content/rings/%s.tres" % ring_id)), ("station_bonus_multiplier", "1.25")])
    rank2 = r.sub("rank_2", "res://scripts/data/rank_reward_data.gd", [("rank", 2), ("max_netrun_tier", 3),
        ("hub_upgrade", r.res("res://content/hub_cores/%s.tres" % hub_mk2)), ("station_bonus_multiplier", "1.5")])
    rank3 = r.sub("rank_3", "res://scripts/data/rank_reward_data.gd", [("rank", 3), ("max_netrun_tier", 4),
        ("ring_segment_options", arr(seg_script, [r.res(SEG(s)) for s in options])), ("station_bonus_multiplier", "2.0")])
    st_type, st_amount = station
    st_fx = r.effect("fx_station", st_type, 0, st_amount) if station_mult is None else r.effect("fx_station", st_type, 0, None, multiplier=station_mult)
    st_te = r.te("te_station", 12, [st_fx])
    card_script = r.script("res://scripts/data/card_data.gd")
    r.main = ['id = &"%s"' % cid, 'display_name = "%s"' % name, 'description = "%s"' % desc, "starting_wheel = " + wheel,
              "starting_deck = " + arr(card_script, [r.res("res://content/cards/%s.tres" % c) for c in deck]),
              "exclusive_cards = " + arr(card_script, [r.res("res://content/cards/%s.tres" % c) for c in exclusives]),
              "base_hp = %d" % hp, "starting_ram = 6", "max_ram = 12", "ram_regen = 4", "free_nudges_per_turn = 1",
              "station_bonus = " + arr(r.script(S_TE), [st_te]), "rank_rewards = " + arr(rr, [rank1, rank2, rank3])]
    if alternative_of:
        r.main.append('alternative_of = &"%s"' % alternative_of)
    r.write("content/classes/%s.tres" % cid, comment)

klass("ghost", "Ghost", "Slips past resistance. Perfect landings strip the target's defences.", 50,
      ["atk_14", "def_6", "atk_14", "evade_1", "def_6", "miss"], "ghost_core", "ghost_core_mk2", "ghost_ring",
      ["seg_blank", "seg_anchor", "seg_corrupt", "seg_accelerator"],
      ["fine_tune", "fine_tune", "fine_tune", "jolt", "jolt", "jam", "micro_adjust", "strip", "snap", "ghost_step"],
      ["ghost_step", "blind_spot"], (9, 1),
      "Ghost (GDD 5.2): 50 HP; Atk, Atk, Def, Def, Evade, Miss. Station bonus: threats entering the node\nare held 1 step (FREEZE amount 1; Rank scales it: 1 / 1 / 2 / 2 steps).")
klass("rigger", "Rigger", "Runs hot on RAM. Perfect landings pay for the next move.", 55,
      ["atk_16", "def_6", "atk_16", "shield_5", "def_6", "miss"], "rig_core", "rig_core_mk2", "rigger_ring",
      ["seg_pierce", "seg_corrupt", "seg_anchor"],
      ["jolt", "jolt", "jolt", "fine_tune", "fine_tune", "calibrate", "cache", "ring_tap", "brute_spin", "torque_wrench"],
      ["torque_wrench", "hot_swap"], (14, 5),
      "Rigger (GDD 5.2): 55 HP; Atk, Atk, Def, Def, Shield, Miss. Station bonus: the node regains 5\nintegrity after each wave and when the raid ends (HEAL amount 5, Rank scales it).")
klass("botnet", "Botnet", "Fights through drones that ride the whole netrun.", 45,
      ["atk_16", "deploy_1", "atk_16", "deploy_1", "def_8", "miss"], "swarm_core", "swarm_core_mk2", "botnet_ring",
      ["seg_pierce", "seg_anchor", "seg_accelerator"],
      ["jolt", "jolt", "jolt", "fine_tune", "fine_tune", "twist", "counter_spin", "pull", "cache", "spawn_drone"],
      ["spawn_drone", "parasite_pulse"], (18, 1),
      "Botnet (GDD 5.2): 45 HP; Atk, Atk, Def, Deploy, Deploy, Miss. Station bonus: one free turret on\nthe node for each raid (DEPLOY_DRONE amount 1; config.station_deploy_asset; Rank scales it).")

BREAKER_DECK = ["jolt", "jolt", "jolt", "jolt", "brute_spin", "brute_spin", "fine_tune", "fine_tune", "mirror_flip", "overdrive"]
klass("wrecker", "Wrecker", "A Breaker that trades spin control for a heavier Perfect.", 60,
      ["crit_12", "atk_6", "atk_6", "atk_6", "def_5", "miss"], "wrecker_core", "wrecker_core_mk2", "breaker_ring",
      ["seg_corrupt", "seg_anchor", "seg_accelerator", "seg_echo"], BREAKER_DECK, ["overdrive"], (0, None),
      "Wrecker: Breaker alternative (GDD 3.4, same deck + different core; decision 2026-09-24).", alternative_of="breaker", station_mult="1.5")
klass("phantom", "Phantom", "A Ghost that dodges instead of slipping resistance.", 50,
      ["atk_14", "def_6", "atk_14", "evade_1", "def_6", "miss"], "phantom_core", "phantom_core_mk2", "ghost_ring",
      ["seg_blank", "seg_anchor", "seg_corrupt", "seg_accelerator"],
      ["fine_tune", "fine_tune", "fine_tune", "jolt", "jolt", "jam", "micro_adjust", "strip", "snap", "ghost_step"],
      ["ghost_step", "blind_spot"], (9, 1), "Phantom: Ghost alternative (decision 2026-09-24).", alternative_of="ghost")
klass("overclocker", "Overclocker", "A Rigger that banks raw RAM instead of free nudges.", 55,
      ["atk_16", "def_6", "atk_16", "shield_5", "def_6", "miss"], "overclock_core", "overclock_core_mk2", "rigger_ring",
      ["seg_pierce", "seg_corrupt", "seg_anchor"],
      ["jolt", "jolt", "jolt", "fine_tune", "fine_tune", "calibrate", "cache", "ring_tap", "brute_spin", "torque_wrench"],
      ["torque_wrench", "hot_swap"], (14, 5), "Overclocker: Rigger alternative (decision 2026-09-24).", alternative_of="rigger")
klass("hivemind", "Hivemind", "A Botnet whose swarm is bigger but never leaves the fight.", 45,
      ["atk_16", "deploy_1", "atk_16", "deploy_1", "def_8", "miss"], "hive_core", "hive_core_mk2", "botnet_ring",
      ["seg_pierce", "seg_anchor", "seg_accelerator"],
      ["jolt", "jolt", "jolt", "fine_tune", "fine_tune", "twist", "counter_spin", "pull", "cache", "spawn_drone"],
      ["spawn_drone", "parasite_pulse"], (18, 1), "Hivemind: Botnet alternative (decision 2026-09-24).", alternative_of="botnet")

# ---- Unlocks ------------------------------------------------------------------------------------------------------------
for cid, name, cost in [("ghost", "Ghost", 80), ("rigger", "Rigger", 80), ("botnet", "Botnet", 80),
                        ("wrecker", "Wrecker", 60), ("phantom", "Phantom", 60), ("overclocker", "Overclocker", 60), ("hivemind", "Hivemind", 60)]:
    r = Res("ProfileUnlockData", "res://scripts/data/profile_unlock_data.gd")
    r.main = ['id = &"unlock_%s"' % cid, "kind = 0", 'display_name = "Class: %s"' % name,
              'description = "Recruit %s operatives in every campaign."' % name, "schematic_cost = %d" % cost,
              "unlocks = " + r.res("res://content/classes/%s.tres" % cid)]
    r.write("content/unlocks/unlock_%s.tres" % cid, "Class unlock (GDD 3.4: 80 Schematics, alternatives 60, spent from the current campaign). UnlockKind 0 = CLASS.")

# ---- Barks --------------------------------------------------------------------------------------------------------------
BARKS = {
    "ghost": [("perfect", "Clean. They never saw the wheel move."), ("perfect", "Perfect. Resistance is a rumour."),
              ("miss", "Miss. Stay quiet, reset, try again."), ("hurt", "Grazed. Nothing they can trace."),
              ("victory", "Gone before the log catches up."), ("defeat", "They saw me. First time for everything."),
              ("deploy", "No drones. I prefer to be alone in here."), ("jack_in", "Ghosting in. Leave no footprints."),
              ("boss", "Big wheel, bigger blind spots.")],
    "rigger": [("perfect", "Perfect. The deck pays me back."), ("perfect", "Latched and refunded."),
               ("miss", "Miss. Rerouting power."), ("hurt", "Running hot. Still running."),
               ("victory", "Rig holds. Next node."), ("defeat", "Power's out. Tell the Cell the rig was good."),
               ("deploy", "Deploying? That's the Botnet's job."), ("jack_in", "RAM topped up. Let's overclock something."),
               ("boss", "That thing eats RAM for breakfast. So do I.")],
    "botnet": [("perfect", "Perfect Deploy. Something of mine is inside theirs now."), ("perfect", "The swarm says hello."),
               ("miss", "Miss. The drones will cover."), ("hurt", "They hit a drone. Probably."),
               ("victory", "Swarm intact. Carry on."), ("defeat", "Swarm down. Scatter the seeds."),
               ("deploy", "Another one on the wheel."), ("jack_in", "Waking the swarm."),
               ("boss", "Every drone on the Hub. Now.")],
}
for cid, lines in BARKS.items():
    r = Res("LineSetData", "res://scripts/data/line_set_data.gd")
    line_script = r.script("res://scripts/data/voice_line_data.gd")
    subs = [r.sub("l%d" % i, "res://scripts/data/voice_line_data.gd", [("key", '"bark:%s"' % k), ("text", '"%s"' % t)]) for i, (k, t) in enumerate(lines)]
    r.main = ['id = &"barks_%s"' % cid, "speaker = 1", 'class_id = &"%s"' % cid, "lines = " + arr(line_script, subs)]
    r.write("content/voice/barks_%s.tres" % cid)

# ---- Config: Parasite multiplier and the Botnet station asset --------------------------------------------------------
p = "content/config/campaign_config.tres"
s = open(p, encoding="utf-8").read()
if "station_deploy_asset" not in s:
    s = s.replace('[ext_resource type="Resource" path="res://content/raids/raid_purge.tres" id="raid_purge"]\n',
                  '[ext_resource type="Resource" path="res://content/raids/raid_purge.tres" id="raid_purge"]\n[ext_resource type="Resource" path="res://content/assets/turret.tres" id="station_turret"]\n', 1)
    s = s.replace("overclock_multiplier = 1.5\n", "overclock_multiplier = 1.5\nparasite_multiplier = 0.5\n", 1)
    s = s.replace("armory_capacity = 6\n", 'armory_capacity = 6\nstation_deploy_asset = ExtResource("station_turret")\n', 1)
    import re
    m = re.search(r"load_steps=(\d+)", s)
    s = s.replace(m.group(0), "load_steps=%d" % (int(m.group(1)) + 1), 1)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("patched config")
