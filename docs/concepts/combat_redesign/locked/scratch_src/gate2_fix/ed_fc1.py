"""edit final_checks.py: ticket floor = the K type value; card rules text may wrap (cards_all_fields_drawn)"""
p = 'D:/rc_scratch/combat_redesign/locked/corp/src/final_checks.py'
s = open(p, encoding='utf-8').read()
a = "    row['ticket_pass'] = all(g['ink_h'] >= 16 and g['p90_L'] >= 90 for t_ in tk for g in t_) and all(tk)"
b = ("    # 2026-11-04 (gate 1, review 1.2): 'full value' for a ticket glyph is the K type value (rb_tokens.K_TYPE_L, L* 84), the same on W4, W5 and W6;\n"
     "    # time stays on the ticket edge value and pips.  The glyphs sat at L* 98, above the HOT marks and the tower (K must sit under the tower).\n"
     "    row['ticket_pass'] = all(g['ink_h'] >= 16 and RBK.T.K_TYPE_L - 4 <= g['p90_L'] <= RBK.T.K_TYPE_L + 4 for t_ in tk for g in t_) and all(tk)")
assert a in s; s = s.replace(a, b)
a = ("REP['stage2_rule'] = ('2.7: hand bottom (alpha >= 128) at least 12 px above y = 1080; 2.14: every kind glyph on the three wave tickets has an ink '\n"
     "                      'height of 16 px or more and p90 L* >= 90 (full value; time is on the ticket edge and pips)')")
b = ("REP['stage2_rule'] = ('2.7: hand bottom (alpha >= 128) at least 12 px above y = 1080; 2.14: every kind glyph on the three wave tickets has an ink '\n"
     "                      'height of 16 px or more and p90 L* within 4 of the K type value (L* %.0f, the same full value on every ticket; time is on the ticket edge and pips)' % RBK.T.K_TYPE_L)")
assert a in s; s = s.replace(a, b)
a = "        r[card] = dict(missing=[e for e in exp if e not in strs], state_cost=J['cards'][card][0], state_trace=J['cards'][card][1])"
b = ("        # 2026-11-04 (gate 1): the rules text wraps to two lines at a word break (stage 2), so it is drawn as two strings; it counts as drawn when\n"
     "        # the card's strings, joined, contain it (letters and digits only)\n"
     "        joined = norm(' '.join(str(x_) for x_ in strs))\n"
     "        r[card] = dict(missing=[e for e in exp if e not in strs and not (e == sp['txt'] and norm(e) in joined)], state_cost=J['cards'][card][0], state_trace=J['cards'][card][1],\n"
     "                       rules_lines=[x_ for x_ in strs if norm(x_) and norm(x_) in norm(sp['txt'])])")
assert a in s; s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
