"""Wheel specs for the round 10 combat mockups, from content/*.tres via roster.py / tresdata.py.

Player: Breaker (content/classes/breaker.tres). Its real wheel is ZERO-DAY 12, EXPLOIT 6 x3,
FIREWALL 5, NULL. For this mockup slot 2 (an EXPLOIT) shows VIRUS 3 and slot 5 (NULL) shows
PROXY 4, so the reworked slices are seen in context. Values 3 / 4 are round 5's defaults.
"""
import copy
import roster as RS


def player(hp=41, pred=0):
    s, m = RS.class_spec("breaker")
    s = copy.deepcopy(s)
    s["slots"][2] = dict(program="VIRUS", value=3, special=None, badge=None, name="Virus", id="mock_virus")
    s["slots"][5] = dict(program="PROXY", value=4, special=None, badge=None, name="Proxy", id="mock_proxy")
    s["hp"] = (hp, m["hp"])
    s["pred"] = pred
    s["key"] = "breaker"
    s["hp_number"] = False
    return s, m


def regular(hp=None, pred=0):
    s, m = RS.enemy_spec("route_optimizer")
    s = copy.deepcopy(s)
    s["hp"] = (hp if hp is not None else m["hp"], m["hp"])
    s["pred"] = pred
    s["key"] = "route_optimizer"
    s["hp_number"] = False
    return s, m


def boss(hp=None, pred=0):
    p1, p2, m = RS.boss_specs("meridian")
    s = copy.deepcopy(p1)
    s["hp"] = (hp if hp is not None else m["hp"], m["hp"])
    s["pred"] = pred
    s["key"] = "the_manifest"
    s["hp_number"] = False
    return s, m
