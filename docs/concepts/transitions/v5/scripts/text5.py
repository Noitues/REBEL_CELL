"""Text for transitions v5 (designer rulings on v4, build's B-105 / DECISIONS 2026-11-16 "transitions v4 rulings").
Changed transitions are written out here; unchanged ones (T6, T7, T8) are taken from v4's text4.py (a verbatim copy in
this folder). T10 is HELD (ruling 7) and lives in archive/. Every 'chg' line is the change vs v4 with the ruling number."""
import copy
from text4 import TEXT as V4

V4D = {t['id']: t for t in V4}
TEXT = []


def add(**k): TEXT.append(k)


def keep(i, **over):
    t = copy.deepcopy(V4D[i]); t.update(over); TEXT.append(t)


# jack beats at half the animatic (art/jack-6s 980f31f1a, ui_motion.tres): terminal 0.70, rain 0.625, collapse 0.225,
# dive 1.50, reveal 1.82, mark 0.50, mark hold 0.40, zoom 0.50, settle 0.25; select hold 0.30 (jack-out only)
add(id='t01', file='t01_city_to_netrun_street.jpg', status='changed',
    title='T1  City map to netrun: pick a site, jack in, zoom to the exact building on its real street',
    dur='6.52 s from JACK IN to CHOOSE (art/jack-6s: every entry beat at half the animatic); one press skips all of it',
    ease='terminal: type-on; rain: linear; CRT collapse: ease-in; dive: CityZoomTo path (push on the lot, then the dolly), no overshoot; reveal: linear left to right; zoom to the start room: ease-out cubic, 0.25 s settle',
    labels=['K1  0.00 s  city map, site picked, JACK IN pressed', 'K2  0.35 s  Cell terminal types the jack line (0.70 s)',
            'K3  1.00 s  binary rain on the chosen link only (0.625 s)', 'K4  1.45 s  terminal despawns: CRT collapse (0.225 s)',
            'K5  1.55 s  dive starts: the real city, the site building marked', 'K6  2.07 s  dive: District band, push on the lot',
            'K7  2.53 s  dive: Near band, the dress builds in', 'K8  3.05 s  landed: the real street at the building, rooms shut',
            'K9  3.96 s  REVEAL: room walls break to bits, links write on', 'K10 6.52 s  marks drawn, start room: CHOOSE'],
    cam='Bible 4.6 chain, one camera path, no cut. The terminal and the CRT collapse sit over the frozen city map (0-1.55 s). The dive (1.55-3.05 s) is art/zoom-to-building: CityZoomToRun plays over entry_dive, the camera pushes on the exact lot of the site building, then dollies down into its own real street and stands 0.75 of the street depth out from its frontage (bands City, District, Near, Street; the street dress rises along the path). It lands on the building the netrun is about: no staged run, no stand-in track. After the reveal the camera does the along-street dolly to the start room.',
    ui='0.00 s: JACK IN sticker slap; the site dossier and map chrome fade (0.2 s). 0.00-0.70 s: the Cell terminal types `jack --from CULTURE_INTAKE --to SEED_VAULT`, routing, handshake, CONNECTED. 0.70-1.325 s: binary rain on the chosen link only. 1.325-1.55 s: CRT collapse. 1.55-3.05 s: no chrome. 3.05-4.87 s: REVEAL, the room fronts break into 0/1 bits left to right while the wax links write on. 4.87-5.77 s: MARK (0.50 s) and its hold (0.40 s): node stickers draw. 5.77-6.52 s: zoom to the start room (0.50 s) and settle (0.25 s), the key strip and street HUD slide in (panel_in 0.22 s); input (CHOOSE) at 6.52 s.',
    rm='0.25 s cross-fade from the city map to the street at CHOOSE (K10), stickers and HUD already drawn. One press at any beat also skips to K10.',
    feel='Committing to one door, watching the line get made, then dropping straight onto the building you chose.',
    real='K6, K7 and K8 are art/zoom-to-building captures (A-143, lit street v2; seed 7, a real lot by the Solace HQ). K1 is the r42 map page. K2 and K5 are composites (terminal panel; capture plus target ring). K10 is the capture with the room cutaways and stickers placed on it (composite). K3, K4 and K9 carry invented FX: concept.',
    chg='Ruling 1: retimed from about 13 s to 6.52 s (every beat halved, as art/jack-6s). Standing ruling (no staged streets): the staged run (run 8), the round 4 stand-in track and the pick B plate are gone; the dive and landing are the zoom-to-building captures on the real street, ending at the exact building. Rooms on that street are cutaways placed on the real frontage (no render of rooms on the real street yet).')

