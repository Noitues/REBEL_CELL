import sys
sys.dont_write_bytecode = True
import wc_core_opts as CO
import wc_over_opts as OO
import wc_base as WB
import wc_tower as T

OUT = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/r1/wheel_core/'


def fav_cfg():
    tile = dict(CO.FRAME['A'])
    tile.update(tex=CO.tex_factory('A', 'A'), tex_gain=1.0, glow_k=(0.0, 0.0))
    c = CO.cfg_with(tile=tile, hub=CO.hub_factory('A', 'A', 'A', 'A'), frame=CO.frame_factory('A'), icon_dims=(34, 34),
                    icons=CO.icons_cfg({'BURST': 'A', 'SHIELD': 'A', 'TURRET': 'A', 'REPAIR': 'A'}))
    def post(L):
        for s in range(6):
            a = 60 * s + 30
            L.line([WB.ppx(WB.C, 44, a), WB.ppx(WB.C, 159, a)], (3, 4, 8), 8)
    c['post_frame'] = post
    return c


SEL = {'slice_stage': OO.stage_factory('A', 'A'), 'threat_trim': OO.trim_factory('A'), 'hp_ring': OO.hp_ring_factory('A'),
       'nudge': OO.nudge_factory('A'), 'guns': OO.guns_factory('A')}

if __name__ == '__main__':
    for beat in ('p1', 'p2', 'nowords'):
        im = WB.render(beat, sel=SEL, core='wc', cfg=fav_cfg())
        im.convert('RGB').save(OUT + 'plate_favourites_%s.png' % beat)
        WB.crop(im, (356, 360, 716, 720), 2).save(OUT + 'crops/favourites_core_%s.png' % beat)
