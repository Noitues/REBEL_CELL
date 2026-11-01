"""Text for transitions v3 (v2 text kept, updated per transition)."""
TEXT = []


def add(**k): TEXT.append(k)


add(id='t01', file='t01_city_to_raid_view.jpg', title='T1  City Grid to raid view', dur='1.2 s', ease='smootherstep on log(zoom); no overshoot',
    labels=['K1  0.00 s  City Grid, full plan, helix in frame', 'K2  0.40 s  push toward the raid focus, 1.25x',
            'K3  0.80 s  dissolve to the closer iso plate, 1.5x', 'K4  1.20 s  raid view, same city, raid HUD in'],
    cam='Same iso camera throughout (yaw 135, pitch 40); only the ortho width tightens from the City Grid plan to the raid-view plate camera (plate zoom 1.5 about px 722,500). No perspective, no cut: it is the same city getting closer.',
    ui='0.00-0.20 s: City Grid chrome (title, filters) fades. 0.20-0.90 s: none. 0.90-1.20 s: raid-view chrome (resource strip, raid forecast, VIEW LOADOUT, netrun and raid nodes) fades up with a 60 ms stagger; input at 1.20 s. The plate carries no chrome, so the chrome is not drawn.',
    rm='0.25 s cross-fade from City Grid to raid view; chrome appears with it.',
    feel='Leaning in from the whole city to the part of it you are fighting for.',
    real='K1 and K4 are the same real city renders as v2 (godot_zoom stage 1, tide plate 01_plan). K2 and K3 are crops and a blend of them.',
    chg='None. No new material applies to T1; frames and timing are v2.')

add(id='t02', file='t02_raid_to_select_jackin.jpg', title='T2  Raid view to select a netrun and jack in', dur='0.6 s (select, 0.2 s; jack-in press, 0.4 s)', ease='ease-out cubic for the card; the press is a 90 ms flash then ease-in dim',
    labels=['K1  0.00 s  raid view, netrun entries lit', 'K2  0.20 s  netrun selected, dossier card slides in',
            'K3  0.45 s  JACK IN pressed: flash, chrome dims', 'K4  0.54 s  chrome gone; dissolve to the zoom-track city',
            'K5  0.60 s  target highlighted (r7b pick): T3 starts here'],
    cam='No camera move on selection. On JACK IN the camera hands to T3 starting from the zoom-track city frame with the target highlight (round 7b candB: pink 4 px outline, fill 0.22, beam 3.0). That frame is the first frame of the T3 zoom, so the highlight is what the player just selected, and the zoom goes down onto it.',
    ui='0.00-0.20 s: the selected node gets a lime ring pulse and its dossier card (file card, Site, threat, JACK IN) slides in from the right 40 px. 0.45 s: JACK IN flashes white for 90 ms. 0.45-0.60 s: all raid-view chrome fades out; the lime ring becomes the pink-outlined target segment over a 0.15 s dissolve, and that is the zoom target for T3.',
    rm='Dossier appears instantly; JACK IN cross-fades 0.25 s into the highlighted city frame (K5).',
    feel='Choosing a door and committing to it.',
    real='K5 is a real render (r7b candB, the picked highlight). K1-K4 are the real tide plate with a mock node marker, the r42 dossier card and JACK IN pasted in, and a blend.',
    chg='K4 and K5 are new: T2 now ends on the real highlighted target (r7b pick) instead of the dimmed raid view. Timing unchanged. The raid plate and the zoom-track city are different camera crops (log item 1).')

