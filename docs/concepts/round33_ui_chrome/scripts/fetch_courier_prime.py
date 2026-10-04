"""Fetch Courier Prime (SIL OFL 1.1) Regular + Bold and its licence into this round's fonts/.

Source: the Google Fonts repository (github.com/google/fonts, ofl/courierprime), the same source
assets/fonts/README.md uses for Plex. Run ONLY after the user has approved the download:
    python scripts/fetch_courier_prime.py
Then re-render: python scripts/typography.py && python scripts/ui_kit.py && python scripts/abandon.py
"""
import os
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DST = os.path.join(os.path.dirname(HERE), 'fonts')
BASE = 'https://raw.githubusercontent.com/google/fonts/main/ofl/courierprime/'
FILES = ['CourierPrime-Regular.ttf', 'CourierPrime-Bold.ttf', 'OFL.txt']

if __name__ == '__main__':
    os.makedirs(DST, exist_ok=True)
    for f in FILES:
        out = os.path.join(DST, f if f != 'OFL.txt' else 'OFL_CourierPrime.txt')
        with urllib.request.urlopen(BASE + f, timeout=30) as r:
            data = r.read()
        with open(out, 'wb') as fh:
            fh.write(data)
        print('saved', out, len(data), 'bytes')
