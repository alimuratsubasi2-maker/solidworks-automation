"""V6 MOTOR YENI: tum parca govdelerini gri yap ve kaydet."""
import glob
import os
from swlib import connect, Part, darr
from v6_yeni_parcalar import HEDEF

GRI = (0.62, 0.62, 0.64)
sw = connect()
sw.CloseAllDocuments(True)
n = 0
for f in glob.glob(os.path.join(HEDEF, "**", "*.SLDPRT"), recursive=True):
    r = sw.OpenDoc6(f, 1, 1, "", 0, 0)
    p = Part(sw, r[0] if isinstance(r, tuple) else r)
    for b in p._bodies():
        b.MaterialPropertyValues2 = darr([*GRI, 0.6, 0.85, 0.5, 0.4, 0.0, 0.0])
    p.m.Save3(1, 0, 0)
    sw.CloseAllDocuments(True)
    n += 1
    print("gri:", os.path.relpath(f, HEDEF), flush=True)
print("Toplam:", n)
