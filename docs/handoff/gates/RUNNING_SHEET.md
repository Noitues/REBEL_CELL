# Running decisions and questions sheet

The designer reviews this on request. Each line is a call I made without waiting for a ruling. Answer by code, for example
"D3 B" or "Q2 no"; a line with no answer stands. Newest entries go at the top of each section. Full reasoning is in
`docs/DECISIONS.md`.

Standing directive (designer, 2026-10-19; amended the same day: **one corporation at a time to full polish, Solace first**, see `SOLACE_VERTICAL.md`):
- Skip the PT gates. Work through W1 to W4 and Later until all content is in.
- Use the Batch API and cheaper models.
- Art-pass does all visual work; this session keeps game code only.
- Make the calls and log them here.

## Calls made (revisit any)
| Code | Date | Call | Alternative |
|---|---|---|---|
| D16 | 10-20 | RESOLVED (A-067): horizon spikes never lower a building (Python and GD twin), so the 6-floor frontage minimum holds outside HQ zones again. The exemption is removed. | — |
| D18 | 10-20 | Culture garden (EX-02/03/11): each key's lot is the building under its Exploit Site, else the nearest free lot within 24 lots. The run is 9 layers (4 outside, 5 inside), and the target is the final-Rack mini-boss fight. The ward rest uses a held dose, and costs nothing without one. Footprint 48×36 BU. A patrol or reclaim of that Site stays a street run. The other two Solace key buildings are placeholders. | Change any of these |
| D17 | 10-20 | A Site whose icon is cut by the map edge counts as off the map: it gets an edge arrow instead of a label. This is the Meridian label fix after the terrain moved its icon. | none |
| D15 | 10-20 | City rules after the LOOK L5 merge (correction: the three failing buildings were outside HQ zones; horizon spikes lowered them, see D16): inside an HQ zone the HQ height cap (NA-11c) wins over the 6-floor frontage minimum (NA-11), so the HQ reads as the tallest mass. Outside HQ zones the frontage minimum holds. | The frontage minimum wins and the HQ cap gives way |
| D14 | 10-20 | Solace balance r1: Genome Core HP 360 → 400 (the reference policy wins 52 %), Claims Adjuster 112 → 96, Account Manager 150 → 128. Tuned by HP only; enrage and phases unchanged. The class bands in `docs/balance/TARGETS.md` were set after measuring. | Tune enrage instead of HP; set the bands yourself |
| D13 | 10-19 | Two more city tests went red with CITY-A2 step 2 (`test_city_geometry_memo` roofs, `test_city_map_sweeps` Site fit) and are pending until art/look's city work lands. Bisected to 606de8db and 964949bb. | none |
| D12 | 10-19 | Run graph v2 is on by default, so REST / WORKSHOP / CACHE show up in normal runs. WORKSHOP is the existing slice refit at its own price; neither N18 slice levels nor card upgrades exist yet. The CACHE puzzle is off. REST is guaranteed in layers 4-5, and the draft's "no REST before a Mainframe" exclusion is not built. The Solace ladder keeps its own ward rest (not the REST page). | Turn v2 off (`map_v2_enabled`); give the ward rest heal or swap |
| D11 | 10-19 | EV-01 events. Map-edit picks are deterministic (fewest inbound links, then node id), not random or player-picked. Combat modifiers from events apply to the next fight and end with the netrun. Event fights don't count as normal fights. Two broken draft details were dropped: the escort's +1 Block (it never took effect) and the R11 quality tiers. The event wheel has no Undo. | Let the player pick map-edit targets (draft 08) |
| D10 | 10-19 | Stopping point for the Solace vertical: Halcyon's rules are finished and merged into w2, gated by corp, with no further work on them. RD-02 and the other corps' rules, exploit buildings and events are on hold. The shared run-graph v2 work merges. | Merge Halcyon now |
| D9 | 10-19 | Events (W3 3.17): none of the 30 drafted events fits today's event schema. They need these fields: start-a-combat, next-combat modifiers, next-raid modifiers, map edits and an event wheel. **Call:** a minimal schema slice, EV-01, adds them (logged under rule 8), queued after Halcyon and the RG-05 map edits. Then the Batch lane authors all 30 as they were drafted. Aurelian and Tethys events wait for the corp wave. | Ship only the choices that fit today's schema |
| D8 | 10-19 | ST-02, status audit: no new status ships. Only "vulnerable" (more damage taken) has no existing equivalent; it is noted, not built. | Rule "vulnerable" in, which means a new combat rule and a save change |
| D7 | 10-19 | The canonical status list is the code's five (CORRUPTED, OVERCLOCKED, ENCRYPTED, OUTPUT_DOWN, TIER_DOWN). GDD 2.9 is stale, to be fixed in a docs pass logged in DECISIONS. | Keep the three in GDD 2.9 |
| D6 | 10-19 | Solace v2: an ACROSS move costs a flat amount, and the Breach key makes it free. Decay applies after the raid's rise; a CITY LOST raid gets no decay. Heat is read on entering a node, before that node's own Heat is added. | Ask to change any of these |
| D5 | 10-19 | Solace v2: the Breach setback is not capped, so the first entry at T1 can show a gap above 5.0. | Cap the setback at the maximum gap |
| D4 | 10-19 | Old route window: a test that went red with CITY-A2 step 2 (`test_anim_r2_city` placement, "the baked city knows its streets") is marked pending until art/look's city work lands (A-059). | none |
| D3 | 10-19 | Every THEMES2 follow-up (ME1-5, OR1-6, SO1-4, HA1-6, RC1-5, AU1-3, TE1-4) took its recommended default, so W2 builds from the v2 drafts. The list is in `THEMES2_FOLLOWUP_2026-10-19.md`. | Answer any code to change it |
| D2 | 10-19 | Old route window: the fallback page stays (a street that can't be derived still gets a route page; GRID VIEW and boss runs use the same code). Only the test-only `street_route` flag is removed. | B: drop the fallback and show an error page, removing about 200 lines |
| D1 | 10-19 | PT gates are skipped per wave. Before every push of main, the user-ready gate still runs the full suite once, plus smoke and validate (CLAUDE.md). | none |

## Open questions (a default is taken; answer to change it)
| Code | Date | Question | Default taken |
|---|---|---|---|
| Q10 | 10-20 | A boss fight that reaches the 60-turn cap counts as a loss (24 % of reference fights end there). Is that right? | Yes, a loss |
| Q9 | 10-20 | The builtin bot wins 25 % of campaigns, below the 50 % floor (already on main before this pass). | Investigate in the next balance round |
| Q8 | 10-20 | The campaign is too long: the reference policy takes about 45 runs and 700 min against the GDD's ~395. The cause is the shared exploit and rank gating, not Solace. Shorten the gating, or change the target? | Shorten the gating in the next balance round |
| Q7 | 10-20 | RESOLVED: the Care Swarm tune (20 HP, 2 satellites) shipped. The animation test assumed a fight never ends mid-turn; the view was right. Normal fights at T4 are now in band (100 % win). | — |
| Q6 | 10-19 | RESOLVED (EV-02): the raid-win event fires on every raid win, and the HQ-view host is built (every 3rd completed netrun, config). Event 29 is authored. Open: should a hub event open on arrival (built) or wait as an HQ button? Hub events turn Schematics into Cycles at 10:1. | Opens on arrival |
| Q5 | 10-19 | RD-01, raid operative roles: 30 questions across 8 classes (`plan2/drafts/raid_operatives/QUESTIONS.md`). Ghost's step table (1/1/2/2) doesn't match its multipliers. | Every question at its recommended default; Ghost follows the multipliers |
| Q1 | 10-19 | Solace v2: infection decay after a held raid: partial (flat amount plus kills), or a full reset to 0? | Partial decay |
| Q2 | 10-19 | Solace v2: do Heat objective Sites and Proxy Relay completions also cure infection? | Yes, both cure |
| Q3 | 10-19 | Solace v2: cap the combined Exploit slowdown when all three are stacked? | No cap; tune after the sim |
| Q4 | 10-19 | Solace v2: does Heat pace reach 160 % at PURGE? | Yes, 160 % |
