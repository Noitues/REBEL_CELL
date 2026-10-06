"""Rebuild every round 44 B board: python scripts/make_all.py (city_plate renders scratch/city_f00.png on first use)."""
import os
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import new_campaign, campaign_slots, stats, codex, pause, deck_viewer, options, contact_b44  # noqa: E401,E402

new_campaign.main()
campaign_slots.main()
stats.main()
codex.main()
pause.main()
deck_viewer.deck()
deck_viewer.spinner()
options.main()
contact_b44.main()
