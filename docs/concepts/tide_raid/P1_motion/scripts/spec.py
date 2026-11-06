"""THE timing spec: the single source for the storyboards, the timing table and the tide_look.tres tuning block.
Frames are 30 fps. A beat is (key, label, f0, f1, ease, means, sound, cite, skip, reduce).
 - key     : tide_look.tres property stem. The duration is `<key>_f` (frames), the curve `<key>_ease`.
 - means   : what the motion says with NO text.
 - cite    : the REF_BASELINE cheat-sheet number it beats or borrows.
 - skip    : SNAP = jump to the end state in skip_snap_f; FF = play at skip_speed x with holds floored at skip_hold_min_f;
             HOLD = a hold that only a player action ends; NONE = input-bound, never skipped.
 - reduce  : the reduce-motion rule for this beat.
"""

CS = 'REF_BASELINE cheat-sheet'

BOARDS = []


def board(**kw):
    BOARDS.append(kw)


# ------------------------------------------------------------------ 01 jack-in
board(
    id='01', slug='jackin', title='JACK-IN', render='jackin',
    means='The city drops into the hacked layer, starting from OUR deck; the corp tower ignites; the Sites grow ICE.',
    total=18, ready=12,
    frames=[0, 2, 4, 6, 8, 10, 13, 18],
    beats=[
        ('jackin_ack', 'Plug-in ack', 0, 2, 'STEP', 'I plugged in: the HOME deck flashes white and its cable lights.',
         'relay clack + sub thump on f0', 'CP2077 quickhack: grade is the switch, no wind-up (enter +0 f). Beat: 2 f ack.',
         'SNAP', 'keep as one 2 f brightness step, luminance capped (alpha .30).'),
        ('jackin_grade', 'World grade drop (radial)', 0, 10, 'OUT_CUBIC',
         'The city changes how it looks, spreading from my deck outward: mine is the source, the corp tower is the far edge.',
         '10 f filtered-noise sweep, low-pass opening', 'CP2077 grade 8-10 f; WD2 camera feed 24-40 f is too slow. Beat: 10 f OUT_CUBIC with a lit front.',
         'SNAP', 'no radial, no front: 8 f IN_OUT_QUAD global cross-fade of the grade.'),
        ('jackin_pads', 'Site pad rings pop', 2, 8, 'OUT_BACK',
         'These are the places that matter: each Site pulses once as the front reaches it.',
         'soft ping per Site', 'CP2077 target marker pops at +2 f; WD2 label pops 6 f. Borrow: +2 f, 6 f pop.',
         'SNAP', 'rings dropped; the tower fade carries the cue.'),
        ('jackin_towers', 'ICE towers rise, 1 f stagger', 3, 18, 'OUT_BACK_SOFT',
         'Sites grow a body, nearest HOME first, so the eye is pulled out toward the corp. Idle Sites rise short.',
         'ten soft ticks, pitch stepping up (a zip)', 'CP2077 list stagger 2 f, readable by 6-8 f. Beat: 1 f stagger x 10 + 6 f rise; readable by f12.',
         'SNAP', 'all towers fade in together over 8 f LINEAR, no rise, no stagger.'),
        ('jackin_hq', 'Corp cage ignites', 2, 12, 'OUT_CUBIC',
         'The thing we are here to hit lights up and answers: a hot ring leaves it.',
         'low organic hum swells', 'Frozen Synapse flare ramp (about 6 f up). Borrow: 10 f ring.',
         'SNAP', 'cage fades up over 8 f; no ring.'),
        ('jackin_ui', 'HUD and hand slide in', 4, 10, 'OUT_CUBIC',
         'Controls arrive after the world, never before: the grade is the mode change, UI is secondary.',
         'card-slide whisper x5', 'CP2077 panel +4 f, list readable by +6-8 f. Borrow: +4 f, 6 f, hand stagger 0.8 f.',
         'SNAP', 'fade 6 f, no slide, no stagger.'),
        ('jackin_ready', 'Input live', 12, 12, 'STEP',
         'The board is mine to touch; towers may still be settling (they finish by f18).',
         'none', 'CP2077 full list readable by about 8 f (0.27 s). Beat: 12 f (0.40 s) with 3x the content.',
         'NONE', 'same frame.'),
    ],
    extras=[
        ('first_jackin_grade_f', 24, 'the very first jack-in of a save may take 24 f IN_OUT_CUBIC (Invisible Inc. CGI overlay, 16-24 f). Once per save.'),
        ('first_jackin_tower_stagger_f', 2, 'first-ever stagger 2 f, rise 8 f: about 45 f in all.'),
        ('jackin_front_feather_px', 220, 'soft edge of the radial grade front.'),
        ('jackin_front_glow', .55, 'brightness of the lit front line (not in reduce-motion).'),
    ],
)

