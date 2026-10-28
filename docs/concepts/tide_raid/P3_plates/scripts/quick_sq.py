import sys
from PIL import Image
out = sys.argv[1]
ims = [Image.open(f).convert('RGB').resize((320, 180), Image.LANCZOS) for f in sys.argv[2:]]
st = Image.new('RGB', (len(ims) * 326 + 6, 2 * 186 + 6), (8, 6, 20))
for i, im in enumerate(ims):
    st.paste(im, (6 + i * 326, 6))
    st.paste(im.convert('L').convert('RGB'), (6 + i * 326, 192))
# enlarge x3 for viewing
st = st.resize((st.width * 2, st.height * 2), Image.NEAREST)
st.save(out)