add(id='t03', file='t03_jackin_zoom.jpg', title='T3  Jack-in zoom to the netrun street along the node route', dur='1.4 s', ease='smootherstep on log(ppb); the old wheel-circle zoom is removed',
    labels=['K1  0.00 s  zoom-track city, highlighted target (r7b pick)', 'K2  0.30 s  push into the district, ribbon begins (r4 f16)',
            'K3  0.65 s  iso close, ribbon follows the route (r4 f34)', 'K4  0.95 s  dolly-zoom to perspective, pitch 40 to 12 (r4 f50)',
            'K5  1.20 s  near street, horizon dropping (r4 f63)', 'K6  1.40 s  the netrun street (r6) + ribbon and room tags',
            'K7  1.90 s  idle: sign flicker loop (r7 GIF, 640 px)'],
    cam='ZOOM_RULES 5.5 path, shown with the round-4 zoom track (zoom_motion.gif, 75 frames mapped onto the 1.4 s: frame = t/1.4 x 74): iso ortho push to the district (0.65 s), dolly-zoom fov 8 to 40 with pitch 40 to 12 (0.65-0.95 s), pitch to 0, lens shift and eye to 4 m (last 0.45 s). The camera rides the node route: the focus point slides along the lime ribbon, which is the connected path of rooms, ending framed on the street at a horizontal third. Track frames are 480 px (the GIF source); the street (K6) is the round-6 full-res render.',
    ui='Chrome is already gone (T2). 0.30 s: the route ribbon draws from the target along the node route, tracking the camera. 1.10-1.40 s: room tags (type, state) pop onto the street rooms in 60 ms steps; the netrun HUD (resource strip, route legend, menu) fades up at 1.25 s; input at 1.40 s. The r7 sign flicker (4 s loop, 12 fps) runs on the street from arrival and is not part of the 1.4 s.',
    rm='0.25 s cross-fade from the highlighted city frame to the netrun street with room tags and HUD already shown (K6).',
    feel='Dropping through the city and landing in a single street that is yours to run.',
    real='K1 (r7b pick) and K7 (r7 flicker GIF) are real. The pictures under K2-K6 (r4 track, r6 street) are real renders; the route ribbon, room tags and HUD are mock overlays, so K2-K6 are COMP.',
    chg='K1-K6 now use the real zoom track and the r6 street (v2 used godot_zoom stages and the r5 street). K1 is the highlighted target, not the plate. K7 added. Timing and easing unchanged. Node rooms are still tags on real storefronts, not geometry (log item 3).')

add(id='t04', file='t04_street_to_room.jpg', title='T4  Select a room on the netrun street and zoom into it (combat, event, shop)', dur='0.8 s', ease='ease-in cubic for the push, ease-out cubic for the room settle',
    labels=['K1  0.00 s  netrun street, three rooms (FIGHT, EVENT, SHOP)', 'K2  0.15 s  room selected, white and pink frame',
            'K3  0.35 s  push into the room facade 3x (r6 crop)', 'K4  0.55 s  iris opens on the cutaway room',
            'K5  0.80 s  FIGHT: bio cutaway settled (v3.1)', 'K5b 0.80 s  EVENT: event cutaway (v3.1)',
            'K5c 0.80 s  SHOP: shop cutaway (v3.1)', 'K5d 1.05 s  EVENT: card slides up over the room'],
    cam='The camera pushes at the chosen room storefront (3x on the r6 street), then a lime iris opens on the interior: a v3.1 cutaway room (combat_backdrop/v3_1: bio, srv, gh, rec, lobby for fights; event; shop). The rooms are composed at the city iso angle on a SOLACE-signed facade, so no camera swap is needed after the iris.',
    ui='0.00-0.15 s: room selected (white and pink frame, tooltip with type and reward). 0.15-0.35 s: street HUD dims to 40 % and drifts out. 0.35-0.55 s: iris only. 0.55-0.80 s: the interior is quiet, then T5 (combat) starts, or the event card (title, choices) slides up from the bottom for events (K5d, 0.25 s after settle), or the shop panel for shops.',
    rm='0.25 s cross-fade from the street to the interior; no iris, no push.',
    feel='Choosing a door in the street and stepping inside it.',
    real='K5, K5b and K5c are real v3.1 cutaway renders (combat, event, shop). K1-K4 are the real r6 street with mock tags, crop, blur and iris; K5d pastes the real event card.',
    chg='The combat room is v3.1 bio (the room under the new E10 plate), not the v2 server room. K5b is a real event room (v2: a card pasted on a dimmed v2 room); K5c and K5d added. The street is r6. Timing unchanged.')