# ------------------------------------------------------------------ 02 card draw
board(
    id='02', slug='draw', title='CARD DRAW', render='draw',
    means='A card leaves the deck strip, turns over in the air and takes its place in the hand: nothing was added to the board.',
    total=20, ready=16,
    frames=[0, 2, 4, 6, 8, 10, 12, 16],
    beats=[
        ('draw_lift', 'Deck top lifts', 0, 2, 'OUT_QUAD', 'The deck notices me: the top card peels up 6 px (anticipation).',
         'paper peel tick', 'ITB deploy: ring flash first (6 f). Beat: 2 f lift, shorter than ITB.',
         'SNAP', 'skipped; the card simply appears in the slot.'),
        ('draw_fly', 'Arc to the hand slot', 2, 12, 'OUT_CUBIC', 'Fast out, slow in: it is thrown, then placed. The arc is a Bezier through (1480,760).',
         'card-slide whoosh, pitch falls', 'ITB placement about 18 f total. Beat: 16 f total (2+10+4).',
         'SNAP 2 f', 'no arc: the card cross-fades in at its slot over 6 f.'),
        ('draw_flip', 'Back-to-face flip', 6, 10, 'IN_OUT_QUAD', 'The face is revealed mid-flight, scaleX through 0: what I drew is visible before it lands.',
         'single tick at the edge-on frame', 'Mini Metro ring pop 10 f. Beat: 4 f.',
         'SNAP', 'no flip: the face shows from the first frame of the fade.'),
        ('draw_settle', 'Landing settle + dust ring', 12, 16, 'OUT_BACK', 'It lands with a 6% squash and a small ring: it has weight.',
         'soft paper thud', 'Placement cheat: 12 f drop + 4 f settle + ring flash. Beat: same 4 f settle.',
         'SNAP', 'no squash, no ring.'),
        ('draw_reflow', 'Hand makes room', 2, 10, 'OUT_CUBIC', 'The hand slides apart before the card arrives: there is a place for it.',
         'none', 'CP2077 hover list swap about 4 f. Beat: 8 f slide (it is a layout move, not a state swap).',
         'SNAP', 'cut at f2.'),
        ('draw_stagger', 'Next card of a multi-draw', 4, 4, 'STEP', 'A draw of five reads as a rhythm of five, 4 f apart.',
         'five ticks, equal spacing', 'WD2 label stagger 6 f. Beat: 4 f.',
         'FF', 'stagger 2 f, no arcs.'),
    ],
    extras=[('draw_arc_apex_px', 200, 'Bezier control height above the straight line.'), ('draw_squash', .06, 'landing squash.')],
)

# ------------------------------------------------------------------ 03 drag and drop onto a Site (valid + invalid)
board(
    id='03', slug='drag', title='CARD DRAG AND DROP ONTO A SITE', render='drag', two_rows=True,
    means='Valid: the card is carried, the Site answers (lime ring, ghost wall, outcome tile), the card becomes the program. Invalid: the Site refuses (red grease circle-slash), the card is shoved back to the hand.',
    total=36, ready=26,
    frames=[0, 3, 10, 14, 24, 30],
    frames_invalid=[0, 10, 14, 18, 26, 34],
    beats=[
        ('drag_pick', 'Pick up (lift)', 0, 3, 'OUT_BACK', 'Mine now: the card lifts to 1.12x, straightens, its shadow grows.',
         'paper pick tick', 'CP2077 selection outline jumps in 1 f; ITB tiles snap 1 f. Beat: 3 f, since a card has mass.',
         'SNAP', 'lift cut in 1 f, no overshoot.'),
        ('drag_follow', 'Follow cursor, lag 2 f, tilt by velocity', 3, 10, 'IN_OUT_QUAD', 'It trails the cursor, tilting into the motion (max 9 deg): it is a thing in my hand, not a cursor.',
         'faint continuous paper-drag', 'No reference drags cards. Beat: critically damped, 2 f lag, tilt cap 9 deg.',
         'NONE', 'follow with no tilt.'),
        ('drag_hover', 'Site answers (hover preview)', 10, 16, 'OUT_CUBIC', 'The Site wants it or refuses it before I let go: lime ring + ghost wall + the outcome tile in place. Preview, not commit.',
         'valid: rising two-note; invalid: single low tick', 'Cheat: response disc hover gets a 4-6 f ease so it reads as a preview, not a commit. Beat: 6 f.',
         'SNAP 2 f', 'ring and tile appear in a 4 f fade; no pop.'),
        ('drag_drop', 'Drop: card sinks into the Site', 14, 26, 'OUT_CUBIC', 'The card shrinks into the Site pad and disappears: it became the thing standing there.',
         'dull stamp thud', 'Cheat: placement 12 f. Beat: 12 f.',
         'SNAP 2 f', 'card fades over 6 f at the Site.'),
        ('drag_program', 'Program stands up + landing ring', 24, 32, 'OUT_CUBIC', 'The wall rises out of the street; a mint ring leaves it. The tile commits.',
         'glassy hex lock-in', 'ITB deploy: unit appears about 6 f after the ring. Beat: ring 6 f, wall 8 f, overlapped.',
         'SNAP', 'wall fades in 6 f, no ring.'),
        ('drag_refuse', 'Refuse: shake 6 f then return', 14, 20, 'LINEAR', 'INVALID: the card is shoved sideways (3 oscillations, 6 px) and a red grease circle-slash holds on the Site.',
         'short low buzz (no pitch bend)', 'ITB hard snaps, no shake. Beat: 6 px for 6 f is on the card only, never the screen.',
         'SNAP', 'NO shake: the card stays; the grease mark holds 12 f.'),
        ('drag_return', 'Return to hand', 20, 32, 'OUT_CUBIC', 'It goes back where it came from; the hand re-opens its slot. The grease mark fades after (f30-38).',
         'paper slide back', 'Same 12 f as a drop. Beat: symmetric with the valid drop.',
         'SNAP 2 f', 'cross-fade back, 6 f.'),
    ],
    extras=[('drag_lag_f', 2, 'cursor follow lag.'), ('drag_tilt_max_deg', 9, 'tilt cap.'), ('drag_refuse_shake_px', 6, 'card shake amplitude; 0 in reduce-motion.'),
            ('drag_grease_fade_f', 8, 'invalid mark fade after the card has left.')],
)

