"""Tum parcalardaki tum govdelerin rengi gri mi kontrol eder, motor montajinin goruntusunu scratchpad'e alir."""
import glob
import os
import sys
from swlib import connect, T, Part
from v6_yeni_parcalar import HEDEF

sw = connect()
sw.CloseAllDocuments(True)
yanlis = []
n = 0
for f in sorted(glob.glob(os.path.join(HEDEF, "**", "*.SLDPRT"), recursive=True)):
    r = sw.OpenDoc6(f, 1, 1, "", 0, 0)
    p = Part(sw, r[0] if isinstance(r, tuple) else r)
    for b in p._bodies():
        v = b.MaterialPropertyValues2
        n += 1
        if not v or abs(v[0] - 0.62) > 0.01 or abs(v[1] - 0.62) > 0.01 or abs(v[2] - 0.64) > 0.01:
            yanlis.append((os.path.basename(f), b.Name, None if not v else [round(x, 2) for x in v[:3]]))
    sw.CloseAllDocuments(True)
print(f"{n} govde kontrol edildi, gri olmayan: {len(yanlis)}")
for y in yanlis:
    print("  ", y)
r = sw.OpenDoc6(os.path.join(HEDEF, "Engine Assembly.SLDASM"), 2, 1, "", 0, 0)
m = T(r[0] if isinstance(r, tuple) else r, "IModelDoc2")
m.ShowNamedView2("*İzometrik", -1)
m.ViewZoomtofit2()
m.SaveBMP(sys.argv[1], 1400, 900)
sw.CloseAllDocuments(True)