add(id='t05', file='t05_room_to_combat.jpg', title='T5  Room to combat: the wheel flies in, enemy rings fly from the room as binary bits', dur='1.2 s', ease='wheel: ease-out cubic with a 4 % overshoot; bits: ease-in-out along curved paths; rings lock with a 90 ms snap',
    labels=['K1  0.00 s  cutaway room, nothing on it (v3.1 bio)', 'K2  0.25 s  the wheel flies in from the camera, 1.35x to 1.0x',
            'K3  0.55 s  bits leave the room, curve toward the wheel', 'K4  0.85 s  bits surround the wheel in three rings',
            'K5  1.05 s  bits resolve into the rings; HUD and hand slide in', 'K6  1.20 s  combat begins: E10 design plate p1_decide'],
    cam='Fixed iso camera on the room; the camera does not move. The only motion is the wheel (scale 1.35 to 1.0, slight spin settle) and the bit streams, which start in the room (the building in the right half, where the enemy "lives") and curve to three ring radii around the wheel. The room is the same v3.1 render in K1 and behind K6 (the E10 design plate is built on room_bio_bare), so no backdrop swap shows.',
    ui='0.00-0.25 s: nothing. 0.25-0.55 s: wheel in. 0.55-1.05 s: bits. 1.05-1.20 s: turn banner and wave ledger slide in from the top right (the new top-HUD panels), cards deal from the bottom (60 ms stagger), UNDO and SEND IT last. No input until 1.20 s. The room dims to 55 % behind the board from K2 on (the plate shows it dimmed and softened).',
    rm='0.25 s cross-fade from the room to the board; the rings are simply there.',
    feel='The enemy pours out of the building as code and wraps around you; the fight is on.',
    real='K1 (v3.1 bio room) and K6 (E10 design plate on the cutaway) are real and share one room. K2 is the real plate wheel scaled over the dimmed room (COMP). K3-K5 carry the bits FX, which is concept (drawn digits only).',
    chg='K6 is the NEW E10 design plate on the cutaway, replacing the old crane-plate E10 (closes the v2 backdrop-mismatch item). The wheel in K2-K4 is cut from that plate. No timing change. p1_decide_srv and p1_decide_gh exist for other fight rooms; the bio plate is shown.')

add(id='t06', file='t06_combat_to_netrun_or_fail.jpg', title='T6  Combat ends, the board dissolves to bits, back to the netrun, or the run fails', dur='0.8 s back to the netrun; 0.6 s plus hold for the failure screen', ease='bits: ease-in; street: ease-out cubic; failure: hard glitch cut, then a 0.3 s settle',
    labels=['K1  0.00 s  combat won (E10 design plate)', 'K2  0.20 s  the board starts to dissolve into bits',
            'K3  0.40 s  mostly bits over the empty cutaway', 'K4  0.80 s  back on the netrun street, room cleared',
            'K5  0.20 s  FAIL branch: signal glitch, board tears', 'K6  0.60 s  FAIL: netrun-failure screen (concept)'],
    cam='Combat: fixed iso camera; the board dissolves in place over the cutaway. Then the iris of T4 runs in reverse and the camera pulls back 3x to the r6 street framing it was left in, which is the framing T4 started from. Failure: no pull-out; the picture glitches (slice offsets) and cuts to the terminal screen over the dimmed route.',
    ui='0.00-0.20 s: UNDO, SEND IT, hand and the top-HUD panels fade; the wheel and rings break into bits that scatter and drain toward the room. 0.40-0.80 s: pull-out, street HUD fades up, the cleared room shows a check. Failure: HUD out in 0.1 s, the terminal panel (title bar, CELL-9 SIGNAL LOST, three lines, two buttons) opens at 0.30 s, input at 0.60 s.',
    rm='0.25 s cross-fade combat to street; failure is a 0.25 s cross-fade to the terminal screen.',
    feel='Win: the fight evaporates like a closed process and you are on the street. Fail: a cold cut to a log.',
    real='K1 is the real new E10 plate; K3 sits over the real v3.1 room; K4 is the r6 street with mock tags (COMP). Bits dissolve and the glitch tear are concept FX; the failure screen is still one concept frame.',
    chg='K1 and the K3 backdrop are the new E10 plate and the v3.1 cutaway; K4 is the r6 street. Timing unchanged. Failure screen: still concept.')

add(id='t07', file='t07_netrun_to_raid_view.jpg', title='T7  Netrun, win or lose, back up to the raid view (the raid node changes)', dur='1.2 s', ease='the T3 path in reverse: smootherstep; the node change is a 0.3 s pop after landing',
    labels=['K1  0.00 s  netrun ends (street, or the end of the route)', 'K2  0.30 s  pull back, chrome out, ribbon retracts (r4, reversed)',
            'K3  0.60 s  pitch up over the district (r4, reversed)', 'K4  0.90 s  zoom-track city, target outline on (r7b)',
            'K5  1.00 s  raid view, node still contested (before)', 'K6  1.20 s  WIN: node turns lime with a check',
            'K7  1.20 s  LOSE: node turns pink with an X'],
    cam='The T3 path in reverse (the r4 track played backwards), ending on the zoom-track city; over 0.90-1.00 s that dissolves to the raid-view camera with the netrun entry the player came from centred. Win and lose use the same path; only the final node pop differs.',
    ui='0.00-0.20 s: netrun HUD out. 0.20-0.90 s: no chrome. 0.90-1.20 s: raid-view chrome fades up; at 1.00 s the node pops: win = lime ring, check, short lime ripple on the city; lose = pink ring, X and a pink ripple that creeps along the nearest lane (Bloom). Input at 1.20 s.',
    rm='0.25 s cross-fade street to raid view, node already in its new state.',
    feel='Back in the big picture with proof that what you did down there mattered.',
    real='K3 and K4 are real renders (r4 track frame, r7b city). K1, K2 and K5-K7 are the r6 street, r4 track and tide plate with mock ribbon and node markers; the markers are a placeholder (no raid-node art exists).',
    chg='Frames now come from the r4 track, r7b city and r6 street. K4 (the join between the two city cameras) is new. Timing unchanged.')