add(id='t02', file='t02_street_to_room.jpg', status='changed',
    title='T2  Street to room: one seamless move in on our room, the other rooms close, then the cutaway pose',
    dur='1.2 s (was 0.8 s: art\'s call, the seamless move needs it; open question)',
    ease='route pulse: linear; move in: ease-in-out cubic; walls close: ease-in, 60 ms stagger by distance from our room; pan / angle to the cutaway pose: ease-out cubic; node pop: BACK',
    labels=['K1  0.00 s  street: rooms open, pick B pad on our next room', 'K2  0.15 s  click: route pulse runs the link (0.4 s)',
            'K3  0.40 s  node pop; camera moves in, other rooms start to close', 'K4  0.70 s  moving in: every other room closed, ours open',
            'K5  0.95 s  pan and angle up toward the cutaway pose', 'K6  1.20 s  ROUTER (fight): cutaway settled',
            'K6b 1.20 s  BLOCK SERVER: the bio lab, giant tank (new plate)', 'K6c 1.20 s  TERMINAL (event): cutaway',
            'K6d 1.20 s  MAINFRAME (shop): cutaway', 'K6e 1.20 s  SERVER RACK / ELITE ROUTER: server room'],
    cam='No cut (ruling 5). One camera move: from the street pose it moves in on our room (0.40-0.80 s, about 2.6x on the room in the frontage), then without stopping pans and angles up to the cutaway camera pose of that room (0.80-1.20 s): the pitch rises from street eye level to the cutaway\'s high three-quarter view while the frame recentres on the room box. No iris.',
    ui='0.00 s: the hovered next room carries the pick B pad (pink 4 px edge, 22 % fill). 0.00-0.40 s: route_pulse 0.4 s runs the wax link to the room; 0.40-0.65 s node_pop (0.25 s BACK) on it; the room left behind dims (visited_dim 0.3 s). 0.15-0.35 s: key strip and street HUD drift out. 0.35-0.75 s: every other room node closes its walls (the cutaway front slides shut top to bottom, 0/1 bits on the closing edge, 0.25 s each, 60 ms stagger outward from ours); only ours stays open. 1.20 s: T3 (fight), or the event terminal (panel_in 0.22 s), or the MAINFRAME shop panel.',
    rm='0.25 s cross-fade from the street to the interior; walls shown closed, no pulse or move.',
    feel='Choosing the door, and the street shutting behind you while the camera takes you in.',
    real='K6, K6c-K6e are v3.1 cutaway renders. K6b is a new 2D plate (BLOCK SERVER bio lab, drawn here over the v3.1 bio box). K1, K2 are the zoom-to-building street capture with the room cutaways placed on its frontage (composite). K3 and K4 carry the invented wall-closing FX (concept); K5 is a composite (the cutaway pose plate warped toward street pitch over the zoomed street).',
    chg='Ruling 5: the iris cut is gone; one seamless move in, then pan / angle to the cutaway pose, and every other room closes its walls during the move. New BLOCK SERVER room: an enhanced bio lab with a giant glowing tank in the centre and cables to server racks round the edge (plates/room_block_server.png). Other kinds keep the v4 mapping. Standing ruling: the street is the real street (zoom-to-building capture), not the pick B plate. Timing 0.8 to 1.2 s (art\'s call).')

