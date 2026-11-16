"""Strip texts for transitions v6 (T2, T4). B-107 rulings."""
T2TXT = {
    'title': 'T2 v6  Street to room, 1.2 s: camera only, the room stays as it is (B-107)',
    'blocks': [
        ('Paradigm (golden plates)', 'The netrun street is the golden plate hq_rebel_cell_decision (art lead): a high oblique view square-on to one straight street, lit cut-away rooms in the frontage buildings and the ground cut open in section on underground tiers. Each room: front wall hidden, '
         'our 3D room inside drawn from that same camera, lit cut edges and a hatched slab, nodes joined by lines (lime walked, orange next, '
         'white dashed ahead). No boxed render, no room card expanding into the fight.'),
        ('What moves', 'Only the camera: pan to the chosen room, tilt and roll into the combat pose (zoom about 4.2, roll -2.5 deg). The room '
         'drawing is identical in K1 and K5. On the way the other rooms get their front walls back (a wall wipe with a 0/1 edge), '
         'so in the fight only our room is open. The street keeps its signage, street FX and lighting.'),
        ('Signage', 'Generic words replaced with Solace-district shop words on every light box and blade: MOSS&MILK, GENE CLINIC, SPORE, '
         'HYDRO, SOLACE CARE+, SEED BANK, CLONE SPA, MOSS, PHARMA. MAINFRAME is only the real MAINFRAME shop in '
         'Rebel Cell territory (K10): the 3D shop room plus its red sign as decor.'),
        ('Timing', 'Click 0.00, route pulse 0.15-0.55, camera 0.15-1.20 (ease in-out), walls closing 0.30-0.90. Hand-over to T3 at 1.20 s: '
         'T3 builds the wheel over the room (unchanged from v5).'),
        ('Badges', 'NEW 2D PLATE = the netrun street paint-over of the golden plate hq_rebel_cell_decision. CONCEPT = motion frames.'),
    ]}
T4TXT = {
    'title': 'T4 v6  Fight ends, 0.8 s back: only the wheel to bits; won and lost (B-107)',
    'blocks': [
        ('Won (W1-W8)', 'Only the wheel dissolves to bits; the screen and the street stay. The bits flow back into the 3D room and the room turns '
         'our colour (lime). The reward screen blooms as bits out of the room (SITE TAKEN, +credits, program, run health kept). On CONTINUE '
         'the screen goes back to bits into the room and each reward flies as bits to where it was added (credits to the purse, the program '
         'to the deck). Then the combat camera reverses (un-roll, un-tilt, pan) to the netrun street view; the walls dissolve again and the '
         'lines and outlines redraw.'),
        ('Lost (L1-L8)', 'Run health 0. Only the wheel dissolves to bits into the room; the room flickers our colour for about 1 s and stays '
         'corporate. The loss screen rises as bits from the screen bottom and typewriters onto the page (the design C trace printout). On '
         'GRID VIEW the camera returns to the netrun view and the lost room keeps its wall (not dissolved again, red outline). Then the '
         'netrun zoom reverses to the city map; the site stays Solace. No glitch fail view.'),
        ('Timing', 'Wheel to bits 0.00-0.35, room recolour 0.20-0.45 (lost: flicker 0.15-1.15), reward bloom 0.35-0.60, close 0.35, camera back 0.80.'),
    ]}
