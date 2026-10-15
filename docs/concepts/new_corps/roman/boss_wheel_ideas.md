# Aurelian Concord: boss wheel ideas (for the Boss Wheel v2 agent)

Boss wheels moved to `docs/concepts/boss_wheel_v2/` (coordinator, 2026-10-15). What is here is reference only.

## What exists (reference, not final)
- `boss_wheel_options.png`: three motifs on the unchanged round 41 D4 renderer: A COLOSSEUM (picked), B ARENA, C EMPEROR.
- `boss_wheel.png`: option A finished: rim = two tiers of arcade arches, the arcade "facade" wraps both flanks outside the
  threat ring (kept clear of the banner/pointer at the top and the HP arc at the bottom), laurel-arch lugs, a carved
  travertine thumbs-down in the hub.
- `scripts/wheel41.py`: how the new theme plugs into round 41 without editing it (theme rows in CORP_STYLE, MO.ACCENT,
  slicelib.CORPS, skins.SKINS/BOSS, scenes18.SCENES/PAL, RW.CORP_EMBLEM via crests15.CUSTOM; wrapped corp_rim / crest /
  _hub_std). The slice skin (porphyry + verdigris meander + arcades) and six slice scenes (gladius, trident, testudo,
  sand + parma, falling sand, the crowd's thumbs for VERDICT) are reusable as they are.

## Ideas worth keeping
1. **The Circus is the wheel.** The HQ is a colosseum of turning rings (hq_overview.png, the TURNING GATES). A boss
   wheel whose layers are the HQ's seating rings (each ring a counter-rotating band with its own gate notches) ties the
   map, the HQ run and the boss together. The gates could show where the next pointer appears (a Migrate telegraph).
2. **VERDICT on the wheel.** The house rule marks a player slice; the boss's special slice is the crowd. The marked
   player slice could carry a small thumb badge; the boss rail could read `VERDICT // MARK`.
3. **Hub = the emperor's box**, not a portrait: a thumbs-down (designer: good idea, cleaner execution) with the
   toga cuff. Avoid the bust (reads as "museum").
4. **Phase 2:** the arcade openings change from verdigris to gilt (the crowd turns), and the Grand Stand (hub) lights.
5. Palette: verdigris #29DBA6 (corp hue), travertine #E9D5AA (material / tier II), porphyry #3A1426 (backs), gilt
   #C9A35A only as small accents (it sits near Exploit gold).
6. Emblem: `nc_kit.g_verdict3` (thumbs-down) is the current pick; it passes the 32 px twin check (max soft IoU 0.61
   against the whole new set).

## Designer review round 2 (2026-10-15)
- The boss emblem is still the weak point. The designer clarified it wants the **emoji THUMBS-DOWN look**: a bold,
  chunky cartoon thumbs-down hand, a rounded fist, the thumb pointing down, simple flat shading with one highlight, a
  thick dark outline and a slight 3/4 angle. It should be in our sticker style, with Roman flavour: a gold or laurel
  cuff at the wrist, an imperial-purple sleeve edge, the corp palette. It must be an original drawing (no platform
  emoji art copied) and **not a face**.
- It must still match the Boss Wheel v2 **colosseum** direction.
- A first pass at that brief is `nc_kit.emblem_thumb_cartoon()`, shown on `crest_icons.png`: a puffy fist turned 12°,
  a gilt cuff with a verdigris laurel, a purple sleeve, skin-gold with one shadow side and one highlight, an ink outline
  of about 17 px at 512. Use it as a reference or a starting point.