add(id='t03', file='t03_room_to_fight.jpg', status='changed',
    title='T3  Room to fight: the bits fly first and build the ring as they land, then the Deface v3 board',
    dur='1.2 s (unchanged)',
    ease='bits: ease-out from the room, ease-in at the rim; ring build: follows the arriving bits (clockwise from 12 o\'clock); glass: ease-out cubic; segments: 90 ms snap; stickers: the bible 3.18.5 slap; HUD: panel_in 0.22 s CUBIC out',
    labels=['K1  0.00 s  room interior, nothing on it', 'K2  0.10 s  bits lift out of the room first',
            'K3  0.30 s  first bits land: a third of the ring, glass fades up', 'K4  0.55 s  two thirds of the ring, wedges fill behind it',
            'K5  0.80 s  ring closed, segments lock; stickers slap on', 'K6  1.00 s  forecast pencil writes on; HUD slides in',
            'K7  1.20 s  board ready (Deface v3, approved)'],
    cam='Fixed camera on the room; no camera move. The room dims to 55 % from 0.10 s.',
    ui='0.00-0.10 s: nothing. 0.10-0.75 s: corp-teal 0/1 bits stream out of the room in a steady flow; each bit that reaches the rim stays as a piece of the rim, so the ring is drawn by the bits clockwise from 12 o\'clock (a third at 0.30 s, two thirds at 0.55 s, closed at 0.75 s); bits run round the rim, never across the face (bible 3.20). 0.20-0.45 s: the glass disc fades up under the growing ring. 0.45-0.80 s: corp segments fill the wedges behind the ring and lock (90 ms snap). 0.80-1.00 s: the five program stickers slap on (60 ms stagger). 1.00-1.20 s: pencil, SOLACE board panel, commit forecast; SEND IT last. Input at 1.20 s.',
    rm='0.25 s cross-fade from the room to the finished board; with reduce effects: no bits, no squash, pencil at once.',
    feel='The building\'s defences pour out and draw the wheel themselves.',
    real='K1 is the v3.1 bio cutaway; K7 the approved v3_board plate. K5 and K6 are v3_board layers over the dimmed room (composite). K2-K4 (bits, the partial ring) are concept FX on cut layers of the board.',
    chg='Ruling 4: the bits start at 0.10 s (was 0.50 s) and build the ring as they arrive, instead of the ring fading up first and the bits running round it. Same 1.2 s and the same layer order after the ring.')

add(id='t04', file='t04_fight_end_to_street_or_fail.jpg', status='changed',
    title='T4  Fight ends: the board dissolves back to the street, or the runner falls (trace printout)',
    dur='0.8 s back to the street; 0.6 s plus hold for the netrun-failure screen',
    ease='bits: ease-in; return: the T2 move reversed (ease-in-out cubic); walls reopen: ease-out; failure: hard glitch cut, then a 0.3 s settle',
    labels=['K1  0.00 s  WIN: WHEEL TAKEN, OURS NOW, CONTINUE', 'K2  0.25 s  CONTINUE: stickers dissolve to bits (Dissolve A)',
            'K3  0.45 s  glass clears, bits drain into the room', 'K4  0.80 s  back on the real street: room walked, rooms reopen',
            'K5  0.12 s  FAIL: run health 0, the board tears', 'K6  0.60 s  FAIL: Solace prints the trace (design C)'],
    cam='Win: the board dissolves over the room, then the T2 camera move runs backwards (cutaway pose down to street pitch, pull back to the street pose) while the other rooms reopen. Fail: no pull-out; the picture tears (row offsets only, no flash) and cuts to the printout.',
    ui='Win: 0.00-0.20 s HUD and CONTINUE fade; Dissolve A on the stickers, bits drain into the room (ease-in). 0.45-0.80 s: the reverse move; the room just won turns lime (walked), the other rooms\' walls slide open again, the next rooms take the orange ring, key strip and HUD back. Fail: HUD out in 0.1 s; the trace printout (netrun_fail design C) feeds out of the printer slot from 0.30 s; input at 0.60 s (GRID VIEW).',
    rm='0.25 s cross-fade fight to street; failure: 0.25 s cross-fade to the printout.',
    feel='Win: the fight closes like a process and the street opens back up. Fail: the corp files its report on your operative.',
    real='K1 is the approved v3_win plate; K6 is netrun_fail design C (C_trace_printout.png). K4 is the zoom-to-building street capture with the placed rooms and the walked check (composite). K2, K3 and K5 carry concept FX.',
    chg='Ruling 2: the fail branch is design C (the trace printout), not A. Standing ruling: the win return lands on the real street (zoom-to capture), not the pick B plate, and is the T2 move reversed (rooms reopen). Kept at 0.8 s; whether it mirrors T2\'s 1.2 s is an open question.')

