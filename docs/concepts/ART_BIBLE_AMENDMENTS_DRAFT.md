# ART_BIBLE amendments (draft, 2026-10-30)

Status: draft for designer review. ART_BIBLE.md not edited.

## Part 1: superseded sections

| Section | (b) Old text (summary) | (c) Proposed new text | (d) Source |
|---|---|---|---|
| 1.2 World row, "Exception" clause | Netrun street, route page, HQ netruns and city night views use AAA-2 "Realistic night" (PBR, no toon bands or ink) | One continuous cel look from city to street, zoomed in. The netrun, route page and HQ netrun use the city's cel + ink look (Cv2 + E); AAA-2 is removed from the netrun. The golden plates `street_overview.png` and `hq_rebel_cell_overview.png` are the bar for detail and polish. | ART CALL 46, item 1 (2026-10-30) |
| 1.2 World row, "The entry dive blends one look into the other on shared geometry (4.6)" | Entry dive blends Cv2+E into AAA-2 | Superseded with the AAA-2 exception: no look blend is required; the entry uses the single cel look. | ART CALL 46, item 1 |
| 1.2 Grease pencil row, "orange (`RING_AVAILABLE`) = the netrun plan" | Orange is the netrun plan colour | Not superseded by the files. The 2026-10-15 orange ruling stands; no ruling in the files changes it. | Not superseded by the files |
| 1.2 "Rejected" list, "X1–X3 cyberspace (no wireframe city)" | Route view rejects X1–X3 | Not superseded by the files. | Not superseded by the files |
| 1.2 "Rejected" list, "painterly or neon-painting cities" | (rejected) | Not superseded by the files. | Not superseded by the files |
| 2.4 Corporation palettes | Corp palettes, MERIDIAN and HALCYON etc. | Not superseded by the files (palette values). The Meridian landmark is affected by the Meridian hibernation ruling (see the Meridian entry below). | Not superseded by the files (palette values); Meridian landmark superseded by Meridian hibernation ruling |
| 3.14 Combat backdrop, "Map = close-up rule" and "Per corp" table | Backdrop per corp (Meridian crane, Solace helix, Halcyon Civic Core, Orbital silo, REBEL_CELL canyon); boss backdrop is the corp HQ close-up | Backdrop is a cutaway: the chosen building on the netrun street, opened on its street, with one room type per Site role (bio-lab, server room, greenhouse, records/office, lobby) themed by corp (corp colour on trim and light). The lobby band is kept as the default context strip. | ART CALL 47 (combat backdrop: cutaway); cutaway v2 review 2026-10-30 (designer answer: one room type per Site role, themed by corp); ART CALL 46, item 4 |
| 3.14 "Fight won" and "Framing" | Lit close-up of HQ, Meridian boss crane | Superseded where the cutaway replaces the HQ close-up; the lit-building recolour on win is not mentioned in the files and is not changed. | ART CALL 47 (cutaway) |
| 3.22 "Pink has one job: unit screens" | Pink reserved for unit screens only; CELL-9 sticker cyan; SEND IT yellow; lane/next-turn trim pale blue | "Pink has one job" is loosened: pink may be used where it serves the theme and polish, case by case. | ART CALL 46, item 3 (2026-10-30) |
| 4.6 Netrun look, "AAA-2 look" | Netrun structure and route view use AAA-2 "Realistic night" look | Netrun look is one continuous cel look from city to street (Cv2 + E + ink), zoomed in; the golden plates are the bar. | ART CALL 46, item 1 |
| 4.6 Netrun route view traffic line "light streaks only, no car models" | Netrun traffic is light streaks only, no car models | Not superseded by the files for the rule itself. Per the 2026-10-30 traffic ruling, corp-colour light streaks and cars swap at 200 px/s (see 2c). The "no car models" clause is changed by ruling: streaks at speed, cars below the swap threshold. | Traffic ruling 2026-10-30 (corp-colour traffic adopted); ZOOM_RULES §2.4 |
| 4.6 Netrun "Transition" wording (entry flow, wheel-free dive, AAA-2 blend) | Entry dive: one camera path, route rooms hidden until street, walls dissolve; blends looks | Wheel slap and wheel lens are dropped (unchanged); the look blend is removed; transitions are re-storyboarded per ART CALL 49 (see Part 3 and 2f timing). | ART CALL 49 (transitions list, 2026-10-30) |
| 4.6 Route view "Connections are grease pencil... Traffic is light streaks only, no car models. The look is AAA-2 (1.2)." | As above | Look: cel (1.2 revised). Traffic: streaks plus corp-colour car swap per 2c. | ART CALL 46 item 1; 2026-10-30 traffic ruling |
| 4.7 HQ netruns | HQ netruns use route-view rig with AAA-2 look | Look changes to cel per ART CALL 46 item 1; the route-view rig and rules are unchanged. | ART CALL 46 item 1 |
| Meridian entries (4.4 Meridian HQ; 2.4 Meridian row; 3.14 Meridian boss/regular Site; 4.5 Site labels; 4.7 Meridian compound/mechanic) | Meridian active with its own HQ, Site set and HQ mechanic | Meridian is hibernated. Every active name, work order, Site name and THREAT INTEL line is Solace. Meridian art is not produced; no Meridian element is active in the slice. | Solace-only slice ruling, ART CALL 46 item 7 (2026-10-30) |
| 4.7b Corp-wide themes, "Meridian, Orbital: still open" | Meridian theme open | Meridian is hibernated; its theme is not drawn. | ART CALL 46 item 7 |

