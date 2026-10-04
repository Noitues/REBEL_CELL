# Round 32: the reward screen after the takeover, and the MAINFRAME shop

These build on round 31. The designer locked three things there:
- the reward screen, option A (peel from the loot sheet);
- the dialogue screen, option A (a cel bust on a CRT feed);
- the event screens, kept as they are.

Some parts of this round belong to other agents, so they are only placeholders here:
- the netrun route;
- the MAINFRAME sign (`round32_mainframe_sign/`);
- Microchips;
- Daemons.

## Files

| File | What changed |
|---|---|
| `reward_screen_v2.png` | **The Cell took the building.** The backdrop is reframed so the target depot sits under the loot sheet. Inside the depot only, its Meridian lights are recoloured to Cell colours: lime outlines and pink hazard stripes. The rest of the district dims to about 62 %. The streets keep Meridian yellow, so the taken building stands out. A yellow grease-pencil note reads "OURS NOW". |
| `shop_v2.png` | The full shop, with every change from the list below. |
| `shop_slice_wheel.gif` (1.4 MB) | Entering the shop, the slice wheel spins with motion blur, eases out and stops (ZERO-DAY lands at the pointer). Then the 5 slices not for sale grey out, the top 3 get a lit arc, and their price tags drop in. |
| `removal_options.png` | Four replacements for SHRED. The best two are rendered: **A PURGE**, the rm -rf key (recommended), and **B DEGAUSS**, the magnet coil. DEFRAG and RECYCLE BIN are sketches. |

## Shop changes (designer list)

- **The MAINFRAME sign is a placeholder.**
  - The old letters are blanked and MAINFRAME is drawn as blue tubes.
  - The pink spill on the facade is shifted to blue, and a PLACEHOLDER SIGN label is added.
  - Swap in the real sign when `round32_mainframe_sign` lands.
- **The clerk screen moved down.** It now sits at y 728–1058, under the sign plate, so the whole sign shows.
- **The MODEM sticker is gone.** In its place is a grease-pencil note on the clerk screen: "ask about the back room".
- **Slices come from a wheel**, not a sticker rack. Details are in the next section.
- **Removal is PURGE.** On the board, a red rm -rf keycap replaces the shredder. It's labelled "PURGE A CARD", with the hint "drop a card on the key" and a price tag of 50 (+25 each time, per GDD 11.2).
- **LEAVE is louder.** LEAVE is in holographic-foil vinyl letters. A pink triple-chevron arrow sticker sits beside it and a small pink "THE MAINFRAME" tag sticker sits under it. It stays in the sticker language but has colour and direction. In motion, the chevrons should nudge right on idle (the GIF hook is `wiggle` in `shop2.py`).
- **Microchips and Daemons are placeholders.** Each has a dashed placeholder box: "placeholder: own design pass".

## The slice wheel (design)

- **Spin.** An 8-slice stock wheel spins once on entry, using a seeded shop RNG stream. It is a *random event*, so it sets a checkpoint, per the GDD rule. It cannot be respun.
- **Offer.** Only the slice under the pointer and its two neighbours are for sale. Price tags hang radially outside those three slices. The tag shows the slice overwrite price (100). The centre slice can carry a premium (shown as 120); that is a proposal, and the number belongs in config.
- **The rest.** The other five slices get a greyscale + dark shader at 55 %. They are visible, so you see what you missed, but they can't be clicked.
- **Buying.** Dragging an offered slice opens the operative's mini spinner as a slot picker. The MISS slot costs 150, per the GDD.
- **Tiers.** Stock slices show their V2 strong tiers (a II or III border). This needs the open SliceData tier decision.
- **Build.**
  - The wheel is the combat wheel scene in a `stock` mode, and it reuses the combat spin tween.
  - The motion blur is a radial-blur uniform that follows angular speed.
  - The reveal is a 0.6 s tween: the dim mask, then the lit arcs, then the tags drop 40 px with a little settle.

## Removal concepts

| | Concept | Card | Slice | Verdict |
|---|---|---|---|---|
| **A** | **PURGE**: a red mechanical rm -rf keycap | Drop the card on the key. It dissolves into bits (the locked dissolve A) that pour into the key, and a CRT log prints "DELETED". | The same key blanks a slot. | **Recommended.** One verb for both, a terminal joke that fits, and it reuses a locked effect. |
| B | **DEGAUSS**: a coil wand | The sticker's ink slides off, leaving blank vinyl. | The CRT screen wobbles in rainbow rings, then goes blank. | A strong second, and slices really are CRTs. But it needs two separate effects. |
| C | **DEFRAG** | The card breaks into blocks that pack away. | — | Reads as "tidy up", not "delete". |
| D | **RECYCLE BIN** | Peel, crumple, bin it. EMPTY BIN confirms, so it can be undone until then. | — | The most physical option, the least cyber. |

## Scripts

- `assets.py` renders the round 17 slice tiles and wheels, plus `shop_wheel.png` (8 slices).
- `reward.py a` builds `reward_screen_v2.png`. The recolour is `cell_takeover()`: an HSV mask over the depot polygon.
- `shop2.py` (`still|gif`) builds `shop_v2.png` and `shop_slice_wheel.gif`. It imports `shop.py` (round 31: pegboard, tags, label tape) and `removal.py` (for the keycap).
- `removal.py` builds `removal_options.png`. It contains the keycap, dissolve-into-the-key, the degauss warp, the coil and the wiped card.
- `r31lib.py`, `sticker_lib19.py` and `lib17/` are copied from round 31.
- `clear_scratch.py` removes `scratch/` and the caches. All randomness is seeded.
