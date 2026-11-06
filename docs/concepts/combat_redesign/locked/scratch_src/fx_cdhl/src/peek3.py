from PIL import Image
W='D:/rc_scratch/combat_redesign/locked/fx_cdhl/work/'
b=Image.open(W+'base_neutral_p3.png').convert('RGBA')
t=Image.open(W+'trig_yel.png')
c=b.copy(); c.alpha_composite(t)
c.crop((200,580,720,940)).resize((1040,720)).save(W+'c3.png')
