# Area: screens (title, menus, settings, shop, rewards, events, dialogue, campaign end, dossier, pages)

Owns: `scripts/ui/menus/`, `scripts/ui/shop/`, `scripts/ui/events/`, `scripts/ui/pages/`,
`scripts/ui/kit/` pieces the brief names, `strings.csv` lines for its screens, `test_art9_*`,
`test_art10_*`, `test_art11_*`, `test_b5_*`, `test_title_and_menus`.
Reference: ART_BIBLE v2 §screens (paper, stickers, CRT, holo), the concept exports for each page.
Rules specific here: sticker safe margin 24 px × text scale from every edge (`fx.gd`); every label
through a TextDb key (re-export after `strings.csv` changes); pad reachability for every new
control (`test_pad_reachability`); abandon/quit dialogs on `HudDialogPanel`; skins (v2 / cobalt /
graphite) must still render every changed page.
