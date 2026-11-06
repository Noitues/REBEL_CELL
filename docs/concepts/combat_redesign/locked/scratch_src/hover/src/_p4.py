s=open('cs_skin.py').read()
s=s.replace("    hue_shift = 68.0\n","    hue_shift = 68.0\n    kind_gain = (2.4, 2.1, 2.0)      # O-27 follow-up: unit-kind wash separation per ring (Lab push away from the kind mean, solved by de_kinds.py)\n",1)
i=s.index("class Meridian")
j=s.index("    hue_shift = 0.0\n",i)
s=s[:j]+"    hue_shift = 0.0\n    kind_gain = (1.0, 1.1, 1.2)\n"+s[j+len("    hue_shift = 0.0\n"):]
open('cs_skin.py','w').write(s)
