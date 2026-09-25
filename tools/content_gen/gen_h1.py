"""Horizontal pass 1 fixes (GAP_ANALYSIS H1): pirate-radio DJ sets per corporation (the
generic set keeps the corporation-neutral lines), a rescue event for every corporation
(the rescued operative is one of the classes already on your roster, NetrunSession), and
the Breaker's second exclusive card (Shatter), shared with the Wrecker."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "gen_classes.py"), encoding="utf-8").read()
exec(_src[:_src.index("# ---- standalone ring segments")])

S_LINE = "res://scripts/data/voice_line_data.gd"
DJ = {
    "": ["You are listening to nobody, on no frequency, from nowhere. Stay unlicensed.",
         "Whoever is running the Cell tonight: your handler is fast. Faster than a person. Just saying.",
         "The voice giving the orders in the district does not breathe between sentences. I have the tapes."],
    "solace": ["Word from the district: three leashes went quiet last night and the owners are still walking. Somebody is doing good work.",
               "Solace raised the cardiac tier again. If your chest ticks, it ticks on credit. This next track is free.",
               "Reminder to all subbies: a bricked implant is a recall they did not announce. Say it back to me.",
               "Collections is on the move. If your links light up gold, that is a lockdown. Walk around it.",
               "Somebody sold Solace patient data before Solace lost it. Think about that order of operations."],
    "meridian": ["Meridian lost another pallet of insulin today. Lost, like a magician loses a coin.",
                 "Tariff season in the district: if your deck feels light, somebody billed it.",
                 "Night shift, this one is for you. Sit down for three minutes. The scoring engine cannot hear music.",
                 "Couriers overhead. If one follows you home, it already knew the way."],
    "halcyon": ["Halcyon fined the whole block for existing loudly. This track is also loud.",
                "Water prices went up with the temperature again. Stay hydrated, stay angry.",
                "If a streetlight turns to look at you, wave. It is a camera. Wave anyway.",
                "The smart meters are listening. Hello, smart meters. This song is not for you."],
    "orbital": ["Storm tonight over the eastern districts. Orbital knew yesterday. Now you know too.",
                "Positioning is a subscription now. This radio is not. You are exactly here.",
                "The founder is on the free band again. Look her up. Look up in general.",
                "Solar flare warning: if your deck runs hot, enjoy it, then cool it down."],
    "rebel_cell": ["This is the pirate radio. I am still here. I do not know if you are still you.",
                   "Someone is broadcasting your old orders on every band. Do not follow them.",
                   "Every safehouse you ever had is lit up tonight. None of them are safe.",
                   "DISPATCH asked me to play this one. I am playing something else."],
}
for corp, lines in DJ.items():
    vr = Res("LineSetData", "res://scripts/data/line_set_data.gd")
    subs = [vr.sub("l%d" % i, S_LINE, [("key", '"dj"'), ("text", '"%s"' % t)]) for i, t in enumerate(lines)]
    vid = "dj_hq" if corp == "" else "dj_%s" % corp
    vr.main = ['id = &"%s"' % vid, "speaker = 0"] + (['corporation_id = &"%s"' % corp] if corp else []) + ["lines = " + arr(vr.script(S_LINE), subs)]
    vr.write("content/voice/%s.tres" % vid, "Pirate-radio DJ lines (HQ). Horizontal pass 1: split per corporation.")

RESCUE = {
    "meridian": ("ev_mer_rescue", "Returned to Sender", "An operative sealed in a Meridian returns crate, still breathing, labelled DAMAGED IN TRANSIT."),
    "halcyon": ("ev_hal_rescue", "Holding Cell", "A Halcyon holding cell. The operative inside was booked for loitering near a Rack."),
    "orbital": ("ev_orb_rescue", "Grounded", "An operative trapped in a ground-station cage, charged with unlicensed transmission."),
    "rebel_cell": ("ev_rc_rescue", "Deprogramming", "One of your own, held by DISPATCH's Handler, halfway through a loyalty rewrite."),
}
S_CHOICE = "res://scripts/data/event_choice_data.gd"
for corp, (eid, title, text) in RESCUE.items():
    r = Res("TerminalEventData", "res://scripts/data/terminal_event_data.gd")
    c0 = r.sub("c0", S_CHOICE, [("label", '"Break them out (6 damage): a rescued operative joins the roster"'),
        ("result_text", '"They are shaky, but they are yours."'), ("hp_cost", 6), ("reward", r.res("res://content/classes/breaker.tres"))])
    c1 = r.sub("c1", S_CHOICE, [("label", '"Leave them"'), ("result_text", '"You tell yourself someone else will come."')])
    r.main = ['id = &"%s"' % eid, 'title = "%s"' % title, "speaker = 0", 'text = "%s"' % text,
              "choices = " + arr(r.script(S_CHOICE), [c0, c1]), 'corporation_id = &"%s"' % corp, "min_tier = 2"]
    r.write("content/events/%s.tres" % eid, "Rescue event (GDD 5.4). The reward class is a placeholder: the rescued operative is one of\nthe classes already on the roster (NetrunSession._rescue_class).")

r = Res("CardData", "res://scripts/data/card_data.gd")
fx = r.script(S_EFFECT)
e0 = r.effect("fx0", 11, 2, 1)
e1 = r.effect("fx1", 10, 2, -1)
r.main = ['id = &"shatter"', 'display_name = "Shatter"', 'description = "Breach the target Hub for 1 turn and strip 1 resistance."',
          "rarity = 1", "ram_cost = 2", "cycle_cost = 70", 'class_id = &"breaker"', "wheel_target = 1", "effects = " + arr(fx, [e0, e1])]
r.write("content/cards/shatter.tres", "Breaker exclusive #2 (horizontal pass 1): every class has two exclusives.")
print("H1 CONTENT DONE")
