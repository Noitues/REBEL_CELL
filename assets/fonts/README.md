# Fonts

| Font | Role (STYLE_GUIDE 3, ART_BIBLE v2 §2.9) | Licence |
|---|---|---|
| Permanent Marker | handwriting, tags, notes (Cell voice) | Apache 2.0 (LICENSE_PermanentMarker.txt) |
| Anton | zine display, numbers | OFL 1.1 (OFL_Anton.txt) |
| Share Tech Mono | system text, net labels, logs, CRT, DISPATCH | OFL 1.1 (OFL_ShareTechMono.txt) |
| IBM Plex Sans Condensed (Regular, Medium) | body text over 3 lines and tooltips (`Palette.FONT_BODY`, `UiTheme.BODY_TEXT`); not applied to any screen yet (ART-1..12) | OFL 1.1 (OFL_IBMPlexSansCondensed.txt) |

Source: github.com/google/fonts (`ofl/ibmplexsanscondensed` for Plex, fetched 2026-09-28 on
the art-pass branch, ported in ART-0 E). Confirm each licence before release (STYLE_GUIDE 3).

Every face is imported with MSDF (`multichannel_signed_distance_field=true`,
`msdf_pixel_range=16`, ART_BIBLE v2 §2.9). The `.import` files here are tracked in git
(force-added; `*.import` is ignored elsewhere) so the MSDF settings survive a fresh
checkout; `tests/unit/test_art_w1_tokens.gd` fails if any face loses MSDF.
