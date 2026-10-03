# Round 31: reward, Server Rack, Terminal event, dialogue, netrun route, Modem shop

Every screen is 1920×1080 and uses the locked look: vinyl stickers for things that don't change, opaque
grease pencil for plans (yellow) and threats (red), CRT "Screens & Data" panels for the Cell's own systems,
intercepted corp paper for corp artifacts, and Cv2 + E backdrops. Slices come from the round 17 kit with
the V2 strong tiers. Glyphs come from `round17_slice_system/glyphs/`. Card, event and enemy text is the
real content (`content/events/*.tres`, `art_asset.md` appendices).

## Files (* = recommended)

| File | What it shows |
|---|---|
| * `reward_screen.png` | **A, peel from a loot sheet.** The card offers sit on a sticker backing liner (kiss-cut slots, liner print); the hovered card peels and lifts. Firmware drop with a mini spinner and lit valid slots. PAYOUT on CRT. |
| `reward_screen_B.png` | **B, decompiled from the beaten wheel.** Offers rise out of the defeated enemy's empty ring on bit streams (the locked dissolve A, reversed). |
| `reward_reveal.gif` (1.4 MB) | A, with B's bit assembly as the entrance: title slap, the liner slides up, cards build from bits, the pick peels and flies to DECK (17 → 18). |
| * `server_rack.png` | RACK BREACHED. Left: BANKED on CRT (Schematics, Heat, armory) and the rare Daemon pick. Centre: the spinner on the flash bench. Right: the I → II → III ladder (V2 strong). Bottom: the Rack drawer for a swap (dashed = what-if). |
| * `event_screen.png` | Locked Ward (`ev_rescue_operative`). The story is in the Solace-green CRT Terminal with a CAM feed in the world style. Choices are sticker buttons with outcome chips. Grease pencil: the one-off slogan "PLAY IT SAFE??". |
| * `event_screen_memo.png` | Variant: an intercepted Solace memo (`ev_continuum_memo`) taped over the Terminal. Shown after the pick: CHOSEN stamp, the other choice greyed, the result typed in, and the Heat/Cycles changes confirmed. |
| * `dialogue.png` | **A, low-poly cel bust on a CRT comm feed.** The speaker is live; the listener (CELL-9 BREAKER) is dimmed; DISPATCH is queued as a waveform with no face. |
| `dialogue_B.png` | **B, sticker portrait.** The same bust as a die-cut vinyl sticker; the listener is a greyed sticker. |
| * `netrun_map.png` | The route as yellow grease pencil on an intercepted Meridian site plan (paper). Node kinds are stickers, and the final Rack sits in the depot's rack hall. CRT panels: NEXT choices with Heat cost, and the route key. |
| * `shop_interior.png` | The Modem over the MARKET NEON facade. Stock hangs on a pegboard with kraft price tags and label-tape sections. The clerk is the facade's pixel smiley on CRT, with the wallet. Includes the shredder, a SOLD tag, an unaffordable tag, and the BUY / SHRED pencil notes. |
| `contact_sheet.jpg` | Every screen on one sheet. |
| `scripts/` | `make_all.py` rebuilds everything. See the scripts section below. |

## Recommendations

- **Reward: A.** The pick reads instantly. Peel-and-slap is the card language players already learn in combat, and the liner makes "pick 1 of 3" physical: the empty kiss-cut slot shows what you took. Keep B's bit assembly as the entrance animation (the GIF does this).
- **Dialogue: A (CRT feed).** Portraits *change*: hurt, triumphant, flatlined (art_asset B1). By the locked rule, stickers are only for things that don't change, so a sticker portrait breaks the rule. The CRT feed can also glitch, dim and drop out, which is the job a live medium does. DISPATCH never gets a face.
- **Event:** both screens are the same layout. The memo variant is just a paper layer for events whose speaker is corp (`speaker = 2`).

## Medium per element

