# Netrun-failure screen (T6 FAIL branch): three designs

Art only, compositing only (PIL, numpy). Solace slice, generic names (CELL-9 // BREAKER, STREET MERC untouched). Made overnight; choices are logged below. Builds on `transitions/v3` T6 K5/K6 (hard glitch cut, 0.3 s settle, panel opens 0.30 s, input 0.60 s; reduced motion 0.25 s cross-fade).

Files: `sheet.jpg` (A/B/C plus squints), `A_crt_feed.png`, `B_route_map.png`, `C_trace_printout.png` (1920x1080), `*_placeholders.png` (same plates with amber numbered boxes on every placeholder), `keys_A/B/C.jpg` (5-frame 0.6 s glitch-in strip, plus the 3-frame reduced-motion row), `squint_A/B/C.png`, `flash_report.json`, `scripts/` (`make_all.py` rebuilds everything; `nf_lib.py` kit; `build_A/B/C.py`; `nf_trans.py` glitch).

## What the player must learn (from the GDD, nothing invented)
GDD 4.2: death is permanent for the operative and takes everything unbanked (Cycles, cards, Firmware, Daemons, unbanked assets); the campaign gains 10 + tier Heat (11.5; +5 more at ICE 6 to 10). GDD 7.3: assets banked at a Server Rack or run completion survive. Loss of the campaign is only home server integrity 0 (GDD 1.3), so the campaign continues. ART_BIBLE "Run failed": never a black void; the city grades grey; FLATLINED; stats as a receipt. Every design shows the same facts so they are comparable:

1. It is over: SIGNAL LOST / NETRUN LOST / INTRUSION TERMINATED, operative FLATLINED, HP 0/60.
2. Where: SEED VAULT EXCHANGE, node 5 of 7 (elite router), last fight THE ADJUSTER turn 2.
3. What was lost with the operative (five unbanked categories) vs what is kept (banked Schematics and Armory, home server 50/50 holds).
4. The campaign price: Heat 52 to 63 (+10 +1 tier), crew 4 to 3.
5. The way out: one button, GRID VIEW [G] (label from the r42 route page; T07 returns a lost netrun to the raid view).

## Designs

**A, CRT feed cuts to signal lost** (`A_crt_feed.png`, `keys_A.jpg`). The netrun street feed (r6 street frame, greyed, tracking bands, static, chroma split) is what is left on screen; SIGNAL LOST in RGB-split Anton; the Breaker tile in the bible's flatlined state (greyed, static, red pencil X, flatline, FLATLINED stamp); a clean-text DISPATCH panel (GDD 8.2: never zine-styled) says what happened in four lines; a RUN LOG terminal panel (r42 chrome, pink edge for loss, red chips for losses, green for kept) carries the facts; heat meter reuses the route-page bar. Most literal to the storyboard (K5 tear lands on the same feed language) and the most information.

**B, the route, struck** (`B_route_map.png`, `keys_B.jpg`). The 7-layer node route on the dimmed r42 city: walked nodes lime with checks and tags (ROUTER 1, 2, 3, TERMINAL 4, matching the r42 loot and event screens), the failed elite router ringed and crossed in red grease pencil with LOST HERE and a fallen operative token, unreached nodes ghosted, the link out of the loss cut. The route-page top HUD is reused with the loss written on it (Heat 63 +11, HP 0/60, Cycles 160 struck to 0). Right terminal panel NETRUN LOST with the ledger. Best at showing where and how far.

**C, Solace prints the trace report** (`C_trace_printout.png`, `keys_C.jpg`). In the corp's voice: a green-bar tractor-feed printout hanging out of a printer slot over the blurred, dimmed street with red and pink searchlights (Heat feedback, GDD 9.4): SOLACE BIOSYSTEMS security ops INTRUSION TERMINATED, the same facts as a table (the kept items become "NOT REACHED / NOT BREACHED", which tells the player what survived by the corp's failure), a heat bar, a scorched corner, a red TRACE BURNED stamp, and one yellow post-it from the Cell. In the same folder language as the Solace end screens, so it ties the failure to the campaign-end dossier. The riskiest and loudest.

## Glitch-in (0.6 s) and reduced motion
Key frames at 0.00 / 0.12 / 0.20 / 0.34 / 0.60 s for each design (`keys_*.jpg`): combat plate p1_decide (REAL), HUD out and board tears, hard cut to the new feed with the tear still on it, the panel opens as the tear settles (0.3 s), settled and input live. The tear only moves rows (no brightening, no white flash); the cut is one luminance step. Reduced motion is the 0.25 s cross-fade (three frames at the bottom of each strip). With reduce-effects on, tear, static, scanlines and chroma split drop out; no effect carries information.

