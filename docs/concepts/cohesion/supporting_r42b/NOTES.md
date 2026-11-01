# Supporting r42b: Terminal event card CAM feed (O-9)

r42 left the card's CAM photo as the old pale slab (a crop of the round-24 Solace regular-night frame). r42b swaps only that feed for a real security-cam frame, tinted Solace. `supporting_r42/` is untouched.

Files: `01_cam_options_sheet.png` (old slab + options A/B/C at 1:1 with source crops), `01_terminal_event.png` (re-rendered, pick A), `01b_terminal_event_memo.png` (re-rendered; the memo variant has no CAM, so pixel-identical to r42), `07_heat_strip_by_page.png` (copied from r42: the event row is only the top 130 px of the card, above the feed, so unchanged; verified pixel-identical), `old_vs_new.jpg`, `squint_01_terminal_event.png`, `squint_01b_terminal_event_memo.png`. Scripts in `scripts/`.

## Options (all compositing; every pixel is from the two source frames)
- **A  CORNER CAM, HIGH (PICK)**: `combat_backdrop/v3_1/room_event_bare.png` crop (1100,340)-(1860,856): the whole Solace event room from a high corner, beds, fridges, the purple cone machine, door sign at the bottom. Fisheye k 0.16.
- **B  DOOR CAM, STREET LEVEL**: same frame, crop (1170,736)-(1640,1055): the SOLACE sign, vertical SOLACE blade and the glass doors, fisheye k 0.22. Reads well as "locked door" but is mostly roof/sign, no ward inside.
- **C  NETRUN STREET, STOREFRONTS**: `netrun_cel/zoom_rules/round6/street_frame.png` crop (1330,504)-(1920,906): right-hand storefronts and towers at street level, fisheye k 0.24, gain 1.45. Honest street-cam look and ties to the netrun street, but with no Solace read (the sign text is lost at 280 px) and the muddiest.

## Treatment (scripts/cam.py)
crop -> resize to 280x190 (low-res cel) -> barrel fisheye (bilinear remap) -> luminance posterized to 6 steps -> Solace duotone (dark green 2,14,10 to Solace green 61,255,139; 74-80% duotone, the rest a coarse 4-level copy of the original hue so pinks and cyans survive faintly) -> 2x nearest to 560x380 -> scanlines (every 3rd row 0.62, next 0.92), 1 px chroma split, rolling brightness bar, one horizontal tear line, grain, vignette -> HUD: red REC dot + `CAM 04  MAINT. WARD` (unchanged label), timestamp `11.01  03:41:07` bottom left, `SOL-NET  CH4` bottom right, green corner ticks, the old dark 6 px frame.

## Pick: A, why
It is the only option that shows a ward with someone possibly in it (the story: a maintenance ward running on battery, a runner inside), it is already a high-angle view so it reads as a corner cam, the room's own green neon makes the Solace tint feel native, and it matches the cutaway used for reward/shop/rack. B is the runner-up if the card ever wants an explicit "locked door" shot; C only if the event is moved to a street node.

## Choices made overnight
- Kept the card layout, label text and chips as they were; only the feed bitmap and the grease-pencil annotation changed.
- The red circle and "WARD" scrawl were repositioned onto the new frame (circle on the room's bed/machine cluster, local feed coords in `cam.OPTIONS[...]["circle"]`/`["ward"]`, since the old circle sat on the slab's door). Pencil style unchanged.
- Gain of 1.3 on A (brighter) so the feed holds against the dark card; the first pass sank into the panel.
- Timestamp date 11.01 and 03:41:07 are placeholders; `SOL-NET CH4` is invented flavour (no corp-text rule broken: it names Solace's own net).
- The 07 strip needs no rerun; if the feed ever moves up into the top 130 px, rerun `topbar44.py` (it needs 03/04 from r42 copied beside it).
- Rebuild: `python options_sheet.py A`, `python build_event.py A` (arg = option key), `python make_contact_b.py`. `build_event.py`/`event.py` are copies of the r42 ones with `PICK` and the circle patched; the rest of `scripts/` is the unchanged r42 set.

## Squint (1/16)
PASS: the feed reads as a green lit block with a red ring and the card panel still leads; stickers, pencil and chips unchanged. The feed is a touch quieter than the old white slab, which is the intent (the old slab was the brightest thing on the card).

## Process slip
Twice I ran an empty `python -` heredoc by mistake (hung on stdin; both stopped by task id; nothing ran from them).
