p = 'hv_comp.py'
s = open(p, encoding='utf-8').read()
s = s.replace("""    if lift is None:
        if not feasible_rest:
            return None""", """    HL_STATS.clear()
    HL_STATS.update(rest_opts=len(rest_opts), feasible_rest=len(feasible_rest), feasible_rest_head=[fr[:5] for fr in feasible_rest[:8]])
    if lift is None:
        if not feasible_rest:
            return None""", 1)
s = s.replace("""    if best is not None:
        best['tried'] = tried
        best['n_rest_feasible'] = len(feasible_rest)
    return best""", """    HL_STATS.update(tried=tried, lift_free={k_: len(v) for k_, v in free.items()})
    if best is not None:
        best['tried'] = tried
        best['n_rest_feasible'] = len(feasible_rest)
    return best""", 1)
s = s.replace("HAND_MASKS = {}\n", "HAND_MASKS = {}\nHL_STATS = {}\n", 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok', s.count('HL_STATS'))
