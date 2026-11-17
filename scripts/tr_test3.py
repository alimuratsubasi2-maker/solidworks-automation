import os
from swlib import connect, T
from tr_pro import Resim
from v6_yeni_parcalar import HEDEF

sw = connect()
sw.SetUserPreferenceToggle(10, False)
sw.CloseAllDocuments(True)
R = Resim(sw, os.path.join(HEDEF, "OilPan.SLDPRT"), "OilPan", "x", gorunumler=("on",), iso=False)
R.h("on", (-165.1, 25.4, 0), (165.1, 25.4, 0), "ust", 1)
m = R.m
f = T(m.FirstFeature(), "IFeature")
while f is not None:
    if f.GetTypeName2() == "DrSheet":
        sub = T(f.GetFirstSubFeature(), "IFeature")
        while sub is not None:
            if sub.GetTypeName2() == "ProfileFeature":
                m.ClearSelection2(True)
                print("select:", sub.Select2(False, 0), "secili:", T(m.SelectionManager, "ISelectionMgr").GetSelectedObjectCount2(-1))
                print("blank oncesi gorunur:", sub.Visible if hasattr(sub, "Visible") else "?")
                try:
                    print("blank:", m.BlankSketch())
                except Exception as e:
                    print("blank hata", e)
                sk = T(sub.GetSpecificFeature2(), "ISketch")
                print("sketch:", sk, "nokta sayisi:", len(sk.GetSketchPoints2() or []) if sk else None)
                print("sonra gorunur:", sub.Visible)
                m.ClearSelection2(True)
                sub.Select2(False, 0)
                m.BlankSketch()
                print("ikinci blank sonrasi:", sub.Visible)
            sub = T(sub.GetNextSubFeature(), "IFeature")
    f = T(f.GetNextFeature(), "IFeature")
sw.CloseAllDocuments(True)