# ------------------------------------------------------------------ 04 daemon slither
board(
    id='04', slug='daemon', title='THE DAEMON SLITHER', render='daemon',
    means='A parked head waits, then runs the street: the road behind it lights and cools, the head eases through corners like something alive, and dies where something stops it.',
    total=120, ready=34,
    frames=None,
    beats=[
        ('daemon_telegraph', 'Telegraph hold (the plan, lit, waiting)', 0, 30, 'HOLD', 'This is what will happen; nothing is hidden behind hover. The ghost wall, ring and tile sit there.',
         'quiet bed, a 1 Hz sub pulse', 'CP2077 contagion marker waits about 40 f then fires; ITB telegraph persists all turn. Beat: 30 f minimum, never behind hover.',
         'FF', 'identical (it is already static); keep every frame of the hold.'),
        ('daemon_anticipate', 'Head pulls back + charge', 30, 34, 'IN_QUAD', 'It coils: 10 px back along its own street, glow up.',
         'servo wind-up, short', 'ITB attack: line extends about 6 f. Beat: 4 f coil.',
         'SNAP', 'skipped.'),
        ('daemon_travel', 'Travel: 14 px/f cruise, 40% corner slow-down', 34, 83, 'OUT_QUAD', 'It slithers: slow into every corner, quick on the straight, easing to a stop at the wall. About 12 px/f average, 16-19 f per mean 200 px street block.',
         'servo hum rising with speed; soft tick on each Site passed', 'ITB laser 6 f, acid arc 18 f; Bad North longships seconds. Cheat: 12-18 f per street segment. Borrow: 16-19 f per block, the slow edge of the range (cruise is a tuning value).',
         'FF x4', 'NO travel: ribbon cross-fades to lit over 8 f, head fades out at start and in at the stop (state cut).'),
        ('daemon_wake', 'Wake: lit road decays to resting', 34, 103, 'OUT_QUAD', 'The street it has run stays warm and cools over 20 f: you can read where it has been without a trail graphic.',
         'none', 'Google route ribbon: a bright core on the street. Beat: brightness 1.05 -> .55 over 330 px (about 20 f).',
         'SNAP', 'wake not shown; the ribbon is simply lit.'),
        ('daemon_pass', 'Pass-through Site ripple', 57, 64, 'OUT_CUBIC', 'The beam goes by a Site that does nothing: one small ring, no tier mark (declutter rule).',
         'soft tick', 'WD2 sting: label pop 6 f. Beat: 7 f ring.',
         'SNAP', 'dropped.'),
        ('daemon_arrive', 'Arrive: handed to the shield flash (board 07)', 83, 85, 'STEP', 'The head hits the wall: that is the next board, the impact language.',
         'see board 07', 'see board 07', 'SNAP', 'see board 07'),
    ],
    extras=[('daemon_cruise_px_f', 14.0, 'cruise speed on a straight (about 8.4 px/f at a 60 deg corner).'), ('daemon_corner_slow', .40, 'speed loss at a 60 deg turn.'),
            ('daemon_wake_px', 330, 'length of the cooling wake behind the head.'), ('daemon_coil_px', 10, 'anticipation pull-back distance.')],
)

