import sys
sys.path.insert(0,'D:/rc_art/art-pass/docs/concepts/solace_endscreens/v2/scripts')
from v2_lib import *
import subprocess
D=OUT
F=ImageFont.truetype(R+'assets/fonts/ShareTechMono-Regular.ttf',26)
# sheet
tw_,th_=944,531
rows=[('A  GLOSSY 8x10 SURVEILLANCE PRINT OF THE HELIX','A'),('B  SOLACE AERIAL SURVEY MAP, GREASE-PENCIL NETWORK','B'),('C  CCTV CONTACT STRIP OF THE OPERATIVES','C')]
sh=Image.new('RGB',(1920,3*(th_+46)+60),(8,10,18)); d=ImageDraw.Draw(sh)
d.text((24,14),'SOLACE FOLDER MEMO v2   win (left) / lose (right)',font=F,fill=(150,255,70))
y=56
for t,k in rows:
    d.text((24,y),t,font=F,fill=(0,229,255)); y+=36
    for i,kind in enumerate(('win','lose')):
        sh.paste(Image.open(D+f'{kind}_{k}.png').convert('RGB').resize((tw_,th_),Image.LANCZOS),(12+i*(tw_+8),y))
    y+=th_+10
sh.save(D+'sheet.jpg',quality=90)
# bookends
b=Image.new('RGB',(1920,531+110),(8,10,18)); d=ImageDraw.Draw(b)
d.text((24,14),'BOOKENDS   START (choose the file)  /  WIN (the memo on your activity)  /  LOSE',font=F,fill=(150,255,70))
w3,h3=630,354
for i,n in enumerate(('start_page','win_A','lose_A')):
    b.paste(Image.open(D+n+'.png').convert('RGB').resize((w3,h3),Image.LANCZOS),(8+i*(w3+8),60))
b=b.crop((0,0,1920,60+h3+10)); b.save(D+'bookends.jpg',quality=90)
# squints
for n in ('start_page','win_A','lose_A','win_B','lose_B','win_C','lose_C'):
    im=Image.open(D+n+'.png').convert('RGB').resize((120,68),Image.BOX).filter(ImageFilter.GaussianBlur(0.7)).resize((960,540),Image.BICUBIC)
    im.save(D+'squint_'+n+'.png')
sq=Image.new('RGB',(960*2+8,540*4+24),(8,10,18))
for i,n in enumerate(('start_page','win_A','lose_A','win_B','lose_B','win_C','lose_C')):
    sq.paste(Image.open(D+'squint_'+n+'.png'),((i%2)*968,(i//2)*548))
sq.resize((1280,1124)).save(D+'squints.jpg',quality=88)
