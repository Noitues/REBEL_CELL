import sys
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/tide_raid/B_ctos_profiler/scripts')
from ctos_common import *
j = load_coords('default', 'forecast')
city = load_city()
m = territory_mask(j)
g = grade(city, m)
to_img(finish(g)).save('D:/rc_scratch/tide_concepts/venv_b/t_base.png')