add(id='t05', file='t05_street_end_to_city_map.jpg', status='changed',
    title='T5  Street end, back up to the city map: the claimed site changes, then the advance choice',
    dur='6.82 s jack-out (art/jack-6s; one press skips it) + 0.3 s site pop + 0.22 s advance panel: input at 7.34 s',
    ease='zoom out: ease-in cubic; walls close: linear right to left; rise: the T1 zoom-to path reversed; CRT open: ease-out; site pop: BACK 0.3 s; panel: panel_in 0.22 s CUBIC out',
    labels=['K1  0.00 s  street end: last-layer SERVER RACK cleared', 'K2  0.75 s  settle and zoom back out, marks fade',
            'K3  2.56 s  walls close: rooms back to bits, right to left', 'K4  3.47 s  rise starts off the real street',
            'K5  4.25 s  rising over the district (zoom-to reversed)', 'K6  4.97 s  city overview, the building still marked',
            'K7  5.38 s  CRT opens: dot, line, then the map', 'K8  6.47 s  terminal: DISCONNECTED, loot banked',
            'K9  7.12 s  city map: the site flips to the Cell', 'K10 7.34 s  the advance choice (next sites)'],
    cam='Jack-out = the street side of the chain backwards, the select hold, then the HQ side backwards (art/jack-6s, DECISIONS 2026-11-16). The camera runs T1\'s zoom-to path in reverse: from the street pose up through Near, District and City to the overview with the building still marked, then the CRT opens onto the city map.',
    ui='0.00-0.25 s settle out; 0.25-0.75 s zoom out (street HUD out); 0.75-1.15 s mark hold, 1.15-1.65 s markers erase; 1.65-3.47 s walls close (reveal reversed); 3.47-4.97 s rise, no chrome; 4.97-5.27 s select hold; 5.27-5.495 s CRT opens; 5.495-6.12 s rain retracts up the link; 6.12-6.82 s terminal prints `jack --out`, DISCONNECTED and the banked loot. 6.82-7.12 s: the site sticker flips to the Cell (BACK 0.3 s, lime ring, check). 7.12-7.34 s: the advance choice slides in (panel_in 0.22 s); input at 7.34 s.',
    rm='0.25 s cross-fade from the street to the city map with the site already claimed, then the advance cards appear with no slide.',
    feel='Climbing back out with the loot, and seeing the city change because of it.',
    real='K4 and K5 are zoom-to-building captures (the path reversed). K1, K2, K6, K8 and K9 are composites (placed rooms and marker, dim, ring, terminal, map sticker). K3, K7 and K10 are concept (bits, CRT open, the advance cards).',
    chg='Ruling 1: retimed from about 13.6 s to 6.82 s (+0.52 s site pop and panel, input at 7.34 s). Standing ruling: the staged run (L7, overview) and the stand-in track are replaced by the real street and the zoom-to captures reversed.')

keep('t06', status='copied', chg=V4D['t06']['chg'] + ' v5: unchanged. Ruling 7: Heat 100 opens this same alert (a normal raid, only stronger); no PURGE event.')
keep('t07', status='copied', chg=V4D['t07']['chg'] + ' v5: unchanged.')
keep('t08', status='copied', chg=V4D['t08']['chg'] + ' v5: unchanged; approved (ruling 8). Under v47 every raid routes through claimed sites and ends at our HQ, so the HQ chip (K7) can follow any raid.')

add(id='t09', file='t09_city_to_hq_workshop.jpg', status='changed',
    title='T9  HQ workshop: an overlay on the city map (recruit, weapons, talents) and back',
    dur='0.30 s in (map dims 0.20 s, overlay panel_in 0.22 s from 0.08 s); tabs 0.22 s; 0.30 s out',
    ease='map dim: ease-in-out; overlay: panel_in 0.22 s CUBIC out (48 px); tab switch: panel_in 0.22 s; out: the same reversed',
    labels=['K1  0.00 s  map: CREW / MARKET picked', 'K2  0.15 s  map dims, the workshop overlay slides in',
            'K3  0.30 s  overlay: RECRUIT', 'K4  +0.22 s  tab: WEAPONS', 'K5  +0.22 s  tab: TALENTS',
            'K6  0.15 s  back: overlay slides out', 'K7  0.30 s  city map again'],
    cam='No camera move: the city map stays where it is under the overlay (no room, no monitor, no jack geometry).',
    ui='0.00 s: CREW or MARKET sticker press. 0.00-0.20 s: the map dims to 45 % (Heat strip and the CREW / MARKET / DEFENCE column stay lit). 0.08-0.30 s: one terminal-glass overlay slides up over the map (navy glass, cyan edge, mono title, pink rule) with three tabs: RECRUIT (crew cards), WEAPONS (loadout), TALENTS. Input at 0.30 s. Tabs switch with panel_in 0.22 s. Back (Esc or the map): the overlay slides out 0.22 s and the map undims.',
    rm='0.25 s cross-fade each way.',
    feel='Pulling the crew board over the city without leaving it.',
    real='K1, K2, K6 and K7 are the r42 map page (real) with dims and the panel (composite). K3-K5 are concept: no workshop screen exists; the crew cards in RECRUIT are cut from the r42 map page.',
    chg='Ruling 3: the round 42 HQ room and its deck-CRT jack are dropped; the workshop is an overlay on the city map (ruling 6: the r42 hq_idle page, Solace). Timing 0.8 s each way to 0.30 s (panel values).')