add(id='t08', file='t08_raid_lose_to_dossier.jpg', title='T8  Raid view lose: the dossier folder ends the campaign (image slot B)', dur='1.6 s', ease='city dims: ease-in-out; folder: ease-out cubic slide, 0.3 s settle',
    labels=['K1  0.00 s  the city is lost (real raid beat)', 'K2  0.50 s  city dims and drains to pink, grease marks start',
            'K3  0.90 s  the folder drops in, tilt -2 deg', 'K4  1.60 s  dossier, slot B: survey map, every node crossed'],
    cam='No camera move. The camera locks on the lost city at 0.0 s; the folder is a UI card dropping from above onto the dimmed city.',
    ui='0.00-0.40 s: raid chrome out. 0.40-0.90 s: city to 35 %; the folder slides down 140 px, tilting -4 to -2 degrees. 0.90-1.60 s: FILED stamp thuds at 1.2 s, the survey map marks draw in (every node crossed out, the Bloom spreading), memo fields type in, MAIN MENU and NEW CAMPAIGN arm at 1.60 s. In the game the marks come from the player network on the real city plan.',
    rm='0.25 s cross-fade to the finished folder; stamp and marks pre-drawn.',
    feel='The corporation closing the file on you: quiet and final.',
    real='K1 (tide plate 07_city_lost) and K4 (end screen v2, slot B) are real; K2 and K3 are composites of them.',
    chg='None. The end screens v2 slot B are the same files.')

add(id='t09', file='t09_raid_to_plan_and_back.jpg', title='T9  Raid view to planning the raid, and back', dur='0.7 s each way', ease='smootherstep in; ease-out cubic out',
    labels=['K1  0.00 s  raid view (real)', 'K2  0.25 s  chrome out, push 1.15x, planning cards slide in',
            'K3  0.70 s  RAID SETUP page (real r42)', 'K4  0.40 s  planning: lane tray and threat intel (crop 1.6x)',
            'K5  0.35 s  back: cards slide out, pull to the raid view', 'K6  0.70 s  raid view again (real)'],
    cam='A 15 % push on the same iso camera into the plan composition (the r42 setup page is the same city on the same camera, with the lanes drawn on it); back is the reverse. No cut, no perspective change.',
    ui='In: 0.00-0.20 s raid chrome fades; 0.20-0.70 s STRAIN AUDIT card from the left, THREAT INTEL from the right, lane tray rising from the bottom (80 ms stagger). Back: the cards slide out in 0.25 s, then raid chrome returns with any chosen lanes drawn on the city.',
    rm='0.25 s cross-fade each way.',
    feel='A calm move into the planning table and back out to the city, with your plan on it.',
    real='K1, K3, K6 real (tide plate, r42 raid setup). K2, K4, K5 are crops and blends of them.',
    chg='None. No new material applies.')

add(id='t10', file='t10_raid_start_result_back.jpg', title='T10  Raid view to starting a raid, the result, and back to the raid view', dur='0.9 s in, raid plays, 1.0 s to result, 0.7 s back', ease='ease-out cubic for the raid; result: ease-in-out with a 0.3 s hold; back: smoothstep',
    labels=['K1  0.00 s  raid view, raid warning (real)', 'K2  0.90 s  raid begins, FX enter from the edge (real)',
            'K3  1.40 s  impact at the defended node (real)', 'K4  1.90 s  RESULT held: aftermath (real)',
            'K5  1.90 s  RESULT lost: city lost (real, branch)', 'K6  2.60 s  back on the raid view, nodes updated'],
    cam='Raid camera is the plate camera (zoom 1.5 about px 722,500) throughout. 0.9 s, the raid starts with a settle only; the result is a slow 1.0 to 1.1x push on the impact point over 1.0 s; back is a 0.7 s pull to the raid-view framing.',
    ui='0.00-0.25 s: raid chrome out. 0.25-0.90 s: raid HUD (wave, defense) in. 1.90 s: HUD out; result banner (HELD or CITY LOST) and tally in; the lost branch desaturates the city to 60 % over 0.5 s. Back: banner dismisses, raid chrome returns, nodes in their result state.',
    rm='Each step is a 0.25 s cross-fade; the raid FX plays at normal speed in the raid step.',
    feel='A threat arrives, hits, and the aftermath settles; then the city is yours again, changed.',
    real='K1-K5 are real tide plates. K6 is the plate with a mock node marker.',
    chg='None. No new material applies.')

