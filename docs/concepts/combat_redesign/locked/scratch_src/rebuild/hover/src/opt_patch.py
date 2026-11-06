p = 'hv_core.py'
s = open(p, encoding='utf-8').read()
old = """        if r_.get('best'):
            RB3.best_star(L, xr - RB3.BEST_STAR_R, yg)
        out.append(dict(box=box, **{k: v for k, v in r_.items() if k != 'next'}, next=nx))"""
new = """        star = None
        if r_.get('best'):
            star = [xr - RB3.BEST_STAR_R, yg, RB3.BEST_STAR_R]
            RB3.best_star(L, star[0], yg)
        out.append(dict(box=box, star=star, **{k: v for k, v in r_.items() if k != 'next'}, next=nx))"""
assert old in s
s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
