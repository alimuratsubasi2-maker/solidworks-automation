"""V6 motor montaj teknik resmi (.SLDDRW + PDF): A2, ISO, 1. acili izdusum, 1:5.
On / yan / ust gorunus + renkli izometrik + parca listesi + balonlar."""
import os
import sys

from swlib import connect, T, MM, darr
from parcalar_ciz import HEDEF

DRW_TEMPLATE = r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\Teknik Resim.DRWDOT"
SAYFA = r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\lang\turkish\sheetformat\a2 - iso.slddrt"
BOM_TPL = r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang\turkish\bom-standard.sldbomtbt"
ASM = os.path.join(HEDEF, "engine complete.SLDASM")
OUT = os.path.join(HEDEF, "engine complete.SLDDRW")
W, H = 0.594, 0.420
SAYFA_OLCEK = 1 / 5


def mm(x, y):
    return x * MM, y * MM


def view_from(drw, names, x, y):
    for n in names:
        v = drw.CreateDrawViewFromModelView3(ASM, n, x, y, 0)
        if v is not None:
            return T(v, "IView")
    raise RuntimeError("Gorunus olusturulamadi: " + "/".join(names))


def select_view(m, v):
    m.ClearSelection2(True)
    return T(m.Extension, "IModelDocExtension").SelectByID2(v.Name, "DRAWINGVIEW", 0, 0, 0, False, 0, None, 0)


def view_vertices(sw, v):
    """Gorunusteki gorunur kose noktalari: [(sayfa_x, sayfa_y, vertex), ...]"""
    mu = T(sw.GetMathUtility(), "IMathUtility")
    vx = T(v.ModelToViewTransform, "IMathTransform")
    out = []
    for c in v.GetVisibleComponents() or []:
        c = T(c, "IComponent2")
        ents = v.GetVisibleEntities2(c, 3) or []
        ct = T(c.Transform2, "IMathTransform")
        for e in ents:
            vt = T(e, "IVertex")
            p = T(mu.CreatePoint(darr(vt.GetPoint())), "IMathPoint")
            if ct is not None:
                p = T(p.MultiplyTransform(ct), "IMathPoint")
            p = T(p.MultiplyTransform(vx), "IMathPoint")
            x, y, _ = p.ArrayData
            out.append((x, y, vt))
    return out


def olcu(sw, m, v, yatay, metin_ofset=12):
    """Gorunusun en uc iki kose noktasi arasina gercek (model) olcu koyar."""
    pts = view_vertices(sw, v)
    if len(pts) < 2:
        return None
    k = 0 if yatay else 1
    a = min(pts, key=lambda p: p[k])
    b = max(pts, key=lambda p: p[k])
    sm = T(m.SelectionManager, "ISelectionMgr")
    sd = T(sm.CreateSelectData(), "ISelectData")
    sd.View = v
    m.ClearSelection2(True)
    T(a[2], "IEntity").Select4(False, sd)
    T(b[2], "IEntity").Select4(True, sd)
    o = v.GetOutline()
    if yatay:
        dd = m.AddHorizontalDimension2((o[0] + o[2]) / 2, o[3] + metin_ofset * MM, 0)
    else:
        dd = m.AddVerticalDimension2(o[0] - metin_ofset * MM, (o[1] + o[3]) / 2, 0)
    m.ClearSelection2(True)
    if dd is None:
        return None
    return round(T(T(dd, "IDisplayDimension").GetDimension2(0), "IDimension").SystemValue / MM, 1)


def genel_olcu(m, drw, v, yatay, deger_mm, ofset=10):
    """Gorunus sinirina yerlestirilen olcu; deger montajin gercek sinir kutusundan gelir."""
    o = list(v.GetOutline())
    # oklari model kenarlarina hizala: gorunus merkezi +- gercek olcu x olcek / 2
    yari = deger_mm * MM * v.ScaleDecimal / 2
    if yatay:
        c = (o[0] + o[2]) / 2
        o[0], o[2] = c - yari, c + yari
    else:
        c = (o[1] + o[3]) / 2
        o[1], o[3] = c - yari, c + yari
    drw.EditSheet()
    sm = T(m.SketchManager, "ISketchManager")
    sm.AddToDB = True
    k = 1 / SAYFA_OLCEK     # sayfa eskizi model olceginde: sayfa koordinati / olcek
    if yatay:
        y = o[3] + ofset * MM
        p1, p2 = sm.CreatePoint(o[0] * k, y * k, 0), sm.CreatePoint(o[2] * k, y * k, 0)
    else:
        x = o[0] - ofset * MM
        p1, p2 = sm.CreatePoint(x * k, o[1] * k, 0), sm.CreatePoint(x * k, o[3] * k, 0)
    m.ClearSelection2(True)
    T(p1, "ISketchPoint").Select4(False, None)
    T(p2, "ISketchPoint").Select4(True, None)
    if yatay:
        dd = m.AddHorizontalDimension2((o[0] + o[2]) / 2, o[3] + (ofset + 6) * MM, 0)
    else:
        dd = m.AddVerticalDimension2(o[0] - (ofset + 6) * MM, (o[1] + o[3]) / 2, 0)
    m.ClearSelection2(True)
    if dd is None:
        return None
    return round(T(T(dd, "IDisplayDimension").GetDimension2(0), "IDimension").SystemValue / MM, 1)


