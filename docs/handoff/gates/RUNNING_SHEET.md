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
| Q6 | 10-19 | Events: how should the raid-win host trigger (every win, or by chance)? Draft 27 is authored but dormant. Draft 29 needs an HQ-view event host that runs a fight outside a netrun; not built. | Rumor fires on every raid win; the HQ-view host is deferred |
| Q5 | 10-19 | RD-01, raid operative roles: 30 questions across 8 classes (`plan2/drafts/raid_operatives/QUESTIONS.md`). Ghost's step table (1/1/2/2) doesn't match its multipliers. | Every question at its recommended default; Ghost follows the multipliers |
| Q1 | 10-19 | Solace v2: infection decay after a held raid: partial (flat amount plus kills), or a full reset to 0? | Partial decay |
| Q2 | 10-19 | Solace v2: do Heat objective Sites and Proxy Relay completions also cure infection? | Yes, both cure |
| Q3 | 10-19 | Solace v2: cap the combined Exploit slowdown when all three are stacked? | No cap; tune after the sim |
| Q4 | 10-19 | Solace v2: does Heat pace reach 160 % at PURGE? | Yes, 160 % |
