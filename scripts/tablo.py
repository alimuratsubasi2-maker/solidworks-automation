"""<klasor>/_onizlemeler/NN.bmp dosyalarini tek tabloya cevirir.
Kullanim: python tablo.py drone|motor"""
import glob
import os
import sys
from PIL import Image, ImageDraw, ImageFont

if sys.argv[1] == "drone":
    from drone_parcalar import PARCALAR, ONIZ, HEDEF
    C = 5
else:
    from parcalar_ciz import PARCALAR, ONIZ, HEDEF
    C = 6
W, H = 300, 233
fs = sorted(glob.glob(os.path.join(ONIZ, "[0-9][0-9].bmp")))
sh = Image.new("RGB", (C * W, ((len(fs) + C - 1) // C) * (H + 24)), "white")
d = ImageDraw.Draw(sh)
f = ImageFont.truetype("arial.ttf", 15)
for k, p in enumerate(fs):
    i = int(os.path.basename(p)[:2])
    im = Image.open(p).convert("RGB")
    im.save(p[:-4] + ".png")
    os.remove(p)
    im.thumbnail((W, H))
    x, y = (k % C) * W, (k // C) * (H + 24)
    sh.paste(im, (x, y + 24))
    d.text((x + 6, y + 4), f"{i}. {' '.join(PARCALAR[i - 1][0].split())}", fill="black", font=f)
out = os.path.join(HEDEF, "_tum_parcalar_onizleme.png")
sh.save(out)
print(out)