Sections checked and found not superseded by the files: 1.2 "Words" row except as noted; 2.1–2.3, 2.5–2.10; 3.1–3.13, 3.15–3.21; 4.1–4.5 (except Meridian entries); 4.8–4.14; 5; 6; Appendix A–C. The 3.22 remainder and 4.7 remainder are not superseded beyond the items above.

## Part 2: new sections

**2a. Netrun look: one continuous cel look from city to street, zoomed in.**
Rule: The netrun (street, route page, HQ netrun, city night views for the netrun) uses the same cel look as the city: Cv2 faceted low-poly, 3 hard toon bands, ink from id/normal/depth, light spill, grime. The golden plates `golden_plates/street_overview.png` and `hq_rebel_cell_overview.png` are the bar for detail and polish. The city zooms into the street without a look change. Source: ART CALL 46, item 1 (2026-10-30). Supersedes 1.2 Exception and AAA-2 wording in 4.6.

**2b. Zoom bands and per-element detail.**
Rule: Five zoom bands (City, District, Near-street, Street, Close) are set by screen pixels per building unit (ppb). Thresholds and transitions: City below 8 ppb; District 8–16; Near-street 16–28; Street 28–56; Close 56 and over. Each city element gains detail in phases tied to these bands. Per-element phase tables, the street camera (40° FOV, eye 4 m, horizon at 0.74 of frame height), and the transition rules are in `netrun_cel/zoom_rules/ZOOM_RULES.md` (link: netrun_cel/zoom_rules/ZOOM_RULES.md). Not restated here. Source: designer ruling 2026-10-30 (DIRECTION_REVIEW "Godot zoom prototype review" and "Netrun zoom rules"); ZOOM_RULES spec review 2026-10-30.

**2c. Corp-colour traffic.**
Rule: Traffic light and car colour takes the corp hue. Roads and highway surfaces stay neutral grey; only light lines carry the traffic colour. Tunes: surface traffic 1.4x speed; light gain as set in the traffic tune; highway decks 3.5x; the streak swap at 200 px/s on screen; car head = corp hue, tail = darker shade of the corp hue (no white). Source: traffic corp-colour ruling 2026-10-30 (adopted), with tunes per the review entries of 2026-10-30.

**2d. Staged netrun street.**
Rule (ART CALL 48): the netrun route street is widened to about 3x the current road width; facing row heights are kept; netrun nodes are placed only on visible floors so no tall facade is cut at the top; the street is lit and wet (storefront band, reflection, lamp row, car streaks); the surrounding city stays real, with procedural detail added on top. Source: ART CALL 48 (2026-10-30).

