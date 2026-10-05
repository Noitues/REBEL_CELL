# Fonts

| Font | Role (STYLE_GUIDE 3, ART_BIBLE v2 §2.9) | Licence |
|---|---|---|
| Permanent Marker | handwriting, tags, notes (Cell voice) | Apache 2.0 (LICENSE_PermanentMarker.txt) |
| Anton | zine display, numbers | OFL 1.1 (OFL_Anton.txt) |
| Share Tech Mono | system text, net labels, logs, CRT, DISPATCH | OFL 1.1 (OFL_ShareTechMono.txt) |
| IBM Plex Sans Condensed (Regular, Medium) | body text over 3 lines and tooltips (`Palette.FONT_BODY`, `UiTheme.BODY_TEXT`); not applied to any screen yet (ART-1..12) | OFL 1.1 (OFL_IBMPlexSansCondensed.txt) |

Source: github.com/google/fonts (`ofl/ibmplexsanscondensed` for Plex, fetched 2026-09-28 on
the art-pass branch, ported in ART-0 E). Confirm each licence before release (STYLE_GUIDE 3).

ART_BIBLE v2 §2.9: every face imports as MSDF. The switch lives in each face's `.import`
file (`multichannel_signed_distance_field`, with `msdf_pixel_range=16`), tracked in git
(force-added; `*.import` is ignored elsewhere) so it survives a fresh checkout. It is OFF
until ART-1 (`Palette.FONTS_MSDF`): MSDF changes the faces' line metrics, which moves main's
multi-line text; ART-1 flips it with the layouts it moves (DECISIONS "Art direction — ART-0
tokens and VFX tiers"). `tests/unit/test_art_w1_tokens.gd` fails if a face's import and
`Palette.FONTS_MSDF` disagree.
