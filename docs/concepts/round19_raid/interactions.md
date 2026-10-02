# Round 19: raid interactions and their feedback

This list covers every player-facing interaction and state in raid setup (GDD 7.1) and the playout (GDD 7.2). Each entry gives the feedback and the **medium** that carries it. Example crops are in `interactions_sheet.png` (01–12), `interactions_sheet_2.png` (13–24) and `interactions_sheet_3.png` (25–29).

**Mediums:**
- **INLAY:** the street-plane circuit decal (sockets, links, lanes, rings). The tactical truth always lives here.
- **STICKER:** used only for things that never change: defence and node cards, buttons, the screen title, final result stamps. The sheen is subtle at rest; a slow, occasional sweep plays on one sticker at a time.
- **PENCIL:** grease pencil, for plans (yellow) and *static* tactical states (red). A pencil mark never shows something the rules don't do.
- **TERMINAL:** the CRT panel in the C screens and data language, for anything that changes (feed, forecast numbers, speed, Heat).
- **FLOAT:** diegetic hit feedback: binary shards, rising numerals and thin holo bars (live option L3).

**Rules check:** taken from `scripts/core/raid_resolver.gd`.
- Only DECOY and HONEYPOT (`decoy_pull`) change routing. Turrets, Flak and Railgun never re-route.
- A threat stops at each live node it enters.
- A node reaching 0 is Disabled, and 50% of the excess damage cascades to its claimed neighbours. A Disabled node that is hit again is Seized.
- Threats still on a node at the end Seize it.
- The Vault is a priority target only for HIGHEST_VALUE threats (raid_priority). It is not a general target.

## Setup

| # | Interaction / state | Feedback | Medium |
|---|---|---|---|
| 01 | Pick up a defence | The card peels off the tray and follows the cursor with a lifted shadow. Every socket that can take it lights a white frame. | STICKER + INLAY |
| 02 | Hover a valid node | The socket shows a white frame and its dashed forecast ring re-projects live (e.g. amber > green). A yellow pencil arrow + circle connects card and node. The IF PLACED terminal shows the outcome and home change. | INLAY + PENCIL + TERMINAL |
| 03 | Route redirect preview | Only shown when the defence changes routing (DECOY / HONEYPOT). The old route stays as a ghost lane. The new one is a dashed red lane on the street, with a dashed red pencil arrow at the turn. Example: DECOY on RELAY pulls route B off the Firewall road. *The coordinator's example used a Flak Array; per GDD 7 / the resolver, guns never re-route, so the example uses DECOY.* | INLAY + PENCIL |
| 04 | Invalid drop | A red frame + X on the socket (seized, no free asset slot, or not a node). The card springs back to the tray. | INLAY + STICKER |
| 05 | Defence placed | A lime ripple spreads from the socket, the unit model drops in, and the tray count goes down. The forecast numbers tick in the terminal. | INLAY + TERMINAL |
| 06 | Remove a placed defence | Drag the unit off its socket onto the tray (dashed yellow pencil while dragging). The card returns +1 and the forecast ring re-projects. | INLAY + PENCIL + STICKER |
| 07 | Move / swap between nodes | Drag from node to node; both forecasts update. Dropping on an occupied slot swaps the two units. | INLAY + PENCIL |
| 08 | Forecast changes | The dashed ring colour shows the projected outcome (green holds, amber disabled, red seized). The terminal numbers count to their new values (`HOME 42 > 45`). | INLAY + TERMINAL |
| 09 | Link frozen / sealed / jammed (pre-raid) | LOCKDOWN UNIT freezes the busiest link to home: the trace frosts ice-blue and nothing routes or shoots across it. A Customs / Tow / Jammer seal appears when the unit passes during play. | INLAY |
| 10 | Threat routes revealed | Red trace lanes run from each corp entry socket (violet, corp glyph). Pencil circles + letters A/B/C match the THREAT INTEL rows. | INLAY + PENCIL + TERMINAL |
| 11 | START DEFENSE | The single sticker button. On press it squashes ("slap"), then the tray peels away and the playout starts. | STICKER |
| 12 | Day read | No fog at this zoom. The inlay keeps lime and the status colours. | INLAY |

