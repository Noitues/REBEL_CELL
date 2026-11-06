from PIL import Image, ImageDraw, ImageFont
B='D:/rc_scratch/e10_design/assembled/before/'
A='D:/rc_art/art-pass/docs/concepts/combat_e10_design/final/'
FD='D:/rc_art/art-pass/assets/fonts/'
mo=ImageFont.truetype(FD+'ShareTechMono-Regular.ttf',18)
items=[('O1 warded badge, unit 3 (p1)','p1_decide',(570,330,730,450)),
 ('O2 HOLD NEXT vs bezel spoke (p1)','p1_decide',(690,810,850,930)),
 ('O3 soak X (p2, shield slice)','p2_preview',(600,470,700,550)),
 ('O4a live tape label (nowords)','p1_nowords',(560,140,720,230)),
 ('O4b Spin card multiplier (nowords)','p1_nowords',(1170,850,1320,940))]
K=3; GAP=14; HDR=26
rows=[]
for lab,pl,bx in items:
    b=Image.open(B+pl+'.png').convert('RGB').crop(bx); a=Image.open(A+pl+'.png').convert('RGB').crop(bx)
    b=b.resize((b.width*K,b.height*K),Image.LANCZOS); a=a.resize((a.width*K,a.height*K),Image.LANCZOS)
    rows.append((lab,b,a))
W=max(r[1].width for r in rows)*2+GAP*3
H=sum(r[1].height+HDR+GAP for r in rows)+GAP
sh=Image.new('RGB',(W,H),(10,12,20)); d=ImageDraw.Draw(sh); y=GAP
for lab,b,a in rows:
    d.text((GAP,y),lab+'   BEFORE (left)  /  AFTER (right)   3x',font=mo,fill=(255,226,0)); y+=HDR
    sh.paste(b,(GAP,y)); sh.paste(a,(GAP*2+b.width,y)); y+=b.height+GAP
sh.save(A+'fixes_crops.jpg',quality=90); print(sh.size)