**2e. Folder-memo end-screen language.**
Rule: Win and lose end screens take the form of a corp internal memo in a manila corp file. The campaign-start folder is the mirror. Structure: open manila corp file with crest tab, hazard strip, routing slip, ROUTED/FILED stamps and TO/FROM/RE memo. Image slot B: the Solace aerial survey map with the Cell's network drawn in grease pencil. WIN: the network is marked in red grease pencil. LOSE: every node is crossed out and the Bloom spreads. Start page (G7) shows the folder open with other corps closed behind it, bookending the end screen. Source: ART CALL 47 (folder, D1); folder v2 review and designer pick (image slot B), 2026-10-30.

**2f. Cutaway combat backdrop.**
Rule: The combat backdrop is a cutaway of the chosen building on its street. One room type per Site role: bio-lab, server room, greenhouse, records/office, lobby. Corp colour sits on trim and light. The lobby band is kept as the default context strip (art-pass default, pending designer confirmation). Rooms are built from procedural interior modules (kit v2). Source: ART CALL 47 (cutaway as combat backdrop); cutaway v2 review and designer answer (one room type per Site role, themed by corp), 2026-10-30.

## Part 3: loosened rules

1. **Pink use (ART_BIBLE 3.22, "Pink has one job: unit screens").** Designer's exact words: "Pink may be used where it serves the theme and polish, case by case." Numeric limit: No numeric limit given: unknown.
2. **Rules may stretch for the look (general).** Designer's exact words: "rules may stretch, bend or break to get there, and the designer wants to see the result." Numeric limit: No numeric limit given: unknown.
3. **Netrun AAA-2 realism exception (ART_BIBLE 1.2).** Loosened to "one continuous cel look"; the exception is removed. Numeric limit: No numeric limit given: unknown.
4. **Traffic "no car models" in the netrun (ART_BIBLE 4.6).** Designer's ruling: streaks at 200 px/s on screen, car models below it. The threshold 200 px/s is numeric and given in the files. Other numeric limit: No numeric limit given: unknown.
5. **Netrun entry flow wording (ART_BIBLE 4.6).** The "wheel-free dive" and "lit building" wording is replaced by the 12 transitions in ART CALL 49: a camera zoom to the netrun street, with no wheel-circle zoom. Numeric limit: none given (timings are in transitions/v2/STORYBOARD.md, proposed by art-pass).

## Part 4: open items

- E10 micro-detail polish: designer says "a ton of the micro details and sub-elements of the combat plate could be improved, but as a whole it meets the visuals we want." Queued after the backdrop pick. Final: unknown.
- Halcyon win dossier: reads as a defeat (STATUS PROCESSED, CASE CLOSED). Numbers on the Solace win screens are placeholders. Game-data fix owed. Decision: unknown.
- Netrun camera framing choice: ZOOM_RULES open items (long lens vs wider fov; dolly along the route vs one frame; node anchors; palette grade; reflections method; night only). Designer pick needed: unknown.
- Solace data renames: A-112 (hauler, courier, sink_the_cargo_logs ids on plates; game data is build's job). Status: unknown.
- Lobby band question for the cutaway: keep the lobby as context strip or crop for a bigger room. Designer answer: unknown.
- Traffic corp-colour: designer has evaluated and adopted; final GIF look approval pending: unknown.
- Transitions storyboard v2: 10 assumptions in STORYBOARD.md awaiting designer answers; E10 plate still has the old backdrop. Status: unknown.
- Win/lose screens for corps other than Solace: concepts requested, starting with Solace. Status: unknown.
- Meridian: hibernated; its HQ art, Site art and mechanic remain unknown for reactivation.
- Perf of the zoom prototype not measured on a quiet GPU: unknown.
- Day look for the netrun: not specified: unknown.

Amendments: 12 superseded entries, 6 new sections, 5 loosened rules (the Part 1 rows marked "not superseded" are not counted).