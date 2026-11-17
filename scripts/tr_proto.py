"""Prototip: on gorunus + kesit gorunus + koordinata bagli olculer + nokta gizleme (Piston Head)."""
import os
from swlib import connect, T, MM, darr
from v6_yeni_teknik_resim import DRW_TEMPLATE, SAYFA, W, H, gorunus, sec
from v6_yeni_parcalar import HEDEF

sw = connect()
sw.SetUserPreferenceToggle(10, False)
sw.CloseAllDocuments(True)
import sys
yol = os.path.join(HEDEF, *sys.argv[1].split("/")) if len(sys.argv) > 1 else os.path.join(HEDEF, "Piston parcalari", "Piston Head.SLDPRT")
r = sw.OpenDoc6(yol, 1, 1, "", 0, 0)
pm = T(r[0] if isinstance(r, tuple) else r, "IModelDoc2")
bb = list(T(pm, "IPartDoc").GetPartBox(True))
print("bbox mm:", [round(b / MM, 1) for b in bb])
sw.CloseAllDocuments(True)

a, b = 1, 1
m = T(sw.NewDocument(DRW_TEMPLATE, 8, W, H), "IModelDoc2")
drw = T(m, "IDrawingDoc")
sh = T(drw.GetCurrentSheet(), "ISheet")
drw.SetupSheet5(sh.GetName(), 8, 12, a, b, True, SAYFA, W, H, "Default", True)
sh = T(drw.GetCurrentSheet(), "ISheet")
sh.SetScale(a, b, True, False)

on = gorunus(drw, yol, ["*Ön", "*Front"], 90, 190)
print("on outline mm:", [round(x / MM, 1) for x in on.GetOutline()])

# --- kesit: on gorunusun merkezinden dikey cizgi ---
drw.ActivateView(on.Name)
o = on.GetOutline()
cx = (o[0] + o[2]) / 2
sm = T(m.SketchManager, "ISketchManager")
sm.AddToDB = True
seg = T(sm.CreateLine(cx, o[1] - 0.01, 0, cx, o[3] + 0.01, 0), "ISketchSegment")
print("cizgi:", seg is not None)
m.ClearSelection2(True)
seg.Select4(False, None)
sv = drw.CreateSectionViewAt5(0.21, 0.19, 0, "A", 0, None, 0)
print("kesit:", sv)
sv = T(sv, "IView")
print("kesit adi:", sv.Name, "tur:", sv.Type, "outline:", [round(x / MM, 1) for x in sv.GetOutline()])
sv.SetDisplayMode4(False, 7, False, True, False)
m.SaveBMP(os.path.join(HEDEF, "_onizlemeler", "proto_bmp.bmp"), 1600, 1000)
sm.InsertSketch(True) if False else None
m.ClearSelection2(True)
drw.EditSheet()
m.ForceRebuild3(False)
m.SaveAs3(os.path.join(HEDEF, "Teknik Resimler", "_proto.SLDDRW"), 0, 1)
m.SaveAs3(os.path.join(HEDEF, "Teknik Resimler", "_proto.pdf"), 0, 1)
print("ok")
