# Pause menu as stickers: three layouts (mockups, no game code)

Designer follow-up 2026-10-05: every pause choice is a sticker; find a cleaner layout. Each mockup is 1280x720 over a
real capture of the HQ and of a fight (blurred 6 px and dimmed with the SCRIM, as `GlassScrim` does). Every sticker is
baked by the round 33 kit code itself (`ui31.sticker` for the word, `ui31.focus_sticker` for the lime halo, placed by
`sticker_lib31.place`, as `tools/art/bake_menus_r33.py` does; `mock_pause_layouts.py` imports that script's
`point_fonts`). Nothing is redrawn. The panel, code field and copy button are Pillow approximations of the game's own
(the real ones are `CrtWindow` and `CodeField`).

Colour roles (v2): **RESUME** = `FILL_PINK`, the one primary. **OPTIONS, CODEX, SAVE & QUIT, QUIT TO DESKTOP** =
`FILL_CALM` (round 32's calm sticker for safe choices; quit is not destructive, so it is calm too).
**ABANDON RUN** (in a run) and **ABANDON CAMPAIGN** (at HQ) = harm: the kit's fill tuple with ui31's HARM red
(255,68,51) as its dark end, set under a HARM rule and a `CANNOT UNDO` chip like the abandon concept's. This red
sticker fill is the one thing the kit does not have baked yet (the concept's BURN IT is pink); the alternative is pink
with the HARM rule and chip only, if the designer wants pink to stay "the committing verb". The key hint `[Esc]` is
mono text beside Resume (it is not part of the sticker). The sticker words are translated and baked per language by
the game, as the title's are.

Files: `opt<A|B|C>_<hq|fight>.png` (focus on one sticker in each: A on RESUME, B on OPTIONS, C on CODEX),
`optB_grid_<hq|fight>_text2.0.png` (the favourite at text scale 2.0; stickers grow with the text up to 1.5x, as
`VerbSticker.SCALE_MAX`, the code field and caption grow fully).

| Option | Layout | For | Against |
|---|---|---|---|
| A stack | one left-aligned column: Resume, the four calm stickers, a red rule, CANNOT UNDO, the abandon sticker, the code field | the simplest reading order and focus order (Up/Down through one list); narrowest panel (560 px) | tall (440 px, 640 px at 2.0: nearly the screen), the right half of the panel is empty |
| B grid | Resume across the top; a 2 x 2 block (Options / Quit to desktop, Codex / Save & quit); the harm strip at the foot with the abandon sticker on the left and the code field beside it | the harm verb is set apart at the foot, far from Resume; the code sits on the same line as it; short (330 px), centred, fills its width; at 2.0 it stays on the screen (560 px) | pad focus is 2-D (Left/Right too); two columns need the stickers' widths balanced |
| C dock | Resume big on the left with the code field under it; the other stickers as a column on the right, the harm verb at its foot | Resume is the unmistakable landing point and the code is its own corner | widest (740 px, 1040 at 2.0), a hole under Resume, the longest focus path from Resume to the abandon sticker |

**Pick: B, the grid.** It is the cleanest: three bands that read top to bottom (go on, the everyday choices, the
dangerous one with its own code), the destructive sticker apart from Resume and from quit, the least height at every
text scale, and the code field gets a full row instead of a corner. Focus order for the build: Resume, Options, Codex,
Save & quit, Quit to desktop, Abandon, then the copy button (Left/Right moves across a row of the grid, Up/Down between
rows). Where the abandon rows do not exist (no campaign: the title's pause, the tutorial), the strip holds the code
alone, or nothing, and the panel shrinks.

Open points for the designer: (1) red harm fill vs pink with the red rule and chip; (2) is `[Esc]` beside Resume
enough, or on the sticker itself like the title's key hints.
