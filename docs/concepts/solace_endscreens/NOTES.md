# Solace win / lose screens: 3 directions (art-pass concept job, 2026-10-30)

Six 1920x1080 concepts, `sheet.jpg` for the overview. Scripts in `scripts/` (PIL + numpy, 2x supersampled; `ui_lib.py` is the shared chrome).
Chrome kept: vinyl stickers (Anton, ink, white die-cut) for MAIN MENU / NEW CAMPAIGN (pink, allowed per the 2026-10-30 ruling) and result words, Share Tech Mono CRT, Courier corp paper. City art is `tide_raid/G1_parity/r42/plan_r42.png`, with the under-UI grade on D2.
No Meridian names. Only the data fields of the Halcyon screens are shown, nothing new.

| Dir | WIN | LOSE |
|---|---|---|
| D1 Specimen file | `d1_win.png` Biosafety "CONTAINMENT REPORT": the Cell is a colony in cyan/pink/Cell-lime growing on lime agar and crawling out of the dish; stamp CONTAINMENT FAILED. | `d1_lose.png` "CERTIFICATE OF TREATMENT": the same dish bleached clear, dead grey specks, STERILE stamp, WIPE IN countdown. |
| D2 Helix from the city | `d2_win.png` r42 helix hacked: lime to cyan, glitch bands, Cell-lime halo, the Cell's node network over the park; CRT campaign audit; CELL HOLDS sticker. | `d2_lose.png` the Bloom (pink veins) has taken the whole city, one lime island stays round the helix; Solace NOTICE window "YOUR CELL HAS BEEN TREATED", TREATED stamp. |
| D3 Solace Live | `d3_win.png` the news feed seized: torn, RGB-split headline "CONTAMINATION CONTAINED" struck and replaced by FAILED, hacked helix footage, CRT audit window. | `d3_lose.png` clean bulletin "CONTAMINATION CONTAINED", calm lower third with the data. |

## Data shown (from the Halcyon screens)
- Lose: HOME SERVER 00/50, nodes encrypted 6/6 (Solace verb: STERILISED), WIPE IN 00:02.80, "no appeal is offered", the corp verb (TREATED / STERILE, from the round-20 house-style row).
- Win: subject, duration, status, netruns, raids, exploits, schematics, network at closure, home server, heat graph, operatives list.
- **Flag for build/designer:** the Halcyon `campaign_dossier.png` (labelled win) reads as a defeat: STATUS PROCESSED, home server 0/50, CASE CLOSED, "operatives lost". The WIN values here are placeholders (field set unchanged, numbers made to fit a win). The real win data is a game-data question, not art's.
- Heat peak on LOSE is shown as 100 (placeholder).

## Method / references
- Web research was thin (search returned mostly stock and AI-image pages). What informed the choices:
  - Biosafety paperwork and Petri-plate looks (ink-outlined colonies, a cleared bleach ring).
  - Broadcast news-bug and lower-third layouts for D3; glitch/tear feed seizure as in hacking-game takeover screens (from general knowledge, no single cited source).
  - Own earlier art: round-20 `campaign_lost.png` (house-style lose, the verbs), the round-21 dossier (layout), `solace_vertical/bloom` (necrosis veins, the 90 % island), r42/r43 city.
  - Game-over screens that name the victor in their own voice (the round-20 recommendation) rather than a bare GAME OVER.
- Squint: D1 reads by dish + big paper; D2 by helix colour (cyan vs lime), the one message; D3 by headline word shape.

## Own pick: D2 (helix from the city)
It is the only one in the same world as the rest of the game (the r42 city, the helix, the Bloom), and its WIN/LOSE swap is one clear colour story (lime to cyan vs pink swallowing the city). It also reuses real city art that will exist in Godot. D1 is the most charming and the cheapest to build (2D UI only). D3 has the best voice (clean vs seized) but a flat background.

## Notes for polish
- The D2 helix recolour is a hue shift of a 2x-upscaled r42 crop (soft). Final should be a Godot render of the helix at closer zoom with a Cell-colour material.
- Solace lime (#96FF46) and Cell lime (#D4FF00) sit close in D2 WIN (halo, graph); the colour-blind pass should check them.
- Pink is used on the Bloom veins, REBEL_CELL stickers and NEW CAMPAIGN, per the 2026-10-30 ruling.