Flash check (`flash_report.json`, 60 fps simulation of the same code, mean and per-pixel linear luminance): no frame-to-frame area change of 0.10 or more covers 25 percent of the frame, so no WCAG-style flash pair in any design (max area changed 0.08 to 0.09 for A and B, 0.09 for C); the strict perceptual proxy counts 0 reversals for A and B and 1 for C (the darker plate to the bright paper), which is 1.67 per second extrapolated. Limit is 3 per second. Honest limit: this is a whole-frame proxy at 480x270, not a certified flash analyser.

## Squint (1/16 plus blur 0.7; mean / p95 / loud share above 0.38 luminance)
| | mean | p95 | loud |
|---|---|---|---|
| combat plate p1_decide (what we cut from) | 0.19 | 0.39 | 5.7 % |
| A | 0.14 | 0.39 | 5.2 % |
| B | 0.15 | 0.30 | 1.7 % |
| C | 0.26 | 0.67 | 31.6 % |

A and B sit at or under the combat plate, so the cut does not read as a flash up; A's first read is SIGNAL LOST then the run log, B's is the red X and the lime route. C is a big bright paper (31.6 percent loud even after a lamp-fall-off gradient); it reads best as an object but is the loudest screen in the project and would need a dimmer paper or a narrower sheet to match the family.

## Placeholders (amber boxes in `*_placeholders.png`; number = tag)
1. Node reached, "ELITE ROUTER 5 OF 7" (node 3 router and node 4 terminal come from the r42 loot and event screens; 5 is mock).
2. Last fight, "THE ADJUSTER, TURN 2": read off the combat plate (KILL ADJUSTER, turn 2); whether the game records the killer is assumed.
3. The unbanked-loss values (Cycles 160, 18 cards, 1 Firmware, 1 Daemon, 1 asset). Categories are GDD; numbers are mock (160 matches the event HUD).
4. Heat 52 to 63: "+10 +1 tier" assumes tier 1 and ICE below 6. 63 crosses the minor-60 line (a netrun complication); no design announces that.
5. Crew 4 to 3: inferred from "operative permanently lost"; CREW exists on the Run HUD.
6. Home server 50/50: standard slot is 50; the live value is mock.
7. DISPATCH copy (A, B) and the Cell post-it (C): wording invented; whether DISPATCH speaks on this screen is a decision. The voice rule (clean text) is GDD 8.2. Optional, not drawn: a DISPATCH timestamp tell (GDD 8.2 "replies before messages").
8. Button label/destination GRID VIEW [G]. No second button: the old concept's "view trace log" is dropped because no such screen exists.
9. Rank "R1" and the kept list ("Schematics, Armory"): which items are banked depends on the run.

Not shown on purpose (unknown to the design docs): what happens to the Site (T07 shows the raid node with a pink X; used-up or retryable is not stated), a reward or XP screen, a per-run stats history, the Heat threshold event.

## Recommendation
**A for T6**, with B's red-grease X as an optional echo on the raid-view node in T07. A continues the K5 glitch into the same CRT language, holds the most facts in one read, stays at the plate's squint level, and its flatlined Breaker tile is the ART_BIBLE state. B is the clearest "where did I fall" picture and the right second screen if the run needs a postmortem; it is the one to build if the team wants the failure to teach route planning. C has the best in-world tie to the Solace dossier ending but is the loudest, shows a corp-voice screen where the Cell is the player, and its "TRACE BURNED" stamp could be misread as the combat Trace meter (the cause line says HP 0, the stamp is flavour; rename if kept).

## Choices log (made overnight without asking)
1. All three share one fact set (above) so the choice is about presentation, not content. Numbers are mock and tagged.
2. Failure panels use pink edges (Cell hue, lose-screen Bloom family) with HARM red for losses and GAIN green for what is kept; cyan stays for ours (DISPATCH, HUD). Solace identity by material and crest only (C).
3. Fonts per BRIEF 3.4: Anton, Share Tech Mono, Plex; Courier Prime for the corp printout; smallest text on the plates is 18 px at 1080p.
4. The old v3 concept line "rewards forfeited, heat +2" is dropped: GDD 11.5 says +10 + tier.
5. The failed node is "ELITE ROUTER 5 OF 7" to fit the r42 event screen (node 4 of 7) and the plate's Adjuster.
6. Session note: one empty `python -` heredoc was run by mistake early on (it executed nothing); every build after that ran from script files.
