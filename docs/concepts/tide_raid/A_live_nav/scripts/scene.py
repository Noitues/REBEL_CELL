"""Scene geometry for the Live Nav frames: nodes, wire, route ribbons (lane-offset), site kinds."""
from lib import *
from ui import *

ORDER = ['known0', 'known1', 'cand0', 'cand1', 'cand2', 'hunter0', 'hunter1', 'hunter']
WID = {'known': 17, 'cand': 9, 'hunter': 9}
GHOST = hexc('C7C2E6')


class Scene:
    def __init__(self, scn='decay', geom_beat='plan_empty'):
        self.scn = scn
        d = load(scn, geom_beat)
        self.d = d
        self.nodes = node_map(d)
        self.hq = self.nodes['the_genome_core']
        self.home = self.nodes['home']
        self.sites = {s['id']: s for s in d['sites']}
        self.link_pts = []
        self.links = []
        for l in d['links']:
            if l['polyline']:
                pts, _ = clean_poly(l['polyline'], self.nodes)
                self.link_pts.append(pts)
                self.links.append((l['a'], l['b'], pts))
        beams = {b['name']: b for b in d['beams']}
        names = [n for n in ORDER if n in beams]
        polys, vis, self.meta = [], [], {}
        for n in names:
            b = beams[n]
            pts, v = clean_poly(b['polyline'], self.nodes)
            polys.append(pts)
            vis.append(v)
            self.meta[n] = b
        widths = [WID[beams[n]['role']] for n in names]
        off = lane_offsets(polys, widths)
        self.names = names
        self.rib = {}
        for n, o in zip(names, off):
            b = beams[n]
            self.rib[n] = dict(pts=o, typ=b['type'], role=b['role'], w=WID[b['role']], path=b['site_path'],
                               len=poly_len(o))
        # helpers

    def s_at(self, name, site):
        r = self.rib[name]
        node = self.nodes.get(site)
        if node is None:
            return None
        return nearest_s(r['pts'], node)

    def kind(self, sid):
        s = self.sites[sid]
        if s['tier'] == 1:
            return 'stack'
        if s['tier'] == 2:
            return 'diamond' if s['exploit'] else 'nut'
        return 'core'

    def draw_wires(self, cv):
        for pts in self.link_pts:
            wire(cv, pts)

    def draw_pins(self, cv, states, rings=None, focus=None, clocks=None, badges=None, dim=None, skip=()):
        rings = rings or {}
        clocks = clocks or {}
        badges = badges or {}
        order = sorted(self.sites, key=lambda k: self.nodes[k][1])
        for sid in order:
            if sid in skip or sid not in self.nodes:
                continue
            s = self.sites[sid]
            site_pin(cv, self.nodes[sid], s['tier'], self.kind(sid), states.get(sid, 'healthy'),
                     ring=rings.get(sid), focus=(focus == sid), clock=clocks.get(sid), badge=badges.get(sid),
                     dim=(dim or {}).get(sid, 1.0), scale=1.7)
