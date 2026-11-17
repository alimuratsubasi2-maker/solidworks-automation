"""Orijinal parcalarin olculerini ve 4 acidan (on/ust/sag/izo) gorunusunu cikarir.
Kullanim: python orijinal_incele.py <klasor> <cikti_klasoru> "parca adi" ..."""
import os
import sys
from PIL import Image, ImageDraw, ImageFont
from swlib import connect, T, MM

sw = connect()
sw.CloseAllDocuments(True)
klasor, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
font = ImageFont.truetype("arial.ttf", 16)
for ad in sys.argv[3:]:
    r = sw.OpenDoc6(os.path.join(klasor, ad + ".SLDPRT"), 1, 1, "", 0, 0)
    m = T(r[0] if isinstance(r, tuple) else r, "IModelDoc2")
    p = T(m, "IPartDoc")
    box = [round(v / MM, 1) for v in p.GetPartBox(True)]
    boyut = [round(box[i + 3] - box[i], 1) for i in range(3)]
    print(f"{ad:22s} kutu={box}  boyut(XYZ)={boyut}")
    tiles = []
    for vn in ("*Ön", "*Üst", "*Sağ", "*İzometrik"):
        m.ShowNamedView2(vn, -1)
        m.ViewZoomtofit2()
        b = os.path.join(out, "_t.bmp")
        m.SaveBMP(b, 700, 520)
        tiles.append((vn, Image.open(b).convert("RGB")))
    sheet = Image.new("RGB", (1400, 1040 + 30), "white")
    d = ImageDraw.Draw(sheet)
    d.text((8, 6), f"{ad}   boyut X={boyut[0]} Y={boyut[1]} Z={boyut[2]} mm", fill="black", font=font)
    for k, (vn, im) in enumerate(tiles):
        x, y = (k % 2) * 700, 30 + (k // 2) * 520
        sheet.paste(im, (x, y))
        d.text((x + 8, y + 6), vn, fill="red", font=font)
    sheet.save(os.path.join(out, ad.replace(" ", "_") + ".png"))
    sw.CloseAllDocuments(True)
os.remove(os.path.join(out, "_t.bmp"))
