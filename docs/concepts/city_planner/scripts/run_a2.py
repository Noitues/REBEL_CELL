"""Build A2: map + legend panel + city_A2.json. Usage: python scripts/run_a2.py"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

import numpy as np

import design_a2 as A2
from geom import cum, plen, resample
from panel import compose, make_panel

OUT = os.path.join(os.path.dirname(__file__), '..')
U2M = A2.U2M
ORIGIN_U = 500.0

CLASS_WIDTH_M = {'ring': 40.0, 'motorway': 34.0, 'truck': 28.0, 'arterial': 20.0, 'collector': 12.0}
RAIL_GAUGE_M = {'freight': 12.0, 'commuter': 10.0, 'metro': 8.0}


def MP(p):
    return [round((p[0] - ORIGIN_U) * U2M, 1), round((ORIGIN_U - p[1]) * U2M, 1)]


def MPL(pl, step=None):
    pts = resample(list(pl), step) if step else list(pl)
    return [MP(p) for p in pts]


def bearing_deg(theta_screen):
    dx, dy_north = math.cos(theta_screen), -math.sin(theta_screen)
    return round(math.degrees(math.atan2(dx, dy_north)) % 360.0, 1)


def slug(s):
    out = ''.join(ch.lower() if ch.isalnum() else '_' for ch in s)
    while '__' in out:
        out = out.replace('__', '_')
    return out.strip('_')


def export(m):
    ex = m.layout_extra
    C = ex['C']
    names = {'centre': 'The Old City (Rebel Cell)', 'halcyon': 'Halcyon', 'solace': 'Solace', 'orbital': 'Orbital',
             'meridian': 'Meridian', 'aurelian': 'Aurelian Concord', 'tethys': 'Tethys Deep'}
    hq_by = {d['district']: d for d in A2.LM if d['kind'] == 'hq'}
    gates_by = {}
    for g in A2.CHECKPOINTS:
        gates_by.setdefault(g['district'], []).append(MP(g['pos']))
    walls = {w['name']: w for w in m.walls}
    districts = []
    cents = {}
    for key in ('centre', 'halcyon', 'solace', 'orbital', 'meridian', 'aurelian', 'tethys'):
        a = m.mnp(m.z[key]['mask'])
        ys, xs = np.nonzero(a)
        cen = (float(xs.mean()), float(ys.mean()))
        cents[key] = cen
        d = dict(id=key, name=names[key], colour_rgb=list(m.z[key]['color']), polygon=MPL(m.z[key]['poly'], 6.0),
                 centre=MP(cen), area_km2=round(float(a.sum()) * (U2M / 1000.0) ** 2, 2))
        if key in hq_by:
            d['hq'] = hq_by[key]['name']
            d['hq_position'] = MP(hq_by[key]['pos'])
        if key in walls:
            d['wall'] = MPL(walls[key]['pts'])
            d['gates'] = gates_by.get(key, [])
        d['distance_from_old_city_m'] = round(math.hypot(cen[0] - cents.get('centre', cen)[0], cen[1] - cents.get('centre', cen)[1]) * U2M, 0) if key != 'centre' else 0.0
        districts.append(d)
    dists = [d['distance_from_old_city_m'] for d in districts if d['id'] != 'centre']
    ratio = round(max(dists) / min(dists), 2)

    landmarks = []
    for l in A2.LM:
        e = dict(l)
        e['pos'] = MP(l['pos'])
        landmarks.append(e)

    roads = []
    for i, r in enumerate(m.roads):
        segs = m._split(r['pts'], r['tunnels'])
        roads.append(dict(id='road_%03d' % i, name=r['name'], class_=r['cls'], width_m=CLASS_WIDTH_M[r['cls']],
                          closed=bool(r['closed']), polyline=MPL(r['pts'], 4.0),
                          tunnels=[MPL(s, 4.0) for s, t in segs if t], bridges=[MPL(b, 4.0) for b in r['bridges']]))
    for r in roads:
        r['class'] = r.pop('class_')
    inter = []
    for i, f in enumerate(m.interchanges):
        inter.append(dict(id='ix_%02d' % i, type=f['type'], position=MP(f['pos']), roads=list(f['roads']),
                          ramps=[MPL(rp, 2.0) for rp in f['ramps']]))
    rails = []
    for i, r in enumerate(m.rails):
        segs = m._split(r['pts'], r['tunnels'])
        rails.append(dict(id='rail_%03d' % i, name=r['name'], kind=r['kind'], gauge_m=RAIL_GAUGE_M[r['kind']],
                          closed=bool(r['closed']), polyline=MPL(r['pts'], 4.0), tunnels=[MPL(s, 4.0) for s, t in segs if t]))
    stations = []
    for i, s in enumerate(m.station_list):
        stations.append(dict(id='st_%03d' % i, name=s['name'], kind=s['kind'], position=MP(s['pos']), lines=s['lines']))

    feats = {}
    for f in m.features:
        feats.setdefault(f['kind'], []).append(dict(name=f['name'], polygon=MPL(f['poly'], 4.0)))
    markets = [dict(name=l['name'], position=MP(l['pos'])) for l in A2.LM if l['kind'] == 'glyph:market']

    pier_specs = [(668, 672, 55, 8, math.pi), (668, 704, 55, 8, math.pi), (668, 736, 55, 8, math.pi),
                  (666, 768, 55, 8, math.pi), (662, 798, 52, 8, math.pi)]
    port = dict(name='Port of Meridian (container terminal)', district_context='meridian (NOT tethys)',
                terminal_polygon=MPL(ex['port_poly']),
                piers=[dict(base=MP((x, y)), length_m=ln * U2M, width_m=w * U2M, bearing_deg=bearing_deg(a))
                       for x, y, ln, w, a in pier_specs],
                freight_rail_terminus=MP((692, 676)), truck_gate=MP((672, 783)),
                hq_between_port_and_rail=MP((790, 720)),
                intermodal_yard=feats.get('rail_yard', [{}])[0].get('polygon'))
    lag = ex['lagoon']
    dams = [dict(name=d['name'], kind=d['kind'], polyline=MPL(d['pts'])) for d in m.dams]
    drowned = dict(name='Tethys drowned quarter', polygon=MPL(lag, 6.0), behind_dams=[d['name'] for d in m.dams if 'Tethys' in (d['name'] or '')],
                   pier_city=dict(hq='Floating Pier City (Tethys HQ)', position=MP((322, 770)), radius_m=66 * 1.4 * U2M,
                                  bearing_deg=bearing_deg(0.15)),
                   water_depth_m=4.0)
    ring = next(l for l in A2.LM if l['style'] == 'launch_ring') if False else next(l for l in A2.LM if l.get('style') == 'launch_ring')
    airport_feat = feats.get('airport', [{}])[0]
    airport = dict(name='Veyra Airport', polygon=airport_feat.get('polygon'), centre=MP((745, 258)),
                   runways=[dict(centre=MP((745, 258 + sgn * 7)), length_m=95 * U2M, bearing_deg=bearing_deg(0.05)) for sgn in (-1, 1)])
    out = dict(
        meta=dict(
            name='REBEL_CELL city plan A2 (Horseshoe Bay, refined)', version=1,
            unit='metre', origin='planning-grid point (500,500) = map centre = (0,0)',
            axes='+X east, +Y north, +Z up (Blender-ready); all x,y pairs are [x_m, y_m]',
            planning_grid='1000 x 1000 units, 1 unit = 20 m; x_m = (x_unit - 500) * 20; y_m = (500 - y_unit) * 20',
            extent_m=[-10000, 10000], sea_level_m=0.0, hill_height_scale_m_per_unit=260.0,
            old_city_centre_m=MP(C), farthest_to_nearest_corp_ratio=ratio,
            notes=['Polylines are open unless closed=true (then the last point equals the first).',
                   'Hill heights: terrain.hills are Gaussians, height_m = h * 260; add fbm noise of about 12 m if desired.',
                   'Roads: class is ring|motorway|truck|arterial|collector; tunnels and bridges are sub-polylines of the main polyline.',
                   'Bearings are compass degrees clockwise from north.']),
        terrain=dict(
            coastline=MPL(m.coast), ocean_polygon=[MP(p) for p in (m.coast + list(ex['closing']))],
            rivers=[dict(name=r['name'], kind=r['kind'], polyline=MPL(r['pts']), width_start_m=r['w0'] * 10.0,
                         width_end_m=r['w1'] * 10.0) for r in m.rivers],
            lakes=[dict(name=l['name'], polygon=MPL(l['poly'], 6.0)) for l in m.lakes],
            hills=[dict(centre=MP((cx, cy)), sigma_x_m=sx * U2M, sigma_y_m=sy * U2M, height_m=round(h * 260.0, 1),
                        rotation_rad=ang) for cx, cy, sx, sy, h, ang in ex['bumps']]),
        defences=dict(dams_and_barriers=dams, sea_walls=[dict(name=s['name'], polyline=MPL(s['pts'])) for s in m.seawalls]),
        drowned_quarter=drowned,
        districts=districts,
        neighbourhoods=[dict(name=n['name'], centre=MP(n['pos']), radius_m=n['radius'] * U2M, kind=n['kind']) for n in A2.NEIGH],
        landmarks=landmarks,
        roads=roads, interchanges=inter, rails=rails, stations=stations,
        port=port,
        parks=feats.get('park', []), plazas=feats.get('plaza', []), cemeteries=feats.get('cemetery', []),
        markets=markets,
        industry=feats.get('industry', []) + feats.get('power', []) + feats.get('sewage', []) + feats.get('recycling', []) + feats.get('data_centre', []),
        informal_housing=feats.get('slum', []),
        airport=airport,
        spaceport=dict(name=ring['name'], ring_centre=MP(ring['pos']), ring_radius_m=ring['ring_radius_m'],
                       exclusion_radius_m=ring['exclusion_radius_m'], launch_azimuth_deg=ring['azimuth_deg']),
        undercity=dict(polygon=MPL(feats['undercity'][0]['polygon'] and m.features[[f['kind'] for f in m.features].index('undercity')]['poly']),
                       tunnels=[MPL(l) for l in m.undercity_lines], entrances=[dict(name=e['name'], position=MP(e['pos'])) for e in m.undercity_entrances]),
        checkpoints=[dict(district=g['district'], position=MP(g['pos'])) for g in A2.CHECKPOINTS],
        ferries=[MPL(f['pts']) for f in m.ferries], drone_corridors=[MPL(d['pts']) for d in m.drones],
    )
    # undercity polygon is stored in unit coordinates inside features (already converted above when reading feats) -> fix
    uf = next(f for f in m.features if f['kind'] == 'undercity')
    out['undercity']['polygon'] = MPL(uf['poly'], 6.0)
    return out, ratio, dists


def main():
    t0 = time.time()
    m = A2.build()
    rep = A2.checks(m)
    print('HQ clearance (district, road, rail):', rep[0])
    print('ends near Meridian HQ:', rep[1])
    print('sharp turns:', rep[2])
    mp = m.final(2000)
    mp.save(os.path.join(OUT, 'map_A2_horseshoe_bay.png'))
    M = A2.META
    pn = make_panel(M['title'], M['subtitle'], M['blurb'], M['notes'], M['skip'], (), M['evo'])
    compose(mp, pn, os.path.join(OUT, 'plan_A2_horseshoe_bay.png'))
    data, ratio, dists = export(m)
    with open(os.path.join(OUT, 'city_A2.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, separators=(',', ':'))
    print('corp distances m:', dists, 'ratio', ratio)
    print('interchanges:', [(i['type']) for i in data['interchanges']])
    print('json bytes:', os.path.getsize(os.path.join(OUT, 'city_A2.json')), 'time', round(time.time() - t0, 1))


if __name__ == '__main__':
    main()
