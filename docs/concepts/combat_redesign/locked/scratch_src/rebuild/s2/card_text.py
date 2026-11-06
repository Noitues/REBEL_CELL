"""stage 2 scratch: card rules-text widths and cap heights at the hand scale (1.10x)."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import card_render as CR
import rb_capture as RBC
for f in (CR.PLEX, CR.MONO, CR.ANTON):
    print(f, 'cap ratio', round(RBC.cap_ratio(f), 4), 'px for 16.0 cap at 1.10:', round(16.0 / (RBC.cap_ratio(f) * 1.10), 2))
for nm in CR.ORDER:
    t = CR.CARDS[nm]['txt']
    print('%-9s %-18s' % (nm, t), ' '.join('%4.1f:%5.1f' % (px, CR.text_w(t, CR.PLEX, px)) for px in (20.5, 21.0, 21.5)))
for w in ('TWIST', 'TRIGGER', 'BRACE', 'PLAYED', 'FIREWALL', 'NUDGE', 'SPIN 3'):
    print(w, 'mono21', round(CR.text_w(w, CR.MONO, 21, 1.0), 1), 'mono22', round(CR.text_w(w, CR.MONO, 22, 1.0), 1))
print('NO RAM anton 15.5', round(CR.text_w('NO RAM', CR.ANTON, 15.5), 1), '17', round(CR.text_w('NO RAM', CR.ANTON, 17.0), 1))