add(id='t11', file='t11_raid_to_hq_netrun.jpg', title='T11  Raid view to the HQ netrun: a special fly-in to the hand-authored HQ', dur='1.8 s', ease='smootherstep on log(zoom); the final approach decelerates over the last 0.5 s',
    labels=['K1  0.00 s  raid view, the HQ node selected', 'K2  0.30 s  dissolve from the city (1.8x) into the authored fly-in',
            'K3  0.52 s  fly-in frame 2 of 8: aerial, helix and ring road', 'K4  0.87 s  fly-in frame 4 of 8: descent toward the avenue',
            'K5  1.15 s  fly-in frame 6 of 8: low, helix ahead', 'K6  1.65 s  fly-in frame 8 of 8: the HQ avenue, settled',
            'K7  1.80 s  HQ chrome up on the hero frame (r42 crops)'],
    cam='The HQ netrun is bespoke, so only the first 0.3 s is the procedural city. A 0.3 s dissolve (city at 1.8x on the helix into fly-in frame 1) hands to the authored HQ set camera (hq_set round 3, 8 frames): one continuous descent from the aerial over the ring to the low avenue pointing at the helix. Frames are spaced evenly in camera travel; they are held about 0.17 s each at first and 0.25 s each over the last three, which is the 0.5 s deceleration. The settled frame is hero.png.',
    ui='0.00-0.25 s: raid chrome out. 0.25-1.35 s: only an avenue ribbon draws toward the helix (not drawn here). 1.45-1.80 s: HQ chrome (file card, node dossier, crew tray, JACK IN) fades up with a 60 ms stagger on the settled hero frame; input at 1.80 s.',
    rm='0.25 s cross-fade from the raid view to the settled HQ hero frame with the chrome on.',
    feel='Approaching the corporation that built the city: slowly, and a little ominously.',
    real='K3-K6 are real renders of the hand-authored HQ set (hq_set round 3, fly_in f01, f03, f05, f07). The raid-view node (K1), the dissolve (K2) and the chrome (K7, cropped from the r42 HQ page) are composites.',
    chg='K3-K6 are real fly-in frames; v2 K2-K5 were crops of the city and the v1 concept frame 4. The camera is authored from 0.3 s on, so the camera match at the dissolve is needed only at frame 1. The final frame is the hero street, not the iso HQ map page (log item 4). Dissolve shortened 0.4 to 0.3 s inside the same 1.8 s.')

add(id='t12', file='t12_hq_to_win_dossier.jpg', title='T12  Custom HQ netrun to campaign win, then the dossier folder (win, image slot B)', dur='1.4 s plus 0.9 s folder', ease='helix recolour: ease-in-out; flash: 90 ms; folder: ease-out cubic slide, 0.3 s settle',
    labels=['K1  0.00 s  HQ netrun, last node resolved (r42 page)', 'K2  0.20 s  chrome out; dissolve to the HQ hero street',
            'K3  0.55 s  helix hacked: lime to cyan sweeps up, 4 % push', 'K4  0.80 s  white flash over the helix close-up',
            'K5  1.40 s  the folder drops over the dimmed cyan HQ avenue', 'K6  2.30 s  dossier, slot B: red grease marks on the network'],
    cam='A 0.2 s dissolve from the iso HQ page to the hero street (the view the player saw settle in T11), a 4 % push toward the helix while it recolours, then the flash cuts to the helix close-up (alt_helix_closeup); the folder is a UI card over the dimmed street.',
    ui='0.00-0.30 s: HQ chrome out. 0.40-0.90 s: the lime-to-cyan sweep (the ruling colour story of the win). 0.80 s: 90 ms flash. 1.40-2.30 s: the folder slides in, the ROUTED stamp thuds at 1.9 s, the survey map marks draw in red grease pencil, MAIN MENU and NEW CAMPAIGN arm at 2.30 s.',
    rm='0.25 s cross-fade from the HQ page to the finished folder.',
    feel='A quiet win: the helix changes colour, and the corporation files you as a case.',
    real='K1 (r42 HQ page) and K6 (end screen slot B) are real; the pictures under K2-K5 (hero, close-up) are real renders. The cyan sweep and the flash are scripted hue shifts: concept FX (K3, K4).',
    chg='The recolour is now on the real HQ hero and helix close-up renders (v2: a hue shift on the HQ page and the concept frame 4). A 0.2 s page-to-street dissolve is added. Folder over the HQ street (v2 assumption 9 kept). Timing unchanged.')

