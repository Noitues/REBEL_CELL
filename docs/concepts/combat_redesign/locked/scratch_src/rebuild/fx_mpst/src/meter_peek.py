"""meter_peek.py <meter json>: the regions at 3 flashes per s (beat tiles and skip paths)"""
import sys, json
m = json.load(open(sys.argv[1]))
b = m['beat']
for k, t in b['tiles'].items():
    for w in t['worst']:
        if w['max_flashes_per_s'] >= 3:
            print('beat tile', k, w)
for Ts, s in m['skips'].items():
    print('skip', Ts, 'whole', s['whole']['flashes'], s['whole']['flash_ms'], 'any', s['max_flashes_per_s_any_region'],
          {k: (v['max_flashes_per_s'], v['worst'][0]['x0'], v['worst'][0]['y0'], v['worst'][0]['flash_ms']) for k, v in s['tiles'].items() if v['worst']})