# ------------------------------------------------------------------ 05 sealed lock reveal
board(
    id='05', slug='lock', title='THE SEALED LOCK OPENS', render='lock',
    means='A letter lock rattles, pops open, its letter breaks into pixels and the beam type stands there in its place; the fog under that street clears and the road is drawn out from the corp.',
    total=100, ready=34,
    frames=[0, 15, 18, 21, 25, 29, 32, 38, 50, 70],
    beats=[
        ('lock_idle', 'Locked, waiting', 0, 14, 'HOLD', 'Closed: you can see where the street might run but not what is in it.',
         'quiet static bed', 'ITB: telegraph persists. Beat: idle before reveal is not animated.',
         'FF', 'identical.'),
        ('lock_rattle', 'Anticipation rattle', 14, 17, 'STEP', 'It jitters 2 px for 3 f: something is about to give.',
         'tumbler ticks x3', 'CP2077 marker waits then fires in 1 f. Beat: 3 f rattle.',
         'SNAP', 'rattle replaced by one 3 f brightness pulse (alpha .6).'),
        ('lock_shackle', 'Shackle pops open', 17, 21, 'OUT_BACK', 'It is open: the shackle kicks up and over.',
         'latch click', 'WD2 sticker pop about 6 f. Beat: 4 f.',
         'SNAP', 'cut open on f17.'),
        ('lock_dissolve', 'Letter dissolves into pixel blocks; hue fog -> type', 18, 30, 'LINEAR', 'The letter breaks into pixel blocks that fly off: the secret is leaving; the edge turns from fog lavender to the type hue.',
         'rising digital shatter, 12 f', 'CP2077 target dissolves to red pixel blocks over about 12 f. Borrow: 12 f.',
         'SNAP', 'letter/silhouette cross-fade 8 f, no flying blocks.'),
        ('lock_pop', 'Type silhouette pops (jitter overshoot)', 28, 34, 'OUT_BACK', 'The beam type stands there: dart, block or ram. Overshoot 12% with 2 px jitter, plus a ring.',
         'type timbre: D hi tick, N bleep, E horn stab', 'WD2 sticker pops about 6 f with jitter overshoot, then holds 24-36 f. Borrow: 6 f, jitter.',
         'SNAP', 'fade in 8 f, no overshoot, no jitter, no ring.'),
        ('lock_corridor', 'Fog clears, road drawn out from the corp', 30, 50, 'OUT_CUBIC', 'The corridor resolves into a lit road, drawn outward from the corp: now you know its course.',
         'filtered sweep, fades', 'WD2 city-map street lines draw about 18 f in 3 steps. Beat: 20 f OUT_CUBIC.',
         'SNAP', 'fog -> ribbon cross-fade over 8 f.'),
        ('lock_hold', 'Read hold', 34, 100, 'HOLD', 'It stays long enough to be read: silhouette + road + head parked.',
         'none', 'WD2 sticker holds 24-36 f. Beat: at least 24 f (this board holds 66).',
         'HOLD', 'identical: the hold is the meaning.'),
    ],
    extras=[('lock_rattle_px', 2, 'rattle amplitude.'), ('lock_pop_overshoot', .12, 'silhouette overshoot (via OUT_BACK 1.70).'), ('lock_read_hold_min_f', 24, 'minimum read hold.')],
)

# ------------------------------------------------------------------ 06 hunter reticle lock
board(
    id='06', slug='hunter', title='THE HUNTER LOCKS ONE STREET', render='hunter',
    means='A white eye looks around, opens, and a reticle slams onto one of two streets; the other street is struck out. The marked street then waits.',
    total=80, ready=28,
    frames=[0, 8, 14, 18, 22, 25, 30, 40, 70, 76],
    beats=[
        ('hunter_scan', 'Eye scans (looks left, right)', 0, 12, 'IN_OUT_QUAD', 'It is looking: slow side-to-side, 24 f period.',
         'faint servo', 'Bad North: the silhouette is the cue. Beat: slow idle.', 'FF', 'eye static, 24 f breathing removed.'),
        ('hunter_open', 'Iris dilates', 12, 16, 'OUT_BACK', 'It has found something: the eye opens 18%.',
         'servo catch', 'CP2077 marker pop +2 f. Beat: 4 f.', 'SNAP', 'cut open.'),
        ('hunter_acquire', 'Reticle homes in from 3.2x', 16, 24, 'OUT_EXPO', 'Fast, then precise: the reticle crashes in on one street.',
         'rising servo whine, 8 f', 'CP2077 hack: telegraph marker then 1 f burst. Beat: 8 f expo-out.', 'SNAP 2 f', 'reticle fades in on the street (6 f), no travel.'),
        ('hunter_click', 'Lock click', 24, 28, 'IN_OUT_QUAD', 'The four corners thump inward 14% and bounce: LOCKED. One white flash frame.',
         'two-tone pip-PIP', 'Frozen Synapse flash; ITB snap. Beat: 4 f thump + 1 f flash.', 'SNAP', 'no thump, no flash.'),
        ('hunter_strike', 'Other street is struck out + dims 78%', 26, 34, 'OUT_CUBIC', 'The street it did not pick is crossed out and dimmed: the choice is made.',
         'short scratch', 'Invisible Inc.: zones outside vision go dark. Beat: 8 f.', 'SNAP', 'dim 78% in 8 f LINEAR, X appears complete.'),
        ('hunter_wait', 'Locked-target hold', 28, 64, 'HOLD', 'It waits: the player reads which street. No motion except the eye breathing.',
         'tense hush, no music change', 'CP2077 contagion marker waits about 40 f. Beat: 36 f.', 'HOLD', 'identical.'),
        ('hunter_fire', 'White ram runs the street, turns yellow behind', 64, 76, 'LINEAR', 'It strikes: a white head runs the marked street, the road behind it turns E yellow.',
         'horn stab on contact', 'ITB laser 6 f. Beat: 12 f (street is 385 px).', 'FF x4', 'ribbon cross-fades in over 8 f, head at the end.'),
    ],
    extras=[('hunter_reticle_start_scale', 3.2, 'initial reticle scale.'), ('hunter_wait_min_f', 30, 'telegraph hold floor.')],
)

