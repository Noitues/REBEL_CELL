# Designer decisions: open questions and defaults taken without you (2026-10-19)

You can answer per line with a code, for example "Orbital: B", "S3 b", "H4 shuttered" or "keep". This page gathers the lists. The
sources stay as they are:
- `docs/handoff/plan2/drafts/themes/THEMES_SHEET.md`: the theme question sheet; full rules in `themes/<corp>.md`.
- `docs/handoff/gates/REPLAN_2026-10-19.md`: §B lists the themes per corp; §G lists the defaults to revisit.
- `docs/DECISIONS.md`:
  - "2026-10-18 — Overnight: defaults taken on open calls";
  - "## Open questions for the designer", around line 8036;
  - the W2 Solace entries, which are on branch `w2` only for now.

**Cost of change:** only **Solace** is built (branch `w2`, not on main). Halcyon, REBEL_CELL, Orbital and Meridian have no code yet,
so changing their theme now costs nothing. Changing Solace means editing three rules slices.

## 1. Theme picks I made for you (overnight 2026-10-18)

| Corp | Picked | Other options (themes/<corp>.md) | Why picked |
|---|---|---|---|
| Meridian | **A PAYLOAD**: loot weight turns into spin resistance on your wheel | B CUSTOMS (surrender an item at checkpoints) · C DELIVERY WINDOW (fast-finish bonus) · D SUPPLY LINE (cut feeder chains to weaken the boss; strongest identity, biggest cost) | the draft's recommendation; cheapest |
| Orbital | **A DEAD ZONE**: on dark turns the free nudge is locked; relays escape it | B OVERWATCH (telegraphed orbital strike; the draft's recommendation) · C KESSLER (debris cascade) · D INTERCEPT (enemy reads your orders) | your stated leaning toward comm blackouts |
| Solace | THE BLOOM (virus front) | (single draft) | — |
| Halcyon | The Eye (PANOPTICON gaze) | (single draft) | — |
| REBEL_CELL | DISPATCH (3 lanes, Sync Strike finale) | (single draft) | Q34 ruled by you |
| Tethys / Aurelian | THE WATER LEVEL / Colosseum rings | (single drafts) | not playable until the corp wave |

## 2. Theme sub-questions answered by default

Rule used: take the draft's **(default)**; with no default, take the lighter, less punishing option.

**Solace (BUILT on w2)**
- S1 raid infection resets per raid (default) · alt: it carries over as a campaign figure.
- S2 Heat speeds raids only · alt: Heat also speeds the street Bloom.
- S3 bosses and mini-bosses are exempt from the per-turn Bloom cost · alt: elites and mini-bosses pay 0.1 layer per turn.
- S4 HQ Waiting Room debts are cut · alt: keep them (needs a new visual channel).
- S5 keep the T1 free dose · alt: no safety net.
- S6 Virus is the Exploit that slows the Bloom (75 % pace) · alt: Intel or Breach.

**Halcyon** (not built)
- H1 the HQ keeps only the gaze, Spotted fights and the beam · alt: keep Alert / Lockdown, Annex rooms, Stall, Cut the Power.
- H2 only completed netruns move the Eye · alt: deaths and abandoned runs move it too.
- H3 level 2 puts the Blade on Elites and Racks, plus +1 Heat · alt: the Blade on every normal fight.
- H4 non-fight HQ nodes inside the eye work at a cost · alt: shuttered.
- H5 raid: threats inside the sector hit harder · alt: your assets inside the sector are blinded.

**Orbital** (not built)
- O1 no lock beyond the free nudge on dark turns · alt: blackouts only cost resources.
- O2 strikes never ignore SANDBOX.
- O3 raids hit only your own nodes · alt: neutral cleared Sites too.
- O4 full form only at the HQ; street runs get one flagged dark fight.
- O5 no permanent run cost.

**Meridian** (not built)
- M1 reward-leaning: Jettison refunds 50 %, Over resistance caps at 3 · alt: the theme may cost you power.
- M2-M4 apply only to options B, C and D.

**REBEL_CELL** (not built)
- R1 the HQ needs exactly three operatives (default) · alt: a smaller crew runs fewer lanes.
- R2 if one operative dies in the route phase, the other lanes continue and the dead lane goes DARK (default) · alt: abandon the whole run.
- R3 the lead limit between lanes is 2 layers (default).
- R4 the three proposed lane effects on the finale (default) · alt: an ARMED lane carries nothing.
- R5 route HP carries into the finale with a 20 % heal (default) · alt: the regroup fully heals.
- Also: Cycles are shared, Sync Strike focus is chosen by click or keys 1-3, and the resolve order is fixed.

**Tethys** (Later)
- T1 the street start Head goes by tier (default).
- T2 raids start LOW.
- T3 Submerged mutes turrets only.
- T4 keep the Dry salvage bonus.
- T5 "wait for the tide" is free.
- T6 Divert expires after one layer.

**Aurelian** (Later)
- A1 the turning-gate clock runs at the HQ only.
- A2 telegraph 1 step, with Intel extending it to 4 (default).
- A3 fixed gate order: INTEL outer, BREACH middle, VIRUS inner.
- A4 a key-gated Cache in street runs.
- A5 a retry keeps the same layout.
- A6 drop a seating ring (about 25 min).

## 3. Solace build details decided by the agents (w2; easy to change before merge)
- **Doses:** held and used on demand. A Mainframe sells one. The Terminal-event dose is not wired yet.
- **Catch timing:** a catch after a won fight lands at the fight's end, before rewards.
- **HQ ladder:**
  - The Clinic Gate, then 9 rungs on two towers (WARD / BILLING), then the crown: 11 layers.
  - Ward rests are forced at rungs 5 and 8, and the Account Manager mini-boss sits at rung 9 on both towers.
  - ACROSS is an edge with a time cost.
  - Not built: tower pressure, READ horizon, Waiting Room, Key Fragments.
- **Ladder rewards:** no Server Rack captures, so there are no banked Schematics or Rack Heat; the mini-boss gives an elite Firmware offer.
- **Run kind:** the Solace breach is a new run kind `hq`, so it lost the old compound-city look and the breach-gate preview.
- **Raid infection:**
  - It counts in basis points.
  - Each step adds a base amount plus an amount per living threat.
  - The gaps between waves don't count as delay.
  - A tie between home loss and the infection threshold is scored BREACHED.

## 4. Other defaults worth a look (not themes)
- **City:** every campaign uses the A2 plan. The seed varies only the block fill, the Sites and the textures. Aurelian and Tethys
  districts are neutral Sprawl, and the fixed seed 7 stays the old city.
- **Street look:**
  - the body fog density multiplier is 0.12;
  - light units were converted by factors;
  - the street's fixed plate camera leaves an empty band (to be filled by the wet street).
  - Art-pass owns all of this now.
- **Exploit buildings:** treated as ruled in, as relayed by art-pass. **Still to be confirmed by you.**
- **Combat open questions:** N6 listeners, N8 stacks (the Botnet Trojan x4), N14 SANDBOX `detour_2`, N22 lopsided pools (Halcyon has
  no HARD normal), N13 / N21 / N2 / N4 / N3 edges. All are in DECISIONS "Open questions for the designer".
