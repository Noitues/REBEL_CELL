# Round 31: UI chrome (menus, HUD, panels, buttons, tooltips, type)

This is the first concept pass for backlog item "Menus and UI chrome" (DIRECTION_REVIEW §9). It applies the locked overlay rules: each medium has one job.

| Medium | Job | Never |
|---|---|---|
| **Vinyl sticker** (Anton keyline, white die-cut) | Things that never change: screen titles (THE GRID, OPTIONS), the one primary verb per screen (CONTINUE, JACK IN, BURN IT), card names, node types, operative name plates. | A value that changes. Two sticker verbs competing on one screen. |
| **Terminal** (CRT glass, Share Tech Mono) | The Cell's own systems: menus, resources, Heat, crew, map key, tooltips, toggles, toasts, forecasts (IF CLEARED), the raid alert, Speed/Skip. | Paper or corp intel. |
| **Paper** (typewriter + letterhead + stamps) | Intercepted corp documents: work orders, after-action reports, audit dossiers. | The Cell's own UI. |
| **Holo** (corp tint, scan bands, RGB edge, seal) | Decrypted corp intel: the selected Site's file, threat intel, intercepted corp broadcasts (news toasts). | Anything the Cell owns. |
| **Grease pencil** (opaque wax, dark under-shadow) | Plans and annotations that are true to the rules. Yellow = our plan / valid; red = threat / invalid / loss. Dashed = what-if (forecast route). Slogans (NEVER SLEEP, the plan note). | Jokes that misstate the game state. Live numbers. Body text. |
| **Bare Anton** (no vinyl; 2 px dark rim + own-colour glow) | Live big numbers: HP, Heat value, damage. | — |

**Focus** is the same everywhere: lime `#D4FF00` corner brackets, 3 px wide, 7 px outside the element. A focused sticker gets a lime die-cut halo instead. A focused menu line also gets a `>` caret. Lime is therefore never used as an ON or selected colour in chrome (ON and selected are cyan fills plus a word).

## Files
| File | What |
|---|---|
| `typography.png` | The type system: one row per medium, with the face, true 1080p sizes, floors, tracking, usage rules and licences. |
| `ui_kit.png` | The chrome kit. Buttons: sticker primary and terminal secondary, each in idle / hover / pressed / disabled / focus. Panels per medium. A terminal tooltip with round 17 glyph rows. Toggles, sliders and tabs. A modal confirm. Toasts (plain / refusal / corp news). Keyboard and pad focus. The 9-slice sticker plate. |
| `title_screen.png` | Title / main menu over the living night city: the REBEL_CELL neon tube sign on a circuit-board backing, a CONTINUE sticker (default focus) with a terminal slot summary, the terminal MAIN menu, PROFILE stats, the version line, pad prompts, a pirate-radio ticker, and NEVER SLEEP + the plan note in grease pencil. |
| `title_screen.gif` | A 960x540 idle loop, 48 frames x 80 ms, seamless, about 1.8 MB. It shows the round 26 v4 city traffic, the `_` cursor blinking (0.96 s period), one E stutter, a two-frame drop to "CELL" only (the takeover echo), a slow gloss sweep over CONTINUE, and the ticker. |
| `city_map_hud.png` | The City Grid HUD over `round30_meridian_castle/city_night_hq_v6.jpg`. It has the THE GRID title sticker, a terminal resource strip (Schematics, Exploits x/3, Sites, Armory, Runs), the Heat meter, the crew roster, the map key, the selected Site as a decrypted Halcyon holo, a terminal IF CLEARED forecast, the RAID PENDING alert with RAID SETUP, PREV/NEXT/BACK, the runner chip and the JACK IN sticker. A yellow pencil plan (circle + arrow) and a red dashed raid forecast sit on the map. |
| `settings_menu.png` | Options > Accessibility, over a paused combat. It shows every switch from `settings_panel.gd`, including **HEAT GLITCH** with the round 18 ON/OFF preview and the "LIMITED" chip that appears while the flash limiter or reduce effects is on. It also shows the text-scale slider with a live sample, colour-blind tiles, resolve speed tiles, Reset, and pad prompts. |
| `contact_sheet.jpg` | All boards on one page. |
| `scripts/` | See "Scripts" below. |

## Type system (summary of `typography.png`)
Sizes are 1080p pixels: the UiTheme step at 1280x720 multiplied by 1.5. They are then multiplied by the Settings text scale (1.0 / 1.3 / 1.6). Stickers scale as whole objects.