# ------------------------------------------------------------------ 07 shield flash
board(
    id='07', slug='shield', title='THE SHIELD FLASH WITH BITS', render='shield',
    means='The beam meets a wall: a white flash, a hex ripple that spreads and holds, binary bits fly out, the head dies; the wall is left cracked and the HOLDS tile pops.',
    total=52, ready=16,
    frames=[0, 1, 2, 4, 8, 12, 18, 22, 30, 44],
    beats=[
        ('shield_flash', 'Contact flash frame', 0, 2, 'STEP', 'Contact: white, brightest on f0 and f1 only.',
         'glass tap + low thump', 'ITB hit: first white frame f3; CP2077 spark f1. Beat: f0 is the white frame.',
         'SNAP', 'ONE 3 f brightness step, capped at alpha .30, no strobe.'),
        ('shield_ripple', 'Hex ripple spreads', 1, 8, 'OUT_EXPO', 'The wall rings like struck glass: hex cells light outward from the point of contact.',
         'hex chime, decaying', 'CP2077 bloom peak f5-7. Beat: ripple reaches full size f8.', 'SNAP', 'ripple at full size from f0, 3 f fade in.'),
        ('shield_peak_hold', 'HOLD at the peak', 4, 12, 'HOLD', 'It holds the bright moment so the block is felt: 8 f.',
         'sustained ring', 'Cheat: peak f4-7, HOLD 6-8 f. CP2077 still bright at f11+. Beat: 8 f hold.', 'HOLD min 3 f', 'identical (hold kept).'),
        ('shield_bits', 'Bits fly out', 2, 20, 'OUT_QUAD', 'Debris of the beam leaves in all directions: it was destroyed, not stopped politely.',
         'dry binary tick-spray', 'Frozen Synapse streak lines. Beat: 18 f scatter, 12 f fade.', 'FF', 'no bits.'),
        ('shield_decay', 'Wall dims to spent', 12, 24, 'IN_QUAD', 'The flash decays; the wall stays standing but cracked and dimmer: it has been used.',
         'tail', 'Cheat: decay 8-12 f. Beat: 12 f.', 'SNAP', '10 f LINEAR fade of the flash.'),
        ('shield_tile', 'HOLDS tile pops', 16, 22, 'OUT_BACK', 'The outcome appears in place: the shield glyph on a hex.',
         'confirm tick', 'ITB in-place tags, +6 f. Beat: 6 f pop at +16 f.', 'SNAP', '6 f fade, no pop.'),
        ('shield_after', 'Aftermath hold with state in place', 22, 52, 'HOLD', 'The block, tile and spent wall stay for 30 f: the result can be read.',
         'none', 'Cheat: aftermath hold 20-30 f. Beat: 30 f.', 'HOLD min 10', 'identical.'),
    ],
    extras=[('shield_hold_f', 8, 'peak hold.'), ('shield_after_hold_f', 30, 'aftermath hold.'), ('flash_cap_alpha', .30, 'reduce-motion luminance cap.')],
)

