"""M12: three more home-server variants (GAP_ANALYSIS P1 10), each a Profile unlock
(UnlockKind 3 = HOME_SERVER). Internal nodes fold into the home server's capacity like the
Bunker (decision 2026-09-24). NetworkNodeType: 0 HOME_SERVER, 1 RELAY, 2 FIREWALL_RELAY.
AssetType 1 = ICE_LOCK."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "gen_classes.py"), encoding="utf-8").read()
exec(_src[:_src.index("# ---- standalone ring segments")])

S_NODE = "res://scripts/data/network_node_data.gd"
S_ASSET = "res://scripts/data/defense_asset_data.gd"
VARIANTS = [
    # id, name, desc, core (integrity, slots), internal nodes [(id, name, type, integrity, slots, built-in asset or None)], cost
    ("home_relay_nest", "Relay Nest home server", "50 integrity spread thin, 5 asset slots: room for a whole armory.",
     (35, 3), [("nest_relay", "Nest Relay", 1, 15, 2, None)], 50),
    ("home_ghost", "Ghost home server", "50 integrity, 2 slots and a built-in ICE Lock that holds the first threat to reach home.",
     (40, 2), [("ghost_lock_node", "Lock Chamber", 1, 10, 0, ("ghost_lock", "Ghost Lock", "Built in: holds a threat on the home server for 2 steps.", 1, 12, 2))], 60),
    ("home_fortress", "Fortress home server", "100 integrity but only 2 asset slots: it survives, it does not shoot.",
     (60, 1), [("fortress_wall", "Fortress Wall", 2, 40, 1, None)], 80),
]
for vid, name, desc, (core_int, core_slots), internals, cost in VARIANTS:
    r = Res("HomeServerVariantData", "res://scripts/data/home_server_variant_data.gd")
    core = r.sub("core", S_NODE, [("id", '&"%s_core"' % vid), ("node_type", 0), ("display_name", '"Home Server"'),
        ("description", '"Lose the campaign if it reaches 0."'), ("install_cost", 0), ("integrity", core_int), ("asset_slots", core_slots)])
    nodes = []
    for i, (nid, nname, ntype, nint, nslots, asset) in enumerate(internals):
        fields = [("id", '&"%s"' % nid), ("node_type", ntype), ("display_name", '"%s"' % nname),
                  ("description", '"Part of the %s."' % name), ("install_cost", 0), ("integrity", nint), ("asset_slots", nslots)]
        if asset:
            aid, aname, adesc, atype, aint, delay = asset
            a = r.sub("asset%d" % i, S_ASSET, [("asset_type", atype), ("id", '&"%s"' % aid), ("display_name", '"%s"' % aname),
                ("description", '"%s"' % adesc), ("integrity", aint), ("damage", 0), ("range_hops", 0), ("shots_per_step", 1),
                ("targeting", 0), ("delay_steps", delay), ("decoy_pull", 0)])
            fields.append(("built_in_asset", a))
        nodes.append(r.sub("node%d" % i, S_NODE, fields))
    total_int = core_int + sum(n[3] for n in internals)
    total_slots = core_slots + sum(n[4] for n in internals)
    r.main = ['id = &"%s"' % vid, 'display_name = "%s"' % name, 'description = "%s"' % desc, "core = " + core,
              "internal_nodes = " + arr(r.script(S_NODE), nodes),
              "internal_links = Array[Vector2i]([%s])" % ", ".join("Vector2i(0, %d)" % (i + 1) for i in range(len(nodes)))]
    r.write("content/nodes/%s.tres" % vid, "%s (M12, decision 2026-09-24): %d integrity, %d asset slots in total." % (name, total_int, total_slots))
    u = Res("ProfileUnlockData", "res://scripts/data/profile_unlock_data.gd")
    u.main = ['id = &"unlock_%s"' % vid, "kind = 3", 'display_name = "Home server: %s"' % name.replace(" home server", ""),
              'description = "Start campaigns on the %s (%s)."' % (name, desc.split(":")[0].rstrip(".")), "schematic_cost = %d" % cost,
              "unlocks = " + u.res("res://content/nodes/%s.tres" % vid)]
    u.write("content/unlocks/unlock_%s.tres" % vid, "Home-server unlock (GDD 3.4; M12). UnlockKind 3 = HOME_SERVER.")
print("HOME VARIANTS DONE")
