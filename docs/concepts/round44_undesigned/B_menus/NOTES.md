# Round 44 B: menu screens the concept pass never designed

These are the art director's suggested approach (INTEGRATION_REVIEW `REVIEW.md` section f, plus c, D11, D13, D21 and D22) for the menu screens that the M14 integration built without a concept. Each render is 1920x1080. `contact_B.jpg` puts each render beside the build capture it replaces.

## Designer rulings applied (round 44 brief change; these override REVIEW section f)
1. **Pause:** the build's all-sticker pause menu stays. Every option is a sticker and D13 is not applied. RESUME has the default focus. The abandon confirm is as briefed.
2. **Slots:** every folder has a LOAD and a DELETE sticker. Each DELETE carries the red grease-pencil CAN'T UNDO.
3. **Sticker focus:** focus and hover show only the peel-back (corner curl). The rainbow gloss sweep runs on a scheduler, one sticker at a time. Each board shows at most one sticker mid-sweep. Focused stickers show the curl and no lime halo. Terminal rows keep the lime brackets and the `>` caret, because lime still means focus only.
4. **RESET TO DEFAULTS resets every tab** (Q12). It is a terminal button labelled RESET ALL TABS, never a sticker.

## Files
| File | What it shows |
|---|---|
| `new_campaign.png` | **Media:** one terminal panel over the dimmed title city. NEW CAMPAIGN is the yellow title sticker. TRUST NO ONE is a small white-vinyl sticker slogan; it was pencil in the build, but it is a motto, not a plan. START is the one sticker verb (pink); it shows the focus curl and carries the sweep.<br>**Tiles:** target, ICE stepper, home server and crew tiles. A selected tile has a 3 px cyan edge plus a SELECTED word tab; it is never filled. The pad focus shows lime brackets (on Solace). Each corp tile shows its crest on a small **holo** chip (corp tint, 4 px scan lines, an RGB-split edge). Locked tiles are hatched and show a lock with the cost. Crew tiles use the build's busts, greyed when locked.<br>**Right column:** TODAY'S RUN and SHARE CODES as terminal rows, plus the city seed row. |
| `campaign_slots.png` | **Folders:** three manila case files. They are the Cell's own files, so each tab carries a **terminal tab-clip label** (a small CRT label holder reading "SLOT 1 // CELL-03"). The fields are printed in Share Tech Mono (the Cell's printer, not Courier). Each folder has the Cell's red hex-and-fist rubber stamp ("ACTIVE // REBEL_CELL // OWN FILE") and crew polaroids. No corp letterhead.<br>**Verbs:** LOAD (pink) and DELETE (neutral white vinyl) on every folder, each DELETE with the red pencil CAN'T UNDO (ruling 2). The focused slot is straight and lifted, and its LOAD shows the curl and the sweep. |
| `stats.png` | **Stat tiles:** terminal tiles, each with a glyph, a bare Anton live number and a mono label. The numbers match the title's PROFILE panel.<br>**Achievements:** die-cut sticker badges on a white liner strip (#F7F7F2). Earned badges are glossy vinyl; unearned ones are an empty kiss-cut outline in the liner. The focused empty badge shows lime brackets and a terminal tip with its condition. THE WALL carries the sweep.<br>**Run history:** terminal log rows (date, crest and target, run, operative, cycles, banked, outcome). Only COMPLETED and FLATLINED get a small Anton outcome sticker; JACKED OUT and ABANDONED stay mono words. |
| `codex.png` | **Panel:** terminal glass, `> CODEX // WHAT THE CELL KNOWS`, with the build's tab plates in two rows (CORPORATIONS active).<br>**Entries:** glyph-tile rows (a 26 px glyph in a navy tile, then Plex text), the corps first and then the corp rules. Halcyon Civic is selected (cyan wash, brackets, caret).<br>**Holo card:** the selected entry opens an intercepted **holo** card: crest with glow, the house rule, BOSSES ON FILE as glyph rows (The Civic Core / Emergency Powers, City Manager, Zoning Board, Riot Control, from `content/enemies`) and a DECRYPTED chip. No paper. |
| `pause.png` | **Stickers (ruling 1):** every option is a sticker. Colour carries a role: RESUME is yellow (safe, default focus, curl plus sweep), ABANDON RUN is pink (destructive), and OPTIONS, CODEX and the two QUITs are neutral white vinyl, so the old pink/cyan QUIT pair is gone. Size carries the hierarchy: RESUME is big and the rest are plates.<br>**Text:** each option's consequence is a mono line under it, and the pencil captions ("No going back", "Come back soon") are removed. One terminal panel holds the run line, the campaign code row with COPY, and pad hints. |
| `pause_abandon.png` | The round 33 abandon dialog as built, over the dimmed pause: terminal body, yellow CANCEL (default focus, shown with the curl only) and pink BURN IT. No sweep on this board, which keeps the destructive choice calm. |
| `deck_viewer.png` | **Window:** the LOADOUT terminal window, DECK tab.<br>**Sheet:** the hand's own C-C card faces (round 34 `r31lib.card_sticker`, the face the build exports) are stuck on the white liner sheet #F7F7F2 in kiss-cut slots. The focused card is peeled up (curl plus sweep), and its empty kiss-cut slot shows beneath.<br>**Detail column:** the card detail sits in the same terminal. It shows the name plate, then notes as tooltip glyph rows, then a RAM curve. |
| `deck_viewer_spinner.png` | **Wheel:** the SPINNER tab shows the locked D4 player wheel, cropped unchanged from round 41 `combat_typical_v4.png`. It is at combat size (slice radius about 220) on a dimmed pool of the city that the window opens onto.<br>**Rows:** the slices as glyph rows in the round 34 names, plus the firmware and hub rows. |
| `options.png` | Round 31 options as built, opened from the title (TITLE // OPTIONS). The only change is the footer: RESET ALL TABS as a terminal button, with "every tab back to its defaults", CLOSE and the pad hints ("Y reset all"). |
| `contact_B.jpg` | Each render beside the build capture it replaces: build on the left, concept on the right, labelled. There is no build capture of the SPINNER tab, so that cell says so. END dossiers are kept as they are, with no render. |
| `scripts/` | `make_all.py` rebuilds everything (about 40 s). `b44.py` holds the shared helpers. There is one script per board, plus `contact_b44.py` and `city_plate.py`. |

## Decisions
- **Backdrop.** Every board except the pause pair uses the title's lit night city, the round 33 locked title backdrop. `city_plate.py` re-renders it through round 33's `cm.py` / `roads.py`, without labels. It is then blurred 5 px, dimmed to 56 % and vignetted, with a soft scrim pool under the panel.
  - **Pause and abandon** sit over the paused fight (`combat_typical_v4`, dimmed to 34 %) instead, because the pause menu is drawn over the screen it pauses. This follows the round 33 abandon dialog. If the designer wants the city behind the pause too, change one line in `pause.py`.
  - The ON AIR ticker is not shown on these pages (D20).
- **Cohesion.** Each page has one terminal panel, the world dimmed behind it, and at most one sweep. Pages have no paper document; the slot folders are the Cell's own objects, not corp paper.
  - **Sticker counts.** The pages that keep several stickers (pause, slots) do so by the designer's rulings. On other pages the extra stickers are titles or fixed name plates, not competing verbs.
- **Neutral sticker colour.** A new fill, `FILL_WHITE` in `b44.py`, is white vinyl lettering with the ink keyline. It is used for stickers that are not the page's verb (pause secondaries, DELETE, the slogan).
  - The ink fill was tried and rejected: black letters on the black keyline did not read.
  - Grey stays reserved for *disabled* (round 33 rule).
- **Sweep look.** The scheduled sweep is drawn as a narrow diagonal band whose hue runs through the spectrum across its width, with a white core, clipped to the die-cut. In Godot this is the existing `foil.gdshader` `gloss_pos` band with a hue ramp across it.
- **Curl size.** The focus curl is a fixed fold of about 34 px at 1080p (24 px on short words such as CANCEL and START), not a fraction of the sticker. A fractional fold either vanished on short words or ate letters on long ones.
- **Text floor.** All text is 12 px or larger at 1080p. The stamp micro-line is about 12.6 px, and the card body text is the exported face's own 13 px at 1:1. Decorative hex-dump characters inside the CRT glass are texture, not text.
- **Randomness.** Every random value is seeded: paper grain, stamp ink, folder tilt, pencil and hex dump.

## Reused, never redrawn
- Round 33 `ui31.py` and `sticker_lib31.py` (panels, tabs, toggles, sliders, stickers, pencil, holo), `settings.py` (`tiles`), and `cm.py` / `roads.py` (city).
- Round 34 `r31lib.card_sticker` (card faces).
- Round 41 `combat_typical_v4.png` (the D4 wheel and the pause backdrop).
- Round 18 `heat_glitch_storyboard.png` (the options preview).
- The build's own exports, read only from `D:/Godot/rebel_cell/assets`: `wheel/glyphs_interim/crest_*.png`, `glyphs/masters/*.png` and `portraits/busts_*.png`.
- All of these are imported in place with `sys.dont_write_bytecode`, so nothing is written into earlier rounds.

## Could not do / open
- **Wheel rim wording.** The cropped wheel's rim telemetry still reads the pre-round-34 word "ZERO-DAY". That text is baked into the locked render. The slice list beside it uses the round 34 names (OVERFLOW, SHIM, DEFRAG, DETOUR, INFECT).
- **Spinner tab has no build capture.** That contact cell is a placeholder.
- **OVERVOLT's rule** in the spinner firmware row is left as "hover the socket for its rule". I did not invent a number.
- **Holo font.** The holo card title uses Bahnschrift, which is what the round 31 kit's `holo_panel` uses. It is a Windows system font and is concept only; ship with Plex Condensed.
