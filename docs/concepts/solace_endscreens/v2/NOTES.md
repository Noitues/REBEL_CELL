# Solace end screens v2: the corp file folder (ART CALL 47)

Designer: D1, "the corporation internal memo on your activities", mirroring the campaign start where you choose a corp file folder. Image slot to be the D2 view; open to other ideas.

## What changed from D1
- The bench and Petri dish are gone. The screen is one open **manila folder** on the bench: Solace crest tab (SB-7718 // CELL-03), lime/black hazard strip, paperclip, tape, **routing slip** (ticked departments, initials MO / RK / TL, ACTION note), ROUTED / FILED stamp, and the **internal memorandum** (TO / FROM / RE, same fields as before). Kept: sticky notes, M.OKAFOR signature, sample log of operatives, MAIN MENU / NEW CAMPAIGN.
- WIN memo is "ACTIVITY OF CELL-03", routing action NOTE + PURSUE, stamp CONTAINMENT FAILED. LOSE memo is "DISPOSAL OF CELL-03", action NOTE + CLOSE, all four boxes ticked, stamp STERILE, FILED.
- Same data as the Halcyon screens. Win numbers and the lose heat peak remain placeholders (flag from v1 stands: the Halcyon "win" dossier reads as a defeat).

## The image slot (WIN / LOSE each)
| | WIN | LOSE |
|---|---|---|
| **A helix print** (`win_A`, `lose_A`) | Glossy taped 8x10 cropped from the 2560 Cycles golden plate `hq_solace_overview`: helix hacked lime to cyan with torn scan bands, halo to Cell lime, the Cell's network inked over the park, camera burn-in "CAM H-07 HELIX PARK 23:41". | Same print, Bloom veins over the city, one lime island, lower helix turning pink. |
| **B survey map** (`win_B`, `lose_B`) | Solace aerial survey of the r42 city (faded, grid, title block) with the Cell's network in red grease pencil, circled and numbered. | Network crossed out node by node, one big slash, "network lost. do not restore.", the Bloom crawling in from the edges. |
| **C CCTV strip** (`win_C`, `lose_C`) | Three film-strip frames of the operatives (Breaker, Ghost, Rigger busts) in green camera look: REC, corner brackets, "ID MATCH". | Same frames darkened, [ REDACTED ] bars, RECLASSIFIED. |

Sharpness: A is cropped from the 2560x1440 plate at about 1:1 into a 400x500 print (supersampled 2x), so no soft upscale. B uses the 1920 r42 plan at about 0.4x, so it is crisp but lower in city detail than A. C uses the round-39 busts (low-poly, fine at this size). The r43 images (02/03/04) were not used; they are raid beats with their own marks, and the HQ plate is the one that carries the helix at polish quality.

## Start page (G7) and bookends
`start_page.png`: the Solace folder is chosen and open in front, tab with crest, marked "SELECTED" (stamp) and ringed in yellow grease pencil (yellow = our plan). Halcyon, Orbital (locked, 160) and Classified (opens at ICE 10) stand as closed folders behind, in their own tints. Left page: CORPORATION (Solace, best ICE 6), ICE DIFFICULTY 0-13 stepper, HOME SERVER five slots (Standard chosen, others locked with costs). Right page: CREW as polaroids (Breaker chosen, Ghost, six locked with costs). Only the pickers the GDD already lists. Stickers: NEW CAMPAIGN, TRUST NO ONE, START (pink), BACK.
Data and unlock costs are taken from the round-44 `new_campaign.png`, which the build uses. Meridian is not shown (hibernated). Dropped from that page: city seed, today's run and share codes (not in the G7 list). Say if they should come back.
`bookends.jpg`: start, WIN, LOSE side by side; same folder, desk, crest tab, hazard strip and paper, so the campaign reads as one file opened at the start and closed at the end.

## Squints (`squint_*.png`, `squints.jpg`; 1/16 scale blur)
All pages read as the same shape: dark desk, a tan two-page folder, bright memo on the right. First read is the white memo, then the stickers/stamps. Of the image slots:
- A WIN: cyan helix against dark city reads as a cool vertical on tan; best and clearest read. A LOSE: pink veined block, clearly different from WIN at a glance.
- B: WIN is a grey-green block with red marks, LOSE a magenta block; distinguishable but the map is the weakest as a picture.
- C: a dark strip with green blobs; the least readable at a squint but the most narrative up close.
- Start page: the yellow grease rings plus pink START read first, as intended; the closed folders sit back.

## Pick for the image slot: A (the glossy helix print)
It is the only option that carries polish-level art (a real render of our HQ), it reads in one glance at squint, and WIN/LOSE are one colour story (cyan hack vs pink Bloom) that matches the lose-screen Bloom and the Godot city. B is the best "story" (the player's own network as a grease-pencil plan, then crossed out) and a good second: it reuses the grease-pencil language and could even be generated from the real network data in Godot, which A cannot. C is charming but uses small low-poly busts and is hard to read at size.
Suggested combination if wanted: A as the main print, with B's grease-pencil network drawn on A on WIN (already done lightly) and the crossed-out node marks on LOSE.

## References
Real-world: manila case folders with tab labels and routing slips (government/corporate circulation slips with department checkboxes and initials), glossy surveillance prints taped to a file, CCTV contact sheets and film strips, survey maps with grid references and title blocks. Own: `round44_undesigned/B_menus/campaign_slots.png` and `new_campaign.png` (folder tabs, tiles and unlock data), `golden_plates/hq_solace_overview.png`, `solace_vertical/bloom/A3d_*` (Bloom), round-20/21 dossier layouts.
Scripts: `scripts/` (`v2_lib.py` paper and folder helpers, `prints.py` the three slots, `make_v2.py`, `start_page.py`, `fin.py` sheets). `vor.py` replaces scipy.spatial, whose import hangs on this machine.