keep('t11', status='changed',
     labels=['K1  0.00 s  the core tape hits 0 (a raid ends at our HQ)', 'K2  0.50 s  raid chrome out, city dims and drains',
             'K3  0.90 s  the folder drops in, tilt -2 deg', 'K4  1.60 s  dossier, slot B: the survey map, every node crossed'],
     real='K4 is the end screen v2 slot B (real). K1-K3 are composites of the set 8 HQ raid plate (Heat 100, a normal raid at our HQ; core tape crossed in red pencil, dim) and the folder.',
     chg='Ruling 7: no PURGE raid. The trigger is HQ integrity 0 from any raid (v47: every raid ends at our HQ). Same pictures and timing; only the labels changed.')

add(id='t12', file='t12_hq_netrun_to_win.jpg', status='changed',
    title='T12  Tier 3 sites taken: fly in on the Solace HQ street (real city), BLOCK SERVER, the win and the dossier',
    dur='1.8 s fly-in (+ the T1 entry beats from REVEAL on arrival), the HQ street; win 1.4 s + 0.9 s folder (unchanged, approved)',
    ease='fly-in: the CityZoomTo path, the last 0.5 s decelerates; recolour: ease-in-out; flash: 90 ms; folder: ease-out cubic, 0.3 s settle',
    labels=['K1  0.00 s  map: the last tier 3 site claimed', 'K2  0.40 s  the Solace HQ unlocks: its street\'s building marked',
            'K3  0.90 s  fly-in: push down on the real lot', 'K4  1.80 s  the HQ street: a real street by the Solace HQ',
            'K5  +0 s  BLOCK SERVER beaten: the tank goes dark', 'K6  +0.4 s  the street recolours to the Cell',
            'K7  +0.8 s  flash', 'K8  +1.4 s  the folder drops over the HQ street', 'K9  +2.3 s  dossier, slot B: campaign won'],
    cam='Taking the last tier 3 site opens the Solace HQ. The map camera flies down the zoom-to-building path onto a real lot by the Solace HQ (1.8 s, the last 0.5 s decelerates) and stands in its real street; the HQ netrun plays there (T2 to T4), its last room the BLOCK SERVER bio lab. On the win the camera holds on the street while it recolours, a 90 ms flash, and the folder drops over the dimmed street.',
    ui='0.00-0.40 s: the site flips (T5) and a DISPATCH line names the Solace HQ. 0.40-1.80 s: no chrome. 1.80 s: the T1 entry beats from REVEAL run on the HQ street. Win (BLOCK SERVER beaten): HUD out 0.3 s, the tank goes dark, recolour 0.4-0.9 s, flash 0.8 s, folder 1.4-2.3 s, ROUTED stamp at 1.9 s, MAIN MENU / NEW CAMPAIGN at 2.3 s.',
    rm='0.25 s cross-fade from the map to the HQ street; win: 0.25 s cross-fade to the finished folder.',
    feel='Walking down the corp\'s own street, finding what it was growing, and switching it off.',
    real='K2, K3 and K4 are zoom-to-building captures (seed 7, hq = solace; K2 with the target ring). K9 is the end screen v2 slot B. K1 and K8 are composites. K5 is the new BLOCK SERVER plate in its beaten state (2D). K6 and K7 are concept FX on the real street.',
    chg='Ruling 8: approved, redone on Solace and the real streets: the Meridian staged HQ run (run 10) is gone; the fly-in and street are zoom-to-building captures near the Solace HQ; the win beat is the BLOCK SERVER bio lab going dark (ruling 5), then the street recolours. Timings unchanged.')

T10_NOTE = ('T10 (PURGE recall at Heat 100) is HELD / withdrawn (ruling 7): PURGE is dropped as a special event; Heat 100 is '
            'a normal raid through T6, T7 and T8, only stronger. The recall-streak FX is held (not deleted). The v4 sheet is '
            'kept in `archive/t10_purge_recall_HELD.jpg`, stamped HELD.')

