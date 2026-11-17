"""_onizlemeler/*.bmp -> tek PNG tablo (parca numarasi + adi)."""
import glob
import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.argv += []
from parcalar_ciz import PARCALAR, ONIZ, HEDEF

W, H, COLS = 300, 233, 6
files = sorted(glob.glob(os.path.join(ONIZ, "*.bmp")))
rows = (len(files) + COLS - 1) // COLS
sheet = Image.new("RGB", (COLS * W, rows * (H + 24)), "white")
d = ImageDraw.Draw(sheet)
font = ImageFont.truetype("arial.ttf", 15)
for k, f in enumerate(files):
    i = int(os.path.basename(f)[:2])
    im = Image.open(f).convert("RGB")
    im.thumbnail((W, H))
    x, y = (k % COLS) * W, (k // COLS) * (H + 24)
    sheet.paste(im, (x, y + 24))
    d.text((x + 6, y + 4), f"{i}. {' '.join(PARCALAR[i - 1][0].split())}", fill="black", font=font)
out = os.path.join(HEDEF, "_tum_parcalar_onizleme.png")
sheet.save(out)
for f in files:
    im = Image.open(f); im.save(f[:-4] + ".png"); os.remove(f)
print(out)
