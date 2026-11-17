"""V6 MOTOR YENI: her parca ve montaj icin A3 teknik resim (.SLDDRW + .pdf).
1. aci izdusum: on + yan + ust + izometrik, genel olculer; montajlarda parca listesi + balon.
Kullanim: python v6_yeni_teknik_resim.py [dosya adi filtresi]"""
import os
import sys
import traceback

from swlib import connect, T, MM, darr
from v6_yeni_parcalar import HEDEF, PARCALAR

DRW_TEMPLATE = r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\Teknik Resim.DRWDOT"
SAYFA = r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\lang\turkish\sheetformat\a3 - iso.slddrt"
BOM_TPL = r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang\turkish\bom-standard.sldbomtbt"
CIKTI = os.path.join(HEDEF, "Teknik Resimler")
W, H = 0.420, 0.297
OLCEKLER = [(5, 1), (2, 1), (1, 1), (1, 2), (1, 5), (1, 10)]

MONTAJLAR = ["Piston Assembly.SLDASM", "Rocker Arm Assembly.SLDASM", "Engine Assembly.SLDASM"]


DONEL = ("piston head", "piston pin", "valve", "camshaft bushing", "crankshaft bushing", "rocker arm roll",
         "rocker arm pin1", "partr11", "partr3", "camshaft.", "airturbo")
_DX = None


