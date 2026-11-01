import sys
from PIL import Image
sys.dont_write_bytecode=True
a=Image.open(sys.argv[1]).convert("RGB").resize((960,540)); b=Image.open(sys.argv[2]).convert("RGB").resize((960,540))
c=Image.new("RGB",(1920,540)); c.paste(a,(0,0)); c.paste(b,(960,0)); c.save(sys.argv[3],quality=90)
