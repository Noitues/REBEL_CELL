"""06 icons: 9 slice types and 4 statuses on a 64 px grid, each also shown at 24 px."""
from kit import *
from icons import slice_icon, status_icon, STATUS

SLICES = ['ATTACK', 'CRITICAL', 'DEFEND', 'SHIELD', 'EVADE', 'HEAL', 'AFFLICT', 'DEPLOY', 'MISS']
STATS = ['CORRUPTED', 'OVERCLOCKED', 'ENCRYPTED', 'PARASITE']


def cell(d, cx, cy, seed):
    """A faint 64 px grid cell behind each icon."""
    q = [(cx - 40, cy - 40), (cx + 40, cy - 40), (cx + 40, cy + 40), (cx - 40, cy + 40)]
    quad_fill(d, q, DARK, 1, seed, 2, 2, var=0.02)


def render():
    img = sheet()
    d = ImageDraw.Draw(img)
    labels = []
    text(d, 120, 170, 'SLICE TYPES', 22, LABEL, anchor='lm')
    for k, name in enumerate(SLICES):
        cx = 170 + k * 198
        cell(d, cx, 300, ('c', name))
        slice_icon(d, name, cx, 300, 64)
        slice_icon(d, name, cx + 74, 320, 24)
        labels += [(cx + 20, 380, name)]
    text(d, 120, 520, 'STATUSES', 22, LABEL, anchor='lm')
    for k, name in enumerate(STATS):
        cx = 300 + k * 420
        cell(d, cx, 660, ('s', name))
        status_icon(d, name, cx, 660, 64)
        status_icon(d, name, cx + 78, 680, 24)
        labels += [(cx + 20, 744, name), (cx + 20, 772, 'helps you' if STATUS[name] else 'hurts you')]
    # larger reference row so the facets read
    text(d, 120, 870, 'AT 2x', 22, LABEL, anchor='lm')
    for k, name in enumerate(SLICES[:5] + STATS[:2] + ['DEPLOY', 'MISS']):
        cx = 300 + k * 182
        if name in STATUS:
            status_icon(d, name, cx, 960, 128)
        else:
            slice_icon(d, name, cx, 960, 128)
    return finish(img, '06_icons.png', labels, '06', 'ICONS  //  SLICE TYPES + STATUSES  (64 px + 24 px)')


if __name__ == '__main__':
    render()