def dimxpert(sw, yol):
    """DimXpert otomatik olcu semasi (boyut + konum + derinlik olculeri), parcaya kaydedilir."""
    global _DX
    import pythoncom
    import win32com.client
    if _DX is None:
        la = pythoncom.LoadTypeLib(r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\swdimxpert.tlb").GetLibAttr()
        _DX = win32com.client.gencache.EnsureModule(str(la[0]), la[1], la[3], la[4])
    r = sw.OpenDoc6(yol, 1, 1, "", 0, 0)
    m = T(r[0] if isinstance(r, tuple) else r, "IModelDoc2")
    mgr = T(m.Extension, "IModelDocExtension").DimXpertManager("", True)
    part = _DX.IDimXpertPart(mgr.DimXpertPart._oleobj_)
    if part.GetAnnotationCount() == 0:
        opt = part.GetAutoDimSchemeOption()
        opt.PartType = 1 if os.path.basename(yol).lower().startswith(DONEL) else 0
        part.AutoDimensionScheme(opt)
        m.ForceRebuild3(False)
        m.Save3(1, 0, 0)
    return part.GetAnnotationCount()


def model_boyut(sw, yol):
    asm = yol.upper().endswith(".SLDASM")
    r = sw.OpenDoc6(yol, 2 if asm else 1, 1, "", 0, 0)
    m = T(r[0] if isinstance(r, tuple) else r, "IModelDoc2")
    b = T(m, "IAssemblyDoc").GetBox(0) if asm else T(m, "IPartDoc").GetPartBox(True)
    return [(b[i + 3] - b[i]) / MM for i in range(3)]


def olcek_sec(bx, by, bz):
    for a, b in OLCEKLER:
        s = a / b
        if (bx + bz) * s <= 255 and (by + bz) * s <= 215:
            return a, b
    return 1, 20


def gorunus(drw, yol, adlar, x, y):
    for n in adlar:
        v = drw.CreateDrawViewFromModelView3(yol, n, x * MM, y * MM, 0)
        if v is not None:
            return T(v, "IView")
    raise RuntimeError("gorunus yok")


def sec(m, v):
    m.ClearSelection2(True)
    T(m.Extension, "IModelDocExtension").SelectByID2(v.Name, "DRAWINGVIEW", 0, 0, 0, False, 0, None, 0)


def olcu(m, drw, v, yatay, deger, s, ofset=8):
    o = list(v.GetOutline())
    yari = deger * MM * s / 2
    if yatay:
        c = (o[0] + o[2]) / 2
        o[0], o[2] = c - yari, c + yari
    else:
        c = (o[1] + o[3]) / 2
        o[1], o[3] = c - yari, c + yari
    drw.EditSheet()
    sm = T(m.SketchManager, "ISketchManager")
    sm.AddToDB = True
    k = 1 / s
    if yatay:
        yy = o[3] + ofset * MM
        p1, p2 = sm.CreatePoint(o[0] * k, yy * k, 0), sm.CreatePoint(o[2] * k, yy * k, 0)
    else:
        xx = o[0] - ofset * MM
        p1, p2 = sm.CreatePoint(xx * k, o[1] * k, 0), sm.CreatePoint(xx * k, o[3] * k, 0)
    m.ClearSelection2(True)
    T(p1, "ISketchPoint").Select4(False, None)
    T(p2, "ISketchPoint").Select4(True, None)
    if yatay:
        m.AddHorizontalDimension2((o[0] + o[2]) / 2, o[3] + (ofset + 5) * MM, 0)
    else:
        m.AddVerticalDimension2(o[0] - (ofset + 5) * MM, (o[1] + o[3]) / 2, 0)
    m.ClearSelection2(True)


def cap_olculeri(sw, m, drw, v, maks=5):
    """Gorunusde gercek daire gorunen kenarlara benzersiz yaricapli cap olcusu koyar (sadece parcalar)."""
    mu = T(sw.GetMathUtility(), "IMathUtility")
    vx = T(v.ModelToViewTransform, "IMathTransform")
    sm = T(m.SelectionManager, "ISelectionMgr")
    sd = T(sm.CreateSelectData(), "ISelectData")
    sd.View = v
    ents = v.GetVisibleEntities2(None, 1) or []
    gorulen, adet = set(), 0
    o = v.GetOutline()
    for e in ents:
        if adet >= maks:
            break
        try:
            ed = T(e, "IEdge")
            cv = T(ed.GetCurve(), "ICurve")
            if not cv.IsCircle():
                continue
            cp = cv.CircleParams
            r = round(cp[6], 2)
            if r in gorulen or r < 0.5:
                continue
            ax = T(mu.CreateVector(darr(cp[3:6])), "IMathVector")
            ax = T(ax.MultiplyTransform(vx), "IMathVector")
            if abs(ax.ArrayData[2]) < 0.98:
                continue
            gorulen.add(r)
            m.ClearSelection2(True)
            T(e, "IEntity").Select4(False, sd)
            yy = o[1] + (o[3] - o[1]) * (0.15 + 0.14 * adet)
            if m.AddDimension2(o[2] + 12 * MM, yy, 0) is not None:
                adet += 1
        except Exception:
            continue
    m.ClearSelection2(True)
    return adet


def not_ekle(m, metin, x, y, pt=10):
    n = m.InsertNote(metin)
    if n is None:
        return
    n = T(n, "INote")
    n.SetHeightInPoints(pt)
    T(n.GetAnnotation(), "IAnnotation").SetPosition2(x * MM, y * MM, 0)


def resim(sw, rel):
    yol = os.path.join(HEDEF, rel)
    ad = os.path.splitext(os.path.basename(rel))[0]
    asm = rel.upper().endswith(".SLDASM")
    n_dx = 0
    if not asm:
        try:
            n_dx = dimxpert(sw, yol)
        except Exception:
            n_dx = -1
    bx, by, bz = model_boyut(sw, yol)
    a, b = olcek_sec(bx, by, bz)
    s = a / b
    m = T(sw.NewDocument(DRW_TEMPLATE, 8, W, H), "IModelDoc2")
    drw = T(m, "IDrawingDoc")
    sh = T(drw.GetCurrentSheet(), "ISheet")
    drw.SetupSheet5(sh.GetName(), 8, 12, a, b, True, SAYFA, W, H, "Default", True)
    sh = T(drw.GetCurrentSheet(), "ISheet")
    sh.SetScale(a, b, True, False)
    fx, fy = 25 + bx * s / 2 + 22, 280 - by * s / 2 - 24
    on = gorunus(drw, yol, ["*Ön", "*Front"], fx, fy)
    sec(m, on)
    yan = T(drw.CreateUnfoldedViewAt3((fx + bx * s / 2 + 25 + bz * s / 2) * MM, fy * MM, 0, False), "IView")
    sec(m, on)
    ust = T(drw.CreateUnfoldedViewAt3(fx * MM, (fy - by * s / 2 - 25 - bz * s / 2) * MM, 0, False), "IView")
    for v in (on, yan, ust):
        if v is not None:
            v.SetDisplayMode4(False, 2, False, True, False)
    iso = gorunus(drw, yol, ["*İzometrik", "*Isometric"], *((180, 62) if asm else (335, 200)))
    iso.UseSheetScale = False
    iso.ScaleDecimal = s * (0.4 if asm else 0.6)
    iso.SetDisplayMode4(False, 7, False, True, False)
    if asm and "Engine" not in rel:
        # taranmis kesit (A-A): aktif gorunumde eskiz = model metresi, orijin gorunus merkezi
        drw.ActivateView(on.Name)
        sm_ = T(m.SketchManager, "ISketchManager")
        sm_.AddToDB = True
        hh = by * MM / 2 + 0.015
        seg = T(sm_.CreateLine(0, -hh, 0, 0, hh, 0), "ISketchSegment")
        m.ClearSelection2(True)
        seg.Select4(False, None)
        kv = T(drw.CreateSectionViewAt5(330 * MM, 205 * MM, 0, "A", 1, None, 0), "IView")
        kv.UseSheetScale = False
        kv.ScaleDecimal = on.ScaleDecimal
        kv.SetDisplayMode4(False, 2, False, True, False)
        m.ClearSelection2(True)
    if asm:
        # (UseAnchor, x, y, AnchorType=2 sag-ust, BomType=1 sadece parcalar) - V6 ilk resimde calisan cagri
        on.InsertBomTable4(False, 240 * MM, 284 * MM, 1, 1, "", BOM_TPL, False, 0, False)
        m.ForceRebuild3(False)
        opts = drw.CreateAutoBalloonOptions()
        opts.IgnoreMultiple = True
        sec(m, on)
        drw.AutoBalloon5(opts)
    s = on.ScaleDecimal          # gercek gorunus olcegi (sayfa eskizi de bu olcekte)
    if not asm:                  # montaj resminde genel olcu yok (sayfa disina tasiyordu)
        olcu(m, drw, on, True, bx, s)
        olcu(m, drw, on, False, by, s)
        if yan is not None:
            olcu(m, drw, yan, True, bz, s)
    if not asm:
        drw.EditSheet()
        # DimXpert olculeri + model olculeri + delik/ceper cagri notlari; tum gorunuslere dagit
        tur = 8 | 32768 | 524288 | 65536 | 131072 | 1048576
        for v in (on, yan, ust):
            if v is not None:
                sec(m, v)
                try:
                    drw.InsertModelAnnotations3(0, tur, False, True, True, False)
                except Exception:
                    pass
    drw.ActivateSheet(sh.GetName())
    not_ekle(m, f"V6 MOTOR  -  {ad}  -  Olculer mm", 22, 24, 12)
    m.ForceRebuild3(False)
    m.ViewZoomtofit2()
    out = os.path.join(CIKTI, ad + ".SLDDRW")
    m.SaveAs3(out, 0, 1)

    sw.CloseAllDocuments(True)
    return f"{a}:{b}", (round(bx), round(by), round(bz))


def main():
    os.makedirs(CIKTI, exist_ok=True)
    sw = connect()
    sw.SetUserPreferenceToggle(10, False)      # olcu eklerken "Degistir" kutusu acilmasin
    sw.CloseAllDocuments(True)
    liste = [ad + ".SLDPRT" for ad, _ in PARCALAR] + MONTAJLAR
    filt = sys.argv[1:]
    if filt:
        liste = [r for r in liste if any(f.lower() in r.lower() for f in filt)]
    ok = 0
    try:
        for rel in liste:
            try:
                ol, bo = resim(sw, rel)
                ok += 1
                print(f"OK   {rel:48s} olcek {ol:5s} boyut {bo}", flush=True)
            except Exception:
                print(f"HATA {rel}")
                traceback.print_exc()
                sw.CloseAllDocuments(True)
    finally:
        sw.SetUserPreferenceToggle(10, True)
    print("Basarili:", ok, "/", len(liste))


if __name__ == "__main__":
    main()

