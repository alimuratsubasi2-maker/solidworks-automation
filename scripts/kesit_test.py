import os
from swlib import connect, T, MM, darr
from tr_pro import Resim
from v6_yeni_parcalar import HEDEF

sw = connect()
sw.SetUserPreferenceToggle(10, False)
sw.CloseAllDocuments(True)
R = Resim(sw, os.path.join(HEDEF, "CylinderHead.SLDPRT"), "CylinderHead", "x", gorunumler=("on",), iso=False)
on = R.views["on"]
o = list(on.GetOutline())
cx = (o[0] + o[2]) / 2
R.drw.ActivateView(on.Name)
sm = T(R.m.SketchManager, "ISketchManager")
sm.AddToDB = True
seg = T(sm.CreateLine(cx, o[1] - 0.01, 0, cx, o[3] + 0.01, 0), "ISketchSegment")
R.m.ClearSelection2(True)
seg.Select4(False, None)
sv = T(R.drw.CreateSectionViewAt5(o[2] + 0.12, (o[1] + o[3]) / 2, 0, "A", 0, None, 0), "IView")
print("kesit:", sv.Name, [round(x * 1000) for x in sv.GetOutline()])
mu = T(sw.GetMathUtility(), "IMathUtility")
vx = T(sv.ModelToViewTransform, "IMathTransform")
for nm, p in (("orijin", (0, 0, 0)), ("z+100", (0, 0, 0.1)), ("y+100", (0, 0.1, 0)), ("x+100", (0.1, 0, 0))):
    pt = T(mu.CreatePoint(darr(p)), "IMathPoint")
    q = T(pt.MultiplyTransform(vx), "IMathPoint").ArrayData
    print(nm, [round(v * 1000, 1) for v in q])
R.m.SaveAs3(os.path.join(HEDEF, "Teknik Resimler", "_k.pdf"), 0, 1)
sw.CloseAllDocuments(True)