## In progress

| # | Interaction / state | Feedback | Medium |
|---|---|---|---|
| 13 | Wave incoming | The entry socket emits expanding red rings. Red pencil circle + INCOMING (a static state until the wave spawns). The terminal shows `NEXT WAVE STEP n`. | INLAY + PENCIL + TERMINAL |
| 14 | Threat moving | Each corp vehicle has a red ring on the street; its lit segments show HP. The lane ahead of it brightens. | INLAY + 3D |
| 15 | Defence fires / hit | A tracer from the unit, binary 0/1 shards from the hit point, and a damage numeral that rises and fades. The feed logs the shot. | FLOAT + TERMINAL |
| 16 | Threat held (ICE LOCK / Tar Pit) | The ring turns into an ice crystal for the hold steps. | INLAY |
| 17 | Threat lured (DECOY) | A dashed lane bends toward the decoy's node (`move.decoy` event). | INLAY |
| 18 | Unit destroyed | The ring breaks into a grey X on the street. A pencil X + DOWN stays as the record. | INLAY + PENCIL |
| 19 | Node hit / damaged | The integrity track drains clockwise from the pin-1 notch, turning amber below 2/3 and red below 1/3. Cracks spread and a surge runs down its link. | INLAY |
| 20 | Node disabled + cascade | The frame goes to dashed amber, the pins go dark, the glyph flickers and the riser dims. The 50% excess surges along the links into the neighbours' tracks. | INLAY |
| 21 | Node seized / overrun | A disabled node hit again (or a threat on it at the end): violet corp hatch, corp glyph, dead links and riser. The building sign switches to the corp mark. Pencil LOST. | INLAY + PENCIL |
| 22 | Node lost (report) | The seized node is removed: a burnt socket with embers, until it is reclaimed + reinstalled. | INLAY |
| 23 | Threat reaches home | The CORE track drops with a pink flash and `HOME 50 > 41` in the terminal. | INLAY + TERMINAL |
| 24 | Spotlight targets a node | The chopper circles above and its pool wobbles over the node. **PROPOSAL (needs a GDD decision):** a spotlit node is *exposed*, taking extra damage this step, shown by white hazard ticks round the socket. | 3D + INLAY |

## End of the raid

| # | Interaction / state | Feedback | Medium |
|---|---|---|---|
| 25 | Heat escalation event | A threshold is crossed mid-run (25/50/75): another chopper enters from the frame edge and a terminal banner names the rule (e.g. `RAID STRENGTH +25%`). | 3D + TERMINAL |
| 26 | Wave cleared | The lanes drain, the entry sockets dim, packets flow home again, and the terminal shows `WAVE 1/2 CLEARED`. | INLAY + TERMINAL |
| 27 | Successfully defended | Every socket turns green and a pulse runs the whole network. The final result stamp (CELL HOLDS) is a sticker because it never changes. | INLAY + STICKER |
| 28 | Raid lost / home breached | The CORE socket burns out. Pencil BREACHED; the terminal shows `CAMPAIGN LOST`. | INLAY + PENCIL + TERMINAL |
| 29 | Speed / skip | The 1x / 2x / 4x / SKIP terminal strip with a step counter. | TERMINAL |

Not drawn as tiles, but covered by the same language:
- **Post-raid report:** a terminal page with the per-node outcomes; each row uses the socket icon from the key.
- **Stationed operative recalled:** the safehouse sign blinks and the operative card returns to the roster.
- **Asset destroyed:** its model breaks and its socket slot empties (the track doesn't change).
- **Icebreaker opens a locked link:** a new trace is cut into the street with sparks, then stays lit.