STILL = ['## Still concept (what the next pass would replace)\n',
         '- **Entry and jack-out FX** (T1 K3, K4, K9; T5 K3, K7): binary rain, CRT collapse / open, the room fronts to bits.',
         '- **Rooms on the real street** (T1 K9-K10, T2 K1-K4, T4 K4, T5 K1-K3): the zoom-to-building street has no rooms rendered yet (A-142: rooms show on landing, room lots pending from build). The cutaways here are v3.1 crops placed on the real frontage; the wall closing (T2) is drawn.',
         '- **Cutaway pose surroundings** (T2 K6-K6e): the v3.1 room plates stand in their own kit street; in game the cutaway pose is on the real building.',
         '- **BLOCK SERVER bio lab** (T2 K6b, T12 K5): a 2D plate; a cutaway kit render with a tank prop is the next step.',
         '- **Board assembly** (T3 K2-K4): bits building the rim.',
         '- **Raid alert** (T6 K2): the DISPATCH strip and the red tint.',
         '- **Advance choice** (T5 K10) and the **workshop overlay** (T9 K3-K5): no screen exists.',
         '- **Lost raid report** (T8 K5): no lost aftermath plate exists.',
         '- **HQ win recolour** (T12 K6, K7): a hue shift on the real street.', '']

CALLS = ['## Calls I made (not designer rulings)\n',
         '1. **T2 is 1.2 s** (was 0.8 s): a move in, a pan / angle and the walls closing do not read in 0.8 s. T4\'s win return stays 0.8 s.',
         '2. **Walls close top to bottom with bits on the edge**, 0.25 s each, staggered outward from our room by 60 ms (the reveal\'s language reversed).',
         '3. **T3 ring builds clockwise from 12 o\'clock**, drawn by the bits that arrive (a third by 0.30 s, closed by 0.75 s).',
         '4. **The workshop overlay** is one terminal-glass panel with three tabs over the dimmed map, 0.30 s in and out, panel values only.',
         '5. **Real-street frames** are the A-143 lit captures (`D:/rc_tmp/claude/zt/final`, the frames of `zoom_to_building/zoom_strip.jpg`), copied to `plates/zoom_to/`; the older `D:/rc_scratch/zoom_to/` frames are the dark v1 street and were not used.',
         '6. **The HQ street (T12)** is the capture at lot (-47, -55) next to the Solace HQ rect; the helix landmark is not in those frames, so the win beat is the BLOCK SERVER tank going dark plus a street recolour.',
         '7. **BLOCK SERVER plate** is drawn in 2D over the v3.1 bio cutaway box (same geometry, street and SOLACE signage), Solace palette (corp_solace #3DFF8B, net_cyan #5CE1FF).', '']

OPEN = ['## Open questions for the designer\n',
        '1. **T2 length:** 1.2 s for the seamless move (art\'s call). And should T4\'s win return mirror it (1.2 s) or stay 0.8 s?',
        '2. **BLOCK SERVER bio lab:** is the plate the right direction (giant tank, a dark specimen with one lit eye, racks on the back walls, overhead and floor cables)? If yes, art builds it as a cutaway kit room.',
        '3. **The specimen:** keep a silhouette that is never shown clearly, or show what Solace is growing?',
        '4. **Workshop overlay:** one panel with tabs (drawn), or three separate cards by the CREW / MARKET buttons? Talents still have no screen.',
        '5. **Advance choice** (T5 K10) and the **lost raid report** (T8 K5) are still open from v4.', '']

LOG = ['## Build log\n',
       '- Built by `scripts/build5.py` (with `helpers5.py`, a copy of v4 `helpers4.py`; `text5.py`, which reuses a verbatim copy of v4 `text4.py`; and `blocklab5.py`, the BLOCK SERVER plate), run as `python scripts/build5.py` from `transitions/v5/`. PIL and numpy only; no Godot, no Blender. v4 is untouched.',
       '- Writes only into `transitions/v5/`. Unchanged strips (T6, T7, T8) are byte copies of the v4 files. `plates/PLATES.txt` lists every source with its md5 prefix.',
       '- Iterations: room slots on the street were first placed from a scaled grid read and landed off the shopfronts (fixed to source pixels); room crops tightened; T12 recolour narrowed to the neon (the first pass tinted the whole street). Every sheet was looked at.',
       '- Process slip (honest): one shell call carried a stray `python - 2>/dev/null` fragment; it was blocked by the permission check before it ran, nothing executed. Every build ran as `python scripts/<file>.py`, one process at a time, in the foreground.',
       '- Jack timings are from art/jack-6s 980f31f1a (godot_look): ui_motion.tres beats at 0.5 of the animatic, select hold 0.3 s; jack-in 6.52 s, jack-out 6.82 s.', '']