STILL = ['## Still concept (what the next render pass would replace)\n',
         '- **Bits FX and the enemy-ring fly-out** (T5 K3-K5, T6 K2-K3): drawn digits only; needs a particle pass and a ring build-up.',
         '- **Netrun-failure screen** (T6 K6): one concept frame in the Solace terminal look over the dimmed route page.',
         '- **HQ win sweep and flash** (T12 K3-K4): a hue shift on the real hero and close-up; the real thing is a shader sweep on the helix material.',
         '- **Route ribbon, room tags, raid-node markers, dossier and HQ chrome** (T2-T4, T7, T10, T11): mock overlays over real renders; the plates have no HUD and no raid-node art exists.',
         '- **Street rooms as geometry:** the r6 street has storefronts but no node rooms; tags sit on real storefronts. The facade-to-cutaway match (the SOLACE sign) is assumed, not rendered.',
         '- **Fight rooms other than bio:** p1_decide_srv and p1_decide_gh exist, but T5 shows the bio plate; rec and lobby have no E10 plate.',
         '- **Sources at low resolution:** T3 K2-K5 and T7 K2-K3 come from a 480 px GIF; the flicker K7 is a 640 px band.', '']

LOG = ['## Choices and changes log (O-23, made overnight without asking)\n',
       '1. **Two city cameras.** The raid-view plate (tide plate camera, zoom 1.5 about px 722,500) and the zoom-track city (r7b highlight frame, godot_zoom stage 1) are different crops. v3 joins them with a short dissolve at the end of T2 and the start of T7 (K4). The proper fix is one city camera for both screens; not done here.',
       '2. **T3 frames.** The r4 zoom_motion.gif (480 px, 75 frames) supplies K2-K5, mapped linearly onto the 1.4 s (frame = t/1.4 x 74), so they are real but soft. K6 is the r6 street at full res. The r7 sign flicker is an idle loop after arrival, shown as K7.',
       '3. **T4 rooms.** The three street rooms are the HOTEL, TEA and DATA storefronts of the r6 street, typed FIGHT, EVENT, SHOP. FIGHT uses the bio cutaway because the E10 plate is built on it; srv, gh, rec and lobby are alternates for other fight sites. Event and shop use the v3.1 event and shop rooms as the street-room proposals.',
       '4. **T11 end frame.** The real fly-in settles on the street-level hero frame, not the iso HQ map page used in v2. The HQ chrome is pasted (r42 crops) on the hero frame. Open question: is the HQ node screen the iso page or this street? v3 follows the real frames; the r42 iso page is kept as T12 K1.',
       '5. **T11 timing inside 1.8 s.** Dissolve 0.3 s (was 0.4), then the 8 fly-in frames, the last three held longer for the 0.5 s deceleration. Total unchanged.',
       '6. **T12 camera.** The v2 push toward the helix on the HQ page is replaced by a short dissolve to the hero street, the recolour on it, and a flash that hides the cut to the helix close-up. Duration and the folder (over the HQ street) unchanged.',
       '7. **T5 wheel.** The wheel layer is cut from the E10 plate with an elliptical mask (HUD, cards and top panels removed); the room behind it is dimmed to 55 %. The scale-in is 1.35x (v2: 1.6x) so the wheel stays on screen.',
       '8. **E10 plates.** Copied to `plates/` at build time from `combat_e10_design/final/` after the final fix pass was announced; `plates/PLATES.txt` has the hashes of the version used.',
       '9. **Unchanged:** T1, T8, T9, T10 (no new material applies). Frames are the same files as v2.',
       '10. **v2 assumptions 1 to 10** are kept as written in `../v2/STORYBOARD.md`; none was contradicted by the new renders. Assumption 9 (the folder over the HQ street) is now shown with the real hero street.', '']
