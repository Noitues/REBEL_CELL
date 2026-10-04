# Round 33: UI chrome (designer review of round 32)

The rules from rounds 31 and 32 still apply (`../round31_ui_chrome/NOTES.md`, `../round32_ui_chrome/NOTES.md`). Title option A is **LOCKED**.

## 1. CANCEL is yellow
- The calm slate sticker (grey ink on white vinyl) was hard to read. CANCEL now uses the yellow fill, the same one as screen-title stickers (`FILL_YELLOW` #FFEE60 → #FFB60E).
- It still carries the default focus, as the safe choice. BURN IT stays pink.
- Updated in `abandon_dialog.png` (dialog + states strip) and in the modal on `ui_kit.png`.
- **Rule:** in a two-sticker choice, yellow = the safe or back-out choice and pink = the committing verb. Grey vinyl is now used only for the *disabled* state.

## 2. Title option A: glitch DISABLE, fist OVERTHROW
See `title_screen.png` and `title_screen.gif` (960x540, 48 x 80 ms, seamless).
- **DISABLE** uses the CORRUPTED glitch language: white letters, a pink split on the left and a green split on the right, and thin pink and green scan lines.
  - The glitch stays **inside the lettering**. The die-cut is taken from the clean word, so the sticker silhouette never moves.
  - At rest the glitch is a light split.
  - In the GIF it bursts twice per loop: on frames 9-10 and on frames 27-28. Each burst shifts slices of the letters sideways for 160 ms.
- **OVERTHROW** is in a readable blue (`#84C8FF` → `#2268E8`). Its last **O is a red rebel fist** (`#E8141E`, the REBEL_CELL red): four knuckles, a thumb across the front, and a forearm with a cuff. It has the same ink keyline and extrude as the letters, so it reads as part of the word.
- **Build (`scripts/menu33.py`):**
  - `fist_word_sticker()`: any letter slot can take a pictogram with its own fill.
  - `glitch_sticker_set()`: calm and burst frames on the same die-cut.
  - In Godot, both are baked sticker textures, like every other sticker word.
  - The burst is a frame swap. The CORRUPTED glitch shader could drive it instead, masked to the letter fill; reduce effects turns the burst off.
  - Under the flash limiter, the bursts are far below 3 per second.

## 3. DISABLE → Tutorial: recommendation
- DISABLE describes doing something to an enemy. A tutorial is a safe practice run, so the word misleads a new player.
- **Recommended: SIMULATE → TUTORIAL**, with "a practice run in a simulated net" underneath. See `title_screen_alt_simulate.png`.
  - It says exactly what the tutorial is.
  - It fits the glitch treatment (a simulated net).
  - It keeps the three-step plan rhythm: BREACH / SIMULATE / OVERTHROW.
- The other verbs, ranked:
  - DRILL: short and punchy, but it can read as "drill into a server".
  - TRAIN: clear, but plain.
  - PROBE: it means scouting a target, not learning.
- To keep the word DISABLE, map it to **CAMPAIGN SLOTS** instead ("take over a saved Cell"), and move Tutorial into the MORE list.
- Note: the slogan "1. BREACH / 2. DISABLE / 3. OVERTHROW" on the typography board's pencil sample is unchanged. It is the Cell's motto, not the menu.

## 4. Courier Prime: in place
- The orchestrator fetched Courier Prime with the user's approval. I copied the files from `../round32_ui_chrome/fonts/` into `fonts/`, with no new download:
  - `CourierPrime-Regular.ttf`
  - `CourierPrime-Bold.ttf`
  - `OFL_CourierPrime.txt`: SIL OFL 1.1, (c) 2015 The Courier Prime Project Authors.
- `typography.png`, `ui_kit.png` and `abandon_dialog.png` were re-rendered.
- Corp paper now uses:
  - Courier Prime Regular for the typewriter fields;
  - Courier Prime Bold for document titles;
  - Plex Sans Condensed Medium for the letterhead.

## Files
| File | What |
|---|---|
| `abandon_dialog.png` | Yellow CANCEL (focus) + pink BURN IT, with the states strip. |
| `title_screen.png` / `.gif` | Locked option A: BREACH, glitch DISABLE, fist OVERTHROW. |
| `title_screen_alt_simulate.png` | The recommended mapping: SIMULATE → Tutorial. |
| `ui_kit.png` | The modal uses the yellow CANCEL. |
| `typography.png` | The paper row uses Courier Prime (§4). |
| `contact_sheet.jpg` | All boards on one page. |
| `scripts/` | Round 32's scripts, plus `menu33.py` (the glitch and fist stickers). `title.py` now renders A + SIMULATE instead of option B. Run `city_frames.py` first. |
| `fonts/` | Courier Prime Regular and Bold, plus its OFL licence. |
