"""Klasordeki SLDPRT'lerin olculerini ve montajdaki bilesen konumlarini yazdirir.
Kullanim: python olcu_cikar.py <klasor> <montaj.SLDASM>"""
import glob
import os
import sys
from swlib import connect, T, MM

sw = connect()
klasor, asm = sys.argv[1], sys.argv[2]


def r(v):
    return [round(x / MM, 1) for x in v]


for f in sorted(glob.glob(os.path.join(klasor, "*.SLDPRT"))):
    res = sw.OpenDoc6(f, 1, 1, "", 0, 0)
    m = T(res[0] if isinstance(res, tuple) else res, "IModelDoc2")
    if m is None:
        print("## acilamadi:", os.path.basename(f))
        continue
    p = T(m, "IPartDoc")
    bodies = p.GetBodies2(0, False) or []
    box = p.GetPartBox(True)
    feats = []
    ft = T(m.FirstFeature(), "IFeature")
    while ft is not None:
        tn = ft.GetTypeName2()
        if tn not in ("RefPlane", "OriginProfileFeature", "MaterialFolder", "SensorFolder", "DocsFolder",
                      "DetailCabinet", "HistoryFolder", "SelectionSetFolder", "CommentsFolder",
                      "FavoriteFolder", "EqnFolder", "EnvFolder", "InkMarkupFolder", "MateReferenceGroupFolder",
                      "SolidBodyFolder", "SurfaceBodyFolder", "BlockFolder", "LiveSectionFolder"):
            feats.append(tn)
        ft = T(ft.GetNextFeature(), "IFeature")
    print(f"## {os.path.basename(f)}  govde={len(bodies)}  kutu(mm)={r(box)}")
    print("   ozellikler:", ", ".join(feats))
    sw.CloseDoc(m.GetTitle())

res = sw.OpenDoc6(asm, 2, 1, "", 0, 0)
m = T(res[0] if isinstance(res, tuple) else res, "IModelDoc2")
for c in T(m, "IAssemblyDoc").GetComponents(True) or []:
    c = T(c, "IComponent2")
    t = c.Transform2
    a = list(t.ArrayData) if t else [0] * 13
    sup = c.IsSuppressed()
    print(f"{c.Name2:32s} supp={sup} org={[round(v/MM,1) for v in a[9:12]]} "
          f"X={[round(v,2) for v in a[0:3]]} Y={[round(v,2) for v in a[3:6]]} path={os.path.basename(c.GetPathName())}")