# ------------------------------------------------------------------ 08 HOME hit
board(
    id='08', slug='home', title='THE HOME HIT (WITH A HIT HOLD)', render='home',
    means='The beam arrives at my deck and stops; everything goes white for two frames, the screen jolts 3 px, a ring leaves, six ticks fly off the gauge; the moment HOLDS, then the damage stays in place.',
    total=58, ready=28,
    frames=[0, 5, 6, 7, 8, 12, 20, 40],
    beats=[
        ('home_approach', 'Head decelerates into HOME', 0, 6, 'OUT_QUAD', 'It slows as it touches: the last 80 px take 6 f. The six ticks about to be lost sit orange (preview).',
         'servo winds down', 'ITB: arrow then hit. Beat: 6 f decel.', 'SNAP', 'identical, no deceleration.'),
        ('home_flash', 'Impact flash (white 2 f)', 6, 8, 'STEP', 'Impact: white at f6 and f7, orange after.',
         'heavy thud + glass', 'ITB white flash f3, CP2077 spark f1. Beat: f6 is the white frame.', 'SNAP', 'ONE 3 f orange-white step, alpha .30.'),
        ('home_shake', 'Screen shake 3 px, 4 f, decaying', 6, 10, 'STEP', 'The frame jolts diagonally along the beam, (3,-2) (-3,2) (2,-1) (-1,1): the only shake in the game.',
         'low-end rumble 4 f', 'No reference shakes or hit-stops. Beat: 3 px / 4 f at the HOME hit ONLY.', 'SNAP', 'REMOVED. No shake, ever, in reduce-motion.'),
        ('home_shock', 'Shock rings', 6, 18, 'OUT_EXPO', 'Two rings leave the deck (100 and 150 px): the blast.',
         'sub boom tail', 'Frozen Synapse flare about 20 f. Beat: 12 f.', 'SNAP', 'ring dropped; a single static 100 px ring fades in 4 f.'),
        ('home_hold', 'HIT HOLD: the peak is held', 8, 16, 'HOLD', 'Everything else freezes under the held flash, tear and bits for 8 f: the moment is long enough to take in.',
         'sustained ring, high filter', 'Cheat: HOLD 6-8 f at the peak. Beat: 8 f.', 'HOLD min 3 f', 'identical (hold kept).'),
        ('home_sparks', 'Six ticks fly off the ring', 7, 23, 'OUT_QUAD', 'The damage is physical: the six lost gauge ticks leave as sparks.',
         'six metallic pings', 'Mini Metro: pressure as a physical quantity. Beat: 16 f.', 'FF', 'ticks dim in place, 8 f.'),
        ('home_tear', 'Datamosh tear', 8, 14, 'LINEAR', 'The screen tears for 6 f over HOME: it hurts.',
         'digital rip', 'WD2 glitch cut 3-6 f. Beat: 6 f.', 'SNAP', 'REMOVED.'),
        ('home_tile', 'DAMAGED tile + -6 pops', 12, 18, 'OUT_BACK', 'The cost is written in place: solid orange plate, heart glyph, -6.',
         'single low bell', 'ITB POWER LOST tags +6 f. Beat: 6 f pop.', 'SNAP', '8 f fade.'),
        ('home_decay', 'Decay to settled', 16, 28, 'IN_OUT_QUAD', 'The world un-dims; HOME now has six scarred ticks.',
         'tail', 'Cheat: decay 8-12 f. Beat: 12 f.', 'SNAP', 'identical.'),
        ('home_after', 'Aftermath hold with damage in place', 28, 58, 'HOLD', 'The scarred ring, tile and number stay 30 f.',
         'none', 'Cheat: 20-30 f. Beat: 30 f.', 'HOLD min 10', 'identical.'),
    ],
    extras=[('home_shake_px', 3, 'amplitude; 0 in reduce-motion.'), ('home_shake_f', 4, 'duration.'), ('home_hold_f', 8, 'hit hold.'),
            ('home_dim_amount', .50, 'world dim during the hit (reduce-motion .25).'), ('home_telegraph_hold_f', 30, 'before the approach.')],
)

