s = open('asm_render.py').read()
s = s.replace("import lw_render as LW\n", '''from PIL import ImageDraw
TEXTLOG = []
_otext = ImageDraw.ImageDraw.text


def _t(self, xy, text, *a, **k):
    TEXTLOG.append(str(text))
    return _otext(self, xy, text, *a, **k)


ImageDraw.ImageDraw.text = _t
import lw_render as LW
import card_render as CR
CARDLOG = {}
_CUR = [None]
_orb = CR.render_base
_otx = CR.text


def _rb(spec, nowords=False, R=4.0, seed=0):
    _CUR[0] = (spec['name'], bool(nowords))
    return _orb(spec, nowords, R, seed)


def _tx(cv, txt, *a, **k):
    if _CUR[0] is not None:
        CARDLOG.setdefault('%s|%d' % _CUR[0], []).append(txt)
    return _otx(cv, txt, *a, **k)


CR.render_base = _rb
CR.text = _tx
''')
s = s.replace("rep = dict(beat=beat,", "rep = dict(textlog=TEXTLOG, cardlog=CARDLOG, beat=beat,")
open('asm_render.py','w').write(s)
