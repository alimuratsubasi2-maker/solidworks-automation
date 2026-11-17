"""Bir SolidWorks dosyasini acip izometrik goruntusunu kaydeder.
Kullanim: python ac_ve_goruntule.py <dosya> <cikti.bmp>"""
import sys
from swlib import connect, T

sw = connect()
yol, out = sys.argv[1], sys.argv[2]
tip = 2 if yol.upper().endswith(".SLDASM") else 1
r = sw.OpenDoc6(yol, tip, 1, "", 0, 0)
m = T(r[0] if isinstance(r, tuple) else r, "IModelDoc2")
m.ShowNamedView2("*Isometric", 7)
m.ViewZoomtofit2()
m.GraphicsRedraw2()
m.SaveBMP(out, 1400, 900)
if tip == 2:
    comps = T(m, "IAssemblyDoc").GetComponents(True) or []
    from collections import Counter
    c = Counter(T(x, "IComponent2").Name2.rsplit("-", 1)[0] for x in comps)
    for k, v in sorted(c.items()):
        print(f"{v:3d} x {k}")
