"""asm_glyphs: the ONE glyph library of the E10 assembly (decision Y3).  kglyph2 (cards) is the master; this module registers into it
   - the wave_rings unit masters (packet_R worm_R payload_R jammer_R ring_R) replacing kglyph2's own five unit drawings,
   - WC2_CREST (crest), WC2_BURST_B (burst), turret_a (turret), WC2_REPAIR_P (repair), and the objectives padlock (padlock),
and aliases every legacy name (KA_*, A2_CREST, WC2_*, WR_*_R, U_* ) to the master so nothing else can draw a different glyph.
mask(id) -> 512 'L' mask.  name(id) -> 'KM_<id>'."""
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
import bb_lib  # noqa
import crests15 as C15
import kglyph2 as KG
import wr2_glyphs  # noqa  registers WR_*_R/V
import wc2_glyphs  # noqa  registers WC2_*

UNIT_SRC = {'packet': 'WR_PACKET_R', 'worm': 'WR_WORM_R', 'payload': 'WR_PAYLOAD_R', 'jammer': 'WR_JAMMER_R', 'ring': 'WR_RING_R',
            'crest': 'WC2_CREST', 'burst': 'WC2_BURST_B', 'turret': 'WC2_TURRET_A', 'repair': 'WC2_REPAIR_P'}
KIND_ID = {'Packet': 'packet', 'Worm': 'worm', 'Payload': 'payload', 'Jammer': 'jammer', 'Ring': 'ring'}
NEW_IDS = ['burst', 'turret', 'repair', 'padlock']


def _norm(m):
    m = m.convert('L')
    if m.size != (512, 512):
        m = m.resize((512, 512), Image.LANCZOS)
    return m


def padlock_mask():
    """the trace_cap padlock, geometry lifted from obj2.el_cap (shackle polyline, body 11.4 x 8.6 r2, keyhole + slot knocked out), on the 512 grid (32 units per obj2 px)"""
    k = 2
    S = 512 * k
    m = Image.new('L', (S, S), 0)
    d = ImageDraw.Draw(m)
    u = 32.0 * k
    ox, oy = S / 2, S / 2 + 0.3 * u

    def T(x, y):
        return (ox + x * u, oy + y * u)
    by, bh, bw = 2.6, 8.6, 11.4
    sh = [(-3.5, by - bh / 2 + 0.4), (-3.5, by - bh / 2 - 3.0), (-1.8, by - bh / 2 - 4.7), (1.8, by - bh / 2 - 4.7), (3.5, by - bh / 2 - 3.0), (3.5, by - bh / 2 + 0.4)]
    pts = [T(*p) for p in sh]
    d.line(pts, fill=255, width=int(2.4 * u), joint='curve')
    for p in (pts[0], pts[-1]):
        d.ellipse([p[0] - 1.2 * u, p[1] - 1.2 * u, p[0] + 1.2 * u, p[1] + 1.2 * u], fill=255)
    a_, b_ = T(-bw / 2, by - bh / 2), T(bw / 2, by + bh / 2)
    d.rounded_rectangle([a_[0], a_[1], b_[0], b_[1]], radius=int(2 * u), fill=255)
    e0, e1 = T(-1.5, by - 1.9), T(1.5, by + 1.1)
    d.ellipse([e0[0], e0[1], e1[0], e1[1]], fill=0)
    a_, b_ = T(-0.7, by - 0.4), T(0.7, by + 2.6)
    d.rounded_rectangle([a_[0], a_[1], b_[0], b_[1]], radius=int(0.4 * u), fill=0)
    return m.resize((512, 512), Image.LANCZOS)


def register():
    for gid, src in UNIT_SRC.items():
        KG._cache[gid] = _norm(C15.CUSTOM[src]())
        if gid not in KG.IDS:
            KG.IDS.append(gid)
    KG._cache['padlock'] = padlock_mask()
    if 'padlock' not in KG.IDS:
        KG.IDS.append('padlock')
    KG.register()
    # legacy aliases -> master
    leg = {'trigger': 'trigger', 'brace': 'brace', 'twist': 'twist', 'hold': 'hold', 'shove': 'shove', 'spin2': 'spin2', 'spin3': 'spin3', 'nudge': 'nudge', 'spin1': 'nudge',
           'strike': 'strike', 'firewall': 'firewall', 'pull': 'pull'}
    for a, b in leg.items():
        C15.CUSTOM['KA_' + a] = (lambda b=b: KG.mask(b).copy())
    for a, b in dict(A2_CREST='crest', WC2_CREST='crest', WC2_BURST_B='burst', WC2_TURRET_A='turret', WC2_REPAIR_P='repair').items():
        C15.CUSTOM[a] = (lambda b=b: KG.mask(b).copy())
    for kind, gid in KIND_ID.items():
        C15.CUSTOM['WR_%s_R' % kind.upper()] = (lambda g=gid: KG.mask(g).copy())


register()


def mask(gid):
    return KG.mask(gid)


def name(gid):
    return 'KM_' + gid


def kind_name(kind):
    return 'KM_' + KIND_ID[kind]
