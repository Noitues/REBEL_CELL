p='lw_render.py'
s=open(p).read()
s=s.replace("SKIN = NeutralSkin()","import cs_skin as _CS\n_CORP = os.environ.get('CORP', 'neutral')\nSKIN = NeutralSkin() if _CORP == 'neutral' else _CS.SKINS[_CORP]")
open(p,'w').write(s)
p='asm_render.py'
s=open(p).read()
s=s.replace("sfx = beat + ('' if room == 'bio' else '_' + room)","sfx = beat + ('' if room == 'bio' else '_' + room)\nCORP = os.environ.get('CORP', 'neutral')\nif CORP != 'neutral':\n    sfx = sfx + '_' + CORP")
open(p,'w').write(s)