def not_ekle(m, metin, x, y, yukseklik=None):
    n = m.InsertNote(metin)
    if n is None:
        return
    n = T(n, "INote")
    if yukseklik:
        n.SetHeightInPoints(yukseklik)
    T(n.GetAnnotation(), "IAnnotation").SetPosition2(x * MM, y * MM, 0)


def main():
    sw = connect()
    sw.SetUserPreferenceToggle(10, False)   # olcu eklerken "Degistir" kutusunu acma
    sw.CloseAllDocuments(True)
    m = T(sw.NewDocument(DRW_TEMPLATE, 9, W, H), "IModelDoc2")
    drw = T(m, "IDrawingDoc")
    sheet = T(drw.GetCurrentSheet(), "ISheet")
    ok = drw.SetupSheet5(sheet.GetName(), 9, 12, 1, 5, True, SAYFA, W, H, "Default", True)
    print("sayfa:", sheet.GetName(), ok)

    # ana gorunus: motorun on yuzu -Z'de -> modelin "Arka" gorunusu
    on = view_from(drw, ["*Geri", "*Back"], *mm(125, 285))
    on.SetDisplayMode4(False, 2, False, True, False)
    select_view(m, on)
    yan = T(drw.CreateUnfoldedViewAt3(*mm(285, 285), 0, False), "IView")
    select_view(m, on)
    ust = T(drw.CreateUnfoldedViewAt3(*mm(125, 115), 0, False), "IView")
    iso = view_from(drw, ["*İzometrik", "*Isometric"], *mm(300, 115))
    iso.UseSheetScale = False
    iso.ScaleDecimal = 1 / 6
    iso.SetDisplayMode4(False, 7, False, True, False)    # golgeli + kenarli
    for v, ad in ((on, "on"), (yan, "yan"), (ust, "ust"), (iso, "iso")):
        print(ad, v.Name if v else None, [round(t / MM) for t in (v.GetOutline() if v else [])])

    # parca listesi (sag ust; X,Y = tablonun sol ust kosesi)
    bom = on.InsertBomTable4(False, *mm(400, 408), 1, 1, "", BOM_TPL, False, 0, False)
    print("BOM:", bom is not None)

    # genel olculer (gercek model degerleri)
    box = T(T(on.ReferencedDocument, "IModelDoc2"), "IAssemblyDoc").GetBox(0)
    gx, gy, gz = [(box[i + 3] - box[i]) / MM for i in range(3)]
    print("montaj sinir kutusu (mm):", round(gx), round(gy), round(gz))
    print("genislik:", genel_olcu(m, drw, on, True, gx))
    print("yukseklik:", genel_olcu(m, drw, on, False, gy))
    print("uzunluk:", genel_olcu(m, drw, yan, True, gz))

    # basliklar
    drw.ActivateSheet(sheet.GetName())
    for v, ad in ((on, "ÖN GÖRÜNÜŞ"), (yan, "YAN GÖRÜNÜŞ"), (ust, "ÜST GÖRÜNÜŞ"), (iso, "İZOMETRİK GÖRÜNÜŞ")):
        o = v.GetOutline()
        alt = 22 if v in (on, yan) else 8          # balonlarin altina in
        not_ekle(m, ad, (o[0] + o[2]) / 2 / MM - 15, o[1] / MM - alt, 11)
    not_ekle(m, "V6 MOTOR - MONTAJ RESMİ   |   Ölçek 1:5 (izometrik 1:6)   |   Ölçüler mm", 20, 405, 14)

    # otomatik balonlar
    opts = drw.CreateAutoBalloonOptions()
    opts.IgnoreMultiple = True
    for v in (on, yan):
        select_view(m, v)
        r = drw.AutoBalloon5(opts)
        print("balon", v.Name, r is not None)

    m.ForceRebuild3(False)
    m.ViewZoomtofit2()
    m.SaveAs3(OUT, 0, 1)
    m.SaveAs3(OUT.replace(".SLDDRW", ".pdf"), 0, 1)
    m.SaveBMP(os.path.join(HEDEF, "_onizlemeler", "teknik_resim.bmp"), 2376, 1680)
    print("kaydedildi:", OUT)


if __name__ == "__main__":
    main()

