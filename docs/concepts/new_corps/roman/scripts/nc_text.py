"""New corps: the words (identity, voice, rules). Exploratory, not content. Identical copy in both scripts/ folders."""

TEXT = {
    "aurelian": dict(
        sells=("The bread and the circus. Aurelian Concord feeds the lower wards through the DOLE (free nutrient "
               "loaves, paid for in patronage: your vote, your data, your labour hours) and keeps them watching the "
               "CIRCUS: arena bloodsport streamed to every leash, with the betting on the side. Under it all runs the "
               "patron ledger: every subbie is some House's client, and the House collects."),
        controls="Food rations, arena streams + betting, client debt, the aqueduct data conduits, the gate tolls.",
        house_title="VERDICT (the crowd's thumb)",
        house=("Aurelian specials mark one of your slices with a VERDICT. When the marked slice next resolves, the "
               "landing decides: PERFECT = thumbs up, the slice is OVERCLOCKED; WEAK = thumbs down, it is CORRUPTED; "
               "GOOD = the mark stays. Uses only existing statuses; the preview shows the verdict before SEND IT."),
        boss_rule=("THE ROSTRUM calls a VERDICT on the slice under your pointer every turn unless its Hub, "
                   "THE GRAND STAND, is breached."),
        enemies="Lictor (fasces bodyguard satellites), Legionary drone, Tax Farmer, Lanista, Vestal Firewall; elites Praetorian, Censor.",
        exploits="INTEL the client rolls / BREACH the gate codes / VIRUS the open dole (frees the ration chips).",
        raid="LEVIES: legion wedges in verdigris + a gilded float; the after-action report is a LEVY RECEIPT.",
        heat=["NOTICED: lictor drones circle the side blocks", "FLAGGED: rooftop statues' eyes turn red, two arena searchlights",
              "HUNTED: the triumph gates seal; the Legion marches the boulevard"],
        speakers="The Patron (gilded mask bust), Lanista Corvina (arena promoter), the Tribune of Clients (debt collector).",
        paths="The Free Bread, Fixed Games, Census of Clients, Bread Riot, A Patron for DISPATCH (foreshadows DISPATCH), The Triumph.",
        lost="PACIFIED",
        tone="Grand, paternal, legal. Latin tags as branding, never as decoration. It congratulates you while it bills you.",
        memo_title="CLIENT NOTICE // LOT XXIV",
        memo=["Citizen-client,", "", "Your patronage has been RENEWED.", "Your ration is assured.",
              "Your attendance at the Games of the", "Ides is EXPECTED.", "", "Rejoice.", "",
              "-- House of Aurelian, Office of Clients"],
        stamp="RENEWED",
        dispatch=["Aurelian's throwing games tonight. Whole ward's watching the arena.",
                  "Nobody's watching the aqueduct."],
        type_accent="Inscription caps: Plex Sans Condensed Medium, tracking +45 %, V for U, interpuncts between words, "
                    "Roman numerals for lots and seats. Carved: an inset shadow on travertine; in neon a single tube line.",
    ),
    "tethys": dict(
        sells=("The air and the waterline. When the sea came up, Tethys Deep built the seawall and the pumps; the "
               "lower wards stay dry only while their district pays the BREATHE PLAN. Below the waves the ATLANTIS "
               "arcology holds the city's cold storage (banks, backups, memories) in pods chilled by the abyss, wired "
               "ashore through Tethys sea cables."),
        controls="Seawall + pumps (who stays dry), air leases in the flooded wards, sea cables, cold data storage, desal water.",
        house_title="TIDE (a four-turn cycle)",
        house=("Every Tethys fight runs on a tide shown on the HUD: LOW, RISING, HIGH, FALLING, one step per turn, "
               "the start step seeded at fight start. At HIGH their SANDBOX slices give double shield; at LOW their "
               "shield drains by 3 at turn start. Fixed and visible, so preview equals result."),
        boss_rule=("THE BLACK SMOKER OVERCLOCKS one of its own slices every turn unless its Hub, THE VENT CAP, is breached."),
        enemies="Pump Warden, Diver drone, Kelp Crawler, Pressure Sentinel, Lamprey (parasite); elites Siphonophore (chained satellites), Angler.",
        exploits="INTEL the tide tables / BREACH the pump override / VIRUS open air (frees the air leases).",
        raid="HIGH TIDES: amphibious pods + flood barges; the after-action report is a FLOOD ADVISORY.",
        heat=["NOTICED: buoy beacons blink on the canals", "FLAGGED: sonar pings ripple across the map, two dive lights",
              "HUNTED: seawall sirens, flood gates shut, the ward goes under"],
        speakers="The Harbourmaster, Dr. Selka Marr (pressure medicine), VOICE OF ATLANTIS (the arcology's concierge AI).",
        paths="The Breathe Plan, Ward Nine Floods, Cold Storage, The Cable Cut, Sunken Ghost (foreshadows DISPATCH), Salvage Rights.",
        lost="SUBMERGED",
        tone="Calm, spa-soft, clinical about breath. Lowercase, short sentences, countdowns. Never raises its voice; it lowers the water.",
        memo_title="SERVICE ADVISORY // ward 9",
        memo=["Resident,", "", "your breathe plan has lapsed.", "pumps in your district will pause", "in 00:30.", "",
              "please move to higher ground", "or renew.", "", "breathe easy.  -- tethys / deep"],
        stamp="LAPSED",
        dispatch=["Tide's up in Ward 9. They switched the pumps off at midnight.",
                  "Go deep while they're busy bailing."],
        type_accent="Lowercase Plex Sans Condensed with a waterline: a 1 px cut through the x-height, depth marks "
                    "(-412 m) in Share Tech-like tabular figures on paper only. Neon: a single blue tube, bubbles for dots.",
    ),
}
