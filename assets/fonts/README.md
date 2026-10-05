# Fonts

One face per medium (ART_BIBLE v2 §2.9, `docs/art_reference/menus/round33_ui_chrome/typography.jpg`).

| Font | Medium and role (ART_BIBLE v2 §2.9) | Palette | Licence |
|---|---|---|---|
| Anton Regular | Sticker / display: verbs, screen titles, stamps, the Cell's own lettering on its fixed objects; bare Anton for live numbers (HP, Heat, damage; `UiTheme.live_number`) | `FONT_DISPLAY`, `display()`, `marker()` | SIL OFL 1.1 (`OFL_Anton.txt`) |
| Share Tech Mono Regular | Terminal (CRT): panels, menus, HUD numbers, logs, key hints, DISPATCH; CAPS tracked +8 %; the bits' 0/1 | `FONT_MONO`, `mono()` | SIL OFL 1.1 (`OFL_ShareTechMono.txt`) |
| IBM Plex Sans Condensed Regular + Medium | Body / tooltip prose (over 3 lines), corp letterheads (Medium) | `FONT_BODY(_MEDIUM)`, `body()`, `body_medium()`, `UiTheme.BODY_TEXT` | SIL OFL 1.1 (`OFL_IBMPlexSansCondensed.txt`) |
| Courier Prime Regular + Bold | Corp paper: typewriter fields (Regular), document titles (Bold) | `FONT_PAPER(_BOLD)`, `paper()`, `paper_bold()` | SIL OFL 1.1 (`OFL_CourierPrime.txt`) |
| Permanent Marker Regular | Grease pencil only (plans and threats, rendered as wax); never body text, numbers or UI chrome | `FONT_PENCIL`, `pencil()` | Apache 2.0 (`LICENSE_PermanentMarker.txt`) |

Sources: github.com/google/fonts (`ofl/ibmplexsanscondensed` for Plex, fetched 2026-09-28 on
the art-pass branch, ported in ART-0 E); Courier Prime from github.com/quoteunquoteapps/CourierPrime
(fetched for round 33 into `docs/concepts/round33_ui_chrome/fonts/`, kept in
`docs/art_reference/fonts/`, copied here in ART-1 1A). Confirm each licence before release
(STYLE_GUIDE 3). Consolas and Courier New are concept-only and never ship.

**MSDF on (ART-1 1A).** Every face imports as MSDF (`multichannel_signed_distance_field=true`,
`msdf_pixel_range=16`) and `Palette.FONTS_MSDF` is true. The switch lives in each face's
`.import` file, tracked in git (force-added; `*.import` is ignored elsewhere) so it survives a
fresh checkout. `tests/unit/test_art_w1_tokens.gd` fails if a face's import and
`Palette.FONTS_MSDF` disagree. MSDF faces report fractional line heights
(`Font.get_height`); code that sizes or pages text by whole lines measures with
`UiTheme.line_px`, the height the text server lays a line at.