| Role | Face | Sizes (1080p) | Floor | Licence |
|---|---|---|---|---|
| Sticker / display | Anton Regular, 5 px ink keyline, 7 px extrude, 12 px die-cut | 144 verbs, 96 titles, 66 stamps, 45 values | 36 (sticker word), 30 (bare number) | OFL 1.1, in repo |
| Terminal | Share Tech Mono | 33 / 27 / 22 / 18; CAPS +8 % tracking | 18 | OFL 1.1, in repo |
| Paper | Courier New (fields) + Bahnschrift Bold / Bold Condensed (letterhead, titles) | 30 letterhead, 34 title, 20 fields, 15 meta | 20 for anything read | **Windows system fonts: concept only, not redistributable.** Ship with Courier Prime (OFL, not in repo yet: fetch it) and IBM Plex Sans Condensed Medium (in repo) for letterheads. |
| Grease pencil | Permanent Marker, rendered as wax | 48 / 34 / 28 | 26 | Apache 2.0, in repo |
| Body / tooltip | IBM Plex Sans Condensed Regular + Medium | 22 body, 20 small, line 1.4, 36-60 characters a line | 20 | OFL 1.1, in repo |

## Rules per screen
- **One sticker verb per screen.** Title: CONTINUE. Grid: JACK IN. Confirm: BURN IT. Everything else on the screen is a terminal chip. The screen title is also a sticker, in yellow, so it never competes with the pink verb.
- **Live values are never stickers.** HP, Heat, resources and forecasts are terminal text or bare Anton.
- **Heat meter (map):** a terminal gauge with the 25/50/75 thresholds and the four band words (COOL cyan, NOTICED amber, FLAGGED orange, HUNTED red). The band word is always printed, never colour alone. The live modifier ("while >= 50: enemies +1 resistance") and the next thresholds sit inside the panel. The HQ keeps its WANTED poster (art_asset H).
- **Site file = holo; IF CLEARED = terminal.** The corp's own data is decrypted intel. The gains are the Cell's computation. Every number follows the GDD: T2 rack +17 Schematics, Heat +3 rack +10 exploit, and raid retaliation for an Exploit extracted at Heat 50+.
- **Pencil on the map** is a plan only: the circle on the chosen Site and the arrow from the Cell's nearest node. The forecast raid route is red and **dashed** (the locked path rule: dashed = what-if).
- **Tooltips:** a terminal header with the name, the value and a type tag in the type's colour. Each row has a glyph tile (round 17 glyphs, 26 px) and Plex 20 text. Keywords are Plex Medium in their colour. A key-hint row closes the tooltip. Delay 350 ms.
- **Toasts:** plain = cyan terminal; refusal = HARM edge + no-entry mark; corp news = holo strip. They sit at the foot of the screen for 2.4 s.
- **Disabled** keeps its words legible: terminal = grey edge + hatch; sticker = greyscale vinyl at 80 % + a RESOLVING chip.

## Building it in Godot 4.7
**Theme (extend `UiTheme.build()`).** Add type variations instead of per-node overrides:
- `TerminalPanel`: PanelContainer, StyleBoxFlat. Background `rgba(5,13,28,0.92)`, border 2 px `#5CE1FF` at 80 %, `corner_detail` 1. The chamfer is either a StyleBoxTexture with a 16 px cut corner (NinePatch margins 18) or a small custom StyleBox drawing the polygon (see `style_box_brackets.gd` for the pattern). The header strip is a child HBox: the `> TITLE` Label (mono CAPS, 18 px at 1080p) + a tag Label with a 1 px StyleBoxFlat border.
- `TerminalButton`: Button. The `normal` / `hover` / `pressed` / `disabled` / `focus` StyleBoxes follow `ui_kit.png`. `focus` = the existing **StyleBoxBrackets** in lime (draws outside the rect, grow 7 px). Hover adds the `>` caret through `text` or `icon`; there is no colour-only cue.
- `HoloPanel`: PanelContainer with a ShaderMaterial (below). `PaperPanel`: a NinePatchRect paper texture (margins 24) + a Label stack with the paper fonts.
- Fonts: the four repo faces are already MSDF imports (`assets/fonts/README.md`). Tracking is a `FontVariation` with `spacing_glyph` (+8 % CAPS mono = +2 px at 27 px). Text scale stays on `UiTheme.font_px()`.

**Sticker words.** Bake every sticker word (title, verb, name plate) offline with this round's `sticker_lib31.py` into a per-locale atlas at 2x: keyline + extrude + die-cut + rest gloss. They never change at runtime, so baking costs nothing and keeps the hand-cut look. At runtime a `TextureButton` (or the existing `StickerButton`, re-skinned from taped paper to vinyl) plays the states:
- hover: scale 1.05, shadow offset (26, 34) blur 22, gloss sweep;
- pressed: scale (1.04, 0.90), shadow snaps to (2, 3);
- disabled: CanvasItem `modulate` greyscale shader at 80 %;
- focus: a pre-baked lime halo sprite (die-cut dilated 4-9 px) toggled on `focus_entered`.

