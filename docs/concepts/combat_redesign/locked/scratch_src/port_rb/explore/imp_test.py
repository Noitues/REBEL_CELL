"""imp_test: import the corp/src skin modules read-only and list what they expose (exploration only; checks import side effects)."""
import sys, time
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
t0 = time.time()
import rb_tokens as T
import cs_skin as CS
print('cs_skin ok', time.time() - t0)
import rb_patch as RBP
print('rb_patch ok', time.time() - t0)
import rb3_patch as RB3
print('rb3 ok', time.time() - t0)
import gram as G
print('gram ok', time.time() - t0)
print('skins in cs_skin:', [n for n in dir(CS) if isinstance(getattr(CS, n), type)])
print('Solace kind_gain before', getattr(CS.Solace, 'kind_gain', None))
RBP._skins()
print('Solace kind_gain after', CS.Solace.kind_gain, 'Meridian', CS.Meridian.kind_gain)
print('Solace pal', CS.Solace.pal)
print('Meridian pal', CS.Meridian.pal)
import lw_skin as LS
print('lw_skin classes', [n for n in dir(LS) if isinstance(getattr(LS, n), type)])
for k in ('Packet', 'Worm', 'Jammer', 'Payload', 'Ring'):
    print(k, [G.kind_wash(k, d, ramp=(0.0, 0.0, 0.0)) for d in range(3)])
print('done', time.time() - t0)
