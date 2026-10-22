# G: Merged Telegraph (round 5; the calibration anchor)

G4 with every number reconciled to the game (code: `tools/raid_concepts/concept_g5_merged.py`; frames in `r5/`).

## Rules
The rules are the package:
- fixed routes;
- home is never a corridor;
- the weaker-node tie-break;
- ICE blocks the strike;
- a 3-of-5 deploy draft;
- no cascade.

Rounding follows GDScript `roundi`, so a crew-boosted Sentry deals 5.

## Payout
- +4 Schematics salvage per kill.
- +6 if CLEAN.
- Net = payout − the full repair bill:
  - home and SCUFFED cost 1 per point;
  - DOWN costs half the install;
  - TAKEN costs the full install.
- Raids do not move Heat.
- Verdict tiers are CLEAN / HOLDS / BREACHED.

## Loop
1. **Netrun map.** A dial counts the netruns until home, and a cobalt ring marks where the raid lands. The raid size
   for each Heat tier is shown, along with the raid record.
2. **Warning.** Routes are drawn cobalt with a white core. A fork glyph appears only where a tie-break chose the route.
3. **Draft.** Each card's coin shows its marginal value: the best net with it minus the best net without it, over the
   full sweep. A glyph shows what each gun aims at.
4. **Planning.** Effective numbers on pieces, reach rings, and a what-if chip.
5. **Forecast.** Three plans (net +10 / +9 / +4), the net box, and attack-order chips.
6. **Resolution.** Beat pacing: 9 beats plus 3 kill-cams = 15 s, and the clock counts both. Zero input.
7. **Aftermath.** Patching is a per-node choice. Each choice shows the next raid's projection: Heat-75 roster
   (Lockdown Unit added), Solace plating, and the same pieces left in place.
8. **Next raid.** Lockdown freezes a home link. Plating (the Enforcer ignores shots of 8+) shifts the draft values:
   the Railgun goes from +11 to +3, and the cards show the change.