# ------------------------------------------------------------------ 09 poster slam
board(
    id='09', slug='poster', title='THE WHEATPASTE POSTER SLAM', render='poster',
    means='The verdict is slapped on the city: blocks of verdict colour flash and clear, a paper poster flies at the screen and is stuck down with a jolt; it stays.',
    total=48, ready=18,
    frames=[0, 3, 6, 9, 10, 12, 14, 18, 30],
    beats=[
        ('poster_dissolve', 'Pixel-block dissolve of the patch', 0, 10, 'LINEAR', 'The city under the poster breaks into blocks of the verdict colour: something is about to be put here.',
         'digital crunch', 'CP2077 dissolve about 12 f; WD2 takeover blocks 8-12 f. Beat: 10 f.', 'SNAP', '6 f cross-fade of the poster; no blocks.'),
        ('poster_slap', 'Poster slaps in: 1.5x -> 1.0x', 8, 12, 'IN_CUBIC', 'It comes AT me and hits the screen: scale falls, shadow tightens.',
         'wet slap + paper crack', 'WD2 sticker pops about 6 f overshoot. Beat: 4 f slap + 6 f jitter.', 'SNAP', 'fade in at the final pose.'),
        ('poster_jitter', 'Jitter overshoot', 12, 18, 'LINEAR', 'It settles with a 5 px, 2 deg wobble that dies in 6 f: it was pasted by hand.',
         'paper rustle', 'WD2: jitter overshoot about 6 f. Beat: 6 f.', 'SNAP', 'REMOVED.'),
        ('poster_puff', 'Paste puff', 12, 17, 'OUT_EXPO', 'A pale puff and ring leave the corners: wet paste.',
         'none', 'Frozen Synapse flare. Beat: 5 f.', 'SNAP', 'REMOVED.'),
        ('poster_hold', 'Read hold', 18, 48, 'HOLD', 'The verdict stays at least 24 f: this is the poster read.',
         'none', 'WD2 sticker holds 24-36 f. Beat: 30 f.', 'HOLD', 'identical (hold kept).'),
    ],
    extras=[('poster_hold_min_f', 24, 'minimum read hold.'), ('poster_jitter_px', 5, 'jitter amplitude; 0 in reduce-motion.')],
)

# ------------------------------------------------------------------ 10 Bloom creep
board(
    id='10', slug='bloom', title='THE BLOOM CREEPS (DECAY)', render='bloom',
    means='A fallen Site drains its clock, then a dark plum wound seeds in it and creeps outward in a visible tick, eating the lights behind its hot edge, until it fills its district.',
    total=105, ready=30,
    frames=[0, 14, 20, 26, 34, 48, 62, 76],
    beats=[
        ('bloom_clock', 'DOWN clock drains', 0, 20, 'LINEAR', 'The ring on a fallen Site eats itself: time is running out on it.',
         'ticking, slowing', 'Mini Metro ring timer. Beat: 20 f.', 'FF', 'hold the DOWN state; ring static.'),
        ('bloom_seed', 'Plum seed pops', 20, 26, 'OUT_BACK', 'The Site turns: a seed of dark plum pops with a small overshoot.',
         'wet low pop', 'Cheat: each cell pops 0.8 -> 1.0, 6 f ease-out. Beat: 6 f.', 'SNAP', 'part of the state cut.'),
        ('bloom_creep', 'Creep: one visible step every 5 f', 26, 76, 'OUT_QUAD', 'It advances in visible beats, like a clock: ten steps, each 3 f. You can count it.',
         'crackle tick per step, organic bed', 'Cheat: stagger new cells every 4-6 f. WD2 labels 6 f; Mini Metro line extrusion about 10 f. Beat: 5 f / step.', 'FF x4', 'NO creep: the whole wound cross-fades in over 8 f (state cut + held peak).'),
        ('bloom_windows', 'Windows die behind the front', 29, 80, 'OUT_QUAD', 'Lights behind the hot edge go out: the city is dying, not covered.',
         'none', 'Bad North: fire/collapse as the loss language, over seconds. Beat: follows the front.', 'FF', 'same, as part of the cross-fade.'),
        ('bloom_card', 'INFECTED cards fly to the deck strip (board only)', 30, 46, 'OUT_CUBIC', 'The damage becomes cards in my deck: that is the real cost of decay.',
         'paper flick x3', 'ITB tags. Beat: 16 f arcs.', 'SNAP', 'cards appear in the strip; no flight.'),
        ('bloom_hold', 'Wound hold', 76, 105, 'HOLD', 'It stops; the front stays hot and still for 30 f.',
         'none', 'Cheat: aftermath 20-30 f. Beat: 30 f.', 'HOLD', 'identical.'),
    ],
    extras=[('bloom_step_f', 5, 'frames between steps.'), ('bloom_step_ease_f', 3, 'frames of each step.'), ('bloom_steps', 10, 'steps from seed to full.'),
            ('bloom_state_cut_f', 8, 'reduce-motion cross-fade.')],
)