The **gloss** is the existing `foil.gdshader` pattern: one diagonal band uniform (`gloss_pos`), with 0.22 at rest and a 1.2 s sweep every 6-10 s, one sticker at a time.

**Name plates (9-slice).** Use a `NinePatchRect` with the vinyl plate texture authored at 2x (182x78 at 1x in the board, `patch_margin_*` = 30 at 1x), `axis_stretch` = STRETCH. The words are a Label child (Anton, ink `#141016`). Corners never stretch, so the die-cut radius stays true at every width.

**Shaders** (each effect is a uniform, so `rc_common` reduce-effects can zero it):
- `crt_panel.gdshader` (exists): add a scrolling hex-dump texture at 6 % alpha (scroll 4 px/s), an edge glow from an SDF of the panel rect, and keep the 3 px scanlines at 10 %. Flicker stops under reduce effects; the static scanlines stay.
- `holo_panel.gdshader` (new): corp tint at 78 %, 4 px scan lines, 3-4 bright bands drifting down (period 3-5 s), and a +/-2 px RGB split on the edge only. Reduce effects: no bands, no split.
- Grease pencil: `marker_stroke.gdshader` (exists) on a `Line2D` with a wax-grain texture. A duplicate Line2D offset (2, 3) in `#060308` at 85 % acts as the under-shadow. Dashed forecast = `texture_mode` TILE with a dash texture.
- Live numbers: a `LabelSettings` with Anton, outline 2 px `#06060A`, and shadow `size` 10 in the number's own colour at 50 % (the glow).
- Title tilt-shift: two passes of the existing `glass_blur.gdshader` masked by a vertical band (sharp at 56 % height). Reduce motion keeps it; it is static.

**Title sign.** Bake the REBEL_CELL Anton outline tubes into one texture. Each letter's mask goes in its own colour channel or a small atlas, and a shader takes `uniform float lit[10]`. A tiny script drives the states: cursor blink 0.48 s on / 0.48 s off, an E stutter every ~8 s, and the drop to "CELL" every ~20 s, lasting 160 ms. The pink street spill is an additive Sprite2D with modulate = the mean of `lit`.
- Under the flash limiter, the drop and the stutter count as flashes (at most 3 per second; they are far below that).
- Under reduce effects, the stutter and the drop stop and the cursor blink stays.

**Ticker:** a Label inside a clipping Control, moving at 120 px/s at 1080p. The GIF uses a short repeating line, so its loop is exact.

**Existing kit classes to re-skin** (no new mechanics): `UiTheme`, `TerminalWindow`, `StickerButton`, `ZineToggle` → terminal pill, `ZineSlider` → terminal slider, `TilePicker`, `Toast`, `FocusTip`, `ConfirmDialog`, `SettingsPanel`, `PadGlyph`, `HudStats`, `MapLegend`. The existing StickerButton (taped paper note + marker) is superseded for primary verbs by the vinyl sticker. Combat's RESPIN/UNDO were already terminal chips in the locked combat HUD.

## Open questions for the designer
1. **Paper faces:** OK to fetch Courier Prime (OFL) as the shipping typewriter face? The concept uses Courier New / Bahnschrift, which are Windows-only and can't be shipped.
2. **Title backdrop spoiler:** the night map shows the REBEL_CELL red fist (as on the map, by the round 28 decision). Keep it on the title, or reframe the title crop away from it?
3. **Heat on the map** is a terminal gauge. The HQ keeps the WANTED poster. Should the map also get a small poster?
4. **Profile stats on the title:** keep the panel, or move it into Stats & achievements?
5. **Assist mode wording:** the board avoids numbers, because Settings fills them from config.

## Scripts
Run every script from this folder: `python scripts/<name>.py`.

**Board scripts:**
- `typography.py`
- `ui_kit.py`
- `title.py` (pass `nogif` for the PNG only)
- `city_hud.py`
- `settings.py`
- `contact.py`

**Shared code:**
- `ui31.py`: the medium helpers (terminal panel, button, toggle, slider, tabs, focus brackets, holo, corp seal, paper, rubber stamp, grease pencil, live numbers).
- `sticker_lib31.py`: a copy of round 21's `sticker_lib19.py`.

**City backdrop:**
- `city_frames.py` renders round 26's v4 night motion at 1920x1080 without labels into `scratch/city/`.
- It uses this round's copies of round 26's `cm.py`, `roads.py`, `fx.py` and `bases.py`. The only change is in `bases.py`: the baked map labels are patched out with clones of the city a few blocks away.
- Run it before the boards.

**Utilities:**
- `inspect_gif.py`
- `clean_scratch.py`: removes this round's own `scratch/` only.

All randomness is seeded. Each script writes its board to this folder.
