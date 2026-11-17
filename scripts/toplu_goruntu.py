"""Klasordeki tum SLDPRT/SLDASM dosyalarinin izometrik goruntulerini tek tabloya koyar.
Kullanim: python toplu_goruntu.py <klasor> <cikti.png>"""
import glob
import os
import sys
from PIL import Image, ImageDraw, ImageFont
from swlib import connect, T

sw = connect()
sw.CloseAllDocuments(True)
klasor, out = sys.argv[1], sys.argv[2]
tmp = os.path.join(os.path.dirname(out), "_tg")
os.makedirs(tmp, exist_ok=True)
files = [f for f in sorted(glob.glob(os.path.join(klasor, "*.SLD*"))) if not os.path.basename(f).startswith("~$")]
imgs = []
for f in files:
    tip = 2 if f.upper().endswith(".SLDASM") else 1
    r = sw.OpenDoc6(f, tip, 1, "", 0, 0)
    m = T(r[0] if isinstance(r, tuple) else r, "IModelDoc2")
    if m is None:
        continue
    m.ShowNamedView2("*Isometric", 7)
    m.ViewZoomtofit2()
    b = os.path.join(tmp, f"{len(imgs):02d}.bmp")
    m.SaveBMP(b, 900, 700)
    imgs.append((os.path.basename(f), b))
    if tip == 2:
        comps = T(m, "IAssemblyDoc").GetComponents(True) or []
        print(os.path.basename(f), "->", sorted({T(c, "IComponent2").Name2.rsplit("-", 1)[0] for c in comps}))
    sw.CloseAllDocuments(True)

W, H, C = 300, 233, 4
sheet = Image.new("RGB", (C * W, ((len(imgs) + C - 1) // C) * (H + 24)), "white")
d = ImageDraw.Draw(sheet)
font = ImageFont.truetype("arial.ttf", 15)
for k, (ad, b) in enumerate(imgs):
    im = Image.open(b).convert("RGB")
    im.thumbnail((W, H))
    x, y = (k % C) * W, (k // C) * (H + 24)
    sheet.paste(im, (x, y + 24))
    d.text((x + 6, y + 4), ad, fill="black", font=font)
    os.remove(b)
sheet.save(out)
print(out)
