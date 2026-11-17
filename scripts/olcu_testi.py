"""Acik teknik resimde on gorunusun kose noktalarini bul, secimi ve olcuyu dene."""
from swlib import connect, T, MM
from teknik_resim import view_vertices

sw = connect()
sw.SetUserPreferenceToggle(10, False)
m = T(sw.ActiveDoc, "IModelDoc2")
drw = T(m, "IDrawingDoc")
v = T(T(drw.GetFirstView(), "IView").GetNextView(), "IView")
print("gorunus:", v.Name, "outline:", [round(t / MM) for t in v.GetOutline()])
pts = view_vertices(sw, v)
print("nokta sayisi:", len(pts))
xs = sorted(p[0] / MM for p in pts)
print("x min/max (sayfa mm):", round(xs[0], 1), round(xs[-1], 1))
a = min(pts, key=lambda p: p[0]); b = max(pts, key=lambda p: p[0])
sm = T(m.SelectionManager, "ISelectionMgr")
sd = T(sm.CreateSelectData(), "ISelectData")
sd.View = v
m.ClearSelection2(True)
print("sec1:", T(a[2], "IEntity").Select4(False, sd), "sec2:", T(b[2], "IEntity").Select4(True, sd))
print("secili:", sm.GetSelectedObjectCount2(-1))
dd = m.AddHorizontalDimension2(0.125, 0.35, 0)
print("yatay olcu:", dd)
if dd is None:
    dd = m.AddDimension2(0.125, 0.35, 0)
    print("AddDimension2:", dd)
if dd:
    print("deger mm:", T(T(dd, "IDisplayDimension").GetDimension2(0), "IDimension").SystemValue / MM)