| Element | Medium | Why |
|---|---|---|
| Screen titles (FIGHT WON, RACK BREACHED, NETRUN, BRIEFING, MODEM), big actions (CONTINUE, UPGRADE, LEAVE THE MODEM, BUY 60, SKIP) | Vinyl sticker (sticker_lib19) | Fixed words. |
| Cards, firmware chips, daemons, slice tiles for sale, route nodes, choice buttons | Die-cut sticker | Objects that don't change. A hover adds lift plus the full gloss sweep. |
| Cycles, HP, Heat, Schematics, wallet, deck count, route NEXT panel, key, story text, dialogue text | CRT panel (Cell's systems) | Live values, and the Cell's own screens. |
| Outcome chips (−12 HP, +1 BREAKER, NO CHANGE) | CRT chip | Live, computed numbers. Green = gain, red = cost, grey = no change. |
| Corp memo, site plan, price tags (kraft), SOLD / CONFIDENTIAL / DO NOT FORWARD stamps | Paper | Corp artifacts, or street paper. |
| Route walked (solid), choices (dashed what-if), numbers, ticks, BUY / SHRED notes, "+1 = 18" | Yellow grease pencil | Plans and notes. These follow the locked path rules. |
| The Rack guardian, WARD, "−20 SHORT", "(bricking)" | Red grease pencil | Threats and costs. |
| Event illustration (CAM feed), backdrops | Cv2 + E render | World style. |
| Section labels in the shop | Label-maker tape | A fixed sticker variant that reads as shop furniture. |

## Layout rules

- The left third holds the context (title sticker plus a CRT strip saying where you are). The centre holds the decision. The right column holds live values.
- One primary sticker action, bottom right (CONTINUE, UPGRADE, LEAVE THE MODEM). SKIP is a smaller grey sticker under the offers.
- Grease pencil only says true things: where the pick goes, what costs too much, who guards the Rack. At most one slogan per screen.
- Offers never overlap a CRT panel. Pencil may cross anything.
- Hover is a sticker lift: scale 1.05–1.08, a 14–26 px rise, gloss 0.6, a bigger soft shadow. On a card, the bottom-right corner also curls. The SOLD state greys the sticker and stamps its tag. When an item is unaffordable, its tag price turns red and a red pencil ring goes round it.

## Designer questions and flags

1. **The Server Rack screen.** In the GDD, a Server Rack is an elite fight that **banks** Schematics and offers rare Daemons. Upgrading a slice is not in the game: slice tiers I–III are a placeholder (SliceData has no tier). The screen proposes that breaching a Rack also gives **one flash**: upgrade one slice by a tier, or swap one slice for one from the Rack drawer. This is a design question for DECISIONS.md, not art.
2. **"Boss HQ" on the route.** By the GDD, the last node is always a Server Rack (the Site's guardian, for example the Logistics Director). The map shows that rather than an HQ.
3. **Card type band (WHEEL / HACK / SYSTEM).** It is kept from C-C, but the GDD card list has no type names. The mapping used here (Overload = HACK, Duck = SYSTEM) is a guess.
4. **The shop clerk as the pixel smiley.** This is a new character choice. Confirm it, or keep the clerk faceless.

## Godot build notes

- **Loot sheet.**
  - The sheet is a `NinePatchRect` liner with the print baked in. Each offer is a `Control` with the card `TextureRect` plus a sticker material (die-cut border, gloss uniform). The peel is the existing curl shader.
  - When an offer is taken, its kiss-cut slot outline stays and switches to a shiny "empty" texture.
  - Unpicked stickers are released on CONTINUE.
- **Bit assembly.** This is the dissolve-A shader (round 19) run backwards: a `progress` uniform runs 1 → 0, and the reveal edge moves top to bottom with per-column jitter. The falling `0`/`1` are a GPUParticles2D emitter sampling the card texture's colour.
- **Fly to deck.** A quadratic Bézier path to the DECK CRT counter. Scale goes 1 → 0.25 and rotation −25°. The counter ticks on arrival (Signal Up: the view emits `card_taken`; the run state adds the card).
- **CRT panel.** One reusable `PanelContainer` StyleBox (glass colour, accent border, corner brackets) plus a CanvasItem shader for the scanlines (every 3 px at 22 %), the top glass sheen and the text glow. The accent colour is a theme constant per use: cyan for the Cell, lime for firmware, gold for Schematics, the corp colour inside corp Terminals, red for DISPATCH.
- **Grease pencil.** `Line2D` with a round cap, width 8–10, near-opaque yellow `#FFE200` / red `#FF1C2C`, and a 2/3 px dark under-shadow `Line2D` beneath it. Dashed what-if lines use a dash texture.
- **Route nodes.** `TextureButton` stickers. A cut-off node uses a greyscale shader at 75 % alpha. The current node gets the pencil ring plus the class token sticker. The walked path redraws as solid on each move.
- **Slices on the Rack bench and in the shop.** These reuse the combat slice scene with the `tier` uniform (V2 strong); the silhouette stays the same at every tier.
- **Busts.**
  - Rendered offline from `bust_blender.py`: Cv2 facets come from triangulation plus per-face brightness jitter; E toon comes from a Shader-to-RGB constant ramp with three bands, a class-colour rim and an inverted-hull ink line. Shadows are off so the hull doesn't shadow the mesh.
  - In game, a portrait is a `TextureRect` inside the CRT feed shader (RGB split, scanlines, rolling bar). The states (hurt, triumphant, flatlined) are separate renders plus shader params (dim, glitch, static).
  - Portraits get a dedicated pass later; these busts only prove the treatment.

## Scripts

- `make_all.py`: rebuilds everything in this order:
  1. slice tiles and wheels (`assets.py`, which uses the round 17 kit copied into `lib17/`);
  2. the two Blender busts;
  3. every screen;
  4. the GIF;
  5. the contact sheet.
- `r31lib.py` is the shared kit:
  - backdrops;
  - the `CRT` panel;
  - paper, stamps and tape;
  - sticker words and sticker-from-art;
  - C-C card faces;
  - firmware chip and daemon art;
  - price tags;
  - outcome chips;
  - pencil helpers.
- `sticker_lib19.py` is copied from round 21.
- One script per screen: `reward.py` (`a|b|gif`), `server_rack.py`, `event.py` (`main|memo`), `dialogue.py` (`a|b`), `netrun_map.py`, `shop.py`, `contact.py`.
- All randomness is seeded. The `scratch/` folder (tile cache, bust renders) is git-ignored and was cleared after the run.