# ------------------------------------------------------------------ 11 CITY LOST
board(
    id='11', slug='lost', title='THE CITY LOST FLOOD AND SKULL', render='lost',
    means='The last Site falls and HOME is hit for the last time; the plum Bloom floods the whole map, the colour drains, the screen tears, and a skull is stamped on the ruin.',
    total=100, ready=70,
    frames=[0, 4, 10, 20, 34, 48, 58, 66],
    beats=[
        ('lost_hit', 'Last hit (board 08 hit, 8 f hold)', 0, 8, 'STEP', 'The final hit lands exactly as before: flash, ring, 8 f hold: the loss is not a different language.',
         'heavy thud, then silence', 'ITB base damage. Beat: reuse board 08.', 'SNAP', 'same as board 08 reduce.'),
        ('lost_flood', 'Bloom floods the map', 8, 56, 'IN_OUT_QUAD', 'Loss is slow and total: 48 f of plum rising from every fallen Site and from HOME.',
         'sub-bass fall, organic growl', 'Cheat: loss escalation over seconds not frames; Bad North fire. Beat: 48 f.', 'FF x4', '12 f cross-fade to the final flooded state; no growth.'),
        ('lost_desat', 'Colour drains', 20, 44, 'IN_OUT_QUAD', 'The world loses its colour: this is no longer a living city.',
         'filter closes', 'CP2077 grade as the mode change. Beat: 24 f, 55% desaturation.', 'SNAP', 'same, 24 f LINEAR.'),
        ('lost_tear', 'Datamosh tear', 44, 50, 'LINEAR', 'The picture tears once: system failure.',
         'digital rip, short', 'WD2 glitch 3-6 f. Beat: 6 f.', 'SNAP', 'REMOVED.'),
        ('lost_skull', 'Skull slams in 1.6x -> 1.0x, jitter 4 f', 56, 62, 'OUT_BACK', 'The verdict: a skull, bone-pink, stamped on the ruin.',
         'single bell, sub drop', 'WD2 sticker pop 6 f overshoot. Beat: 6 f + 4 f jitter.', 'SNAP', 'fade 12 f at final size.'),
        ('lost_ring', 'Skull ring draws', 60, 70, 'OUT_CUBIC', 'A ring closes round it: sealed.',
         'none', 'Mini Metro ring pop 10 f. Beat: 10 f.', 'SNAP', 'complete.'),
        ('lost_hold', 'Hold before any button', 70, 100, 'HOLD', 'Nothing moves for 30 f: the player takes it in before they may act.',
         'none', 'Cheat: 20-30 f hold. Beat: 30 f.', 'HOLD', 'identical.'),
    ],
    extras=[('lost_desat_amount', .55, 'desaturation.'), ('lost_buttons_after_f', 70, 'buttons enable after the skull ring.')],
)

# ------------------------------------------------------------------ 12 jack-out
board(
    id='12', slug='jackout', title='JACK-OUT', render='jackout',
    means='Out is faster than in: the controls drop at once, the towers sink, the grade collapses back into my deck, one flicker of fringe, and the plain city map is back.',
    total=10, ready=10,
    frames=[0, 1, 2, 3, 4, 5, 7, 10],
    beats=[
        ('jackout_ui', 'UI drops', 0, 3, 'IN_CUBIC', 'The controls are gone first: I am no longer in the layer.',
         'cards slide away, short', 'CP2077 exit: panels gone by +3 f. Beat: 3 f.', 'SNAP', 'fade 6 f.'),
        ('jackout_towers', 'Towers sink, reverse stagger 0.5 f', 0, 6, 'IN_CUBIC', 'The Sites drop back into the ground, farthest from HOME first.',
         'soft thunks collapse into one', 'CP2077 exit asymmetric. Beat: 4 f each, 0.5 f stagger.', 'SNAP', 'fade 6 f.'),
        ('jackout_ungrade', 'Grade collapses to HOME', 2, 8, 'IN_QUAD', 'The grade is sucked back into my deck: the way in, reversed, faster.',
         'down-sweep, 6 f', 'CP2077 exit: un-grade about +5 f. Beat: 6 f, starting at f2.', 'SNAP', '6 f IN_OUT_QUAD global cross-fade.'),
        ('jackout_fringe', 'Chromatic fringe + one scan tear', 4, 10, 'OUT_QUAD', 'A last flicker: the signal drops.',
         'static burst, 6 f', 'CP2077 exit: rainbow fringe + purple scanline glitch 6-8 f. Borrow: 6 f.', 'SNAP', 'REMOVED.'),
    ],
    extras=[('jackout_total_f', 10, 'whole jack-out (in is 18 f: asymmetric on purpose).')],
)


GLOBAL = [
    ('fps', 30, 'timeline rate; every `_f` value is in frames at this rate.'),
    ('skip_snap_f', 2, 'a SNAP beat jumps to its end state in this many frames when the player skips.'),
    ('skip_speed', 4.0, 'FF beats play at this multiple when the player holds skip.'),
    ('skip_hold_min_f', 3, 'an impact hold is never shorter than this when skipped.'),
    ('reduce_grade_cross_fade_f', 8, 'every mode-change grade becomes this cross-fade.'),
    ('reduce_flash_f', 3, 'every flash becomes ONE brightness step this long.'),
    ('reduce_flash_cap_alpha', .30, 'luminance cap of that step.'),
    ('reduce_fade_f', 6, 'default replacement for a pop or slide: fade this long.'),
    ('reduce_keep_holds', True, 'holds (telegraph, impact peak, aftermath, read) are never shortened by reduce-motion.'),
    ('reduce_shake_px', 0, 'shake and jitter are removed.'),
]
