from PIL import Image
im=Image.open('D:/rc_tmp/combat_critic/plates/waves_e10/p1_decide.png').convert('RGB')
c=(536,540)
im.crop((c[0]-180,c[1]-180,c[0]+180,c[1]+180)).resize((1080,1080),Image.LANCZOS).save('D:/rc_scratch/e10_design/wheel_core/cur_core_p1_3x.png')
