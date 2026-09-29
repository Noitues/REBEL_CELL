# Fonts

| Font | Role (ART_BIBLE §4.1) | Licence |
|---|---|---|
| Permanent Marker | verb graffiti and handwriting (Cell voice) | Apache 2.0 (LICENSE_PermanentMarker.txt) |
| Anton | zine display, numbers | OFL 1.1 (OFL_Anton.txt) |
| Share Tech Mono | system text, net labels, logs, CRT, DISPATCH | OFL 1.1 (OFL_ShareTechMono.txt) |
| IBM Plex Sans Condensed (Regular, Medium) | body text over 3 lines (`Palette.FONT_BODY`, `UiTheme.BODY_TEXT`) | OFL 1.1 (OFL_IBMPlexSansCondensed.txt) |

Source: github.com/google/fonts (`ofl/ibmplexsanscondensed` for Plex, fetched 2026-09-28).
Confirm each licence before release (STYLE_GUIDE 3).

Every face is imported with MSDF (`multichannel_signed_distance_field=true`,
`msdf_pixel_range=16`, ART_BIBLE §4.1/§13). The `.import` files here are tracked in git
(force-added; `*.import` is ignored elsewhere) so the MSDF settings survive a fresh
checkout; `tests/unit/test_art_w1_tokens.gd` fails if any face loses MSDF.
